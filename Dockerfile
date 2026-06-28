FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONUTF8=1

# Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Pre-download Whisper small model into the image layer (~464 MB).
# Avoids a cold-start download on the first STT request in production.
RUN python3 -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"

# App code (frontend is static — no build step) + backend
COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 8080

# On boot:
#   1. Ingest Gita verses into MongoDB (idempotent — skips if already loaded)
#   2. Seed reflective questions from CSV (idempotent — skips existing docs)
#   3. Start the API server
CMD ["sh", "-c", "cd backend && python scripts/ingest_gita.py && python scripts/import_questions.py --input questions_review.csv || true && python -m uvicorn app.main:app --host 0.0.0.0 --port 8080"]
