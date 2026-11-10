#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib==7.6.0"]
# ///
"""Verify exact line binding and create-only evidence output."""

from copy import deepcopy
from hashlib import sha256
import json
import os
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

    def view(self, *args, source=None, checksum=None, manifest=None):
        pin_args = (["--manifest", str(manifest)] if manifest is not None
                    else ["--sha256", sha256(self.source.read_bytes()).hexdigest()
                          if checksum is None else checksum])
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "lines", "--source-root", str(self.root),
             "--source", self.source.name if source is None else source,
             *pin_args, *args],
            capture_output=True, check=False, env=dict(os.environ) | {"PYTHONIOENCODING": "ascii"},
        )

    def test_numbered_view_matches_physical_line_binding(self):
        result = self.view()
        self.assertEqual(result.returncode, 0, result.stderr)
        view = json.loads(result.stdout)
        self.assertEqual(view["source_sha256"], self.plan["sources"][0]["sha256"])
        self.assertEqual(view["line_count"], 4)
        self.assertEqual(view["lines"], [
            {"line": 1, "text": "\ufeffDébut."},
            {"line": 2, "text": "Clé\u2028intacte."},
            {"line": 3, "text": ""},
            {"line": 4, "text": "Fin."},
        ])
        ranged = self.view("--start-line", "2", "--end-line", "3")
        self.assertEqual(ranged.returncode, 0, ranged.stderr)
        self.assertEqual(json.loads(ranged.stdout)["lines"], view["lines"][1:3])

    def test_numbered_view_handles_empty_and_terminated_sources(self):
        for raw, expected in (
            (b"", []),
            (b"\n", [""]),
            (b"start\rbody\n\nend\r\n", ["start\rbody", "", "end"]),
        ):
            with self.subTest(raw=raw):
                self.source.write_bytes(raw)
                result = self.view()
                self.assertEqual(result.returncode, 0, result.stderr)
                view = json.loads(result.stdout)
                self.assertEqual(view["line_count"], len(expected))
                self.assertEqual([row["text"] for row in view["lines"]], expected)

    def test_numbered_view_checks_path_pin_range_and_existing_output(self):
        for args, kwargs in (
            (("--start-line", "0"), {}),
            (("--start-line", "3", "--end-line", "2"), {}),
            (("--end-line", "5"), {}),
            ((), {"source": "../outside.txt"}),
            ((), {"checksum": "0" * 64}),
        ):
            with self.subTest(args=args, kwargs=kwargs):
                result = self.view(*args, "--output", str(self.output), **kwargs)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertFalse(self.output.exists())
        self.output.write_bytes(b"existing")
        self.assertEqual(self.view("--output", str(self.output)).returncode, 2)
        self.assertEqual(self.output.read_bytes(), b"existing")

    def test_manifest_view_matches_explicit_pin_with_provenance_fields(self):
        manifest = self.root / "manifest.json"
        row = self.plan["sources"][0] | {"source_id": "source", "url": "https://example.org/source"}
        manifest.write_text(json.dumps({"sources": [row], "revision": "frozen"}), encoding="utf-8")
        flags = ("--start-line", "2", "--end-line", "3")
        explicit = self.view(*flags)
        from_manifest = self.view(*flags, manifest=manifest)
        self.assertEqual(explicit.returncode, 0, explicit.stderr)
        self.assertEqual(from_manifest.returncode, 0, from_manifest.stderr)
        self.assertEqual(explicit.stdout, from_manifest.stdout)
        self.assertEqual(self.view("--sha256", row["sha256"], manifest=manifest).returncode, 2)

    def test_manifest_rejects_ambiguous_invalid_and_stale_pins(self):
        manifest = self.root / "manifest.json"
        row = self.plan["sources"][0]
        for raw in (
            b'{"sources":[],"sources":[]}',
            b'{"sources":[]}',
            json.dumps({"sources": [None, row]}).encode(),
            json.dumps({"sources": [row, row]}).encode(),
            json.dumps({"sources": [row | {"path": "unlisted.txt"}]}).encode(),
            json.dumps({"sources": [row | {"sha256": "0" * 65}]}).encode(),
            json.dumps({"sources": [row | {"sha256": "0" * 64}]}).encode(),
        ):
            with self.subTest(raw=raw):
                manifest.write_bytes(raw)
                result = self.view("--output", str(self.output), manifest=manifest)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertFalse(self.output.exists())

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
