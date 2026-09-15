"""Render a confession into numbered JPEG slides."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FEED = (1080, 1350)   # 4:5, Instagram feed max height
STORY = (1080, 1920)  # 9:16
MAX_PAGES = 10        # Instagram carousel cap
BG, FG, MUTED = "#111111", "#f5f5f5", "#888888"


def _font(size, bold=False):
    return ImageFont.truetype(str(FONT_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)


def _wrap(text, font, max_w, draw):
    """Word-wrap text to max_w pixels, preserving blank lines."""
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            cand = f"{line} {word}".strip()
            if draw.textlength(cand, font=font) <= max_w or not line:
                line = cand
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def _paginate(lines, per_page):
    pages = [lines[i:i + per_page] for i in range(0, len(lines), per_page)] or [[]]
    if len(pages) > MAX_PAGES:
        pages = pages[:MAX_PAGES]
        pages[-1][-1] = pages[-1][-1][:-1] + "…"
    return pages


def render(text, number, date_str, out_dir, prefix, size=FEED):
    """Write slides to out_dir/<prefix>_<i>.jpg and return their paths."""
    w, h = size
    pad, body_size = 80, 48
    body, head, foot = _font(body_size), _font(56, bold=True), _font(32)
    line_h = int(body_size * 1.45)
    top, bottom = pad + 120, h - pad - 60
    per_page = (bottom - top) // line_h

    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    pages = _paginate(_wrap(text, body, w - 2 * pad, draw), per_page)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, page in enumerate(pages, 1):
        img = Image.new("RGB", size, BG)
        d = ImageDraw.Draw(img)
        d.text((pad, pad), f"Confession #{number}", font=head, fill=FG)
        d.line([(pad, pad + 90), (w - pad, pad + 90)], fill=MUTED, width=2)
        y = top
        for line in page:
            d.text((pad, y), line, font=body, fill=FG)
            y += line_h
        d.text((pad, h - pad - 20), date_str, font=foot, fill=MUTED)
        if len(pages) > 1:
            d.text((w - pad, h - pad - 20), f"{i}/{len(pages)}", font=foot, fill=MUTED, anchor="ra")
        p = out_dir / f"{prefix}_{i}.jpg"
        img.save(p, "JPEG", quality=90)
        paths.append(p)
    return paths
