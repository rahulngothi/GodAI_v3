"""In-memory rate limiting (single-process app, so this is sufficient).

Two layers:
  * per-user sliding window — a reasonable personal allowance
  * global sliding window — keeps total LLM calls safely under the NVIDIA/Kimi
    free-tier ceiling of 40 requests/minute
"""
from __future__ import annotations

import time
from collections import deque

from fastapi import HTTPException

PER_USER_PER_MIN = 8
GLOBAL_PER_MIN = 30  # safety margin under Kimi's 40/min

_user_hits: dict[str, deque] = {}
_global_hits: deque = deque()


def check(user: str) -> None:
    """Raise 429 if the user or the app as a whole is over its window."""
    now = time.time()

    q = _user_hits.setdefault(user, deque())
    while q and now - q[0] > 60:
        q.popleft()
    while _global_hits and now - _global_hits[0] > 60:
        _global_hits.popleft()

    if len(q) >= PER_USER_PER_MIN:
        raise HTTPException(
            status_code=429,
            detail="Gently now — you've asked many questions this minute. Take a breath and return in a moment. 🙏",
        )
    if len(_global_hits) >= GLOBAL_PER_MIN:
        raise HTTPException(
            status_code=429,
            detail="Many seekers are here right now. Please try again in a short while. 🙏",
        )

    q.append(now)
    _global_hits.append(now)
