#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Validate pixel-art stills and motion, including exact source-color outputs."""

from __future__ import annotations

import argparse
from colorset_contract import tokens as colorset_tokens
import hashlib
import io
import json
import math
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

from PIL import Image, ImageChops, ImageOps, UnidentifiedImageError


Color = tuple[int, int, int]


def nested(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            raise SystemExit(f"Manifest is missing {'.'.join(keys)}")
        value = value[key]
    return value


def color_hex(color: Color) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in color)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pixel_grid_matches(image: Image.Image, logical_size: tuple[int, int]) -> bool:
    rgba = image.convert("RGBA")
    reconstructed = rgba.resize(logical_size, Image.Resampling.NEAREST).resize(rgba.size, Image.Resampling.NEAREST)
    return ImageChops.difference(rgba, reconstructed).getbbox() is None


def inspect_pillow(path: Path, logical_size: tuple[int, int] | None, *, collect_palette: bool = True) -> dict[str, Any]:
    try:
        with Image.open(path) as image:
            frame_count = max(1, int(getattr(image, "n_frames", 1)))
            durations: list[int] = []
            colors: set[Color] = set()
            hashes: set[str] = set()
            pixel_grid_ok = True
            for index in range(frame_count):
                image.seek(index)
                frame = image.convert("RGBA")
                hashes.add(hashlib.sha256(frame.tobytes()).hexdigest())
                if logical_size is not None and not pixel_grid_matches(frame, logical_size):
                    pixel_grid_ok = False
                if not collect_palette:
                    pass
                elif frame.getchannel("A").getextrema() == (255, 255):
                    counted = frame.convert("RGB").getcolors(maxcolors=1 << 24)
                    if counted is None:
                        raise SystemExit("Frame exceeds the validator color-count limit")
                    colors.update(color for _, color in counted)
                else:
                    # Lossless WebP may normalize invisible RGB beneath alpha=0.
                    # Those pixels cannot change the visible palette contract.
                    pixels = getattr(frame, "get_flattened_data", frame.getdata)()
                    colors.update((red, green, blue) for red, green, blue, alpha in pixels if alpha > 0)
                if frame_count > 1:
                    duration = int(image.info.get("duration", 0) or 0)
                    if duration <= 0:
                        raise SystemExit(f"Frame {index} has no positive duration")
                    durations.append(duration)
            return {
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "frameCount": frame_count,
                "distinctFrameCount": len(hashes),
                "durationSeconds": round(sum(durations) / 1000, 6) if durations else None,
                "fps": round(frame_count * 1000 / sum(durations), 6) if durations else None,
                "loop": int(image.info.get("loop", 0) or 0) if frame_count > 1 else None,
                "palette": [color_hex(color) for color in sorted(colors)] if collect_palette else None,
                "paletteSize": len(colors) if collect_palette else None,
                "pixelGridExact": pixel_grid_ok if logical_size else None,
                "audio": False,
            }
    except (UnidentifiedImageError, OSError) as error:
        raise SystemExit(f"Cannot decode output image: {error}") from error


def inspect_video(path: Path, ffprobe: str, ffmpeg: str) -> dict[str, Any]:
    try:
        probe = subprocess.run(
            [ffprobe, "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as error:
        raise SystemExit(f"Cannot run ffprobe: {error}") from error
    if probe.returncode != 0:
        raise SystemExit(f"ffprobe failed: {probe.stderr.strip()}")
    try:
        data = json.loads(probe.stdout)
        streams = data.get("streams", [])
        video = next(stream for stream in streams if stream.get("codec_type") == "video")
    except (ValueError, StopIteration, TypeError) as error:
        raise SystemExit("Video output has no readable video stream") from error
    raw_rate = video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1"
    try:
        fps = float(Fraction(raw_rate))
    except (ValueError, ZeroDivisionError):
        fps = 0
    frame_count = int(video.get("nb_read_frames") or video.get("nb_frames") or 0)
    duration = float(data.get("format", {}).get("duration") or video.get("duration") or 0)
    try:
        decoded = subprocess.run(
            [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(path),
                "-vf", "scale=64:64:flags=area", "-pix_fmt", "rgb24",
                "-f", "rawvideo", "pipe:1",
            ],
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise SystemExit(f"Cannot run ffmpeg for motion inspection: {error}") from error
    if decoded.returncode != 0:
        details = decoded.stderr.decode("utf-8", errors="replace").strip()
        raise SystemExit(f"MP4 frame decoding failed: {details}")
    frame_bytes = 64 * 64 * 3
    if len(decoded.stdout) % frame_bytes:
        raise SystemExit("Video inspection returned an incomplete decoded frame")
    hashes = {
        hashlib.sha256(decoded.stdout[index : index + frame_bytes]).hexdigest()
        for index in range(0, len(decoded.stdout), frame_bytes)
    }
    return {
        "format": "MKV" if path.suffix.lower() == ".mkv" else "MP4",
        "codec": video.get("codec_name"),
        "pixelFormat": video.get("pix_fmt"),
        "width": int(video.get("width", 0)),
        "height": int(video.get("height", 0)),
        "frameCount": frame_count,
        "distinctFrameCount": len(hashes),
        "durationSeconds": round(duration, 6),
        "fps": round(fps, 6),
        "loop": None,
        "palette": None,
        "paletteSize": None,
        "pixelGridExact": None,
        "audio": any(stream.get("codec_type") == "audio" for stream in streams),
    }


def exact_source_path(manifest: dict[str, Any]) -> Path:
    source = Path(str(nested(manifest, "source", "path")))
    if not source.is_file():
        raise SystemExit("Original source is unavailable for exact-color validation")
    if nested(manifest, "source", "sha256") != sha256_file(source):
        raise SystemExit("Original source SHA-256 changed since conversion")
    return source


def load_exact_still_source(manifest: dict[str, Any], size: tuple[int, int], ffmpeg: str | None) -> Image.Image:
    source = exact_source_path(manifest)
    kind = nested(manifest, "source", "kind")
    if kind == "svg":
        # Re-render the same declarative SVG, then independently compare sampled pixels.
        from pixel_art import render_svg

        return render_svg(source, size, 30000)
    if kind == "raster":
        try:
            with Image.open(source) as image:
                return ImageOps.exif_transpose(image).convert("RGBA")
        except (UnidentifiedImageError, OSError) as error:
            raise SystemExit(f"Cannot decode original raster: {error}") from error
    if kind == "video":
        if not ffmpeg:
            raise SystemExit("ffmpeg is required to validate a still extracted from video")
        start = float(nested(manifest, "render", "sourceStartSeconds"))
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", f"{start:g}", "-i", str(source),
             "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"],
            capture_output=True, check=False,
        )
        if result.returncode != 0:
            raise SystemExit(f"Cannot decode original video frame: {result.stderr.decode(errors='replace')}")
        with Image.open(io.BytesIO(result.stdout)) as image:
            return image.convert("RGBA").copy()
    raise SystemExit(f"Unsupported exact-color source kind: {kind}")


def validate_exact_still(path: Path, manifest: dict[str, Any], logical_size: tuple[int, int], ffmpeg: str | None) -> None:
    size = (int(nested(manifest, "render", "width")), int(nested(manifest, "render", "height")))
    source = load_exact_still_source(manifest, size, ffmpeg)
    sampled = source.convert("RGBA").resize(logical_size, Image.Resampling.NEAREST)
    expected = sampled.resize(size, Image.Resampling.NEAREST)
    threshold = int(nested(manifest, "render", "alphaThreshold"))
    expected.putalpha(sampled.getchannel("A").point(lambda value: 255 if value >= threshold else 0).resize(size, Image.Resampling.NEAREST))
    with Image.open(path) as image:
        actual = image.convert("RGBA")
    if ImageChops.difference(actual.getchannel("A"), expected.getchannel("A")).getbbox() is not None:
        raise SystemExit("Output alpha differs from the nearest-neighbor source sample")
    rgb_difference = ImageChops.difference(actual.convert("RGB"), expected.convert("RGB"))
    visible = expected.getchannel("A")
    if Image.composite(rgb_difference, Image.new("RGB", size), visible).getbbox() is not None:
        raise SystemExit("Output contains RGB values differing from the original nearest-neighbor source pixels")


def validate_exact_motion(path: Path, manifest: dict[str, Any], logical_size: tuple[int, int], ffmpeg: str) -> None:
    source = exact_source_path(manifest)
    fps = float(nested(manifest, "motion", "fps"))
    start = float(nested(manifest, "motion", "startSeconds"))
    duration = float(nested(manifest, "motion", "sourceSelectionSeconds"))
    frame_count = int(nested(manifest, "motion", "frameCount"))
    width, height = logical_size
    output_size = (int(nested(manifest, "render", "width")), int(nested(manifest, "render", "height")))
    source_frame_bytes = width * height * 3
    output_frame_bytes = output_size[0] * output_size[1] * 3
    source_filter = f"fps={fps:g},format=rgb24,scale={width}:{height}:flags=neighbor"
    commands = (
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", f"{start:g}", "-i", str(source),
         "-t", f"{duration:g}", "-vf", source_filter, "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1"],
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(path),
         "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1"],
    )
    processes: list[subprocess.Popen[bytes]] = []
    try:
        for command in commands:
            processes.append(subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        source_process, output_process = processes
        assert source_process.stdout is not None and output_process.stdout is not None
        for index in range(frame_count):
            original = source_process.stdout.read(source_frame_bytes)
            converted = output_process.stdout.read(output_frame_bytes)
            if len(original) != source_frame_bytes or len(converted) != output_frame_bytes:
                raise SystemExit(f"Exact-color frame {index + 1} is missing or incomplete")
            expected = Image.frombytes("RGB", logical_size, original).resize(output_size, Image.Resampling.NEAREST)
            if expected.tobytes() != converted:
                raise SystemExit(f"Exact-color frame {index + 1} differs from the enlarged original RGB pixels")
        if source_process.stdout.read(1) or output_process.stdout.read(1):
            raise SystemExit("Exact-color frame counts differ from the manifest")
        for process in processes:
            if process.wait(timeout=30) != 0:
                assert process.stderr is not None
                raise SystemExit(f"Exact-color decode failed: {process.stderr.read().decode(errors='replace')}")
    except OSError as error:
        raise SystemExit(f"Cannot decode exact-color video: {error}") from error
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
            process.wait()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expect-width", type=int)
    parser.add_argument("--expect-height", type=int)
    parser.add_argument("--expect-pixel-size", type=int)
    parser.add_argument("--expect-source-kind", choices=("svg", "raster", "video"))
    parser.add_argument("--expect-palette-mode", choices=("colorset1", "colorset2", "adaptive", "forest4", "sunset8", "custom", "preserve"))
    parser.add_argument("--expect-colorset", choices=("colorset1", "colorset2"))
    parser.add_argument("--max-colors", type=int)
    parser.add_argument("--expect-fps", type=float)
    parser.add_argument("--expect-duration", type=float)
    parser.add_argument("--expect-loop", type=int)
    parser.add_argument("--expect-audio", choices=("keep", "drop"))
    parser.add_argument("--min-frames", type=int, default=2)
    parser.add_argument("--min-distinct-frames", type=int, default=2)
    parser.add_argument("--json-report", type=Path)
    parser.add_argument("--ffprobe", default=shutil.which("ffprobe"))
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    args = parser.parse_args(argv)
    if not args.output.is_file() or not args.manifest.is_file():
        parser.error("output and manifest must exist")
    if args.output.suffix.lower() not in {".png", ".webp", ".gif", ".mp4", ".mkv"}:
        parser.error("output must be PNG, WebP, GIF, MP4, or MKV")
    if args.min_frames < 2 or args.min_distinct_frames < 2:
        parser.error("minimum frame counts must be at least 2")
    if args.max_colors is not None and not 1 <= args.max_colors <= 256:
        parser.error("--max-colors must be between 1 and 256")
    if args.output.suffix.lower() in {".mp4", ".mkv"} and (not args.ffmpeg or not args.ffprobe):
        parser.error("ffmpeg and ffprobe are required for video validation")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Cannot read manifest: {error}") from error
    if not isinstance(manifest, dict) or manifest.get("schema") != "pixel-art-image-video/v1":
        raise SystemExit("Manifest schema must be pixel-art-image-video/v1")
    if Path(str(nested(manifest, "output"))).resolve() != args.output.resolve():
        raise SystemExit("Manifest output path does not match the inspected file")
    if nested(manifest, "sha256") != sha256_file(args.output):
        raise SystemExit("Output SHA-256 does not match its manifest")
    logical_size = (int(nested(manifest, "render", "logicalWidth")), int(nested(manifest, "render", "logicalHeight")))
    suffix = args.output.suffix.lower()
    mode = nested(manifest, "render", "paletteMode")
    preserve = mode == "preserve"
    probe = inspect_video(args.output, args.ffprobe, args.ffmpeg) if suffix in {".mp4", ".mkv"} else inspect_pillow(args.output, logical_size, collect_palette=not preserve)
    checks = ["format", "manifest-schema", "manifest-path", "manifest-sha256"]
    expected_format = {".png": "PNG", ".webp": "WEBP", ".gif": "GIF", ".mp4": "MP4", ".mkv": "MKV"}[suffix]
    if probe["format"] != expected_format:
        raise SystemExit(f"Expected {expected_format} output, found {probe['format']}")
    for key in ("width", "height"):
        if int(nested(manifest, "render", key)) != probe[key]:
            raise SystemExit(f"Manifest render.{key} does not match the output")
    checks.append("dimensions")
    if args.expect_width is not None and probe["width"] != args.expect_width:
        raise SystemExit(f"Expected width {args.expect_width}, found {probe['width']}")
    if args.expect_height is not None and probe["height"] != args.expect_height:
        raise SystemExit(f"Expected height {args.expect_height}, found {probe['height']}")
    if args.expect_pixel_size is not None and nested(manifest, "render", "pixelSize") != args.expect_pixel_size:
        raise SystemExit("Manifest pixel size does not match the expectation")
    if args.expect_source_kind and nested(manifest, "source", "kind") != args.expect_source_kind:
        raise SystemExit("Manifest source kind does not match the expectation")
    if args.expect_palette_mode and nested(manifest, "render", "paletteMode") != args.expect_palette_mode:
        raise SystemExit("Manifest palette mode does not match the expectation")
    checks.append("source-and-style-contract")
    if preserve:
        if suffix not in {".png", ".webp", ".mkv"}:
            raise SystemExit("Exact source-color mode requires PNG, lossless WebP, or FFV1 MKV")
        if nested(manifest, "render", "palette") is not None or nested(manifest, "render", "paletteSize") is not None:
            raise SystemExit("Exact source-color mode must not declare a reduced palette")
        if nested(manifest, "render", "sourceColorsExact") is not True:
            raise SystemExit("Manifest does not declare the exact source-color contract")
        if nested(manifest, "render", "contrast") != 1 or nested(manifest, "render", "saturation") != 1 or nested(manifest, "render", "dither") != "none":
            raise SystemExit("Exact source-color mode cannot alter color channels")
        if args.max_colors is not None:
            raise SystemExit("--max-colors does not apply to exact source-color mode")
        if suffix == ".mkv":
            if probe["codec"] != "ffv1" or probe["pixelFormat"] != "bgr0":
                raise SystemExit("Exact source-color video must use FFV1 with RGB-family bgr0 pixels")
            validate_exact_motion(args.output, manifest, logical_size, args.ffmpeg)
            checks.append("exact-pixel-grid")
        else:
            if not probe["pixelGridExact"]:
                raise SystemExit("Output is not an exact nearest-neighbor logical-pixel grid")
            validate_exact_still(args.output, manifest, logical_size, args.ffmpeg)
            checks.append("exact-pixel-grid")
        checks.append("exact-source-colors")
    else:
        palette = set(nested(manifest, "render", "palette"))
        active = nested(manifest, "render", "colorset")
        if active not in {"colorset1", "colorset2"} or not palette <= set(colorset_tokens(active)):
            raise SystemExit("Declared pixel paints do not fit a canonical colorset")
        if args.expect_colorset and active != args.expect_colorset:
            raise SystemExit("Active colorset does not match --expect-colorset")
        checks.append("canonical-colorset")
        if len(palette) != int(nested(manifest, "render", "paletteSize")):
            raise SystemExit("Manifest palette contains duplicate or mismatched colors")
        if suffix not in {".mp4", ".mkv"}:
            if not set(probe["palette"]).issubset(palette):
                raise SystemExit("Output contains colors outside the declared palette")
            if args.max_colors is not None and probe["paletteSize"] > args.max_colors:
                raise SystemExit(f"Output contains {probe['paletteSize']} colors, above {args.max_colors}")
            if not probe["pixelGridExact"]:
                raise SystemExit("Output is not an exact nearest-neighbor logical-pixel grid")
            checks.extend(["palette-bound", "exact-pixel-grid"])
        elif args.max_colors is not None and len(palette) > args.max_colors:
            raise SystemExit("Declared source palette exceeds --max-colors; video compression may add nearby tones")
    if suffix in {".gif", ".mp4", ".mkv"}:
        motion = nested(manifest, "motion")
        if not isinstance(motion, dict):
            raise SystemExit("Animated output needs motion metadata")
        if probe["frameCount"] != int(nested(manifest, "motion", "frameCount")):
            raise SystemExit("Manifest motion frame count does not match the output")
        if probe["frameCount"] < args.min_frames or probe["distinctFrameCount"] < args.min_distinct_frames:
            raise SystemExit("Animated output has too few total or visually distinct frames")
        checks.append("actual-motion")
        if args.expect_fps is not None and not math.isclose(probe["fps"], args.expect_fps, abs_tol=0.55):
            raise SystemExit(f"Expected approximately {args.expect_fps:g} fps, found {probe['fps']:g}")
        if args.expect_duration is not None and not math.isclose(probe["durationSeconds"], args.expect_duration, abs_tol=0.12):
            raise SystemExit(f"Expected approximately {args.expect_duration:g} seconds, found {probe['durationSeconds']:g}")
        if args.expect_loop is not None and probe["loop"] != args.expect_loop:
            raise SystemExit(f"Expected GIF loop {args.expect_loop}, found {probe['loop']}")
        if args.expect_audio and probe["audio"] != (args.expect_audio == "keep"):
            raise SystemExit(f"Expected audio {args.expect_audio}, found audio={probe['audio']}")
        if suffix in {".mp4", ".mkv"} and probe["audio"] != bool(motion.get("audioKept")):
            raise SystemExit("Manifest audioKept disagrees with the video streams")
        checks.extend(["timing", "audio-contract"])
    else:
        if manifest.get("motion") is not None or probe["frameCount"] != 1:
            raise SystemExit("Still output has unexpected animation metadata or frames")
        checks.append("single-still")
    result = {"ok": True, "output": str(args.output.resolve()), "checks": checks, **probe}
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
