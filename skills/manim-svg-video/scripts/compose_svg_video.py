#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "manim>=0.20.0",
#   "pyyaml>=6.0.2",
#   "playwright>=1.55,<2",
# ]
# ///

from __future__ import annotations

import argparse
import fnmatch
import json
import math
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import yaml
from palette_contract import require_color, text_on_fill
from arrow_quality import ARROW_AUDIT


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
    "import_mode": "auto",
    "render_source": "final",
    "snapshot_seconds": 0.0,
    "preserve_source_media": None,
    "background": "#ffffff",
    "title_color": "#1c1c1c",
    "tile_fill": "#f7f7f7",
    "tile_stroke": "#cfcfcf",
    "label_color": "#000000",
    "placeholder_fill": "#9e1b32",
    "placeholder_stroke": "#e8002a",
    "placeholder_text": "#ffffff",
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
    source_media_preserved: bool = False


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
    unmatched_preserved = set(args.preserve_source_media) - {asset.source.resolve() for asset in assets}
    if unmatched_preserved:
        raise SystemExit("--preserve-source-media must name a selected original asset: " +
                         ", ".join(str(path) for path in sorted(unmatched_preserved)))

    prepared_assets = []
    try:
        for index, asset in enumerate(assets, start=1):
            prepared_assets.append(prepare_asset(asset, index, args, assets_dir))
    except Exception as error:
        failure = {"status": "blocked", "reason": str(error),
                   "sources": [str(asset.render_source) for asset in assets]}
        (out_dir / "preparation-error.json").write_text(json.dumps(failure,indent=2)+"\n",encoding="utf-8")
        print(str(error), file=sys.stderr)
        return 2
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
    parser.add_argument("--import-mode", choices=("auto", "image", "svg"), default=DEFAULTS["import_mode"],
                        help="Auto preserves SVG markers with a browser image; svg requires materialized arrowheads.")
    parser.add_argument("--render-source", choices=("final", "animated"), default=DEFAULTS["render_source"])
    parser.add_argument("--snapshot-seconds", type=float, default=DEFAULTS["snapshot_seconds"],
                        help="Explicit CSS/SMIL snapshot time for --render-source animated image import.")
    parser.add_argument("--preserve-source-media", type=Path, action="append",
                        help="Exact original asset path whose existing paint/width must remain faithful; retain its quality findings. Repeat per imported asset.")
    parser.add_argument("--background", default=DEFAULTS["background"])
    parser.add_argument("--title-color", default=DEFAULTS["title_color"])
    parser.add_argument("--tile-fill", default=DEFAULTS["tile_fill"])
    parser.add_argument("--tile-stroke", default=DEFAULTS["tile_stroke"])
    parser.add_argument("--tile-border-width", type=float, default=0, help="Explicit outline width; borderless by default.")
    parser.add_argument("--label-color", default=DEFAULTS["label_color"])
    parser.add_argument("--placeholder-fill", default=DEFAULTS["placeholder_fill"])
    parser.add_argument("--placeholder-stroke", default=DEFAULTS["placeholder_stroke"])
    parser.add_argument("--placeholder-border-width", type=float, default=0, help="Explicit placeholder outline width; borderless by default.")
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
    args.preserve_source_media = [resolve_path(Path(path)).resolve() for path in (args.preserve_source_media or [])]

    if args.duration <= 0:
        raise SystemExit("--duration must be greater than 0.")
    if args.active_slots <= 0:
        raise SystemExit("--active-slots must be greater than 0.")
    if args.fps <= 0:
        raise SystemExit("--fps must be greater than 0.")
    if not math.isfinite(args.snapshot_seconds) or args.snapshot_seconds < 0:
        raise SystemExit("--snapshot-seconds must be finite and nonnegative.")
    if not re.fullmatch(r"\d+,\d+", args.resolution):
        raise SystemExit('--resolution must use Manim format "W,H".')
    if args.dry_run:
        args.render = False
    for field in ("tile_border_width", "placeholder_border_width"):
        if getattr(args, field) < 0 or not math.isfinite(getattr(args, field)):
            raise SystemExit(f"{field.replace('_', '-')} must be finite and nonnegative.")
    for field, background in (("title_color", "background"), ("label_color", "tile_fill"), ("placeholder_text", "placeholder_fill")):
        option = "--" + field.replace("_", "-")
        if option not in sys.argv and field not in config:
            setattr(args, field, text_on_fill(getattr(args, background)))
    for field in ("background", "title_color", "tile_fill", "tile_stroke", "label_color", "placeholder_fill", "placeholder_stroke", "placeholder_text"):
        setattr(args, field, require_color(getattr(args, field)))
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
    asset.source_media_preserved = asset.source.resolve() in {
        resolve_path(Path(path)).resolve() for path in (getattr(args, "preserve_source_media", None) or [])
    }
    markers = has_svg_markers(asset.render_source)
    if markers and args.render_source == "final" and has_svg_animation(asset.render_source):
        raise ValueError(f"A marker-bearing animated source needs a readable .static.svg final companion: {asset.render_source}. Create that snapshot, or explicitly use --render-source animated --snapshot-seconds <time> and inspect its arrowheads.")
    if args.import_mode == "svg" and markers:
        raise ValueError(f"Vector import would omit SVG arrow markers: {asset.render_source}. Materialize their heads as ordinary SVG paths, or use --import-mode auto/image.")
    if args.import_mode == "svg" or (args.import_mode == "auto" and not markers):
        asset.import_mode = "svg"
        asset.prepared_source = asset.render_source
        return asset

    png_path = assets_dir / f"{index:03d}-{sanitize_name(asset.label)}.png"
    try:
        rasterize_svg(asset.render_source, png_path, args.snapshot_seconds, asset.source_media_preserved,
                      getattr(args, "tile_fill", DEFAULTS["tile_fill"]))
        asset.import_mode = "image"
        asset.prepared_source = png_path.resolve()
    except Exception as error:  # noqa: BLE001 - generated SVG failures belong in the manifest.
        asset.conversion_error = f"{type(error).__name__}: {error}"
        raise RuntimeError(f"Cannot preserve SVG paint for {asset.render_source}: {asset.conversion_error}. Install the Playwright Chromium browser or an SVG rasterizer; no marker-dropping fallback was rendered.") from error
    return asset


def has_svg_markers(source: Path) -> bool:
    """Detect marker paint before SVGMobject can silently discard direction."""
    text = source.read_text(encoding="utf-8-sig")
    root = ElementTree.fromstring(text)
    return any(any(key in node.attrib and node.attrib[key] != "none" for key in
                   ("marker", "marker-start", "marker-mid", "marker-end")) for node in root.iter()) or any(
        match.group(1).strip().lower() != "none" for match in
        re.finditer(r"\bmarker(?:-(?:start|mid|end))?\s*:\s*([^;}]+)", text, re.IGNORECASE)
    )


def has_svg_animation(source: Path) -> bool:
    text = source.read_text(encoding="utf-8-sig")
    return bool(re.search(r"<(?:[\w-]+:)?(?:animate\w*|set|script)\b|@keyframes|animation(?:-name)?\s*:", text, re.IGNORECASE))


def browser_rasterize_svg(source: Path, target: Path, width: int, height: int, snapshot_seconds: float = 0,
                          preserve_source_media: bool = False, canvas: str = "#ffffff") -> None:
    """Use actual browser SVG paint, including CSS and context-stroke markers."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=True)
        except Exception:
            installed = [Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
                         Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")]
            executable = next((p for p in installed if p.is_file()), None)
            if executable is None:
                raise
            browser = pw.chromium.launch(headless=True, executable_path=str(executable))
        try:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.goto(source.resolve().as_uri(), wait_until="load")
            page.evaluate("""([width,height]) => {
                const svg=document.documentElement;
                if(svg.localName!=='svg')throw Error('Expected an SVG document');
                svg.setAttribute('width',width);svg.setAttribute('height',height);
                svg.style.width=width+'px';svg.style.height=height+'px';
                svg.style.display='block';svg.style.margin='0';
            }""", [width,height])
            page.evaluate("document.fonts.ready")
            page.evaluate(r"""seconds => {
                const svg=document.documentElement;
                svg.pauseAnimations?.();svg.setCurrentTime?.(seconds);
                for(const animation of document.getAnimations()){animation.pause();animation.currentTime=seconds*1000;}
                const arrows=[...svg.querySelectorAll('path,line,polyline,polygon,circle,ellipse,rect')].filter(e => {
                    if(e.closest('defs,marker'))return false;
                    const css=getComputedStyle(e);return ['markerStart','markerMid','markerEnd'].some(k=>css[k]&&css[k]!=='none');
                });
                const context=document.createElementNS('http://www.w3.org/1999/xhtml','canvas').getContext('2d');
                function painted(e,channel,stop=null,owner=null){
                    const css=getComputedStyle(e);let color=css[channel],opacity=+css[channel+'Opacity'];
                    if(channel==='stroke'&&+parseFloat(css.strokeWidth)<=0)return false;
                    if(color==='context-stroke')color=owner?.stroke;
                    if(color==='context-fill')color=owner?.fill;
                    if(!color||color==='none')return false;
                    for(let n=e;n&&n!==stop;n=n.parentElement){const s=getComputedStyle(n);
                        if(s.display==='none'||s.visibility!=='visible')return false;opacity*=+s.opacity;
                        for(const f of s.filter.matchAll(/opacity\((\d+(?:\.\d+)?)(%)?\)/g))opacity*=+f[1]/(f[2]?100:1);
                    }
                    if(opacity<=0)return false;
                    if(color.startsWith('url('))return true; // The quality audit handles unsupported paint.
                    context.clearRect(0,0,1,1);context.fillStyle=color;context.fillRect(0,0,1,1);
                    return context.getImageData(0,0,1,1).data[3]>0;
                }
                if(arrows.some(e=>{let alpha=1;for(let n=e;n;n=n.parentElement){const css=getComputedStyle(n);
                    if(css.display==='none'||css.visibility!=='visible')return true;alpha*=+css.opacity;}
                    return alpha===0||e.getTotalLength()===0||!painted(e,'stroke');}))throw Error('The requested SVG snapshot contains a hidden arrow; choose a readable time/static companion.');
                for(const arrow of arrows){const owner=getComputedStyle(arrow);
                    for(const key of ['markerStart','markerMid','markerEnd']){
                        const match=owner[key]?.match(/#([^"\)]+)/);if(!match)continue;
                        const marker=svg.querySelector('#'+CSS.escape(match[1]));if(!marker)continue;
                        const children=[...marker.querySelectorAll('*')].filter(e=>e instanceof SVGGeometryElement);
                        if(!children.some(e=>painted(e,'fill',marker.parentElement,owner)||painted(e,'stroke',marker.parentElement,owner)))
                            throw Error('The requested SVG snapshot contains a hidden arrowhead; choose a readable time/static companion.');
                    }
                }
            }""", snapshot_seconds)
            # CSS paints the root behind its SVG children. Composite that paint
            # over the actual tile before auditing ordinary SVG backing shapes.
            # Preserve the original PNG alpha instead of painting the tile in it.
            source_backing = page.evaluate(r"""tile => {
                const css=getComputedStyle(document.documentElement);
                if(css.backgroundImage!=='none')throw Error('Unsupported SVG root background image; inspect its actual arrow backing separately.');
                const ctx=document.createElementNS('http://www.w3.org/1999/xhtml','canvas').getContext('2d');
                ctx.fillStyle=tile;ctx.fillRect(0,0,1,1);
                ctx.fillStyle=css.backgroundColor;ctx.fillRect(0,0,1,1);
                const p=ctx.getImageData(0,0,1,1).data;
                return {cssBackground:css.backgroundColor,compositedCanvas:`rgb(${p[0]}, ${p[1]}, ${p[2]})`};
            }""", canvas)
            arrows = page.evaluate(ARROW_AUDIT, {"canvas": source_backing["compositedCanvas"]})
            arrows["deliveryBacking"] = canvas
            arrows["sourceCssBacking"] = source_backing
            # Preserve only explicitly named imported media. Existing low contrast
            # or thin source strokes remain recorded, never become authored passes.
            # Missing/covered heads, unsupported geometry and unreadable snapshots
            # still block conversion; preservation never licenses marker loss.
            preserved_kinds = {"arrow-low-contrast", "arrow-too-thin"} if preserve_source_media else set()
            blocking = [issue for issue in arrows["issues"] if issue["kind"] not in preserved_kinds]
            arrows["sourceMediaPreservation"] = {
                "explicit": preserve_source_media,
                "source": str(source.resolve()),
                "retainedSourceFindings": [issue for issue in arrows["issues"] if issue["kind"] in preserved_kinds],
                "authoredQualityPassed": not arrows["issues"],
            }
            target.with_suffix(".arrow-audit.json").write_text(json.dumps(arrows, indent=2) + "\n", encoding="utf-8")
            if blocking:
                raise ValueError("Source arrow visibility audit failed: " + json.dumps(blocking))
            page.locator("svg").first.screenshot(path=str(target.resolve()), omit_background=True)
        finally:
            browser.close()


def rasterize_svg(source: Path, target: Path, snapshot_seconds: float = 0,
                  preserve_source_media: bool = False, canvas: str = "#ffffff") -> None:
    width, height = raster_size(source)
    # Native converters differ in marker/CSS support. Use browser paint first;
    # converter fallback is limited to sources without marker semantics.
    try:
        browser_rasterize_svg(source, target, width, height, snapshot_seconds, preserve_source_media, canvas)
        return
    except Exception:
        if has_svg_markers(source):
            raise
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
            "snapshot_seconds": args.snapshot_seconds,
            "preserve_source_media": [relative_to_cwd(path) for path in args.preserve_source_media],
            "background": args.background,
            "title_color": args.title_color,
            "tile_fill": args.tile_fill,
            "tile_stroke": args.tile_stroke,
            "tile_border_width": args.tile_border_width,
            "label_color": args.label_color,
            "placeholder_fill": args.placeholder_fill,
            "placeholder_stroke": args.placeholder_stroke,
            "placeholder_border_width": args.placeholder_border_width,
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
                "source_media_preserved": asset.source_media_preserved,
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
        stroke_width=settings["tile_border_width"],
        stroke_color=settings["tile_stroke"],
        fill_color=settings["tile_fill"],
        fill_opacity=1,
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
        fill_opacity=1,
        stroke_width=settings["placeholder_border_width"],
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
