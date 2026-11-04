"""One product, one image, minimal text. 11.11 sale.

Usage: python3 render_single.py <fonts_dir> <out_dir> <photo> <name> <price> <slug>
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

FONTS, OUT, PHOTO, NAME, PRICE, SLUG = sys.argv[1:7]
MODE = sys.argv[7] if len(sys.argv) > 7 else "room"
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


def studio(W, H, story):
    """Warm wall + floor scene with the product cut out from its white background."""
    wall_top, wall_bot = (88, 78, 66), (150, 136, 116)
    floor_y = int(H * (0.66 if not story else 0.62))
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(floor_y):
        t = y / floor_y
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(wall_top, wall_bot)))
    for y in range(floor_y, H):
        t = (y - floor_y) / (H - floor_y)
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip((118, 92, 66), (60, 44, 32))))
    # soft light pool on the wall
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((W * 0.1, H * 0.1, W * 0.9, floor_y * 1.05), fill=70)
    bg = Image.composite(Image.new("RGB", (W, H), (205, 190, 166)), bg, glow.filter(ImageFilter.GaussianBlur(160)))
    src = Image.open(PHOTO).convert("RGB")
    lum = src.convert("L")
    mask = lum.point(lambda v: 0 if v > 200 else (255 if v < 170 else int((200 - v) / 30 * 255)))
    # drop the neutral grey floor shadow baked into the photo (sofa leather is warm, shadow is grey)
    hsv = src.convert("HSV")
    _, sat, val = hsv.split()
    grey = Image.merge("RGB", (sat, val, val)).point(lambda v: v)
    m2 = Image.new("L", src.size, 255)
    sp, vp, mp = sat.load(), val.load(), m2.load()
    for y in range(src.height):
        for x in range(src.width):
            if vp[x, y] > 95 and sp[x, y] < 40:
                mp[x, y] = 0
    from PIL import ImageChops
    mask = ImageChops.multiply(mask, m2).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.MinFilter(15)).filter(ImageFilter.MinFilter(3))
    bb = mask.point(lambda v: 255 if v > 40 else 0).getbbox()
    src, mask = src.crop(bb), mask.crop(bb)
    # clear stray floor bits between the outer legs
    ImageDraw.Draw(mask).rectangle((int(mask.width * 0.15), int(mask.height * 0.845), int(mask.width * 0.85), mask.height), fill=0)
    pw = int(W * 0.94)
    ph = int(src.height * pw / src.width)
    src = src.resize((pw, ph), Image.LANCZOS)
    mask = mask.resize((pw, ph), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
    px, py = (W - pw) // 2, floor_y + int((H - floor_y) * 0.18) - ph
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse((px + pw * 0.04, py + ph - 26, px + pw * 0.96, py + ph + 30), fill=170)
    bg = Image.composite(Image.new("RGB", (W, H), (25, 18, 12)), bg, sh.filter(ImageFilter.GaussianBlur(22)))
    bg.paste(src, (px, py), mask)
    return bg


def render(W, H, out):
    story = H >= 1900
    if MODE == "studio":
        im = studio(W, H, story)
        return finish(im, W, H, story, out)
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
    return finish(im, W, H, story, out)


def finish(im, W, H, story, out):
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
