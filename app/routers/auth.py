from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import SignUpRequest, VerifyEmailRequest, LoginRequest, TokenResponse, PublicUser, ForgotPasswordRequest, ResetPasswordRequest
from app.services import auth_service
from app.core.logger import logger
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/signup", response_model=PublicUser)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
    logger.info(f"Signup API called for email: {payload.email}")
    try:
        user = auth_service.signup(db, payload.email, payload.password, payload.name)
        logger.info(f"Signup successful for email: {payload.email}")
        return user
    except HTTPException as e:
        logger.warning(f"Signup failed for email: {payload.email} - {e.detail}")
        raise

@router.post("/verify-email", response_model=PublicUser)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    logger.info(f"Verify-email API called for email: {payload.email}")
    try:
        user = auth_service.verify_email(db, payload.email, payload.code)
        logger.info(f"Email verification successful for: {payload.email}")
        return user
    except HTTPException as e:
        logger.warning(f"Email verification failed for email: {payload.email} - {e.detail}")
        raise

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login API called for email: {payload.email}")
    try:
        token = auth_service.login(db, payload.email, payload.password)
        logger.info(f"Login successful for email: {payload.email}")
        return TokenResponse(access_token=token)
    except HTTPException as e:
        logger.warning(f"Login failed for email: {payload.email} - {e.detail}")
        raise

@router.post("/resend-verification-code")
def resend_verification(payload: dict, db: Session = Depends(get_db)):
    """
    Resend the email verification code to a user.
    Body: {"email": "user@example.com"}
    """
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=422, detail="Email is required.")

    logger.info(f"Resend-verification API called for email: {email}")
    try:
        result = auth_service.resend_verification_email(db, email)
        logger.info(f"Resend-verification successful for email: {email}")
        return result
    except HTTPException as e:
        logger.warning(f"Resend-verification failed for email: {email} - {e.detail}")
        raise

@router.post("/logout", summary="Logout / Revoke JWT")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """
    Logout user and revoke their current JWT.
    """
    await auth_service.logout(current_user)
    return JSONResponse(
        {"detail": "Successfully logged out"},
        status_code=status.HTTP_200_OK
    )

@router.post("/refresh-token", summary="Refresh Access Token")
def refresh_token(refresh_token: str = Depends(oauth2_scheme)):
    try:
        tokens = auth_service.refresh_access_token(refresh_token)
        return JSONResponse(content=tokens, status_code=status.HTTP_200_OK)
    except HTTPException as e:
        raise e
    
@router.post("/send-forgot-password-code")
async def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = auth_service.get_user_by_email(db, payload.email)  # DB lookup
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await auth_service.send_reset_password_email(user)

@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    return await auth_service.reset_password(db, payload.email, payload.code, payload.new_password)

@router.get("/me", response_model=PublicUser, summary="Get current user profile")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return the logged-in user's profile using JWT sub claim.
    """
    user_data = auth_service.get_user_profile(db, current_user["sub"])
    return PublicUser.validate(user_data)  # Ensure it matches schema