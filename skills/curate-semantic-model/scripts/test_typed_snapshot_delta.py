#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


CLI = Path(__file__).with_name("compare_document_versions.py")
CLASS_LINES = ["Parcel is a class.", "Item is a class.", "Signature is a class."]


def citation(line, quote):
    return {"start_line": line, "end_line": line, "quote": quote}


def inventory():
    return {
        "classes": [
            {"id": label.lower(), "label": label, "evidence": citation(i, quote)}
            for i, (label, quote) in enumerate(zip(("Parcel", "Item", "Signature"), CLASS_LINES), 1)
        ],
        "subclasses": [],
        "relations": [],
        "constraints": [],
    }


def rule(kind, value, line, quote):
    return {"subject": "parcel", "object": "signature", "predicate": "includes",
            "kind": kind, "value": value, "evidence": citation(line, quote)}


class TestTypedSnapshotCLI(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def invoke(self, pair, base=(), head=(), suffix="", extra=()):
        inputs = {name: self.directory / f"{name}.txt" for name in ("base", "head")}
        for side, lines in (("base", base), ("head", head)):
            inputs[side].write_bytes(("\n".join([*CLASS_LINES, *lines]) + "\n").encode("utf-8"))
        proposal = self.directory / "pair.json"
        proposal.write_text(json.dumps(pair), encoding="utf-8")
        target = self.directory / f"result{suffix}.json"
        run = subprocess.run([sys.executable, "-B", str(CLI), "--base", str(inputs["base"]),
                              "--head", str(inputs["head"]), "--snapshot-pair", str(proposal),
                              "--output", str(target), *extra], capture_output=True, text=True, check=False)
        return run, target

    def success(self, pair, base=(), head=(), suffix=""):
        run, target = self.invoke(pair, base, head, suffix)
        self.assertEqual(run.returncode, 0, (run.stdout, run.stderr))
        payload = json.loads(target.read_bytes())
        summary = json.loads(run.stdout)
        self.assertEqual(summary, {"engine_status": "completed", "semantic_status": "not_run",
                                   "snapshot_status": payload["status"],
                                   **{key: len(payload[key]) for key in ("added", "removed", "modified")}})
        return payload, target.read_bytes()

    def test_equal_semantics_with_renumbered_ids_and_reflowed_evidence(self):
        base, head = inventory(), inventory()
        quote = "Parcel includes Item."
        base["relations"] = [{"subject": "parcel", "object": "item", "predicate": "includes",
                              "evidence": citation(4, quote)}]
        for row in head["classes"]:
            row["id"] = "new_" + row["id"]
        head["classes"].reverse()
        head["relations"] = [{"subject": "new_parcel", "object": "new_item", "predicate": "includes",
                              "evidence": citation(5, quote)}]
        payload, _ = self.success({"base": base, "head": head}, [quote], ["Moved relation", quote])
        self.assertEqual(payload, {"status": "unchanged", "added": [], "removed": [],
                                   "modified": [], "review": None})

    def test_class_identity_is_case_preserving_and_source_ids_are_local(self):
        base, head = inventory(), inventory()
        head["classes"][0].update(label="PARCEL", evidence=citation(4, "PARCEL is a class."))
        payload, _ = self.success({"base": base, "head": head}, [], ["PARCEL is a class."])
        self.assertEqual(payload["added"], [{"collection": "classes", "index": 0}])
        self.assertEqual(payload["removed"], [{"collection": "classes", "index": 0}])

    def test_reversed_subclass_and_relation_are_distinct_operations(self):
        base, head = inventory(), inventory()
        old = ["Item is a kind of Parcel.", "Parcel follows Item."]
        new = ["Parcel is a kind of Item.", "Item follows Parcel."]
        base["subclasses"] = [{"child": "item", "parent": "parcel", "evidence": citation(4, old[0])}]
        head["subclasses"] = [{"child": "parcel", "parent": "item", "evidence": citation(4, new[0])}]
        base["relations"] = [{"subject": "parcel", "object": "item", "predicate": "follows",
                              "evidence": citation(5, old[1])}]
        head["relations"] = [{"subject": "item", "object": "parcel", "predicate": "follows",
                              "evidence": citation(5, new[1])}]
        payload, first = self.success({"base": base, "head": head}, old, new)
        expected = [{"collection": "relations", "index": 0}, {"collection": "subclasses", "index": 0}]
        self.assertEqual(payload, {"status": "changed", "added": expected, "removed": expected,
                                   "modified": [], "review": None})
        _, second = self.success({"head": head, "base": base}, old, new, suffix="-repeat")
        self.assertEqual(first, second)

    def test_polarity_and_cardinality_are_typed_replacements(self):
        base, head = inventory(), inventory()
        old = ["Parcel requires a Signature.", "Parcel has exactly one Signature."]
        new = ["Parcel has exactly two Signatures.", "Parcel forbids a Signature."]
        base["constraints"] = [rule("required", True, 4, old[0]), rule("exact-cardinality", 1, 5, old[1])]
        head["constraints"] = [rule("exact-cardinality", 2, 4, new[0]), rule("forbidden", True, 5, new[1])]
        payload, _ = self.success({"base": base, "head": head}, old, new)
        self.assertEqual(payload["added"], [])
        self.assertEqual(payload["removed"], [])
        self.assertEqual(payload["modified"], [{"collection": "constraints", "before": 1, "after": 0},
                                                {"collection": "constraints", "before": 0, "after": 1}])

    def test_constraint_pairing_keeps_ambiguous_or_different_families_separate(self):
        base, head = inventory(), inventory()
        old = ["Parcel requires a Signature.", "Parcel has at least one Signature.",
               "Parcel has at most three Signatures."]
        new = ["Parcel has exactly two Signatures."]
        base["constraints"] = [rule("required", True, 4, old[0]), rule("min-cardinality", 1, 5, old[1]),
                               rule("max-cardinality", 3, 6, old[2])]
        head["constraints"] = [rule("exact-cardinality", 2, 4, new[0])]
        payload, _ = self.success({"base": base, "head": head}, old, new)
        self.assertEqual(payload["modified"], [])
        self.assertEqual({selector["index"] for selector in payload["removed"]}, {0, 1, 2})
        self.assertEqual(payload["added"], [{"collection": "constraints", "index": 0}])
        base["constraints"] = base["constraints"][:1]
        payload, _ = self.success({"base": base, "head": head}, old, new, suffix="-cross-family")
        self.assertEqual(payload["modified"], [])
        self.assertEqual(payload["removed"], [{"collection": "constraints", "index": 0}])
        self.assertEqual(payload["added"], [{"collection": "constraints", "index": 0}])

    def test_explicit_abstention_retains_caller_reason_and_citations(self):
        reason = "The context is unresolved by this review."
        review = {"reason": reason, "base": [citation(1, CLASS_LINES[0])],
                  "head": [citation(2, CLASS_LINES[1])]}
        base, head = inventory(), inventory()
        head["classes"].pop()
        payload, _ = self.success({"base": base, "head": head, "review": review})
        self.assertEqual(payload, {"status": "abstain", "added": [], "removed": [],
                                   "modified": [], "review": review})
        review["head"][0]["quote"] = "Missing quote."
        run, output = self.invoke({"base": base, "head": head, "review": review}, suffix="-bad-review")
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)["error"]["path"], "/review/head/0")
        self.assertFalse(output.exists())

    def test_invalid_rows_fail_without_writing(self):
        good = inventory()
        variants = {}
        bad_quote = deepcopy(good)
        bad_quote["classes"][0]["evidence"]["quote"] += " Forged."
        variants["quote"] = (bad_quote, "INVALID_SNAPSHOT_EVIDENCE", ())
        bad_line = deepcopy(good)
        bad_line["classes"][0]["evidence"]["start_line"] = True
        variants["line"] = (bad_line, "INVALID_SNAPSHOT_EVIDENCE", ())
        duplicate = deepcopy(good)
        duplicate["classes"].append(duplicate["classes"][0])
        variants["duplicate"] = (duplicate, "INVALID_SNAPSHOT", ())
        collision = deepcopy(good)
        collision["classes"][1]["label"] = " Parcel "
        variants["collision"] = (collision, "INVALID_SNAPSHOT", ())
        dangling = deepcopy(good)
        dangling["relations"].append({"subject": "item", "object": "unknown", "predicate": "contains",
                                      "evidence": citation(1, CLASS_LINES[0])})
        variants["dangling"] = (dangling, "INVALID_SNAPSHOT", ())
        bad_value = deepcopy(good)
        quote = "Parcel has exactly one Signature."
        bad_value["constraints"].append(rule("exact-cardinality", True, 4, quote))
        variants["bool-cardinality"] = (bad_value, "INVALID_SNAPSHOT", (quote,))
        for suffix, (invalid, code, lines) in variants.items():
            with self.subTest(suffix=suffix):
                run, output = self.invoke({"base": good, "head": invalid}, head=lines, suffix=suffix)
                self.assertEqual(run.returncode, 2, run.stderr)
                self.assertEqual(json.loads(run.stdout)["error"]["code"], code)
                self.assertFalse(output.exists())

    def test_conflicting_modes_and_existing_output_fail(self):
        pair = {"base": inventory(), "head": inventory()}
        run, output = self.invoke(pair, extra=("--draft", str(self.directory / "unused.json")))
        self.assertEqual(run.returncode, 2)
        self.assertFalse(output.exists())
        output.write_bytes(b"unchanged bytes")
        run, output = self.invoke(pair)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(output.read_bytes(), b"unchanged bytes")
