"""Buddy sem contorno: todo branco vira transparente (estilo 1ª imagem)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "docs" / "buddy.png"
OUT_PNG = ROOT / "assets" / "images" / "buddy.png"
OUT_WEBP = ROOT / "assets" / "images" / "buddy.webp"
OUT_PREVIEW = ROOT / "docs" / "buddy-on-circle-preview.png"

# Quase-branco → transparente (fundo, faixa, focinho, peito, contorno)
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
                # anti-alias claro na borda do branco: suaviza alpha
                # se for cinza muito claro residual, também some
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


def write_preview(im: Image.Image) -> None:
    size = 640
    margin = 40
    diam = size - 2 * margin
    bg = Image.new("RGBA", (size, size), (51, 41, 30, 255))
    circle = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(circle).ellipse(
        (margin, margin, size - margin, size - margin), fill=(255, 231, 160, 255)
    )
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse(
        (margin, margin, size - margin, size - margin), fill=255
    )

    dog_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dog = im.copy()
    dog.thumbnail((int(diam * 0.70), int(diam * 0.70)), Image.Resampling.LANCZOS)
    dog_layer.alpha_composite(
        dog, ((size - dog.width) // 2, (size - dog.height) // 2 + int(diam * 0.03))
    )
    dog_clipped = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dog_clipped.paste(dog_layer, (0, 0), mask)

    out = Image.alpha_composite(Image.alpha_composite(bg, circle), dog_clipped)
    OUT_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    out.convert("RGB").save(OUT_PREVIEW)
    print(f"wrote {OUT_PREVIEW}")


def main() -> None:
    print(f"source: {SRC}")
    out = trim(whiten_to_alpha(Image.open(SRC)))
    px = out.load()
    assert px is not None
    for pt in [(0, 0), (out.width - 1, 0), (0, out.height - 1), (out.width - 1, out.height - 1)]:
        if px[pt][3] != 0:
            raise SystemExit(f"corner not transparent: {pt}")

    # não deve restar branco opaco (contorno)
    white_left = 0
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a > 200 and r >= WHITE_MIN and g >= WHITE_MIN and b >= WHITE_MIN:
                white_left += 1
    print(f"remaining opaque white={white_left} size={out.size}")
    if white_left > 50:
        raise SystemExit("still has white outline/fill")

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT_PNG, optimize=True)
    out.save(OUT_WEBP, "WEBP", quality=92, method=6)
    print(f"wrote {OUT_PNG} and {OUT_WEBP}")
    write_preview(out)


if __name__ == "__main__":
    main()
