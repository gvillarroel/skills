#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
# ]
# ///

"""Validate dimensions, timing, palette, looping, and manifest data for a stylized GIF."""

from __future__ import annotations

import argparse
from colorset_contract import colors as colorset_colors
import hashlib
import json
import math
from pathlib import Path
from typing import Sequence

from PIL import Image, UnidentifiedImageError


Color = tuple[int, int, int]
WHITE: Color = (255, 255, 255)
BLACK: Color = (0, 0, 0)


def parse_hex_color(value: str) -> Color:
    token = value.strip().lower()
    if len(token) == 4 and token.startswith("#"):
        token = "#" + "".join(character * 2 for character in token[1:])
    if len(token) != 7 or not token.startswith("#"):
        raise argparse.ArgumentTypeError("color must be #RGB or #RRGGBB")
    try:
        return tuple(int(token[index : index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]
    except ValueError as error:
        raise argparse.ArgumentTypeError("color must be #RGB or #RRGGBB") from error


def color_hex(color: Sequence[int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in color)


def inspect_gif(path: Path) -> dict[str, object]:
    try:
        with Image.open(path) as image:
            if image.format != "GIF":
                raise SystemExit(f"Expected GIF format, found {image.format or 'unknown'}")
            frame_count = max(1, int(getattr(image, "n_frames", 1)))
            durations: list[int] = []
            colors: set[Color] = set()
            frame_color_counts: list[int] = []
            frame_hashes: set[str] = set()
            for frame_index in range(frame_count):
                image.seek(frame_index)
                duration = int(image.info.get("duration", 0) or 0)
                if duration <= 0:
                    raise SystemExit(f"Frame {frame_index} has no positive duration")
                durations.append(duration)
                converted = image.convert("RGB")
                counted = converted.getcolors(maxcolors=1 << 24)
                if counted is None:
                    raise SystemExit(f"Frame {frame_index} exceeds the validator color-count limit")
                frame_colors = {color for _, color in counted}
                colors.update(frame_colors)
                frame_color_counts.append(len(frame_colors))
                frame_hashes.add(hashlib.sha256(converted.tobytes()).hexdigest())
            return {
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "frameCount": frame_count,
                "distinctFrameCount": len(frame_hashes),
                "durationMs": sum(durations),
                "frameDurationsMs": durations,
                "averageFps": round(frame_count * 1000 / sum(durations), 6),
                "loop": int(image.info.get("loop", 0) or 0),
                "palette": [color_hex(color) for color in sorted(colors)],
                "paletteColorCount": len(colors),
                "maxFrameColorCount": max(frame_color_counts),
            }
    except (UnidentifiedImageError, OSError) as error:
        raise SystemExit(f"Cannot inspect GIF {path}: {error}") from error


def load_manifest(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Cannot read manifest {path}: {error}") from error
    if not isinstance(value, dict):
        raise SystemExit("Manifest root must be a JSON object")
    return value


def nested(mapping: dict[str, object], *keys: str) -> object:
    value: object = mapping
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            raise SystemExit(f"Manifest is missing {'.'.join(keys)}")
        value = value[key]
    return value


def validate_manifest(manifest: dict[str, object], gif: Path, probe: dict[str, object]) -> list[str]:
    checks: list[str] = []
    if manifest.get("schema") != "one-bit-dither-gif/v1":
        raise SystemExit("Manifest schema must be one-bit-dither-gif/v1")
    output = Path(str(manifest.get("output", ""))).resolve()
    if output != gif.resolve():
        raise SystemExit(f"Manifest output points to {output}, not {gif.resolve()}")
    for key in ("width", "height", "frameCount"):
        render_value = nested(manifest, "render", key)
        if int(render_value) != int(probe[key]):
            raise SystemExit(f"Manifest render.{key}={render_value} does not match GIF {probe[key]}")
    if int(nested(manifest, "encoding", "loop")) != int(probe["loop"]):
        raise SystemExit("Manifest loop value does not match GIF loop metadata")
    checks.extend(["manifest-schema", "manifest-output", "manifest-render", "manifest-loop"])
    return checks


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gif", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--expect-mode", choices=("original", "custom", "regional"))
    parser.add_argument("--expect-custom-color", type=parse_hex_color)
    parser.add_argument("--expect-source-kind", choices=("svg", "raster"))
    parser.add_argument("--expect-source-format")
    parser.add_argument("--expect-width", type=int)
    parser.add_argument("--expect-height", type=int)
    parser.add_argument("--expect-fps", type=float)
    parser.add_argument("--expect-loop", type=int)
    parser.add_argument("--min-frames", type=int, default=2)
    parser.add_argument("--min-distinct-frames", type=int, default=2)
    parser.add_argument("--max-colors", type=int, default=256)
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args(argv)
    if not args.gif.is_file():
        parser.error(f"GIF not found: {args.gif}")
    if args.gif.suffix.lower() != ".gif":
        parser.error("input must end in .gif")
    if args.manifest and not args.manifest.is_file():
        parser.error(f"manifest not found: {args.manifest}")
    if args.expect_mode == "custom" and args.expect_custom_color is None:
        parser.error("custom mode validation requires --expect-custom-color")
    if args.expect_custom_color is not None and args.expect_mode != "custom":
        parser.error("--expect-custom-color requires --expect-mode custom")
    if (args.expect_source_kind or args.expect_source_format) and args.manifest is None:
        parser.error("source provenance expectations require --manifest")
    if args.min_frames < 2:
        parser.error("--min-frames must be at least 2")
    if args.min_distinct_frames < 2:
        parser.error("--min-distinct-frames must be at least 2")
    if not 2 <= args.max_colors <= 256:
        parser.error("--max-colors must be between 2 and 256")
    if args.expect_fps is not None and args.expect_fps <= 0:
        parser.error("--expect-fps must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    probe = inspect_gif(args.gif)
    checks = ["gif-format", "positive-frame-timing"]
    if int(probe["frameCount"]) < args.min_frames:
        raise SystemExit(f"Expected at least {args.min_frames} frames; found {probe['frameCount']}")
    checks.append("animated-frame-count")
    if int(probe["distinctFrameCount"]) < args.min_distinct_frames:
        raise SystemExit(
            f"Expected at least {args.min_distinct_frames} visually distinct frames; "
            f"found {probe['distinctFrameCount']}"
        )
    checks.append("actual-motion")
    if args.expect_width is not None and int(probe["width"]) != args.expect_width:
        raise SystemExit(f"Expected width {args.expect_width}; found {probe['width']}")
    if args.expect_height is not None and int(probe["height"]) != args.expect_height:
        raise SystemExit(f"Expected height {args.expect_height}; found {probe['height']}")
    if args.expect_width is not None or args.expect_height is not None:
        checks.append("dimensions")
    if args.expect_loop is not None and int(probe["loop"]) != args.expect_loop:
        raise SystemExit(f"Expected loop {args.expect_loop}; found {probe['loop']}")
    if args.expect_loop is not None:
        checks.append("loop")
    if args.expect_fps is not None:
        average_fps = float(probe["averageFps"])
        if not math.isclose(average_fps, args.expect_fps, abs_tol=0.55):
            raise SystemExit(f"Expected approximately {args.expect_fps:g} fps; measured {average_fps:g}")
        checks.append("frame-rate")
    if int(probe["paletteColorCount"]) > args.max_colors:
        raise SystemExit(f"Expected at most {args.max_colors} colors; found {probe['paletteColorCount']}")
    checks.append("palette-limit")

    palette = {parse_hex_color(value) for value in probe["palette"]}  # type: ignore[union-attr]
    manifest = load_manifest(args.manifest)
    active = manifest.get("colorset") if manifest else ("colorset1" if palette <= set(colorset_colors("colorset1")) else "colorset2")
    if active not in {"colorset1", "colorset2"} or not palette <= set(colorset_colors(active)):
        raise SystemExit("Decoded GIF paints must belong to the declared canonical colorset")
    checks.append("canonical-colorset")
    if args.expect_mode == "original":
        if not palette.issubset({BLACK, WHITE}) or palette != {BLACK, WHITE}:
            raise SystemExit(f"Original mode must contain exactly black and white; found {probe['palette']}")
        checks.append("original-palette")
    elif args.expect_mode == "custom":
        expected = {args.expect_custom_color, WHITE}
        if palette != expected:
            raise SystemExit(
                f"Custom mode must contain exactly {sorted(color_hex(color) for color in expected)}; "
                f"found {probe['palette']}"
            )
        checks.append("custom-palette")

    if manifest is not None:
        if args.expect_mode and manifest.get("mode") != args.expect_mode:
            raise SystemExit(f"Manifest mode {manifest.get('mode')!r} does not match {args.expect_mode!r}")
        if args.expect_source_kind and nested(manifest, "source", "kind") != args.expect_source_kind:
            raise SystemExit(
                f"Manifest source.kind {nested(manifest, 'source', 'kind')!r} "
                f"does not match {args.expect_source_kind!r}"
            )
        if args.expect_source_kind:
            checks.append("source-kind")
        if args.expect_source_format:
            actual_format = str(nested(manifest, "source", "format")).upper()
            if actual_format != args.expect_source_format.upper():
                raise SystemExit(
                    f"Manifest source.format {actual_format!r} does not match {args.expect_source_format.upper()!r}"
                )
            checks.append("source-format")
        checks.extend(validate_manifest(manifest, args.gif, probe))

    result = {"ok": True, "gif": str(args.gif.resolve()), "checks": checks, **probe}
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        result["report"] = str(args.json_report.resolve())
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
