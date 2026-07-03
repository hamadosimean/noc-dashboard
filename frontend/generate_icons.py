#!/usr/bin/env python3
"""
Regenerates the app logo variants and browser favicon set from the master
brand asset (src/assets/images/noc-logo.png).

Run this after swapping in a new logo:
    python3 frontend/generate_icons.py

Requires Pillow: pip install pillow
"""
from PIL import Image, ImageDraw

SRC = "src/assets/images/noc-logo.png"
IMAGES_DIR = "src/assets/images"
PUBLIC_DIR = "public"
NAVY = (11, 18, 32)  # matches --color-page in src/index.css


def clean_master(path: str) -> Image.Image:
    """Masks the 4 corners transparent via a geometric rounded-rect (not
    color-keying — the mark itself has white accents that must stay opaque)."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    radius = int(w * 0.214)  # ~268px at 1254px source — matches the brand's corner roundedness
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    rgba = img.convert("RGBA")
    rgba.putalpha(mask)
    return rgba


def main():
    rgba = clean_master(SRC)
    rgba.save(f"{IMAGES_DIR}/noc-logo.png")
    rgba.resize((256, 256), Image.LANCZOS).save(f"{IMAGES_DIR}/noc-logo-256.png", optimize=True)

    # Favicons: flatten onto navy (crisper than transparency at 16-32px).
    flat_bg = Image.new("RGBA", rgba.size, NAVY + (255,))
    flat = Image.alpha_composite(flat_bg, rgba).convert("RGB")

    flat.resize((16, 16), Image.LANCZOS).save(f"{PUBLIC_DIR}/favicon-16x16.png")
    flat.resize((32, 32), Image.LANCZOS).save(f"{PUBLIC_DIR}/favicon-32x32.png")
    flat.resize((180, 180), Image.LANCZOS).save(f"{PUBLIC_DIR}/apple-touch-icon.png")
    flat.resize((192, 192), Image.LANCZOS).save(f"{PUBLIC_DIR}/icon-192.png")
    flat.resize((512, 512), Image.LANCZOS).save(f"{PUBLIC_DIR}/icon-512.png")
    flat.save(f"{PUBLIC_DIR}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    print("Regenerated logo variants and favicon set.")


if __name__ == "__main__":
    main()
