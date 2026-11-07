#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10,<13", "playwright>=1.52,<2"]
# ///
"""Verify that all gallery palettes paint the agent loop bitmap under five covers."""

import argparse
import io
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import Error, sync_playwright


PROJECT = Path(__file__).resolve().parents[1]
SKILL = PROJECT.parents[1] / "skills/d3"
GALLERIES = {
    "base": "d3-animated-svg",
    "cs1": "d3-animated-svg-cs1",
    "cs2": "d3-animated-svg-colorset2",
}
REGIONS = ["main-loop", "prompt-builder", "tool-system", "sub-agents", "compaction"]


INSPECT = r"""async svg => {
    const bitmap = svg.querySelector(':scope > image');
    const veil = bitmap.nextElementSibling;
    const url = new URL(bitmap.href.baseVal, document.baseURI);
    const decoded = new Image();
    decoded.src = url.href;
    await decoded.decode();
    return {
        bitmap: {width: decoded.naturalWidth, height: decoded.naturalHeight,
            opacity: Number(getComputedStyle(bitmap).opacity),
            source: url.pathname.split('/').slice(-2).join('/')},
        veil: {role: veil.dataset.opacityRole, opacity: Number(getComputedStyle(veil).opacity)},
        regions: Array.from(svg.querySelectorAll('.agent-cover'), node => {
            const cover = node.querySelector('.agent-cover-fill');
            return {id: node.dataset.region, width: cover.width.animVal.value,
                targetWidth: Number(node.dataset.targetWidth), alpha: Number(getComputedStyle(cover).fillOpacity)};
        }),
    };
}"""


def verify_page(browser, path, palette, output):
    context = browser.new_context(viewport={"width": 1600, "height": 1000}, service_workers="block")
    context.route("http*://**", lambda route: route.abort())
    try:
        page = context.new_page()
        page.goto(path.as_uri(), wait_until="load")
        svg = page.locator('[data-example="agent-loop-overlay"] svg')
        svg.scroll_into_view_if_needed()
        svg.evaluate("svg => { svg.pauseAnimations(); svg.setCurrentTime(4); }")
        evidence = svg.evaluate(INSPECT)
        assert evidence["bitmap"] == {"width": 980, "height": 618, "opacity": 0.72,
                                       "source": "assets/agent-loop-reference.png"}, evidence
        assert evidence["veil"] == {"role": "semantic", "opacity": 0.08}, evidence
        assert [region["id"] for region in evidence["regions"]] == REGIONS, evidence
        assert all(0 < region["alpha"] < 0.3 and
                   math.isclose(region["width"], region["targetWidth"], abs_tol=0.01)
                   for region in evidence["regions"]), evidence
        normal = svg.screenshot(path=output / f"{palette}.png")
        svg.locator(":scope > image").evaluate("image => image.style.visibility = 'hidden'")
        without_bitmap = svg.screenshot(path=output / f"{palette}-without-bitmap.png")
        with Image.open(io.BytesIO(normal)) as image, Image.open(io.BytesIO(without_bitmap)) as blank:
            difference = ImageChops.difference(image.convert("RGB"), blank.convert("RGB"))
            evidence["bitmapRgbMeanDifference"] = sum(ImageStat.Stat(difference).mean) / 3
            assert evidence["bitmapRgbMeanDifference"] > 5, evidence
        return evidence
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PROJECT / "artifacts/audit/agent-loop-source")
    parser.add_argument("--channel", help="Chromium channel when using an installed browser, such as msedge.")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT / "artifacts"):
        parser.error("Keep audit files under the project artifact directory.")
    output.mkdir(parents=True, exist_ok=True)
    examples = SKILL / "assets/examples"
    fixture_bitmap = examples / "d3-animated-svg/assets/agent-loop-reference.png"
    assert fixture_bitmap.read_bytes() == (SKILL / "assets/reference/agent-loop-reference.png").read_bytes(), (
        "The gallery bitmap and runtime bitmap differ.")
    with sync_playwright() as playwright:
        options = {"channel": args.channel} if args.channel else {}
        browser = playwright.chromium.launch(**options)
        try:
            palettes = {name: verify_page(browser, examples / gallery / "index.html", name, output)
                        for name, gallery in GALLERIES.items()}
        finally:
            browser.close()
    (output / "report.json").write_text(json.dumps({"passed": True, "palettes": palettes}, indent=2) + "\n",
                                       encoding="utf-8")
    print("Verified visible source bitmap, semantic veil, and five covers in all three palettes.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, Error, OSError) as error:
        sys.exit(f"Agent loop source verification failed. {error}")
