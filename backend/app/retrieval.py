"""Semantic verse retrieval.

Loads all verse embeddings into memory once (the Gita is only ~700 verses),
then does cosine similarity against the question embedding. No external vector
DB needed at this scale — MongoDB holds the vectors, numpy does the search.
"""
from __future__ import annotations

import numpy as np

from .db import VERSES, get_db
from .nvidia import embed_one

_matrix: np.ndarray | None = None   # (N, dim) L2-normalised
_docs: list[dict] | None = None     # row-aligned metadata


def _load() -> None:
    global _matrix, _docs
    if _matrix is not None:
        return
    docs = list(get_db()[VERSES].find({"embedding": {"$exists": True}}))
    if not docs:
        raise RuntimeError(
            "No embedded verses found in MongoDB. Run: python -m scripts.ingest_gita"
        )
    mat = np.asarray([d["embedding"] for d in docs], dtype=np.float32)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    _matrix = mat / norms
    _docs = docs


def reset_cache() -> None:
    global _matrix, _docs
    _matrix, _docs = None, None


def search(question: str, k: int = 5) -> list[dict]:
    _load()
    assert _matrix is not None and _docs is not None
    q = np.asarray(embed_one(question, input_type="query"), dtype=np.float32)
    qn = np.linalg.norm(q)
    if qn:
        q = q / qn
    sims = _matrix @ q
    top = np.argsort(-sims)[:k]
    results = []
    for i in top:
        d = _docs[int(i)]
        results.append(
            {
                "ref": d["ref"],
                "source": d.get("source", "Bhagavad Gita"),
                "chapter": d.get("chapter"),
                "verse": d.get("verse"),
                "sanskrit": d.get("sanskrit"),
                "transliteration": d.get("transliteration"),
                "translation": d["translation"],
                "translator": d["translator"],
                "score": round(float(sims[int(i)]), 4),
            }
        )
    return results
