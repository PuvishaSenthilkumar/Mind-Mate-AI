from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/mood", tags=["mood"])


@router.post("", response_model=schemas.MoodOut, status_code=201)
def create_mood(
    payload: schemas.MoodCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    entry = models.MoodEntry(
        user_id=current_user.id,
        mood_score=payload.mood_score,
        mood_label=payload.mood_label,
        note=payload.note,
        entry_date=payload.entry_date or date.today(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=List[schemas.MoodOut])
def list_moods(
    start: Optional[date] = None,
    end: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.MoodEntry).filter(models.MoodEntry.user_id == current_user.id)
    if start:
        query = query.filter(models.MoodEntry.entry_date >= start)
    if end:
        query = query.filter(models.MoodEntry.entry_date <= end)
    return query.order_by(models.MoodEntry.entry_date.asc()).all()


@router.delete("/{mood_id}", status_code=204)
def delete_mood(
    mood_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    entry = (
        db.query(models.MoodEntry)
        .filter(models.MoodEntry.id == mood_id, models.MoodEntry.user_id == current_user.id)
        .first()
    )
    if entry:
        db.delete(entry)
        db.commit()
    return None
