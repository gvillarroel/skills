#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib==7.6.0"]
# ///
"""Verify exact line binding and create-only evidence output."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

import check_extraction

SCRIPT = Path(check_extraction.__file__)
TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


class EvidenceBindingTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.ontology = self.root / "schema.ttl"
        self.data = self.root / "data.ttl"
        self.source = self.root / "source.txt"
        self.selection = self.root / "selection.json"
        self.output = self.root / "evidence.json"
        self.ontology.write_text(
            "<urn:class:Thing> a <http://www.w3.org/2002/07/owl#Class> .\n", encoding="utf-8"
        )
        self.data.write_text(
            f"<urn:record:first> <{TYPE}> <urn:class:Thing> .\n"
            f"<urn:record:second> <{TYPE}> <urn:class:Thing> .\n", encoding="utf-8"
        )
        self.raw = "\ufeffDébut.\r\nClé\u2028intacte.\r\n\r\nFin.".encode()
        self.source.write_bytes(self.raw)
        self.plan = {
            "sources": [{"id": "source", "path": self.source.name, "sha256": sha256(self.raw).hexdigest()}],
            "assertions": [
                {"subject": "urn:record:first", "predicate": TYPE, "object": {"iri": "urn:class:Thing"},
                 "source_id": "source", "start_line": 1, "end_line": 2},
                {"subject": "urn:record:second", "predicate": TYPE, "object": {"iri": "urn:class:Thing"},
                 "source_id": "source", "start_line": 4, "end_line": 4},
            ],
        }

    def invoke(self, plan, output=None):
        self.selection.write_text(json.dumps(plan), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "bind", "--ontology", str(self.ontology),
             "--data", str(self.data), "--selection", str(self.selection), "--source-root", str(self.root),
             "--output", str(self.output if output is None else output)],
            capture_output=True, text=True, check=False,
        )

    def test_exact_raw_offsets_and_order_independent_output(self):
        result = self.invoke(self.plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.output.read_bytes()
        assertions = json.loads(output)["assertions"]
        self.assertEqual([item["quote"] for item in assertions],
                         ["\ufeffDébut.\r\nClé\u2028intacte.", "Fin."])
        text = self.raw.decode()
        for item in assertions:
            self.assertEqual(text[item["start"]:item["end"]], item["quote"])
        replay = self.root / "replay.json"
        result = self.invoke(self.plan | {"assertions": list(reversed(self.plan["assertions"]))}, replay)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output, replay.read_bytes())

    def test_line_range_and_source_errors_do_not_create_output(self):
        for update in (
            {"start_line": True}, {"start_line": 0}, {"end_line": 5},
            {"start_line": 3, "end_line": 3}, {"source_id": "unknown"},
        ):
            with self.subTest(update=update):
                plan = deepcopy(self.plan)
                plan["assertions"][0].update(update)
                result = self.invoke(plan)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertFalse(self.output.exists())
        self.source.write_bytes(self.raw + b"\n")
        result = self.invoke(self.plan)
        self.assertIn("source SHA-256 mismatch", result.stderr)
        self.assertFalse(self.output.exists())

    def test_unasserted_triple_and_missing_evidence_are_rejected(self):
        plan = deepcopy(self.plan)
        plan["assertions"][0]["subject"] = "urn:record:unasserted"
        self.assertIn("unasserted triple", self.invoke(plan).stderr)
        self.assertFalse(self.output.exists())
        plan["assertions"] = self.plan["assertions"][1:]
        self.assertIn("asserted triple lacks valid evidence", self.invoke(plan).stderr)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_preserved(self):
        self.output.write_bytes(b"existing")
        self.assertEqual(self.invoke(self.plan).returncode, 2)
        self.assertEqual(self.output.read_bytes(), b"existing")


if __name__ == "__main__":
    unittest.main()
