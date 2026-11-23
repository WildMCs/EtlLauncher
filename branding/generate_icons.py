#!/usr/bin/env python3
"""Export PNG variants and a Windows ICO from the same transparent master."""

import argparse
from pathlib import Path

from PIL import Image, ImageOps


BRANDING = Path(__file__).resolve().parent
MASTER = BRANDING.parent / "public-news/IconApp/Modrith_rosita_fresita.png"
WINDOWS_SIZES = (16, 24, 32, 40, 48, 64, 96, 128, 256)
PNG_SIZES = (*WINDOWS_SIZES, 512)


def render_icon(master: Image.Image, size: int) -> Image.Image:
    margin = max(1, round(size * 0.02))
    content_size = size - 2 * margin
    content = ImageOps.contain(master, (content_size, content_size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size))
    canvas.paste(content, ((size - content.width) // 2, (size - content.height) // 2))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, nargs="?", default=MASTER)
    parser.add_argument("--output", type=Path, default=BRANDING / "icons")
    args = parser.parse_args()

    with Image.open(args.source, formats=["PNG"]) as source:
        master = source.convert("RGBA")
    if max(master.size) < max(PNG_SIZES) or master.getchannel("A").getbbox() is None:
        parser.error("Use a visible PNG at least 512 pixels on its longest side.")

    args.output.mkdir(parents=True, exist_ok=True)
    variants = {size: render_icon(master, size) for size in PNG_SIZES}
    for size, image in variants.items():
        image.save(args.output / f"{size}.png")
    largest = WINDOWS_SIZES[-1]
    variants[largest].save(
        args.output / "EternalLauncher.ico",
        sizes=[(size, size) for size in WINDOWS_SIZES],
        append_images=[variants[size] for size in WINDOWS_SIZES[:-1]],
    )


if __name__ == "__main__":
    main()
