#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52,<2"]
# ///
"""Verify the source population pyramid keeps age labels clear of both bar series."""

import argparse
import math
from pathlib import Path

from playwright.sync_api import sync_playwright


PROJECT = Path(__file__).resolve().parents[1]
EXAMPLES = PROJECT.parents[1] / "skills/d3/assets/examples"
AGES = ("80+", "70", "60", "50", "40", "30", "20", "10", "0")
GALLERIES = ("d3-animated-svg", "d3-animated-svg-cs1", "d3-animated-svg-colorset2")
COMPOSITION = "d3-composition-symmetry-population-pyramid"

INSPECT = """(svg, [ageSelector, barSelector]) => {
    const box = node => {
        const rect = node.getBoundingClientRect();
        return {left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom};
    };
    return {
        ages: [...svg.querySelectorAll(ageSelector)].map(node => ({text: node.textContent, ...box(node)})),
        bars: [...svg.querySelectorAll(barSelector)].map(node => ({width: node.width.animVal.value, ...box(node)})),
        headers: [...svg.querySelectorAll('text')].filter(node => /^Group [AB]$/.test(node.textContent))
            .map(node => ({text: node.textContent, ...box(node)})),
    };
}"""


def verify_gutter(result, ages):
    assert tuple(label["text"] for label in result["ages"]) == ages, result
    assert len(result["bars"]) == 2 * len(ages), result
    assert [label["text"] for label in result["headers"]] == ["Group A", "Group B"], result
    for label in result["ages"]:
        bars = [bar for bar in result["bars"] if label["bottom"] > bar["top"] and label["top"] < bar["bottom"]]
        assert len(bars) == 2, label
        left, right = sorted(bars, key=lambda bar: bar["left"])
        assert left["right"] + 2 < label["left"] < label["right"] < right["left"] - 2, (label, bars)
    assert max(header["bottom"] for header in result["headers"]) < result["ages"][0]["top"], result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", help="Installed Chromium channel such as msedge.")
    args = parser.parse_args()
    output = PROJECT / "artifacts/audit/pyramid-source"
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**({"channel": args.channel} if args.channel else {}))
        page = browser.new_page(viewport={"width": 1600, "height": 1000}, service_workers="block")
        page.route("http*://**", lambda route: route.abort())
        for gallery in GALLERIES:
            page.goto((EXAMPLES / gallery / "index.html").as_uri(), wait_until="load")
            svg = page.locator('[data-example="population-pyramid"] svg')
            svg.scroll_into_view_if_needed()
            svg.evaluate("svg => { svg.pauseAnimations(); svg.setCurrentTime(4); }")
            result = svg.evaluate(INSPECT, [".age-label", "rect.left, rect.right"])
            verify_gutter(result, AGES)
            left = [18 + i*4 + (i % 3)*3 for i in range(len(AGES))]
            right = [22 + (8-i)*3 + (i % 2)*4 for i in range(len(AGES))]
            assert all(math.isclose(bar["width"], value * 416/120, abs_tol=0.001)
                       for bar, value in zip(result["bars"], left + right, strict=True)), result
            svg.screenshot(path=output / f"{gallery}.png")
        uri = (EXAMPLES / GALLERIES[0] / "composition-sheets.html").as_uri()
        page.goto(f"{uri}#{COMPOSITION}", wait_until="load")
        svg = page.locator(f"#{COMPOSITION}-svg")
        svg.scroll_into_view_if_needed()
        svg.locator(".semantic-balance-axis-label").first.wait_for()
        verify_gutter(svg.evaluate(INSPECT, [".semantic-balance-axis-label", ".semantic-balance-bar"]), AGES[:6])
        svg.screenshot(path=output / "composition.png",
                       style="[data-replay-composition] { visibility: hidden !important; }")
        browser.close()
    print("Population pyramid gutters passed in three palettes and one composition.")


if __name__ == "__main__":
    main()
