"""Authentication — MongoDB users collection + bcrypt hashed passwords.

Token format (stdlib-only, no PyJWT dependency):
    base64url(payload) + "." + HMAC-SHA256(payload, JWT_SECRET)
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

import bcrypt as _bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings
from .db import get_db

_USERS = "users"

TOKEN_TTL = 7 * 24 * 3600  # 7 days


def _hash(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt(rounds=12)).decode()


def _verify(password: str, hashed: str) -> bool:
    return _bcrypt.checkpw(password.encode(), hashed.encode())


def signup(username: str, password: str, display_name: str = "") -> None:
    """Insert new user. Raises ValueError if username is already taken."""
    db = get_db()
    if db[_USERS].find_one({"username": username}):
        raise ValueError("Username already taken.")
    db[_USERS].insert_one({
        "username": username,
        "password_hash": _hash(password),
        "display_name": display_name or username,
    })


def authenticate(username: str, password: str) -> bool:
    doc = get_db()[_USERS].find_one({"username": username})
    if not doc:
        return False
    return _verify(password, doc["password_hash"])


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
