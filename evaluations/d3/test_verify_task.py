#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the evaluator-owned D3 Harbor verifier."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import verify_task


VISUAL_CONTRACT = {
    "taskId": "verifier-self-test",
    "route": "visualization",
    "colorset": "colorset1",
    "requireExtended": False,
    "expectedPatternId": "d3-verifier-self-test",
    "requiredTerms": ["Alpha", "Beta", "12", "19"],
    "orderedTerms": ["Alpha", "Beta"],
    "tagMinimums": {"rect": 2, "text": 4},
    "classMinimums": {"data-mark": 2},
    "requiredIds": ["chart"],
    "requiredAttributes": {"data-chart-kind": "bar"},
    "requiresAnimation": True,
    "requiresInteraction": True,
    "visualPalette": {
        "requiredGroups": ["primary"],
        "minDistinctColors": 1,
        "minPixelsPerColor": 24.0,
        "minPaletteEffectivePixels": 64.0,
        "minPaletteCoverageRatio": 0.001,
        "minInfluenceEffectivePixels": 32.0,
        "minInfluenceRatio": 0.0005,
    },
}


VALID_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><style>body{margin:0;background:#f7f7f7;color:#333e48}</style></head>
<body data-colorset="colorset1" data-renderer="d3">
<svg id="chart" data-chart-kind="bar" viewBox="0 0 400 260" width="800" height="520" role="img">
<title>Alpha and Beta</title><desc>Two deterministic bars</desc>
<rect class="data-mark" x="70" y="70" width="100" height="140" fill="#9e1b32"/>
<rect class="data-mark" x="230" y="30" width="100" height="180" fill="#6d1222"/>
<text x="90" y="235" fill="#333e48">Alpha</text><text x="260" y="235" fill="#333e48">Beta</text>
<text x="105" y="100" fill="#ffffff">12</text><text x="265" y="60" fill="#ffffff">19</text>
</svg>
<script>const d3={select(){return{transition(){return this},on(){return this}}}};d3.select("svg").transition().on("click",()=>{});</script>
</body></html>
"""


class HarborVerifierTests(unittest.TestCase):
    def make_visual_workspace(self, root: Path, source: str) -> tuple[Path, Path]:
        workspace = root / "workspace"
        log_dir = root / "logs"
        deliverables = workspace / "deliverables"
        deliverables.mkdir(parents=True)
        log_dir.mkdir(parents=True)
        (deliverables / "visual.html").write_text(source, encoding="utf-8")
        (deliverables / "decision.json").write_text(
            json.dumps(
                {
                    "route": "visualization",
                    "colorset": "colorset1",
                    "patternId": "d3-verifier-self-test",
                    "reason": "A deterministic bar chart fits the supplied comparison.",
                }
            ),
            encoding="utf-8",
        )
        return workspace, log_dir

    def test_browser_render_palette_and_counterfactual_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace, log_dir = self.make_visual_workspace(Path(temporary), VALID_HTML)
            result = verify_task.verify_visual(workspace, log_dir, VISUAL_CONTRACT)
            self.assertTrue(result["ok"], json.dumps(result, indent=2))
            self.assertGreater(result["counterfactualReplacements"], 0)
            self.assertTrue(result["visualPalette"]["influence"]["ok"])

    def test_browser_uses_explicit_playwright_core_with_isolated_npm_cache(self) -> None:
        explicit = os.environ.get("HARBOR_PLAYWRIGHT_CORE_PATH")
        if not explicit or not (Path(explicit) / "package.json").is_file():
            self.skipTest("HARBOR_PLAYWRIGHT_CORE_PATH is not available")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace, log_dir = self.make_visual_workspace(root, VALID_HTML)
            empty_cache = root / "isolated-npm-cache"
            empty_cache.mkdir()
            with patch.dict(
                os.environ,
                {
                    "npm_config_cache": str(empty_cache),
                    "NPM_CONFIG_CACHE": str(empty_cache),
                    "HARBOR_PLAYWRIGHT_CORE_PATH": explicit,
                },
                clear=False,
            ):
                result = verify_task.verify_visual(workspace, log_dir, VISUAL_CONTRACT)
            self.assertTrue(result["ok"], json.dumps(result, indent=2))

    def test_extended_token_fails_colorset1(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace, log_dir = self.make_visual_workspace(
                Path(temporary), VALID_HTML.replace("#9e1b32", "#007298")
            )
            result = verify_task.verify_visual(workspace, log_dir, VISUAL_CONTRACT)
            self.assertFalse(result["ok"])
            self.assertIn("#007298", result["staticPalette"]["forbiddenColors"])

    def test_evaluation_route_checks_traceable_findings(self) -> None:
        contract = {
            "taskId": "evaluation-self-test",
            "route": "evaluation",
            "colorset": "colorset1",
            "expectedPatternId": "d3-composition-audit",
            "requiredTerms": ["Artifact: audit-target.svg", "#label-hot", "label clearance"],
            "patterns": [r"Overall composition score:\s*\d{1,3}/100"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            deliverables = root / "deliverables"
            logs = root / "logs"
            deliverables.mkdir()
            logs.mkdir()
            (deliverables / "evaluation.md").write_text(
                "Artifact: audit-target.svg\n\n#label-hot fails label clearance.\n\nOverall composition score: 62/100\n",
                encoding="utf-8",
            )
            (deliverables / "decision.json").write_text(
                json.dumps(
                    {
                        "route": "evaluation",
                        "colorset": "colorset1",
                        "patternId": "d3-composition-audit",
                        "reason": "The visible SVG needs a traceable composition audit.",
                    }
                ),
                encoding="utf-8",
            )
            result = verify_task.verify_evaluation(root, logs, contract)
            self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
