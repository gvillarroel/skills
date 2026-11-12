#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise message lifecycle and malformed-stream boundaries without a host."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("a2ui_checker", HERE / "check_a2ui.py")
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def stream():
    return [
        {"version": "v0.9", "createSurface": {"surfaceId": "tasks", "catalogId": "https://example.invalid/catalog"}},
        {"version": "v0.9", "updateComponents": {"surfaceId": "tasks", "components": [
            {"id": "root", "component": "MaterialColumn", "children": ["title"]},
            {"id": "title", "component": "MaterialText", "text": "Ready"}]}},
        {"version": "v0.9", "updateDataModel": {"surfaceId": "tasks", "path": "/", "value": {"ready": True}}},
    ]


class MessageChecks(unittest.TestCase):
    def codes(self, messages):
        return {finding["code"] for finding in CHECKER.check_messages(messages)["findings"]}

    def test_valid_payload_does_not_claim_schema_or_paint(self):
        result = CHECKER.check_messages(stream())
        self.assertTrue(result["passed"])
        self.assertFalse(result["catalog_schema_validated"])
        self.assertFalse(result["host_paint_tested"])

    def test_template_fits_profile(self):
        messages = json.loads((HERE.parent / "assets/templates/status-panel.json").read_text())
        self.assertTrue(CHECKER.check_messages(messages)["passed"])

    def test_update_requires_live_surface(self):
        self.assertIn("unknown-surface", self.codes(stream()[1:]))

    def test_duplicate_create_is_rejected(self):
        messages = stream()
        messages.append(copy.deepcopy(messages[0]))
        self.assertIn("duplicate-surface", self.codes(messages))

    def test_delete_then_recreate_is_valid(self):
        messages = stream()
        messages.append({"version": "v0.9", "deleteSurface": {"surfaceId": "tasks"}})
        messages.extend(stream())
        self.assertTrue(CHECKER.check_messages(messages)["passed"])

    def test_deleted_surface_cannot_receive_model_updates(self):
        messages = stream()
        messages.insert(2, {"version": "v0.9", "deleteSurface": {"surfaceId": "tasks"}})
        self.assertIn("unknown-surface", self.codes(messages))

    def test_root_duplicates_and_dangling_children(self):
        for change, expected in [
            (lambda nodes: nodes.pop(0), "missing-root"),
            (lambda nodes: nodes.append(copy.deepcopy(nodes[0])), "duplicate-id"),
            (lambda nodes: nodes[0].update(children=["missing"]), "unresolved-child"),
        ]:
            with self.subTest(expected=expected):
                messages = stream()
                change(messages[1]["updateComponents"]["components"])
                self.assertIn(expected, self.codes(messages))

    def test_cycles_do_not_recurse_forever(self):
        messages = stream()
        messages[1]["updateComponents"]["components"][1]["children"] = ["root"]
        self.assertIn("component-cycle", self.codes(messages))

    def test_versions_and_extra_operations_are_rejected(self):
        messages = stream()
        messages[0]["version"] = "v1.0"
        self.assertIn("unsupported-version", self.codes(messages))
        messages = stream()
        messages[0]["deleteSurface"] = {"surfaceId": "tasks"}
        self.assertIn("invalid-operation", self.codes(messages))

    def test_model_paths_and_null_values(self):
        for path, valid in [("", True), ("/", True), ("/a~0b~1c", True), ("invalid", False), ("/bad~2", False), (None, False)]:
            with self.subTest(path=path):
                messages = stream()
                messages[-1]["updateDataModel"].update(path=path, value=None)
                self.assertEqual("invalid-path" not in self.codes(messages), valid)

    def test_non_object_input_and_dynamic_children_fail_cleanly(self):
        for messages in [None, {}, [], [None], [4], ["bad"]]:
            self.assertFalse(CHECKER.check_messages(messages)["passed"])
        messages = stream()
        messages[1]["updateComponents"]["components"][0]["children"] = {"path": "/rows"}
        self.assertIn("unsupported-children", self.codes(messages))

    def test_cli_writes_exact_report_and_fails_invalid_input(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            source, output = root / "bad.json", root / "reports/result.json"
            source.write_text('{"bad": true}', encoding="utf-8")
            result = subprocess.run([sys.executable, str(HERE / "check_a2ui.py"), str(source), "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout), json.loads(output.read_text()))
            self.assertFalse(json.loads(output.read_text())["passed"])


if __name__ == "__main__":
    unittest.main()
