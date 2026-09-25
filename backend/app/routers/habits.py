from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/habits", tags=["habits"])


@router.post("", response_model=schemas.HabitOut, status_code=201)
def create_habit(
    payload: schemas.HabitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    habit = models.Habit(
        user_id=current_user.id,
        habit_type=payload.habit_type,
        target_value=payload.target_value,
        unit=payload.unit,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("", response_model=List[schemas.HabitOut])
def list_habits(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Habit).filter(models.Habit.user_id == current_user.id).all()


@router.delete("/{habit_id}", status_code=204)
def delete_habit(
    habit_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    habit = (
        db.query(models.Habit)
        .filter(models.Habit.id == habit_id, models.Habit.user_id == current_user.id)
        .first()
    )
    if habit:
        db.delete(habit)
        db.commit()
    return None


@router.post("/{habit_id}/log", response_model=schemas.HabitLogOut, status_code=201)
def log_habit(
    habit_id: str,
    payload: schemas.HabitLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    habit = (
        db.query(models.Habit)
        .filter(models.Habit.id == habit_id, models.Habit.user_id == current_user.id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log_date = payload.log_date or date.today()
    completed = payload.value >= habit.target_value

    existing_log = next((l for l in habit.logs if l.log_date == log_date), None)
    if existing_log:
        existing_log.value = payload.value
        existing_log.completed = completed
        log = existing_log
    else:
        log = models.HabitLog(
            habit_id=habit.id, log_date=log_date, value=payload.value, completed=completed
        )
        db.add(log)

    db.flush()

    # Recompute streak: consecutive completed days ending today (or log_date)
    yesterday = log_date - timedelta(days=1)
    prev_log = next((l for l in habit.logs if l.log_date == yesterday and l.completed), None)
    if completed:
        habit.current_streak = (habit.current_streak + 1) if prev_log else 1
        habit.best_streak = max(habit.best_streak, habit.current_streak)
    else:
        habit.current_streak = 0

    db.commit()
    db.refresh(log)
    return log


@router.get("/{habit_id}/logs", response_model=List[schemas.HabitLogOut])
def get_habit_logs(
    habit_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    habit = (
        db.query(models.Habit)
        .filter(models.Habit.id == habit_id, models.Habit.user_id == current_user.id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return sorted(habit.logs, key=lambda l: l.log_date)
