#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "manim>=0.20.0",
#   "pyyaml>=6.0.2",
# ]
# ///

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import yaml


INVOCATION_CWD = Path.cwd()
DEFAULT_EXCLUDES = (
    "**/node_modules/**",
    "**/.git/**",
    "**/__pycache__/**",
    "**/media/videos/**",
    "**/media/images/**",
    "**/media/Tex/**",
)
DEFAULTS: dict[str, Any] = {
    "discover_root": None,
    "include": None,
    "exclude": None,
    "from_list": None,
    "out": Path("projects/manim-svg-video/artifacts/videos/composition"),
    "name": "manim-svg-video",
    "title": "Animated SVG Sequence",
    "duration": 600.0,
    "layout": "replace",
    "active_slots": 4,
    "max_assets": None,
    "enter_seconds": 3.0,
    "exit_seconds": 1.2,
    "pulse_every_seconds": 12.0,
    "pulse_seconds": 1.6,
    "intro_seconds": 2.0,
    "outro_seconds": 2.0,
    "import_mode": "svg",
    "render_source": "final",
    "background": "#ffffff",
    "title_color": "#111827",
    "tile_fill": "#f8fafc",
    "tile_stroke": "#cbd5e1",
    "label_color": "#334155",
    "placeholder_fill": "#fff1f2",
    "placeholder_stroke": "#e11d48",
    "placeholder_text": "#9f1239",
    "quality": "l",
    "fps": 15.0,
    "resolution": "854,480",
    "show_labels": False,
    "exact_duration": True,
    "render": False,
    "dry_run": False,
}


@dataclass
class Asset:
    source: Path
    render_source: Path
    label: str
    import_mode: str = "svg"
    prepared_source: Path | None = None
    conversion_error: str | None = None


def main() -> int:
    args = normalize_args(parse_args())
    out_dir = args.out.resolve()
    assets_dir = out_dir / "assets"
    media_dir = out_dir / "media"
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    assets = discover_assets(args)
    if args.max_assets:
        assets = assets[: args.max_assets]
    if not assets:
        raise SystemExit("No SVG assets were discovered.")

    prepared_assets = [
        prepare_asset(asset, index, args, assets_dir)
        for index, asset in enumerate(assets, start=1)
    ]
    manifest_path = out_dir / "composition-manifest.json"
    scene_path = out_dir / "manim_svg_video_scene.py"
    manifest = build_manifest(args, prepared_assets, scene_path, media_dir)

    scene_path.write_text(generate_scene_code(manifest_path), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Discovered {len(assets)} SVG asset(s).")
    print(f"Manifest: {manifest_path}")
    print(f"Manim scene: {scene_path}")

    if not args.render:
        print("Dry run complete; pass --render to create an MP4.")
        return 0

    output_file = sanitize_name(args.name)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        str(scene_path),
        "SvgVideoScene",
        "--media_dir",
        str(media_dir),
        "--format",
        "mp4",
        "--output_file",
        output_file,
        "--quality",
        args.quality,
        "--fps",
        str(args.fps),
        "--resolution",
        args.resolution,
        "--disable_caching",
    ]
    print("Running:", " ".join(command))
    subprocess.run(command, check=True)

    rendered = find_rendered_video(media_dir, output_file)
    if rendered:
        if args.exact_duration:
            exact_rendered = enforce_exact_duration(rendered, args.duration, args.fps)
            if exact_rendered != rendered:
                manifest["rendered_video_raw"] = relative_to_cwd(rendered)
                rendered = exact_rendered
        manifest["rendered_video"] = relative_to_cwd(rendered)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Rendered video: {rendered}")
    else:
        print("Render finished, but the MP4 path could not be detected automatically.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose many SVG assets into one Manim video.")
    parser.add_argument("--config", type=Path, help="Optional YAML or JSON config file.")
    parser.add_argument("--discover-root", action="append", type=Path, help="Directory to search for SVGs.")
    parser.add_argument("--include", action="append", help="Glob pattern relative to each discover root.")
    parser.add_argument("--exclude", action="append", help="Glob pattern to exclude.")
    parser.add_argument("--from-list", type=Path, help="Text file containing one SVG path per line.")
    parser.add_argument("--out", type=Path, default=DEFAULTS["out"])
    parser.add_argument("--name", default=DEFAULTS["name"])
    parser.add_argument("--title", default=DEFAULTS["title"])
    parser.add_argument("--duration", type=float, default=DEFAULTS["duration"])
    parser.add_argument("--layout", choices=("replace", "mosaic"), default=DEFAULTS["layout"])
    parser.add_argument("--active-slots", type=int, default=DEFAULTS["active_slots"])
    parser.add_argument("--max-assets", type=int)
    parser.add_argument("--enter-seconds", type=float, default=DEFAULTS["enter_seconds"])
    parser.add_argument("--exit-seconds", type=float, default=DEFAULTS["exit_seconds"])
    parser.add_argument("--pulse-every-seconds", type=float, default=DEFAULTS["pulse_every_seconds"])
    parser.add_argument("--pulse-seconds", type=float, default=DEFAULTS["pulse_seconds"])
    parser.add_argument("--intro-seconds", type=float, default=DEFAULTS["intro_seconds"])
    parser.add_argument("--outro-seconds", type=float, default=DEFAULTS["outro_seconds"])
    parser.add_argument("--import-mode", choices=("image", "svg"), default=DEFAULTS["import_mode"])
    parser.add_argument("--render-source", choices=("final", "animated"), default=DEFAULTS["render_source"])
    parser.add_argument("--background", default=DEFAULTS["background"])
    parser.add_argument("--title-color", default=DEFAULTS["title_color"])
    parser.add_argument("--tile-fill", default=DEFAULTS["tile_fill"])
    parser.add_argument("--tile-stroke", default=DEFAULTS["tile_stroke"])
    parser.add_argument("--label-color", default=DEFAULTS["label_color"])
    parser.add_argument("--placeholder-fill", default=DEFAULTS["placeholder_fill"])
    parser.add_argument("--placeholder-stroke", default=DEFAULTS["placeholder_stroke"])
    parser.add_argument("--placeholder-text", default=DEFAULTS["placeholder_text"])
    parser.add_argument("--quality", choices=("l", "m", "h", "p", "k"), default=DEFAULTS["quality"])
    parser.add_argument("--fps", type=float, default=DEFAULTS["fps"])
    parser.add_argument("--resolution", default=DEFAULTS["resolution"])
    parser.add_argument("--show-labels", action="store_true")
    parser.add_argument("--no-exact-duration", dest="exact_duration", action="store_false")
    parser.add_argument("--render", action="store_true", help="Render the generated Manim scene to MP4.")
    parser.add_argument("--dry-run", action="store_true", help="Generate manifest and scene without rendering.")
    parser.set_defaults(exact_duration=DEFAULTS["exact_duration"])
    return parser.parse_args()


def normalize_args(args: argparse.Namespace) -> argparse.Namespace:
    config = load_config(args.config)
    for key, value in config.items():
        attr = key.replace("-", "_")
        if hasattr(args, attr) and getattr(args, attr) == DEFAULTS.get(attr):
            setattr(args, attr, value)

    args.out = Path(args.out)
    args.from_list = Path(args.from_list) if args.from_list else None
    args.discover_root = [Path(root) for root in (args.discover_root or [Path(".")])]
    args.include = list(args.include or ["**/*.animated.svg"])
    args.exclude = [*DEFAULT_EXCLUDES, *(args.exclude or [])]

    if args.duration <= 0:
        raise SystemExit("--duration must be greater than 0.")
    if args.active_slots <= 0:
        raise SystemExit("--active-slots must be greater than 0.")
    if args.fps <= 0:
        raise SystemExit("--fps must be greater than 0.")
    if not re.fullmatch(r"\d+,\d+", args.resolution):
        raise SystemExit('--resolution must use Manim format "W,H".')
    if args.dry_run:
        args.render = False
    return args


def load_config(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    content = path.read_text(encoding="utf-8")
    parsed = json.loads(content) if path.suffix.lower() == ".json" else yaml.safe_load(content)
    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise SystemExit("Config file must contain a mapping.")
    return parsed


def discover_assets(args: argparse.Namespace) -> list[Asset]:
    if args.from_list:
        paths = []
        for line in args.from_list.read_text(encoding="utf-8").splitlines():
            cleaned = line.strip()
            if cleaned and not cleaned.startswith("#"):
                paths.append(resolve_path(cleaned))
    else:
        paths = []
        for root in args.discover_root:
            resolved_root = resolve_path(root)
            for pattern in args.include:
                paths.extend(path for path in resolved_root.glob(pattern) if path.is_file())

    seen: set[Path] = set()
    assets: list[Asset] = []
    for path in sorted(paths, key=lambda item: relative_to_cwd(item)):
        resolved = path.resolve()
        if resolved in seen or should_exclude(resolved, args.exclude):
            continue
        seen.add(resolved)
        render_source = resolve_render_source(resolved, args.render_source)
        assets.append(Asset(source=resolved, render_source=render_source, label=label_for(resolved)))
    return assets


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (INVOCATION_CWD / path)


def should_exclude(path: Path, patterns: list[str]) -> bool:
    posix = relative_to_cwd(path)
    return any(fnmatch.fnmatch(posix, pattern.replace("\\", "/")) for pattern in patterns)


def resolve_render_source(path: Path, mode: str) -> Path:
    if mode == "animated" or not path.name.endswith(".animated.svg"):
        return path

    base = path.name[: -len(".animated.svg")]
    candidates = [path.with_name(f"{base}.static.svg")]
    if path.parent.name == "animated":
        candidates.append(path.parent.parent / "static" / f"{base}.static.svg")

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return path


def label_for(path: Path) -> str:
    name = path.name
    for suffix in (".animated.svg", ".static.svg", ".svg"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name.replace("-", " ").replace("_", " ").strip() or path.stem


def prepare_asset(asset: Asset, index: int, args: argparse.Namespace, assets_dir: Path) -> Asset:
    if args.import_mode == "svg":
        asset.import_mode = "svg"
        asset.prepared_source = asset.render_source
        return asset

    png_path = assets_dir / f"{index:03d}-{sanitize_name(asset.label)}.png"
    try:
        rasterize_svg(asset.render_source, png_path)
        asset.import_mode = "image"
        asset.prepared_source = png_path.resolve()
    except Exception as error:  # noqa: BLE001 - generated SVG failures belong in the manifest.
        asset.conversion_error = f"{type(error).__name__}: {error}; falling back to svg import"
        asset.import_mode = "svg"
        asset.prepared_source = asset.render_source
    return asset


def rasterize_svg(source: Path, target: Path) -> None:
    width, height = raster_size(source)
    if shutil.which("magick"):
        subprocess.run(
            ["magick", str(source), "-resize", f"{width}x{height}", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
        return
    if shutil.which("rsvg-convert"):
        subprocess.run(
            ["rsvg-convert", "-w", str(width), "-h", str(height), "-o", str(target), str(source)],
            check=True,
            capture_output=True,
            text=True,
        )
        return
    if shutil.which("inkscape"):
        subprocess.run(
            [
                "inkscape",
                str(source),
                "--export-type=png",
                f"--export-filename={target}",
                f"--export-width={width}",
                f"--export-height={height}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return
    raise RuntimeError("no SVG rasterizer found on PATH: expected magick, rsvg-convert, or inkscape")


def raster_size(path: Path) -> tuple[int, int]:
    width = 1200
    aspect = svg_aspect_ratio(path) or (16 / 9)
    height = max(360, int(width / aspect))
    if height > 1600:
        height = 1600
        width = int(height * aspect)
    return width, height


def svg_aspect_ratio(path: Path) -> float | None:
    try:
        root = ElementTree.parse(path).getroot()
    except ElementTree.ParseError:
        return None

    view_box = root.get("viewBox") or root.get("viewbox")
    if view_box:
        values = [float(value) for value in re.split(r"[\s,]+", view_box.strip()) if value]
        if len(values) == 4 and values[2] > 0 and values[3] > 0:
            return values[2] / values[3]

    width = parse_svg_length(root.get("width"))
    height = parse_svg_length(root.get("height"))
    if width and height:
        return width / height
    return None


def parse_svg_length(value: str | None) -> float | None:
    if not value:
        return None
    match = re.match(r"([0-9.]+)", value)
    return float(match.group(1)) if match else None


def build_manifest(
    args: argparse.Namespace,
    assets: list[Asset],
    scene_path: Path,
    media_dir: Path,
) -> dict[str, Any]:
    width, height = (int(part) for part in args.resolution.split(","))
    return {
        "asset_count": len(assets),
        "scene": relative_to_cwd(scene_path),
        "media_dir": relative_to_cwd(media_dir),
        "settings": {
            "name": args.name,
            "title": args.title,
            "duration": args.duration,
            "layout": args.layout,
            "active_slots": args.active_slots,
            "enter_seconds": args.enter_seconds,
            "exit_seconds": args.exit_seconds,
            "pulse_every_seconds": args.pulse_every_seconds,
            "pulse_seconds": args.pulse_seconds,
            "intro_seconds": args.intro_seconds,
            "outro_seconds": args.outro_seconds,
            "import_mode": args.import_mode,
            "render_source": args.render_source,
            "background": args.background,
            "title_color": args.title_color,
            "tile_fill": args.tile_fill,
            "tile_stroke": args.tile_stroke,
            "label_color": args.label_color,
            "placeholder_fill": args.placeholder_fill,
            "placeholder_stroke": args.placeholder_stroke,
            "placeholder_text": args.placeholder_text,
            "quality": args.quality,
            "fps": args.fps,
            "resolution": args.resolution,
            "frame_width": 16.0,
            "frame_height": 16.0 * height / width,
            "show_labels": args.show_labels,
            "exact_duration": args.exact_duration,
        },
        "assets": [
            {
                "index": index,
                "source": relative_to_cwd(asset.source),
                "render_source": relative_to_cwd(asset.render_source),
                "prepared_source": relative_to_cwd(asset.prepared_source) if asset.prepared_source else None,
                "label": asset.label,
                "import_mode": asset.import_mode,
                "conversion_error": asset.conversion_error,
            }
            for index, asset in enumerate(assets, start=1)
        ],
    }


def generate_scene_code(manifest_path: Path) -> str:
    manifest_literal = json.dumps(str(manifest_path.resolve()))
    return f'''from __future__ import annotations

import json
import math
from pathlib import Path

from manim import *


MANIFEST_PATH = Path({manifest_literal})


class SvgVideoScene(Scene):
    def construct(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        settings = manifest["settings"]
        assets = manifest["assets"]
        self.camera.background_color = settings["background"]

        frame_width = float(config.frame_width)
        frame_height = float(config.frame_height)
        left = -frame_width / 2
        top = frame_height / 2
        margin_x = 0.28
        margin_y = 0.28
        header_h = 0.44 if settings.get("title") else 0.1
        grid_top = top - header_h - margin_y
        grid_bottom = -frame_height / 2 + margin_y
        grid_h = max(1.0, grid_top - grid_bottom)
        grid_w = frame_width - margin_x * 2

        elapsed = 0.0
        if settings.get("title"):
            title = Text(settings["title"], font_size=24, color=settings["title_color"])
            title.scale_to_fit_width(min(frame_width - 1.0, max(4.0, title.width)))
            title.move_to([0, top - 0.28, 0])
            self.add(title)

        intro = float(settings["intro_seconds"])
        if intro > 0:
            self.wait(intro)
            elapsed += intro

        if settings.get("layout") == "mosaic":
            elapsed += render_mosaic_layout(
                self, assets, left, grid_top, grid_w, grid_h, frame_width, frame_height, elapsed, settings
            )
        else:
            elapsed += render_replace_layout(
                self, assets, left, grid_top, grid_w, grid_h, elapsed, settings
            )

        remaining = max(0.0, float(settings["duration"]) - elapsed)
        if remaining > 0:
            self.wait(remaining)


def render_mosaic_layout(scene, assets, left, grid_top, grid_w, grid_h, frame_width, frame_height, elapsed, settings):
    columns = max(1, math.ceil(math.sqrt(max(1, len(assets)) * frame_width / max(frame_height, 0.1))))
    rows = max(1, math.ceil(len(assets) / columns))
    cell_w = grid_w / columns
    cell_h = grid_h / rows
    tile_w = cell_w * 0.9
    tile_h = cell_h * 0.78
    wave_size = max(1, int(settings["active_slots"]))
    wave_count = max(1, math.ceil(len(assets) / wave_size))
    reserved_outro = max(0.0, float(settings["outro_seconds"]))
    available = max(0.1, float(settings["duration"]) - elapsed - reserved_outro)
    wave_seconds = available / wave_count
    local_elapsed = 0.0

    for wave_index in range(wave_count):
        wave_assets = assets[wave_index * wave_size : (wave_index + 1) * wave_size]
        wave_tiles = [
            make_mosaic_tile(asset, left, grid_top, cell_w, cell_h, tile_w, tile_h, columns, settings)
            for asset in wave_assets
        ]

        enter_seconds = min(float(settings["enter_seconds"]), wave_seconds * 0.45)
        if wave_tiles and enter_seconds > 0:
            scene.play(
                AnimationGroup(
                    *[FadeIn(tile, shift=UP * min(0.12, cell_h * 0.2)) for tile in wave_tiles],
                    lag_ratio=0.08,
                ),
                run_time=enter_seconds,
            )
            local_elapsed += enter_seconds
        else:
            scene.add(*wave_tiles)

        dwell = max(0.0, wave_seconds - enter_seconds)
        local_elapsed += play_pulses(scene, wave_tiles, dwell, settings)

    return local_elapsed


def render_replace_layout(scene, assets, left, grid_top, grid_w, grid_h, elapsed, settings):
    slot_count = max(1, int(settings["active_slots"]))
    columns = 1 if slot_count == 1 else 2
    rows = max(1, math.ceil(slot_count / columns))
    cell_w = grid_w / columns
    cell_h = grid_h / rows
    tile_w = cell_w * 0.93
    tile_h = cell_h * 0.82
    wave_count = max(1, math.ceil(len(assets) / slot_count))
    reserved_outro = max(0.0, float(settings["outro_seconds"]))
    available = max(0.1, float(settings["duration"]) - elapsed - reserved_outro)
    wave_seconds = available / wave_count
    local_elapsed = 0.0

    for wave_index in range(wave_count):
        wave_assets = assets[wave_index * slot_count : (wave_index + 1) * slot_count]
        wave_tiles = [
            make_slot_tile(asset, slot_index, left, grid_top, cell_w, cell_h, tile_w, tile_h, columns, settings)
            for slot_index, asset in enumerate(wave_assets)
        ]
        is_last_wave = wave_index == wave_count - 1
        enter_seconds = min(float(settings["enter_seconds"]), wave_seconds * 0.28)
        exit_seconds = 0.0 if is_last_wave else min(float(settings["exit_seconds"]), wave_seconds * 0.2)

        if wave_tiles and enter_seconds > 0:
            scene.play(
                AnimationGroup(
                    *[FadeIn(tile, shift=UP * min(0.16, cell_h * 0.16)) for tile in wave_tiles],
                    lag_ratio=0.08,
                ),
                run_time=enter_seconds,
            )
            local_elapsed += enter_seconds
        else:
            scene.add(*wave_tiles)

        dwell = max(0.0, wave_seconds - enter_seconds - exit_seconds)
        local_elapsed += play_pulses(scene, wave_tiles, dwell, settings)

        if exit_seconds > 0 and wave_tiles:
            scene.play(
                AnimationGroup(*[FadeOut(tile, shift=DOWN * min(0.16, cell_h * 0.16)) for tile in wave_tiles], lag_ratio=0.06),
                run_time=exit_seconds,
            )
            local_elapsed += exit_seconds

    return local_elapsed


def make_slot_tile(asset, slot_index, left, grid_top, cell_w, cell_h, tile_w, tile_h, columns, settings):
    row = slot_index // columns
    column = slot_index % columns
    center_x = left + 0.28 + cell_w * (column + 0.5)
    center_y = grid_top - cell_h * (row + 0.5)
    return make_tile_at(asset, center_x, center_y, cell_w, cell_h, tile_w, tile_h, settings)


def make_mosaic_tile(asset, left, grid_top, cell_w, cell_h, tile_w, tile_h, columns, settings):
    index = int(asset["index"]) - 1
    row = index // columns
    column = index % columns
    center_x = left + 0.28 + cell_w * (column + 0.5)
    center_y = grid_top - cell_h * (row + 0.5)
    return make_tile_at(asset, center_x, center_y, cell_w, cell_h, tile_w, tile_h, settings)


def make_tile_at(asset, center_x, center_y, cell_w, cell_h, tile_w, tile_h, settings):
    frame = RoundedRectangle(
        corner_radius=0.035,
        width=cell_w * 0.93,
        height=cell_h * 0.9,
        stroke_width=0.45,
        stroke_color=settings["tile_stroke"],
        fill_color=settings["tile_fill"],
        fill_opacity=0.82,
    )
    frame.move_to([center_x, center_y, -0.02])

    visual = load_visual(asset, settings)
    fit_to_box(visual, tile_w, tile_h if not settings.get("show_labels") else tile_h * 0.72)
    visual.move_to([center_x, center_y + (cell_h * 0.06 if settings.get("show_labels") else 0), 0])

    parts = [frame, visual]
    if settings.get("show_labels"):
        label = Text(asset["label"][:42], font_size=8, color=settings["label_color"])
        if label.width > cell_w * 0.82:
            label.scale_to_fit_width(cell_w * 0.82)
        label.next_to(frame.get_bottom(), UP, buff=cell_h * 0.08)
        parts.append(label)

    tile = Group(*parts)
    tile.set_opacity(0)
    tile.move_to([center_x, center_y, 0])
    return tile


def load_visual(asset, settings):
    source = asset.get("prepared_source")
    if not source:
        return placeholder(asset, "conversion failed", settings)

    try:
        mode = asset.get("import_mode", settings["import_mode"])
        mob = SVGMobject(source) if mode == "svg" else ImageMobject(source)
        if mob.width <= 0 or mob.height <= 0:
            return placeholder(asset, "blank import", settings)
        return mob
    except Exception as error:
        return placeholder(asset, type(error).__name__, settings)


def placeholder(asset, reason, settings):
    box = Rectangle(
        width=1.4,
        height=0.8,
        stroke_color=settings["placeholder_stroke"],
        fill_color=settings["placeholder_fill"],
        fill_opacity=0.8,
    )
    label = Text(f"SVG {{asset['index']}}", font_size=16, color=settings["placeholder_text"])
    note = Text(str(reason)[:24], font_size=8, color=settings["placeholder_text"])
    note.next_to(label, DOWN, buff=0.08)
    return Group(box, label, note)


def fit_to_box(mob, width, height):
    if mob.width > width:
        mob.scale_to_fit_width(width)
    if mob.height > height:
        mob.scale_to_fit_height(height)


def play_pulses(scene, wave_tiles, dwell, settings):
    if dwell <= 0:
        return 0.0
    pulse_every = max(0.1, float(settings["pulse_every_seconds"]))
    pulse_seconds = max(0.0, min(float(settings["pulse_seconds"]), pulse_every))
    elapsed = 0.0

    if not wave_tiles or pulse_seconds <= 0:
        scene.wait(dwell)
        return dwell

    while elapsed + 0.001 < dwell:
        wait_time = min(max(0.0, pulse_every - pulse_seconds), dwell - elapsed)
        if wait_time > 0:
            scene.wait(wait_time)
            elapsed += wait_time
        if elapsed + 0.001 >= dwell:
            break
        run_time = min(pulse_seconds, dwell - elapsed)
        scene.play(
            AnimationGroup(
                *[tile.animate(rate_func=there_and_back).scale(1.035) for tile in wave_tiles],
                lag_ratio=0.02,
            ),
            run_time=run_time,
        )
        elapsed += run_time
    return elapsed
'''


def find_rendered_video(media_dir: Path, output_file: str) -> Path | None:
    candidates = sorted(media_dir.rglob(f"{output_file}.mp4"), key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def enforce_exact_duration(path: Path, target_duration: float, fps: float) -> Path:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("ffmpeg or ffprobe not found; skipping exact-duration post-processing.")
        return path

    current = probe_duration(path)
    frame_interval = 1.0 / fps
    if current is None or abs(current - target_duration) <= frame_interval / 2:
        return path

    fixed = path.with_name(f"{path.stem}-exact-{int(round(target_duration))}s{path.suffix}")
    pad_seconds = max(0.0, target_duration - current + frame_interval)
    video_filter = (
        f"tpad=stop_mode=clone:stop_duration={pad_seconds:.6f},"
        f"trim=duration={target_duration:.6f},setpts=PTS-STARTPTS,fps={fps}"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-vf",
            video_filter,
            "-an",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(fixed),
        ],
        check=True,
    )
    return fixed


def probe_duration(path: Path) -> float | None:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
        return float(json.loads(result.stdout)["format"]["duration"])
    except Exception as error:  # noqa: BLE001 - duration repair should not hide a successful Manim render.
        print(f"Could not probe rendered video duration: {error}")
        return None


def sanitize_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-._")
    return cleaned or "manim-svg-video"


def relative_to_cwd(path: Path | None) -> str:
    if path is None:
        return ""
    resolved = path.resolve()
    try:
        return resolved.relative_to(INVOCATION_CWD).as_posix()
    except ValueError:
        return resolved.as_posix()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from error
