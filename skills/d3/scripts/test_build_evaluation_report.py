#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the deterministic composition-evaluation builder."""

from __future__ import annotations

import argparse
import unittest

import build_evaluation_report


def arguments(**overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "artifact": "audit.svg",
        "score": 68,
        "route": "evaluation",
        "colorset": "colorset1",
        "pattern_id": "d3-composition-audit",
        "reason": "The visible artifact requires a composition audit.",
        "required_term": ["reading path", "implementation contract", "#label-hot"],
        "composition_finding": ["#label-hot overlaps #node-hot and weakens the reading path."],
        "implementation_finding": ["implementation contract: move the label and add clearance."],
        "validation": ["Render in Chromium and inspect the settled SVG."],
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class EvaluationReportBuilderTests(unittest.TestCase):
    def test_preserves_exact_contract_terms_and_report_shape(self) -> None:
        report, decision = build_evaluation_report.build(arguments())
        self.assertTrue(report.startswith("Artifact: audit.svg\n"))
        for term in ("reading path", "implementation contract", "#label-hot"):
            self.assertIn(f"- {term}", report)
        self.assertIn("Overall composition score: 68/100", report)
        self.assertIn("## Validation", report)
        self.assertEqual(decision["patternId"], "d3-composition-audit")

    def test_rejects_missing_finding_category(self) -> None:
        with self.assertRaisesRegex(ValueError, "composition-finding"):
            build_evaluation_report.build(arguments(composition_finding=[]))

    def test_rejects_out_of_range_score(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            build_evaluation_report.build(arguments(score=101))

    def test_help_emphasizes_exact_repeated_terms(self) -> None:
        help_text = build_evaluation_report.make_parser().format_help()
        self.assertIn("--required-term EXACT-LITERAL", help_text)
        self.assertIn("Do not normalize spaces, punctuation, selectors, or case.", help_text)


if __name__ == "__main__":
    unittest.main()
