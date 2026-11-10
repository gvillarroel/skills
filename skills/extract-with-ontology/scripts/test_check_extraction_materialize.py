#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib==7.6.0"]
# ///
"""Check that a single assertion plan publishes consistent RDF and evidence."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import check_extraction

SCRIPT = Path(check_extraction.__file__)
READING = "urn:example:reading"
LABEL = "urn:example:label"
INTEGER = "http://www.w3.org/2001/XMLSchema#integer"


class ClaimMaterializationTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.ontology = self.root / "schema.ttl"
        self.selection = self.root / "selection.json"
        self.output = self.root / "result"
        raw = "Début\r\nMesure 007.\r\nLabel with a newline.\r\n".encode()
        (self.root / "source.txt").write_bytes(raw)
        datatype_property = "http://www.w3.org/2002/07/owl#DatatypeProperty"
        self.ontology.write_text(
            f"<{READING}> a <{datatype_property}> .\n<{LABEL}> a <{datatype_property}> .\n",
            encoding="utf-8",
        )
        statement = {"subject": "urn:example:meter", "predicate": READING,
                     "object": {"value": "007", "datatype": INTEGER}, "source_id": "report"}
        self.plan = {
            "sources": [{"id": "report", "path": "source.txt", "sha256": sha256(raw).hexdigest()}],
            "assertions": [
                statement | {"start_line": 1, "end_line": 2},
                statement | {"start_line": 2, "end_line": 2},
                statement | {"predicate": LABEL, "object": {"value": 'A "label"\nClé', "language": "FR"},
                             "start_line": 3, "end_line": 3},
            ],
        }

    def invoke(self, plan, output=None, *, manifest=None):
        self.selection.write_text(json.dumps(plan), encoding="utf-8")
        command = [
            sys.executable, "-B", str(SCRIPT), "materialize", "--ontology", str(self.ontology),
            "--selection", str(self.selection), "--source-root", str(self.root),
            "--output-dir", str(self.output if output is None else output),
        ]
        if manifest is not None:
            command.extend(["--manifest", str(manifest)])
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def test_deduplicated_graph_preserves_lexical_terms_and_all_citations(self):
        result = self.invoke(self.plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["asserted_triples"], 2)
        graph = (self.output / "data.ttl").read_bytes()
        self.assertIn(b'"007"^^<', graph)
        self.assertIn(b'"A \\"label\\"\\n', graph)
        self.assertIn(b'"@fr', graph)
        evidence = (self.output / "evidence.json").read_bytes()
        ledger = json.loads(evidence)
        self.assertEqual(len(ledger["assertions"]), 3)
        self.assertEqual(ledger["assertions"][0]["quote"], "Début\r\nMesure 007.")

        replay = self.root / "replay"
        reversed_plan = self.plan | {"assertions": list(reversed(self.plan["assertions"]))}
        self.assertEqual(self.invoke(reversed_plan, replay).returncode, 0)
        self.assertEqual(graph, (replay / "data.ttl").read_bytes())
        self.assertEqual(evidence, (replay / "evidence.json").read_bytes())

    def test_rejects_unbound_or_undeclared_rows_before_creating_files(self):
        for update in (
            {"predicate": "urn:example:unknown"},
            {"subject": "urn:example:invalid\x00iri"},
            {"end_line": 8},
            {"source_id": "unknown"},
        ):
            with self.subTest(update=update):
                plan = deepcopy(self.plan)
                plan["assertions"][0].update(update)
                result = self.invoke(plan)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertFalse(self.output.exists())

    def test_manifest_roster_reproduces_the_explicit_plan(self):
        original = self.invoke(self.plan)
        self.assertEqual(original.returncode, 0, original.stderr)
        source = self.plan["sources"][0]
        entry = {"source_id": source["id"], "path": source["path"], "sha256": source["sha256"],
                 "publisher_url": "https://example.org/report"}
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps({"sources": [entry]}), encoding="utf-8")
        target = self.root / "manifest-result"
        result = self.invoke({"assertions": self.plan["assertions"]}, target, manifest=manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("data.ttl", "evidence.json"):
            self.assertEqual((target / name).read_bytes(), (self.output / name).read_bytes())

    def test_manifest_rejects_competing_rosters_and_invalid_pins(self):
        manifest = self.root / "manifest.json"
        source = self.plan["sources"][0]
        claims = {"assertions": self.plan["assertions"]}
        (self.root / "other.txt").write_bytes(b"changed")
        for plan, sources in (
            (self.plan, [source]),
            (claims, [source | {"source_id": "another"}]),
            (claims, [source | {"id": "unknown"}]),
            (claims, [source, {"id": "unused", "path": "other.txt", "sha256": "0" * 64}]),
        ):
            with self.subTest(plan=plan, sources=sources):
                manifest.write_text(json.dumps({"sources": sources}), encoding="utf-8")
                self.assertEqual(self.invoke(plan, manifest=manifest).returncode, 2)
                self.assertFalse(self.output.exists())

    def test_respects_existing_output_even_for_empty_assertions(self):
        self.output.mkdir()
        marker = self.output / "existing.txt"
        marker.write_bytes(b"keep")
        self.assertEqual(self.invoke(self.plan | {"assertions": []}).returncode, 2)
        self.assertEqual(list(self.output.iterdir()), [marker])
        self.assertEqual(marker.read_bytes(), b"keep")

    def test_failed_second_file_cleans_the_new_directory(self):
        original = Path.open

        def open_with_fault(path, mode="r", *args, **kwargs):
            if path == self.output / "evidence.json" and mode == "xb":
                raise OSError("injected second-file failure")
            return original(path, mode, *args, **kwargs)

        with patch.object(Path, "open", open_with_fault):
            with self.assertRaisesRegex(OSError, "injected"):
                check_extraction.write_claim_bundle(self.output, "", {})
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
