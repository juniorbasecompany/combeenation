"""Gera tile seamless de favo (hexágonos pointy-top)."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

# Pointy-top — https://www.redblobgames.com/grids/hexagons/
SIZE = 36.0
W = math.sqrt(3) * SIZE
H = 2.0 * SIZE
VERT = 1.5 * SIZE
TILE_W = W
TILE_H = 2.0 * VERT  # 3 * SIZE

ROOT = Path(__file__).resolve().parent
OUT_PNG = ROOT / "assets" / "images" / "honeycomb-pattern.png"
OUT_SVG = ROOT / "assets" / "images" / "svg" / "honeycomb-pattern.svg"
OUT_PREVIEW = ROOT / "docs" / "honeycomb-preview.png"
OUT_TILED = ROOT / "docs" / "honeycomb-tiled-check.png"


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
    """
    Gera arestas de hexágonos numa vizinhança do tile e mantém
    cada aresta uma vez (evita diagonais internas / estrelas).
    """
    edges: set[tuple] = set()
    # cobrir tile + margem
    for row in range(-1, 4):
        cy = SIZE + row * VERT
        x_off = (W / 2) if (row % 2) else 0.0
        for col in range(-1, 3):
            cx = W / 2 + x_off + col * W
            pts = hex_corners(cx, cy)
            for i in range(6):
                edges.add(edge_key(pts[i], pts[(i + 1) % 6]))

    # Só arestas que intersectam o retângulo do tile (com pequena folga)
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


def write_svg(edge_list: list[tuple[tuple[float, float], tuple[float, float]]]) -> None:
    lines = [
        f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}"/>'
        for a, b in edge_list
    ]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{TILE_W:.4f}" height="{TILE_H:.4f}" viewBox="0 0 {TILE_W:.4f} {TILE_H:.4f}">
  <g fill="none" stroke="#f6b719" stroke-opacity="0.9" stroke-width="1.7" stroke-linecap="round">
    {chr(10).join("    " + line for line in lines)}
  </g>
</svg>
"""
    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT_SVG} ({len(lines)} edges)")


def write_preview() -> None:
    cols, rows = 10, 9
    pw = int(cols * W + W * 0.5)
    ph = int(rows * VERT + H)
    img = Image.new("RGB", (pw, ph), "#1a1510")
    draw = ImageDraw.Draw(img)
    for row in range(rows):
        cy = SIZE + row * VERT
        x_off = (W / 2) if (row % 2) else 0.0
        for col in range(cols):
            cx = W / 2 + x_off + col * W
            pts = hex_corners(cx, cy)
            draw.polygon(pts, outline=(246, 183, 25), width=2)
    OUT_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_PREVIEW)
    print(f"wrote {OUT_PREVIEW}")


def write_tiled_check() -> None:
    """Repete o PNG 3x3 para validar costura."""
    tile = Image.open(OUT_PNG).convert("RGBA")
    tw, th = tile.size
    canvas = Image.new("RGB", (tw * 3, th * 3), "#1a1510")
    for gy in range(3):
        for gx in range(3):
            canvas.paste(tile, (gx * tw, gy * th), tile)
    OUT_TILED.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT_TILED)
    print(f"wrote {OUT_TILED}")


def main() -> None:
    edge_list = collect_unique_edges()
    write_png(edge_list)
    write_svg(edge_list)
    write_preview()
    write_tiled_check()


if __name__ == "__main__":
    main()
