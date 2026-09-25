"""
Safety utilities.

IMPORTANT: This module performs lightweight, keyword-based screening to flag
messages that *may* indicate the user is in distress. It is NOT a diagnostic
tool, does not detect all risk situations, and must never be presented to
users as clinically validated. Its only job is to:
  1. Flag conversation/journal content for a supportive, non-diagnostic reply.
  2. Surface configurable crisis resources so the user can reach a real human.

This is a safety net, not a substitute for professional judgment.
"""
from app.config import settings

# Deliberately broad, non-exhaustive phrase list. Kept at the pattern level.
CONCERN_KEYWORDS = [
    "kill myself", "suicide", "end my life", "want to die", "not worth living",
    "hurt myself", "self harm", "self-harm", "can't go on", "no reason to live",
    "better off dead", "give up on life",
]


def screen_text_for_concern(text: str) -> bool:
    """Return True if the text contains language that may indicate crisis risk."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in CONCERN_KEYWORDS)


def get_crisis_resources() -> dict:
    return {
        "message": (
            "It sounds like you might be going through something really hard. "
            "You deserve support from a real person who can help — please consider "
            "reaching out to someone you trust or a crisis service."
        ),
        "hotline_name": settings.CRISIS_HOTLINE_NAME,
        "hotline_number": settings.CRISIS_HOTLINE_NUMBER,
        "text_line": settings.CRISIS_TEXT_LINE,
        "international_resources_url": settings.CRISIS_INTERNATIONAL_URL,
    }


SAFETY_DISCLAIMER = (
    "MindMate AI is a wellness support tool, not a medical device or a "
    "replacement for therapy, counseling, or professional mental-health care. "
    "It cannot diagnose or treat any condition. If you are in crisis or in "
    "danger, please contact local emergency services or a crisis line immediately."
)
