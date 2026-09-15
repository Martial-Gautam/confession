import tempfile
from PIL import Image
import render

with tempfile.TemporaryDirectory() as d:
    short = render.render("I ate the last slice.", 1, "15 Sep 2026", d, "feed")
    assert len(short) == 1
    long = render.render(("lorem ipsum dolor sit amet " * 100).strip(), 2, "15 Sep 2026", d, "story", render.STORY)
    assert 1 < len(long) <= render.MAX_PAGES, len(long)
    for p in short + long:
        assert p.exists() and Image.open(p).size in (render.FEED, render.STORY)
print("ok:", len(short), "feed page,", len(long), "story pages")
