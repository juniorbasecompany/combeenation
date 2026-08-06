"""Alarga buddy.png: fundo gerado + foto original no centro com costura suave."""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "assets" / "images" / "buddy.png"
# Imagem gerada com extensao de fundo (referencia visual)
WIDE = Path(r"C:\Users\jr\.cursor\projects\c-git-combeenation\assets\buddy-wide.png")
OUT = SRC
FADE = 36


def restore_original() -> Image.Image:
    data = subprocess.check_output(["git", "show", "HEAD:assets/images/buddy.png"])
    SRC.write_bytes(data)
    return Image.open(SRC).convert("RGB")


def compose(orig: Image.Image, wide: Image.Image, fade: int = FADE) -> Image.Image:
    h = orig.size[1]
    base = wide.convert("RGB").resize((h, h), Image.Resampling.LANCZOS)
    ow, _ = orig.size
    left = (h - ow) // 2

    out = base.copy()
    out.paste(orig, (left, 0))

    for i in range(fade):
        a = (i + 1) / (fade + 1)
        x = left + i
        mixed = Image.blend(base.crop((x, 0, x + 1, h)), orig.crop((i, 0, i + 1, h)), a)
        out.paste(mixed, (x, 0))

        x = left + ow - fade + i
        src_x = ow - fade + i
        mixed = Image.blend(
            orig.crop((src_x, 0, src_x + 1, h)),
            base.crop((x, 0, x + 1, h)),
            (i + 1) / (fade + 1),
        )
        out.paste(mixed, (x, 0))

    return out


def main() -> None:
    if not WIDE.exists():
        raise SystemExit(f"missing wide background: {WIDE}")

    print(f"restoring original from git…")
    orig = restore_original()
    print(f"before: {orig.size}")
    out = compose(orig, Image.open(WIDE))
    print(f"after:  {out.size}")
    out.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
