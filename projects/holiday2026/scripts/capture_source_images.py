#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0.0",
#   "playwright>=1.45.0",
# ]
# ///
"""Acquire image-first official source visuals for the Holiday 2026 videos."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import textwrap
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


PROJECT = Path(__file__).resolve().parents[1]
PACKAGES = PROJECT / "video-packages"
WIDTH = 1280
HEIGHT = 720
MAX_DOWNLOAD_BYTES = 20 * 1024 * 1024
MAX_SOURCE_PIXELS = 24_000_000
MAX_SOURCE_EDGE = 9_000
BLOCK_MARKERS = (
    "sorry, you have been blocked",
    "access denied",
    "attention required! | cloudflare",
    "coming soon",
    "under construction",
    "ongoing construction",
    "use the tunnel on the left side",
    "page not found",
    "this page no longer exists",
    "well that's just peachy",
    "well that’s just peachy",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def image_metrics(image: Image.Image) -> dict:
    alpha_ratio = 0.0
    if "A" in image.getbands():
        alpha = image.getchannel("A")
        alpha_sample = alpha.resize((160, 90), Image.Resampling.LANCZOS)
        alpha_ratio = sum(1 for value in alpha_sample.getdata() if value < 245) / (160 * 90)
    rgb = image.convert("RGB")
    sample = rgb.copy()
    sample.thumbnail((320, 180), Image.Resampling.LANCZOS)
    gray = sample.convert("L")
    stddev = float(ImageStat.Stat(gray).stddev[0])
    colors = sample.getcolors(maxcolors=sample.width * sample.height + 1)
    color_count = len(colors) if colors is not None else sample.width * sample.height
    dominant_ratio = max((count for count, _ in colors), default=0) / max(1, sample.width * sample.height) if colors is not None else 0.0
    white_ratio = sum(1 for value in gray.getdata() if value >= 244) / max(1, sample.width * sample.height)
    return {
        "width": rgb.width,
        "height": rgb.height,
        "luminanceStddev": round(stddev, 3),
        "colorCount": color_count,
        "whiteRatio": round(white_ratio, 4),
        "dominantColorRatio": round(dominant_ratio, 4),
        "transparentPixelRatio": round(alpha_ratio, 4),
    }


def acceptable_image(image: Image.Image) -> tuple[bool, dict]:
    metrics = image_metrics(image)
    aspect = metrics["width"] / max(1, metrics["height"])
    ok = (
        metrics["width"] >= 600
        and metrics["height"] >= 320
        # Portrait source photos are useful when they still have enough
        # horizontal detail for a centered 16:9 cover crop.
        and 0.55 <= aspect <= 3.2
        and metrics["luminanceStddev"] >= 16
        and metrics["colorCount"] >= 96
        and metrics["whiteRatio"] <= 0.86
        and metrics["dominantColorRatio"] <= 0.62
        and metrics["transparentPixelRatio"] <= 0.18
    )
    metrics["aspectRatio"] = round(aspect, 4)
    return ok, metrics


def save_cover(image: Image.Image, path: Path) -> dict:
    image = ImageOps.exif_transpose(image).convert("RGB")
    canvas = ImageOps.fit(image, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS, centering=(0.5, 0.46))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=True)
    return image_metrics(canvas)


def soft_fallback(path: Path, item: dict, category: dict, rank: int, reason: str) -> None:
    bg = hex_rgb("#F6F3EE")
    soft = hex_rgb(category.get("accent_soft", "#E9EFEB"))
    accent = hex_rgb(category["accent"])
    ink = hex_rgb("#263238")
    muted = hex_rgb("#59666F")
    image = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        color = tuple(round(bg[i] * (1 - t * 0.55) + soft[i] * (t * 0.55)) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    draw.rectangle((52, 52, WIDTH - 52, HEIGHT - 52), outline=accent, width=4)
    draw.ellipse((82, 90, 214, 222), fill=soft, outline=accent, width=4)
    draw.text((148, 156), str(rank), fill=accent, font=font(58, True), anchor="mm")
    draw.text((252, 92), "FAMILY DESTINATION", fill=accent, font=font(23, True))
    lines = textwrap.wrap(item["name"], width=31)[:3]
    y = 146
    for line in lines:
        draw.text((252, y), line, fill=ink, font=font(50, True))
        y += 58
    location = ", ".join(part for part in [item.get("city"), item.get("state")] if part)
    draw.text((252, y + 14), location, fill=muted, font=font(27))
    draw.text((82, 598), "Official photo unavailable; use the source link in the Excel guide.", fill=ink, font=font(22, True))
    draw.text((82, 638), textwrap.shorten(reason, 110, placeholder=""), fill=muted, font=font(18))
    image.save(path, format="PNG", optimize=True)


def page_urls(item: dict) -> list[str]:
    values = [
        candidate.get("page_url")
        for candidate in item.get("image_candidates", [])
        if isinstance(candidate, dict)
    ]
    values.append(item.get("official_url"))
    values.append(item.get("corroborating_url"))
    output: list[str] = []
    for value in values:
        if value and value.startswith(("http://", "https://")) and value not in output:
            output.append(value)
    return output


def extract_candidates(page) -> dict:
    return page.evaluate(
        """() => {
          const absolute = (value) => { if (!value) return null; try { return new URL(value, document.baseURI).href; } catch (_) { return null; } };
          const metas = [
            ['meta[property="og:image:secure_url"]','content'],
            ['meta[property="og:image"]','content'],
            ['meta[name="twitter:image"]','content'],
            ['meta[property="twitter:image"]','content']
          ].map(([selector, attr]) => absolute(document.querySelector(selector)?.getAttribute(attr))).filter(Boolean);
          const images = [...document.images].map((img, index) => {
            const rect = img.getBoundingClientRect();
            return { index, url: absolute(img.currentSrc || img.src), naturalWidth: img.naturalWidth || 0,
              naturalHeight: img.naturalHeight || 0, visibleWidth: Math.max(0, rect.width), visibleHeight: Math.max(0, rect.height) };
          }).filter(item => item.url && !item.url.startsWith('data:') && !item.url.endsWith('.svg'))
            .sort((a,b) => (b.visibleWidth*b.visibleHeight + b.naturalWidth*b.naturalHeight*.15) - (a.visibleWidth*a.visibleHeight + a.naturalWidth*a.naturalHeight*.15));
          const visibleImageArea = images.reduce((sum, item) => sum + item.visibleWidth * item.visibleHeight, 0);
          return { metas, images: images.slice(0, 18), bodyText: (document.body?.innerText || '').slice(0, 12000),
            title: document.title || '', visibleImageAreaRatio: visibleImageArea / Math.max(1, innerWidth * innerHeight) };
        }"""
    )


def download_image(context, url: str, referer: str, timeout_ms: int) -> tuple[Image.Image | None, str | None]:
    try:
        response = context.request.get(
            url,
            timeout=timeout_ms,
            headers={"Referer": referer, "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"},
        )
        if not response.ok:
            return None, f"HTTP {response.status}"
        declared_size = int(response.headers.get("content-length", "0") or 0)
        if declared_size > MAX_DOWNLOAD_BYTES:
            return None, f"image response too large: {declared_size} bytes"
        data = response.body()
        if len(data) > MAX_DOWNLOAD_BYTES:
            return None, f"image body too large: {len(data)} bytes"
        image = Image.open(BytesIO(data))
        width, height = image.size
        if width * height > MAX_SOURCE_PIXELS or max(width, height) > MAX_SOURCE_EDGE:
            return None, f"image dimensions too large: {width}x{height}"
        if image.format == "JPEG":
            image.draft("RGB", (2560, 1440))
        image.load()
        image.thumbnail((2560, 1440), Image.Resampling.LANCZOS)
        return image, None
    except Exception as exc:
        return None, str(exc)


def acquire_one(context, page, item: dict, category: dict, rank: int, output: Path, timeout_ms: int) -> dict:
    attempts: list[dict] = []
    for source_url in page_urls(item):
        try:
            page.goto(source_url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(900)
            snapshot = extract_candidates(page)
        except PlaywrightError as exc:
            attempts.append({"pageUrl": source_url, "status": "navigation-error", "error": str(exc)})
            continue
        body = (snapshot.get("bodyText") or "").lower()
        marker = next((value for value in BLOCK_MARKERS if value in body), None)
        if marker:
            attempts.append({"pageUrl": source_url, "status": "blocked-or-administrative", "marker": marker})

        page.evaluate(
            """() => {
              const vw = innerWidth, vh = innerHeight;
              for (const el of [...document.body.querySelectorAll('*')]) {
                const style = getComputedStyle(el), rect = el.getBoundingClientRect();
                const ratio = Math.max(0, rect.width) * Math.max(0, rect.height) / Math.max(1, vw * vh);
                const textLength = (el.innerText || '').trim().length;
                if ((style.position === 'fixed' || style.position === 'sticky') && ratio > .22 && textLength > 24) {
                  el.style.setProperty('display', 'none', 'important');
                }
              }
            }"""
        )
        snapshot = extract_candidates(page)

        candidates: list[tuple[str, str]] = []
        for url in snapshot.get("metas", []):
            candidates.append(("official-meta-image", url))
        for row in snapshot.get("images", []):
            if row.get("naturalWidth", 0) >= 640 and row.get("naturalHeight", 0) >= 320:
                candidates.append(("official-hero-image", row["url"]))
        seen: set[str] = set()
        for method, image_url in candidates:
            if image_url in seen:
                continue
            seen.add(image_url)
            image, error = download_image(context, image_url, source_url, timeout_ms)
            if image is None:
                attempts.append({"pageUrl": source_url, "imageUrl": image_url, "status": "image-download-error", "error": error})
                continue
            ok, metrics = acceptable_image(image)
            attempts.append({"pageUrl": source_url, "imageUrl": image_url, "method": method, "status": "accepted" if ok else "weak-image", "metrics": metrics})
            if ok:
                final_metrics = save_cover(image, output)
                return {
                    "rank": rank,
                    "itemId": item.get("id"),
                    "name": item["name"],
                    "status": "strong",
                    "method": method,
                    "pageUrl": source_url,
                    "imageUrl": image_url,
                    "output": str(output),
                    "sha256": sha256(output),
                    "metrics": final_metrics,
                    "rightsStatus": "official-source-private-family-planning-use",
                    "attribution": f"Official source image for {item['name']}; verify reuse terms before public publication.",
                    "attempts": attempts,
                }

        # A maintenance or access notice can still expose a useful official
        # OpenGraph/hero image. Never use the page screenshot in that case,
        # but keep the image-first candidates above.
        if not marker and snapshot.get("visibleImageAreaRatio", 0) >= 0.30:
            try:
                page.screenshot(path=str(output), full_page=False)
                image = Image.open(output)
                ok, metrics = acceptable_image(image)
                attempts.append({"pageUrl": source_url, "method": "official-visual-page", "status": "accepted" if ok else "weak-page", "metrics": metrics})
                if ok:
                    save_cover(image, output)
                    return {
                        "rank": rank,
                        "itemId": item.get("id"),
                        "name": item["name"],
                        "status": "strong",
                        "method": "official-visual-page",
                        "pageUrl": source_url,
                        "imageUrl": None,
                        "output": str(output),
                        "sha256": sha256(output),
                        "metrics": image_metrics(Image.open(output)),
                        "rightsStatus": "official-source-private-family-planning-use",
                        "attribution": f"Official visual page for {item['name']}; private family-planning use.",
                        "attempts": attempts,
                    }
            except Exception as exc:
                attempts.append({"pageUrl": source_url, "status": "page-screenshot-error", "error": str(exc)})

    reason = attempts[-1].get("status", "no image candidate") if attempts else "no source URL"
    soft_fallback(output, item, category, rank, reason)
    return {
        "rank": rank,
        "itemId": item.get("id"),
        "name": item["name"],
        "status": "fallback",
        "method": "soft-project-card",
        "pageUrl": page_urls(item)[0] if page_urls(item) else None,
        "imageUrl": None,
        "output": str(output),
        "sha256": sha256(output),
        "metrics": image_metrics(Image.open(output)),
        "rightsStatus": "project-generated",
        "attribution": "Holiday 2026 project-generated fallback card.",
        "attempts": attempts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire official image-first visuals for Holiday 2026.")
    parser.add_argument("--category", action="append", help="Category ID or video slug; repeat to select multiple.")
    parser.add_argument("--timeout-ms", type=int, default=12_000)
    parser.add_argument("--max-rank", type=int, default=8)
    parser.add_argument("--min-strong", type=int, default=6)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    categories = json.loads((PROJECT / "source" / "categories.json").read_text(encoding="utf-8"))
    ranked = json.loads((PROJECT / "artifacts" / "data" / "ranked-places.json").read_text(encoding="utf-8"))
    requested = set(args.category or [])
    if requested:
        categories = [item for item in categories if item["id"] in requested or item["video_slug"] in requested]
        found = {item["id"] for item in categories} | {item["video_slug"] for item in categories}
        missing = requested - found
        if missing:
            raise SystemExit("Unknown categories: " + ", ".join(sorted(missing)))

    results: list[dict] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1,
            locale="en-US",
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
        )
        page = context.new_page()
        for category in categories:
            items = [item for item in ranked if item.get("category_id") == category["id"] and item.get("selected")]
            items.sort(key=lambda item: int(item.get("rank") or 9999))
            output_dir = PACKAGES / category["video_slug"] / "artifacts" / "source-images"
            output_dir.mkdir(parents=True, exist_ok=True)
            rows: list[dict] = []
            print(f"Capturing image-first sources: {category['video_slug']}", flush=True)
            for rank, item in enumerate(items[: args.max_rank], start=1):
                output = output_dir / f"source-rank-{rank:02d}.png"
                report_path = output_dir / f"source-rank-{rank:02d}.json"
                if output.exists() and report_path.exists() and not args.force:
                    cached = json.loads(report_path.read_text(encoding="utf-8"))
                    identity_matches = (
                        cached.get("itemId") == item.get("id")
                        and cached.get("name") == item.get("name")
                        and int(cached.get("rank") or -1) == rank
                    )
                    if identity_matches:
                        row = cached
                    else:
                        row = acquire_one(context, page, item, category, rank, output, args.timeout_ms)
                        report_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
                else:
                    row = acquire_one(context, page, item, category, rank, output, args.timeout_ms)
                    report_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
                rows.append(row)
                print(f"  rank {rank}: {row['status']} via {row['method']}", flush=True)
            strong = sum(1 for row in rows if row["status"] == "strong")
            unique = len({row["sha256"] for row in rows})
            category_report = {
                "schemaVersion": 2,
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "categoryId": category["id"],
                "videoSlug": category["video_slug"],
                "ok": strong >= args.min_strong and unique >= args.min_strong,
                "strongImageCount": strong,
                "fallbackCount": len(rows) - strong,
                "uniqueImageHashes": unique,
                "minimumStrongImages": args.min_strong,
                "images": rows,
            }
            (output_dir / "source-image-acquisition.json").write_text(json.dumps(category_report, indent=2) + "\n", encoding="utf-8")
            results.append(category_report)
        context.close()
        browser.close()

    summary = {
        "schemaVersion": 2,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "ok": all(row["ok"] for row in results),
        "categoryCount": len(results),
        "strongImageCount": sum(row["strongImageCount"] for row in results),
        "fallbackCount": sum(row["fallbackCount"] for row in results),
        "results": [
            {
                "videoSlug": row["videoSlug"],
                "ok": row["ok"],
                "strongImageCount": row["strongImageCount"],
                "fallbackCount": row["fallbackCount"],
                "uniqueImageHashes": row["uniqueImageHashes"],
            }
            for row in results
        ],
    }
    output = PROJECT / "artifacts" / "reviews" / "source-image-series-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
