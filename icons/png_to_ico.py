#!/usr/bin/env python3
"""
Convert a PNG to a square ICO (app icon).
- If the PNG is not square, center-crops to a square (uses the smaller dimension).
- Saves as .ico with common sizes (16, 32, 48, 256) for Windows.

Usage:
  python png_to_ico.py input.png [output.ico]
  python png_to_ico.py icons/logo.png icons/app.ico

Requires: pip install Pillow
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Install Pillow: pip install Pillow")
    sys.exit(1)

ICO_SIZES = (16, 32, 48, 256)


def png_to_square_ico(png_path: str | Path, ico_path: str | Path | None = None) -> Path:
    """Load PNG, make it square (center-crop), save as ICO. Returns path to saved ICO."""
    png_path = Path(png_path)
    if not png_path.is_file():
        raise FileNotFoundError(f"Not found: {png_path}")

    if ico_path is None:
        ico_path = png_path.with_suffix(".ico")
    else:
        ico_path = Path(ico_path)

    img = Image.open(png_path).convert("RGBA")
    w, h = img.size

    # Center-crop to square (side = min(w, h))
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    # Resize to 256 for a clean base; Pillow will generate other sizes for ICO
    img = img.resize((256, 256), Image.Resampling.LANCZOS)

    # Save as ICO with standard sizes
    img.save(ico_path, format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    return ico_path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    png = sys.argv[1]
    ico = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        out = png_to_square_ico(png, ico)
        print(f"Saved: {out}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
