"""Render HomeSpectations 11.11 sale ad images (4:5 feed + 9:16 story) per category.

Usage: python3 render.py <fonts_dir> <out_dir> [offer_line] [offer_sub]
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
FONTS, OUT = sys.argv[1], sys.argv[2]
OFFER = sys.argv[3] if len(sys.argv) > 3 else "FLAT 11% OFF"
OFFER_SUB = sys.argv[4] if len(sys.argv) > 4 else "11 to 13 November only"

INK = (24, 30, 27)
BRASS = (201, 156, 82)
STONE = (241, 237, 230)
PAPER = (255, 255, 255)
MUTED = (104, 108, 104)
RED = (196, 52, 40)


def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if weight:
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
    return f


ANTON = lambda s: font("Anton.ttf", s)
SERIF = lambda s: font("DMSerifDisplay-Regular.ttf", s)
SANS = lambda s, w="Bold": font("Manrope.ttf", s, w)

CATS = {
    "consoles": {
        "title": "Consoles & sideboards",
        "kind": "photo",
        "items": [
            ("c-blinder.jpg", "Blinder", 56500),
            ("c-seona.jpg", "Seona", 61000),
            ("c-note.jpg", "Note", 56500),
            ("c-rihna.jpg", "Rihna", 48500),
        ],
        "from": 34500,
    },
    "sofas": {
        "title": "Sofa sets (3+2+1)",
        "kind": "cutout",
        "crop": (0.0, 0.17, 1.0, 0.535),
        "suffix": " for the 3+2+1 set",
        "items": [
            ("s-chester.jpg", "Chester", 204500),
            ("s-triade.jpg", "Triade", 156000),
            ("s-mauk.jpg", "Mauk", 173500),
            ("s-flavia.jpg", "Flavia", 173500),
        ],
        "from": 156000,
    },
    "beds": {
        "title": "Double beds",
        "kind": "cutout",
        "items": [
            ("b-cobb.png", "Cobb", 57500),
            ("b-garret.png", "Garret", 109000),
            ("b-edler.jpg", "Edler", 105000),
            ("b-rian.jpg", "Rian", 103500),
        ],
        "from": 57500,
    },
}


def pkr(n):
    return f"PKR {n:,}"


def load(fn, crop=None):
    im = Image.open(os.path.join(SRC, fn)).convert("RGB")
    if fn == "b-edler.jpg":  # paint out the "Anti-fade upholstery" callout
        d = ImageDraw.Draw(im)
        w, h = im.size
        d.rectangle((int(w * 0.55), 0, w, int(h * 0.36)), fill=(255, 255, 255))
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    return im


def cutout(im, bw, bh):
    lum = im.convert("L")
    bbox = lum.point(lambda v: 255 if v < 232 else 0).getbbox()
    if bbox:
        pad = 6
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    return ImageOps.contain(im, (bw, bh), Image.LANCZOS)


def tile(cat, item, w, h):
    fn, name, price = item
    t = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(t)
    label_h = 96
    ph = h - label_h
    if cat["kind"] == "photo":
        im = load(fn)
        bb = im.convert("L").point(lambda v: 255 if v < 245 else 0).getbbox()
        if bb:
            im = im.crop(bb)
        im = ImageOps.fit(im, (w, ph), Image.LANCZOS, centering=(0.5, 0.6))
        t.paste(im, (0, 0))
    else:
        im = load(fn, cat.get("crop"))
        # flatten any off-white ground to white so tiles look uniform
        im = cutout(im, w - 40, ph - 30)
        t.paste(im, ((w - im.width) // 2, (ph - im.height) // 2 + 10))
    d.text((20, ph + 14), name, font=SANS(28, "ExtraBold"), fill=INK)
    d.text((20, ph + 52), pkr(price) + cat.get("suffix", ""), font=SANS(26, "SemiBold"), fill=MUTED)
    return t


def chip(d, xy, text, f, fg, bg, pad=(22, 10)):
    x, y = xy
    tw = d.textlength(text, font=f)
    asc, desc = f.getmetrics()
    d.rounded_rectangle((x, y, x + tw + 2 * pad[0], y + asc + desc + 2 * pad[1]), radius=999, fill=bg)
    d.text((x + pad[0], y + pad[1]), text, font=f, fill=fg)
    return x + tw + 2 * pad[0]


def render(key, W, H, out):
    cat = CATS[key]
    story = H >= 1900
    img = Image.new("RGB", (W, H), STONE)
    d = ImageDraw.Draw(img)
    m = 48
    top_safe = 210 if story else 0
    bot_safe = 300 if story else 0

    # header band
    band_h = 440
    y0 = top_safe
    d.rectangle((0, 0, W, y0 + band_h), fill=INK)
    d.text((m, y0 + 40), "HOMESPECTATIONS", font=SANS(26, "ExtraBold"), fill=(190, 186, 176))
    d.text((W - m, y0 + 40), "11.11 SALE", font=SANS(26, "ExtraBold"), fill=BRASS, anchor="ra")
    f11 = ANTON(200)
    d.text((m - 4, y0 + 78), "11.11", font=f11, fill=BRASS)
    x11 = m + d.textlength("11.11", font=f11) + 24
    d.text((x11, y0 + 104), "SALE", font=ANTON(96), fill=PAPER)
    d.text((x11, y0 + 222), cat["title"], font=SANS(34, "Bold"), fill=(220, 216, 206))
    # offer strip
    oy = y0 + band_h - 92
    d.rectangle((0, oy, W, y0 + band_h), fill=RED)
    d.text((m, oy + 46), OFFER, font=ANTON(58), fill=PAPER, anchor="lm")
    d.text((W - m, oy + 46), OFFER_SUB, font=SANS(28, "Bold"), fill=PAPER, anchor="rm")

    # grid
    gy = y0 + band_h + 32
    foot_h = 150
    gh = H - bot_safe - foot_h - gy - 16
    gap = 18
    tw = (W - 2 * m - gap) // 2
    th = (gh - gap) // 2
    for i, it in enumerate(cat["items"]):
        t = tile(cat, it, tw, th)
        img.paste(t, (m + (i % 2) * (tw + gap), gy + (i // 2) * (th + gap)))

    # footer
    fy = H - bot_safe - foot_h
    d.text((m, fy + 22), "Book with 20% advance, rest on delivery", font=SANS(32, "ExtraBold"), fill=INK)
    d.text((m, fy + 72), "Free delivery across Pakistan · Built to order", font=SANS(28, "SemiBold"), fill=MUTED)
    f = SANS(30, "ExtraBold")
    cta = "Shop now"
    cw = d.textlength(cta, font=f) + 60
    d.rounded_rectangle((W - m - cw, fy + 30, W - m, fy + 100), radius=35, fill=INK)
    d.text((W - m - cw / 2, fy + 65), cta, font=f, fill=PAPER, anchor="mm")
    img.save(out, quality=92)


os.makedirs(OUT, exist_ok=True)
for k in CATS:
    for tag, (W, H) in {"feed-4x5": (1080, 1350), "story-9x16": (1080, 1920)}.items():
        p = os.path.join(OUT, f"{k}_{tag}.jpg")
        render(k, W, H, p)
        print("wrote", p)
