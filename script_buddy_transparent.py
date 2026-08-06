"""Buddy sem contorno: todo branco vira transparente (estilo 1a imagem)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "docs" / "buddy.png"
OUT_WEBP = ROOT / "assets" / "images" / "buddy.webp"

# Quase-branco -> transparente (fundo, faixa, focinho, peito, contorno)
WHITE_MIN = 230


def whiten_to_alpha(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    assert px is not None
    cleared = 0
    kept = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8 or (r >= WHITE_MIN and g >= WHITE_MIN and b >= WHITE_MIN):
                if a != 0:
                    cleared += 1
                px[x, y] = (0, 0, 0, 0)
            else:
                # anti-alias claro na borda do branco
                if min(r, g, b) >= 200 and abs(r - g) < 12 and abs(g - b) < 12:
                    px[x, y] = (0, 0, 0, 0)
                    cleared += 1
                else:
                    kept += 1
    print(f"cleared~{cleared} kept={kept}")
    return im


def trim(im: Image.Image, pad: int = 12) -> Image.Image:
    bbox = im.getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    return im.crop(
        (
            max(0, l - pad),
            max(0, t - pad),
            min(im.width, r + pad),
            min(im.height, b + pad),
        )
    )


def main() -> None:
    print(f"source: {SRC}")
    out = trim(whiten_to_alpha(Image.open(SRC)))
    px = out.load()
    assert px is not None
    for pt in [(0, 0), (out.width - 1, 0), (0, out.height - 1), (out.width - 1, out.height - 1)]:
        if px[pt][3] != 0:
            raise SystemExit(f"corner not transparent: {pt}")

    white_left = 0
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a > 200 and r >= WHITE_MIN and g >= WHITE_MIN and b >= WHITE_MIN:
                white_left += 1
    print(f"remaining opaque white={white_left} size={out.size}")
    if white_left > 50:
        raise SystemExit("still has white outline/fill")

    OUT_WEBP.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT_WEBP, "WEBP", quality=92, method=6)
    print(f"wrote {OUT_WEBP}")


if __name__ == "__main__":
    main()
