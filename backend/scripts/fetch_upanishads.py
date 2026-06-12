"""Scrape Max Müller's Upanishad translations (Sacred Books of the East vols 1 & 15,
1879/1884, public domain) from sacred-texts.com into corpus JSON with CANONICAL
chapter.section.verse refs (e.g. "Katha Upanishad 1.2.20").

Polite crawl: browser UA + 1.6s delay + retry on 403/429.
Writes backend/corpus/upanishads.json (replacing the old running-index file).
"""
from __future__ import annotations

import html as H
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "backend" / "corpus"
CACHE = ROOT / "data" / "raw" / "sbe_cache"
CACHE.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

VOLS = {
    "sbe15": "https://sacred-texts.com/hin/sbe15/",
    "sbe01": "https://sacred-texts.com/hin/sbe01/",
}

# Müller's archaic titles -> modern canonical names (substring match, in order).
NAME_MAP = [
    ("katha", "Katha Upanishad"),
    ("mundaka", "Mundaka Upanishad"),
    ("taittiriyaka", "Taittiriya Upanishad"),
    ("brihadaranyaka", "Brihadaranyaka Upanishad"),
    ("svetasvatara", "Svetasvatara Upanishad"),
    ("prasna", "Prashna Upanishad"),
    ("maitrayana", "Maitrayana Upanishad"),
    ("khandogya", "Chandogya Upanishad"),
    ("talavakara", "Kena Upanishad"),
    ("vagasaneyi", "Isha Upanishad"),
    ("kaushitaki", "Kaushitaki Upanishad"),
]

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
         "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16}
ORDINAL = {w: i + 1 for i, w in enumerate(
    ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH",
     "NINTH", "TENTH", "ELEVENTH", "TWELFTH", "THIRTEENTH", "FOURTEENTH", "FIFTEENTH", "SIXTEENTH"])}


def deaccent(s: str) -> str:
    import unicodedata
    s = H.unescape(s)
    # decompose accents (â->a+combining) then drop all combining marks
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def fetch(url: str, cache_name: str) -> str:
    dest = CACHE / cache_name
    if dest.exists() and dest.stat().st_size > 500:
        return dest.read_text(encoding="utf-8", errors="ignore")
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
            txt = raw.decode("utf-8", errors="ignore")
            dest.write_text(txt, encoding="utf-8")
            time.sleep(1.6)
            return txt
        except Exception as e:
            wait = 6 * (attempt + 1)
            print(f"   retry {url} after {wait}s ({type(e).__name__})")
            time.sleep(wait)
    raise RuntimeError(f"failed to fetch {url}")


def parse_index(vol: str) -> list[dict]:
    """Return [{name, pages:[(file,label),...]}] for the Upanishads we want."""
    txt = fetch(VOLS[vol] + "index.htm", f"{vol}_index.htm")
    # split on section anchors
    chunks = re.split(r'<A NAME="section_\d+">', txt, flags=re.I)
    out = []
    for chunk in chunks[1:]:
        mh = re.search(r"<H3[^>]*>(.*?)</H3>", chunk, re.I | re.S)
        if not mh:
            continue
        title = deaccent(re.sub(r"<[^>]+>", "", mh.group(1))).strip().lower()
        canon = next((c for key, c in NAME_MAP if key in title), None)
        if not canon:
            continue
        pages = re.findall(r'<A HREF="(' + vol + r'\d+\.htm)">(.*?)</A>', chunk, re.I | re.S)
        out.append({"name": canon, "vol": vol,
                    "pages": [(f, deaccent(re.sub(r"<[^>]+>", "", l)).strip()) for f, l in pages]})
    return out


def label_to_prefix(label: str) -> str | None:
    """'I, 2' -> '1.2' | 'II' -> '2' | 'FIRST VALLI' -> '1' | else None (skip page)."""
    lab = label.strip().rstrip(".")
    m = re.match(r"^([IVX]+)\s*,\s*(\d+)$", lab)
    if m:
        return f"{ROMAN[m.group(1)]}.{m.group(2)}"
    m = re.match(r"^([IVX]+)\s*,\s*([IVX]+)$", lab)
    if m:
        return f"{ROMAN[m.group(1)]}.{ROMAN[m.group(2)]}"
    m = re.match(r"^([IVX]+)$", lab)
    if m:
        return str(ROMAN[m.group(1)])
    m = re.match(r"^(\w+)\s+(VALLI|PRAPATHAKA|ADHYAYA|KHANDA|PRASNA|BRAHMANA|QUESTION)", lab, re.I)
    if m and m.group(1).upper() in ORDINAL:
        return str(ORDINAL[m.group(1).upper()])
    m = re.match(r"^(VALLI|PRAPATHAKA|ADHYAYA|KHANDA|QUESTION)\s+([IVX]+)$", lab, re.I)
    if m:
        return str(ROMAN[m.group(2).upper()])
    return None


def parse_page(vol: str, fname: str, name: str, prefix: str) -> list[dict]:
    txt = fetch(VOLS[vol] + fname, f"{vol}_{fname}")
    # body starts after the breadcrumb line
    m = re.search(r"at sacred-texts\.com", txt)
    body = txt[m.end():] if m else txt
    body = re.split(r"Next:", body)[0]
    body = re.sub(r"<script.*?</script>", " ", body, flags=re.S | re.I)
    # block-level tags become newlines; inline tags (<i>, <a>, <sup>...) vanish
    # WITHOUT breaking words (Müller italicizes letters inside Sanskrit names).
    body = re.sub(r"(?i)</?(p|br|h\d|div|td|tr|table|center|blockquote)[^>]*>", "\n", body)
    body = re.sub(r"(?is)<sup>\s*\d+\s*</sup>", "", body)   # footnote superscripts
    text = re.sub(r"<[^>]+>", "", body)
    text = deaccent(text)
    text = re.sub(r"\bp\.\s*\d+\b", " ", text)

    verses, cur_n, cur = [], None, []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if re.match(r"^\d+:\d+", s):       # footnote block begins
            break
        mv = re.match(r"^(\d+)\.\s+(.*)$", s)
        if mv:
            if cur_n is not None and cur:
                verses.append((cur_n, " ".join(cur)))
            cur_n, cur = int(mv.group(1)), [mv.group(2)]
        elif cur_n is not None:
            if s.isupper() and len(s) < 40:   # section headers inside page
                continue
            cur.append(s)
    if cur_n is not None and cur:
        verses.append((cur_n, " ".join(cur)))

    out = []
    for n, t in verses:
        t = re.sub(r"\s+", " ", t).strip()
        # leftover footnote digits: " word 2 ," / " word 1 word" -> drop the bare digit
        t = re.sub(r"\s\d{1,3}(\s*[,.;:!?)\"'])", r"\1", t)
        t = re.sub(r"(\S)\s\d{1,3}\s(?=[a-z(])", r"\1 ", t)
        t = re.sub(r"\s*\d+\s*$", "", t)        # trailing footnote digit
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) < 15:
            continue
        out.append({
            "ref": f"{name} {prefix}.{n}" if prefix else f"{name} {n}",
            "source": "Upanishads",
            "translator": "F. Max Müller",
            "translation": t,
            "layer": "scripture",
        })
    return out


def main() -> None:
    all_docs: list[dict] = []
    for vol in VOLS:
        for sec in parse_index(vol):
            count = 0
            for fname, label in sec["pages"]:
                prefix = label_to_prefix(label)
                if prefix is None and len(sec["pages"]) == 1:
                    prefix = ""  # single-page Upanishads (e.g. Isha): plain verse numbers
                if prefix is None:
                    continue
                docs = parse_page(vol, fname, sec["name"], prefix)
                all_docs.extend(docs)
                count += len(docs)
            print(f"{sec['name']:28s} -> {count} verses")
    # dedupe by ref (keep first)
    seen, deduped = set(), []
    for d in all_docs:
        if d["ref"] in seen:
            continue
        seen.add(d["ref"])
        deduped.append(d)
    (CORPUS / "upanishads.json").write_text(json.dumps(deduped, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nTOTAL: {len(deduped)} verses -> corpus/upanishads.json")
    for d in deduped[:3] + deduped[-3:]:
        print(f'  [{d["ref"]}] {d["translation"][:90]}')


if __name__ == "__main__":
    main()
