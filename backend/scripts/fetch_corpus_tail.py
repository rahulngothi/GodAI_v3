"""Corpus tail: Mandukya (Hume 1921, PD), Aitareya Upanishad (Müller SBE vol 1),
Vidura Niti + Yaksha Prashna (Ganguli Mahabharata, PD, sacred-texts).

Writes corpus/upanishads_extra.json and corpus/mahabharata.json.
Every extraction prints samples for human verification.
"""
from __future__ import annotations

import html as H
import json
import re
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
CACHE = RAW / "sbe_cache"
CORPUS = ROOT / "backend" / "corpus"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}


def deaccent(s: str) -> str:
    s = H.unescape(s)
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def fetch(url: str, cache_name: str) -> str:
    dest = CACHE / cache_name
    if dest.exists() and dest.stat().st_size > 500:
        return dest.read_text(encoding="utf-8", errors="ignore")
    for attempt in range(4):
        try:
            txt = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read().decode("utf-8", "ignore")
            dest.write_text(txt, encoding="utf-8")
            time.sleep(1.6)
            return txt
        except Exception as e:
            time.sleep(6 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


# ---------- 1) Mandukya from Hume 1921 OCR ----------
def mandukya() -> list[dict]:
    t = (RAW / "hume.txt").read_text(encoding="utf-8", errors="ignore")
    seg = t[915000:923500]
    lines = seg.split("\n")
    verses: list[tuple[int, list[str]]] = []
    cur_n, cur = None, []
    for ln in lines:
        s = re.sub(r"\s+", " ", ln).strip()
        if not s:
            continue
        # page headers / page numbers / sub-headings
        if re.search(r"upanishad", s, re.I) and len(s) < 50 and not re.match(r"^\d+\.", s):
            continue
        if re.match(r"^\d{2,3}$", s) or re.match(r"^\([a-z]\)", s):
            cur_n = cur_n  # page number or (a)/(b) heading — ignore line
            continue
        mv = re.match(r"^(\d{1,2})\.\s+(.*)$", s)
        if mv and (cur_n is None or int(mv.group(1)) == cur_n + 1):
            if cur_n is not None:
                verses.append((cur_n, cur))
            cur_n, cur = int(mv.group(1)), [mv.group(2)]
            continue
        # footnote block start: digit + space + Capital, no period -> close current verse
        if re.match(r"^\d{1,2}\s+[A-Z]", s) and cur_n is not None:
            verses.append((cur_n, cur))
            cur_n, cur = None, []
            continue
        if cur_n is not None:
            cur.append(s)
    if cur_n is not None:
        verses.append((cur_n, cur))

    out = []
    for n, parts in verses:
        if n > 12:
            continue
        txt = " ".join(parts)
        txt = re.sub(r"\{[^}]*\}", "", txt)                      # OCR'd Sanskrit braces
        txt = re.sub(r"\(([^()\s]+)\)", "", txt)                  # single-token Sanskrit parens
        txt = re.sub(r"[\^\*]", "", txt)
        txt = re.sub(r"\s\d{1,2}(\s*[,.;:!?)\"'])", r"\1", txt)   # footnote digits
        txt = re.sub(r"(\S)\s\d{1,2}\s(?=[a-z(])", r"\1 ", txt)
        txt = re.sub(r"\s+([,.;:!?])", r"\1", txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        if len(txt) > 20:
            out.append({"ref": f"Mandukya Upanishad {n}", "source": "Upanishads",
                        "translator": "Robert Ernest Hume (1921)",
                        "translation": txt, "layer": "scripture"})
    return out


# ---------- 2) Aitareya Upanishad (= Aitareya Aranyaka II.4-II.6, Müller vol 1) ----------
def aitareya() -> list[dict]:
    idx = fetch("https://sacred-texts.com/hin/sbe01/index.htm", "sbe01_index.htm")
    chunks = re.split(r'<A NAME="section_\d+">', idx)
    pages = []
    for c in chunks[1:]:
        mh = re.search(r"<H3[^>]*>(.*?)</H3>", c, re.I | re.S)
        if mh and "aitareya" in deaccent(re.sub(r"<[^>]+>", "", mh.group(1))).lower():
            pages = re.findall(r'<A HREF="(sbe01\d+\.htm)">(.*?)</A>', c, re.I | re.S)
            break
    # AA II.4-6 = Aitareya Upanishad chapters 1-3; one sacred-texts page per khanda.
    wanted = {"II, 4, 1": "1.1", "II, 4, 2": "1.2", "II, 4, 3": "1.3",
              "II, 5, 1": "2", "II, 6, 1": "3"}
    out = []
    for fname, rawlab in pages:
        label = deaccent(re.sub(r"<[^>]+>", "", rawlab)).strip()
        ch = wanted.get(label)
        if not ch:
            continue
        txt = fetch(f"https://sacred-texts.com/hin/sbe01/{fname}", f"sbe01_{fname}")
        m = re.search(r"at sacred-texts\.com", txt)
        body = txt[m.end():] if m else txt
        body = re.split(r"Next:", body)[0]
        body = re.sub(r"(?i)</?(p|br|h\d|div|td|tr|table|center|blockquote)[^>]*>", "\n", body)
        body = re.sub(r"(?is)<sup>\s*\d+\s*</sup>", "", body)
        text = deaccent(re.sub(r"<[^>]+>", "", body))
        text = re.sub(r"\bp\.\s*\d+\b", " ", text)
        cur_n, cur = None, []
        rows: list[tuple[int, str]] = []
        for ln in text.split("\n"):
            s = ln.strip()
            if not s:
                continue
            if re.match(r"^\d+:\d+", s):
                break
            mv = re.match(r"^(\d+)\.\s+(.*)$", s)
            if mv:
                if cur_n is not None and cur:
                    rows.append((cur_n, " ".join(cur)))
                cur_n, cur = int(mv.group(1)), [mv.group(2)]
            elif cur_n is not None and not (s.isupper() and len(s) < 40):
                cur.append(s)
        if cur_n is not None and cur:
            rows.append((cur_n, " ".join(cur)))
        for n, txt2 in rows:
            txt2 = re.sub(r"\s\d{1,3}(\s*[,.;:!?)\"'])", r"\1", txt2)
            txt2 = re.sub(r"(\S)\s\d{1,3}\s(?=[a-z(])", r"\1 ", txt2)
            txt2 = re.sub(r"\s+", " ", txt2).strip()
            if len(txt2) < 15:
                continue
            out.append({"ref": f"Aitareya Upanishad {ch}.{n}", "source": "Upanishads",
                        "translator": "F. Max Müller", "translation": txt2, "layer": "scripture"})
    return out


# ---------- 3) Mahabharata wisdom (Ganguli, PD) ----------
def mahabharata() -> list[dict]:
    sections = (
        [("m05", n, "Vidura Niti") for n in range(33, 41)] +       # Udyoga Parva 33-40
        [("m03", n, "Yaksha Prashna") for n in range(311, 314)]    # Vana Parva 311-313
    )
    out = []
    for book, n, name in sections:
        fname = f"{book}{n:03d}.htm"
        try:
            txt = fetch(f"https://sacred-texts.com/hin/{book}/{fname}", f"{book}_{fname}")
        except Exception:
            print(f"   !! missing {fname}")
            continue
        m = re.search(r"at sacred-texts\.com", txt)
        body = txt[m.end():] if m else txt
        body = re.split(r"Next:", body)[0]
        paras = re.findall(r"<p>(.*?)</p>", body, re.S | re.I)
        i = 0
        for p in paras:
            t = deaccent(re.sub(r"<[^>]+>", " ", p))
            t = re.sub(r"\bp\.\s*\d+\b", " ", t)
            t = re.sub(r"^\s*\[paragraph continues\]\s*", "", t)
            t = re.sub(r"\s+", " ", t).strip()
            if len(t) < 160 or t.startswith("("):
                continue
            i += 1
            book_no = 5 if book == "m05" else 3
            out.append({"ref": f"{name} (Mahabharata {book_no}.{n}) §{i}",
                        "source": "Mahabharata", "translator": "Kisari Mohan Ganguli",
                        "translation": t, "layer": "scripture"})
    return out


def main() -> None:
    # Mandukya: NO clean public-domain machine-readable source exists (Hume OCR is
    # unusable; Müller never translated it). Documented gap — we do not ship OCR junk.
    extra = aitareya()
    (CORPUS / "upanishads_extra.json").write_text(json.dumps(extra, ensure_ascii=False, indent=1), encoding="utf-8")
    mb = mahabharata()
    (CORPUS / "mahabharata.json").write_text(json.dumps(mb, ensure_ascii=False, indent=1), encoding="utf-8")

    man = [d for d in extra if d["ref"].startswith("Mandukya")]
    ait = [d for d in extra if d["ref"].startswith("Aitareya")]
    print(f"Mandukya: {len(man)} verses | Aitareya: {len(ait)} verses | Mahabharata: {len(mb)} passages")
    print("\n--- ALL Mandukya verses (verify by eye) ---")
    for d in man:
        print(f'[{d["ref"]}] {d["translation"]}')
    print("\n--- Aitareya samples ---")
    for d in ait[:3]:
        print(f'[{d["ref"]}] {d["translation"][:110]}')
    print("\n--- Mahabharata samples ---")
    for d in mb[:2] + mb[-1:]:
        print(f'[{d["ref"]}] {d["translation"][:110]}')


if __name__ == "__main__":
    main()
