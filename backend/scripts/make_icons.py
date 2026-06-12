"""Generate PWA PNG icons (saffron tile + white Om) for the home-screen app."""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[2] / "frontend" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\Nirmala.ttf",
    r"C:\Windows\Fonts\NirmalaB.ttf",
    r"C:\Windows\Fonts\mangal.ttf",
]


def load_font(size: int):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def make(size: int):
    img = Image.new("RGBA", (size, size), (184, 65, 14, 255))  # saffron
    d = ImageDraw.Draw(img)
    f = load_font(int(size * 0.6))
    text = "ॐ"  # ॐ
    bbox = d.textbbox((0, 0), text, font=f)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]), text, font=f, fill=(255, 255, 255, 255))
    out = OUT / f"icon-{size}.png"
    img.save(out)
    print(f"wrote {out} ({size}x{size})")


if __name__ == "__main__":
    for s in (180, 192, 512):
        make(s)
