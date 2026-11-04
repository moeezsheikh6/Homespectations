"""One product, one image, minimal text. 11.11 sale.

Usage: python3 render_single.py <fonts_dir> <out_dir> <photo> <name> <price> <slug>
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONTS, OUT, PHOTO, NAME, PRICE, SLUG = sys.argv[1:7]
PRICE = int(PRICE)
BRASS = (214, 172, 98)
WHITE = (255, 255, 255)
SOFT = (232, 228, 220)


def f(name, size, w=None):
    ft = ImageFont.truetype(os.path.join(FONTS, name), size)
    if w:
        ft.set_variation_by_name(w)
    return ft


def gradient(W, H, y0, y1, max_a, up=False):
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        if y0 <= y <= y1:
            t = (y - y0) / max(1, (y1 - y0))
            g.putpixel((0, y), int(max_a * ((1 - t) if up else t) ** 1.6))
    return g.resize((W, H))


def render(W, H, out):
    story = H >= 1900
    im = Image.open(PHOTO).convert("RGB")
    bb = im.convert("L").point(lambda v: 255 if v < 245 else 0).getbbox()
    im = im.crop(bb)
    if story:
        # keep the whole piece: photo full width, dark ground above and below
        ph = ImageOps.fit(im, (W, int(W * im.height / im.width)), Image.LANCZOS)
        canvas = Image.new("RGB", (W, H), (14, 14, 14))
        canvas.paste(ph, (0, (H - ph.height) // 2 - 40))
        im = canvas
    else:
        im = ImageOps.fit(im, (W, H), Image.LANCZOS, centering=(0.5, 1.0))
    dark = Image.new("RGB", (W, H), (12, 12, 12))
    im = Image.composite(dark, im, gradient(W, H, H // 2, H, 225))
    im = Image.composite(dark, im, gradient(W, H, 0, 300 + (200 if story else 0), 150, up=True))
    d = ImageDraw.Draw(im)
    m = 64
    top = 230 if story else 56
    bot = H - (330 if story else 64)

    # 11.11 SALE tag, top left
    ft = f("Anton.ttf", 92)
    tw = d.textlength("11.11 SALE", font=ft)
    d.rectangle((m, top, m + tw + 56, top + 140), fill=(16, 16, 16))
    d.text((m + 28, top + 70), "11.11 SALE", font=ft, fill=BRASS, anchor="lm")
    d.text((W - m, bot + 2), "HOMESPECTATIONS", font=f("Manrope.ttf", 22, "ExtraBold"), fill=(170, 166, 158), anchor="rs")

    # bottom: name + price + one line
    d.text((m, bot - 60), "Free delivery across Pakistan  ·  20% advance", font=f("Manrope.ttf", 28, "SemiBold"), fill=SOFT, anchor="ls")
    d.text((m, bot - 120), f"PKR {PRICE:,}", font=f("Manrope.ttf", 46, "Bold"), fill=BRASS, anchor="ls")
    d.text((m, bot - 190), NAME, font=f("DMSerifDisplay-Regular.ttf", 88), fill=WHITE, anchor="ls")
    im.save(out, quality=93)


os.makedirs(OUT, exist_ok=True)
for tag, size in {"feed-4x5": (1080, 1350), "story-9x16": (1080, 1920)}.items():
    p = os.path.join(OUT, f"{SLUG}_{tag}.jpg")
    render(*size, p)
    print(p)
