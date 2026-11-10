#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check exact glossary evidence, unresolved matches and deterministic output."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from compile_glossary_proposals import compile_ledger

CLI = Path(__file__).with_name("compile_glossary_proposals.py")


def proposal(term, value, line, *, kind="definition", lane="entity"):
    return {"kind": kind, "lane": lane, "term": {"quote": term},
            "value": {"quote": value} if value else None,
            "evidence": {"start_line": line, "end_line": line}}


def draft(source, rows):
    return {"source_sha256": sha256(source).hexdigest(), "proposals": rows}


class GlossaryProposalTests(unittest.TestCase):
    def test_distinct_definitions_and_lanes_remain_source_local(self):
        source = b"X7 denotes the gateway device.\nX7 denotes the gateway certificate.\nX7 means to forward.\n"
        rows = [proposal("X7", "the gateway device", 1), proposal("X7", "the gateway certificate", 2),
                proposal("X7", "to forward", 3, lane="predicate")]
        first = compile_ledger(source, draft(source, rows))
        second = compile_ledger(source, draft(source, list(reversed(rows))))
        self.assertEqual(first, second)
        self.assertEqual([entry["value"]["quote"] for entry in first["proposals"]],
                         ["the gateway device", "the gateway certificate", "to forward"])
        self.assertTrue(all(entry["status"] == "candidate" for entry in first["proposals"]))

    def test_exact_token_offsets_require_explicit_repeat_selector(self):
        source = b"C means C at the edge.\n"
        row = proposal("C", "C at the edge", 1)
        with self.assertRaisesRegex(ValueError, "term must locate one exact"):
            compile_ledger(source, draft(source, [row]))
        row["term"]["first_char"] = 0
        result = compile_ledger(source, draft(source, [row]))["proposals"][0]
        self.assertEqual(result["term"], {"quote": "C", "start": 0, "end": 1})
        row["term"]["first_char"] = 8
        with self.assertRaisesRegex(ValueError, "must be separate"):
            compile_ledger(source, draft(source, [row]))
        row["term"] = {"quote": "edge", "first_char": 0}
        with self.assertRaisesRegex(ValueError, "term must locate one exact"):
            compile_ledger(source, draft(source, [row]))

    def test_adjacent_context_selects_a_repeated_term_and_value(self):
        source = b"The example uses Lease for storage, but production uses Lease for storage too.\n"
        row = proposal("Lease", "storage", 1)
        row["term"]["prefix"] = "production uses "
        row["value"]["suffix"] = " too."
        entry = compile_ledger(source, draft(source, [row]))["proposals"][0]
        self.assertEqual(entry["term"]["start"], source.rindex(b"Lease"))
        self.assertEqual(entry["value"]["start"], source.rindex(b"storage"))
        self.assertEqual(entry["term"]["quote"], "Lease")
        self.assertEqual(entry["value"]["quote"], "storage")

        revised = b"Note: " + source
        moved = compile_ledger(revised, draft(revised, [row]))["proposals"][0]
        self.assertEqual(moved["term"]["start"], entry["term"]["start"] + len(b"Note: "))
        self.assertEqual(moved["value"]["start"], entry["value"]["start"] + len(b"Note: "))

    def test_context_and_offsets_must_agree_at_one_exact_occurrence(self):
        source = b"X needs A. X needs A in review.\n"
        row = proposal("X", "A", 1)
        row["term"] |= {"first_char": 0, "suffix": " needs A."}
        row["value"]["prefix"] = "X needs "
        with self.assertRaisesRegex(ValueError, "value must locate one exact"):
            compile_ledger(source, draft(source, [row]))
        row["value"]["suffix"] = "."
        self.assertEqual(compile_ledger(source, draft(source, [row]))["proposals"][0]["term"]["start"], 0)

        for change in (
            {"first_char": source.rindex(b"X")},
            {"prefix": "A. "},
            {"suffix": " needs A in review."},
            {"suffix": ""},
            {"suffix": True},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                modified = row | {"term": row["term"] | change}
                compile_ledger(source, draft(source, [modified]))

    def test_stale_raw_source_and_duplicate_occurrence_are_rejected(self):
        source = b"X means device.\nOther text.\n"
        row = proposal("X", "device", 1)
        with self.assertRaisesRegex(ValueError, "digest does not match"):
            compile_ledger(source+b"Uncited edit.\n", draft(source, [row]))
        broader = row | {"evidence": {"start_line": 1, "end_line": 2}}
        with self.assertRaisesRegex(ValueError, "duplicate source-bound proposal"):
            compile_ledger(source, draft(source, [row, broader]))

    def test_unicode_and_normalized_offsets_preserve_exact_evidence(self):
        source = b"\xef\xbb\xbf" + "Première ligne.\r\nClé signifie secret d’accès.\r\n".encode("utf-8")
        row = proposal("Clé", "secret d’accès", 2)
        output = compile_ledger(source, draft(source, [row]))
        entry = output["proposals"][0]
        self.assertEqual(entry["term"]["start"], len("Première ligne.\n"))
        self.assertEqual(entry["evidence"]["quote"], "Clé signifie secret d’accès.")
        row["term"] = {"quote": "lé"}
        with self.assertRaisesRegex(ValueError, "exact token-aligned"):
            compile_ledger(source, draft(source, [row]))

    def test_combining_marks_preserve_the_whole_source_token(self):
        for term, prefix, suffix in (
            ("cafe\u0301", "cafe", None),
            ("cafe\u0301teria", "cafe\u0301", "teria"),
            ("क\u093e", "क", None),
            ("a\u20dd", "a", None),
        ):
            with self.subTest(term=term):
                value = f"the {term} label"
                source = f"{term} means {value}.\n".encode()
                row = proposal(term, value, 1)
                row["term"]["first_char"] = 0
                entry = compile_ledger(source, draft(source, [row]))["proposals"][0]
                self.assertEqual(entry["term"], {"quote": term, "start": 0, "end": len(term)})
                self.assertEqual(entry["value"]["quote"], value)
                for partial in (prefix, suffix):
                    if partial is None:
                        continue
                    truncated_term = row | {"term": {"quote": partial, "first_char": term.index(partial)}}
                    with self.assertRaisesRegex(ValueError, "token"):
                        compile_ledger(source, draft(source, [truncated_term]))
                truncated_value = row | {"value": {"quote": f"the {prefix}"}}
                with self.assertRaisesRegex(ValueError, "exact token-aligned"):
                    compile_ledger(source, draft(source, [truncated_value]))

    def test_distinct_normalizations_keep_exact_offsets(self):
        source = "cafe, café and cafe\u0301 are three configuration keys.\n".encode()
        terms = ("cafe", "café", "cafe\u0301")
        rows = [proposal(term, None, 1, kind="attestation", lane="unspecified") for term in terms]
        entry = compile_ledger(source, draft(source, rows))["proposals"]
        self.assertEqual([item["term"] for item in entry], [
            {"quote": terms[0], "start": 0, "end": 4},
            {"quote": terms[1], "start": 6, "end": 10},
            {"quote": terms[2], "start": 15, "end": 20},
        ])

    def test_cli_never_overwrites_and_preserves_attestations(self):
        with TemporaryDirectory() as root:
            root = Path(root)
            source, inputs, output = (root / name for name in ("source.txt", "draft.json", "ledger.json"))
            source.write_bytes(b"X appears in this sentence.\n")
            row = proposal("X", None, 1, kind="attestation", lane="unspecified")
            raw = json.dumps(draft(source.read_bytes(), [row])).encode()
            inputs.write_bytes(raw)
            command = [sys.executable, str(CLI), "--source", str(source), "--draft", str(inputs),
                       "--output", str(output)]
            first = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            result = output.read_bytes()
            self.assertIsNone(json.loads(result)["proposals"][0]["value"])
            self.assertEqual(json.loads(result)["draft_sha256"], sha256(raw).hexdigest())
            second = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(output.read_bytes(), result)


if __name__ == "__main__":
    unittest.main()
