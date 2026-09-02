#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for Mermaid accessibility metadata reporting."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "skills" / "mermaid" / "scripts" / "style_mermaid_directory.py"
ANIMATOR_PATH = REPO_ROOT / "skills" / "mermaid" / "scripts" / "animate_mermaid_svg.py"


def load_styler():
    spec = importlib.util.spec_from_file_location("mermaid_style_accessibility_test", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


STYLER = load_styler()


def load_animator():
    scripts_directory = str(ANIMATOR_PATH.parent)
    if scripts_directory not in sys.path:
        sys.path.insert(0, scripts_directory)
    spec = importlib.util.spec_from_file_location("mermaid_animation_accessibility_test", ANIMATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ANIMATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ANIMATOR = load_animator()


class AccessibilityMetadataTests(unittest.TestCase):
    def test_single_line_title_and_description_are_detected(self) -> None:
        source = """flowchart LR
  accTitle: Request validation
  accDescr: Requests pass through validation before accepted work reaches storage.
  A --> B
"""
        self.assertEqual(STYLER.accessibility_metadata(source), (True, True))

    def test_multiline_description_is_detected_after_frontmatter(self) -> None:
        source = """---
config:
  theme: base
---
stateDiagram-v2
  accTitle: Review lifecycle
  accDescr {
    A request moves from draft through review and reaches either approval or rejection.
  }
  Draft --> Review
"""
        self.assertEqual(STYLER.accessibility_metadata(source), (True, True))

    def test_empty_or_missing_directives_are_reported(self) -> None:
        source = """flowchart LR
  accTitle:
  A --> B
"""
        self.assertEqual(STYLER.accessibility_metadata(source), (False, False))

    def test_report_identifies_the_missing_directive_per_block(self) -> None:
        source = """flowchart LR
  accTitle: Queue pressure
  A --> B
"""
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            path = root / "queue.mmd"
            path.write_text(source, encoding="utf-8")
            _, diagrams, _ = STYLER.style_file(path, root, "colorset1")
            report = STYLER.build_report(
                root,
                "colorset1",
                diagrams,
                [],
                True,
                True,
            )

        self.assertEqual(report["accessibleDiagramCount"], 0)
        self.assertEqual(report["missingAccessibilityCount"], 1)
        self.assertEqual(report["missingAccessibility"][0]["missing"], ["accDescr"])

    def test_rendered_svg_accessibility_contract_accepts_resolved_metadata(self) -> None:
        root = ANIMATOR.ET.fromstring(
            """<svg xmlns="http://www.w3.org/2000/svg"
              aria-labelledby="diagram-title" aria-describedby="diagram-description">
              <title id="diagram-title">Review queue</title>
              <desc id="diagram-description">Requests enter a capacity-two review queue.</desc>
            </svg>"""
        )
        ANIMATOR.assert_accessible_svg(root, Path("review-queue.svg"))

    def test_rendered_svg_accessibility_contract_rejects_unresolved_description(self) -> None:
        root = ANIMATOR.ET.fromstring(
            """<svg xmlns="http://www.w3.org/2000/svg"
              aria-labelledby="diagram-title" aria-describedby="wrong-description">
              <title id="diagram-title">Review queue</title>
              <desc id="diagram-description">Requests enter a capacity-two review queue.</desc>
            </svg>"""
        )
        with self.assertRaisesRegex(ValueError, "aria-describedby"):
            ANIMATOR.assert_accessible_svg(root, Path("review-queue.svg"))

    def test_rendered_svg_accessibility_contract_rejects_non_svg_root(self) -> None:
        root = ANIMATOR.ET.fromstring(
            """<root aria-labelledby="title" aria-describedby="description">
              <title id="title">Review queue</title>
              <desc id="description">Review queue description.</desc>
            </root>"""
        )
        with self.assertRaisesRegex(ValueError, "must have an <svg> root"):
            ANIMATOR.assert_accessible_svg(root, Path("not-svg.xml"))

    def test_rendered_svg_accessibility_contract_rejects_duplicate_ids(self) -> None:
        root = ANIMATOR.ET.fromstring(
            """<svg xmlns="http://www.w3.org/2000/svg"
              aria-labelledby="title" aria-describedby="description">
              <title id="title">Review queue</title>
              <desc id="description">Review queue description.</desc>
              <g id="title" />
            </svg>"""
        )
        with self.assertRaisesRegex(ValueError, "duplicate element IDs: title"):
            ANIMATOR.assert_accessible_svg(root, Path("duplicate-id.svg"))


if __name__ == "__main__":
    unittest.main()
