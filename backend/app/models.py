import uuid
from datetime import datetime, date, timedelta
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.config import settings
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=True, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Email / Phone verification
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    email_verification_sent_at = Column(DateTime, nullable=True)

    # Privacy controls
    data_sharing_opt_in = Column(Boolean, default=False)
    ai_chat_enabled = Column(Boolean, default=True)

    mood_entries = relationship("MoodEntry", back_populates="user", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")


class EmailOTP(Base):
    __tablename__ = "email_otps"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String(255), nullable=True, index=True)
    phone_number = Column(String(20), nullable=True, index=True)
    otp_code = Column(String(6), nullable=False)
    purpose = Column(String(20), nullable=False, default="verify")  # verify | reset
    method = Column(String(10), nullable=False, default="email")  # email | phone
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    mood_score = Column(Integer, nullable=False)  # 1 (very low) - 5 (very good)
    mood_label = Column(String(30), nullable=False)  # e.g. "happy", "anxious"
    note = Column(Text, nullable=True)
    entry_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mood_entries")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=True)
    sentiment = Column(String(30), nullable=True)  # positive/neutral/negative
    emotion_tags = Column(String(255), nullable=True)  # comma separated
    flagged_concern = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="journal_entries")


class Habit(Base):
    __tablename__ = "habits"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    habit_type = Column(String(30), nullable=False)  # sleep, water, exercise, screen_time
    target_value = Column(Float, nullable=False)  # e.g. hours, liters, minutes
    unit = Column(String(20), nullable=False)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    habit_id = Column(UUID(as_uuid=False), ForeignKey("habits.id"), nullable=False)
    log_date = Column(Date, default=date.today)
    value = Column(Float, nullable=False)
    completed = Column(Boolean, default=False)

    habit = relationship("Habit", back_populates="logs")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    role = Column(String(10), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    detected_emotion = Column(String(30), nullable=True)
    flagged_concern = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(40), nullable=False)  # breathing, meditation, gratitude, stress_relief
    duration_seconds = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activity_logs")
