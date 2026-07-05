#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.45.0"]
# ///

from __future__ import annotations

import argparse
import io
import json
import statistics
import sys
from pathlib import Path
from typing import Any

from PIL import Image

from audit_metro_rendered_frames import (
    goto_with_retry,
    launch_chromium,
    resolve_config,
    sample_times,
    serve_directory,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a Metro mute-test by hiding rendered text and verifying that visual marks still carry motion."
    )
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-package", type=Path, help="Optional source-package.json for video id, duration, and format.")
    parser.add_argument("--video-id", help="renderConceptFrame video id. Defaults to source-package outputId.")
    parser.add_argument("--duration", type=float, help="Duration in seconds. Defaults to source-package durationSeconds.")
    parser.add_argument("--samples", type=int, default=6)
    parser.add_argument("--width", type=int, help="Viewport width. Defaults to source-package format.width or 1280.")
    parser.add_argument("--height", type=int, help="Viewport height. Defaults to source-package format.height or 720.")
    parser.add_argument("--selector", default="#stage")
    parser.add_argument("--min-hidden-changing-pairs", type=int, default=3)
    parser.add_argument("--min-median-hidden-change-ratio", type=float, default=0.0012)
    parser.add_argument("--min-hidden-to-full-change-ratio", type=float, default=0.35)
    parser.add_argument("--min-hidden-nonbackground-ratio", type=float, default=0.08)
    parser.add_argument("--min-hidden-color-buckets", type=int, default=5)
    parser.add_argument("--min-hidden-mark-count", type=int, default=24)
    parser.add_argument("--min-hidden-zone-elements", type=int, default=5)
    parser.add_argument("--min-hidden-gray-levels", type=int, default=4)
    parser.add_argument("--change-threshold", type=int, default=8)
    parser.add_argument("--install-browser", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--launch-timeout-ms", type=int, default=8_000)
    return parser.parse_args()


def load_image(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")


def image_pixels(image: Image.Image) -> list[tuple[int, int, int]]:
    if hasattr(image, "get_flattened_data"):
        return list(image.get_flattened_data())  # type: ignore[attr-defined]
    return list(image.getdata())


def quantized_bucket(pixel: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(channel // 32 for channel in pixel)


def image_metrics(image: Image.Image) -> dict[str, Any]:
    pixels = image_pixels(image)
    if not pixels:
        return {"colorBuckets": 0, "nonbackgroundRatio": 0.0}
    buckets = {quantized_bucket(pixel) for pixel in pixels}
    background = max(set(pixels), key=pixels.count)
    nonbackground = 0
    for pixel in pixels:
        if sum(abs(pixel[index] - background[index]) for index in range(3)) > 18:
            nonbackground += 1
    return {
        "colorBuckets": len(buckets),
        "backgroundRgb": background,
        "nonbackgroundRatio": nonbackground / len(pixels),
    }


def image_change_ratio(before: Image.Image, after: Image.Image, threshold: int) -> float:
    if before.size != after.size:
        after = after.resize(before.size)
    before_pixels = image_pixels(before)
    after_pixels = image_pixels(after)
    if not before_pixels:
        return 0.0
    changed = 0
    for left, right in zip(before_pixels, after_pixels):
        if max(abs(left[index] - right[index]) for index in range(3)) > threshold:
            changed += 1
    return changed / len(before_pixels)


def median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def collect_dom_metrics(page: Any, selector: str) -> dict[str, Any]:
    return page.evaluate(
        """
        ({ selector }) => {
          const stage = document.querySelector(selector) || document.querySelector("svg");
          if (!stage) throw new Error(`No stage matched selector ${selector}`);
          const visible = (node) => {
            const style = window.getComputedStyle(node);
            if (style.display === "none" || style.visibility === "hidden") return false;
            if (Number(style.opacity || "1") <= 0.01) return false;
            const box = node.getBoundingClientRect();
            const tag = node.tagName.toLowerCase();
            if (["line", "path", "polyline"].includes(tag)) {
              const stroke = node.getAttribute("stroke") || style.stroke;
              return stroke && stroke !== "none" && stroke !== "transparent";
            }
            return box.width > 0.5 && box.height > 0.5;
          };
          const marks = Array.from(stage.querySelectorAll("rect,line,path,polyline,polygon,circle,ellipse"))
            .filter(visible);
          const zones = marks.filter((node) => node.getAttribute("data-zone-id"));
          const fills = marks
            .map((node) => node.getAttribute("fill") || window.getComputedStyle(node).fill)
            .filter((fill) => fill && fill !== "none" && fill !== "transparent");
          const grayFills = fills.filter((fill) => {
            const raw = String(fill).toLowerCase().trim();
            if (/^#[0-9a-f]{6}$/.test(raw)) {
              const r = parseInt(raw.slice(1, 3), 16);
              const g = parseInt(raw.slice(3, 5), 16);
              const b = parseInt(raw.slice(5, 7), 16);
              return Math.max(r, g, b) - Math.min(r, g, b) <= 3;
            }
            const match = raw.match(/^rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)$/);
            if (!match) return false;
            const values = match.slice(1).map(Number);
            return Math.max(...values) - Math.min(...values) <= 3;
          });
          const grayLevels = new Set(grayFills.map((fill) => String(fill).toLowerCase().trim()));
          return {
            markCount: marks.length,
            zoneElementCount: zones.length,
            zoneIdCount: new Set(zones.map((node) => node.getAttribute("data-zone-id"))).size,
            grayLevelCount: grayLevels.size,
          };
        }
        """,
        {"selector": selector},
    )


def hide_text(page: Any, selector: str) -> None:
    page.evaluate(
        """
        ({ selector }) => {
          const stage = document.querySelector(selector) || document.querySelector("svg");
          if (!stage) throw new Error(`No stage matched selector ${selector}`);
          Array.from(stage.querySelectorAll("text, foreignObject")).forEach((node) => {
            node.dataset.muteTestVisibility = node.style.visibility || "";
            node.style.visibility = "hidden";
          });
        }
        """,
        {"selector": selector},
    )


def restore_text(page: Any, selector: str) -> None:
    page.evaluate(
        """
        ({ selector }) => {
          const stage = document.querySelector(selector) || document.querySelector("svg");
          if (!stage) return;
          Array.from(stage.querySelectorAll("text, foreignObject")).forEach((node) => {
            node.style.visibility = node.dataset.muteTestVisibility || "";
            delete node.dataset.muteTestVisibility;
          });
        }
        """,
        {"selector": selector},
    )


def sample_mute_frames(
    html: Path,
    times: list[float],
    config: dict[str, Any],
    selector: str,
    install_browser: bool,
    launch_timeout_ms: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise RuntimeError(f"Playwright import failed: {exc}") from exc

    samples: list[dict[str, Any]] = []
    with serve_directory(html.parent) as base_url:
        with sync_playwright() as playwright:
            browser, browser_notes = launch_chromium(
                playwright,
                install_browser=install_browser,
                timeout_ms=launch_timeout_ms,
            )
            try:
                page = browser.new_page(viewport={"width": int(config["width"]), "height": int(config["height"])})
                page.set_default_timeout(10_000)
                page.set_default_navigation_timeout(10_000)
                goto_with_retry(page, f"{base_url}/{html.name}")
                page.wait_for_function("() => typeof window.renderConceptFrame === 'function'", timeout=10_000)
                for index, seconds in enumerate(times):
                    state = page.evaluate(
                        "({ videoId, seconds }) => window.renderConceptFrame(videoId, seconds, { capture: true })",
                        {"videoId": str(config["videoId"]), "seconds": seconds},
                    )
                    clip = page.evaluate(
                        """
                        ({ selector }) => {
                          const stage = document.querySelector(selector) || document.querySelector("svg");
                          if (!stage) throw new Error(`No stage matched selector ${selector}`);
                          const box = stage.getBoundingClientRect();
                          return {
                            x: Math.max(0, box.x),
                            y: Math.max(0, box.y),
                            width: Math.max(1, box.width),
                            height: Math.max(1, box.height),
                          };
                        }
                        """,
                        {"selector": selector},
                    )
                    full_image = load_image(page.screenshot(type="png", clip=clip))
                    hide_text(page, selector)
                    try:
                        dom_metrics = collect_dom_metrics(page, selector)
                        hidden_image = load_image(page.screenshot(type="png", clip=clip))
                    finally:
                        restore_text(page, selector)
                    samples.append(
                        {
                            "sample": index,
                            "seconds": seconds,
                            "state": state if isinstance(state, dict) else {},
                            "fullImage": full_image,
                            "hiddenImage": hidden_image,
                            "fullMetrics": image_metrics(full_image),
                            "hiddenMetrics": image_metrics(hidden_image),
                            "domMetrics": dom_metrics,
                        }
                    )
            finally:
                browser.close()
    return samples, browser_notes


def public_sample(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "sample": sample.get("sample"),
        "seconds": sample.get("seconds"),
        "fullMetrics": sample.get("fullMetrics"),
        "hiddenMetrics": sample.get("hiddenMetrics"),
        "domMetrics": sample.get("domMetrics"),
        "state": sample.get("state"),
    }


def build_findings(report: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if report["hiddenChangingPairs"] < args.min_hidden_changing_pairs:
        findings.append(
            {
                "code": "mute-test-hidden-motion-too-weak",
                "minimum": args.min_hidden_changing_pairs,
                "actual": report["hiddenChangingPairs"],
            }
        )
    if report["medianHiddenChangeRatio"] < args.min_median_hidden_change_ratio:
        findings.append(
            {
                "code": "mute-test-hidden-change-ratio-too-low",
                "minimum": args.min_median_hidden_change_ratio,
                "actual": report["medianHiddenChangeRatio"],
            }
        )
    if report["medianHiddenToFullChangeRatio"] < args.min_hidden_to_full_change_ratio:
        findings.append(
            {
                "code": "mute-test-text-carries-motion",
                "minimum": args.min_hidden_to_full_change_ratio,
                "actual": report["medianHiddenToFullChangeRatio"],
            }
        )
    if report["medianHiddenNonbackgroundRatio"] < args.min_hidden_nonbackground_ratio:
        findings.append(
            {
                "code": "mute-test-hidden-visual-area-too-low",
                "minimum": args.min_hidden_nonbackground_ratio,
                "actual": report["medianHiddenNonbackgroundRatio"],
            }
        )
    if report["minHiddenColorBuckets"] < args.min_hidden_color_buckets:
        findings.append(
            {
                "code": "mute-test-hidden-color-diversity-too-low",
                "minimum": args.min_hidden_color_buckets,
                "actual": report["minHiddenColorBuckets"],
            }
        )
    if report["medianHiddenMarkCount"] < args.min_hidden_mark_count:
        findings.append(
            {
                "code": "mute-test-too-few-hidden-marks",
                "minimum": args.min_hidden_mark_count,
                "actual": report["medianHiddenMarkCount"],
            }
        )
    if report["maxHiddenZoneElementCount"] < args.min_hidden_zone_elements:
        findings.append(
            {
                "code": "mute-test-too-few-zone-elements",
                "minimum": args.min_hidden_zone_elements,
                "actual": report["maxHiddenZoneElementCount"],
            }
        )
    if report["medianHiddenGrayLevelCount"] < args.min_hidden_gray_levels:
        findings.append(
            {
                "code": "mute-test-weak-hidden-gray-hierarchy",
                "minimum": args.min_hidden_gray_levels,
                "actual": report["medianHiddenGrayLevelCount"],
            }
        )
    return findings


def main() -> int:
    args = parse_args()
    html = args.html.resolve()
    if not html.exists():
        print(f"HTML file not found: {html}", file=sys.stderr)
        return 2
    config = resolve_config(args)
    times = sample_times(float(config["duration"]), args.samples)
    samples, browser_notes = sample_mute_frames(
        html,
        times,
        config,
        args.selector,
        args.install_browser,
        args.launch_timeout_ms,
    )
    full_change_ratios: list[float] = []
    hidden_change_ratios: list[float] = []
    hidden_to_full_ratios: list[float] = []
    for left, right in zip(samples, samples[1:]):
        full_change = image_change_ratio(left["fullImage"], right["fullImage"], args.change_threshold)
        hidden_change = image_change_ratio(left["hiddenImage"], right["hiddenImage"], args.change_threshold)
        full_change_ratios.append(full_change)
        hidden_change_ratios.append(hidden_change)
        if full_change > 0.00001:
            hidden_to_full_ratios.append(hidden_change / full_change)
        elif hidden_change > 0.00001:
            hidden_to_full_ratios.append(1.0)
        else:
            hidden_to_full_ratios.append(0.0)

    hidden_nonbackground = [float(item["hiddenMetrics"].get("nonbackgroundRatio") or 0.0) for item in samples]
    hidden_color_buckets = [int(item["hiddenMetrics"].get("colorBuckets") or 0) for item in samples]
    mark_counts = [int(item["domMetrics"].get("markCount") or 0) for item in samples]
    zone_counts = [int(item["domMetrics"].get("zoneElementCount") or 0) for item in samples]
    gray_counts = [int(item["domMetrics"].get("grayLevelCount") or 0) for item in samples]

    report: dict[str, Any] = {
        "passed": False,
        "html": args.html.as_posix(),
        "sourcePackage": args.source_package.as_posix() if args.source_package else None,
        "videoId": config["videoId"],
        "duration": config["duration"],
        "width": config["width"],
        "height": config["height"],
        "samplesRequested": args.samples,
        "sampleTimes": times,
        "browserNotes": browser_notes,
        "fullChangeRatios": full_change_ratios,
        "hiddenChangeRatios": hidden_change_ratios,
        "hiddenToFullChangeRatios": hidden_to_full_ratios,
        "hiddenChangingPairs": sum(1 for value in hidden_change_ratios if value >= args.min_median_hidden_change_ratio),
        "medianFullChangeRatio": median(full_change_ratios),
        "medianHiddenChangeRatio": median(hidden_change_ratios),
        "medianHiddenToFullChangeRatio": median(hidden_to_full_ratios),
        "medianHiddenNonbackgroundRatio": median(hidden_nonbackground),
        "minHiddenColorBuckets": min(hidden_color_buckets, default=0),
        "medianHiddenMarkCount": median([float(value) for value in mark_counts]),
        "maxHiddenZoneElementCount": max(zone_counts, default=0),
        "medianHiddenGrayLevelCount": median([float(value) for value in gray_counts]),
        "thresholds": {
            "minHiddenChangingPairs": args.min_hidden_changing_pairs,
            "minMedianHiddenChangeRatio": args.min_median_hidden_change_ratio,
            "minHiddenToFullChangeRatio": args.min_hidden_to_full_change_ratio,
            "minHiddenNonbackgroundRatio": args.min_hidden_nonbackground_ratio,
            "minHiddenColorBuckets": args.min_hidden_color_buckets,
            "minHiddenMarkCount": args.min_hidden_mark_count,
            "minHiddenZoneElements": args.min_hidden_zone_elements,
            "minHiddenGrayLevels": args.min_hidden_gray_levels,
        },
        "samples": [public_sample(item) for item in samples],
        "findings": [],
    }
    findings = build_findings(report, args)
    report["findings"] = findings
    report["passed"] = not findings
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
