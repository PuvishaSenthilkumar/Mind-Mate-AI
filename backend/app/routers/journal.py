from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth, ai_service, safety

router = APIRouter(prefix="/api/journal", tags=["journal"])


@router.post("", response_model=schemas.JournalOut, status_code=201)
async def create_journal(
    payload: schemas.JournalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    emotion = ai_service.detect_emotion(payload.content)
    flagged = safety.screen_text_for_concern(payload.content)
    summary = await ai_service.summarize_journal(payload.content)

    entry = models.JournalEntry(
        user_id=current_user.id,
        title=payload.title,
        content=payload.content,
        ai_summary=summary,
        sentiment=emotion,
        emotion_tags=emotion,
        flagged_concern=flagged,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=List[schemas.JournalOut])
def list_journals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.JournalEntry)
        .filter(models.JournalEntry.user_id == current_user.id)
        .order_by(models.JournalEntry.created_at.desc())
        .all()
    )


@router.get("/{journal_id}", response_model=schemas.JournalOut)
def get_journal(
    journal_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    entry = (
        db.query(models.JournalEntry)
        .filter(models.JournalEntry.id == journal_id, models.JournalEntry.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry


@router.put("/{journal_id}", response_model=schemas.JournalOut)
async def update_journal(
    journal_id: str,
    payload: schemas.JournalUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    entry = (
        db.query(models.JournalEntry)
        .filter(models.JournalEntry.id == journal_id, models.JournalEntry.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    if payload.title is not None:
        entry.title = payload.title
    if payload.content is not None:
        entry.content = payload.content
        entry.sentiment = ai_service.detect_emotion(payload.content)
        entry.emotion_tags = entry.sentiment
        entry.flagged_concern = safety.screen_text_for_concern(payload.content)
        entry.ai_summary = await ai_service.summarize_journal(payload.content)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{journal_id}", status_code=204)
def delete_journal(
    journal_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    entry = (
        db.query(models.JournalEntry)
        .filter(models.JournalEntry.id == journal_id, models.JournalEntry.user_id == current_user.id)
        .first()
    )
    if entry:
        db.delete(entry)
        db.commit()
    return None
