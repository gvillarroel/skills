#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit every D3 gallery card for font consistency, SVG-native animation, "
            "text viewport clipping, and replay stability."
        ),
    )
    parser.add_argument("input", help="Gallery HTML file, file URL, or HTTP URL")
    parser.add_argument("--expected", type=int, default=0, help="Expected number of examples")
    parser.add_argument("--wait-ms", type=int, default=4500, help="Extra time after load before inspection")
    parser.add_argument("--timeout-ms", type=int, default=45000)
    parser.add_argument("--viewport", type=parse_viewport, default=parse_viewport("1440x1100"))
    parser.add_argument("--margin-px", type=float, default=2.0, help="Allowed text overflow margin in CSS pixels")
    parser.add_argument("--min-font-size", type=float, default=7.0, help="Minimum visible SVG text size in px")
    parser.add_argument("--max-font-size", type=float, default=24.0, help="Maximum visible SVG text size in px")
    parser.add_argument("--report", type=Path, help="Optional JSON report path")
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

            audit = page.evaluate(
                """config => {
                    const margin = config.marginPx;
                    const minFont = config.minFontSize;
                    const maxFont = config.maxFontSize;
                    const cards = Array.from(document.querySelectorAll("[data-example]"));

                    function effectiveOpacity(node) {
                        let opacity = 1;
                        let current = node;
                        while (current && current.nodeType === Node.ELEMENT_NODE) {
                            const style = getComputedStyle(current);
                            if (style.display === "none" || style.visibility === "hidden") return 0;
                            const styleOpacity = Number.parseFloat(style.opacity);
                            if (Number.isFinite(styleOpacity)) opacity *= styleOpacity;
                            const attrOpacity = Number.parseFloat(current.getAttribute("opacity"));
                            if (Number.isFinite(attrOpacity)) opacity *= attrOpacity;
                            if (current.tagName && current.tagName.toLowerCase() === "svg") break;
                            current = current.parentNode;
                        }
                        return opacity;
                    }

                    function hasOpenSans(fontFamily) {
                        return /Open Sans|Arial|sans-serif/i.test(fontFamily || "");
                    }

                    function styleSummary(textNodes) {
                        const sizes = textNodes
                            .map(node => Number.parseFloat(getComputedStyle(node).fontSize))
                            .filter(Number.isFinite);
                        const uniqueSizes = Array.from(new Set(sizes.map(size => Number(size.toFixed(2))))).sort((a, b) => a - b);
                        return {
                            minFontSize: sizes.length ? Math.min(...sizes) : null,
                            maxFontSize: sizes.length ? Math.max(...sizes) : null,
                            uniqueFontSizes: uniqueSizes
                        };
                    }

                    const reports = cards.map(card => {
                        const exampleId = card.getAttribute("data-example");
                        const svg = card.querySelector("svg");
                        const svgRect = svg.getBoundingClientRect();
                        const rootStyle = getComputedStyle(svg);
                        const rootFontFamily = rootStyle.fontFamily;
                        const rootFontAttr = svg.getAttribute("font-family") || "";
                        const animationCount = svg.querySelectorAll("animate, animateMotion, animateTransform").length;
                        const elementCount = svg.querySelectorAll("*").length;
                        const visibleTexts = [];
                        const clippedTexts = [];
                        const badFonts = [];
                        const badFontSizes = [];

                        Array.from(svg.querySelectorAll("text")).forEach((text, textIndex) => {
                            const content = (text.textContent || "").trim().replace(/\\s+/g, " ");
                            if (!content) return;
                            if (effectiveOpacity(text) < 0.05) return;
                            const rect = text.getBoundingClientRect();
                            if (rect.width <= 0 && rect.height <= 0) return;
                            const style = getComputedStyle(text);
                            const fontFamily = style.fontFamily;
                            const fontSize = Number.parseFloat(style.fontSize);
                            const item = {
                                index: textIndex,
                                text: content.length > 80 ? `${content.slice(0, 77)}...` : content,
                                fontFamily,
                                fontSize: Number.isFinite(fontSize) ? Number(fontSize.toFixed(2)) : null,
                                box: {
                                    left: Number((rect.left - svgRect.left).toFixed(2)),
                                    top: Number((rect.top - svgRect.top).toFixed(2)),
                                    right: Number((rect.right - svgRect.left).toFixed(2)),
                                    bottom: Number((rect.bottom - svgRect.top).toFixed(2))
                                }
                            };
                            visibleTexts.push(text);
                            if (!hasOpenSans(fontFamily)) {
                                badFonts.push(item);
                            }
                            if (!Number.isFinite(fontSize) || fontSize < minFont || fontSize > maxFont) {
                                badFontSizes.push(item);
                            }
                            if (
                                rect.left < svgRect.left - margin ||
                                rect.top < svgRect.top - margin ||
                                rect.right > svgRect.right + margin ||
                                rect.bottom > svgRect.bottom + margin
                            ) {
                                clippedTexts.push(item);
                            }
                        });

                        return {
                            id: svg.id,
                            exampleId,
                            patternId: card.getAttribute("data-pattern-id"),
                            elementCount,
                            animationCount,
                            textCount: svg.querySelectorAll("text").length,
                            visibleTextCount: visibleTexts.length,
                            rootFontFamily,
                            rootFontAttr,
                            rootFontOk: hasOpenSans(rootFontFamily) && /Open Sans/i.test(rootFontAttr),
                            size: {
                                width: Number(svgRect.width.toFixed(2)),
                                height: Number(svgRect.height.toFixed(2))
                            },
                            styleSummary: styleSummary(visibleTexts),
                            clippedTexts,
                            badFonts,
                            badFontSizes
                        };
                    });

                    return {
                        expected: config.expected,
                        cardCount: cards.length,
                        svgCount: document.querySelectorAll("[data-example] svg").length,
                        reports,
                        failures: {
                            rootFont: reports.filter(item => !item.rootFontOk),
                            noAnimation: reports.filter(item => item.animationCount < 1),
                            clippedText: reports.filter(item => item.clippedTexts.length),
                            badFonts: reports.filter(item => item.badFonts.length),
                            badFontSizes: reports.filter(item => item.badFontSizes.length)
                        }
                    };
                }""",
                {
                    "expected": expected,
                    "marginPx": args.margin_px,
                    "minFontSize": args.min_font_size,
                    "maxFontSize": args.max_font_size,
                },
            )

            if audit["cardCount"] != expected or audit["svgCount"] != expected:
                raise SystemExit(
                    f"Expected {expected} cards/SVGs, found {audit['cardCount']} cards and {audit['svgCount']} SVGs."
                )

            replay_failures = []
            cards = page.locator("[data-example]")
            for index in range(expected):
                card = cards.nth(index)
                example_id = card.get_attribute("data-example")
                before = card.locator("svg").evaluate(
                    """svg => ({
                        id: svg.id,
                        elementCount: svg.querySelectorAll("*").length,
                        animationCount: svg.querySelectorAll("animate, animateMotion, animateTransform").length,
                        renderPass: svg.closest("[data-example]")?.getAttribute("data-render-pass") || null
                    })"""
                )
                button = card.locator("[data-replay]")
                button.click()
                page.wait_for_timeout(90)
                start = card.locator("svg").evaluate(
                    """svg => ({
                        currentTime: typeof svg.getCurrentTime === "function" ? svg.getCurrentTime() : null,
                        replayState: svg.closest("[data-example]")?.getAttribute("data-replay-state") || null,
                        renderPass: svg.closest("[data-example]")?.getAttribute("data-render-pass") || null,
                        elementCount: svg.querySelectorAll("*").length,
                        animationCount: svg.querySelectorAll("animate, animateMotion, animateTransform").length
                    })"""
                )
                page.wait_for_timeout(160)
                after = card.locator("svg").evaluate(
                    """svg => ({
                        currentTime: typeof svg.getCurrentTime === "function" ? svg.getCurrentTime() : null,
                        elementCount: svg.querySelectorAll("*").length,
                        animationCount: svg.querySelectorAll("animate, animateMotion, animateTransform").length
                    })"""
                )

                messages = []
                if start["renderPass"] == before["renderPass"]:
                    messages.append("replay did not change data-render-pass")
                if start["replayState"] != "running":
                    messages.append("replay did not expose running state")
                if start["currentTime"] is not None and start["currentTime"] > 0.4:
                    messages.append(f"timeline did not reset near zero ({start['currentTime']:.3f}s)")
                if (
                    start["currentTime"] is not None
                    and after["currentTime"] is not None
                    and after["currentTime"] <= start["currentTime"]
                ):
                    messages.append("timeline did not advance after replay")
                if start["elementCount"] != before["elementCount"]:
                    messages.append(
                        f"element count changed after replay ({before['elementCount']} -> {start['elementCount']})"
                    )
                if start["animationCount"] != before["animationCount"]:
                    messages.append(
                        f"animation count changed after replay ({before['animationCount']} -> {start['animationCount']})"
                    )
                if after["animationCount"] < 1:
                    messages.append("replay left SVG without animation nodes")
                if messages:
                    replay_failures.append({"index": index, "exampleId": example_id, "messages": messages})

            audit["failures"]["replay"] = replay_failures

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

    if args.report:
        write_json(args.report.resolve(), audit)

    failure_summary = {
        key: len(value)
        for key, value in audit["failures"].items()
    }
    print(f"Audited examples: {audit['cardCount']}")
    print(f"Root font failures: {failure_summary['rootFont']}")
    print(f"Missing animation failures: {failure_summary['noAnimation']}")
    print(f"Clipped text failures: {failure_summary['clippedText']}")
    print(f"Text font-family failures: {failure_summary['badFonts']}")
    print(f"Text font-size failures: {failure_summary['badFontSizes']}")
    print(f"Replay failures: {failure_summary['replay']}")
    if args.report:
        print(f"Report: {args.report.resolve()}")
    if args.screenshot:
        print(f"Screenshot: {args.screenshot.resolve()}")

    failed = {key: value for key, value in audit["failures"].items() if value}
    if failed:
        print("[ERROR] D3 gallery visual audit failed:", file=sys.stderr)
        for key, value in failed.items():
            print(f"- {key}: {len(value)}", file=sys.stderr)
            for item in value[:8]:
                print(f"  {item.get('exampleId') or item.get('id') or item}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
