"""Conversion creatives (Nov 2026): one product, no prices, trust footer.

Usage: python3 render_conv.py <fonts_dir> <out_dir> [slug ...]
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
FONTS, OUT = sys.argv[1], sys.argv[2]
IVORY, INK, MUTED, BRASS = (244, 239, 231), (28, 26, 23), (110, 104, 96), (166, 124, 62)

# slug, photo, label, headline, crop centering, full-bleed photo?
ADS = [
    ("bed-cobb", "b-cobb.png", "STORAGE BEDS", "Space for everything.\nBuilt to last.", (0.5, 0.5), False),
    ("bed-roche", "r-roche16.jpg", "STORAGE BEDS", "Two drawers.\nZero clutter.", (0.5, 0.55), False),
    ("sofa-chester", "r-chester71.jpg", "CHESTERFIELD", "A classic,\nmade to order.", (0.5, 0.5), False),
    ("console-note", "c-note.jpg", "CONSOLES", "Finish\nthe room.", (0.5, 0.6), True),
    ("table-caricara", "caricara-b.jpg", "COFFEE TABLES", "The centre of\nevery evening.", (0.5, 0.5), False),
    ("client-sloan", "sloan-client4.jpg", "DELIVERED TO A CLIENT", "Real home.\nReal furniture.", (0.5, 0.6), True),
]


def f(name, size, w=None):
    ft = ImageFont.truetype(os.path.join(FONTS, name), size)
    if w:
        ft.set_variation_by_axes([w])
    return ft


def spaced(d, xy, text, font, fill, track, anchor="l"):
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x, y = xy
    if anchor == "r":
        x -= total
    for c, w in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill)
        x += w + track


def render(slug, photo, cat, head, centering, bleed, W=1080, H=1350):
    im = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(im)
    m = 64
    spaced(d, (m, 46), "HOMESPECTATIONS", f("Manrope.ttf", 22, 700), INK, 6)
    spaced(d, (W - m, 46), "MADE TO ORDER", f("Manrope.ttf", 22, 600), MUTED, 5, anchor="r")
    py, ph = 104, 800
    src = Image.open(os.path.join(SRC, photo)).convert("RGB")
    if bleed:
        pic = ImageOps.fit(src, (W - 2 * m, ph), Image.LANCZOS, centering=centering)
        im.paste(pic, (m, py))
    else:  # product cut-out on white: fit inside a white panel, no cropping
        panel = Image.new("RGB", (W - 2 * m, ph), (255, 255, 255))
        bb = src.convert("L").point(lambda v: 255 if v < 245 else 0).getbbox()
        if bb:
            src = src.crop(bb)
        src.thumbnail((W - 2 * m - 90, ph - 110), Image.LANCZOS)
        panel.paste(src, ((panel.width - src.width) // 2, (ph - src.height) // 2))
        im.paste(panel, (m, py))
    ty = py + ph + 44
    spaced(d, (m, ty), cat, f("Manrope.ttf", 22, 700), BRASS, 5)
    hf = f("Cormorant.ttf", 76, 600)
    y = ty + 34
    for line in head.split("\n"):
        d.text((m, y), line, font=hf, fill=INK)
        y += 78
    d.line((m, H - 118, W - m, H - 118), fill=(214, 205, 192), width=2)
    sf = f("Manrope.ttf", 25, 500)
    d.text((m, H - 66), "Pay 20% to confirm  ·  Rest on delivery", font=sf, fill=MUTED, anchor="ls")
    cf = f("Manrope.ttf", 25, 700)
    cta = "Shop now  →"
    d.text((W - m, H - 66), cta, font=cf, fill=INK, anchor="rs")
    cw = d.textlength(cta, font=cf)
    d.line((W - m - cw, H - 54, W - m, H - 54), fill=INK, width=2)
    out = os.path.join(OUT, f"{slug}_4x5.jpg")
    im.save(out, quality=94)
    return out


os.makedirs(OUT, exist_ok=True)
only = sys.argv[3:]
for a in ADS:
    if (not only or a[0] in only) and os.path.exists(os.path.join(SRC, a[1])):
        print(render(*a))
