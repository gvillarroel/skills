#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression controls for approved premise-reuse plans."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/extract-ontologies/scripts"))
from plan_owl_premise_reuse import compare, plan


def source(*lines):
    return {"id": "policy", "namespace": "urn:test:policy#", "ontology_iri": "urn:test:policy",
            "scope": "Project the archive policy.",
            "segments": [{"id": "term-registry", "text": "Export: Export (class)"}] +
            [{"id": f"p{index:02}", "text": text} for index, text in enumerate(lines, 1)]}


def approved(prior):
    return {"premises": [{"id": row["id"], "axioms": [], "gap": None} for row in prior["segments"][1:]]}


def row(*reads, watches=(), complete=True):
    return {"complete": complete, "reads": list(reads), "watches": list(watches)}


def side(rows, selectors=None):
    return {"rows": rows, "selectors": selectors or {}}


def dispositions(result):
    return {pid: value["action"] for pid, value in result["decisions"].items()}


class ReusePlanTests(unittest.TestCase):
    def setUp(self):
        self.old = source("Archive export is permitted unless held.", "Every export is audited.")
        self.new = source("Archive export is permitted unless held.", "Every export is audited.",
                          "A legal hold overrides the default.")
        self.base = approved(self.old)
        self.review = {
            "before": side({"p01": row(watches=["holds"]), "p02": row()}, {"holds": {"complete": True, "members": []}}),
            "after": side({"p01": row(watches=["holds"]), "p02": row(), "p03": row()},
                          {"holds": {"complete": True, "members": ["p03"]}}),
        }

    def run_plan(self, *, profile_changed=False):
        return compare(self.old, self.new, self.review, self.base, profile_changed=profile_changed)

    def test_first_exception_invalidates_same_text_and_preserves_independent_row(self):
        result = self.run_plan()
        self.assertEqual(dispositions(result), {"p01": "recompute", "p02": "reuse", "p03": "recompute"})
        self.assertEqual(result["decisions"]["p01"]["changed_selectors"], ["holds"])

    def test_unavailable_selector_blocks_unchanged_row(self):
        del self.review["before"]["selectors"]["holds"]
        decision = self.run_plan()["decisions"]["p01"]
        self.assertEqual(decision["reason"], "incomplete-dependency-review")
        self.assertEqual(decision["trace"]["before_gaps"], ["incomplete-selector:holds"])

    def test_transitive_cycle_propagates_edit(self):
        self.old = source("Source definition one.", "Reference to definition.", "Uses the reference.")
        self.new = source("Source definition two.", "Reference to definition.", "Uses the reference.")
        self.base = approved(self.old)
        reviewed = side({"p01": row("p03"), "p02": row("p01"), "p03": row("p02")})
        self.review = {"before": reviewed, "after": reviewed}
        result = self.run_plan()
        self.assertEqual(dispositions(result), {pid: "recompute" for pid in ("p01", "p02", "p03")})
        self.assertEqual(result["decisions"]["p03"]["reason"], "dependency-or-selector-edited")
        identical = compare(self.old, self.old, self.review, self.base, profile_changed=False)
        self.assertEqual(set(dispositions(identical).values()), {"reuse"})

    def test_authoring_profile_or_unresolved_approval_blocks_reuse(self):
        result = self.run_plan(profile_changed=True)
        self.assertEqual(set(dispositions(result).values()), {"recompute"})
        self.assertIn("authoring_profile", result["changed_profile"])
        self.base["premises"][1]["gap"] = "Approval requires a narrower scope."
        self.assertEqual(self.run_plan()["decisions"]["p02"]["reason"], "approved-ledger-row-unresolved")

    def test_renumbered_identical_wording_needs_separate_identity_review(self):
        self.new["segments"][2]["id"] = "p04"
        self.review["after"]["rows"]["p04"] = self.review["after"]["rows"].pop("p02")
        result = self.run_plan()
        self.assertEqual(result["decisions"]["p04"]["reason"], "new-premise")
        self.assertEqual(result["removed_premises"], ["p02"])

    def test_json_pin_binds_exact_bytes_even_after_cosmetic_edit(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            before, after, baseline, review = [root / name for name in ("before", "after", "baseline", "review")]
            for target, value in ((before, self.old), (after, self.new), (baseline, self.base)):
                target.write_bytes(json.dumps(value).encode())
            fields = {"before_source_sha256": before, "after_source_sha256": after,
                      "approved_ledger_sha256": baseline}
            envelope = {name: sha256(path.read_bytes()).hexdigest() for name, path in fields.items()}
            envelope.update(before_profile_sha256="a" * 64, after_profile_sha256="a" * 64,
                            dependencies=self.review)
            review.write_bytes(json.dumps(envelope).encode())
            self.assertEqual(dispositions(plan(before, after, baseline, review))["p02"], "reuse")
            for path in (after, baseline):
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                with self.assertRaisesRegex(ValueError, "exact source and approved ledger bytes"):
                    plan(before, after, baseline, review)
                path.write_bytes(original)

    def test_first_insertion_and_complete_deletion(self):
        empty = source()
        nonempty = source("Every export is audited.")
        empty_review, one_review = side({}), side({"p01": row()})
        inserted = compare(empty, nonempty, {"before": empty_review, "after": one_review},
                           approved(empty), profile_changed=False)
        self.assertEqual(inserted["decisions"]["p01"]["reason"], "new-premise")
        removed = compare(nonempty, empty, {"before": one_review, "after": empty_review},
                          approved(nonempty), profile_changed=False)
        self.assertEqual(removed["removed_premises"], ["p01"])
        self.assertEqual(removed["decisions"], {})

    def test_selector_member_order_is_part_of_the_reviewed_context(self):
        self.new = deepcopy(self.old)
        self.new["segments"][1:] = reversed(self.new["segments"][1:])
        shared = side({"p01": row(watches=["rules"]), "p02": row()},
                      {"rules": {"complete": True, "members": ["p01", "p02"]}})
        self.review = {"before": shared, "after": shared}
        result = self.run_plan()
        self.assertEqual(dispositions(result), {"p02": "reuse", "p01": "recompute"})
        self.assertTrue(result["decisions"]["p01"]["order_changed"])


if __name__ == "__main__":
    unittest.main()
