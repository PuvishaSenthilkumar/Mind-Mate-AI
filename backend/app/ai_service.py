"""
AI integration layer.

Reads the API key/model from environment variables (see config.py) —
never hard-coded. Supports:
  - "gemini": Google Gemini via the Generative Language API
  - "mock": offline fallback so the app still runs without any key
            (useful for local dev/demo).
"""
import asyncio  # noqa: F401 — used for Gemini rate-limit backoff
import logging
from typing import List, Dict

import certifi
import httpx
import pip_system_certs.bootstrap  # noqa: F401 — use Windows/system CA store
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

from app.config import settings

logger = logging.getLogger(__name__)


def _http_client() -> httpx.AsyncClient:
    """Use certifi CA bundle so HTTPS works on Windows dev machines."""
    return httpx.AsyncClient(timeout=30, verify=certifi.where())


SYSTEM_PROMPT = """You are MindMate, a warm, supportive wellness companion for \
students and young adults. You are NOT a therapist, doctor, or crisis counselor, \
and you must never diagnose, prescribe, or claim to treat any mental health \
condition. Keep responses empathetic, brief (3-6 sentences), validating, and \
practical (breathing exercises, journaling prompts, healthy habits, encouragement \
to talk to trusted people or professionals when appropriate). If the user expresses \
thoughts of self-harm or suicide, respond with warmth, take it seriously, encourage \
them to reach out to a trusted person or crisis line right now, and do not try to \
handle it alone as an AI."""


def _to_gemini_contents(messages: List[Dict[str, str]]) -> List[types.Content]:
    """Map chat roles to Gemini's user/model format."""
    contents: List[types.Content] = []
    for message in messages:
        role = "model" if message["role"] == "assistant" else "user"
        contents.append(
            types.Content(role=role, parts=[types.Part(text=message["content"])])
        )
    return contents


def _is_transient(exc: BaseException) -> bool:
    if isinstance(exc, (ClientError, ServerError)):
        return getattr(exc, "code", None) in (429, 500, 502, 503, 504)
    if isinstance(exc, RuntimeError):
        return "Event loop is closed" in str(exc)
    if isinstance(exc, (httpx.NetworkError, httpx.RemoteProtocolError, httpx.TimeoutException)):
        return True
    return False


async def _call_gemini(messages: List[Dict[str, str]]) -> str:
    if not settings.GEMINI_API_KEY:
        return _mock_reply(messages)

    history = _to_gemini_contents(messages[:-1]) if len(messages) > 1 else []
    last_message = messages[-1]["content"] if messages else "Hello"

    max_retries = 5
    base_delay = 1.0

    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            chat = client.aio.chats.create(
                model=settings.GEMINI_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=1024,
                    temperature=0.7,
                ),
                history=history,
            )
            response = await chat.send_message(last_message)
            reply = (response.text or "").strip()
            if not reply:
                raise ValueError("Gemini returned an empty response")
            return reply
        except BaseException as exc:
            if _is_transient(exc) and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning("Gemini transient error (%s: %s), retrying in %.1fs...", type(exc).__name__, exc, delay)
                await asyncio.sleep(delay)
                continue
            raise

    raise RuntimeError("Gemini retries exhausted")


def _mock_reply(messages: List[Dict[str, str]]) -> str:
    """Offline fallback used when no API key is configured, so the app is
    still fully demoable without any external service."""
    last = messages[-1]["content"] if messages else ""
    emotion = detect_emotion(last)
    templates = {
        "positive": "I'm really glad to hear that! Keep noting what's working for you — small wins add up. Want to log this mood or jot a gratitude note?",
        "negative": "That sounds really tough, and it makes sense you'd feel that way. You don't have to carry it alone — would it help to talk through what's weighing on you, or try a short breathing exercise together?",
        "neutral": "Thanks for sharing that with me. How has your day been treating you overall — anything on your mind you'd like to unpack?",
    }
    return templates.get(emotion, templates["neutral"])


async def get_ai_reply(conversation: List[Dict[str, str]]) -> str:
    try:
        return await _call_gemini(conversation)
    except Exception as exc:
        logger.exception("AI provider gemini failed: %s", exc)
        return _mock_reply(conversation)


# ---- Lightweight sentiment/emotion detection (rule-based, no external calls) ----
POSITIVE_WORDS = {"happy", "great", "good", "grateful", "excited", "calm", "relaxed",
                   "proud", "hopeful", "joy", "love", "peaceful", "confident"}
NEGATIVE_WORDS = {"sad", "anxious", "stressed", "tired", "angry", "overwhelmed",
                    "depressed", "lonely", "worried", "scared", "hopeless", "upset",
                    "frustrated", "exhausted"}


def detect_emotion(text: str) -> str:
    lowered = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in lowered)
    neg = sum(1 for w in NEGATIVE_WORDS if w in lowered)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


async def summarize_journal(content: str) -> str:
    """Ask the LLM for a short empathetic summary; falls back to a naive summary."""
    prompt = (
        "Summarize the following personal journal entry in 2-3 supportive, "
        "non-judgmental sentences, reflecting the writer's feelings without "
        "giving medical advice:\n\n" + content
    )
    reply = await get_ai_reply([{"role": "user", "content": prompt}])
    return reply
