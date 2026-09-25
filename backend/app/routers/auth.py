from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

OTP_COOLDOWN_SECONDS = 60
_otp_cooldowns: dict[str, float] = {}


def _get_cooldown_key(email: str = "", phone_number: str = "") -> str:
    return email or phone_number or ""


def _check_otp_cooldown(key: str) -> int:
    now = datetime.utcnow().timestamp()
    last_sent = _otp_cooldowns.get(key, 0)
    elapsed = now - last_sent
    remaining = max(0, int(OTP_COOLDOWN_SECONDS - elapsed))
    if remaining > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {remaining} seconds before requesting another OTP.",
        )
    _otp_cooldowns[key] = now
    return 0


@router.post("/register", response_model=schemas.OTPResponse, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    if payload.phone_number:
        existing_phone = db.query(models.User).filter(models.User.phone_number == payload.phone_number).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="An account with this phone number already exists")

    user = models.User(
        full_name=payload.full_name,
        email=payload.email,
        phone_number=payload.phone_number,
        hashed_password=auth.hash_password(payload.password),
        email_verified=False,
        phone_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _check_otp_cooldown(_get_cooldown_key(email=user.email, phone_number=user.phone_number or ""))
    result = _send_or_store_otp(db, email=user.email, purpose="verify", method="email")
    if result["sent"]:
        return schemas.OTPResponse(
            message="Account created. Please verify your email with the OTP sent.",
            email=user.email,
        )
    else:
        return schemas.OTPResponse(
            message="Account created but email delivery failed. Check your spam folder or try again.",
            email=user.email,
        )


@router.post("/send-otp", response_model=schemas.OTPResponse)
def send_otp(payload: schemas.OTPRequest, db: Session = Depends(get_db)):
    """Send OTP via email or phone."""
    if payload.method == "phone":
        if not payload.phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required for phone OTP")
        user = db.query(models.User).filter(models.User.phone_number == payload.phone_number).first()
        if not user:
            raise HTTPException(status_code=404, detail="No account found with this phone number")
        if user.phone_verified:
            raise HTTPException(status_code=400, detail="Phone number is already verified")

        _check_otp_cooldown(_get_cooldown_key(phone_number=payload.phone_number))
        result = _send_or_store_otp(db, phone_number=payload.phone_number, purpose="verify", method="phone")
        if result["sent"]:
            return schemas.OTPResponse(message="OTP sent to your phone.", phone_number=payload.phone_number)
        else:
            return schemas.OTPResponse(
                message="SMS could not be sent. Please check your number or try again.",
                phone_number=payload.phone_number,
            )
    else:
        if not payload.email:
            raise HTTPException(status_code=400, detail="Email is required for email OTP")
        user = db.query(models.User).filter(models.User.email == payload.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="No account found with this email")
        if user.email_verified:
            raise HTTPException(status_code=400, detail="Email is already verified")

        _check_otp_cooldown(_get_cooldown_key(email=payload.email))
        result = _send_or_store_otp(db, email=payload.email, purpose="verify", method="email")
        if result["sent"]:
            return schemas.OTPResponse(message="OTP sent to your email.", email=payload.email)
        else:
            return schemas.OTPResponse(
                message="Email could not be sent. Please check your inbox or try again.",
                email=payload.email,
            )


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.email_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please verify your email before logging in.",
        )

    token = auth.create_access_token({"sub": user.id})
    return schemas.TokenResponse(access_token=token, user=schemas.UserOut.model_validate(user))


@router.post("/forgot-password", response_model=schemas.OTPResponse)
def forgot_password(payload: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    """Send a password reset OTP to the user's email."""
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user:
        _check_otp_cooldown(_get_cooldown_key(email=payload.email))
        _send_or_store_otp(db, email=user.email, purpose="reset", method="email")
    return schemas.OTPResponse(message="If an account exists with this email, a password reset code has been sent.", email=payload.email)


@router.post("/reset-password", response_model=schemas.OTPResponse)
def reset_password(payload: schemas.PasswordResetVerify, db: Session = Depends(get_db)):
    """Verify the reset OTP and update the user's password."""
    otp_entry = db.query(models.EmailOTP).filter(
        models.EmailOTP.otp_code == payload.otp_code,
        models.EmailOTP.purpose == "reset",
        models.EmailOTP.method == "email",
        models.EmailOTP.email == payload.email,
        models.EmailOTP.expires_at > datetime.utcnow(),
    ).order_by(models.EmailOTP.created_at.desc()).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = auth.hash_password(payload.new_password)
    db.delete(otp_entry)
    db.commit()

    return schemas.OTPResponse(message="Your password has been reset successfully.")


@router.post("/request-otp", response_model=schemas.OTPResponse)
def request_otp(payload: schemas.OTPRequest, db: Session = Depends(get_db)):
    """Resend OTP via email or phone."""
    if payload.method == "phone":
        if not payload.phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required")
        user = db.query(models.User).filter(models.User.phone_number == payload.phone_number).first()
        if not user:
            raise HTTPException(status_code=404, detail="No account found with this phone number")
        if user.phone_verified:
            raise HTTPException(status_code=400, detail="Phone is already verified")

        _check_otp_cooldown(_get_cooldown_key(phone_number=payload.phone_number))
        result = _send_or_store_otp(db, phone_number=payload.phone_number, purpose="verify", method="phone")
        if result["sent"]:
            return schemas.OTPResponse(message="OTP sent to your phone.", phone_number=payload.phone_number)
        else:
            return schemas.OTPResponse(
                message="SMS failed. Please check your number or try again.",
                phone_number=payload.phone_number,
            )
    else:
        if not payload.email:
            raise HTTPException(status_code=400, detail="Email is required")
        user = db.query(models.User).filter(models.User.email == payload.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="No account found with this email")
        if user.email_verified:
            raise HTTPException(status_code=400, detail="Email is already verified")

        _check_otp_cooldown(_get_cooldown_key(email=payload.email))
        result = _send_or_store_otp(db, email=payload.email, purpose="verify", method="email")
        if result["sent"]:
            return schemas.OTPResponse(message="OTP sent to your email.", email=payload.email)
        else:
            return schemas.OTPResponse(
                message="Email failed. Please check your inbox or try again.",
                email=payload.email,
            )


@router.post("/verify-otp", response_model=schemas.OTPVerifyResponse)
def verify_otp(payload: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verify OTP sent via email or phone."""
    query = db.query(models.EmailOTP).filter(
        models.EmailOTP.otp_code == payload.otp_code,
        models.EmailOTP.purpose == "verify",
        models.EmailOTP.expires_at > datetime.utcnow(),
    )

    if payload.method == "phone":
        if not payload.phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required for phone verification")
        query = query.filter(
            models.EmailOTP.phone_number == payload.phone_number,
            models.EmailOTP.method == "phone",
        )
    else:
        if not payload.email:
            raise HTTPException(status_code=400, detail="Email is required for email verification")
        query = query.filter(
            models.EmailOTP.email == payload.email,
            models.EmailOTP.method == "email",
        )

    otp_entry = query.order_by(models.EmailOTP.created_at.desc()).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    if payload.method == "phone":
        user = db.query(models.User).filter(models.User.phone_number == payload.phone_number).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.phone_verified = True
    else:
        user = db.query(models.User).filter(models.User.email == payload.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.email_verified = True

    db.delete(otp_entry)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": user.id})
    return schemas.OTPVerifyResponse(
        message="Verified successfully.",
        access_token=token,
        user=schemas.UserOut.model_validate(user),
    )


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@router.put("/me", response_model=schemas.UserOut)
def update_me(
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number
    if payload.data_sharing_opt_in is not None:
        current_user.data_sharing_opt_in = payload.data_sharing_opt_in
    if payload.ai_chat_enabled is not None:
        current_user.ai_chat_enabled = payload.ai_chat_enabled
    db.commit()
    db.refresh(current_user)
    return current_user


def _send_or_store_otp(
    db: Session,
    email: str = None,
    phone_number: str = None,
    purpose: str = "verify",
    method: str = "email",
) -> dict:
    otp_code = auth.generate_otp()
    expire_minutes = settings.EMAIL_OTP_EXPIRE_MINUTES if method == "email" else settings.SMS_OTP_EXPIRE_MINUTES
    expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)

    # Delete old unused OTPs for same target
    if method == "phone" and phone_number:
        db.query(models.EmailOTP).filter(
            models.EmailOTP.phone_number == phone_number,
            models.EmailOTP.purpose == purpose,
            models.EmailOTP.method == "phone",
            models.EmailOTP.expires_at > datetime.utcnow(),
        ).delete(synchronize_session=False)
    elif method == "email" and email:
        db.query(models.EmailOTP).filter(
            models.EmailOTP.email == email,
            models.EmailOTP.purpose == purpose,
            models.EmailOTP.method == "email",
            models.EmailOTP.expires_at > datetime.utcnow(),
        ).delete(synchronize_session=False)

    otp_entry = models.EmailOTP(
        email=email,
        phone_number=phone_number,
        otp_code=otp_code,
        purpose=purpose,
        method=method,
        expires_at=expires_at,
    )
    db.add(otp_entry)
    db.commit()

    if method == "phone":
        sent = auth.send_sms_otp(phone_number, otp_code, purpose=purpose)
    else:
        sent = auth.send_email_otp(email, otp_code, purpose=purpose)

    return {"otp_code": otp_code, "sent": sent}
