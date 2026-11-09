#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tests for deterministic compilation of document delta proposals."""
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

sys.dont_write_bytecode = True
import compare_document_versions as compare


def row(identifier, before, after, before_lines=None, after_lines=None):
    return {
        "id": identifier,
        "before": {"value": before, "lines": [[1, 1]] if before_lines is None else before_lines},
        "after": {"value": after, "lines": [[1, 1]] if after_lines is None else after_lines},
    }


class CompileObservationsTest(unittest.TestCase):
    def test_typed_values_and_null_control_classification(self):
        draft = {"observations": [
            row("added", None, False, []),
            row("removed", [], None),
            row("modified-bool", False, 0),
            row("modified-number", {"v": 1}, {"v": 1.0}),
            row("modified-array", [1, 2], [2, 1]),
            row("unchanged-null", None, None, [], []),
            row("unchanged-object", {"a": 0, "b": False}, {"b": False, "a": 0}),
        ]}
        result = compare.compile_observations(draft, ["Base"], ["Head"])
        self.assertEqual([item["change"] for item in result["observations"]],
                         ["added", "modified", "modified", "modified", "removed", "unchanged", "unchanged"])
        self.assertEqual(result["observations"][0]["before"], {"value": None, "evidence": []})
        self.assertEqual(result["observations"][4]["after"]["evidence"][0]["quote"], "Head")

    def test_exact_sorted_side_specific_evidence(self):
        draft = {"observations": [row("stable", "same", "same", [[4, 4], [1, 2]], [[2, 2]])]}
        result = compare.compile_observations(draft, ["Indented  ", "  and wrapped", "", "last"],
                                              ["unrelated", "reworded"])
        observation = result["observations"][0]
        self.assertEqual(observation["change"], "unchanged")
        self.assertEqual(observation["before"]["evidence"], [
            {"start_line": 1, "end_line": 2, "quote": "Indented  \n  and wrapped"},
            {"start_line": 4, "end_line": 4, "quote": "last"},
        ])
        self.assertEqual(observation["after"]["evidence"][0]["quote"], "reworded")

    def test_rejects_duplicate_ids_and_invalid_states(self):
        duplicate = row("repeated", True, False)
        with self.assertRaises(compare.EngineError):
            compare.compile_observations({"observations": [duplicate, duplicate]}, ["Base"], ["Head"])
        for state in (None, {"value": False}, {"value": False, "lines": [], "quote": "invented"}):
            with self.subTest(state=state), self.assertRaises(compare.EngineError):
                compare.compile_observations({"observations": [dict(duplicate, before=state)]},
                                              ["Base"], ["Head"])

    def test_rejects_empty_malformed_and_overlapping_evidence(self):
        invalid = ([], [[True, 1]], [[0, 1]], [[2, 1]], [[1, 4]], [[2, 2]],
                   [[1, 3], [3, 3]], [[1, 1], [1, 1]], [[1]], {"start": 1, "end": 1})
        for ranges in invalid:
            with self.subTest(ranges=ranges), self.assertRaises(compare.EngineError):
                compare.compile_observations({"observations": [row("rule", True, False, ranges)]},
                                              ["Base", "", "Other"], ["Head"])

    def test_cli_replay_no_overwrite_and_duplicate_key_rejection(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            base, head, draft = (root / filename for filename in ("base.txt", "head.txt", "draft.json"))
            base.write_bytes("\ufeffBase\r\nMiddle\u2028still middle\r\n".encode("utf-8"))
            head.write_bytes(b"New head\n")
            script = Path(compare.__file__)
            arguments = [sys.executable, str(script), "--base", str(base), "--head", str(head),
                         "--draft", str(draft), "--output"]

            def run(output):
                return subprocess.run([*arguments, str(output)], capture_output=True, check=False, text=True)

            records = [row("one", "same", "same", [[2, 2]]), row("two", 2, 3)]
            draft.write_text(json.dumps({"observations": records}), encoding="utf-8")
            first, second = root / "results" / "first.json", root / "results" / "second.json"
            completed = run(first)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            original = first.read_bytes()
            self.assertEqual(json.loads(original)["observations"][0]["before"]["evidence"][0]["quote"],
                             "Middle\u2028still middle")
            draft.write_text(json.dumps({"observations": records[::-1]}), encoding="utf-8")
            self.assertEqual(run(second).returncode, 0)
            self.assertEqual(second.read_bytes(), original)
            self.assertEqual(run(first).returncode, 2)
            self.assertEqual(first.read_bytes(), original)
            self.assertEqual(run(base).returncode, 2)
            self.assertTrue(base.read_bytes().startswith(b"\xef\xbb\xbf"))
            draft.write_text('{"observations": [], "observations": []}', encoding="utf-8")
            missing = root / "invalid.json"
            result = run(missing)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["error"]["code"], "JSON_DUPLICATE_KEY")
            self.assertFalse(missing.exists())


    def test_cli_rejects_decimal_precision_loss_before_writing(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            old, new, draft, output = (root / name for name in ("old.txt", "new.txt", "draft.json", "out.json"))
            old.write_bytes(b"Old threshold.\n")
            new.write_bytes(b"New threshold.\n")
            draft.write_text(
                '{"observations":[{"id":"threshold","before":{"value":1.0,"lines":[[1,1]]},'
                '"after":{"value":1.0000000000000001,"lines":[[1,1]]}}]}',
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "-P", str(Path(compare.__file__)), "--base", str(old), "--head", str(new),
                 "--draft", str(draft), "--output", str(output)], check=False, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["error"]["code"], "JSON_NUMBER_PRECISION_LOSS")
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
