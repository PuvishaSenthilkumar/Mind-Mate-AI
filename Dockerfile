FROM node:20-alpine AS fe-build
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm install --no-fund --no-audit && npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/app ./backend/app
COPY --from=fe-build /fe/dist ./frontend/dist

EXPOSE 7860
WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn app.main:app --app-dir /app/backend --host 0.0.0.0 --port ${PORT:-7860}"]