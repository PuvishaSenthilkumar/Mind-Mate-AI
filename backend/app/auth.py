from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        pwd_bytes = plain.encode("utf-8")[:72]
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def generate_otp() -> str:
    return f"{secrets.randbelow(900000) + 100000:06d}"


def send_email_otp(email: str, otp_code: str, purpose: str = "verify") -> bool:
    """Send OTP email. Returns True if sent successfully, False otherwise."""
    subject = "MindMate AI - Verify your email"
    if purpose == "verify":
        body = (
            f"Hi,\n\n"
            f"Your MindMate AI verification code is: {otp_code}\n\n"
            f"This code will expire in {settings.EMAIL_OTP_EXPIRE_MINUTES} minutes.\n\n"
            f"If you did not request this, please ignore this email.\n\n"
            f"— MindMate AI Team"
        )
    else:
        subject = "MindMate AI - Password reset code"
        body = (
            f"Hi,\n\n"
            f"Your MindMate AI password reset code is: {otp_code}\n\n"
            f"This code will expire in {settings.EMAIL_OTP_EXPIRE_MINUTES} minutes.\n\n"
            f"If you did not request this, please ignore this email.\n\n"
            f"— MindMate AI Team"
        )

    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print(f"[DEV OTP] To: {email} | Subject: {subject} | OTP: {otp_code}")
        return False

    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import smtplib

        msg = MIMEMultipart()
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL SENT] OTP email sent to {email}")
        return True
    except Exception as exc:
        print(f"[EMAIL ERROR] Failed to send OTP email to {email}: {exc}")
        print(f"[DEV OTP] To: {email} | Subject: {subject} | OTP: {otp_code}")
        return False


def send_sms_otp(phone_number: str, otp_code: str, purpose: str = "verify") -> bool:
    """Send OTP via SMS using MSG91. Returns True if sent successfully."""
    if not settings.MSG91_AUTH_KEY:
        print(f"[DEV OTP] To: {phone_number} | OTP: {otp_code}")
        return False

    try:
        import urllib.request
        import urllib.parse
        import json

        if purpose == "verify":
            message = f"Your MindMate AI verification code is: {otp_code}. It expires in {settings.SMS_OTP_EXPIRE_MINUTES} minutes."
        else:
            message = f"Your MindMate AI password reset code is: {otp_code}. It expires in {settings.SMS_OTP_EXPIRE_MINUTES} minutes."

        params = {
            "authkey": settings.MSG91_AUTH_KEY,
            "mobiles": phone_number,
            "message": message,
            "sender": settings.MSG91_SENDER_ID,
            "route": "4",
            "country": "91",
        }

        if settings.MSG91_TEMPLATE_ID:
            params["DLT_TE_ID"] = settings.MSG91_TEMPLATE_ID

        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request("https://api.msg91.com/api/v5/otp", data=data)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            if result.get("type") == "success":
                print(f"[SMS SENT] OTP SMS sent to {phone_number}")
                return True
            else:
                print(f"[SMS ERROR] MSG91 returned: {result}")
                if settings.ENVIRONMENT == "development":
                    print(f"[DEV OTP] To: {phone_number} | OTP: {otp_code}")
                return False
    except Exception as exc:
        print(f"[SMS ERROR] Failed to send OTP SMS to {phone_number}: {exc}")
        if settings.ENVIRONMENT == "development":
            print(f"[DEV OTP] To: {phone_number} | OTP: {otp_code}")
        return False
