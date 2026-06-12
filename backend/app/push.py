"""Daily Guidance web-push: verse of the day at ~7:00 and ~19:00 IST.

Subscriptions live in Mongo (`push_subs`). A small daemon thread wakes at the
two send times; dead subscriptions (404/410) are pruned automatically. The
notification body is the day's verse directly from the corpus — no LLM call.
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import threading
import time

from pywebpush import WebPushException, webpush

from .config import settings
from .db import get_db

log = logging.getLogger("push")

IST = _dt.timezone(_dt.timedelta(hours=5, minutes=30))
SEND_HOURS_IST = (7, 19)  # morning verse, evening reflection nudge


def enabled() -> bool:
    return bool(settings.vapid_public_key and settings.vapid_private_key)


def save_subscription(user: str, sub: dict) -> None:
    get_db()["push_subs"].update_one(
        {"endpoint": sub.get("endpoint")},
        {"$set": {"user": user, "sub": sub, "updated_at": _dt.datetime.now(_dt.timezone.utc)}},
        upsert=True,
    )


def remove_subscription(user: str, endpoint: str) -> int:
    return get_db()["push_subs"].delete_one({"endpoint": endpoint, "user": user}).deleted_count


def _payload(period: str) -> dict:
    from .daily import _verse_of_day
    v = _verse_of_day()
    title = "🌅 Your morning verse" if period == "morning" else "🌙 Evening reflection"
    body = f'“{v["translation"][:160]}…” — {v["ref"]}' if len(v["translation"]) > 160 \
        else f'“{v["translation"]}” — {v["ref"]}'
    return {"title": title, "body": body, "url": "/"}


def send_to_all(period: str) -> dict:
    subs = list(get_db()["push_subs"].find({}))
    payload = json.dumps(_payload(period))
    sent = dead = 0
    for s in subs:
        try:
            webpush(
                subscription_info=s["sub"],
                data=payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_sub},
            )
            sent += 1
        except WebPushException as e:
            code = getattr(e.response, "status_code", None)
            if code in (404, 410):
                get_db()["push_subs"].delete_one({"_id": s["_id"]})
                dead += 1
            else:
                log.warning("push failed (%s): %s", code, e)
        except Exception as e:
            log.warning("push error: %s", e)
    return {"sent": sent, "pruned": dead, "total": len(subs)}


def _seconds_until_next_send() -> tuple[float, str]:
    now = _dt.datetime.now(IST)
    candidates = []
    for d in (0, 1):
        day = now.date() + _dt.timedelta(days=d)
        for h in SEND_HOURS_IST:
            t = _dt.datetime.combine(day, _dt.time(h, 0), IST)
            if t > now:
                candidates.append(t)
    nxt = min(candidates)
    period = "morning" if nxt.hour < 12 else "evening"
    return (nxt - now).total_seconds(), period


def _loop() -> None:
    while True:
        try:
            wait, period = _seconds_until_next_send()
            time.sleep(max(30.0, wait))
            res = send_to_all(period)
            log.info("daily push (%s): %s", period, res)
        except Exception as e:
            log.warning("push loop error: %s", e)
            time.sleep(300)


def start_scheduler() -> None:
    if not enabled():
        log.info("push disabled (no VAPID keys)")
        return
    threading.Thread(target=_loop, daemon=True, name="push-scheduler").start()
