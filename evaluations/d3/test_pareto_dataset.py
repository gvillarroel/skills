#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the sealed D3 Pareto datasets and final-holdout separation."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest


EXPECTED_SPLITS = {"development": 5, "validation": 3, "holdout": 4}
EXPECTED_ROUTES = {"visualization", "logo", "recomposition", "evaluation"}
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


def instruction_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split(PUBLIC_CONTRACT_MARKER, 1)[0].strip()


class ParetoDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("D3_PARETO_DATASET_ROOT")
        if not configured:
            raise unittest.SkipTest("D3_PARETO_DATASET_ROOT is not set")
        cls.root = Path(configured).resolve()
        cls.manifest = json.loads(
            (cls.root / "dataset-manifest.json").read_text(encoding="utf-8")
        )

    def task_roots(self, split: str) -> list[Path]:
        return sorted(path for path in (self.root / split).iterdir() if path.is_dir())

    def test_manifest_contract_and_objective_weights(self) -> None:
        self.assertEqual(self.manifest["schemaVersion"], 3)
        self.assertEqual(self.manifest["attempts"], 2)
        self.assertEqual(self.manifest["stats"]["splitCounts"], EXPECTED_SPLITS)
        self.assertEqual(self.manifest["stats"]["taskCount"], 12)
        self.assertEqual(self.manifest["stats"]["burnedHoldoutTaskIdOverlap"], 0)
        self.assertEqual(self.manifest["stats"]["burnedHoldoutInstructionOverlap"], 0)
        profile = self.manifest["bundleProfile"]
        self.assertAlmostEqual(profile["semanticWeight"] + profile["bundleWeight"], 1.0)
        self.assertAlmostEqual(sum(profile["progressiveDisclosureWeights"].values()), 1.0)
        self.assertAlmostEqual(sum(profile["bundleEfficiencyWeights"].values()), 1.0)
        self.assertGreater(profile["semanticWeight"], profile["bundleWeight"])

    def test_split_digests_are_current_and_disjoint(self) -> None:
        observed = {split: tree_digest(self.root / split) for split in EXPECTED_SPLITS}
        self.assertEqual(observed, self.manifest["splitDigests"])
        self.assertEqual(len(set(observed.values())), len(observed))

    def test_task_counts_and_ids_are_unique(self) -> None:
        task_ids: list[str] = []
        for split, expected in EXPECTED_SPLITS.items():
            roots = self.task_roots(split)
            self.assertEqual(len(roots), expected, split)
            task_ids.extend(path.name for path in roots)
        self.assertEqual(len(task_ids), len(set(task_ids)))

    def test_visible_and_holdout_routes_are_complete(self) -> None:
        routes: dict[str, set[str]] = {}
        for split in EXPECTED_SPLITS:
            routes[split] = {
                json.loads((root / "tests" / "contract.json").read_text(encoding="utf-8"))["route"]
                for root in self.task_roots(split)
            }
        self.assertEqual(routes["development"] | routes["validation"], EXPECTED_ROUTES)
        self.assertEqual(routes["holdout"], EXPECTED_ROUTES)

    def test_job_configs_are_bound_to_one_split(self) -> None:
        normalized_root = self.root.as_posix()
        for split in EXPECTED_SPLITS:
            config = (self.root / f"{split}-job.yaml").read_text(encoding="utf-8")
            self.assertIn(f"{normalized_root}/{split}", config)
            for other in EXPECTED_SPLITS:
                if other != split:
                    self.assertNotIn(f"{normalized_root}/{other}", config)
            self.assertIn("skill_source_dir:", config)

    def test_prompts_disclose_every_verifier_contract_field(self) -> None:
        for split in EXPECTED_SPLITS:
            for task_root in self.task_roots(split):
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
                expected["bundleProfile"] = contract["bundleProfile"]
                self.assertEqual(disclosed, expected, task_root.name)

    def test_new_tasks_do_not_reuse_burned_holdout(self) -> None:
        configured = os.environ.get("D3_BURNED_HOLDOUT_ROOT")
        if not configured:
            self.skipTest("D3_BURNED_HOLDOUT_ROOT is not set")
        burned_root = Path(configured).resolve()
        burned_ids = {path.name for path in burned_root.iterdir() if path.is_dir()}
        new_ids = {
            root.name
            for split in EXPECTED_SPLITS
            for root in self.task_roots(split)
        }
        self.assertFalse(new_ids & burned_ids)
        burned_hashes = {
            hashlib.sha256(instruction_body(path / "instruction.md").encode("utf-8")).hexdigest()
            for path in burned_root.iterdir()
            if path.is_dir() and (path / "instruction.md").is_file()
        }
        new_hashes = {
            hashlib.sha256(instruction_body(root / "instruction.md").encode("utf-8")).hexdigest()
            for split in EXPECTED_SPLITS
            for root in self.task_roots(split)
        }
        self.assertFalse(new_hashes & burned_hashes)
        self.assertEqual(tree_digest(burned_root), self.manifest["burnedHoldoutTreeDigest"])

    def test_holdout_policy_is_final_only(self) -> None:
        policy = self.manifest["holdoutPolicy"].casefold()
        self.assertIn("never expose", policy)
        self.assertIn("release once", policy)
        self.assertIn("digest-frozen winner", policy)


if __name__ == "__main__":
    unittest.main()
