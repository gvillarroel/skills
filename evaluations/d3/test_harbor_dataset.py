#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate a generated D3 Harbor dataset without disclosing task content."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest


EXPECTED_SPLITS = {"development": 3, "validation": 2, "holdout": 5}
PUBLIC_CONTRACT_MARKER = "Public acceptance contract (every field is a task requirement):"
PUBLIC_CONTRACT_SEMANTICS = (
    "Attribute scalars are exact values; an attribute array lists allowed "
    "alternatives, so choose exactly one array member and do not join members."
)


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        payload = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(payload)).encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


class HarborDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("D3_HARBOR_DATASET_ROOT")
        if not configured:
            raise unittest.SkipTest("D3_HARBOR_DATASET_ROOT is not set")
        cls.root = Path(configured).resolve()
        cls.manifest = json.loads(
            (cls.root / "dataset-manifest.json").read_text(encoding="utf-8")
        )

    def test_manifest_contract_and_coverage(self) -> None:
        self.assertEqual(self.manifest["schemaVersion"], 2)
        self.assertEqual(self.manifest["attempts"], 3)
        self.assertEqual(self.manifest["stats"]["splitCounts"], EXPECTED_SPLITS)
        self.assertEqual(
            self.manifest["stats"]["routeCounts"],
            {"evaluation": 2, "logo": 2, "recomposition": 2, "visualization": 4},
        )
        self.assertEqual(
            self.manifest["stats"]["colorsetCounts"],
            {"colorset1": 7, "colorset2": 3},
        )

    def test_split_digests_are_current_and_disjoint(self) -> None:
        observed = {
            split: tree_digest(self.root / split)
            for split in EXPECTED_SPLITS
        }
        self.assertEqual(observed, self.manifest["splitDigests"])
        self.assertEqual(len(set(observed.values())), len(observed))

    def test_task_counts_match_directories(self) -> None:
        for split, expected in EXPECTED_SPLITS.items():
            task_directories = [path for path in (self.root / split).iterdir() if path.is_dir()]
            self.assertEqual(len(task_directories), expected, split)

    def test_job_configs_do_not_cross_splits(self) -> None:
        normalized_root = self.root.as_posix()
        for split in EXPECTED_SPLITS:
            config = (self.root / f"{split}-job.yaml").read_text(encoding="utf-8")
            self.assertIn(f'{normalized_root}/{split}', config)
            for other in EXPECTED_SPLITS:
                if other != split:
                    self.assertNotIn(f'{normalized_root}/{other}', config)
            self.assertIn("skills/d3", config)
            self.assertIn("skill_source_dir:", config)

    def test_prompts_disclose_every_verifier_contract_field(self) -> None:
        for split in EXPECTED_SPLITS:
            for task_root in (self.root / split).iterdir():
                if not task_root.is_dir():
                    continue
                instruction = (task_root / "instruction.md").read_text(encoding="utf-8")
                contract = json.loads(
                    (task_root / "tests" / "contract.json").read_text(encoding="utf-8")
                )
                self.assertEqual(instruction.count(PUBLIC_CONTRACT_MARKER), 1, task_root.name)
                self.assertIn(PUBLIC_CONTRACT_SEMANTICS, instruction, task_root.name)
                fenced = instruction.split(PUBLIC_CONTRACT_MARKER, 1)[1]
                disclosed_text = fenced.split("```json", 1)[1].split("```", 1)[0]
                disclosed = json.loads(disclosed_text)
                expected = {
                    field: contract[field]
                    for field in (
                        "route",
                        "colorset",
                        "expectedPatternId",
                        "requiredTerms",
                        "orderedTerms",
                        "tagMinimums",
                        "classMinimums",
                        "requiredIds",
                        "requiredAttributes",
                        "requiresAnimation",
                        "requiresInteraction",
                        "patterns",
                    )
                    if field in contract
                }
                if "visualPalette" in contract:
                    expected["paintContract"] = {
                        "literalActiveColorsetTokensOnly": True,
                        "forbidFunctionalColorSyntax": True,
                        "requireExtendedToken": bool(contract.get("requireExtended")),
                        "requiredGroups": contract["visualPalette"]["requiredGroups"],
                        "minDistinctVisibleColors": contract["visualPalette"]["minDistinctColors"],
                        "requireVisiblePaletteInfluence": True,
                    }
                self.assertEqual(disclosed, expected, task_root.name)

    def test_holdout_policy_is_final_only(self) -> None:
        policy = self.manifest["holdoutPolicy"].casefold()
        self.assertIn("do not execute or inspect", policy)
        self.assertIn("released once", policy)


if __name__ == "__main__":
    unittest.main()
