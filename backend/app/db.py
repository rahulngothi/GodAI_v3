"""MongoDB access — lazy singleton client (mirrors nebula's get_database pattern).

We use synchronous pymongo: FastAPI runs sync endpoints in a threadpool, and
the corpus is small + local, so this is simple and robust for v1.0.
"""
from functools import lru_cache

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database

from .config import settings

# Collection names
VERSES = "verses"
REFLECTIVE_QUESTIONS = "reflective_questions"
USER_PROFILES = "user_profiles"


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    return MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)


def get_db() -> Database:
    return get_client()[settings.mongo_db]


def ensure_indexes() -> None:
    """Create all MongoDB indexes. Idempotent."""
    db = get_db()

    # Auth + memory (from auth-memory-profiles branch)
    db["users"].create_index("username", unique=True)
    db["user_profiles"].create_index("user", unique=True)
    db["user_memory"].create_index("user", unique=True)
    db["chats"].create_index([("user", 1), ("updated_at", -1)])

    # Reflective Question Engine
    rq = db[REFLECTIVE_QUESTIONS]
    rq.create_index([("themes", ASCENDING)])
    rq.create_index([("type", ASCENDING)])
    rq.create_index([("depth", ASCENDING)])
    rq.create_index([("status", ASCENDING), ("active", ASCENDING)])
    rq.create_index([
        ("themes", ASCENDING),
        ("active", ASCENDING),
        ("status", ASCENDING),
        ("depth", ASCENDING),
    ], name="rqe_selection")
    rq.create_index([("stats.engagement_rate", DESCENDING)])
    rq.create_index([("source", ASCENDING)])

    # user_profiles: _id is the username string; MongoDB creates the _id index automatically.
