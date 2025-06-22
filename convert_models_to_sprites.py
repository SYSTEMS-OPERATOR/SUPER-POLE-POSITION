#!/usr/bin/env python3
"""Convert 3D models to sprites with optional banking."""
from __future__ import annotations

import argparse
from pathlib import Path

try:
    import pygame
except Exception:  # pragma: no cover
    pygame = None


def render(model: Path, out_dir: Path, bank: str | None = None) -> None:
    if pygame is None:
        return
    img = pygame.image.load(str(model))
    angle = 0
    suffix = ""
    if bank == "left":
        angle = 10
        suffix = "_bankL"
    elif bank == "right":
        angle = -10
        suffix = "_bankR"
    rotated = pygame.transform.rotate(img, angle)
    out = pygame.transform.smoothscale(rotated, (64, 64))
    out_dir.mkdir(parents=True, exist_ok=True)
    pygame.image.save(out, str(out_dir / f"{model.stem}{suffix}.png"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("models", nargs="+")
    parser.add_argument("--out", default="assets/sprites")
    parser.add_argument("--bank", choices=["left", "right"])
    args = parser.parse_args()

    if pygame is None:
        return
    pygame.init()
    out = Path(args.out)
    for m in args.models:
        p = Path(m)
        render(p, out)
        if "player" in p.stem and args.bank:
            render(p, out, args.bank)
    pygame.quit()


if __name__ == "__main__":
    main()
