#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11.0.0", "playwright>=1.52.0"]
# ///

"""Render source previews and build side-by-side pixel-art review images."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
IMAGES = PROJECT / "artifacts" / "images"
sys.path.insert(0, str(ROOT / "skills" / "pixel-art-image-video" / "scripts"))
from pixel_art import render_svg  # noqa: E402


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def prepare(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGBA")
    background = Image.new("RGBA", image.size, "white")
    background.alpha_composite(image)
    return ImageOps.fit(background.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def compare(source: Path, pixel: Path, title: str, note: str, output: Path) -> None:
    with Image.open(source) as source_image, Image.open(pixel) as pixel_image:
        size = pixel_image.size
        original = prepare(source_image, size)
        converted = prepare(pixel_image, size)
    gap = 24
    header = 96
    footer = 42
    width = size[0] * 2 + gap * 3
    height = size[1] + header + footer + gap
    canvas = Image.new("RGB", (width, height), "#12202a")
    draw = ImageDraw.Draw(canvas)
    draw.text((gap, 18), title, font=font(30), fill="#f4f5f2")
    draw.text((gap, 57), note, font=font(21), fill="#b9c7cf")
    draw.text((gap, height - 35), "SOURCE", font=font(18), fill="#f4f5f2")
    draw.text((size[0] + gap * 2, height - 35), "PIXEL ART", font=font(18), fill="#f4f5f2")
    canvas.paste(original, (gap, header))
    canvas.paste(converted, (size[0] + gap * 2, header))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True)
    print(output)


def main() -> None:
    svg = ROOT / "skills" / "vectorize-art-patterns" / "assets" / "examples" / "vectorize-art-patterns" / "svgs" / "vectorize-kandinsky-improvisation-27-cs2.svg"
    svg_preview = IMAGES / "kandinsky-original.png"
    render_svg(svg, (896, 766), 30000).save(svg_preview)
    base = ROOT / "skills" / "vectorize-art-patterns" / "assets" / "base-images"
    compare(base / "van-gogh-bedroom.jpg", IMAGES / "bedroom-pixel.png", "The Bedroom", "4-pixel blocks / 64 adaptive colors / source hues retained", IMAGES / "comparison-bedroom.png")
    compare(base / "hokusai-great-wave.jpg", IMAGES / "wave-pixel.png", "The Great Wave", "3-pixel blocks / 64 adaptive colors / fine detail retained", IMAGES / "comparison-wave.png")
    compare(svg_preview, IMAGES / "kandinsky-pixel.png", "Vectorized artwork from another skill", "4-pixel blocks / 64 adaptive colors / source palette retained", IMAGES / "comparison-kandinsky.png")


if __name__ == "__main__":
    main()
