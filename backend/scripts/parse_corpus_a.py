"""Parse Yoga Sutras (Johnston), Upanishads (Paramananda), Vivekananda Karma-Yoga
into clean {ref, source, translator, translation} corpus JSON files.
Verse text only — interpretive commentary is dropped.
"""
import html as H
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
CORPUS = ROOT / "backend" / "corpus"
CORPUS.mkdir(parents=True, exist_ok=True)

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4}


def parse_yoga():
    t = (RAW / "yogasutras.txt").read_text(encoding="utf-8")
    s = t.find("*** START"); s = t.find("\n", s) + 1
    e = t.find("*** END", s)
    lines = t[s:e].split("\n")
    out, book, k, n = [], 0, 0, len(t[s:e].split("\n"))
    while k < n:
        st = lines[k].strip()
        mb = re.match(r"^BOOK (I|II|III|IV)$", st)
        if mb:
            book = ROMAN[mb.group(1)]; k += 1; continue
        ms = re.match(r"^(\d+)\.\s+(.*)$", lines[k])
        if ms and book:
            num, text = int(ms.group(1)), ms.group(2).strip()
            k += 1
            while k < n and lines[k].strip() != "":
                text += " " + lines[k].strip(); k += 1
            out.append({"ref": f"Yoga Sutra {book}.{num}", "source": "Yoga Sutras",
                        "translator": "Charles Johnston (1912)",
                        "translation": re.sub(r"\s+", " ", text).strip()})
        else:
            k += 1
    return out


def parse_upanishads():
    t = (RAW / "upanishads.txt").read_text(encoding="utf-8")
    ends = [m.start() for m in re.finditer(r"Here ends this Upanishad", t)]
    names = ["Isa", "Katha", "Kena"]
    out, start = [], t.find("Isa-Upanishad", t.find("Isa-Upanishad") + 10)
    for idx, name in enumerate(names):
        seg = t[start:ends[idx]] if idx < len(ends) else t[start:]
        start = ends[idx] if idx < len(ends) else start
        lines = seg.split("\n")
        seq = 0
        for j, ln in enumerate(lines):
            if re.match(r"^[IVXLC]{1,6}$", ln.strip()):
                p = j + 1
                while p < len(lines) and lines[p].strip() == "":
                    p += 1
                para = []
                while p < len(lines) and lines[p].strip() != "":
                    para.append(lines[p].strip()); p += 1
                txt = re.sub(r"\s+", " ", " ".join(para)).strip()
                if len(txt) > 20:
                    seq += 1
                    out.append({"ref": f"{name} Upanishad {seq}", "source": "Upanishads",
                                "translator": "Swami Paramananda",
                                "translation": txt})
    return out


def parse_vivekananda():
    out = []
    for nch in range(1, 9):
        f = RAW / f"kyog{nch:02d}.htm"
        if not f.exists():
            continue
        raw = f.read_text(encoding="utf-8", errors="ignore")
        ps = re.findall(r"<p[^>]*>(.*?)</p>", raw, re.S | re.I)
        para = 0
        for p in ps:
            txt = H.unescape(re.sub(r"<[^>]+>", " ", p))
            txt = re.sub(r"\bp\.\s*\d+\b", "", txt)
            txt = re.sub(r"\s+", " ", txt).strip()
            if len(txt) > 80:
                para += 1
                out.append({"ref": f"Vivekananda: Karma-Yoga {nch}.{para}",
                            "source": "Vivekananda (Complete Works)",
                            "translator": "Swami Vivekananda",
                            "translation": txt})
    return out


def write(name, items):
    (CORPUS / name).write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n=== {name}: {len(items)} passages ===")
    for s in items[:2]:
        print(f'  [{s["ref"]}] {s["translation"][:120]}')


write("yoga_sutras.json", parse_yoga())
write("upanishads.json", parse_upanishads())
write("vivekananda.json", parse_vivekananda())
