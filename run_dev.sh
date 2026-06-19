#!/bin/bash
export PYTHONPATH=/Users/rahul/Documents/GodAI/.venv/lib/python3.9/site-packages
exec /usr/bin/python3 -m uvicorn app.main:app \
  --app-dir /Users/rahul/Documents/GodAI/backend \
  --host 127.0.0.1 \
  --port 8080 \
  --reload
