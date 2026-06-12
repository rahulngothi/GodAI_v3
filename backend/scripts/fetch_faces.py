"""Fetch public-domain / freely-licensed portrait images for the guides from
Wikimedia Commons, license-checked, center-cropped to square 512px JPGs.

Writes frontend/icons/face-<key>.jpg + CREDITS-faces.md with attribution.
"""
from __future__ import annotations

import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "frontend" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "DharmaAI/1.0 (corpus image fetch; contact: dev@local)"}
API = "https://commons.wikimedia.org/w/api.php"

# terms: tried in order; require/exclude: regex on the file title to avoid wrong depictions
SEARCHES = {
    "krishna": {
        "terms": ["Raja Ravi Varma Krishna envoy", "Krishna playing flute painting", "Lord Krishna painting portrait"],
        "require": r"krishna", "exclude": r"yashoda|baby|infant|child|radha and|gopis",
    },
    "buddha": {
        "terms": ["Gautama Buddha painting meditation", "Buddha statue head Sarnath", "Standing Buddha Gandhara"],
        "require": r"buddha", "exclude": r"vinegar|taster|temple complex|map",
    },
    "vivekananda": {
        "terms": ["Swami Vivekananda Chicago 1893", "Swami Vivekananda photograph portrait"],
        "require": r"vivekananda", "exclude": r"statue|memorial|airport|setu",
    },
    "chanakya": {
        "terms": ["Chanakya", "Chanakya artistic depiction"],
        "require": r"chanakya|kautilya", "exclude": r"university|metro|puri|cover|book",
    },
    "ramana": {
        "terms": ["Ramana Maharshi portrait Welling"],
        "require": r"ramana", "exclude": r"temple|hill",
    },
    "shankara": {
        "terms": ["Adi Shankaracharya painting", "Raja Ravi Varma Sankaracharya", "Adi Shankara portrait"],
        "require": r"shankar|sankara", "exclude": r"temple|statue of unity|math building",
    },
}

OK_LICENSE = re.compile(r"(public domain|pd-|cc0|cc by(?!-nc))", re.I)


def api(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url, headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def find_image(cfg: dict) -> dict | None:
    import time
    req_re = re.compile(cfg["require"], re.I)
    exc_re = re.compile(cfg["exclude"], re.I) if cfg.get("exclude") else None
    for term in cfg["terms"]:
        for attempt in range(3):
            try:
                data = api({
                    "action": "query", "generator": "search",
                    "gsrsearch": f"filetype:bitmap {term}", "gsrnamespace": 6, "gsrlimit": 12,
                    "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 700,
                })
                break
            except Exception:
                time.sleep(4 * (attempt + 1))
        else:
            continue
        pages = (data.get("query") or {}).get("pages") or {}
        for p in sorted(pages.values(), key=lambda p: p.get("index", 99)):
            title = p.get("title", "")
            if not req_re.search(title) or (exc_re and exc_re.search(title)):
                continue
            info = (p.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            lic = (meta.get("LicenseShortName") or {}).get("value", "")
            if not OK_LICENSE.search(lic):
                continue
            if info.get("width", 0) < 300 or info.get("height", 0) < 300:
                continue
            return {
                "title": title,
                "url": info.get("thumburl") or info.get("url"),
                "license": lic,
                "artist": re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value", "")).strip(),
            }
        time.sleep(2)
    return None


def crop_square(data: bytes, size: int = 512) -> Image.Image:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = img.size
    side = min(w, h)
    # bias the crop toward the top (faces are usually in the upper part of portraits)
    top = max(0, int((h - side) * 0.18))
    left = (w - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    import time
    credits = ["# Guide portrait credits (Wikimedia Commons)\n"]
    for key, cfg in SEARCHES.items():
        time.sleep(2)
        try:
            hit = find_image(cfg)
            if not hit:
                print(f"!! {key}: no acceptable image found")
                continue
            req = urllib.request.Request(hit["url"], headers=UA)
            raw = urllib.request.urlopen(req, timeout=60).read()
            img = crop_square(raw)
            dest = OUT / f"face-{key}.jpg"
            img.save(dest, "JPEG", quality=88)
            print(f"ok {key}: {hit['title']}  [{hit['license']}]  -> {dest.name} ({dest.stat().st_size//1024}KB)")
            credits.append(f"- **{key}** — {hit['title']} · {hit['license']} · {hit['artist'] or 'unknown artist'}")
        except Exception as e:
            print(f"!! {key}: {type(e).__name__}: {e}")
    (OUT / "CREDITS-faces.md").write_text("\n".join(credits), encoding="utf-8")


if __name__ == "__main__":
    main()
