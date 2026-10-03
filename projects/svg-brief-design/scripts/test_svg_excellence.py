#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Exercise scoring boundaries, renderer interventions and injection isolation."""
import unittest
from svg_excellence import CONFIG, DIMENSIONS, aggregate, make_evidence, read
from prepare_excellence import controls


class ExcellenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubric = read(CONFIG/"rubric.json")
        cls.fixtures = {row["name"]: row for row in controls()}
        cls.evidence = {}
        for name in ["disk-large", "disk-injection", "label-clear", "label-hidden", "label-overlap", "disk-clipped", "external", "invalid", "empty"]:
            row = cls.fixtures[name]
            cls.evidence[name] = make_evidence(row["svg"].encode(), row["request"], row["contract"])

    def decisions(self, value=4):
        values = {key: {"value": value, "needs_review": False,
                       "raw": {"confidence": 1.0, "probabilities": {str(i): float(i == 4) for i in range(5)}}} for key in DIMENSIONS}
        values["evidence_sufficiency"] = {"value": "sufficient", "needs_review": False,
                    "raw": {"confidence": 1, "probabilities": {"sufficient": 1, "unknown": 0}}}
        return values

    def test_full_marks_attainable(self):
        self.assertEqual(aggregate(self.evidence["disk-large"], self.decisions(), self.rubric)["score_100"], 100)

    def test_unknown_has_no_reward(self):
        ds = self.decisions()
        ds["evidence_sufficiency"]["value"] = None
        self.assertIsNone(aggregate(self.evidence["disk-large"], ds, self.rubric)["technical_excellence"])

    def test_confidence_not_quality_multiplier(self):
        ds = self.decisions()
        ds["composition"]["raw"]["confidence"] = 0.4
        self.assertEqual(aggregate(self.evidence["disk-large"], ds, self.rubric)["score_100"], 100)

    def test_low_confidence_needs_review(self):
        ds = self.decisions()
        ds["composition"]["needs_review"] = True
        self.assertEqual(aggregate(self.evidence["disk-large"], ds, self.rubric)["status"], "needs_review")

    def test_critical_brief_cap(self):
        ds = self.decisions()
        ds["brief_adherence"]["value"] = 1
        self.assertEqual(aggregate(self.evidence["disk-large"], ds, self.rubric)["score_100"], 49)

    def test_bad_numbers_fail_closed(self):
        for value in [True, float("nan"), float("inf"), -1, 5, "4"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                aggregate(self.evidence["disk-large"], self.decisions(value), self.rubric)

    def test_missing_dimension_rejected(self):
        ds = self.decisions()
        del ds["geometric_finish"]
        with self.assertRaises(ValueError):
            aggregate(self.evidence["disk-large"], ds, self.rubric)

    def test_hard_failure_never_calls_judge(self):
        for name in ["external", "invalid", "empty"]:
            result = aggregate(self.evidence[name], {}, self.rubric)
            self.assertEqual(result["technical_excellence"], 0)
            self.assertFalse(result["model_called"])

    def test_hidden_information_measured(self):
        self.assertTrue(all(row["observable_ink_fraction"] > 0.95 for row in self.evidence["label-clear"]["measurements"]["text"]))
        self.assertTrue(all(row["observable_ink_fraction"] == 0 for row in self.evidence["label-hidden"]["measurements"]["text"]))

    def test_overlap_measured(self):
        self.assertTrue(self.evidence["label-overlap"]["measurements"]["text_ink_intersections"])
        self.assertFalse(self.evidence["label-clear"]["measurements"]["text_ink_intersections"])

    def test_clipping_measured(self):
        self.assertGreater(self.evidence["disk-clipped"]["measurements"]["nearby_ink_beyond_viewbox_pixels"], 0)

    def test_inert_injection_removed_without_visual_change(self):
        a, b = self.evidence["disk-large"], self.evidence["disk-injection"]
        self.assertEqual(a["measurements"], b["measurements"])
        self.assertEqual(a["svg_source_untrusted"], b["svg_source_untrusted"])

    def test_fundamentally_wrong_subject_has_decisive_failure(self):
        rubric = read(CONFIG/"rubric-v3.json")
        ds = self.decisions()
        ds["brief_adherence"]["value"] = "level_0"
        ds["brief_adherence"]["raw"]["type"] = "choice"
        ds["geometric_finish"]["needs_review"] = True
        ds["geometric_finish"]["value"] = None
        result = aggregate(self.evidence["disk-large"], ds, rubric)
        self.assertEqual(result["status"], "brief_failure")
        self.assertEqual(result["score_100"], 0)

    def test_unknown_brief_never_triggers_fundamental_gate(self):
        ds = self.decisions()
        ds["brief_adherence"]["value"] = None
        ds["brief_adherence"]["needs_review"] = True
        result = aggregate(self.evidence["disk-large"], ds, read(CONFIG/"rubric-v3.json"))
        self.assertIsNone(result["score_100"])

    def test_visual_schema_rejects_grades(self):
        from luna_svg_observer import validate_observation
        with self.assertRaises(ValueError):
            validate_observation({"score": 100})

    def test_large_source_keeps_complete_visual_evidence(self):
        from prepare_visual_excellence import visual_record
        evidence = dict(self.evidence["disk-large"])
        evidence["svg_source_untrusted"] = "x"*13000
        observed = {"description": "disk", "brief_features": [], "geometry": [], "composition": [], "legibility": [], "unverified": []}
        record = visual_record(evidence, observed, "control")
        self.assertEqual(record["visual_observations"], observed)
        self.assertTrue(record["source_crosscheck"].startswith("Full source exceeds"))
        self.assertEqual(record["render_measurements"], evidence["measurements"])


if __name__ == "__main__":
    unittest.main()
