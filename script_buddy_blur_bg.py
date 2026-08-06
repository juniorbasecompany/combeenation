"""Aplica blur leve no fundo de buddy.png, mantendo o Buddy nitido."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "assets" / "images" / "buddy.png"
OUT = SRC
BLUR_SIGMA = 4.5
FEATHER = 28


def subject_mask(bgr: np.ndarray) -> np.ndarray:
    """Mascara aproximada do Buddy via GrabCut + refinamento."""
    h, w = bgr.shape[:2]
    mask = np.zeros((h, w), np.uint8)

    # Retangulo generoso em volta do cao (centro da foto)
    x0, y0 = int(w * 0.18), int(h * 0.02)
    x1, y1 = int(w * 0.82), int(h * 0.98)
    rect = (x0, y0, x1 - x0, y1 - y0)

    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)

    binary = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

    # Limpa ruido e preenche buracos pequenos
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # Mantem so o maior componente (o cao)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if num > 1:
        # label 0 = fundo
        largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        binary = np.where(labels == largest, 255, 0).astype(np.uint8)

    # Suaviza a borda da mascara
    soft = cv2.GaussianBlur(binary, (0, 0), sigmaX=FEATHER / 3)
    return soft.astype(np.float32) / 255.0


def blur_background(im: Image.Image) -> Image.Image:
    rgb = np.asarray(im.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    alpha = subject_mask(bgr)  # 1 = Buddy, 0 = fundo
    # Expandir um pouco o sujeito para nao borrar orelhas/gravata
    alpha = np.clip(alpha * 1.15, 0, 1)
    alpha = cv2.GaussianBlur(alpha, (0, 0), sigmaX=FEATHER / 2)

    blurred = cv2.GaussianBlur(bgr, (0, 0), sigmaX=BLUR_SIGMA)
    alpha3 = alpha[:, :, None]
    out = (bgr.astype(np.float32) * alpha3 + blurred.astype(np.float32) * (1.0 - alpha3)).astype(
        np.uint8
    )
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))


def main() -> None:
    print(f"source: {SRC}")
    src = Image.open(SRC)
    print(f"size: {src.size}")
    out = blur_background(src)
    out.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} (blur sigma={BLUR_SIGMA})")


if __name__ == "__main__":
    main()
