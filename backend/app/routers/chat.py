from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth, ai_service, safety

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/history", response_model=List[schemas.ChatMessageOut])
def get_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.user_id == current_user.id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )


@router.post("", response_model=schemas.ChatResponse)
async def send_message(
    payload: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if not current_user.ai_chat_enabled:
        raise HTTPException(status_code=403, detail="AI chat is disabled in your privacy settings")

    emotion = ai_service.detect_emotion(payload.message)
    flagged = safety.screen_text_for_concern(payload.message)

    user_msg = models.ChatMessage(
        user_id=current_user.id,
        role="user",
        content=payload.message,
        detected_emotion=emotion,
        flagged_concern=flagged,
    )
    db.add(user_msg)
    db.commit()

    # Build short recent conversation context (last 10 messages)
    history = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.user_id == current_user.id)
        .order_by(models.ChatMessage.created_at.desc())
        .limit(10)
        .all()
    )
    history.reverse()
    conversation = [{"role": m.role, "content": m.content} for m in history]

    ai_text = await ai_service.get_ai_reply(conversation)

    assistant_msg = models.ChatMessage(
        user_id=current_user.id,
        role="assistant",
        content=ai_text,
        detected_emotion=None,
        flagged_concern=False,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    crisis_resources = safety.get_crisis_resources() if flagged else None

    return schemas.ChatResponse(
        reply=schemas.ChatMessageOut.model_validate(assistant_msg),
        crisis_resources=crisis_resources,
    )
