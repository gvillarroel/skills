from copy import deepcopy
import json
import unittest

from study import ROOT, bind_span, compile_observations, load, load_sources, make_prompt, normalize_review, parse, render_inputs, score


def span(window, quote):
    return {"window": window, "quote": quote}


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.actor = [{
            "id": "p",
            "windows": [
                {"id": "w1", "text": "Job runner"},
                {"id": "w2", "text": "This capability uses an external service."},
            ],
            "claims": [
                {"id": "c1", "text": "Job runner uses an external service.", "identity": "named"},
                {"id": "c2", "text": "The capability uses an external service.", "identity": "unnamed"},
            ],
        }]
        self.observation = {
            "identity": "unnamed", "subject": span("w2", "This capability"),
            "assertion": span("w2", "uses an external service"), "context": [],
        }

    def observations(self, *rows):
        return {"packets": [{"id": "p", "observations": list(rows), "gaps": []}]}

    def decisions(self, basis):
        return {"decisions": [
            {"id": claim["id"], "verdict": "supported", "basis": list(basis), "reason": "Test.", "question": ""}
            for claim in self.actor[0]["claims"]
        ]}

    def test_observer_cannot_see_claims(self):
        changed = deepcopy(self.actor)
        changed[0]["claims"][0]["text"] = "Alternate caller input with no source authority."
        self.assertEqual(make_prompt(self.actor, "observe"), make_prompt(changed, "observe"))
        self.assertNotEqual(make_prompt(self.actor, "direct"), make_prompt(changed, "direct"))
        self.assertNotIn("Job runner uses an external service.", make_prompt(self.actor, "observe"))

    def test_restricted_review_receives_no_complete_windows(self):
        observations = compile_observations(self.observations(self.observation), self.actor)["packets"]
        payload = json.loads(make_prompt(self.actor, "restricted", observations).split("\n\n", 1)[1])
        self.assertNotIn("windows", payload["packets"][0])
        self.assertEqual(len(payload["packets"][0]["observations"]), 1)

    def test_foreign_and_fabricated_quotes_are_excluded(self):
        foreign = {**self.observation, "subject": span("foreign", "This capability")}
        invented = {**self.observation, "subject": span("w2", "Hypothetical operation")}
        compiled = compile_observations(self.observations(foreign, invented, self.observation), self.actor)
        self.assertEqual(len(compiled["rejected"]), 2)
        self.assertEqual(len(compiled["packets"]["p"]["observations"]), 1)

    def test_demonstrative_cannot_be_marked_named(self):
        false_name = {**self.observation, "identity": "named"}
        compiled = compile_observations(self.observations(false_name), self.actor)
        self.assertEqual(len(compiled["rejected"]), 1)
        self.assertEqual(compiled["packets"]["p"]["observations"], [])

    def test_named_observation_uses_both_windows(self):
        named = {**self.observation, "identity": "named", "subject": span("w1", "Job runner")}
        compiled = compile_observations(self.observations(named), self.actor)["packets"]
        key = compiled["p"]["observations"][0]["id"]
        result = normalize_review(self.decisions([key]), self.actor, compiled, enforce_identity=True)
        self.assertEqual(result["c1"]["witnesses"], ["w1", "w2"])

    def test_unnamed_fact_can_support_the_unnamed_claim(self):
        compiled = compile_observations(self.observations(self.observation), self.actor)["packets"]
        key = compiled["p"]["observations"][0]["id"]
        result = normalize_review(self.decisions([key]), self.actor, compiled, enforce_identity=True)
        self.assertEqual(result["c1"]["verdict"], "unresolved")
        self.assertEqual(result["c1"]["witnesses"], [])
        self.assertTrue(result["c1"]["identity_downgrade"])
        self.assertEqual(result["c2"]["verdict"], "supported")
        self.assertEqual(result["c2"]["witnesses"], ["w2"])

    def test_observation_order_and_duplicates_preserve_the_index(self):
        named = {**self.observation, "identity": "named", "subject": span("w1", "Job runner")}
        first = compile_observations(self.observations(self.observation, named), self.actor)
        second = compile_observations(self.observations(named, self.observation, named), self.actor)
        self.assertEqual(first, second)

    def test_citation_match_is_exact_and_window_local(self):
        self.assertEqual(bind_span(span("w", "raw"), {"w": "raw raw"})["offsets"], [0, 4])
        with self.assertRaisesRegex(ValueError, "not an exact substring"):
            bind_span(span("w", "RAW"), {"w": "raw raw"})

    def test_duplicate_model_fields_and_decisions_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Repeated JSON property"):
            parse('{"id":"a","id":"b"}')
        decisions = self.decisions(["w1"])
        decisions["decisions"][1]["id"] = "c1"
        with self.assertRaisesRegex(ValueError, "Unknown or repeated ID"):
            normalize_review(decisions, self.actor)

    def test_foreign_evidence_rejects_model_decision(self):
        with self.assertRaisesRegex(ValueError, "Invalid verdict"):
            normalize_review(self.decisions(["foreign"]), self.actor)

    def test_correct_verdict_with_extra_window_fails_joint_score(self):
        result = normalize_review(self.decisions(["w1", "w2"]), self.actor)
        gold = {"c1": {"packet": "p", "case": "x", "verdict": "supported", "witnesses": [["w1"]]}}
        row = score(result, gold)["c1"]
        self.assertTrue(row["verdict_correct"])
        self.assertFalse(row["complete"])

    def test_frozen_source_locations_and_oracle_partition(self):
        fixture = load(ROOT / "fixtures.json")
        batches = render_inputs(fixture, load_sources(fixture["sources"]))
        self.assertEqual([len(row["oracle"]) for row in batches.values()], [16, 17])
        for row in batches.values():
            first_stage = make_prompt(row["actor"], "observe")
            for case in row["oracle"].values():
                self.assertNotIn(case["case"], first_stage)
                if "missing" in case:
                    self.assertNotIn(case["missing"], first_stage)


if __name__ == "__main__":
    unittest.main()
