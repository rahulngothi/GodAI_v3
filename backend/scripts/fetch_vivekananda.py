"""Fetch Swami Vivekananda's books (public domain — d. 1902) from Wikisource's
REST API into corpus passages: Jnana-Yoga, Bhakti-Yoga, Raja-Yoga.

(Karma-Yoga already in corpus from sacred-texts.) Writes backend/corpus/vivekananda2.json.
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "backend" / "corpus"
UA = {"User-Agent": "DharmaAI/1.0 (public-domain corpus fetch; dev@local)"}

BOOKS = [
    ("Jnana-Yoga", "The Complete Works of Swami Vivekananda/Volume 2/Jnana-Yoga"),
    ("Bhakti-Yoga", "The Complete Works of Swami Vivekananda/Volume 3/Bhakti-Yoga"),
    ("Raja-Yoga", "The Complete Works of Swami Vivekananda/Volume 1/Raja-Yoga"),
]

MAX_PER_CHAPTER = 25


def get(title: str) -> str:
    url = "https://en.wikisource.org/w/rest.php/v1/page/" + urllib.parse.quote(title, safe="")
    for attempt in range(4):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read())
            time.sleep(1.0)
            return r.get("source", "")
        except Exception as e:
            print(f"   retry {title[-40:]} ({type(e).__name__})")
            time.sleep(5 * (attempt + 1))
    return ""


def strip_wikitext(src: str) -> str:
    # drop the {{header ...}} template block
    src = re.sub(r"^\{\{header.*?\}\}\s*", "", src, flags=re.S | re.I)
    src = re.sub(r"\{\{c\|(.*?)\}\}", r"\1", src, flags=re.S)
    src = re.sub(r"\{\{center\|(.*?)\}\}", r"\1", src, flags=re.S)
    src = re.sub(r"\{\{[^{}]*\}\}", " ", src)          # other simple templates
    src = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", src)  # [[x|y]] -> y
    src = re.sub(r"\[\[([^\]]*)\]\]", r"\1", src)            # [[x]] -> x
    src = re.sub(r"'{2,}", "", src)                            # bold/italic quotes
    src = re.sub(r"==+[^=]*==+", "\n", src)                    # headings
    src = re.sub(r"<ref[^>]*>.*?</ref>", " ", src, flags=re.S | re.I)
    src = re.sub(r"<[^>]+>", " ", src)
    return src


def chapters(index_src: str) -> list[str]:
    return re.findall(r"\*\s*\[\[/([^\]|]+)\|", index_src)


def main() -> None:
    out: list[dict] = []
    for book, index_title in BOOKS:
        idx = get(index_title)
        chs = chapters(idx)
        print(f"{book}: {len(chs)} chapters")
        for ch in chs:
            src = get(f"{index_title}/{ch}")
            if not src:
                continue
            text = strip_wikitext(src)
            paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
            paras = [p for p in paras if len(p) > 150]
            for i, p in enumerate(paras[:MAX_PER_CHAPTER], start=1):
                out.append({
                    "ref": f"Vivekananda: {book}, {ch} §{i}",
                    "source": "Vivekananda (Complete Works)",
                    "translator": "Swami Vivekananda",
                    "translation": p,
                    "layer": "teacher",
                })
            print(f"   {ch[:46]:46s} -> {min(len(paras), MAX_PER_CHAPTER)} passages")
    (CORPUS / "vivekananda2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nTOTAL: {len(out)} passages -> corpus/vivekananda2.json")
    print(" sample:", out[0]["ref"], "|", out[0]["translation"][:100])


if __name__ == "__main__":
    main()
