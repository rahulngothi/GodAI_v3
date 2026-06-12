FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONUTF8=1

# Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# App code (frontend is static — no build step) + backend
COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 8080

# On boot: ingest the Gita into MongoDB (idempotent — skips if already loaded,
# downloads the dataset if missing), then serve.
CMD ["sh", "-c", "cd backend && python scripts/ingest_gita.py && python -m uvicorn app.main:app --host 0.0.0.0 --port 8080"]
