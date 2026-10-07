#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise data-backed shape contracts, graph integration and CLI boundaries."""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from build_generated import build_generated
from build_native import GraphError, document_bytes, package_bytes


def fixture(family: str = "mindMap") -> dict:
    layout = {"id": "generated", "type": family, "position": {"x": 20, "y": 30}, "collectionId": "records", "idField": "id"}
    layout.update({"textField": "name", "parentIdField": "parent"} if family == "mindMap" else {"nameField": "name", "foreignKeyField": "parent"})
    return {"graph": {"title": "Generated family", "nodes": []},
            "collections": [{"id": "records", "values": [{"id": "root", "name": "Root & original", "parent": ""}, {"id": "child", "name": "Child", "parent": "root"}]}],
            "layouts": [layout]}


class GeneratedTests(unittest.TestCase):
    def test_inline_mind_map_preserves_records_and_declares_reflow(self):
        source = fixture()
        document, report = build_generated(source)
        self.assertEqual(document["collections"], source["collections"])
        self.assertEqual(document["pages"][0]["dataBackedShapes"], source["layouts"])
        self.assertEqual(report["generated_layouts"][0]["relationship_count"], 1)
        self.assertIn("not preserved", report["generated_layouts"][0]["geometry"])
        self.assertEqual(report["live_import"], "not executed")

    def test_org_forest_display_fields(self):
        source = fixture("orgChart")
        source["collections"][0]["values"].append({"id": "root2", "name": "Other", "role": "Lead", "email": "own@example.test"})
        source["layouts"][0].update(roleField="role", extraFields=["email"])
        _, report = build_generated(source)
        self.assertEqual(report["generated_layouts"][0]["root_ids"], ["root", "root2"])

    def test_duplicate_keys_dangling_parent_cycles_and_multiple_roots_rejected(self):
        for mutation in ("duplicate", "dangling", "cycle", "roots"):
            source = fixture()
            rows = source["collections"][0]["values"]
            if mutation == "duplicate":
                rows[1]["id"] = "root"
            elif mutation == "dangling":
                rows[1]["parent"] = "absent"
            elif mutation == "cycle":
                rows[0]["parent"] = "child"
            else:
                rows[1]["parent"] = ""
            with self.subTest(mutation=mutation), self.assertRaises(GraphError):
                build_generated(source)

    def test_missing_identity_label_and_nonstring_parent_rejected(self):
        for key in ("id", "name", "parent"):
            source = fixture()
            source["collections"][0]["values"][1][key] = 3
            with self.subTest(key=key), self.assertRaises(GraphError):
                build_generated(source)

    def test_doc_total_limit_includes_shared_collection_reuse(self):
        source = fixture("orgChart")
        source["collections"][0]["values"] = [{"id": str(index), "name": "n"} for index in range(2001)]
        source["layouts"].append(dict(source["layouts"][0], id="second"))
        with self.assertRaisesRegex(GraphError, "4000-item"):
            build_generated(source)

    def test_exact_item_and_markup_limits_pass(self):
        source = fixture("orgChart")
        source["collections"][0]["values"] = [{"id": str(index), "name": "n"} for index in range(4000)]
        _, report = build_generated(source)
        self.assertEqual(report["totals"]["orgChart"], 4000)
        sequence = {"layouts": [{"id": "s", "type": "umlSequence", "position": {"x": 0, "y": 0}, "markup": "x" * 50000}]}
        _, report = build_generated(sequence)
        self.assertEqual(report["generated_layouts"][0]["markup_characters"], 50000)

    def test_dynamic_page_id_collision_rejected(self):
        source = fixture()
        source["graph"]["nodes"] = [{"id": "page1", "type": "rectangle", "x": 0, "y": 0, "width": 10, "height": 10, "label": "n"}]
        for kind in ("layouts", "collections"):
            attempt = deepcopy(source)
            attempt[kind][0]["id"] = "page2"
            with self.subTest(kind=kind), self.assertRaises(GraphError):
                build_generated(attempt)

    def test_huge_numeric_values_and_bad_type_are_clean_errors(self):
        for mode in ("position", "cell", "type"):
            source = fixture()
            if mode == "position":
                source["layouts"][0]["position"]["x"] = 10 ** 400
            elif mode == "cell":
                source["collections"][0]["values"][0]["extra"] = 10 ** 400
            else:
                source["layouts"][0]["type"] = []
            with self.subTest(mode=mode), self.assertRaises(GraphError):
                build_generated(source)

    def test_inline_and_document_byte_caps(self):
        source = fixture()
        source["collections"][0]["values"] = [{"id": str(index), "name": "n", "extra": "x" * 40000} for index in range(26)]
        with self.assertRaisesRegex(GraphError, "1000000-byte"):
            build_generated(source)
        source = {"layouts": [{"id": f"s{index}", "type": "umlSequence", "position": {"x": 0, "y": 0}, "markup": "x" * 50000} for index in range(40)]}
        document, _ = build_generated(source)
        with self.assertRaisesRegex(GraphError, "2000000-byte"):
            document_bytes(document)

    def test_layout_and_collection_id_collisions_rejected(self):
        for kind in ("layouts", "collections"):
            source = fixture()
            source[kind][0]["id"] = "page1"
            with self.subTest(kind=kind), self.assertRaises(GraphError):
                build_generated(source)

    def test_sequence_markup_literal_length_and_external_include(self):
        source = {"layouts": [{"id": "seq", "type": "umlSequence", "position": {"x": 0, "y": 0}, "markup": "@startuml\nA -> B : hello\n@enduml"}]}
        document, report = build_generated(source)
        self.assertEqual(document["pages"][0]["dataBackedShapes"][0]["markup"], source["layouts"][0]["markup"])
        self.assertIn("requires live", report["generated_layouts"][0]["markup_validation"])
        for markup in ("", "a" * 50001, "@startuml\n!includeurl https://example.test/x\n@enduml"):
            source["layouts"][0]["markup"] = markup
            with self.subTest(size=len(markup)), self.assertRaises(GraphError):
                build_generated(source)

    def test_assisted_layout_only_selects_existing_shapes(self):
        source = {"graph": {"nodes": [{"id": "a", "type": "rectangle", "x": 10, "y": 10, "width": 60, "height": 30, "label": "a"}]},
                  "layouts": [{"id": "auto", "type": "assistedLayout", "shapeIds": ["a"]}]}
        document, report = build_generated(source)
        self.assertEqual(report["generated_layouts"][0]["shape_ids"], ["a"])
        self.assertEqual(document["pages"][0]["shapes"][0]["id"], "a")
        source["layouts"][0]["shapeIds"] = ["missing"]
        with self.assertRaises(GraphError):
            build_generated(source)

    def test_unknown_resource_fields_and_nested_cells_rejected(self):
        for mode in ("image", "external", "nested"):
            source = fixture("orgChart")
            if mode == "image":
                source["layouts"][0]["imageUrlField"] = "photo"
            elif mode == "external":
                source["collections"][0]["dataSource"] = "data.csv"
            else:
                source["collections"][0]["values"][0]["nested"] = {"a": 1}
            with self.subTest(mode=mode), self.assertRaises(GraphError):
                build_generated(source)

    def test_deterministic_package_and_source_immutability(self):
        source = fixture()
        original = deepcopy(source)
        document, _ = build_generated(source)
        self.assertEqual(source, original)
        raw = document_bytes(document)
        self.assertEqual(package_bytes(raw), package_bytes(raw))

    def test_cli_exact_outputs_and_no_source_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output, report, doc = (root / name for name in ("input.json", "out.lucid", "ledger.json", "document.json"))
            source.write_text(json.dumps(fixture()), encoding="utf-8")
            command = [sys.executable, str(Path(__file__).with_name("build_generated.py")), str(source), "--output", str(output), "--report", str(report), "--document-json", str(doc)]
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.namelist(), ["document.json"])
                self.assertEqual(archive.read("document.json"), doc.read_bytes())
            self.assertEqual(json.loads(report.read_text(encoding="utf-8"))["live_import"], "not executed")
            command[command.index("--report") + 1] = str(source)
            bad = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(json.loads(source.read_text(encoding="utf-8")), fixture())

    def test_cli_hardlink_alias_does_not_overwrite_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, alias = root / "input.json", root / "alias.json"
            source.write_text(json.dumps(fixture()), encoding="utf-8")
            original = source.read_bytes()
            os.link(source, alias)
            result = subprocess.run([sys.executable, str(Path(__file__).with_name("build_generated.py")), str(source), "--output", str(root / "out.lucid"), "--report", str(alias)], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 2)
            self.assertIn("alias", result.stderr)
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse((root / "out.lucid").exists())


if __name__ == "__main__":
    unittest.main()
