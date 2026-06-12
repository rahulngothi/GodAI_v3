"""MongoDB access — lazy singleton client (mirrors nebula's get_database pattern).

We use synchronous pymongo: FastAPI runs sync endpoints in a threadpool, and
the corpus is small + local, so this is simple and robust for v1.0.
"""
from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from .config import settings

# Collection names
VERSES = "verses"


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    return MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)


def get_db() -> Database:
    return get_client()[settings.mongo_db]
