#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


def parse_viewport(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value.strip().lower())
    if not match:
        raise argparse.ArgumentTypeError("viewport must use WIDTHxHEIGHT, for example 1440x1100")
    width, height = int(match.group(1)), int(match.group(2))
    if width < 320 or height < 320:
        raise argparse.ArgumentTypeError("viewport dimensions must be at least 320 pixels")
    return width, height


def source_to_url(source: str) -> str:
    if re.match(r"^https?://", source) or source.startswith("file://"):
        return source
    path = Path(source).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Input HTML not found: {path}")
    return path.as_uri()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the D3 animated SVG examples gallery in a real browser.")
    parser.add_argument("input", help="Gallery HTML file, file URL, or HTTP URL")
    parser.add_argument(
        "--expected",
        type=int,
        default=0,
        help="Expected number of example panels. When omitted, read document.body.dataset.exampleCount.",
    )
    parser.add_argument("--wait-ms", type=int, default=1800, help="Extra time after load before inspection")
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--viewport", type=parse_viewport, default=parse_viewport("1440x1100"))
    parser.add_argument("--screenshot", type=Path, help="Optional full-page screenshot path")
    args = parser.parse_args()

    url = source_to_url(args.input)
    width, height = args.viewport
    console_errors: list[str] = []
    page_errors: list[str] = []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height})
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.goto(url, wait_until="load", timeout=args.timeout_ms)
            page.wait_for_timeout(max(args.wait_ms, 0))

            expected = args.expected
            if expected <= 0:
                raw_expected = page.locator("body").get_attribute("data-example-count")
                if not raw_expected:
                    raise SystemExit("No --expected value and page did not expose body[data-example-count].")
                expected = int(raw_expected)

            examples = page.locator("[data-example]")
            example_count = examples.count()
            svg_count = page.locator("[data-example] svg").count()
            if example_count != expected:
                raise SystemExit(f"Expected {expected} examples, found {example_count}.")
            if svg_count != expected:
                raise SystemExit(f"Expected {expected} SVGs, found {svg_count}.")

            id_report = page.evaluate(
                """() => {
                    const ids = Array.from(document.querySelectorAll("[id]"), node => node.id).filter(Boolean);
                    const seen = new Set();
                    const duplicates = new Set();
                    for (const id of ids) {
                        if (seen.has(id)) duplicates.add(id);
                        seen.add(id);
                    }
                    const mismatches = Array.from(document.querySelectorAll("[data-example]")).flatMap(card => {
                        const exampleId = card.getAttribute("data-example");
                        const svg = card.querySelector("svg");
                        return svg && svg.id === exampleId ? [] : [{ exampleId, svgId: svg ? svg.id : null }];
                    });
                    return { duplicates: Array.from(duplicates), mismatches };
                }"""
            )
            if id_report["duplicates"]:
                raise SystemExit(f"Duplicate DOM IDs found in gallery: {id_report['duplicates']}")
            if id_report["mismatches"]:
                raise SystemExit(f"Card/SVG ID mismatches found in gallery: {id_report['mismatches']}")

            pattern_report = page.evaluate(
                """() => {
                    const cards = Array.from(document.querySelectorAll("[data-example]"));
                    const seen = new Set();
                    const duplicates = new Set();
                    const missing = [];
                    const mismatches = [];
                    const invalid = [];
                    for (const card of cards) {
                        const exampleId = card.getAttribute("data-example");
                        const patternId = card.getAttribute("data-pattern-id");
                        const svgPatternId = card.querySelector("svg")?.getAttribute("data-pattern-id");
                        if (!patternId) {
                            missing.push(exampleId);
                            continue;
                        }
                        if (!/^[a-z0-9][a-z0-9-]*$/.test(patternId)) {
                            invalid.push({ exampleId, patternId });
                        }
                        if (seen.has(patternId)) duplicates.add(patternId);
                        seen.add(patternId);
                        if (card.id !== patternId || svgPatternId !== patternId) {
                            mismatches.push({ exampleId, cardId: card.id, patternId, svgPatternId });
                        }
                    }
                    return {
                        count: seen.size,
                        duplicates: Array.from(duplicates),
                        missing,
                        mismatches,
                        invalid
                    };
                }"""
            )
            if pattern_report["missing"]:
                raise SystemExit(f"Example cards missing data-pattern-id: {pattern_report['missing']}")
            if pattern_report["invalid"]:
                raise SystemExit(f"Invalid pattern IDs found: {pattern_report['invalid']}")
            if pattern_report["duplicates"]:
                raise SystemExit(f"Duplicate pattern IDs found: {pattern_report['duplicates']}")
            if pattern_report["mismatches"]:
                raise SystemExit(f"Pattern ID mismatches found: {pattern_report['mismatches']}")
            if pattern_report["count"] != expected:
                raise SystemExit(f"Expected {expected} unique pattern IDs, found {pattern_report['count']}.")
            pattern_id_count = pattern_report["count"]

            reports = page.locator("[data-example] svg").evaluate_all(
                """svgs => svgs.map(svg => {
                    const box = svg.getBoundingClientRect();
                    return {
                        id: svg.id,
                        width: box.width,
                        height: box.height,
                        elementCount: svg.querySelectorAll("*").length,
                        textLength: (svg.textContent || "").trim().length,
                        animationCount: svg.querySelectorAll("animate, animateMotion, animateTransform").length
                    };
                })"""
            )

            bad = [
                item for item in reports
                if item["width"] <= 0 or item["height"] <= 0 or item["elementCount"] < 10
            ]
            if bad:
                raise SystemExit(f"SVG panels failed size/content checks: {bad}")

            replay_buttons = page.locator("[data-example] [data-replay]")
            replay_button_count = replay_buttons.count()
            if replay_button_count != expected:
                raise SystemExit(f"Expected {expected} per-card replay buttons, found {replay_button_count}.")

            sample_indexes = sorted(set([0, expected // 2, expected - 1]))
            replay_reports = []
            for index in sample_indexes:
                card = examples.nth(index)
                example_id = card.get_attribute("data-example")
                if not example_id:
                    raise SystemExit(f"Example card at index {index} is missing data-example.")
                button = card.locator("[data-replay]")
                if button.count() != 1:
                    raise SystemExit(f"Expected one replay button for {example_id}, found {button.count()}.")
                target_id = button.get_attribute("data-replay")
                if target_id != example_id:
                    raise SystemExit(f"Replay target mismatch for {example_id}: button targets {target_id}.")

                button.wait_for(state="visible", timeout=args.timeout_ms)
                render_pass_before = card.get_attribute("data-render-pass")
                button.click()
                page.wait_for_timeout(80)
                render_pass_after = card.get_attribute("data-render-pass")
                if render_pass_before == render_pass_after:
                    raise SystemExit(f"Replay button for {example_id} did not trigger a new render pass.")

                timeline_start = card.locator("svg").evaluate(
                    """svg => ({
                        currentTime: typeof svg.getCurrentTime === "function" ? svg.getCurrentTime() : null,
                        replayState: svg.closest("[data-example]")?.getAttribute("data-replay-state") || null
                    })"""
                )
                if timeline_start["replayState"] != "running":
                    raise SystemExit(f"Replay button for {example_id} did not expose running replay state.")
                if timeline_start["currentTime"] is not None and timeline_start["currentTime"] > 0.35:
                    raise SystemExit(
                        f"Replay button for {example_id} did not reset SVG timeline: {timeline_start}"
                    )

                page.wait_for_timeout(420)
                timeline_after = card.locator("svg").evaluate(
                    """svg => ({
                        currentTime: typeof svg.getCurrentTime === "function" ? svg.getCurrentTime() : null
                    })"""
                )
                if (
                    timeline_start["currentTime"] is not None
                    and timeline_after["currentTime"] is not None
                    and timeline_after["currentTime"] <= timeline_start["currentTime"]
                ):
                    raise SystemExit(
                        f"Replay button for {example_id} reset the timeline but it did not advance: "
                        f"{timeline_start} -> {timeline_after}"
                    )

                replay_report = card.locator("svg").evaluate(
                    """svg => ({
                        id: svg.id,
                        elementCount: svg.querySelectorAll("*").length,
                        animationCount: svg.querySelectorAll("animate, animateMotion, animateTransform").length
                    })"""
                )
                replay_reports.append(replay_report)
                if replay_report["animationCount"] == 0 or replay_report["elementCount"] < 10:
                    raise SystemExit(f"Replay left {example_id} without expected animated SVG content: {replay_report}")

            if args.screenshot:
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshot.resolve()), full_page=True)

            browser.close()
    except PlaywrightError as error:
        print(f"[ERROR] Playwright failed: {error}", file=sys.stderr)
        return 1

    if console_errors or page_errors:
        print("[ERROR] Browser reported errors while rendering the D3 gallery:", file=sys.stderr)
        for item in console_errors + page_errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    print(f"Verified examples: {example_count}")
    print(f"Verified unique pattern IDs: {pattern_id_count}")
    print(f"Verified per-card replay buttons: {replay_button_count}; sampled {len(replay_reports)}")
    for item in reports:
        print(
            f"- {item['id']}: {item['width']:.0f}x{item['height']:.0f}, "
            f"{item['elementCount']} elements, {item['animationCount']} animation nodes"
        )
    if args.screenshot:
        print(f"Screenshot: {args.screenshot.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
