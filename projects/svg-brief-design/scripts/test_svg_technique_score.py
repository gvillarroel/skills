#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Check score orientation, abstention, confidence separation and evidence boundaries."""
import copy
import unittest

from svg_art_direction import DIMENSIONS
from svg_technique_score import aggregate, make_job
from svg_technique_review import judge_record, semantic_controls


def fixture(probabilities=None):
    p = probabilities or [0,0,1,0,0]
    scores = {k:{"raw":{"type":"score","probabilities":{str(i):v for i,v in enumerate(p)},"confidence":.8}} for k in DIMENSIONS}
    for k,value in {"overall":"parity","brief_A":"fulfilled","brief_B":"fulfilled","evidence":"sufficient"}.items():
        scores[k] = {"raw":{"type":"choice","choice":value,"confidence":.8}}
    return scores


class TechniqueTests(unittest.TestCase):
    def test_anonymous_order_reversal_preserves_candidate_value(self):
        a = fixture([.07,.13,.29,.31,.20]); b = fixture([.20,.31,.29,.13,.07])
        self.assertAlmostEqual(aggregate(a,"A")["score_100"],aggregate(b,"B")["score_100"])
        self.assertAlmostEqual(aggregate(a,"A")["signed_technique_margin"],aggregate(b,"B")["signed_technique_margin"])

    def test_declared_parity_and_uncertainty_meanings(self):
        self.assertEqual(aggregate(fixture(),"A")["score_100"],90)
        flat = aggregate(fixture([.2]*5),"A")
        self.assertEqual(flat["signed_technique_margin"],0)
        self.assertEqual(flat["score_100"],82)
        self.assertIn("not an absolute aesthetic grade",flat["score_meaning"])

    def test_confidence_is_not_quality_multiplier(self):
        source = fixture([0,1,0,0,0]); low = copy.deepcopy(source)
        for value in low.values(): value["raw"]["confidence"] = .1
        self.assertEqual(aggregate(source,"A")["score_100"],aggregate(low,"A")["score_100"])
        self.assertFalse(aggregate(source,"A")["review_recommended"])
        self.assertTrue(aggregate(low,"A")["review_recommended"])

    def test_missing_evidence_or_subject_produces_no_reward(self):
        for key,value in [("brief_A","unknown"),("evidence","insufficient")]:
            source = fixture(); source[key]["raw"]["choice"] = value
            self.assertIsNone(aggregate(source,"A")["technique_quality"])
        source = fixture(); source["brief_A"]["raw"]["choice"]="wrong"
        self.assertEqual(aggregate(source,"A")["technique_quality"],0)

    def test_minor_and_major_explicit_content_gates(self):
        for fit,expected in [("minor_gap",79),("major_missing",49)]:
            source = fixture([0,0,0,0,1]); source["brief_A"]["raw"]["choice"] = fit
            self.assertEqual(aggregate(source,"A")["score_100"],expected)

    def test_old_global_recommendations_never_reach_new_judge(self):
        old = {"brief_fit":{"A":"facts A","B":"facts B"},"dimensions":{k:{"A":"located A","B":"located B","contrast":"discarded verdict"} for k in DIMENSIONS},"overall_contrast":"discarded global preference","small_scale":"small facts","uncertainty":[]}
        output = judge_record("anonymous","Create an ornament",old,"integrated-ornament")
        self.assertNotIn("discarded",str(output))
        self.assertNotIn("candidate_side",output)
        self.assertEqual(output["visual_evidence"]["dimensions"]["composition_space"]["A"],"located A")

    def test_context_controls_hold_visual_facts_fixed(self):
        cases = semantic_controls()
        for i,j in [(0,1),(2,3)]:
            self.assertEqual(cases[i][0]["visual_evidence"],cases[j][0]["visual_evidence"])
            self.assertNotEqual(cases[i][0]["brief"],cases[j][0]["brief"])
            self.assertNotEqual(cases[i][1]["expected_side"],cases[j][1]["expected_side"])
        self.assertTrue(all(make_job()["questions"][key]["type"]=="score" for key in DIMENSIONS))


if __name__ == "__main__": unittest.main()
