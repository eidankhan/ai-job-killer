import os, smtplib, ssl
from email.message import EmailMessage
from fastapi import HTTPException, status
from app.core.logger import logger
from pydantic import EmailStr, ValidationError, parse_obj_as


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER or "no-reply@example.com")
CODE_TTL_MINUTES = 15
DISPOSABLE_DOMAINS = {"mailinator.com", "10minutemail.com"}


def send_email(to_email: str, subject: str, html_body: str, text_body: str | None = None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    if text_body:
        logger.info("Sending email with both HTML and plain text parts")
        msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

def validate_and_normalize_email(email: str) -> str:
    """
    Validates and normalizes an email address using Pydantic v2.
    
    - Ensures proper email format
    - Converts to lowercase and strips spaces
    - Blocks disposable email domains
    Raises HTTPException if invalid.
    """
    email = email.strip().lower()

    # Validate format using Pydantic EmailStr
    try:
        normalized = parse_obj_as(EmailStr, email)
    except ValidationError:
        logger.warning(f"Invalid email format provided: {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address."
        )

    # Check for disposable domains
    domain = str(normalized).split("@")[-1]
    if domain in DISPOSABLE_DOMAINS:
        logger.warning(f"Disposable email not allowed: {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Disposable email not allowed."
        )

    return str(normalized)
    
def generate_verification_email_template(user_email: str, code: str) -> tuple[str, str]:
    """
    Generates the subject, HTML body, and plain text body for a verification email.

    Args:
        user_email (str): The recipient's email address.
        code (str): The verification code.

    Returns:
        tuple[str, str]: (subject, html_body, text_body)
    """
    subject = "Your ai-job-killer Verification Code"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; 
        border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f9f9f9;">
        <h2 style="color: #333;">Email Verification</h2>
        <p style="font-size: 16px; color: #555;">
            Hello <strong>{user_email}</strong>,<br><br>
            Use the verification code below to complete your signup:
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
        f"Hello {user_email},\n"
        f"Your verification code is: {code}\n"
        f"Expires in {CODE_TTL_MINUTES} minutes."
    )

    return subject, html_body, text_body
