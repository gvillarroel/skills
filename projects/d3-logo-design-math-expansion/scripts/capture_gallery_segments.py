#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

"""Capture inspectable desktop and mobile segments from the mathematical logo batch."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "skills/d3-logo-design/assets/examples/d3-logo-design/index.html"
OUTPUT = ROOT / "projects/d3-logo-design-math-expansion/artifacts/screenshots"


def capture_viewport(page, label: str, width: int, height: int) -> list[str]:
    page.set_viewport_size({"width": width, "height": height})
    page.goto(SOURCE.resolve().as_uri(), wait_until="load")
    page.wait_for_selector('[data-example-id="reuleaux-body"] svg')
    page.evaluate("() => document.fonts && document.fonts.ready")
    outputs: list[str] = []
    for start in range(60, 90, 5):
        end = start + 5
        page.evaluate(
            """([start, end]) => {
              document.querySelectorAll('[data-example]').forEach((card, index) => {
                card.style.display = index >= start && index < end ? '' : 'none';
              });
            }""",
            [start, end],
        )
        page.wait_for_timeout(80)
        output = OUTPUT / f"{label}-{start + 1:02d}-{end:02d}.png"
        page.locator("#logo-gallery").screenshot(path=str(output), animations="disabled", timeout=120_000)
        outputs.append(str(output.relative_to(ROOT)))
    return outputs


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        desktop = capture_viewport(page, "desktop", 1440, 1000)
        mobile = capture_viewport(page, "mobile", 390, 844)
        browser.close()
    report = {"source": str(SOURCE.relative_to(ROOT)), "desktop": desktop, "mobile": mobile}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
