#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the rendered D3 literal-contract checker."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile
import unittest

import check_visual_contract


SVG = """<svg id="service-network" class="chart" data-layout="force" viewBox="0 0 400 240">
<title>Service network</title><desc>Directed service topology</desc>
<g class="node"><circle/><text>Gateway</text></g>
<g class="node"><circle/><text>Queue</text></g>
<g class="link"><line/></g><g class="link"><line/></g>
<text>Store</text></svg>"""


def arguments(path: Path, **overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "artifact": path,
        "require_id": [],
        "require_class": [],
        "require_tag": [],
        "require_attribute": [],
        "require_text": [],
        "ordered_text": [],
        "no_require_svg_contract": False,
        "json_report": None,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class VisualContractTests(unittest.TestCase):
    def write_svg(self, root: Path, source: str = SVG) -> Path:
        path = root / "visual.svg"
        path.write_text(source, encoding="utf-8")
        return path

    def test_exact_structure_and_order_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_svg(Path(temporary))
            result = check_visual_contract.check(
                arguments(
                    path,
                    require_id=["service-network"],
                    require_class=[("node", 2), ("link", 2)],
                    require_tag=[("circle", 2), ("line", 2)],
                    require_attribute=[("data-layout", "force")],
                    require_text=["Gateway", "Store"],
                    ordered_text=["Gateway", "Queue", "Store"],
                )
            )
            self.assertTrue(result["ok"], result)

    def test_near_equivalent_id_and_class_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_svg(Path(temporary))
            result = check_visual_contract.check(
                arguments(path, require_id=["service-dependency-svg"], require_class=[("nodes", 2)])
            )
            self.assertFalse(result["ok"])
            self.assertIn("missing ID: service-dependency-svg", result["findings"])

    def test_accessibility_contract_is_default(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_svg(Path(temporary), "<svg><circle/></svg>")
            result = check_visual_contract.check(arguments(path))
            self.assertFalse(result["ok"])
            self.assertIn("missing rendered title", result["findings"])
            self.assertIn("missing rendered desc", result["findings"])
            self.assertIn("missing stable SVG viewBox", result["findings"])


if __name__ == "__main__":
    unittest.main()
