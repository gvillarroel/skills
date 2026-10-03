#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Check uncertainty propagation without awarding unsupported quality points."""
import unittest
from curated_quality_v52 import aggregate
from test_svg_curated_pairs import answers


class BoundsTests(unittest.TestCase):
    def test_identity_parity(self):
        self.assertEqual(aggregate(answers(),"A")["score_interval_100"],[90,90])

    def test_unknown_dimension_retains_full_possible_range(self):
        a=answers();a["craft_finish"]["raw"]["choice"]="unknown"
        r=aggregate(a,"A")
        self.assertEqual(r["score_interval_100"],[82,92])
        self.assertIsNone(r["point_score_100"])
        self.assertEqual(r["curated_design_quality"],.82)

    def test_uncertain_overall_is_separate_from_weighted_dimensions(self):
        a=answers();a["overall"]["raw"]["choice"]="unknown"
        r=aggregate(a,"A")
        self.assertEqual(r["score_100"],90)
        self.assertTrue(r["overall_preference_unresolved"])
        self.assertTrue(r["review_recommended"])

    def test_unknown_candidate_subject_still_abstains(self):
        a=answers();a["brief_A"]["raw"]["choice"]="unknown"
        self.assertIsNone(aggregate(a,"A")["curated_design_quality"])

    def test_wrong_subject_is_zero_despite_uncertain_design(self):
        a=answers("unknown","wrong")
        self.assertEqual(aggregate(a,"A")["score_interval_100"],[0,0])

    def test_side_swap_preserves_bounds(self):
        a=answers("A_slight");b=answers("B_slight")
        for r in (a,b):r["shape_rhythm"]["raw"]["choice"]="unknown"
        self.assertEqual(aggregate(a,"A")["score_interval_100"],aggregate(b,"B")["score_interval_100"])

    def test_confidence_never_becomes_quality(self):
        self.assertEqual(aggregate(answers(confidence=.01),"A")["score_100"],aggregate(answers(confidence=.99),"A")["score_100"])


if __name__=="__main__":unittest.main()
