#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///
"""Export every SVG from the D3 gallery as standalone source fixtures."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright


def source_to_url(source: str) -> str:
    if re.match(r"^https?://", source) or source.startswith("file://"):
        return source
    path = Path(source).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Input HTML not found: {path}")
    return path.as_uri()


def ensure_svg_document(markup: str) -> str:
    markup = markup.strip()
    if not markup.startswith("<svg"):
        raise SystemExit("Exported element is not an SVG element.")
    start_tag = markup.split(">", 1)[0]
    if "xmlns=" not in start_tag:
        markup = markup.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + markup + "\n"


def safe_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "svg"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Gallery HTML file, file URL, or HTTP URL.")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory for exported SVG fixtures.")
    parser.add_argument("--manifest", type=Path, help="Optional JSON manifest path.")
    parser.add_argument("--expected", type=int, help="Expected SVG/card count.")
    parser.add_argument("--wait-ms", type=int, default=4500)
    parser.add_argument("--viewport", default="1440x1200", help="Browser viewport as WIDTHxHEIGHT.")
    args = parser.parse_args()

    viewport_match = re.fullmatch(r"(\d+)x(\d+)", args.viewport.strip().lower())
    if not viewport_match:
        raise SystemExit("--viewport must use WIDTHxHEIGHT")
    viewport = {"width": int(viewport_match.group(1)), "height": int(viewport_match.group(2))}

    args.out_dir.mkdir(parents=True, exist_ok=True)
    url = source_to_url(args.input)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport=viewport)
        page.goto(url, wait_until="load")
        page.wait_for_timeout(max(args.wait_ms, 0))
        page.wait_for_selector("[data-example] svg")
        exports = page.evaluate(
            """() => Array.from(document.querySelectorAll("[data-example]")).map((card, index) => {
                const svg = card.querySelector("svg");
                const title = card.querySelector("h2")?.textContent?.trim() || "";
                const patternId = card.getAttribute("data-pattern-id") || svg?.getAttribute("data-pattern-id") || "";
                return {
                  index,
                  id: card.getAttribute("data-example") || svg?.id || `example-${index + 1}`,
                  patternId,
                  title,
                  svgId: svg?.id || "",
                  markup: svg?.outerHTML || "",
                  elementCount: svg ? svg.querySelectorAll("*").length : 0,
                  animationCount: svg ? svg.querySelectorAll("animate, animateMotion, animateTransform, set").length : 0,
                  textLength: svg ? (svg.textContent || "").trim().length : 0
                };
            })"""
        )
        browser.close()

    if args.expected is not None and len(exports) != args.expected:
        raise SystemExit(f"Expected {args.expected} SVGs but found {len(exports)}")

    manifest = []
    for item in exports:
        if not item["markup"]:
            raise SystemExit(f"Card {item['id']} did not contain SVG markup")
        file_name = f"{item['index'] + 1:03d}-{safe_name(item['id'])}.svg"
        output_path = args.out_dir / file_name
        output_path.write_text(ensure_svg_document(item["markup"]), encoding="utf-8")
        manifest.append(
            {
                "index": item["index"] + 1,
                "id": item["id"],
                "patternId": item["patternId"],
                "title": item["title"],
                "svgId": item["svgId"],
                "file": str(output_path.resolve()),
                "relativeFile": file_name,
                "elementCount": item["elementCount"],
                "animationCount": item["animationCount"],
                "textLength": item["textLength"],
            }
        )

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps({"count": len(manifest), "items": manifest}, indent=2), encoding="utf-8")

    print(f"Exported SVGs: {len(manifest)}")
    print(f"Output: {args.out_dir.resolve()}")
    if args.manifest:
        print(f"Manifest: {args.manifest.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
