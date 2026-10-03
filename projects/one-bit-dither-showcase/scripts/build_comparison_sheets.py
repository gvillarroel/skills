#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
# ]
# ///

"""Build labeled source-versus-mode comparison sheets for the showcase."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT = Path(__file__).resolve().parents[1]
ARTIFACTS = PROJECT / "artifacts"
PANEL_SIZE = (640, 360)
MARGIN = 28
GAP = 24
TITLE_HEIGHT = 82
LABEL_HEIGHT = 54
CANVAS_SIZE = (
    MARGIN * 2 + PANEL_SIZE[0] * 2 + GAP,
    TITLE_HEIGHT + LABEL_HEIGHT * 2 + PANEL_SIZE[1] * 2 + GAP + MARGIN,
)

CASES = (
    {
        "stem": "watch-load-bars",
        "title": "Watch Load — bar chart",
        "profile": "detailed",
        "settings": "1280×720 render · 2 px cells · Bayer 4×4",
        "custom": "#234E70",
    },
    {
        "stem": "night-watch-lollipop",
        "title": "Night Watch — fine lines and labels",
        "profile": "detailed",
        "settings": "1280×720 render · 2 px cells · Bayer 4×4",
        "custom": "#0B6E4F",
    },
    {
        "stem": "signal-compass",
        "title": "Signal Compass — multicolor emblem",
        "profile": "detailed",
        "settings": "1280×720 render · 2 px cells · Bayer 4×4",
        "custom": "#5B2A86",
    },
    {
        "stem": "signal-compass-png",
        "title": "Signal Compass — PNG raster input",
        "profile": "detailed",
        "settings": "1280×721 render · 2 px cells · Bayer 4×4",
        "custom": "#5B2A86",
        "source_image": "source-signal-compass.png",
        "source_label": "SOURCE · PNG INPUT",
    },
)


def font(size: int, *, semibold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/seguisb.ttf" if semibold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if semibold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


TITLE_FONT = font(28, semibold=True)
SUBTITLE_FONT = font(16)
LABEL_FONT = font(17, semibold=True)


def flatten_white(path: Path, *, resample: Image.Resampling) -> Image.Image:
    with Image.open(path) as opened:
        rgba = opened.convert("RGBA")
    background = Image.new("RGBA", rgba.size, "#ffffff")
    background.alpha_composite(rgba)
    return background.convert("RGB").resize(PANEL_SIZE, resample=resample)


def draw_panel(
    canvas: Image.Image,
    *,
    image_path: Path,
    label: str,
    x: int,
    y: int,
    stylized: bool,
) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (x, y, x + PANEL_SIZE[0], y + LABEL_HEIGHT + PANEL_SIZE[1]),
        radius=12,
        fill="#ffffff",
        outline="#3a414d",
        width=2,
    )
    draw.rounded_rectangle(
        (x, y, x + PANEL_SIZE[0], y + LABEL_HEIGHT + 10),
        radius=12,
        fill="#202631",
    )
    draw.rectangle((x, y + LABEL_HEIGHT - 10, x + PANEL_SIZE[0], y + LABEL_HEIGHT), fill="#202631")
    draw.text((x + 18, y + 15), label, fill="#f7f7f2", font=LABEL_FONT)
    panel = flatten_white(
        image_path,
        resample=Image.Resampling.NEAREST if stylized else Image.Resampling.LANCZOS,
    )
    canvas.paste(panel, (x, y + LABEL_HEIGHT))


def build_case(case: dict[str, str]) -> dict[str, object]:
    stem = case["stem"]
    canvas = Image.new("RGB", CANVAS_SIZE, "#12151b")
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, 18), case["title"], fill="#ffffff", font=TITLE_FONT)
    subtitle = f"QUALITY {case['profile'].upper()} · {case['settings']}"
    draw.text((MARGIN, 52), subtitle, fill="#aeb7c5", font=SUBTITLE_FONT)

    entries = (
        (
            ARTIFACTS / "screenshots" / case.get("source_image", f"source-{stem}.png"),
            case.get("source_label", "SOURCE · D3 OUTPUT"),
            False,
        ),
        (ARTIFACTS / "previews" / f"{stem}-original.png", "1 · ORIGINAL · BLACK + WHITE", True),
        (ARTIFACTS / "previews" / f"{stem}-custom.png", f"2 · CUSTOM · {case['custom']} + WHITE", True),
        (ARTIFACTS / "previews" / f"{stem}-regional.png", "3 · REGIONAL · SOURCE COLORS + B/W", True),
    )
    for index, (path, label, stylized) in enumerate(entries):
        if not path.is_file():
            raise SystemExit(f"Missing comparison input: {path}")
        column = index % 2
        row = index // 2
        x = MARGIN + column * (PANEL_SIZE[0] + GAP)
        y = TITLE_HEIGHT + row * (LABEL_HEIGHT + PANEL_SIZE[1] + GAP)
        draw_panel(canvas, image_path=path, label=label, x=x, y=y, stylized=stylized)

    output = ARTIFACTS / "showcase" / f"{stem}-comparison.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True)
    return {
        "source": stem,
        "profile": case["profile"],
        "settings": case["settings"],
        "customColor": case["custom"],
        "output": str(output.resolve()),
        "width": canvas.width,
        "height": canvas.height,
    }


def main() -> int:
    reports = [build_case(case) for case in CASES]
    report_path = ARTIFACTS / "showcase" / "comparison-sheets.json"
    report_path.write_text(json.dumps({"ok": True, "sheets": reports}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "report": str(report_path.resolve()), "sheets": reports}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
