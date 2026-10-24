#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8", "playwright==1.64.1", "pillow==13.0.0"]
# ///
"""Validate canonical palette allocation, actual SVG paints, and HTML chrome.

Run: uv run --script test_xy_colorsets.py --output-dir artifacts/xy-colorset-tests
Requires Edge, Chrome, or Playwright Chromium for the browser acceptance case.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from PIL import Image
from playwright.sync_api import sync_playwright
import xy

from xy_colorsets import (
    binned_colors, categorical_colors, css, legend_style, load_palette, sequential_colors,
    text_on, theme,
)

OUTPUT = Path("artifacts/xy-colorset-tests")


def _chart(name):
    colors = categorical_colors(name, 3)
    return xy.scatter_chart(
        *[xy.scatter([i + 1], [i + 1], color=color, name=f"Series {i + 1}",
                     size=22, opacity=1, stroke_width=0)
          for i, color in enumerate(colors)],
        xy.x_axis(label="Input (units)", domain=(0, 4)),
        xy.y_axis(label="Response (units)", domain=(0, 4)),
        xy.legend(loc="lower right", style=legend_style(name)), xy.tooltip(), theme(name),
        title=f"{name} palette acceptance", width=640, height=400,
    )


def _paint(value):
    if value.startswith("#"):
        return value.lower()
    match = re.fullmatch(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", value)
    if match:
        return "#" + "".join(f"{int(channel):02x}" for channel in match.groups())
    return value


class PaletteContract(unittest.TestCase):
    def test_load_is_independent_and_rejects_unknown_names(self):
        first = load_palette()
        first["allowed"].clear()
        self.assertEqual(len(load_palette()["allowed"]), 17)
        for name in ("colorset3", "Colorset1", "", None):
            with self.assertRaises(ValueError):
                load_palette(name)

    def test_category_sequence_capacity_and_canvas(self):
        self.assertEqual(categorical_colors(count=6),
                         ["#9e1b32", "#000000", "#828282", "#1c1c1c", "#9c9c9c", "#363636"])
        for name in ("colorset1", "colorset2"):
            palette = load_palette(name)
            for canvas in ("#f7f7f7", "#ffffff", "#1c1c1c", "#FFFFFF"):
                colors = categorical_colors(name, background=canvas)
                self.assertNotIn(canvas.lower(), colors)
                self.assertEqual(colors, [c for c in palette["solidSequence"] if c != canvas.lower()])
                self.assertEqual(len(colors), len(set(colors)))
                with self.assertRaises(ValueError):
                    categorical_colors(name, len(colors) + 1, canvas)
        self.assertEqual(categorical_colors(count=0), [])
        for count in (-1, 1.1, True):
            with self.assertRaises(ValueError):
                categorical_colors(count=count)

    def test_text_is_maximum_black_white_contrast(self):
        for name in ("colorset1", "colorset2"):
            for fill, expected in load_palette(name)["textOnFill"].items():
                self.assertEqual(text_on(fill), expected)
        for fill in ("red", "#fff", "#ffffff00"):
            with self.assertRaises(ValueError):
                text_on(fill)

    def test_numeric_bins_preserve_alignment_and_missing_values(self):
        values = [-1, 0, 1, 2, 3, 4, math.nan, math.inf]
        self.assertEqual(binned_colors(values, domain=(0, 4)),
                         ["#e7e7e7", "#e7e7e7", "#9c9c9c", "#9e1b32", "#6d1222", "#6d1222", None, None])
        self.assertEqual(values[:6], [-1, 0, 1, 2, 3, 4])
        self.assertTrue(math.isnan(values[6]))
        self.assertEqual(binned_colors([math.nan]), [None])
        self.assertEqual(binned_colors([2, 2]), ["#9e1b32", "#9e1b32"])
        for domain in ((1, 1), (2, 1), (0, math.inf), (1,)):
            with self.assertRaises(ValueError):
                binned_colors([1], domain=domain)
        for bins in (0, 1, 5, 2.5, True):
            with self.assertRaises(ValueError):
                binned_colors([1], bins=bins)

    def test_theme_uses_public_xy_api_and_caller_overrides_win(self):
        for name in ("colorset1", "colorset2"):
            node = theme(name)
            self.assertIsInstance(node, xy.Theme)
            allowed = set(load_palette(name)["allowed"])
            self.assertTrue(set(node.palette).issubset(allowed))
            for value in node.style.values():
                if isinstance(value, str) and value.startswith("#"):
                    self.assertIn(value, allowed)
            self.assertEqual(node.style["--chart-tooltip-bg"], "#1c1c1c")
            self.assertEqual(node.style["--chart-tooltip-text"], "#ffffff")
            self.assertTrue(set(sequential_colors(name)).issubset(allowed))
        custom = theme(background="#ffffff", text_color="#333e48",
                       style={"--xy-modebar-text": "#333e48"}, palette=["#6d1222"])
        self.assertEqual(custom.style["--chart-text"], "#333e48")
        self.assertEqual(custom.style["--xy-modebar-text"], "#333e48")
        self.assertEqual(custom.palette, ["#6d1222"])
        self.assertEqual(legend_style(background="#1c1c1c")["color"], "#ffffff")

    def test_native_svg_has_only_allowed_authored_paints(self):
        for name in ("colorset1", "colorset2"):
            path = OUTPUT / f"{name}.svg"
            chart = _chart(name)
            chart.write_image(path)
            chart.to_html(OUTPUT / f"{name}.html", custom_css=css(name))
            allowed = set(load_palette(name)["allowed"])
            seen = set()
            for element in ET.parse(path).iter():
                for key in ("fill", "stroke"):
                    value = element.get(key)
                    if value and value not in ("none", "transparent") and not value.startswith("url("):
                        seen.add(_paint(value))
                if element.tag.endswith("circle"):
                    self.assertIn(element.get("fill-opacity", "1"), ("1", "1.0"))
                    self.assertIn(element.get("stroke-width", "0"), ("0", "0.0"))
            self.assertTrue(seen.issubset(allowed), seen - allowed)
            self.assertTrue(set(categorical_colors(name, 3)).issubset(seen))

    def test_browser_actual_chrome_and_canvas_paints(self):
        evidence = {}
        with sync_playwright() as playwright:
            browser = None
            attempts = []
            for options in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
                try:
                    browser = playwright.chromium.launch(headless=True, **options)
                    break
                except Exception as error:
                    attempts.append(str(error).splitlines()[0])
            self.assertIsNotNone(browser, f"No Chromium browser available: {attempts}")
            try:
                context = browser.new_context(viewport={"width": 900, "height": 650})
                blocked = []
                context.route("**/*", lambda route: (blocked.append(route.request.url), route.abort())
                              if route.request.url.startswith(("http://", "https://")) else route.continue_())
                for name in ("colorset1", "colorset2"):
                    _chart(name).to_html(OUTPUT / f"{name}.html", custom_css=css(name))
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto((OUTPUT / f"{name}.html").resolve().as_uri(), wait_until="load")
                    page.locator(".xy canvas").first.wait_for(state="visible")
                    page.wait_for_timeout(300)
                    page.locator(".xy").first.hover()
                    chrome = page.locator(".xy").first.evaluate("""root => {
                        const grab = node => { const s=getComputedStyle(node); return {
                            color:s.color, background:s.backgroundColor, border:s.borderColor, shadow:s.boxShadow
                        }; };
                        return {root:grab(root), modebar:grab(root.querySelector('[data-xy-slot="modebar"]')),
                            tooltip:grab(root.querySelector('[data-xy-slot="tooltip"]'))};
                    }""")
                    self.assertEqual(chrome["root"]["background"], "rgb(247, 247, 247)")
                    self.assertEqual(chrome["modebar"]["color"], "rgb(0, 0, 0)")
                    self.assertEqual(chrome["modebar"]["background"], "rgb(255, 255, 255)")
                    self.assertEqual(chrome["modebar"]["border"], "rgb(207, 207, 207)")
                    self.assertEqual(chrome["modebar"]["shadow"], "none")
                    self.assertEqual(chrome["tooltip"]["background"], "rgb(28, 28, 28)")
                    self.assertEqual(chrome["tooltip"]["color"], "rgb(255, 255, 255)")
                    self.assertEqual(chrome["tooltip"]["shadow"], "none")
                    button = page.locator('.xy [data-xy-slot="modebar"] button').first
                    button.hover()
                    hover = button.evaluate("node => getComputedStyle(node).backgroundColor")
                    self.assertEqual(hover, "rgb(231, 231, 231)")
                    button.focus()
                    focus = button.evaluate("node => getComputedStyle(node).outlineColor")
                    self.assertIn(focus, ("rgb(158, 27, 50)", "rgb(0, 0, 0)"))
                    screenshot = OUTPUT / f"{name}.png"
                    page.screenshot(path=str(screenshot))
                    with Image.open(screenshot) as image:
                        counts = Counter(image.convert("RGB").get_flattened_data())
                    for color in categorical_colors(name, 3):
                        rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
                        self.assertGreater(counts[rgb], 20, f"Missing actual canvas paint: {color}")
                    self.assertEqual(errors, [])
                    evidence[name] = {"chrome": chrome, "hover_background": hover,
                                      "focus_outline": focus, "page_errors": errors}
                    page.close()
                self.assertEqual(blocked, [])
            finally:
                browser.close()
        (OUTPUT / "browser.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args, remaining = parser.parse_known_args()
    OUTPUT = args.output_dir.resolve()
    if OUTPUT.is_relative_to(Path(__file__).resolve().parent.parent):
        parser.error("Write validation artifacts outside the read-only skill bundle")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    unittest.main(argv=[__file__, *remaining])
