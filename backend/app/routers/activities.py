from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.post("", response_model=schemas.ActivityLogOut, status_code=201)
def log_activity(
    payload: schemas.ActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    log = models.ActivityLog(
        user_id=current_user.id,
        activity_type=payload.activity_type,
        duration_seconds=payload.duration_seconds,
        notes=payload.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=List[schemas.ActivityLogOut])
def list_activities(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.user_id == current_user.id)
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )
