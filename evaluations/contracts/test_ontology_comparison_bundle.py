#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test stable ordering of admitted comparison bundles."""

from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase, main


HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parents[1] / "skills" / "extract-ontologies" / "scripts" / "choose_owl_comparison_bundle.py"
spec = spec_from_file_location("chooser", SCRIPT)
chooser = module_from_spec(spec)
spec.loader.exec_module(chooser)


class BundleChoiceTests(TestCase):
    def test_new_labels_and_reversed_order_preserve_selected_content(self):
        bundle = ["SubClassOf(:A ObjectComplementOf(:B))", "SubClassOf(:A :C)"]
        rival = ["SubClassOf(:A ObjectIntersectionOf(:C ObjectComplementOf(:B)))"]
        self.assertEqual(chooser.choose({"p": {"c2": rival, "c9": bundle[::-1]}}), {"p": "c9"})
        self.assertEqual(chooser.choose({"p": {"c1": bundle, "c7": rival}}), {"p": "c1"})

    def test_empty_bundle_and_no_candidate_are_distinct(self):
        self.assertEqual(chooser.choose({"context": {"case": []}, "unresolved": {}}),
                         {"context": "case", "unresolved": "NONE"})

    def test_invalid_admitted_inputs_are_rejected(self):
        inputs = ([], {"p": []}, {"p": {"NONE": []}}, {" ": {}}, {"p": {"x": [True]}},
                  {"p": {"x": [""]}}, {"p": {"x": ["A\nB"]}})
        for payload in inputs:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                chooser.choose(payload)
        with self.assertRaises(ValueError):
            json.loads('{"p":{"x":[],"x":["A"]}}', object_pairs_hook=chooser.unique_object)

    def test_cli_emits_deterministic_utf8(self):
        with TemporaryDirectory(dir=HERE) as temporary:
            workspace = Path(temporary)
            source, target = workspace / "candidates.json", workspace / "selected.json"
            source.write_text('{"z":{"α":["é"]},"a":{}}', encoding="utf-8")
            result = run([sys.executable, str(SCRIPT), str(source), "--out", str(target)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_bytes(), '{\n  "a": "NONE",\n  "z": "α"\n}\n'.encode("utf-8"))


if __name__ == "__main__":
    main(verbosity=2)
