"""Authentication — hardcoded users for now (test1/test2/test3, password "test").

Tokens are stdlib-only HMAC-SHA256 signed (no external JWT dependency):
    base64(payload).signature   where payload = {"u": username, "exp": unix}
Swap USERS for a Mongo collection + hashed passwords when real signup lands.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

# Temporary hardcoded users (per product decision 2026-06-12).
USERS: dict[str, str] = {"rahul": "rahul", "rishabh": "rishabh", "sid": "sid"}

TOKEN_TTL = 7 * 24 * 3600  # 7 days


def authenticate(username: str, password: str) -> bool:
    expected = USERS.get(username)
    return expected is not None and hmac.compare_digest(expected, password)


def _sign(payload: bytes) -> str:
    return hmac.new(settings.jwt_secret.encode(), payload, hashlib.sha256).hexdigest()


def create_token(username: str) -> str:
    payload = base64.urlsafe_b64encode(
        json.dumps({"u": username, "exp": int(time.time()) + TOKEN_TTL}).encode()
    ).decode()
    return f"{payload}.{_sign(payload.encode())}"


def verify_token(token: str) -> str | None:
    try:
        payload, sig = token.rsplit(".", 1)
        if not hmac.compare_digest(sig, _sign(payload.encode())):
            return None
        data = json.loads(base64.urlsafe_b64decode(payload))
        if data["exp"] < time.time():
            return None
        return data["u"]
    except Exception:
        return None


_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    if creds is None:
        raise HTTPException(status_code=401, detail="Please sign in.")
    user = verify_token(creds.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired — please sign in again.")
    return user
