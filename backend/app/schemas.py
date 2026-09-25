from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------- Auth ----------
class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone_number: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetVerify(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    email_verified: bool
    phone_verified: bool
    data_sharing_opt_in: bool
    ai_chat_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    data_sharing_opt_in: Optional[bool] = None
    ai_chat_enabled: Optional[bool] = None


class OTPRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    method: str = Field(default="email", pattern="^(email|phone)$")

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v, info):
        if info.data.get("method") == "phone" and not v:
            raise ValueError("Phone number is required when method is 'phone'")
        return v


class OTPVerifyRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    otp_code: str = Field(min_length=6, max_length=6)
    method: str = Field(default="email", pattern="^(email|phone)$")


class OTPResponse(BaseModel):
    message: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class OTPVerifyResponse(BaseModel):
    message: str
    access_token: Optional[str] = None
    user: Optional["UserOut"] = None


# ---------- Mood ----------
class MoodCreate(BaseModel):
    mood_score: int = Field(ge=1, le=5)
    mood_label: str
    note: Optional[str] = None
    entry_date: Optional[date] = None


class MoodOut(BaseModel):
    id: str
    mood_score: int
    mood_label: str
    note: Optional[str]
    entry_date: date
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Journal ----------
class JournalCreate(BaseModel):
    title: Optional[str] = None
    content: str = Field(min_length=1, max_length=20000)


class JournalUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = Field(default=None, min_length=1, max_length=20000)


class JournalOut(BaseModel):
    id: str
    title: Optional[str]
    content: str
    ai_summary: Optional[str]
    sentiment: Optional[str]
    emotion_tags: Optional[str]
    flagged_concern: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Habits ----------
class HabitCreate(BaseModel):
    habit_type: str
    target_value: float
    unit: str


class HabitOut(BaseModel):
    id: str
    habit_type: str
    target_value: float
    unit: str
    current_streak: int
    best_streak: int

    class Config:
        from_attributes = True


class HabitLogCreate(BaseModel):
    value: float
    log_date: Optional[date] = None


class HabitLogOut(BaseModel):
    id: str
    log_date: date
    value: float
    completed: bool

    class Config:
        from_attributes = True


# ---------- Chat ----------
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    detected_emotion: Optional[str]
    flagged_concern: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    reply: ChatMessageOut
    crisis_resources: Optional[dict] = None


# ---------- Activities ----------
class ActivityLogCreate(BaseModel):
    activity_type: str
    duration_seconds: int = 0
    notes: Optional[str] = None


class ActivityLogOut(BaseModel):
    id: str
    activity_type: str
    duration_seconds: int
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Dashboard ----------
class DashboardSummary(BaseModel):
    mood_average_7d: Optional[float]
    mood_trend: List[MoodOut]
    habit_progress: List[dict]
    journal_count: int
    journal_sentiment_breakdown: dict
    insights: List[str]
    current_streak: int = 0
    best_streak: int = 0
