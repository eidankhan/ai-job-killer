import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.models.email_verification import EmailVerification
from app.utils.security import hash_password, verify_password, create_access_token, refresh_access_token as security_refresh_token
from app.utils.email import send_email, validate_and_normalize_email, generate_verification_email_template
from app.core.logger import logger
from sqlalchemy.exc import SQLAlchemyError
from app.core.redis import r

CODE_TTL_MINUTES = 15
MAX_ATTEMPTS = 5

def _new_code() -> str:
    return f"{random.randint(0, 999999):06d}"

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email.lower().strip()).first()

def signup(db: Session, email: str, password: str, name: str):
    logger.info(f"Attempting signup for email: {email}")

    # ✅ Validate + normalize email first
    email = validate_and_normalize_email(email)
    
    user = User(
        name=name,
        email=email,  # already normalized in validate_email_address
        password_hash=hash_password(password),
        is_verified=False
    )

    try:
        db.add(user)
        db.flush()
        logger.info(f"New user created: {email}")
    except IntegrityError:
        db.rollback()
        existing = get_user_by_email(db, email)
        if existing and existing.is_verified:
            logger.warning(f"Signup attempt for already registered email: {email}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
        user = existing or None
        if not user:
            logger.error(f"Failed to create user for email: {email}")
            raise HTTPException(status_code=400, detail="Failed to create user.")

    # Consume old codes
    db.query(EmailVerification).filter(
        EmailVerification.user_id == user.id,
        EmailVerification.consumed == False
    ).update({"consumed": True})
    logger.info(f"Old verification codes consumed for user: {email}")

    # Generate and send new verification code
    code = _new_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES)
    ev = EmailVerification(user_id=user.id, code=code, expires_at=expires_at)
    db.add(ev)
    db.commit()
    logger.info(f"Verification code generated for user: {email}")

    subject, html, text_body = generate_verification_email_template(user.email, code)
    send_email(user.email, subject, html, text_body=text_body)

    logger.info(f"Verification email sent to: {email}")

    return user

def verify_email(db: Session, email: str, code: str):
    logger.info(f"Attempting to verify email: {email} with code: {code}")
    
    # ✅ Validate + normalize email first
    validate_and_normalize_email(email)

    user = get_user_by_email(db, email)
    if not user:
        logger.warning(f"Verification failed: user not found: {email}")
        raise HTTPException(status_code=404, detail="User not found.")

    ev = db.query(EmailVerification).filter(
        EmailVerification.user_id == user.id,
        EmailVerification.consumed == False
    ).order_by(EmailVerification.id.desc()).first()

    if not ev:
        logger.warning(f"No active verification code for user: {email}")
        raise HTTPException(status_code=400, detail="No active code. Signup again.")

    if ev.attempts >= MAX_ATTEMPTS:
        ev.consumed = True
        db.commit()
        logger.warning(f"Too many attempts for user: {email}")
        raise HTTPException(status_code=429, detail="Too many attempts.")

    ev.attempts += 1
    now = datetime.now(timezone.utc)
    if now > ev.expires_at:
        ev.consumed = True
        db.commit()
        logger.warning(f"Verification code expired for user: {email}")
        raise HTTPException(status_code=400, detail="Code expired.")

    if code != ev.code:
        db.commit()
        logger.warning(f"Invalid verification code attempt for user: {email}")
        raise HTTPException(status_code=400, detail="Invalid code.")

    ev.consumed = True
    user.is_verified = True
    db.commit()
    logger.info(f"Email verified successfully for user: {email}")
    return user

def login(db: Session, email: str, password: str) -> str:
    logger.info(f"Login attempt for email: {email}")
    
    # ✅ Validate + normalize email first
    validate_and_normalize_email(email)

    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        logger.warning(f"Invalid credentials for email: {email}")
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if not user.is_verified:
        logger.warning(f"Login attempt with unverified email: {email}")
        raise HTTPException(status_code=403, detail="Email not verified.")

    token = create_access_token(sub=str(user.id))
    logger.info(f"Login successful for user: {email}")
    return token

def resend_verification_email(db: Session, email: str):

    logger.info(f"Resend verification email requested for: {email}")

    # Validate and normalize email
    email = validate_and_normalize_email(email)
    
    user = get_user_by_email(db, email)
    if not user:
        logger.warning(f"Resend failed: user not found: {email}")
        raise HTTPException(status_code=404, detail="User not found.")

    if user.is_verified:
        logger.info(f"Resend skipped: user already verified: {email}")
        raise HTTPException(status_code=400, detail="Email already verified.")

    # Invalidate old codes
    db.query(EmailVerification).filter(
        EmailVerification.user_id == user.id,
        EmailVerification.consumed == False
    ).update({"consumed": True})
    logger.info(f"Old verification codes consumed for user: {email}")

    # Generate new code
    code = _new_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES)
    ev = EmailVerification(user_id=user.id, code=code, expires_at=expires_at)
    db.add(ev)
    try:
        db.commit()
        logger.info(f"New verification code generated for user: {email}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to save new verification code for {email}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

    # Send email
    subject, html, text_body = generate_verification_email_template(user.email, code)
    send_email(user.email, subject, html, text_body=text_body)
    logger.info(f"Verification email sent to: {email}")

    return {"message": "Verification email resent successfully."}

async def logout(current_user: dict):
    """
    Business logic to revoke the current JWT.
    """
    token_key = f"revoked:{current_user['sub']}:{current_user['iat']}"
    
    # Calculate remaining lifetime
    exp = datetime.fromtimestamp(current_user["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    ttl = (exp - now).total_seconds()

    if ttl <= 0:
        raise HTTPException(status_code=400, detail="Token already expired")
    
    # Store in Redis with TTL
    await r.set(token_key, "revoked", ex=int(ttl))
    
    return {"message": "Successfully logged out"}

def refresh_access_token(refresh_token: str) -> dict:
    """
    Service layer wrapper — can add logging, revocation checks, etc.
    """
    # Optional: check if refresh token is revoked in Redis
    # revoked = await r.get(f"revoked:{refresh_token}")
    # if revoked:
    #     raise HTTPException(status_code=401, detail="Refresh token revoked")

    return security_refresh_token(refresh_token)

async def send_reset_password_email(user):
        """
        Generate a short-lived reset code and send via email.
        """
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        key = f"pwdreset:{user.email}:{code}"

        # Store in Redis with TTL
        await r.set(key, user.email, ex=CODE_TTL_MINUTES * 60)

        # Email content
        subject = "Your ai-job-killer Verification Code"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; 
            border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f9f9f9;">
            <h2 style="color: #333;">Password Reset</h2>
            <p style="font-size: 16px; color: #555;">
                Hello <strong>{user.email}</strong>,<br><br>
                Use the verification code below to reset your password:
            </p>
            <div style="text-align: center; margin: 20px 0;">
                <span style="display: inline-block; padding: 15px 25px; font-size: 28px; font-weight: 700; 
                    color: #ffffff; background-color: #4CAF50; border-radius: 6px; letter-spacing: 4px;">
                    {code}
                </span>
            </div>
            <p style="font-size: 14px; color: #888;">
                This code will expire in <strong>{CODE_TTL_MINUTES} minutes</strong>.<br>
                If you did not request this, please ignore this email.
            </p>
        </div>
        """
        text_body = (
        f"Hello {user.email},\n"
        f"Your verification code is: {code}\n"
        f"Expires in {CODE_TTL_MINUTES} minutes."
    )
        
        send_email(user.email, subject, html_body, text_body=text_body)

        return {"message": "Password reset code sent."}

async def reset_password(db:Session, email: str, code: str, new_password: str):
    """
    Verify reset code and update password.
    """
    key = f"pwdreset:{email}:{code}"
    stored = await r.get(key)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code."
        )

    # Update password in DB
    user = get_user_by_email(db, email)
    user.password_hash = hash_password(new_password)
    db.commit()
    await r.delete(key)  # Invalidate reset code
    return {"message": "Password updated successfully."}


def get_user_profile(db: Session, user_sub: str) -> dict:
    """
    Fetch full user info from the database by JWT 'sub' claim.
    """
    user = db.query(User).filter(User.id == user_sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": str(user.id),  # convert int to string,
        "email": user.email,
        "name": user.name,
        "is_verified": user.is_verified
    }
