"""Gera tile seamless de favo (hexagonos pointy-top)."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

# Pointy-top - https://www.redblobgames.com/grids/hexagons/
SIZE = 36.0
W = math.sqrt(3) * SIZE
H = 2.0 * SIZE
VERT = 1.5 * SIZE
TILE_W = W
TILE_H = 2.0 * VERT  # 3 * SIZE

ROOT = Path(__file__).resolve().parent
OUT_PNG = ROOT / "assets" / "images" / "honeycomb-pattern.png"


def hex_corners(cx: float, cy: float) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for k in range(6):
        angle = math.radians(-90 + 60 * k)
        pts.append((cx + SIZE * math.cos(angle), cy + SIZE * math.sin(angle)))
    return pts


def edge_key(a: tuple[float, float], b: tuple[float, float]) -> tuple:
    ra = (round(a[0], 3), round(a[1], 3))
    rb = (round(b[0], 3), round(b[1], 3))
    return tuple(sorted((ra, rb)))


def collect_unique_edges() -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Arestas unicas da malha hexagonal na vizinhanca do tile."""
    edges: set[tuple] = set()
    for row in range(-1, 4):
        cy = SIZE + row * VERT
        x_off = (W / 2) if (row % 2) else 0.0
        for col in range(-1, 3):
            cx = W / 2 + x_off + col * W
            pts = hex_corners(cx, cy)
            for i in range(6):
                edges.add(edge_key(pts[i], pts[(i + 1) % 6]))

    kept: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for a, b in edges:
        minx, maxx = min(a[0], b[0]), max(a[0], b[0])
        miny, maxy = min(a[1], b[1]), max(a[1], b[1])
        if maxx < -0.01 or minx > TILE_W + 0.01:
            continue
        if maxy < -0.01 or miny > TILE_H + 0.01:
            continue
        kept.append((a, b))
    return kept


def write_png(edge_list: list[tuple[tuple[float, float], tuple[float, float]]]) -> None:
    scale = 4
    img = Image.new("RGBA", (int(round(TILE_W * scale)), int(round(TILE_H * scale))), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (246, 183, 25, 220)
    width = max(2, scale)

    for a, b in edge_list:
        draw.line(
            [(a[0] * scale, a[1] * scale), (b[0] * scale, b[1] * scale)],
            fill=color,
            width=width,
        )

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_PNG)
    print(f"wrote {OUT_PNG} ({img.size[0]}x{img.size[1]} px, tile {TILE_W:.2f}x{TILE_H:.2f})")


def main() -> None:
    write_png(collect_unique_edges())


if __name__ == "__main__":
    main()
