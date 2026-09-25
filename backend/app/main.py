from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time

from app.database import Base, engine
from app.config import settings
from app import safety
from app.routers import auth, mood, journal, habits, chat, activities, dashboard, debug
from app import models  # noqa: F401  registers tables so create_all works


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        import time
        request_id = str(int(time.time() * 1000))
        request.state.request_id = request_id
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 1)
        print(f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} ({duration}ms)")
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    async def dispatch(self, request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        auth_paths = ["/api/auth/register", "/api/auth/login", "/api/auth/send-otp", "/api/auth/request-otp", "/api/auth/verify-otp", "/api/auth/forgot-password", "/api/auth/reset-password"]

        if any(path.startswith(p) for p in auth_paths):
            now = time.time()
            key = f"{client_ip}:{path}"
            timestamps = self.requests.get(key, [])
            timestamps = [t for t in timestamps if now - t < self.window_seconds]
            if len(timestamps) >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                )
            timestamps.append(now)
            self.requests[key] = timestamps

        return await call_next(request)


app = FastAPI(
    title="MindMate AI",
    description="Mental wellness companion API. Not a medical device or diagnostic tool.",
    version="1.0.0",
    lifespan=lifespan,
)

if settings.ENVIRONMENT == "development":
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, max_requests=20, window_seconds=60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN] if settings.ENVIRONMENT == "production" else [settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(mood.router)
app.include_router(journal.router)
app.include_router(habits.router)
app.include_router(chat.router)
app.include_router(activities.router)
app.include_router(dashboard.router)

if settings.ENVIRONMENT == "development":
    app.include_router(debug.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/safety-info")
def safety_info():
    """Public, non-authenticated endpoint with disclaimer + crisis resources
    so the frontend can render them on any page (e.g. landing page footer)."""
    return {
        "disclaimer": safety.SAFETY_DISCLAIMER,
        "resources": safety.get_crisis_resources(),
    }
