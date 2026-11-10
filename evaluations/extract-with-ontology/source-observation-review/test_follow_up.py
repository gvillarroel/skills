import unittest

from follow_up import allow_empty_context, historical_inputs, unnamed_basis, with_positions
from study import ROOT, compile_observations, load, make_prompt


class FollowUpTests(unittest.TestCase):
    def test_only_omitted_context_is_defaulted(self):
        observer = {"identity": "unnamed", "subject": {"window": "w", "quote": "This capability"},
                    "assertion": {"window": "w", "quote": "uses a service"}}
        extra = {**observer, "unapproved": []}
        unbound = {**observer, "subject": {"window": "w", "quote": "Invented"}}
        reply = {"packets": [{"id": "p", "observations": [observer, extra, unbound], "gaps": []}]}
        actor = [{"id": "p", "windows": [{"id": "w", "text": "This capability uses a service."}]}]
        fixed = allow_empty_context(reply)
        self.assertNotIn("context", observer)
        self.assertNotIn("context", fixed["packets"][0]["observations"][1])
        compiled = compile_observations(fixed, actor)
        self.assertEqual(len(compiled["packets"]["p"]["observations"]), 1)
        self.assertEqual(len(compiled["rejected"]), 2)

    def test_empty_or_named_observations_do_not_establish_an_unnamed_only_basis(self):
        unnamed = {
            "identity": "unnamed", "subject": {"window": "w1"},
            "assertion": {"window": "w1"}, "context": [],
        }
        named = {**unnamed, "identity": "named", "subject": {"window": "w2"}}
        self.assertFalse(unnamed_basis(["w1"], []))
        self.assertTrue(unnamed_basis(["w1"], [unnamed, named]))
        self.assertFalse(unnamed_basis(["w1", "w2"], [unnamed, named]))

    def test_exact_positions_do_not_change_the_frozen_text(self):
        fixture = load(ROOT / "fixtures.json")
        actor = load(ROOT / "run-01" / "b-actor.json")
        amended = with_positions(actor, fixture, "b")
        for before, after in zip(actor, amended, strict=True):
            for window, positioned in zip(before["windows"], after["windows"], strict=True):
                self.assertEqual(window, {key: positioned[key] for key in window})
        self.assertEqual(amended[0]["windows"][0]["document"], amended[0]["windows"][1]["document"])

    def test_history_verifies_receipt_and_omits_claims_from_first_read(self):
        history = historical_inputs()
        for batch in ("a", "b"):
            actor = history[f"{batch}-actor.json"]
            self.assertEqual(len(actor), 4)
            prompt = make_prompt(actor, "observe")
            for packet in actor:
                for claim in packet["claims"]:
                    self.assertNotIn(claim["id"], prompt)
                    self.assertNotIn(claim["text"], prompt)


if __name__ == "__main__":
    unittest.main()
