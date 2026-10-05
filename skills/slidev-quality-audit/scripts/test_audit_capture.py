#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify native state captures and SVG metadata without suppressing hidden copy.

Run prepare-audit-deck.py --deck <work-dir>/deck from its owning workspace
before executing this browser regression.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent
WORK_DIR: Path

SLIDE = """---
theme: default
layout: default
class: capture-regression
background: '#ffffff'
---

<svg class="capture-regression" viewBox="0 0 960 540" style="width:100%;height:100%;background:#ffffff" role="img" aria-label="Workflow" aria-describedby="workflow-description">
<title>Workflow</title>
<desc id="workflow-description">Accessibility description, not visible presentation text.</desc>
<metadata>Authoring metadata, not hidden slide copy.</metadata>
<g fill="#e7e7e7">
<rect x="100" y="180" width="130" height="44"/>
<rect x="300" y="180" width="130" height="44"/>
<rect x="500" y="180" width="130" height="44"/>
<rect x="700" y="180" width="130" height="44"/>
</g>
<g style="font-size:18px;fill:#000000;text-anchor:middle">
<text x="165" y="208">Intake</text><text x="365" y="208">Check</text>
<text x="565" y="208">Approve</text><text x="765" y="208">Archive</text>
<text x="465" y="290">recheck</text>
</g>
<g stroke="#000000" stroke-width="2" fill="none">
<path d="M230 202 H280"/><path d="M430 202 H480"/><path d="M630 202 H680"/>
<path d="M565 224 V310 H365 V245"/>
</g>
<g fill="#000000"><path d="M280 197 L290 202 L280 207 Z"/>
<path d="M480 197 L490 202 L480 207 Z"/><path d="M680 197 L690 202 L680 207 Z"/>
<path d="M360 245 L365 235 L370 245 Z"/></g>
</svg>

<style>
.slidev-layout.capture-regression { padding:0; background:#ffffff; }
.capture-regression text { font-size:18px; fill:#000000; text-anchor:middle; }
</style>
"""


class PreparationTests(unittest.TestCase):
    def load_helper(self):
        spec = importlib.util.spec_from_file_location("audit_deck_preparation", BUNDLE / "scripts/prepare-audit-deck.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_new_scratch_package_is_owned_and_declares_local_tools(self) -> None:
        helper = self.load_helper()
        with tempfile.TemporaryDirectory(dir=WORK_DIR) as temporary:
            workspace = Path(temporary)
            package = helper.prepare(workspace / "deck", workspace)
            data = json.loads(package.read_text(encoding="utf-8"))
            self.assertIn("@slidev/cli", data["devDependencies"])
            self.assertIn("playwright", data["devDependencies"])
            self.assertFalse((workspace / "package.json").exists())
            command = helper.npm_command() + ["install", "--prefix", str(package.parent)]
            self.assertTrue(Path(command[0]).is_absolute())
            self.assertEqual(command[-2:], ["--prefix", str(package.parent.resolve())])

    def test_existing_package_and_lock_are_preserved(self) -> None:
        helper = self.load_helper()
        with tempfile.TemporaryDirectory(dir=WORK_DIR) as temporary:
            workspace = Path(temporary)
            deck = workspace / "deck"
            deck.mkdir()
            content = '{"devDependencies":{"@slidev/cli":"original","playwright":"original","tsx":"original"},"custom":"retain"}'
            (deck / "package.json").write_text(content, encoding="utf-8")
            (deck / "package-lock.json").write_text("original lock", encoding="utf-8")
            helper.prepare(deck, workspace)
            self.assertEqual((deck / "package.json").read_text(encoding="utf-8"), content)
            self.assertEqual((deck / "package-lock.json").read_text(encoding="utf-8"), "original lock")

    def test_unowned_and_skill_paths_are_rejected_before_writing(self) -> None:
        helper = self.load_helper()
        with tempfile.TemporaryDirectory(dir=WORK_DIR) as temporary:
            workspace = Path(temporary)
            for deck in (workspace, workspace.parent / "unowned-deck", BUNDLE / "generated-deck"):
                with self.assertRaises(ValueError):
                    helper.prepare(deck, workspace)


class NativeCaptureTests(unittest.TestCase):
    def audit(self, name: str, *, hidden: bool = False, mode: str | None = None) -> dict:
        deck = WORK_DIR / "deck"
        slides = SLIDE + ('\n<p style="display:none">Missing final explanation</p>\n' if hidden else "")
        (deck / "slides.md").write_text(slides, encoding="utf-8")
        runner = deck / "node_modules/tsx/dist/cli.mjs"
        self.assertTrue(runner.exists(), "Install the bundled scratch-deck dependencies first")
        command = ["node", str(runner), str(BUNDLE / "scripts/audit-slidev-quality.ts"),
                   "--deck", str(deck), "--out", str(WORK_DIR / name), "--colorset", "colorset1"]
        if mode:
            command.extend(["--screenshots", mode])
        result = subprocess.run(command, cwd=WORK_DIR, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=180)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads((WORK_DIR / name / "quality-report.json").read_text(encoding="utf-8"))

    def test_clean_state_keeps_native_screenshot_and_metadata_is_not_hidden_copy(self) -> None:
        report = self.audit("clean-default")
        self.assertEqual(report["findingCount"], 0, report["findings"])
        self.assertEqual(report["viewport"], {"width": 1280, "height": 720})
        self.assertTrue(report["states"])
        for state in report["states"]:
            self.assertTrue(state.get("screenshot"))
            self.assertTrue((WORK_DIR / state["screenshot"]).is_file())

    def test_actual_hidden_presentation_copy_is_still_reported(self) -> None:
        report = self.audit("hidden-copy", hidden=True)
        hidden = [finding for finding in report["findings"] if finding["ruleId"] == "hidden-final-text"]
        self.assertEqual(len(hidden), 1, hidden)
        self.assertIn("Missing final explanation", hidden[0]["message"])
        self.assertTrue(report["states"][0].get("screenshot"))

    def test_explicit_issues_mode_preserves_requested_sparse_capture(self) -> None:
        report = self.audit("clean-issues", mode="issues")
        self.assertEqual(report["findingCount"], 0, report["findings"])
        self.assertTrue(all(not state.get("screenshot") for state in report["states"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    args, remaining = parser.parse_known_args()
    global WORK_DIR
    WORK_DIR = args.work_dir.resolve()
    if WORK_DIR.is_relative_to(BUNDLE):
        parser.error("Keep generated browser regression artifacts outside the read-only skill bundle")
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    result = unittest.main(argv=[__file__, *remaining], exit=False).result
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
