#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.64.1", "pillow==13.0.0"]
# ///
"""Verify a local xy HTML export offline and save browser evidence.

Example: uv run --script verify_html.py --html results/chart.html
         --report results/browser.json --screenshot results/browser.png
         --label "My chart" --label "Time"
"""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright


def checked_paths(args):
    paths = [Path(value).resolve() for value in (args.html, args.report, args.screenshot)]
    source, report, screenshot = paths
    bundle = Path(__file__).resolve().parents[1]
    if len(set(paths)) != 3:
        raise ValueError("HTML input, report, and screenshot paths must be different.")
    for output in (report, screenshot):
        if output.is_relative_to(bundle):
            raise ValueError(f"Write outputs outside the read-only skill bundle: {output}")
        if output.exists() and not output.is_file():
            raise ValueError(f"Output path is not a regular file: {output}")
    return source, report, screenshot


def launch_browser(playwright, args, result):
    channels = [args.browser_channel] if args.browser_channel != "auto" else ["msedge", "chrome", "chromium"]
    attempts = [{"executable_path": args.browser_executable}] if args.browser_executable else [
        {} if channel == "chromium" else {"channel": channel} for channel in channels
    ]
    for options in attempts:
        try:
            browser = playwright.chromium.launch(headless=True, chromium_sandbox=True,
                                                 args=["--allow-file-access-from-files"], **options)
            result["browser"] = options.get("channel", options.get("executable_path", "bundled chromium"))
            return browser
        except Exception as error:
            result["browser_launch_attempts"].append({"browser": options, "error": str(error).splitlines()[0]})
    raise RuntimeError("No requested browser could launch. Install Edge, Chrome, or Playwright Chromium, or provide --browser-executable.")


def image_stats(data):
    with Image.open(io.BytesIO(data)) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        deviation = max(ImageStat.Stat(rgb).stddev)
        colors = len(rgb.resize((100, 100)).getcolors(10000) or [])
        return {"width": width, "height": height, "sample_colors": colors, "stddev": round(deviation, 3),
                "nonblank": width >= 100 and height >= 100 and deviation >= 3 and colors >= 10}


def visible_label(page, label):
    for element in page.get_by_text(label, exact=False).all():
        if element.is_visible() and element.evaluate("""element => {
            for (let node = element; node; node = node.parentElement) {
                const style = getComputedStyle(node);
                if (style.display === 'none' || style.visibility !== 'visible' ||
                    Number(style.opacity) === 0) return false;
            }
            const box = element.getBoundingClientRect();
            return box.width > 0 && box.height > 0;
        }"""):
            return True
    return False


def verify(source, screenshot, args, result):
    with sync_playwright() as playwright:
        browser = launch_browser(playwright, args, result)
        try:
            context = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
            page = context.new_page()

            def route_request(route):
                url = route.request.url
                if url.startswith(("https://", "http://")):
                    result["blocked_requests"].append(url)
                    route.abort()
                else:
                    route.continue_()

            def console_message(message):
                text = message.text
                if message.type == "warning" and "Automatic fallback to software WebGL has been deprecated" in text and "swiftshader" in text.lower():
                    result["expected_swiftshader_warnings"].append(text)
                elif message.type == "error":
                    result["console_errors"].append(text)

            context.route("**/*", route_request)
            page.on("console", console_message)
            page.on("pageerror", lambda error: result["page_errors"].append(str(error)))
            page.goto(source.as_uri(), wait_until="load", timeout=45000)
            page.wait_for_selector("canvas", state="visible", timeout=30000)
            page.wait_for_timeout(700)
            canvases = [(canvas, canvas.bounding_box()) for canvas in page.locator("canvas").all()]
            visible = [(canvas, box) for canvas, box in canvases if box and box["width"] >= 100 and box["height"] >= 100]
            if not visible:
                raise ValueError("No visible chart canvas of at least 100 by 100 pixels was found.")
            canvas, box = max(visible, key=lambda item: item[1]["width"] * item[1]["height"])
            result["canvas"] = image_stats(canvas.screenshot(type="png"))
            result["labels"] = {label: visible_label(page, label) for label in args.label}
            page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            page.mouse.wheel(0, -120)
            page.wait_for_timeout(300)
            result["interaction"] = {"action": "wheel", "dispatched": True, "scope": "Basic pointer delivery and JavaScript error check."}
            screenshot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot), type="png", full_page=True)
            result["screenshot"] = str(screenshot)
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--screenshot", required=True)
    parser.add_argument("--label", action="append", default=[], help="Expected visible text; repeat for multiple labels.")
    parser.add_argument("--browser-channel", choices=("auto", "msedge", "chrome", "chromium"), default="auto")
    parser.add_argument("--browser-executable", help="Explicit Chromium-based browser executable.")
    args = parser.parse_args()
    result = {"schema_version": 1, "passed": False, "browser_launch_attempts": [], "blocked_requests": [],
              "console_errors": [], "page_errors": [], "expected_swiftshader_warnings": [], "errors": []}
    try:
        source, report, screenshot = checked_paths(args)
    except Exception as error:
        result["errors"].append({"stage": "paths", "message": str(error)})
        print(json.dumps(result, ensure_ascii=False))
        raise SystemExit(1)
    result["html"] = str(source)
    try:
        if not source.is_file():
            raise ValueError(f"HTML input does not exist: {source}")
        verify(source, screenshot, args, result)
        if result["blocked_requests"]:
            result["errors"].append({"stage": "offline", "message": "The export attempted HTTP(S) requests."})
        if result["console_errors"] or result["page_errors"]:
            result["errors"].append({"stage": "javascript", "message": "The page reported JavaScript or console errors."})
        if not result.get("canvas", {}).get("nonblank"):
            result["errors"].append({"stage": "canvas", "message": "The chart canvas appears blank or too small."})
        missing = [label for label, present in result.get("labels", {}).items() if not present]
        if missing:
            result["errors"].append({"stage": "labels", "message": "Expected visible labels are missing.", "labels": missing})
    except Exception as error:
        result["errors"].append({"stage": "browser", "message": str(error)})
    result["passed"] = not result["errors"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
