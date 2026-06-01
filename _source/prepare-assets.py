#!/usr/bin/env python3
"""
prepare-assets.py — generate optimised image variants (WebP, AVIF, smaller sizes)
and favicons from the master assets. Run once when source images change.

Produces under _source/assets/:
    knrai.jpg               (master, kept as-is — fallback for old browsers)
    knrai.webp              (master in WebP — ~30% smaller)
    knrai-400.webp          (400px square, optimised)
    knrai-200.webp          (200px square, mobile / portrait)
    knrai-100.webp          (100px square, ultra-low bandwidth)
    favicon-16.png, favicon-32.png, favicon-180.png, favicon.ico
    icon-192.png, icon-512.png, icon-maskable-512.png  (PWA)
    og-image.jpg            (1200x630 social card)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
MASTER = ASSETS / "knrai.jpg"


def webp(src, dst, size, quality=82):
    im = Image.open(src).convert("RGB")
    if size:
        im = im.resize((size, size), Image.LANCZOS)
    im.save(dst, "WEBP", quality=quality, method=6)
    print(f"  {dst.name}  ({dst.stat().st_size//1024}k)")


def png_icon(src, dst, size):
    im = Image.open(src).convert("RGBA")
    im = im.resize((size, size), Image.LANCZOS)
    im.save(dst, "PNG", optimize=True)
    print(f"  {dst.name}  ({dst.stat().st_size//1024}k)")


def maskable_icon(src, dst, size):
    """PWA maskable icon — content inside 80% safe zone, purple background."""
    bg = Image.new("RGBA", (size, size), (20, 19, 77, 255))   # #14134d
    im = Image.open(src).convert("RGBA")
    inner = int(size * 0.7)
    im = im.resize((inner, inner), Image.LANCZOS)
    # round-mask the portrait
    mask = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, inner, inner), fill=255)
    im.putalpha(mask)
    offset = (size - inner) // 2
    bg.paste(im, (offset, offset), im)
    bg.save(dst, "PNG", optimize=True)
    print(f"  {dst.name}  ({dst.stat().st_size//1024}k)")


def og_image(src, dst):
    """1200×630 Open Graph card — portrait left, gradient + text right."""
    W, H = 1200, 630
    card = Image.new("RGB", (W, H), (4, 4, 40))   # #040428
    # purple gradient overlay
    grad = Image.new("RGB", (W, H), (4, 4, 40))
    px = grad.load()
    for y in range(H):
        t = y / H
        r = int(4 + (20 - 4) * t)
        g = int(4 + (19 - 4) * t)
        b = int(40 + (77 - 40) * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    card.paste(grad, (0, 0))

    # portrait on the right, circular
    portrait = Image.open(src).convert("RGB").resize((420, 420), Image.LANCZOS)
    mask = Image.new("L", (420, 420), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 420, 420), fill=255)
    card.paste(portrait, (720, 105), mask)

    # text — fall back to default font if our preferred isn't there
    draw = ImageDraw.Draw(card)
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 64)
        sub_font   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 30)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except OSError:
        title_font = ImageFont.load_default()
        sub_font   = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text((80, 180), "neti neti,",       fill=(235, 156, 255), font=title_font)
    draw.text((80, 260), "charaiveti",       fill=(243, 194, 243), font=title_font)
    draw.text((80, 340), "charaiveti.",      fill=(243, 194, 243), font=title_font)
    draw.text((80, 440), "K.N. Rai · Khalil Asgar",   fill=(200, 180, 220), font=sub_font)
    draw.text((80, 500), "netineticharaiveticharaiveti.in", fill=(150, 130, 180), font=small_font)

    card.save(dst, "JPEG", quality=85, optimize=True, progressive=True)
    print(f"  {dst.name}  ({dst.stat().st_size//1024}k)")


def main():
    print("optimising portrait …")
    webp(MASTER, ASSETS / "knrai.webp",     400)
    webp(MASTER, ASSETS / "knrai-400.webp", 400)
    webp(MASTER, ASSETS / "knrai-200.webp", 200)
    webp(MASTER, ASSETS / "knrai-100.webp", 100, quality=78)

    print("favicons …")
    png_icon(MASTER, ASSETS / "favicon-16.png",  16)
    png_icon(MASTER, ASSETS / "favicon-32.png",  32)
    png_icon(MASTER, ASSETS / "favicon-180.png", 180)
    png_icon(MASTER, ASSETS / "icon-192.png",    192)
    png_icon(MASTER, ASSETS / "icon-512.png",    512)
    maskable_icon(MASTER, ASSETS / "icon-maskable-512.png", 512)

    # favicon.ico (multi-size)
    base = Image.open(MASTER).convert("RGBA")
    base.save(ASSETS / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"  favicon.ico  ({(ASSETS / 'favicon.ico').stat().st_size//1024}k)")

    print("Open Graph card …")
    og_image(MASTER, ASSETS / "og-image.jpg")

    print("done.")


if __name__ == "__main__":
    main()
