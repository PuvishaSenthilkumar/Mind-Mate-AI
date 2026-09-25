from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app import models
from app.config import settings

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/latest-otp")
def get_latest_otp(email: str = "", phone_number: str = "", db: Session = Depends(get_db)):
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=404, detail="Not found")

    query = db.query(models.EmailOTP).filter(
        models.EmailOTP.purpose == "verify",
        models.EmailOTP.expires_at > datetime.utcnow(),
    )

    if email:
        query = query.filter(models.EmailOTP.email == email)
    elif phone_number:
        query = query.filter(models.EmailOTP.phone_number == phone_number)
    else:
        raise HTTPException(status_code=400, detail="email or phone_number is required")

    otp = query.order_by(models.EmailOTP.created_at.desc()).first()
    if not otp:
        raise HTTPException(status_code=404, detail="No active OTP found")

    return {
        "email": otp.email,
        "phone_number": otp.phone_number,
        "otp_code": otp.otp_code,
        "method": otp.method,
        "purpose": otp.purpose,
        "expires_at": otp.expires_at.isoformat(),
        "created_at": otp.created_at.isoformat(),
    }
