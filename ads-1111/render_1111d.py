"""Premium 11.11 creatives: editorial layout, one product, no prices.

Usage: python3 render_premium.py <fonts_dir> <out_dir>
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
FONTS, OUT = sys.argv[1], sys.argv[2]

IVORY = (244, 239, 231)
INK = (28, 26, 23)
MUTED = (110, 104, 96)
BRASS = (166, 124, 62)

# slug, photo, category label, headline (2 lines), crop centering (x, y)
ADS_OLD = [
    ("console-rihna", "c-rihna.jpg", "CONSOLES", "The first thing\nguests notice.", (0.5, 0.6)),
    ("console-maddy", "c-maddy.jpg", "CONSOLES", "Small piece.\nBig presence.", (0.5, 0.55)),
    ("console-seona", "c-seona.jpg", "CONSOLES", "Made to be\nthe centrepiece.", (0.5, 0.6)),
    ("sofa-caroline", "n-caroline-ls.jpg", "SOFAS", "Sink in.\nStay a while.", (0.45, 0.6)),
    ("sofa-casey", "n-casey-ls.jpg", "SOFAS", "Quiet luxury for\nyour living room.", (0.5, 0.6)),
    ("sofa-ayanna", "n-ayanna-ls.jpg", "SOFAS", "Statement seating,\nmade to order.", (0.5, 0.5)),
    ("bed-boucle", "n-boucle1.jpg", "BEDS", "The bed you'll\nlook forward to.", (0.5, 0.6)),
    ("bed-quinn", "n-quinn-ls.jpg", "BEDS", "Rest,\nbeautifully made.", (0.6, 0.6)),
    ("bed-rian", "n-rian-ls.jpg", "BEDS", "Bedrooms,\ndone properly.", (0.55, 0.6)),
    ("deewan-baroque", "n-baroque4.jpg", "DEEWAN", "Lounging,\nelevated.", (0.4, 0.6)),
]


ADS = [
    ("scb-ottinayine", "scb-otti-trim.jpg", "SOFA CUM BEDS", "Sofa by day.\nBed by night.", "panel"),
    ("scb-2124", "scb-2124-trim.jpg", "SOFA CUM BEDS", "One piece.\nTwo rooms' work.", "panel"),
    ("ss-allington", "ss-allington.webp", "SINGLE SEATERS", "Your corner,\nperfected.", (0.5, 0.65)),
    ("ss-caffery", "ss-caffery.jpg", "SINGLE SEATERS", "One chair.\nAll the character.", "panel"),
]


def f(name, size, w=None):
    ft = ImageFont.truetype(os.path.join(FONTS, name), size)
    if w:
        ft.set_variation_by_axes([w])
    return ft


def spaced(d, xy, text, font, fill, track, anchor="l"):
    """Draw letter-spaced caps. anchor l or r."""
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x, y = xy
    if anchor == "r":
        x -= total
    for c, w in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill)
        x += w + track
    return total


def render(slug, photo, cat, head, centering, W=1080, H=1350):
    im = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(im)
    m = 64
    # top bar
    spaced(d, (m, 46), "HOMESPECTATIONS", f("Manrope.ttf", 22, 700), INK, 6)
    # photo
    py, ph = 104, 790
    src = Image.open(os.path.join(SRC, photo)).convert("RGB")
    if centering == "panel":  # white cut-out: fit whole product on white, no crop
        pic = Image.new("RGB", (W - 2 * m, ph), (255, 255, 255))
        bb = src.convert("L").point(lambda v: 255 if v < 245 else 0).getbbox()
        src = src.crop(bb) if bb else src
        src.thumbnail((W - 2 * m - 90, ph - 120), Image.LANCZOS)
        pic.paste(src, ((pic.width - src.width) // 2, (ph - src.height) // 2))
    else:
        bb = src.convert("L").point(lambda v: 255 if v < 240 else 0).getbbox()
        if bb and (bb[2] - bb[0]) < src.width * 0.97:
            src = src.crop((bb[0], 0, bb[2], src.height))
        pic = ImageOps.fit(src, (W - 2 * m, ph), Image.LANCZOS, centering=centering)
    im.paste(pic, (m, py))
    # text block
    ty = py + ph + 46
    spaced(d, (m, ty), cat, f("Manrope.ttf", 22, 700), BRASS, 5)
    hf = f("Cormorant.ttf", 76, 600)
    y = ty + 34
    for line in head.split("\n"):
        d.text((m, y), line, font=hf, fill=INK)
        y += 78
    # big 11.11 mark, right of the headline
    nf = ImageFont.truetype(os.path.join(FONTS, "DMSerifDisplay-Regular.ttf"), 128)
    d.text((W - m, ty + 132), "11.11", font=nf, fill=BRASS, anchor="rs")
    offer = os.environ.get("OFFER", "")
    spaced(d, (W - m, ty + 146), offer or "SALE", f("Manrope.ttf", 22, 700), INK, 6 if offer else 10, anchor="r")
    sf = f("Manrope.ttf", 25, 500)
    d.text((m, H - 74), "Built to order  ·  Delivered across Pakistan", font=sf, fill=MUTED, anchor="ls")
    cf = f("Manrope.ttf", 25, 700)
    cta = "Shop the collection  →"
    d.text((W - m, H - 74), cta, font=cf, fill=INK, anchor="rs")
    cw = d.textlength(cta, font=cf)
    d.line((W - m - cw, H - 62, W - m, H - 62), fill=INK, width=2)
    out = os.path.join(OUT, f"{slug}_4x5.jpg")
    im.save(out, quality=94)
    return out


os.makedirs(OUT, exist_ok=True)
only = sys.argv[3:]
for a in ADS:
    if not only or a[0] in only:
        print(render(*a))
