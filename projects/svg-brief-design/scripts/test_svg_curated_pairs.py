#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Verify anchor-relative semantics, order mapping and failure gates."""
import unittest
from svg_curated_pairs import DIMENSIONS,aggregate,validate


def answers(choice="parity",fit="fulfilled",confidence=.8):
    return {key:{"raw":{"choice":fit if key.startswith("brief_") else choice,"confidence":confidence}} for key in [*DIMENSIONS,"overall","brief_A","brief_B"]}


class CuratedTests(unittest.TestCase):
    def test_anchor_parity_is_an_explicit_convention(self):
        self.assertEqual(aggregate(answers(),"A")["score_100"],90)

    def test_better_candidate_can_exceed_purchased_anchor(self):
        self.assertEqual(aggregate(answers("A_clear"),"A")["score_100"],100)

    def test_swapping_sides_preserves_merit(self):
        a=aggregate(answers("B_clear"),"A");b=aggregate(answers("A_clear"),"B")
        self.assertEqual(a["score_100"],b["score_100"]);self.assertEqual(a["score_100"],50)

    def test_missing_content_cannot_hide_behind_beauty(self):
        self.assertEqual(aggregate(answers("A_clear","major_missing"),"A")["score_100"],49)

    def test_wrong_subject_is_zero(self):
        self.assertEqual(aggregate(answers("A_clear","wrong"),"A")["score_100"],0)

    def test_unknown_is_not_a_numeric_quality(self):
        self.assertIsNone(aggregate(answers("unknown"),"A")["curated_design_quality"])

    def test_confidence_does_not_scale_quality(self):
        a=aggregate(answers(confidence=.01),"A");b=aggregate(answers(confidence=.99),"A")
        self.assertEqual(a["score_100"],b["score_100"]);self.assertTrue(a["review_recommended"])

    def test_missing_dimension_fails_closed(self):
        a=answers();del a["craft_finish"]
        with self.assertRaises(ValueError):aggregate(a,"A")

    def test_invalid_binding_is_rejected(self):
        with self.assertRaises(ValueError):aggregate(answers(),"reference")

    def test_observer_cannot_smuggle_grade_in_schema(self):
        value={"brief_fit":{"A":"ok","B":"ok"},"dimensions":{k:{"A":"fact","B":"fact","contrast":"different"} for k in DIMENSIONS},"overall_contrast":"contrast","small_scale":"clear","uncertainty":[],"score":100}
        with self.assertRaises(ValueError):validate(value)


if __name__=="__main__":unittest.main()
