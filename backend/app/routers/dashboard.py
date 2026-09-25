from datetime import date, timedelta
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _compute_streak(user_id: str, db: Session) -> tuple[int, int]:
    today = date.today()
    activity_dates = set()

    mood_entries = db.query(models.MoodEntry).filter(models.MoodEntry.user_id == user_id).all()
    for m in mood_entries:
        activity_dates.add(m.entry_date)

    journals = db.query(models.JournalEntry).filter(models.JournalEntry.user_id == user_id).all()
    for j in journals:
        activity_dates.add(j.created_at.date())

    habit_logs = db.query(models.HabitLog).join(models.Habit).filter(models.Habit.user_id == user_id).all()
    for h in habit_logs:
        activity_dates.add(h.log_date)

    chats = db.query(models.ChatMessage).filter(models.ChatMessage.user_id == user_id, models.ChatMessage.role == "user").all()
    for c in chats:
        activity_dates.add(c.created_at.date())

    activities = db.query(models.ActivityLog).filter(models.ActivityLog.user_id == user_id).all()
    for a in activities:
        activity_dates.add(a.created_at.date())

    sorted_dates = sorted(activity_dates, reverse=True)

    current_streak = 0
    if sorted_dates and sorted_dates[0] == today:
        current_streak = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == today - timedelta(days=current_streak):
                current_streak += 1
            else:
                break
    elif sorted_dates and sorted_dates[0] == today - timedelta(days=1):
        current_streak = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == today - timedelta(days=current_streak + 1):
                current_streak += 1
            else:
                break

    best_streak = 0
    if sorted_dates:
        streak = 1
        for i in range(1, len(sorted_dates)):
            expected = sorted_dates[i - 1] - timedelta(days=1)
            if sorted_dates[i] == expected:
                streak += 1
            else:
                best_streak = max(best_streak, streak)
                streak = 1
        best_streak = max(best_streak, streak)

    return current_streak, best_streak


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    week_ago = date.today() - timedelta(days=7)

    mood_entries = (
        db.query(models.MoodEntry)
        .filter(models.MoodEntry.user_id == current_user.id, models.MoodEntry.entry_date >= week_ago)
        .order_by(models.MoodEntry.entry_date.asc())
        .all()
    )
    mood_avg = round(sum(m.mood_score for m in mood_entries) / len(mood_entries), 2) if mood_entries else None

    habits = db.query(models.Habit).filter(models.Habit.user_id == current_user.id).all()
    habit_progress = []
    for h in habits:
        recent_logs = [l for l in h.logs if l.log_date >= week_ago]
        completion_rate = (
            round(sum(1 for l in recent_logs if l.completed) / len(recent_logs) * 100, 1)
            if recent_logs
            else 0
        )
        habit_progress.append({
            "habit_type": h.habit_type,
            "current_streak": h.current_streak,
            "best_streak": h.best_streak,
            "completion_rate_7d": completion_rate,
        })

    journals = db.query(models.JournalEntry).filter(models.JournalEntry.user_id == current_user.id).all()
    sentiment_counts = Counter(j.sentiment for j in journals if j.sentiment)

    current_streak, best_streak = _compute_streak(current_user.id, db)

    insights = []
    if mood_avg is not None:
        if mood_avg >= 4:
            insights.append("Your mood has been trending positive this week — keep doing what's working!")
        elif mood_avg <= 2.5:
            insights.append("Your mood has dipped this week. Consider a short mindfulness activity or reaching out to someone you trust.")
        else:
            insights.append("Your mood has been fairly steady this week.")
    else:
        insights.append("Log your mood daily to start seeing personalized trends.")

    low_streak_habits = [h for h in habit_progress if h["current_streak"] == 0]
    if low_streak_habits:
        insights.append("A few habits lost their streak — small consistent steps count more than perfection.")

    if sentiment_counts.get("negative", 0) > sentiment_counts.get("positive", 0):
        insights.append("Recent journal entries lean toward difficult emotions. Try a gratitude entry or talk to MindMate about what's on your mind.")

    if current_streak >= 7:
        insights.append(f"Incredible! You have a {current_streak}-day streak. Keep the momentum going!")

    return schemas.DashboardSummary(
        mood_average_7d=mood_avg,
        mood_trend=mood_entries,
        habit_progress=habit_progress,
        journal_count=len(journals),
        journal_sentiment_breakdown=dict(sentiment_counts),
        insights=insights,
        current_streak=current_streak,
        best_streak=best_streak,
    )
