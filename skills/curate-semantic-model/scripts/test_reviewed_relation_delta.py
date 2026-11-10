#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Black-box checks for the source-pinned reviewed relation comparator."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

CLI = Path(__file__).with_name("compare_document_versions.py")


class RelationPairTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = {"base": "X7 means the courier.\nThe courier may dispatch the parcel.\n",
                        "head": "Y9 means the courier.\nThe courier may dispatch the parcel.\n"}
        self.paths = {}
        self.pair_path = self.root / "reviewed.json"
        self.count = 0
        self.pair = {"source_sha256": {}}
        for side, alias in (("base", "X7"), ("head", "Y9")):
            path = self.root / f"{side}.txt"
            raw = self.sources[side].encode()
            path.write_bytes(raw)
            self.paths[side] = path
            self.pair["source_sha256"][side] = sha256(raw).hexdigest()
            lines = self.sources[side].splitlines()
            definition = {"start_line": 1, "end_line": 1, "quote": lines[0]}
            claim = {"start_line": 2, "end_line": 2, "quote": lines[1]}
            self.pair[side] = {
                "entities": {alias: {"id": "urn:role:courier", "evidence": definition},
                             "P": {"id": "urn:object:parcel", "evidence": claim}},
                "predicates": {"P": {"id": "urn:relation:dispatch", "evidence": claim}},
                "relations": [{"subject": alias, "predicate": "P", "object": "P", "evidence": claim,
                               "qualifiers": {"polarity": "positive", "modality": "permitted",
                                              "time": None, "scope": "urn:scope:production"}}],
            }

    def run_cli(self):
        self.count += 1
        output = self.root / f"out-{self.count}.json"
        raw = json.dumps(self.pair).encode()
        self.pair_path.write_bytes(raw)
        proc = subprocess.run([sys.executable, str(CLI), "--base", str(self.paths["base"]),
                               "--head", str(self.paths["head"]), "--relation-pair", str(self.pair_path),
                               "--output", str(output)], capture_output=True, text=True, check=False)
        return proc, output, sha256(raw).hexdigest()

    def result(self):
        proc, output, digest = self.run_cli()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        result = json.loads(output.read_bytes())
        self.assertEqual(result["relation_pair_sha256"], digest)
        return result

    def test_alias_rename_preserves_directed_roles_and_graph_identity(self):
        result = self.result()
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(result["graph_sha256"]["base"], result["graph_sha256"]["head"])
        head = result["relations"]["head"][0]
        self.assertEqual(head["roles"], {"subject": "urn:role:courier", "object": "urn:object:parcel",
                                         "predicate": "urn:relation:dispatch"})
        self.assertEqual(head["local_roles"]["subject"], "Y9")
        self.assertEqual(head["binding_evidence"]["subject"]["quote"], "Y9 means the courier.")
        self.pair["head"]["entities"]["Y9"]["id"] = "urn:role:recipient"
        changed = self.result()
        self.assertEqual((changed["added"], changed["removed"], changed["modified"]), ([0], [0], []))
        self.assertNotEqual(changed["graph_sha256"]["base"], changed["graph_sha256"]["head"])

    def test_single_qualifier_change_links_only_the_unique_role_slot(self):
        row = self.pair["head"]["relations"][0]
        row["qualifiers"].update(modality="required", time={"start": "2026-02-01", "end": "2026-04-01"})
        result = self.result()
        self.assertEqual(result["modified"], [{"before": 0, "after": 0, "qualifiers": ["modality", "time"]}])
        alternative = deepcopy(row)
        alternative["qualifiers"]["scope"] = "urn:scope:staging"
        self.pair["head"]["relations"].append(alternative)
        result = self.result()
        self.assertEqual(result["modified"], [])
        self.assertEqual(set(result["added"]), {0, 1})
        self.assertEqual(result["removed"], [0])

    def test_relation_order_leaves_graph_fingerprint_unchanged(self):
        for side in ("base", "head"):
            alternative = deepcopy(self.pair[side]["relations"][0])
            alternative["qualifiers"]["scope"] = "urn:scope:staging"
            self.pair[side]["relations"].append(alternative)
        self.pair["head"]["relations"].reverse()
        result = self.result()
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(result["graph_sha256"]["base"], result["graph_sha256"]["head"])

    def test_unresolved_role_blocks_the_pair_without_losing_citations(self):
        del self.pair["head"]["entities"]["Y9"]
        result = self.result()
        self.assertEqual(result["status"], "abstain")
        self.assertEqual(result["unresolved"], [{"index": 0, "roles": ["subject"], "side": "head"}])
        self.assertIsNone(result["graph_sha256"])
        self.assertEqual((result["added"], result["removed"], result["modified"]), ([], [], []))
        self.assertEqual(result["relations"]["head"][0]["evidence"]["quote"], self.sources["head"].splitlines()[1])

    def test_stale_source_pin_blocks_valid_citations(self):
        self.paths["head"].write_bytes(self.paths["head"].read_bytes() + b"Uncited change.\n")
        proc, output, _ = self.run_cli()
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)["error"]["code"], "RELATION_PAIR_BINDING_MISMATCH")
        self.assertFalse(output.exists())

    def test_invalid_unicode_ids_fail_before_report_serialization(self):
        row = self.pair["head"]["relations"][0]
        row["qualifiers"]["scope"] = "\ud800"
        proc, output, _ = self.run_cli()
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)["error"]["code"], "INVALID_RELATION_PAIR")
        self.assertFalse(output.exists())

    def test_invalid_dates_and_duplicate_resolved_rows_are_rejected(self):
        row = self.pair["head"]["relations"][0]
        for time in ({"start": "2026-02-30", "end": None}, {"start": "2026-02-01", "end": "2026-02-01"},
                     {"start": None, "end": None}):
            row["qualifiers"]["time"] = time
            proc, output, _ = self.run_cli()
            self.assertEqual(proc.returncode, 2)
            self.assertFalse(output.exists())
        row["qualifiers"]["time"] = None
        alternate = deepcopy(row)
        alternate["subject"] = "Alias"
        self.pair["head"]["entities"]["Alias"] = deepcopy(self.pair["head"]["entities"]["Y9"])
        self.pair["head"]["relations"].append(alternate)
        proc, output, _ = self.run_cli()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Duplicate resolved relation", proc.stdout)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
