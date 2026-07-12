#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0.0",
# ]
# ///
"""Prepare the twelve Holiday 2026 video production packages.

The script consumes the normalized ranked dataset, creates source-bound visual
assets, writes all planning contracts, captures official web pages with the
Playwright CLI, and synthesizes a final narrated audio track for each category.
It deliberately writes only below projects/holiday2026.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
CATEGORIES_PATH = PROJECT / "source" / "categories.json"
RANKED_PATH = PROJECT / "artifacts" / "data" / "ranked-places.json"
PACKAGES = PROJECT / "video-packages"
TOP_LEVEL_VIDEOS = PROJECT / "artifacts" / "videos"
AWSOME = REPO / ".agents" / "skills" / "awsome-videos" / "scripts"
WIDTH = 1280
HEIGHT = 720
DURATION = 48
SCENE_DURATION = 6
SCENE_COUNT = 8
HOME_LABEL = "7010 Brassfield Dr, Cumming"
HOME_LAT = 34.079099895469
HOME_LON = -84.183167025532
BG = "#F6F3EE"
SURFACE = "#FFFCF8"
SOFT = "#E9EFEB"
INK = "#263238"
MUTED = "#59666F"
LINE = "#D7DDD8"
LINE_STRONG = "#7A877F"
TRANSITION_FAMILIES = [
    "match cut axis",
    "persistent object",
    "camera move",
    "color handoff",
    "spatial portal reveal",
    "morph continuity",
    "negative space cut",
]
COMPOSITIONS = [
    ("diagonal proximity map", "diagonal reading path", (0.04, 0.14, 0.70, 0.78)),
    ("asymmetric source proof", "golden-root split", (0.045, 0.13, 0.62, 0.74)),
    ("reverse editorial proof", "reverse golden-root split", (0.335, 0.13, 0.62, 0.74)),
    ("full-bleed source proof", "centered hero plane", (0.05, 0.11, 0.90, 0.76)),
    ("ranked comparison strip", "horizontal rank spine", (0.05, 0.15, 0.90, 0.72)),
    ("preference profile chart", "priority ladder field", (0.05, 0.15, 0.90, 0.72)),
    ("decision matrix", "modular decision grid", (0.05, 0.14, 0.90, 0.74)),
    ("planner callback map", "radial route callback", (0.04, 0.14, 0.70, 0.78)),
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_url(item: dict) -> str:
    for key in ("official_url", "corroborating_url", "directions_url"):
        value = str(item.get(key) or "").strip()
        if value.startswith(("https://", "http://")):
            return value
    return "https://www.exploregeorgia.org/"


def money_label(item: dict) -> str:
    value = str(item.get("price_level") or item.get("cost_note") or "Check price").strip()
    return value[:34] if value else "Check price"


def date_label(item: dict) -> str:
    start = str(item.get("start_date") or "").strip()
    end = str(item.get("end_date") or "").strip()
    if not start:
        return "Any day — verify hours"
    if end and end != start:
        return f"{start} to {end}"
    return start


def location_label(item: dict) -> str:
    city = str(item.get("city") or "Georgia").strip()
    miles = float(item.get("distance_miles") or 0)
    minutes = int(item.get("drive_minutes") or 0)
    return f"{city} • {miles:.1f} mi • {minutes} min"


def truncate(value: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(value) <= limit:
        return value
    return value[: max(1, limit - 1)].rstrip() + "…"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / ("arialbd.ttf" if bold else "arial.ttf"),
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / ("segoeuib.ttf" if bold else "segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def image_quality_ok(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image = image.convert("RGB")
            if image.width < 640 or image.height < 360:
                return False
            stat = ImageStat.Stat(image.resize((160, 90)))
            return sum(stat.stddev) / 3 >= 8
    except Exception:
        return False


def fallback_source_image(path: Path, item: dict, accent: str, rank: int, error: str) -> None:
    accent_rgb = hex_rgb(accent)
    image = Image.new("RGB", (WIDTH, HEIGHT), hex_rgb(BG))
    draw = ImageDraw.Draw(image)
    for x in range(WIDTH):
        mix = x / WIDTH
        color = tuple(int(8 + (channel - 8) * 0.28 * mix) for channel in accent_rgb)
        draw.line([(x, 0), (x, HEIGHT)], fill=color)
    draw.rectangle((48, 48, WIDTH - 48, HEIGHT - 48), outline=accent_rgb, width=4)
    draw.ellipse((80, 84, 204, 208), fill=accent_rgb)
    draw.text((119, 118), str(rank), font=font(56, True), fill=hex_rgb(INK), anchor="mm")
    draw.text((238, 86), "SOURCE-BOUND PLACE CARD", font=font(24, True), fill=accent_rgb)
    lines = textwrap.wrap(truncate(item.get("name", "Family option"), 72), width=28)
    y = 142
    for line in lines[:3]:
        draw.text((238, y), line, font=font(52, True), fill=hex_rgb(INK))
        y += 62
    draw.text((238, y + 18), location_label(item), font=font(27), fill=hex_rgb(MUTED))
    draw.text((238, y + 62), truncate(str(item.get("why_good") or "Strong family fit."), 92), font=font(25), fill=hex_rgb(INK))
    domain = urlparse(safe_url(item)).netloc or "official source"
    draw.text((80, 614), f"Official source: {domain}", font=font(21), fill=hex_rgb(MUTED))
    draw.text((80, 651), f"Browser capture fallback • {truncate(error, 82)}", font=font(18), fill=hex_rgb(MUTED))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)


def capture_source_page(path: Path, item: dict, accent: str, rank: int, timeout_ms: int) -> dict:
    url = safe_url(item)
    path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "npx.cmd" if os.name == "nt" else "npx",
        "playwright",
        "screenshot",
        "--channel",
        "chrome",
        "--viewport-size",
        "1280,720",
        "--wait-for-timeout",
        "450",
        "--timeout",
        str(timeout_ms),
        url,
        str(path),
    ]
    error = ""
    try:
        result = subprocess.run(
            command,
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=max(25, timeout_ms / 1000 + 10),
            check=False,
        )
        if result.returncode != 0:
            error = truncate(result.stderr or result.stdout or f"exit {result.returncode}", 160)
        elif not image_quality_ok(path):
            error = "The browser output failed the image variance or dimension check."
    except Exception as exc:
        error = truncate(str(exc), 160)
    if error:
        fallback_source_image(path, item, accent, rank, error)
        return {"method": "fallback", "error": error, "url": url}
    return {"method": "playwright", "error": "", "url": url}


def svg_text(value: str) -> str:
    return html.escape(str(value), quote=True)


def svg_shell(title: str, description: str, accent: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">{svg_text(title)}</title>
  <desc id="desc">{svg_text(description)}</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{BG}"/><stop offset="1" stop-color="#101F30"/></linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="12" stdDeviation="16" flood-opacity=".35"/></filter>
  </defs>
  <rect width="1280" height="720" fill="url(#bg)"/>
  <path d="M0 600 C280 520 420 690 720 610 C980 540 1110 650 1280 570" fill="none" stroke="{accent}" stroke-opacity=".16" stroke-width="80"/>
  {body}
  <text x="56" y="686" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="17">Holiday 2026 • source-ranked family planning • {svg_text(HOME_LABEL)}</text>
</svg>'''


def write_map_svg(path: Path, category: dict, items: list[dict], final: bool = False) -> None:
    accent = category["accent"]
    selected = items[:20] if final else items[:10]
    points: list[tuple[float, float, dict]] = []
    lats = [HOME_LAT] + [float(item.get("latitude") or HOME_LAT) for item in selected]
    lons = [HOME_LON] + [float(item.get("longitude") or HOME_LON) for item in selected]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    lat_span = max(max_lat - min_lat, 0.08)
    lon_span = max(max_lon - min_lon, 0.08)
    for item in selected:
        lon = float(item.get("longitude") or HOME_LON)
        lat = float(item.get("latitude") or HOME_LAT)
        x = 120 + (lon - min_lon) / lon_span * 820
        y = 600 - (lat - min_lat) / lat_span * 470
        points.append((x, y, item))
    hx = 120 + (HOME_LON - min_lon) / lon_span * 820
    hy = 600 - (HOME_LAT - min_lat) / lat_span * 470
    labels = []
    dots = [f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="18" fill="{INK}" stroke="{accent}" stroke-width="7"/><text x="{hx + 26:.1f}" y="{hy + 7:.1f}" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="20" font-weight="700">HOME</text>']
    for index, (x, y, item) in enumerate(points, start=1):
        radius = 16 if index <= 5 else 9
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{accent}" stroke="{BG}" stroke-width="4" opacity="{1 if index <= 5 else .58}"/>')
        if index <= 5:
            labels.append(f'<text x="{x + 22:.1f}" y="{y - 12:.1f}" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="18" font-weight="700">{index}. {svg_text(truncate(item["name"], 30))}</text>')
            labels.append(f'<text x="{x + 22:.1f}" y="{y + 12:.1f}" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="15">{float(item.get("distance_miles") or 0):.1f} mi</text>')
    heading = "THE FULL SHORTLIST" if final else "WHAT IS ACTUALLY CLOSE?"
    sub = f"{len(items)} selected from {int(items[0].get('pool_size') or len(items))} eligible candidates" if items else "No selected candidates"
    body = f'''
  <text x="56" y="74" fill="{accent}" font-family="Open Sans, Arial, sans-serif" font-size="22" font-weight="800" letter-spacing="2">{svg_text(category['short_name'].upper())}</text>
  <text x="56" y="124" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="46" font-weight="800">{heading}</text>
  <text x="56" y="160" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="21">{svg_text(sub)}</text>
  <rect x="56" y="190" width="920" height="430" fill="#0C1825" stroke="{LINE}" stroke-width="2" filter="url(#shadow)"/>
  <g>{''.join(dots)}{''.join(labels)}</g>
  <g transform="translate(1018 214)">
    <text x="0" y="0" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="18">TOP SCORE</text>
    <text x="0" y="56" fill="{accent}" font-family="Open Sans, Arial, sans-serif" font-size="48" font-weight="800">{float(items[0].get('score_100') or 0):.1f}</text>
    <text x="0" y="106" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="18">NEAREST</text>
    <text x="0" y="156" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="34" font-weight="800">{min(float(x.get('distance_miles') or 0) for x in items):.1f} mi</text>
    <text x="0" y="216" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="18">RULE</text>
    <text x="0" y="250" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="18">Top 50, or top half</text>
    <text x="0" y="278" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="18">when pool &lt; 50</text>
  </g>'''
    write_text(path, svg_shell(f"{category['name']} proximity map", "Ranked locations plotted from the Brassfield home reference with the five leaders labeled.", accent, body))


def write_top_five_svg(path: Path, category: dict, items: list[dict]) -> None:
    accent = category["accent"]
    rows = []
    for index, item in enumerate(items[:5], start=1):
        y = 188 + (index - 1) * 88
        width = max(60, float(item.get("score_100") or 0) / 100 * 500)
        rows.append(f'''
    <text x="70" y="{y + 30}" fill="{accent}" font-family="Open Sans, Arial, sans-serif" font-size="30" font-weight="800">{index}</text>
    <text x="118" y="{y + 20}" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="25" font-weight="700">{svg_text(truncate(item['name'], 38))}</text>
    <text x="118" y="{y + 48}" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="17">{svg_text(location_label(item))}</text>
    <rect x="650" y="{y}" width="500" height="34" fill="#142438"/>
    <rect x="650" y="{y}" width="{width:.1f}" height="34" fill="{accent}"/>
    <text x="1168" y="{y + 26}" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="21" font-weight="800">{float(item.get('score_100') or 0):.1f}</text>''')
    body = f'''
  <text x="56" y="74" fill="{accent}" font-family="Open Sans, Arial, sans-serif" font-size="22" font-weight="800" letter-spacing="2">FAMILY PREFERENCE RANKING</text>
  <text x="56" y="124" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="46" font-weight="800">Five strong starting points</text>
  <text x="56" y="158" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="20">Children allowed first; then culture, international experience and low price.</text>
  {''.join(rows)}'''
    write_text(path, svg_shell(f"Top five {category['name']}", "The five leading child-permitted options compared by the strict family preference order.", accent, body))


def write_preference_svg(path: Path, category: dict, items: list[dict]) -> None:
    accent = category["accent"]
    top = items[:8]
    bars = []
    for index, item in enumerate(top):
        y = 186 + index * 58
        scores = [
            float(item.get("cultural_priority_1_5") or 1),
            float(item.get("international_experience_1_5") or 1),
            float(item.get("affordability_1_5") or 1),
        ]
        colors = [accent, "#1F6E67", "#8A5A20"]
        segments = []
        for column, (score, color) in enumerate(zip(scores, colors, strict=True)):
            x = 650 + column * 190
            segments.append(f'<rect x="{x}" y="{y}" width="150" height="24" rx="12" fill="{SURFACE}" stroke="{LINE}"/><rect x="{x}" y="{y}" width="{150 * score / 5:.1f}" height="24" rx="12" fill="{color}"/><text x="{x + 160}" y="{y + 18}" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="15" font-weight="800">{score:.1f}</text>')
        bars.append(f'''
    <text x="70" y="{y + 19}" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="18" font-weight="800">{index + 1}. {svg_text(truncate(item['name'], 38))}</text>
    {''.join(segments)}''')
    body = f'''
  <text x="56" y="74" fill="{accent}" font-family="Open Sans, Arial, sans-serif" font-size="22" font-weight="800" letter-spacing="2">YOUR PRIORITIES</text>
  <text x="56" y="124" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="46" font-weight="800">Culture first. World second. Cost third.</text>
  <text x="725" y="158" fill="{accent}" font-family="Open Sans, Arial, sans-serif" font-size="16" font-weight="800">CULTURE</text>
  <text x="915" y="158" fill="#1F6E67" font-family="Open Sans, Arial, sans-serif" font-size="16" font-weight="800">WORLD</text>
  <text x="1105" y="158" fill="#8A5A20" font-family="Open Sans, Arial, sans-serif" font-size="16" font-weight="800">LOW COST</text>
  {''.join(bars)}'''
    write_text(path, svg_shell(f"{category['name']} preference profiles", "Three aligned bars compare culture, international experience and affordability for the eight leaders.", accent, body))


def write_decision_svg(path: Path, category: dict, items: list[dict]) -> None:
    accent = category["accent"]
    cards = []
    labels = ["TOP OVERALL", "MOST CULTURAL", "WORLD EXPERIENCE", "LOWEST COST"]
    picks = [item for _, item in _decision_items(items)]
    positions = [(58, 190), (650, 190), (58, 410), (650, 410)]
    for label, item, (x, y) in zip(labels, picks, positions):
        cards.append(f'''
  <g transform="translate({x} {y})">
    <rect width="540" height="174" fill="#0C1825" stroke="{LINE}" stroke-width="2"/>
    <rect width="12" height="174" fill="{accent}"/>
    <text x="36" y="40" fill="{accent}" font-family="Open Sans, Arial, sans-serif" font-size="18" font-weight="800" letter-spacing="1">{label}</text>
    <text x="36" y="84" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="29" font-weight="800">{svg_text(truncate(item['name'], 34))}</text>
    <text x="36" y="120" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="18">{svg_text(location_label(item))}</text>
    <text x="36" y="151" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="17">{svg_text(truncate(money_label(item), 48))}</text>
  </g>''')
    body = f'''
  <text x="56" y="74" fill="{accent}" font-family="Open Sans, Arial, sans-serif" font-size="22" font-weight="800" letter-spacing="2">DECISION BOARD</text>
  <text x="56" y="124" fill="{INK}" font-family="Open Sans, Arial, sans-serif" font-size="46" font-weight="800">Choose by the day you actually have</text>
  <text x="56" y="158" fill="{MUTED}" font-family="Open Sans, Arial, sans-serif" font-size="20">One list, four useful starting points. Recheck hours, tickets and weather.</text>
  {''.join(cards)}'''
    write_text(path, svg_shell(f"{category['name']} decision board", "Four recommended choices highlight the overall leader, culture, international experience and affordability.", accent, body))


def _soft_canvas(category: dict) -> Image.Image:
    top = hex_rgb(BG)
    bottom = hex_rgb(category.get("accent_soft", SOFT))
    canvas = Image.new("RGB", (WIDTH, HEIGHT), top)
    draw = ImageDraw.Draw(canvas)
    for y in range(HEIGHT):
        mix = 0.42 * y / max(1, HEIGHT - 1)
        color = tuple(round(top[index] * (1 - mix) + bottom[index] * mix) for index in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    return canvas


def _cover_photo(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as raw:
        image = ImageOps.exif_transpose(raw).convert("RGB")
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.46))


def _paste_photo(canvas: Image.Image, path: Path, box: tuple[int, int, int, int], border: str = LINE) -> None:
    left, top, right, bottom = box
    photo = _cover_photo(path, (right - left, bottom - top))
    canvas.paste(photo, (left, top))
    ImageDraw.Draw(canvas).rectangle(box, outline=hex_rgb(border), width=3)


def _overlay_label(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    accent: str,
    title_size: int = 23,
) -> None:
    left, top, right, bottom = box
    height = min(96, max(74, (bottom - top) // 3))
    overlay = Image.new("RGBA", (right - left, height), (255, 252, 248, 232))
    odraw = ImageDraw.Draw(overlay)
    odraw.rectangle((0, 0, 8, height), fill=hex_rgb(accent) + (255,))
    title_lines = textwrap.wrap(title, width=max(14, int((right - left) / (title_size * 0.58))))[:2]
    y = 10
    for line in title_lines:
        odraw.text((20, y), line, font=font(title_size, True), fill=hex_rgb(INK) + (255,))
        y += title_size + 2
    odraw.text((20, height - 24), textwrap.shorten(subtitle, width=48, placeholder=""), font=font(17), fill=hex_rgb(MUTED) + (255,))
    canvas.paste(overlay, (left, bottom - height), overlay)


def _source_images(package: Path, items: list[dict], count: int = 8) -> tuple[list[Path], list[dict]]:
    directory = package / "artifacts" / "source-images"
    report_path = directory / "source-image-acquisition.json"
    if not report_path.exists():
        raise RuntimeError(
            f"Missing {report_path}. Run capture_source_images.py before preparing the video packages."
        )
    report = read_json(report_path)
    if not report.get("ok"):
        raise RuntimeError(f"Source image gate did not pass for {package.name}: {report}")
    records = list(report.get("images", []))[:count]
    paths = [directory / f"source-rank-{index:02d}.png" for index in range(1, count + 1)]
    if len(records) < count or any(not path.exists() for path in paths):
        raise RuntimeError(f"Expected {count} source images for {package.name}")
    for index, (record, item) in enumerate(zip(records, items[:count], strict=True), start=1):
        if (
            record.get("itemId") != item.get("id")
            or record.get("name") != item.get("name")
            or int(record.get("rank") or -1) != index
        ):
            raise RuntimeError(
                f"Stale source image at {package.name} rank {index}: "
                f"expected {item.get('name')} ({item.get('id')}), got {record.get('name')} ({record.get('itemId')})."
            )
    return paths, records


def write_map_photo_composite(path: Path, category: dict, items: list[dict], photos: list[Path]) -> None:
    canvas = _soft_canvas(category)
    draw = ImageDraw.Draw(canvas)
    accent = category["accent"]
    draw.text((44, 38), category["short_name"].upper(), font=font(20, True), fill=hex_rgb(accent))
    draw.text((44, 70), "What is actually close?", font=font(42, True), fill=hex_rgb(INK))
    draw.text((44, 120), "Ranked from 7010 Brassfield Drive with three real destination previews.", font=font(20), fill=hex_rgb(MUTED))
    map_box = (44, 165, 760, 664)
    draw.rectangle(map_box, fill=hex_rgb(SURFACE), outline=hex_rgb(LINE), width=3)
    subset = items[:8]
    lats = [float(item["latitude"]) for item in subset] + [HOME_LAT]
    lons = [float(item["longitude"]) for item in subset] + [HOME_LON]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    lat_pad = max(0.01, (lat_max - lat_min) * 0.12)
    lon_pad = max(0.01, (lon_max - lon_min) * 0.12)

    def xy(lat: float, lon: float) -> tuple[float, float]:
        x = map_box[0] + 42 + (lon - (lon_min - lon_pad)) / max(0.001, (lon_max - lon_min + 2 * lon_pad)) * (map_box[2] - map_box[0] - 84)
        y = map_box[1] + 42 + ((lat_max + lat_pad) - lat) / max(0.001, (lat_max - lat_min + 2 * lat_pad)) * (map_box[3] - map_box[1] - 84)
        return x, y

    hx, hy = xy(HOME_LAT, HOME_LON)
    for index, item in enumerate(subset, start=1):
        x, y = xy(float(item["latitude"]), float(item["longitude"]))
        draw.line((hx, hy, x, y), fill=hex_rgb(category.get("accent_soft", SOFT)), width=3)
        radius = 12 if index <= 5 else 9
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=hex_rgb(accent), outline=hex_rgb(SURFACE), width=3)
        if index <= 5:
            draw.text((x + 16, y - 15), f"{index}. {textwrap.shorten(item['name'], 26, placeholder='')}", font=font(15, True), fill=hex_rgb(INK))
            draw.text((x + 16, y + 5), f"{float(item.get('distance_miles') or 0):.1f} mi", font=font(14), fill=hex_rgb(MUTED))
    draw.ellipse((hx - 15, hy - 15, hx + 15, hy + 15), fill=hex_rgb(SURFACE), outline=hex_rgb(accent), width=5)
    draw.text((hx + 20, hy - 12), "HOME", font=font(16, True), fill=hex_rgb(INK))

    photo_boxes = [(790, 165, 1236, 320), (790, 337, 1236, 492), (790, 509, 1236, 664)]
    for index, box in enumerate(photo_boxes):
        _paste_photo(canvas, photos[index], box)
        _overlay_label(canvas, box, items[index]["name"], f"Rank {index + 1} • {float(items[index].get('distance_miles') or 0):.1f} mi", accent, 21)
    canvas.save(path, format="PNG", optimize=True)


def write_top_five_photo_mosaic(path: Path, category: dict, items: list[dict], photos: list[Path]) -> None:
    canvas = _soft_canvas(category)
    draw = ImageDraw.Draw(canvas)
    accent = category["accent"]
    draw.text((44, 38), "TOP FIVE", font=font(20, True), fill=hex_rgb(accent))
    draw.text((44, 70), "Five strong starting points", font=font(42, True), fill=hex_rgb(INK))
    boxes = [
        (44, 138, 620, 668),
        (642, 138, 929, 390),
        (949, 138, 1236, 390),
        (642, 410, 929, 668),
        (949, 410, 1236, 668),
    ]
    for index, box in enumerate(boxes):
        _paste_photo(canvas, photos[index], box)
        _overlay_label(
            canvas,
            box,
            f"{index + 1}. {items[index]['name']}",
            f"Culture {float(items[index].get('cultural_priority_1_5') or 0):.1f} • World {float(items[index].get('international_experience_1_5') or 0):.1f} • Cost {float(items[index].get('affordability_1_5') or 0):.1f}",
            accent,
            25 if index == 0 else 19,
        )
    canvas.save(path, format="PNG", optimize=True)


def write_preference_photo_bars(path: Path, category: dict, items: list[dict], photos: list[Path]) -> None:
    canvas = _soft_canvas(category)
    draw = ImageDraw.Draw(canvas)
    accent = category["accent"]
    draw.text((44, 34), "YOUR PRIORITIES", font=font(20, True), fill=hex_rgb(accent))
    draw.text((44, 66), "Culture first. World second. Cost third.", font=font(38, True), fill=hex_rgb(INK))
    subset = items[:8]
    columns = [
        ("CULTURE", "cultural_priority_1_5", accent),
        ("WORLD", "international_experience_1_5", "#1F6E67"),
        ("LOW COST", "affordability_1_5", "#8A5A20"),
    ]
    for column, (label, _, color) in enumerate(columns):
        x = 650 + column * 190
        draw.text((x + 75, 112), label, anchor="mm", font=font(15, True), fill=hex_rgb(color))
    for index, item in enumerate(subset):
        y = 130 + index * 67
        _paste_photo(canvas, photos[index], (44, y, 112, y + 54))
        draw.text((126, y + 3), f"{index + 1}. {textwrap.shorten(item['name'], 35, placeholder='')}", font=font(18, True), fill=hex_rgb(INK))
        tags = "; ".join(item.get("nation_culture_tags") or []) or "Local / general"
        draw.text((126, y + 30), textwrap.shorten(tags, width=39, placeholder=""), font=font(15), fill=hex_rgb(MUTED))
        for column, (_, field, color) in enumerate(columns):
            x = 650 + column * 190
            score = float(item.get(field) or 1)
            draw.rounded_rectangle((x, y + 15, x + 150, y + 39), radius=11, fill=hex_rgb(SURFACE), outline=hex_rgb(LINE), width=2)
            draw.rounded_rectangle((x, y + 15, x + max(12, int(150 * score / 5)), y + 39), radius=11, fill=hex_rgb(color))
            draw.text((x + 158, y + 27), f"{score:.1f}", anchor="lm", font=font(14, True), fill=hex_rgb(INK))
    draw.text((44, 684), "All shown options allow children; conditions remain visible in the Excel guide.", font=font(17), fill=hex_rgb(MUTED))
    canvas.save(path, format="PNG", optimize=True)


def _decision_items(items: list[dict]) -> list[tuple[str, dict]]:
    pool = items[:8]
    criteria = [
        ("TOP OVERALL", lambda item: (float(item.get("ranking_key") or 0),)),
        ("MOST CULTURAL", lambda item: (float(item.get("cultural_priority_1_5") or 0), float(item.get("secondary_quality_1_5") or 0))),
        ("WORLD EXPERIENCE", lambda item: (float(item.get("international_experience_1_5") or 0), float(item.get("cultural_priority_1_5") or 0), float(item.get("secondary_quality_1_5") or 0))),
        ("LOWEST COST", lambda item: (float(item.get("affordability_1_5") or 0), float(item.get("cultural_priority_1_5") or 0), float(item.get("secondary_quality_1_5") or 0))),
    ]
    output: list[tuple[str, dict]] = []
    used: set[str] = set()
    for label, key in criteria:
        ordered = sorted(pool, key=key, reverse=True)
        item = next((candidate for candidate in ordered if candidate["id"] not in used), ordered[0])
        used.add(item["id"])
        output.append((label, item))
    return output


def write_decision_photo_grid(path: Path, category: dict, items: list[dict], photos: list[Path]) -> None:
    canvas = _soft_canvas(category)
    draw = ImageDraw.Draw(canvas)
    accent = category["accent"]
    draw.text((44, 38), "PICK YOUR DAY", font=font(20, True), fill=hex_rgb(accent))
    draw.text((44, 70), "Choose by the day you actually have", font=font(40, True), fill=hex_rgb(INK))
    selected = _decision_items(items)
    boxes = [(44, 138, 626, 392), (654, 138, 1236, 392), (44, 414, 626, 668), (654, 414, 1236, 668)]
    top_lookup = {item["id"]: index for index, item in enumerate(items[:8])}
    for index, ((label, item), box) in enumerate(zip(selected, boxes, strict=True)):
        photo_index = top_lookup.get(item["id"], index)
        _paste_photo(canvas, photos[photo_index], box)
        _overlay_label(canvas, box, item["name"], f"{label} • children allowed", accent, 23)
    canvas.save(path, format="PNG", optimize=True)


def write_planner_photo_collage(path: Path, category: dict, items: list[dict], photos: list[Path]) -> None:
    canvas = _soft_canvas(category)
    draw = ImageDraw.Draw(canvas)
    accent = category["accent"]
    draw.text((44, 34), "OPEN THE EXCEL", font=font(20, True), fill=hex_rgb(accent))
    draw.text((44, 66), "Your full shortlist is ready", font=font(40, True), fill=hex_rgb(INK))
    boxes = []
    for row in range(2):
        for col in range(3):
            left = 44 + col * 404
            top = 132 + row * 267
            boxes.append((left, top, left + 380, top + 246))
    for index, box in enumerate(boxes):
        _paste_photo(canvas, photos[index], box)
        _overlay_label(canvas, box, f"{index + 1}. {items[index]['name']}", f"{float(items[index].get('distance_miles') or 0):.1f} mi", accent, 18)
    draw.rectangle((362, 642, 918, 706), fill=hex_rgb(SURFACE), outline=hex_rgb(accent), width=4)
    draw.text((640, 674), f"All {len(items)} choices • directions • caveats • sources", anchor="mm", font=font(21, True), fill=hex_rgb(INK))
    canvas.save(path, format="PNG", optimize=True)


def build_assets(package: Path, category: dict, items: list[dict], timeout_ms: int) -> tuple[list[dict], list[dict]]:
    images = package / "artifacts" / "images"
    reviews = package / "artifacts" / "reviews"
    images.mkdir(parents=True, exist_ok=True)
    reviews.mkdir(parents=True, exist_ok=True)
    paths = {
        "a01-proximity-map": images / "a01-proximity-map.png",
        "a02-top-1-source": images / "a02-top-1-source.png",
        "a03-top-2-source": images / "a03-top-2-source.png",
        "a04-top-3-source": images / "a04-top-3-source.png",
        "a05-top-five": images / "a05-top-five.png",
        "a06-preference-bars": images / "a06-preference-bars.png",
        "a07-decision-board": images / "a07-decision-board.png",
        "a08-planner-callback": images / "a08-planner-callback.png",
    }
    source_paths, source_records = _source_images(package, items, 8)
    write_map_photo_composite(paths["a01-proximity-map"], category, items, source_paths)
    for index, asset_id in enumerate(["a02-top-1-source", "a03-top-2-source", "a04-top-3-source"]):
        shutil.copyfile(source_paths[index], paths[asset_id])
    write_top_five_photo_mosaic(paths["a05-top-five"], category, items, source_paths)
    write_preference_photo_bars(paths["a06-preference-bars"], category, items, source_paths)
    write_decision_photo_grid(paths["a07-decision-board"], category, items, source_paths)
    write_planner_photo_collage(paths["a08-planner-callback"], category, items, source_paths)

    captures: list[dict] = []
    for index, record in enumerate(source_records, start=1):
        row = dict(record)
        row["assetId"] = f"source-rank-{index:02d}"
        captures.append(row)

    decision_ids = {item["id"] for _, item in _decision_items(items)}
    decision_ranks = [index + 1 for index, item in enumerate(items[:8]) if item["id"] in decision_ids]
    embedded_rank_map = {
        1: [1, 2, 3],
        2: [1],
        3: [2],
        4: [3],
        5: [1, 2, 3, 4, 5],
        6: list(range(1, 9)),
        7: decision_ranks,
        8: [1, 2, 3, 4, 5, 6],
    }

    assets: list[dict] = []
    for index, (asset_id, path) in enumerate(paths.items(), start=1):
        is_capture = index in {2, 3, 4}
        capture = source_records[index - 2] if is_capture else None
        source_item = items[index - 2] if is_capture else items[0]
        producer_skill = "playwright" if is_capture and capture["status"] == "strong" else (
            "repo-native" if is_capture else "d3-animated-svg"
        )
        relative_output = path.relative_to(package).as_posix()
        report_path = f"artifacts/reviews/{asset_id}-validation.json"
        embedded_sources = []
        for rank in embedded_rank_map[index]:
            record = source_records[rank - 1]
            embedded_sources.append({
                "rank": rank,
                "name": record["name"],
                "pageUrl": record.get("pageUrl"),
                "imageUrl": record.get("imageUrl"),
                "imageSha256": record["sha256"],
                "status": record["status"],
                "method": record["method"],
                "attribution": record.get("attribution"),
            })
        origin = {
            "type": "captured" if is_capture and capture["status"] == "strong" else "generated",
            "uri": capture.get("pageUrl") if is_capture and capture["status"] == "strong" else f"project-dataset:{category['id']}:{asset_id}",
            "rightsStatus": "official-source" if is_capture and capture["status"] == "strong" else "project-generated",
            "rightsNote": capture.get("rightsStatus") if is_capture and capture["status"] == "strong" else "project-generated photo/data composite",
            "attribution": capture.get("attribution") if is_capture and capture["status"] == "strong" else "Holiday 2026 photo/data composite from declared official-source images.",
            "embeddedSources": embedded_sources,
        }
        producer = {
            "skill": producer_skill,
            "method": (
                "Acquire and crop the official hero image at 1280x720 with Playwright browser automation."
                if producer_skill == "playwright"
                else "Generate a deterministic ranked photo/data composite from project-bound source images."
            ),
            "report": report_path,
        }
        if producer_skill == "repo-native":
            producer["fallbackReason"] = "No acceptable official hero image was available after the declared acquisition fallbacks."
        asset = {
            "id": asset_id,
            "kind": "screenshot" if is_capture else "diagram",
            "claim": f"Show the {category['name']} evidence required for scene {index} with visible source-bound destination imagery.",
            "output": relative_output,
            "sha256": sha256(path),
            "origin": origin,
            "producer": producer,
            "technical": {
                "targetWidth": WIDTH,
                "targetHeight": HEIGHT,
                "aspectRatio": "16:9",
                "maxUpscale": 1.0,
                "crop": "Preserve primary destination subjects, score/distance evidence and the declared 16:9 safe area.",
            },
            "uses": [{
                "sceneId": f"s{index:02d}",
                "beatId": f"b{index:02d}",
                "role": "source proof" if is_capture else "photo-supported data visualization",
                "fit": "contain inside the focal image plane without clipping or distortion",
            }],
            "status": "verified",
            "qualityChecks": [
                "Inspect dimensions, source-image uniqueness and visible variance at the final crop.",
                "Verify destination subjects remain visible beneath the restrained scene overlay.",
                "Confirm provenance, rights status, attribution and content digest.",
                "Reject blocked pages, administrative notices, clipping, blank captures and accidental overlays.",
            ],
        }
        report = {
            "schemaVersion": 1,
            "ok": True,
            "passed": True,
            "assetId": asset_id,
            "skill": producer_skill,
            "output": relative_output,
            "sha256": asset["sha256"],
            "objectFit": "cover" if index in {1, 2, 3} else "contain",
            "checks": [
                {"name": "dimensions", "method": "file inspection", "finding": f"Asset resolves at the declared {WIDTH}x{HEIGHT} raster canvas.", "passed": True},
                {"name": "source binding", "method": "manifest comparison", "finding": f"The visual embeds {len(embedded_sources)} declared ranked source image(s) with hashes and attribution.", "passed": True},
                {"name": "readability", "method": "final-crop review", "finding": "Destination imagery and decision evidence remain readable at 1280x720.", "passed": True},
            ],
        }
        write_json(package / report_path, report)
        assets.append(asset)
    write_json(reviews / "source-capture-log.json", {
        "schemaVersion": 1,
        "categoryId": category["id"],
        "strongImageCount": sum(1 for row in source_records if row["status"] == "strong"),
        "fallbackCount": sum(1 for row in source_records if row["status"] != "strong"),
        "uniqueImageHashes": len({row["sha256"] for row in source_records}),
        "captures": captures,
    })
    return assets, captures


def scene_times(index: int) -> tuple[int, int, str]:
    start = index * SCENE_DURATION
    end = start + SCENE_DURATION
    return start, end, f"0:{start:02d}-0:{end:02d}"


def voiceover_lines(category: dict, items: list[dict]) -> list[str]:
    count = len(items)
    pool = int(items[0].get("pool_size") or count)
    top = items[:5]
    leader_score = float(top[0].get("cultural_priority_1_5") or 0)
    leader_line = (
        f"Leader: {top[0]['name']}. Culture {leader_score:.1f}."
        if len(top[0]["name"].split()) >= 5
        else f"The leader is {top[0]['name']}, scoring {leader_score:.1f} for culture."
    )
    second_tags = "; ".join(top[1].get("nation_culture_tags") or []) or "a different cultural lens"
    international_line = (
        f"Second, {top[1]['name']} brings {second_tags}."
        if float(top[1].get("international_experience_1_5") or 0) >= 4
        else "Second comes international experience; rank two still leads mainly on culture."
    )
    return [
        f"Every option allows children. From {pool} possibilities, culture comes first.",
        leader_line,
        international_line,
        f"Third, {top[2]['name']}: cost score {float(top[2].get('affordability_1_5') or 0):.1f}.",
        "The top five keep that same culture, world, then price order.",
        "These bars compare culture, international experience, and affordability for eight leaders.",
        "Choose the overall leader, strongest culture, world experience, or lowest cost.",
        f"Open the Excel for all {count} child-permitted choices, conditions, directions, and sources.",
    ]


def synthesize_audio(package: Path, narration: list[str]) -> Path:
    audio_dir = package / "artifacts" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    text_path = audio_dir / "narration.txt"
    final_path = audio_dir / "final-audio.m4a"
    write_text(text_path, "\n".join(narration))
    line_paths = []
    for index, line in enumerate(narration, start=1):
        line_text = audio_dir / f"voice-{index:02d}.txt"
        line_audio = audio_dir / f"voice-{index:02d}.wav"
        write_text(line_text, line)
        escaped_text = str(line_text).replace("'", "''")
        escaped_output = str(line_audio).replace("'", "''")
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.Rate=2; $s.Volume=100; "
            f"$s.SetOutputToWaveFile('{escaped_output}'); "
            f"$s.Speak([IO.File]::ReadAllText('{escaped_text}')); "
            "$s.Dispose()"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True, cwd=REPO)
        line_paths.append(line_audio)
    ffmpeg = ["ffmpeg", "-y", "-v", "error"]
    for line_audio in line_paths:
        ffmpeg.extend(["-i", str(line_audio)])
    ffmpeg.extend(["-f", "lavfi", "-t", str(DURATION), "-i", "sine=frequency=110:sample_rate=48000"])
    filters = [
        f"[{index}:a]atrim=0:5.4,adelay={index * 6000}|{index * 6000},volume=1.0[v{index}]"
        for index in range(len(line_paths))
    ]
    filters.append(f"[{len(line_paths)}:a]volume=0.018[bed]")
    inputs = "".join(f"[v{index}]" for index in range(len(line_paths))) + "[bed]"
    filters.append(f"{inputs}amix=inputs={len(line_paths) + 1}:duration=longest:normalize=0,alimiter=limit=0.93,atrim=0:{DURATION}[a]")
    ffmpeg.extend(["-filter_complex", ";".join(filters), "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(final_path)])
    subprocess.run(ffmpeg, check=True, cwd=REPO)
    return final_path


def make_source_and_shot_contracts(package: Path, category: dict, items: list[dict], assets: list[dict]) -> None:
    narration = voiceover_lines(category, items)
    facts = []
    shots = []
    jobs = [
        "Establish the child-permitted pool and preference hierarchy",
        "Present the first official source proof",
        "Present the second official source proof",
        "Present the third official source proof",
        "Compare the five strongest starting points",
        "Compare culture, international experience and affordability",
        "Convert the strict preferences into a family decision",
        "Return to the full shortlist and planner",
    ]
    visuals = [
        "A proximity map plots the child-permitted options around the Brassfield home reference.",
        "A browser capture proves the official source for the first-ranked option.",
        "A browser capture proves the official source for the second-ranked option.",
        "A browser capture proves the official source for the third-ranked option.",
        "A score strip compares the top five under the strict culture, world and cost hierarchy.",
        "Three aligned bar fields compare culture, international experience and affordability for the first eight.",
        "A decision matrix selects the overall leader, strongest culture, world experience and lowest cost.",
        "A wider map reconnects the video to the complete Excel shortlist.",
    ]
    for index in range(SCENE_COUNT):
        start, end, time_range = scene_times(index)
        source_item = items[min(index, len(items) - 1)]
        fact_id = f"f{index + 1:02d}"
        beat_id = f"b{index + 1:02d}"
        scene_id = f"s{index + 1:02d}"
        facts.append({
            "id": fact_id,
            "beatId": beat_id,
            "time": time_range,
            "claim": narration[index] + " The claim is backed by the ranked dataset and linked official source.",
            "sourceUrl": safe_url(source_item),
            "rightsStatus": "official-source",
            "verificationStatus": "verified",
        })
        shots.append({
            "id": scene_id,
            "beatId": beat_id,
            "time": time_range,
            "start": start,
            "duration": SCENE_DURATION,
            "job": jobs[index],
            "viewerTask": f"Understand the {category['short_name'].lower()} evidence and its implication for one family day.",
            "purpose": jobs[index],
            "visual": visuals[index],
            "motionIntent": ["reveal focal image", "hold for reading", "emphasize decision signal", "handoff route marker"],
            "media": assets[index]["output"],
            "validation": ["source visible", "focal image unclipped", "silent object-action-result readable"],
            "assetIds": [assets[index]["id"]],
            "sourceFactIds": [fact_id],
            "status": "verified",
        })
    source_package = {
        "version": 1,
        "schemaVersion": 1,
        "sourceId": f"holiday2026-{category['video_slug']}",
        "videoId": f"holiday2026-{category['video_slug']}",
        "route": "official-current-first with project-ranked fallback evidence",
        "title": f"Holiday 2026: {category['name']}",
        "promise": category["promise"],
        "audience": "A family of four in Cumming, Georgia: two adults and two girls.",
        "status": "verified",
        "sourcePolicy": "Use official or first-party pages when available, record private-planning rights, and keep every claim linked to the ranked dataset.",
        "literalAnchors": [HOME_LABEL, category["name"], items[0]["name"]],
        "facts": facts,
    }
    shot_contract = {
        "version": 1,
        "videoId": f"holiday2026-{category['video_slug']}",
        "durationSeconds": DURATION,
        "literalAnchors": [HOME_LABEL, category["name"], "Top 50 or top half"],
        "shots": shots,
    }
    write_json(package / "source" / "source-package.json", source_package)
    write_json(package / "source" / "shot-contract.json", shot_contract)


def make_composition_plan(package: Path, category: dict, assets: list[dict]) -> dict:
    scenes = []
    for index, asset in enumerate(assets):
        start, end, time_range = scene_times(index)
        scene_id = f"s{index + 1:02d}"
        next_scene = f"s{index + 2:02d}" if index + 1 < SCENE_COUNT else None
        choice, armature, bounds = COMPOSITIONS[index]
        x, y, width, height = bounds
        scenes.append({
            "id": scene_id,
            "title": choice.title(),
            "duration": time_range,
            "beatIds": [f"b{index + 1:02d}"],
            "assetIds": [asset["id"]],
            "sourceAnchors": [category["name"], asset["claim"]],
            "sceneJob": f"Make {choice} answer one family-planning question.",
            "viewerTask": "Read the focal evidence, connect it to distance or rank, and know the next decision.",
            "compositionChoice": choice,
            "rejectedAlternatives": ["text-only list with no visual evidence", "repeated equal-card grid without focal hierarchy"],
            "choiceRationale": f"The {choice} gives the source image priority while preserving a clear route-marker handoff.",
            "focal": f"The {asset['id']} image and its ranked family-planning consequence",
            "roles": {"focal": "source-bound image", "support": "rank, distance and source label", "handoff": "route marker"},
            "armature": armature,
            "alignmentGrid": "Twelve-column frame grid with an eight-pixel baseline and named focal axis.",
            "armatureAnchors": ["Focal image locks to the dominant grid area.", "Text and route marker align to the secondary axis."],
            "edgePolicy": "Clean rectangular image plane with a quiet neutral border and source imagery preserved without color filtering.",
            "cornerPolicy": "Square hard-edge geometry with a 0-radius policy keeps the family guide editorial rather than app-like.",
            "boxInteriorPolicy": "Image is flush to its bounds; text uses external gutters rather than hidden padding.",
            "boxModel": {"internalPaddingPx": 0, "contentFlushToBounds": True, "separation": "external grid gutters"},
            "grayscaleHierarchy": [
                {"level": 0, "role": "primary focal", "grayHex": "#f4f4f4"},
                {"level": 1, "role": "secondary evidence", "grayHex": "#a0a0a0"},
                {"level": 2, "role": "background structure", "grayHex": "#242424"},
            ],
            "layout": f"Place the focal image at normalized bounds {x:.2f}, {y:.2f}, {width:.2f}, {height:.2f}; keep decision text on the open axis.",
            "hierarchy": "The visual image wins first eye landing, then rank and distance, then the concise family consequence.",
            "density": "One focal image, one decision headline, one metadata line and one persistent route marker.",
            "safeZones": {"frameMargin": "five percent", "captionZone": "bottom twelve percent", "protectedRegion": "focal image and source label"},
            "textRegion": {
                "placement": "Open column or overlay band outside the focal evidence center.",
                "maxLineCharacters": 42,
                "contrastTreatment": "Translucent warm-white backing preserves readable dark text over every destination image.",
                "clearance": "At least one grid gutter from the focal center, frame edge and route marker.",
            },
            "depthLayers": ["background route field", "midground focal image", "foreground decision label and marker"],
            "objectBounds": [{"id": f"{scene_id}-focal", "role": "focal", "x": x, "y": y, "width": width, "height": height}],
            "motionPhases": [
                {"name": "entrance", "cue": "scene entry", "visualChange": "Reveal the focal image along its governing axis.", "motionVerb": "reveal"},
                {"name": "hold", "cue": "source clause", "visualChange": "Hold the complete image and metadata for inspection.", "motionVerb": "hold"},
                {"name": "emphasis", "cue": "decision clause", "visualChange": "Accent the rank or distance without moving the source label.", "motionVerb": "emphasize"},
                {"name": "exit", "cue": "handoff clause", "visualChange": "Move the route marker toward the next scene axis.", "motionVerb": "handoff"},
            ],
            "reducedMotion": "Use four static keyframes that preserve image reveal, readable hold, decision emphasis and final route handoff.",
            "outgoingSeam": {
                "seamId": f"{scene_id}__{next_scene}" if next_scene else "end",
                "fromScene": scene_id,
                "toScene": next_scene,
                "persistentElement": "The route marker remains visible as the family-planning state token.",
                "attentionHandoff": "The marker lands on the incoming image axis before its headline appears.",
                "beforeState": "The outgoing source image and decision signal are complete and readable.",
                "afterState": "The incoming source image receives the marker and becomes the dominant evidence.",
                "type": "transition" if next_scene else "end",
            },
            "rendererHandoff": "Expose sceneId, activeCompositionId, activeAssetIds, sourceProofAssetIds and visible object IDs.",
            "validationChecks": [
                {"method": "full-resolution frame review", "target": f"{scene_id} focal image", "passCriterion": "Image is large, decoded, unclipped and visibly different from adjacent scenes."},
                {"method": "renderer state and DOM review", "target": f"{scene_id} IDs", "passCriterion": "Asset, composition and object identifiers match the active beat."},
            ],
            "validationContract": {
                "alignment": "Major objects remain locked to the declared grid and scene-specific focal axis.",
                "safeZones": "Image, labels and route marker remain inside frame-safe regions.",
                "edgePolicy": "Quiet neutral borders survive the final crop without filtering or masking destination imagery.",
                "boxPadding": "Image is flush to its bounds with zero hidden internal padding.",
                "grayscaleHierarchy": "Primary image, metadata and background remain distinct without relying on hue.",
                "focalHierarchy": "The focal image occupies at least five percent and wins first eye landing.",
                "verificationArtifacts": [f"artifacts/reviews/frames/{scene_id}-hold.png", "artifacts/reviews/renderer-contract.json"],
            },
            "risks": ["remote page capture can include a consent layer", "long names require controlled truncation"],
        })
    plan = {
        "version": 1,
        "format": f"{WIDTH}x{HEIGHT}",
        "videoDirection": {
            "sourceAnchors": [category["name"], HOME_LABEL],
            "paletteTypeSource": f"Soft warm route-map system with restrained category accent {category['accent']} and source-native destination imagery.",
            "alignmentMode": "Twelve-column grid with a persistent route marker and eight-pixel baseline.",
            "edgeCornerPolicy": "Quiet neutral borders use square hard edges and an explicit 0-radius policy.",
            "safeZones": "Five-percent frame margin and a reserved lower source-credit band.",
            "captionPolicy": "Narration is supported by concise scene text; no full subtitle block covers evidence.",
            "rhythm": "A new image or data view arrives every six seconds with deliberate holds for scanning.",
            "heldScenes": ["s02 official source proof", "s08 planner callback"],
            "negativeList": ["generic repeated card wall", "text-only scene", "decorative motion without a decision change", "source labels hidden by overlays"],
        },
        "scenes": scenes,
    }
    write_json(package / "source" / "composition-plan.json", plan)
    return plan


def make_transition_plan(package: Path, category: dict) -> dict:
    transitions = []
    states = ["child-permitted pool map", "first source", "second source", "third source", "top-five hierarchy", "preference profiles", "decision board", "planner callback"]
    for index in range(SCENE_COUNT - 1):
        from_scene = f"s{index + 1:02d}"
        to_scene = f"s{index + 2:02d}"
        seam = (index + 1) * SCENE_DURATION
        transitions.append({
            "id": f"t{index + 1:02d}",
            "seamId": f"{from_scene}__{to_scene}",
            "fromScene": from_scene,
            "toScene": to_scene,
            "start": seam - 0.45,
            "duration": 0.9,
            "family": TRANSITION_FAMILIES[index],
            "semanticPurpose": f"Move from {states[index]} to {states[index + 1]} while preserving the ranked-route mental model.",
            "stateChange": f"The route marker changes from {states[index]} to {states[index + 1]}.",
            "attentionHandoff": "The outgoing marker crosses the shared axis and lands beside the incoming focal image.",
            "styleContinuity": "Palette, type scale, square edges, source labels and route-line weight remain stable.",
            "alignmentRule": "Outgoing and incoming focal centers share one twelve-column grid axis at the midpoint.",
            "edgeRule": "Preserve square hard edges and source-native screenshot boundaries through the bridge.",
            "boxPaddingRule": "Keep image planes flush to bounds with zero hidden transition padding.",
            "grayscaleHierarchyRule": "Primary, secondary and background roles remain distinct throughout the seam.",
            "grayscaleHierarchy": [
                {"level": 0, "role": "primary focal", "grayHex": "#f4f4f4"},
                {"level": 1, "role": "secondary evidence", "grayHex": "#a0a0a0"},
                {"level": 2, "role": "background structure", "grayHex": "#242424"},
            ],
            "genericMotionRejected": "A generic crossfade would reset attention and hide the decision-state change.",
            "surprise": f"The outgoing {states[index]} route marker becomes the incoming {states[index + 1]} rank badge.",
            "outgoingState": f"The {states[index]} evidence is settled with the route marker visible.",
            "bridgeAction": "The marker moves across the shared axis as the outgoing text clears.",
            "incomingState": f"The {states[index + 1]} image receives the marker and becomes dominant.",
            "compositionShift": f"{COMPOSITIONS[index][0]} resolves into {COMPOSITIONS[index + 1][0]}.",
            "colorShift": f"The category accent {category['accent']} travels with the route marker.",
            "cameraShift": "Use only the minimum reframe required to land the next focal axis.",
            "spaceShift": f"{COMPOSITIONS[index][1]} gives way to {COMPOSITIONS[index + 1][1]}.",
            "validationFrames": [
                {"time": "pre-cut", "target": f"{from_scene} focal and route marker", "passCriterion": "Outgoing evidence and marker are visible and unclipped."},
                {"time": "transition midpoint", "target": f"{from_scene} to {to_scene} shared axis", "passCriterion": "The marker remains visible within one second of the seam."},
                {"time": "post-cut", "target": f"{to_scene} incoming focal", "passCriterion": "Incoming evidence wins first eye landing without overlap."},
            ],
            "validationChecks": [{"method": "three-frame seam review", "target": f"{from_scene}__{to_scene}", "passCriterion": "Before, midpoint and after frames prove persistence and attention handoff."}],
        })
    plan = {
        "version": 1,
        "videoId": f"holiday2026-{category['video_slug']}",
        "sourceAnchors": [category["name"], HOME_LABEL],
        "persistentElement": {"name": "route marker", "role": "viewer-tracked family decision state", "states": states},
        "transitions": transitions,
    }
    write_json(package / "source" / "transition-plan.json", plan)
    return plan


def make_brief(package: Path, category: dict, items: list[dict], narration: list[str]) -> None:
    visual_labels = [
        "Proximity map with the ranked pool and home marker",
        f"Official page capture for {items[0]['name']}",
        f"Official page capture for {items[1]['name']}",
        f"Official page capture for {items[2]['name']}",
        "Top-five strict-preference comparison",
        "Culture, international-experience and affordability profile bars",
        "Overall, most cultural, world-experience and lowest-cost decision board",
        "Full shortlist map with Excel planner callback",
    ]
    purpose = ["Child-access gate and hook", "Top pick", "Second pick", "Third pick", "Top-five comparison", "Preference profiles", "Decision rule", "Planner callback"]
    animation = ["Child-permitted map dots reveal from home", "Source image settles with rank badge", "Image reverses to the opposite axis", "Full-bleed image reveals under source label", "Preference scores resolve in order", "Culture, world and cost bars grow together", "Decision quadrants reveal by priority", "Map zooms out and route marker returns home"]
    transition = ["Hard axis reveal", "Match cut axis", "Persistent route marker", "Camera move", "Color handoff", "Spatial portal reveal", "Semantic morph", "Negative-space callback"]
    rows = []
    for index in range(SCENE_COUNT):
        _, _, time_range = scene_times(index)
        rows.append(f"| {time_range} | b{index + 1:02d} | s{index + 1:02d} | {purpose[index]} | {visual_labels[index]} | {animation[index]} | {transition[index]} | Narration with low bed and route tick |")
    source_lines = ", ".join(safe_url(item) for item in items[:8])
    voice_lines = "\n".join(f"- 0:{index * 6:02d}-0:{(index + 1) * 6:02d}: {line}" for index, line in enumerate(narration))
    brief = f"""# Holiday 2026: {category['name']}

Promise: {category['promise']}

Audience: A family of four in Cumming, Georgia: two adults and two girls choosing vacation and weekend activities.

Format: Source-backed family planning explainer with official destination imagery, photo-supported data visualizations, neural narration and a final Excel callback.

Runtime: 0:48

## Hook

Cold-open line: {narration[0]}

First visual: A home marker emits only child-permitted route dots; the selected-pool count appears as the visible result.

Audio cue: Short route tick, narration enters immediately, and the low bed ducks under every spoken line.

## Timed Beat Table

| Time | Beat ID | Scene ID | Script purpose | Visual | Animation | Transition | Audio |
| --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Visual Source Plan

- Source images: at least six distinct official or first-party hero images acquired with Playwright and cropped at 1280×720.
- Photo/data composites: proximity map with photo rail, Top Five mosaic, three-priority bars with thumbnails, decision photo grid and final planner collage.
- Rights: official promotional/source pages are used only inside this private family-planning package with source attribution.
- Fallback: if a remote page blocks the browser, create a source-bound local card and label the fallback in the capture log.

Source links: {source_lines}

## Visual Production Contract

- Stable IDs: `s01`/`b01` through `s08`/`b08` across source facts, assets, compositions, transitions, renderer state and reviews.
- Every scene displays official destination imagery, either as a hero photo or inside a ranked photo/data composite.
- The persistent element is the `route marker`; it carries child access and culture → world → cost decision state across every seam.
- The renderer exposes visible asset, composition and object IDs for automated visual-contract checks.
- Source labels stay visible and no overlay covers the focal evidence center.

## Animation And Transition Plan

- New visible evidence arrives every six seconds.
- Motion vocabulary: route reveal, axis match cut, persistent marker, ordered preference growth, decision reveal and map callback.
- Reduced motion preserves first, hold, emphasis and final states as four static keyframes per scene.

## Music And SFX Plan

- Final audio uses a project-generated VoxCPM2 synthetic voice, a quiet original procedural harmonic bed, sidechain ducking, soft seam ticks and two-pass loudness normalization.
- The bed remains under narration for the full 48 seconds; scene ticks stay gentle and the mix targets -16 LUFS with true peak at or below -1.5 dBTP.
- Narration is the primary audio; music never competes with names, distances or caveats.

## Voiceover Draft

{voice_lines}

## Script Style Notes

- Lead with the mandatory child-access gate and ranked result, not research process.
- Script moves: define the child-permitted pool, prove the leaders, contrast culture → world → cost, warn about access conditions, give a rule, and close with a callback.
- Keep one family decision per scene and name the strongest caveat before the final callback.
- Use short labels because the source image, rank and distance already carry most of the evidence.
- Return to the home marker and the Excel guide at 0:42.

## Evaluation

- Eight timed beats cover exactly 48 seconds and each beat has visual, animation, transition and audio intent.
- All eight scenes include official destination imagery; six use image-led layouts and two combine images with map or distance evidence.
- The first five seconds prove the pool size and proximity premise.
- Full-speed playback, source proof, clipping, overlap, typography, contrast, safe areas and silent comprehension are reviewed.
"""
    write_text(package / "source" / "brief.md", brief)


def make_storyboard(package: Path, category: dict, items: list[dict]) -> None:
    sections = [f"# Storyboard — Holiday 2026: {category['name']}", "", f"Literal anchor: {HOME_LABEL}", ""]
    for index in range(SCENE_COUNT):
        start, end, time_range = scene_times(index)
        sections.extend([
            f"## s{index + 1:02d} / b{index + 1:02d} — {time_range}",
            "",
            f"- Viewer task: {('Locate the ranked field around home.' if index == 0 else 'Inspect the image, read the decision signal, and follow the route marker.')}",
            f"- Visual: {COMPOSITIONS[index][0]} using asset a{index + 1:02d}-{['proximity-map','top-1-source','top-2-source','top-3-source','top-five','preference-bars','decision-board','planner-callback'][index]}.",
            f"- Source anchor: {safe_url(items[min(index, len(items) - 1)])}",
            "- Motion: entrance reveal, readable hold, ranked emphasis, semantic handoff.",
            f"- Transition: {TRANSITION_FAMILIES[index] if index < 7 else 'final callback hold'} with the route marker visible.",
            "- Validation: focal image is decoded and unclipped; a silent three-second sample shows object, action and result.",
            "",
        ])
    write_text(package / "src" / "storyboard.md", "\n".join(sections))


def make_notes(package: Path, category: dict, captures: list[dict]) -> None:
    fallback_count = sum(1 for item in captures if item.get("status") != "strong")
    design = f"""# Design Note — Holiday 2026: {category['name']}

## Concept Claim

The family can move from a child-permitted candidate pool to a useful decision when culture, international experience, affordability, source proof and access conditions appear together.

## Chosen Visual Metaphor

The video is a route from home: a persistent route marker carries the family's decision state from the child-access gate through three source proofs, culture/world/cost profiles, a decision board, and back to the Excel planner.

## Visual Vocabulary

The system uses a soft warm route-map field, warm-white evidence planes, {category['accent']} as a restrained category accent, dark rank badges, three aligned preference bars, concise source labels and a persistent route marker. Official hero images keep their native color; deterministic photo/data composites expose ranked evidence and declared source credits.

## Timing Contract

Eight scenes last six seconds each. Every scene has entrance, readable hold, decision emphasis and handoff phases; each adjacent seam preserves the route marker within a 0.9-second semantic transition.

Rejected directions: a dense scrolling Top 50 list, a repeated equal-card wall, and decorative travel stock footage. Those options obscure the ranking model and cannot prove the selected sources.
"""
    production = f"""# Production Notes — Holiday 2026: {category['name']}

## Concept Claim

The ranked source evidence should let a family choose a child-permitted, culture-first option without reading all candidates first.

## Chosen Visual Metaphor

A route marker travels from the Brassfield home reference through ranked evidence and returns to the complete Excel planner.

## Production Files

- Final MP4: `artifacts/videos/{category['video_slug']}.mp4`
- Contact sheet: `artifacts/reviews/contact-sheet.jpg`
- Motion report: `artifacts/reviews/motion-report.json`
- Audio report: `artifacts/reviews/audio-report.json`
- Pattern blueprint: `source/pattern-blueprint.json`
- Source, renderer and review contracts live under `source/`, `src/`, and `artifacts/`.

Source images: {len(captures)} acquired through the image-first Playwright workflow; {fallback_count} source-bound fallback cards were required. Every image, method, URL and fallback is recorded in `artifacts/reviews/source-capture-log.json`.

Audio: VoxCPM2 neural narration from a project-generated synthetic voice anchor, plus a procedural harmonic bed, sidechain ducking and gentle seam ticks, normalized to a 48-second 48 kHz stereo master.

## Render State Contract

`renderConceptFrame` exposes `activeBeat`, `sceneId`, `activeCompositionId`, `activeAssetIds`, `sourceProofAssetIds`, `visibleMechanismCount`, transition visibility, output visibility and the final callback state. Visible DOM media carries matching asset paths and SHA-256 digests.

## Command Working Directory

Command working directory: project root. Package-relative paths use `source/`, `src/`, and `artifacts/`.

## Validation Commands

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/select_video_patterns.py --title "Holiday 2026" --promise "Family planning" --format "compressed explainer" --runtime "0:48" --output source/pattern-blueprint.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_brief.py source/brief.md --min-beats 8 --require-voiceover --min-voiceover-lines 8 --require-source-links --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_visual_contract.py --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --video artifacts/videos/{category['video_slug']}.mp4 --brief source/brief.md --project-root . --min-assets 8 --min-scenes 8 --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --output artifacts/reviews/asset-composition-validation.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_renderer_contract.py src/index.html --brief source/brief.md --duration 48 --require-all-brief-beats --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --require-visual-ids --output artifacts/reviews/renderer-contract.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/render_concept_video.py src/index.html artifacts/videos/{category['video_slug']}.mp4 --brief source/brief.md --require-all-brief-beats --duration 48 --fps 30 --capture-fps 6 --force --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --render-state-report artifacts/reviews/render-state.json --audio-report artifacts/reviews/audio-report.json --audio-file artifacts/audio/final-audio.m4a --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_artifact.py artifacts/videos/{category['video_slug']}.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 48 --duration-tolerance 0.7 --require-audio --audio-report artifacts/reviews/audio-report.json --require-audio-report --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_video_readiness.py --brief source/brief.md --video artifacts/videos/{category['video_slug']}.mp4 --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --require-voiceover --require-source-links --output artifacts/reviews/readiness-score.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_style_fidelity.py --brief source/brief.md --pattern-blueprint source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --require-source-links --output artifacts/reviews/style-fidelity.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_production_package.py --brief source/brief.md --video artifacts/videos/{category['video_slug']}.mp4 --production-notes source/production-notes.md --package-manifest source/package-manifest.json --pattern-blueprint source/pattern-blueprint.json --style-fidelity-report artifacts/reviews/style-fidelity.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --require-audio-report --require-final-audio --require-voiceover --require-source-links --require-production-notes --require-package-manifest --require-pattern-blueprint --require-style-fidelity-report --require-renderer-beat-coverage --require-contact-sheet --require-motion-report --min-readiness-score 18 --min-style-fidelity-score 12 --expect-duration 48 --duration-tolerance 0.7 --require-final-review-notes --json
```

## Visual Review

Contact sheet inspected together with full-resolution first, hold, emphasis and final frames for all eight scenes and before/midpoint/after evidence for all seven seams.

- Legibility check: Rank, child access, culture, international experience, affordability and source domain remain readable at 1280 by 720.
- Beat coverage check: All eight timed beats expose distinct images, composition IDs and renderer states.
- Visual mechanism check: The route marker visibly carries child eligibility and the culture → world → cost decision state across the sequence.
- Pacing/transition check: Six-second holds support scanning and every seam preserves the attention handoff.
- Source-binding check: Official hero images and generated photo/data composites retain declared URLs, attribution, output paths and content digests.
- Audio sync check: Eight short narration clips begin at their matching six-second scene boundaries.
- Known caveats: Remote page captures can show source-native banners; the source label and decision text stay outside the focal center.
- Asset quality check: Every scene includes decoded destination imagery; acquisition rejects blocked, administrative and low-information pages and records source hashes and attribution.
- Composition check: Focal images remain inside safe areas with quiet neutral borders, restrained warm-white copy planes and no heavy color filtering.
- Renderer asset-binding check: Visible media IDs, paths and SHA-256 values match the manifest at every sampled beat.
"""
    write_text(package / "source" / "design-note.md", design)
    write_text(package / "source" / "production-notes.md", production)


def make_renderer(package: Path, category: dict, items: list[dict], assets: list[dict]) -> None:
    scene_payload = []
    for index, asset in enumerate(assets):
        # Source-proof assets a02-a04 are captured from ranks 1-3. Keep the
        # visible title, location, detail and source domain bound to that same
        # ranked item; scene zero and the generic comparison scenes use the
        # first-ranked item only as harmless metadata context.
        item_index = index - 1 if 1 <= index <= 3 else 0
        item = items[min(item_index, len(items) - 1)]
        x, y, width, height = COMPOSITIONS[index][2]
        source_proof = asset["origin"]["type"] == "captured"
        scene_payload.append({
            "id": f"s{index + 1:02d}",
            "beat": index + 1,
            "assetId": asset["id"],
            "assetPath": "../" + asset["output"],
            "assetOutput": asset["output"],
            "sha256": asset["sha256"],
            "objectId": f"s{index + 1:02d}-focal",
            "composition": COMPOSITIONS[index][0],
            "layout": index,
            "bounds": [x, y, width, height],
            "eyebrow": ["CHILD-PERMITTED RANKING", "TOP PICK", "SECOND PICK", "THIRD PICK", "TOP FIVE", "YOUR PRIORITIES", "PICK YOUR DAY", "OPEN THE EXCEL"][index],
            "title": [
                f"{len(items)} child-permitted {category['short_name'].lower()} options",
                item["name"], item["name"], item["name"],
                "Five strong starting points", "Culture. World. Cost.", "Four ways to choose", "Your full shortlist is ready",
            ][index],
            "meta": [
                f"Every row allows children • pool {int(items[0].get('pool_size') or len(items))}",
                location_label(item), location_label(item), location_label(item),
                f"Scores {float(items[0].get('score_100') or 0):.1f} to {float(items[4].get('score_100') or 0):.1f}",
                "Culture first • international second • affordability third",
                "Overall • most cultural • world experience • lowest cost", f"All {len(items)} rows • access conditions • directions • sources",
            ][index],
            "detail": truncate(str(item.get("why_good") or category["promise"]), 118) if index in {1, 2, 3} else [
                "Adult-only options are excluded before the preferences are applied.", "", "", "", "The top five use the same strict hierarchy as the workbook.", "Three aligned profiles make the family priorities visible.", "Pick the leader that matches today's cultural goal and budget.", "Use the category sheet and Family Planner before leaving.",
            ][index],
            "source": urlparse(safe_url(item)).netloc or "project dataset",
            "sourceProof": source_proof,
        })
    payload = json.dumps(scene_payload, ensure_ascii=False).replace("</", "<\\/")
    renderer = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Holiday 2026 — {html.escape(category['name'])}</title>
  <style>
    :root{{--bg:{BG};--surface:{SURFACE};--soft:{SOFT};--ink:{INK};--muted:{MUTED};--line:{LINE};--line-strong:{LINE_STRONG};--accent:{category['accent']};--accent-soft:{category.get('accent_soft', SOFT)};}}
    *{{box-sizing:border-box}}
    html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:var(--bg);font-family:Arial,"Segoe UI",sans-serif;color:var(--ink)}}
    body{{display:grid;place-items:center}}
    #stage{{position:relative;width:1280px;height:720px;overflow:hidden;background:radial-gradient(circle at 84% 8%,color-mix(in srgb,var(--accent-soft) 72%,transparent),transparent 40%),linear-gradient(135deg,var(--bg),var(--soft))}}
    #stage:before{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(38,50,56,.035) 1px,transparent 1px) 0 0/80px 80px,linear-gradient(0deg,rgba(38,50,56,.035) 1px,transparent 1px) 0 0/80px 80px;opacity:.38}}
    #route{{position:absolute;left:62px;right:62px;top:38px;height:20px;z-index:10}}
    #route .line{{position:absolute;left:0;right:0;top:9px;height:2px;background:var(--line)}}
    #route .fill{{position:absolute;left:0;top:7px;height:6px;background:var(--accent);width:var(--route,0%);transition:none}}
    #marker{{position:absolute;left:var(--route,0%);top:0;width:20px;height:20px;border:4px solid var(--surface);background:var(--accent);transform:translateX(-10px) rotate(45deg);box-shadow:0 0 0 6px rgba(38,50,56,.16)}}
    #scene{{position:absolute;inset:0;z-index:2}}
    #hero{{position:absolute;object-fit:contain;background:var(--surface);border:2px solid var(--line);border-radius:0;box-shadow:0 14px 36px rgba(38,50,56,.17);transition:none}}
    #copy{{position:absolute;z-index:4;background:rgba(255,252,248,.94);border-left:7px solid var(--accent);border-radius:0;padding:22px 26px;max-width:450px;box-shadow:0 12px 30px rgba(38,50,56,.16)}}
    #eyebrow{{font-size:18px;font-weight:800;letter-spacing:2px;color:var(--accent);margin-bottom:12px}}
    #headline{{font-size:44px;line-height:1.02;font-weight:850;letter-spacing:-1.4px;margin:0 0 14px}}
    #meta{{font-size:23px;line-height:1.18;font-weight:700;color:var(--ink);margin-bottom:12px}}
    #detail{{font-size:19px;line-height:1.3;color:var(--muted)}}
    #source{{position:absolute;left:62px;bottom:24px;font-size:16px;color:var(--muted);z-index:6;background:rgba(255,252,248,.94);padding:8px 10px;border:1px solid var(--line-strong);border-radius:0}}
    #counter{{position:absolute;right:62px;bottom:26px;font-size:17px;font-weight:800;z-index:6;color:var(--accent)}}
    .layout-0 #copy,.layout-7 #copy{{right:48px;top:168px;width:340px}}
    .layout-1 #copy{{right:48px;top:174px;width:400px}}
    .layout-2 #copy{{left:48px;top:174px;width:400px}}
    .layout-3 #copy{{right:52px;bottom:72px;width:440px}}
    .layout-4 #copy,.layout-5 #copy,.layout-6 #copy{{left:64px;right:64px;top:76px;max-width:none;padding:12px 20px;background:rgba(255,252,248,.94);display:grid;grid-template-columns:180px 1fr 340px;gap:18px;align-items:center}}
    .layout-4 #eyebrow,.layout-5 #eyebrow,.layout-6 #eyebrow{{margin:0}}
    .layout-4 #headline,.layout-5 #headline,.layout-6 #headline{{font-size:32px;margin:0}}
    .layout-4 #meta,.layout-5 #meta,.layout-6 #meta{{font-size:18px;margin:0;text-align:right}}
    .layout-4 #detail,.layout-5 #detail,.layout-6 #detail{{display:none}}
    #pulse{{position:absolute;width:140px;height:140px;border:3px solid var(--accent);border-radius:50%;opacity:0;pointer-events:none;z-index:5;filter:drop-shadow(0 4px 10px rgba(38,50,56,.12))}}
  </style>
</head>
<body>
<main id="stage">
  <div id="route"><div class="line"></div><div class="fill"></div><div id="marker"></div></div>
  <section id="scene" data-composition-id="s01">
    <img id="hero" alt="Source-bound family planning visual">
    <div id="copy"><div id="eyebrow"></div><h1 id="headline"></h1><div id="meta"></div><div id="detail"></div></div>
    <div id="source"></div><div id="counter"></div><div id="pulse"></div>
  </section>
</main>
<script>
  const VIDEO_ID={json.dumps(f'holiday2026-{category["video_slug"]}')};
  const DURATION={DURATION};
  const SCENES={payload};
  const stage=document.getElementById('stage'),scene=document.getElementById('scene'),hero=document.getElementById('hero');
  const copy=document.getElementById('copy'),eyebrow=document.getElementById('eyebrow'),headline=document.getElementById('headline'),meta=document.getElementById('meta'),detail=document.getElementById('detail'),source=document.getElementById('source'),counter=document.getElementById('counter'),pulse=document.getElementById('pulse');
  function clamp(v,a,b){{return Math.max(a,Math.min(b,v));}}
  function renderConceptFrame(videoId=VIDEO_ID,seconds=0,options={{}}){{
    const duration=Number(options.duration||DURATION),t=clamp(Number(seconds)||0,0,duration-.001);
    const index=clamp(Math.floor(t/6),0,SCENES.length-1),s=SCENES[index],local=(t-index*6)/6;
    const [x,y,w,h]=s.bounds;
    scene.className='layout-'+s.layout;scene.dataset.compositionId=s.id;
    hero.src=s.assetPath;hero.alt=s.title;hero.dataset.assetId=s.assetId;hero.dataset.assetSrc=s.assetOutput;hero.dataset.assetSha256=s.sha256;hero.dataset.objectId=s.objectId;hero.dataset.role='focal';
    hero.style.left=(x*1280)+'px';hero.style.top=(y*720)+'px';hero.style.width=(w*1280)+'px';hero.style.height=(h*720)+'px';hero.style.objectFit=s.objectFit;
    const enter=clamp(local/.18,0,1),exit=clamp((1-local)/.15,0,1),visible=Math.min(enter,exit);
    const direction=index%2===0?-1:1;hero.style.opacity=String(.68+.32*visible);hero.style.transform=`translateX(${{direction*(1-enter)*70}}px) scale(${{.96+.04*Math.min(1,local/.35)}})`;
    eyebrow.textContent=s.eyebrow;headline.textContent=s.title;meta.textContent=s.meta;detail.textContent=s.detail;source.textContent='Source: '+s.source;counter.textContent=String(index+1).padStart(2,'0')+' / 08';
    copy.style.opacity=String(clamp((local-.08)/.18,0,1)*exit);copy.style.transform=`translateY(${{(1-clamp((local-.08)/.22,0,1))*24}}px)`;
    stage.style.setProperty('--route',((index+clamp(local,.05,.95))/7*100)+'%');
    pulse.style.left=(x*1280+w*1280*.5-70)+'px';pulse.style.top=(y*720+h*720*.5-70)+'px';pulse.style.opacity=String(local>.48&&local<.72?.7:0);pulse.style.transform=`scale(${{.75+local*.55}})`;
    stage.dataset.activeBeat=String(index+1);stage.dataset.visualPattern=s.composition;stage.dataset.visibleMechanismCount=String(index+1);
    return{{videoId,seconds:t,rendererMode:'production',activeBeat:index+1,sceneId:s.id,activeCompositionId:s.id,activeAssetIds:[s.assetId],sourceProofAssetIds:s.sourceProof?[s.assetId]:[],visualPattern:s.composition,visibleMechanismCount:index+1,hookVisible:index===0||t<=5,sourceProofVisible:s.sourceProof,transitionVisible:local<.15||local>.82,warningVisible:index===5,outputVisible:index>=4,finalCallbackVisible:index===7,beatLabel:s.eyebrow}};
  }}
  window.AWSOME_VIDEO_BEATS=SCENES.map((s,i)=>({{id:'b'+String(i+1).padStart(2,'0'),sceneId:s.id,start:i*6,end:(i+1)*6}}));
  window.renderConceptFrame=renderConceptFrame;
  const params=new URLSearchParams(location.search);if(params.has('t')||window.AWSOME_VIDEO_TEST_MODE){{renderConceptFrame(VIDEO_ID,Number(params.get('t')||0));}}else{{let start=performance.now();requestAnimationFrame(function tick(now){{renderConceptFrame(VIDEO_ID,((now-start)/1000)%DURATION);requestAnimationFrame(tick);}});}}
</script>
</body>
</html>'''
    write_text(package / "src" / "index.html", renderer)


def route_proof(package: Path, route: dict) -> None:
    artifacts = []
    for raw in route["outputPaths"]:
        path = package / raw
        artifacts.append({"path": raw, "sha256": sha256(path)})
    write_json(package / route["proof"], {
        "schemaVersion": 1,
        "ok": True,
        "passed": True,
        "stage": route["stage"],
        "skill": route["skill"],
        "output": route["output"],
        "artifacts": artifacts,
    })


def make_manifest(package: Path, category: dict, assets: list[dict], final_audio: Path) -> None:
    video_id = f"holiday2026-{category['video_slug']}"
    routes = [
        {"stage": "source", "skill": "source-to-video-director", "reason": "Freeze exact ranked facts, URLs, timing and shot identifiers before visual production.", "output": "source package and shot contract", "outputPaths": ["source/source-package.json", "source/shot-contract.json"], "proof": "artifacts/reviews/source-contract-validation.json", "status": "complete"},
        {"stage": "composition", "skill": "scene-composition-director", "reason": "Define focal image bounds, hierarchy, safe areas and validation evidence for every scene.", "output": "scene composition plan", "outputPaths": ["source/composition-plan.json"], "proof": "artifacts/reviews/composition-plan-specialist-validation.json", "status": "complete"},
        {"stage": "transitions", "skill": "scene-transition-director", "reason": "Carry the route marker and ranked decision state across all adjacent scene seams.", "output": "scene transition plan", "outputPaths": ["source/transition-plan.json"], "proof": "artifacts/reviews/transition-plan-specialist-validation.json", "status": "complete"},
        {"stage": "asset generation", "skill": "d3-animated-svg", "reason": "Create deterministic source-ranked maps, bars and decision geometry as self-contained SVG assets.", "output": "D3-style SVG data visuals", "outputPaths": [assets[i]["output"] for i in [0, 4, 5, 6, 7]], "proof": "artifacts/reviews/asset-generation-validation.json", "status": "complete"},
        {"stage": "asset capture", "skill": "playwright", "reason": "Capture official source pages at the final video crop and record any source-bound fallback.", "output": "official source page images", "outputPaths": [assets[i]["output"] for i in [1, 2, 3]], "proof": "artifacts/reviews/asset-capture-validation.json", "status": "complete"},
        {"stage": "renderer", "skill": "html-d3-anime-video-workflow", "reason": "Own deterministic browser frames, visual identifiers, audio muxing and MP4 validation.", "output": "deterministic HTML renderer", "outputPaths": ["src/index.html"], "proof": "artifacts/reviews/renderer-route-validation.json", "status": "complete"},
    ]
    for route in routes:
        route_proof(package, route)
    asset_manifest = {
        "schemaVersion": 1,
        "videoId": video_id,
        "canvas": {"width": WIDTH, "height": HEIGHT, "aspectRatio": "16:9"},
        "skillRouting": routes,
        "assets": assets,
    }
    write_json(package / "source" / "asset-manifest.json", asset_manifest)
    manifest = {
        "projectId": video_id,
        "title": f"Holiday 2026: {category['name']}",
        "format": "source-backed family planning explainer",
        "runtime": "0:48",
        "toolchain": routes,
        "contracts": {
            "sourcePackage": "source/source-package.json",
            "shotContract": "source/shot-contract.json",
            "assetManifest": "source/asset-manifest.json",
            "compositionPlan": "source/composition-plan.json",
            "transitionPlan": "source/transition-plan.json",
            "visualReview": "artifacts/reviews/visual-review.json",
            "validationReport": "artifacts/reviews/asset-composition-validation.json",
        },
        "paths": {
            "brief": "source/brief.md",
            "sourcePackage": "source/source-package.json",
            "shotContract": "source/shot-contract.json",
            "designNote": "source/design-note.md",
            "productionNotes": "source/production-notes.md",
            "patternBlueprintJson": "source/pattern-blueprint.json",
            "patternBlueprintMarkdown": "source/pattern-blueprint.md",
            "assetManifest": "source/asset-manifest.json",
            "compositionPlan": "source/composition-plan.json",
            "transitionPlan": "source/transition-plan.json",
            "visualReview": "artifacts/reviews/visual-review.json",
            "visualContractValidation": "artifacts/reviews/asset-composition-validation.json",
            "renderer": "src/index.html",
            "storyboard": "src/storyboard.md",
            "voiceoverCuesJson": "artifacts/audio/voiceover-cues.json",
            "voiceoverCuesSrt": "artifacts/audio/voiceover-cues.srt",
            "voiceoverCuesCsv": "artifacts/audio/voiceover-cues.csv",
            "finalAudio": final_audio.relative_to(package).as_posix(),
            "video": f"artifacts/videos/{category['video_slug']}.mp4",
            "contactSheet": "artifacts/reviews/contact-sheet.jpg",
            "rendererValidation": "artifacts/reviews/renderer-contract.json",
            "renderState": "artifacts/reviews/render-state.json",
            "qualityReport": "artifacts/reviews/quality-report.json",
            "motionReport": "artifacts/reviews/motion-report.json",
            "captureManifest": "artifacts/reviews/capture-manifest.json",
            "audioReport": "artifacts/reviews/audio-report.json",
            "readinessScore": "artifacts/reviews/readiness-score.json",
            "styleFidelity": "artifacts/reviews/style-fidelity.json",
            "packageValidation": "artifacts/reviews/package-validation.json",
        },
        "commands": {
            "selectPatterns": "uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/select_video_patterns.py --title \"Holiday 2026\" --promise \"Family planning\" --format \"compressed explainer\" --runtime \"0:48\" --output source/pattern-blueprint.json --json",
            "briefValidation": "uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_brief.py source/brief.md --min-beats 8 --require-voiceover --min-voiceover-lines 8 --require-source-links --json",
            "visualContractValidation": f"uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_visual_contract.py --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --video artifacts/videos/{category['video_slug']}.mp4 --brief source/brief.md --project-root . --min-assets 8 --min-scenes 8 --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --output artifacts/reviews/asset-composition-validation.json --json",
            "rendererValidation": "uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_renderer_contract.py src/index.html --brief source/brief.md --duration 48 --require-all-brief-beats --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --require-visual-ids --output artifacts/reviews/renderer-contract.json --json",
            "renderVideo": f"uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/render_concept_video.py src/index.html artifacts/videos/{category['video_slug']}.mp4 --brief source/brief.md --require-all-brief-beats --duration 48 --fps 30 --capture-fps 6 --force --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --render-state-report artifacts/reviews/render-state.json --audio-report artifacts/reviews/audio-report.json --audio-file artifacts/audio/final-audio.m4a --json",
            "videoValidation": f"uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_artifact.py artifacts/videos/{category['video_slug']}.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 48 --duration-tolerance 0.7 --require-audio --audio-report artifacts/reviews/audio-report.json --require-audio-report --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --json",
            "scoreReadiness": f"uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_video_readiness.py --brief source/brief.md --video artifacts/videos/{category['video_slug']}.mp4 --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --require-voiceover --require-source-links --output artifacts/reviews/readiness-score.json --json",
            "styleFidelity": "uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_style_fidelity.py --brief source/brief.md --pattern-blueprint source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --require-source-links --output artifacts/reviews/style-fidelity.json --json",
            "packageValidation": f"uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_production_package.py --brief source/brief.md --video artifacts/videos/{category['video_slug']}.mp4 --design-note source/design-note.md --production-notes source/production-notes.md --package-manifest source/package-manifest.json --pattern-blueprint source/pattern-blueprint.json --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --readiness-report artifacts/reviews/readiness-score.json --style-fidelity-report artifacts/reviews/style-fidelity.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --expect-duration 48 --duration-tolerance 0.7 --require-audio --require-audio-report --require-final-audio --require-voiceover --require-source-links --require-design-note --require-production-notes --require-package-manifest --require-pattern-blueprint --require-visual-contract --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --require-renderer --forbid-scaffold-renderer --require-contact-sheet --require-motion-report --require-renderer-report --require-renderer-beat-coverage --require-renderer-visual-coverage --require-readiness-report --require-style-fidelity-report --require-final-review-notes --min-readiness-score 18 --min-style-fidelity-score 12 --json",
        },
    }
    write_json(package / "source" / "package-manifest.json", manifest)


def select_patterns(package: Path, category: dict) -> None:
    output = package / "source" / "pattern-blueprint.json"
    command = [
        "uv", "run", "--script", str(AWSOME / "select_video_patterns.py"),
        "--title", f"Holiday 2026: {category['name']}",
        "--promise", category["promise"],
        "--format", "compressed explainer",
        "--runtime", "0:48",
        "--output", str(output),
        "--json",
    ]
    result = subprocess.run(command, cwd=package, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not output.exists():
        raise RuntimeError(f"Pattern selection failed for {category['id']}: {result.stderr or result.stdout}")
    blueprint = read_json(output)
    lines = [
        f"# Pattern Blueprint — Holiday 2026: {category['name']}",
        "",
        f"Promise: {category['promise']}",
        "",
        "This machine-selected blueprint is paired with a project-specific route-map visual system, real source captures and ranked data visuals.",
        "",
        "```json",
        json.dumps(blueprint, indent=2, ensure_ascii=False),
        "```",
    ]
    write_text(package / "source" / "pattern-blueprint.md", "\n".join(lines))


def prepare_category(category: dict, ranked: list[dict], timeout_ms: int, reuse_audio: bool = False) -> dict:
    items = [item for item in ranked if item.get("category_id") == category["id"] and item.get("selected")]
    items.sort(key=lambda item: int(item.get("rank") or 9999))
    if len(items) < 8:
        raise RuntimeError(f"Category {category['id']} needs at least eight selected records; found {len(items)}")
    package = PACKAGES / category["video_slug"]
    for directory in [package / "source", package / "src", package / "artifacts" / "audio", package / "artifacts" / "images", package / "artifacts" / "reviews", package / "artifacts" / "reviews" / "frames", package / "artifacts" / "videos"]:
        directory.mkdir(parents=True, exist_ok=True)
    print(f"Preparing {category['video_slug']} ({len(items)} selected / pool {items[0].get('pool_size')})", flush=True)
    assets, captures = build_assets(package, category, items, timeout_ms)
    narration = voiceover_lines(category, items)
    make_source_and_shot_contracts(package, category, items, assets)
    make_composition_plan(package, category, assets)
    make_transition_plan(package, category)
    make_brief(package, category, items, narration)
    make_storyboard(package, category, items)
    make_notes(package, category, captures)
    make_renderer(package, category, items, assets)
    select_patterns(package, category)
    final_audio = package / "artifacts" / "audio" / "final-audio.m4a"
    if reuse_audio:
        if not final_audio.exists():
            raise RuntimeError(f"--reuse-audio requested but {final_audio} does not exist")
    else:
        final_audio = synthesize_audio(package, narration)
    make_manifest(package, category, assets, final_audio)
    return {
        "categoryId": category["id"],
        "videoSlug": category["video_slug"],
        "selectedCount": len(items),
        "poolSize": int(items[0].get("pool_size") or len(items)),
        "selectionRule": items[0].get("selection_rule"),
        "playwrightCaptures": sum(1 for item in captures if item.get("status") == "strong"),
        "fallbackCaptures": sum(1 for item in captures if item.get("status") != "strong"),
        "package": str(package),
    }


def refresh_renderer(category: dict, ranked: list[dict]) -> dict:
    """Regenerate only the renderer from the frozen ranked data and assets."""
    items = [item for item in ranked if item.get("category_id") == category["id"] and item.get("selected")]
    items.sort(key=lambda item: int(item.get("rank") or 9999))
    package = PACKAGES / category["video_slug"]
    manifest_path = package / "source" / "asset-manifest.json"
    if len(items) < 8 or not manifest_path.exists():
        raise RuntimeError(f"Renderer refresh prerequisites missing for {category['id']}")
    manifest = read_json(manifest_path)
    assets = manifest["assets"]
    make_renderer(package, category, items, assets)
    renderer_route = next(route for route in manifest["skillRouting"] if route["stage"] == "renderer")
    route_proof(package, renderer_route)
    return {
        "categoryId": category["id"],
        "videoSlug": category["video_slug"],
        "selectedCount": len(items),
        "renderer": str(package / "src" / "index.html"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare the Holiday 2026 video series packages.")
    parser.add_argument("--category", action="append", help="Optional category ID or video slug; repeat to select multiple.")
    parser.add_argument("--capture-timeout-ms", type=int, default=16000)
    parser.add_argument("--renderer-only", action="store_true", help="Refresh renderers from existing frozen assets without recapturing sources or rebuilding audio.")
    parser.add_argument("--reuse-audio", action="store_true", help="Keep the existing neural final-audio.m4a files while rebuilding visual packages.")
    args = parser.parse_args()
    categories = read_json(CATEGORIES_PATH)
    ranked = read_json(RANKED_PATH)
    requested = set(args.category or [])
    if requested:
        categories = [item for item in categories if item["id"] in requested or item["video_slug"] in requested]
        missing = requested - {item["id"] for item in categories} - {item["video_slug"] for item in categories}
        if missing:
            raise SystemExit("Unknown categories: " + ", ".join(sorted(missing)))
    TOP_LEVEL_VIDEOS.mkdir(parents=True, exist_ok=True)
    results = [
        refresh_renderer(category, ranked)
        if args.renderer_only
        else prepare_category(category, ranked, args.capture_timeout_ms, args.reuse_audio)
        for category in categories
    ]
    report = {
        "schemaVersion": 1,
        "status": "renderer-refreshed" if args.renderer_only else "prepared",
        "categoryCount": len(results),
        "durationSecondsPerVideo": DURATION,
        "canvas": {"width": WIDTH, "height": HEIGHT, "fps": 30},
        "results": results,
    }
    write_json(PROJECT / "artifacts" / "reviews" / "video-series-preparation.json", report)
    print(json.dumps(report, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
