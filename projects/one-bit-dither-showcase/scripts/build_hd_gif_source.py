#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
# ]
# ///

"""Build a deterministic 16:9 harbor animation for the high-definition GIF showcase."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw


WIDTH = 640
HEIGHT = 360
SCALE = 2
FRAMES = 36
FPS = 12


def scaled_point(point: tuple[float, float]) -> tuple[int, int]:
    return round(point[0] * SCALE), round(point[1] * SCALE)


def scaled_box(box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    return tuple(round(value * SCALE) for value in box)  # type: ignore[return-value]


def interpolate(first: tuple[int, int, int], second: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(left + (right - left) * amount) for left, right in zip(first, second, strict=True))  # type: ignore[return-value]


def draw_gradient(image: Image.Image, top: tuple[int, int, int], bottom: tuple[int, int, int], horizon: int) -> None:
    draw = ImageDraw.Draw(image)
    for y in range(horizon * SCALE):
        amount = y / max(1, horizon * SCALE - 1)
        draw.line((0, y, WIDTH * SCALE, y), fill=interpolate(top, bottom, amount))


def build_frame(frame_index: int) -> Image.Image:
    phase = frame_index / FRAMES
    image = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), (14, 25, 38))
    draw_gradient(image, (9, 19, 34), (108, 72, 58), 230)
    draw = ImageDraw.Draw(image, "RGBA")

    # A slow moon and layered clouds provide low-frequency tonal movement.
    moon_x = 116 + 4 * math.sin(phase * math.tau)
    moon_y = 70 + 2 * math.cos(phase * math.tau)
    draw.ellipse(scaled_box((moon_x - 34, moon_y - 34, moon_x + 34, moon_y + 34)), fill=(232, 218, 174, 245))
    draw.ellipse(scaled_box((moon_x - 20, moon_y - 30, moon_x + 22, moon_y + 18)), fill=(82, 68, 67, 115))
    for layer, (base_y, speed, color) in enumerate(
        ((72, 30, (61, 69, 80, 170)), (116, -20, (86, 73, 75, 135)), (154, 12, (118, 87, 75, 95)))
    ):
        offset = ((phase * speed * 12) + layer * 83) % (WIDTH + 180) - 90
        for cloud_index in range(4):
            center_x = (offset + cloud_index * 190) % (WIDTH + 180) - 90
            radius = 22 + cloud_index % 2 * 9
            draw.ellipse(
                scaled_box((center_x - radius * 1.8, base_y - radius * 0.45, center_x + radius * 1.8, base_y + radius * 0.45)),
                fill=color,
            )
            draw.ellipse(
                scaled_box((center_x - radius, base_y - radius, center_x + radius, base_y + radius * 0.5)),
                fill=color,
            )

    # Distant harbor silhouettes and warm windows.
    draw.rectangle(scaled_box((0, 211, WIDTH, 242)), fill=(20, 31, 42, 255))
    for building_index, (x, width, height) in enumerate(((16, 42, 25), (65, 65, 41), (138, 34, 30), (178, 70, 54))):
        draw.rectangle(scaled_box((x, 211 - height, x + width, 220)), fill=(17, 28, 38, 255))
        for window_index in range(max(1, width // 18)):
            if (window_index + building_index + frame_index // 9) % 3:
                wx = x + 8 + window_index * 17
                draw.rectangle(scaled_box((wx, 202 - height, wx + 4, 207 - height)), fill=(233, 160, 83, 220))

    # Lighthouse and a sweeping translucent beam. Its stable pivot makes the dither readable.
    tower_x = 504
    lantern_y = 105
    sweep = math.sin(phase * math.tau) * 0.72
    beam_length = 320
    beam_spread = 0.17
    beam_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    beam_draw = ImageDraw.Draw(beam_layer, "RGBA")
    pivot = scaled_point((tower_x, lantern_y))
    far_a = scaled_point(
        (tower_x - math.cos(sweep - beam_spread) * beam_length, lantern_y + math.sin(sweep - beam_spread) * beam_length)
    )
    far_b = scaled_point(
        (tower_x - math.cos(sweep + beam_spread) * beam_length, lantern_y + math.sin(sweep + beam_spread) * beam_length)
    )
    beam_draw.polygon((pivot, far_a, far_b), fill=(242, 211, 139, 82))
    image = Image.alpha_composite(image.convert("RGBA"), beam_layer).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    draw.polygon(
        tuple(map(scaled_point, ((475, 226), (492, 121), (516, 121), (533, 226)))),
        fill=(219, 207, 177, 255),
    )
    for stripe_y in (145, 179):
        draw.polygon(
            tuple(map(scaled_point, ((488, stripe_y), (520, stripe_y), (524, stripe_y + 13), (486, stripe_y + 13)))),
            fill=(121, 53, 43, 255),
        )
    draw.rectangle(scaled_box((485, 99, 523, 122)), fill=(28, 35, 42, 255))
    draw.rectangle(scaled_box((490, 103, 518, 118)), fill=(239, 170, 72, 255))
    glow = round(9 + 3 * math.sin(phase * math.tau * 2))
    draw.ellipse(scaled_box((504 - glow, lantern_y - glow, 504 + glow, lantern_y + glow)), fill=(255, 215, 120, 175))
    draw.polygon(tuple(map(scaled_point, ((480, 99), (528, 99), (504, 82)))), fill=(18, 28, 37, 255))

    # Animated sea: many thin waves survive one-bit sampling better than a flat fill.
    draw.rectangle(scaled_box((0, 229, WIDTH, HEIGHT)), fill=(22, 62, 72, 255))
    for band in range(13):
        y = 235 + band * 10
        amplitude = 1.7 + band * 0.10
        period = 42 + band * 4
        shift = phase * (54 + band * 5)
        points = []
        for x in range(-10, WIDTH + 11, 4):
            wave_y = y + math.sin((x + shift) / period * math.tau) * amplitude
            points.append(scaled_point((x, wave_y)))
        color = (101 + band * 5, 145 + band * 4, 149 + band * 3, 175)
        draw.line(points, fill=color, width=2 * SCALE)

    # Foreground launch bobs while crossing the watchman's field of view.
    boat_x = 252 + 14 * math.sin(phase * math.tau)
    bob = 5 * math.sin(phase * math.tau * 2)
    draw.polygon(
        tuple(map(scaled_point, ((boat_x - 96, 280 + bob), (boat_x + 92, 280 + bob), (boat_x + 61, 309 + bob), (boat_x - 69, 309 + bob)))),
        fill=(13, 23, 31, 255),
    )
    draw.rectangle(scaled_box((boat_x - 48, 247 + bob, boat_x + 38, 281 + bob)), fill=(26, 35, 40, 255))
    draw.polygon(
        tuple(map(scaled_point, ((boat_x - 30, 247 + bob), (boat_x + 23, 247 + bob), (boat_x + 5, 225 + bob), (boat_x - 18, 225 + bob)))),
        fill=(46, 49, 47, 255),
    )
    draw.line((scaled_point((boat_x - 8, 226 + bob)), scaled_point((boat_x - 8, 184 + bob))), fill=(9, 20, 28, 255), width=3 * SCALE)
    draw.polygon(
        tuple(map(scaled_point, ((boat_x - 6, 188 + bob), (boat_x + 38, 207 + bob), (boat_x - 6, 218 + bob)))),
        fill=(184, 81, 54, 240),
    )
    draw.ellipse(scaled_box((boat_x - 36, 252 + bob, boat_x - 24, 264 + bob)), fill=(239, 177, 78, 255))
    draw.ellipse(scaled_box((boat_x + 8, 252 + bob, boat_x + 20, 264 + bob)), fill=(239, 177, 78, 255))

    # Salt spray/rain uses deterministic trajectories so the loop closes cleanly.
    for particle in range(55):
        seed_x = (particle * 97 + 31) % WIDTH
        seed_y = (particle * 53 + 17) % HEIGHT
        x = (seed_x - phase * (44 + particle % 7) + WIDTH) % WIDTH
        y = (seed_y + phase * (105 + particle % 11)) % HEIGHT
        alpha = 70 + (particle * 19) % 120
        draw.line((scaled_point((x, y)), scaled_point((x - 2, y + 7))), fill=(211, 224, 221, alpha), width=SCALE)

    # Finish with high-quality downsampling; the source remains colorful for regional-mode tests.
    return image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--poster", type=Path)
    args = parser.parse_args(argv)
    if args.output.suffix.lower() != ".gif":
        parser.error("--output must end in .gif")
    if args.poster and args.poster.suffix.lower() != ".png":
        parser.error("--poster must end in .png")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    frames = [build_frame(index) for index in range(FRAMES)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        args.output,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / FPS),
        loop=0,
        disposal=2,
        optimize=False,
    )
    if args.poster:
        args.poster.parent.mkdir(parents=True, exist_ok=True)
        frames[9].save(args.poster)
    print(f"Wrote {args.output.resolve()} ({WIDTH}x{HEIGHT}, {FRAMES} frames, {FPS} fps)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
