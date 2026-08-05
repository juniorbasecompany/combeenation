"""Gera tile SVG seamless de favo de mel com células preenchidas."""
from __future__ import annotations

import math
from pathlib import Path

W = 56.0
H = W * math.sqrt(3) / 2
ROW_DY = H * 0.75
TILE_W = W
TILE_H = ROW_DY * 2

# Cores estilo cera / mel (sobre fundo escuro do hero)
FILL = "#c4840a"
STROKE = "#f6b719"
FILL_OPACITY = "0.22"
STROKE_OPACITY = "0.95"

OUT = Path(__file__).resolve().parent / "assets" / "images" / "svg" / "honeycomb-pattern.svg"


def hex_path(cx: float, cy: float) -> str:
    pts = [
        (cx - W / 4, cy - H / 2),
        (cx + W / 4, cy - H / 2),
        (cx + W / 2, cy),
        (cx + W / 4, cy + H / 2),
        (cx - W / 4, cy + H / 2),
        (cx - W / 2, cy),
    ]
    body = " L ".join(f"{x:.3f} {y:.3f}" for x, y in pts)
    return f"M {body} Z"


def main() -> None:
    # Hexágonos cujos centros caem na faixa do tile (inclui vizinhos que
    # ultrapassam a borda para o background-repeat fechar sem costura).
    path_list: list[str] = []
    for row in range(-1, 3):
        y = H / 2 + row * ROW_DY
        x_off = (W / 2) if (row % 2 == 0) else 0.0
        for col in range(-1, 3):
            cx = x_off + col * W
            cy = y
            # só desenha se intersecta o tile
            if cx + W / 2 < -1 or cx - W / 2 > TILE_W + 1:
                continue
            if cy + H / 2 < -1 or cy - H / 2 > TILE_H + 1:
                continue
            path_list.append(f'<path d="{hex_path(cx, cy)}"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{TILE_W}" height="{TILE_H:.4f}" viewBox="0 0 {TILE_W:.4f} {TILE_H:.4f}">
  <!-- Favo de mel: hexágonos flat-top com preenchimento de cera -->
  <g fill="{FILL}" fill-opacity="{FILL_OPACITY}" stroke="{STROKE}" stroke-opacity="{STROKE_OPACITY}" stroke-width="1.75" stroke-linejoin="round">
    {chr(10).join("    " + p for p in path_list)}
  </g>
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({len(path_list)} hexes), tile {TILE_W}x{TILE_H:.4f}")


if __name__ == "__main__":
    main()
