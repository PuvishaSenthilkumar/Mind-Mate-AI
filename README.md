# MindMate AI — Mental Wellness Companion

A full-stack wellness app for students and young adults: mood tracking, smart
journaling, an AI chat companion, habit tracking, mindfulness activities, and
a personalized dashboard.

> **MindMate AI is a wellness support tool. It is not a medical device, does
> not diagnose or treat any condition, and is not a replacement for therapy
> or professional mental-health care.** If you or someone you know is in
> crisis, contact local emergency services or a crisis line immediately.

---

## Tech Stack

- **Frontend:** React 18 + Vite, React Router, Recharts, Axios
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **Auth:** JWT (bcrypt password hashing)
- **AI:** Configurable — Anthropic (Claude), OpenAI, or an offline "mock" mode
  that works with zero API keys (great for local dev/demo)

---

## Project Structure

```
mindmate-ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entrypoint
│   │   ├── config.py          # env-based settings
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # ORM models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── auth.py            # JWT + password hashing
│   │   ├── ai_service.py      # LLM integration + sentiment detection
│   │   ├── safety.py          # crisis-language screening + resources
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── mood.py
│   │       ├── journal.py
│   │       ├── habits.py
│   │       ├── chat.py
│   │       ├── activities.py
│   │       └── dashboard.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/              # Landing, Login, Register, Dashboard, Chat, MoodTracker, Journal, Habits, Activities, Profile
    │   ├── components/         # Navbar, ProtectedRoute, MoodChart
    │   ├── context/AuthContext.jsx
    │   ├── api.js
    │   ├── App.jsx
    │   └── index.jsx
    ├── package.json
    ├── vite.config.js
    └── .env.example
```

---

## 1. Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 14+ running locally (or a connection string to a hosted instance)

---

## 2. Database Setup

Open a terminal (psql or any Postgres client) and run:

```sql
CREATE DATABASE mindmate_db;
CREATE USER mindmate_user WITH PASSWORD 'mindmate_pass';
GRANT ALL PRIVILEGES ON DATABASE mindmate_db TO mindmate_user;
```

You can use any credentials you like — just make sure they match `DATABASE_URL`
in `backend/.env` (next step).

---

## 3. Backend Setup

```bash
cd backend
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt

# Create your local env file
cp .env.example .env
```

Now open `backend/.env` and fill in your values:

```
DATABASE_URL=postgresql://mindmate_user:mindmate_pass@localhost:5432/mindmate_db
JWT_SECRET_KEY=<generate a long random string>
AI_PROVIDER=mock          # "mock" needs no API key — great for first run
# To use real AI replies, set AI_PROVIDER=anthropic (or openai) and fill in the key below
ANTHROPIC_API_KEY=
```

Generate a strong `JWT_SECRET_KEY` with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Run the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Tables are auto-created on first run. Verify it's alive:

```bash
curl http://localhost:8000/api/health
# {"status":"ok"}
```

Interactive API docs: **http://localhost:8000/docs**

---

## 4. Frontend Setup

Open a **new terminal**:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app will be available at **http://localhost:5173**. API calls to `/api/*`
are proxied to the backend on port 8000 automatically (see `vite.config.js`).

---

## 5. Using the App

1. Go to `http://localhost:5173`, click **Get Started**, and register an account.
2. Log a mood, write a journal entry, chat with the AI companion, set up a
   habit, and try a breathing exercise or meditation timer.
3. Visit the **Dashboard** to see your mood trend, habit progress, and
   personalized insights.
4. Visit **Profile** to review privacy controls and crisis resources.

### Switching to a real AI provider

By default `AI_PROVIDER=mock` in `.env` gives supportive canned-but-contextual
replies with zero setup, so the whole app is demoable offline. To enable real
LLM-generated responses:

1. Get an API key (e.g. from [console.anthropic.com](https://console.anthropic.com)).
2. In `backend/.env`, set `AI_PROVIDER=anthropic` and `ANTHROPIC_API_KEY=<your key>`.
3. Restart the backend.

No code changes are required to switch providers — everything is read from
environment variables in `app/config.py` and `app/ai_service.py`.

---

## 6. Safety Design Notes

- `app/safety.py` performs lightweight keyword screening on chat messages and
  journal entries. It is **not** a clinical detection tool — it exists only to
  trigger a supportive response and surface crisis resources.
- Crisis hotline/text-line details are fully configurable via environment
  variables (`CRISIS_HOTLINE_NAME`, `CRISIS_HOTLINE_NUMBER`, etc.) so they can
  be localized for different regions.
- The AI system prompt (`app/ai_service.py`) explicitly instructs the model
  never to diagnose or claim to treat any condition, and to encourage the user
  to reach out to a trusted person or professional when appropriate.
- Users can disable the AI chat entirely from **Profile → Privacy Controls**.

---

## 7. Running Both Servers Together (quick reference)

```bash
# Terminal 1
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Then open **http://localhost:5173**.

---

## 8. Production Notes

- Replace `Base.metadata.create_all()` in `app/main.py` with proper Alembic
  migrations before deploying.
- Set `ENVIRONMENT=production`, use a strong unique `JWT_SECRET_KEY`, and
  restrict `FRONTEND_ORIGIN` in CORS settings.
- Never commit `.env` files — both `backend/.env` and `frontend/.env` are
  already excluded via `.gitignore`.
- Put the frontend behind a proper build (`npm run build`) served by a static
  host or CDN, with the backend behind HTTPS.
