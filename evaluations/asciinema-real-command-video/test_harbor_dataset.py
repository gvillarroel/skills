#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the generated live terminal-video Harbor dataset."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest


EXPECTED_SPLITS = {"development": 4, "validation": 4}
PUBLIC_CONTRACT_MARKER = "Public acceptance contract (all fields are requirements):"


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
        configured = os.environ.get("ASCIINEMA_VIDEO_HARBOR_DATASET_ROOT")
        if not configured:
            raise unittest.SkipTest("ASCIINEMA_VIDEO_HARBOR_DATASET_ROOT is not set")
        cls.root = Path(configured).resolve()
        cls.expected_model = os.environ.get(
            "ASCIINEMA_VIDEO_HARBOR_MODEL", "openai-codex/gpt-5.3-codex-spark"
        )
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.manifest = json.loads(
            (cls.root / "dataset-manifest.json").read_text(encoding="utf-8")
        )

    def task_roots(self):
        for split in EXPECTED_SPLITS:
            yield from sorted(path for path in (self.root / split).iterdir() if path.is_dir())

    def test_manifest_profile(self) -> None:
        self.assertEqual(self.manifest["schemaVersion"], 1)
        self.assertEqual(self.manifest["harborVersion"], "0.18.0")
        self.assertEqual(self.manifest["agent"], "pi")
        self.assertEqual(self.manifest["agentAdapter"], "WorkspaceWindowsPi")
        self.assertEqual(self.manifest["piVersion"], "0.84.2")
        self.assertEqual(self.manifest["model"], self.expected_model)
        self.assertEqual(self.manifest["attempts"], 1)
        self.assertEqual(self.manifest["concurrency"], 1)
        self.assertEqual(self.manifest["stats"]["splitCounts"], EXPECTED_SPLITS)
        self.assertEqual(self.manifest["stats"]["taskCount"], 8)
        self.assertEqual(self.manifest["stats"]["tuiCount"], 4)
        self.assertEqual(self.manifest["stats"]["argvCount"], 4)
        self.assertEqual(self.manifest["stats"]["authorizedMutationCount"], 1)

    def test_split_digests_are_current_and_disjoint(self) -> None:
        observed = {split: tree_digest(self.root / split) for split in EXPECTED_SPLITS}
        self.assertEqual(observed, self.manifest["splitDigests"])
        self.assertEqual(len(set(observed.values())), 2)

    def test_task_inventory_and_public_contracts(self) -> None:
        ids: set[str] = set()
        fingerprints: set[str] = set()
        for task_root in self.task_roots():
            self.assertTrue((task_root / "task.toml").is_file())
            instruction = (task_root / "instruction.md").read_text(encoding="utf-8")
            contract = json.loads(
                (task_root / "tests" / "contract.json").read_text(encoding="utf-8")
            )
            self.assertEqual(instruction.count(PUBLIC_CONTRACT_MARKER), 1)
            disclosed = json.loads(
                instruction.split(PUBLIC_CONTRACT_MARKER, 1)[1]
                .split("```json", 1)[1]
                .split("```", 1)[0]
            )
            self.assertEqual(disclosed, contract)
            self.assertEqual(contract["taskId"], task_root.name)
            self.assertNotIn(task_root.name.casefold(), ids)
            ids.add(task_root.name.casefold())
            digest = tree_digest(task_root)
            self.assertNotIn(digest, fingerprints)
            fingerprints.add(digest)
        self.assertEqual(len(ids), 8)

    def test_verifier_is_evaluator_owned_and_identical(self) -> None:
        source = (
            self.repo_root
            / "evaluations"
            / "asciinema-real-command-video"
            / "verify_task.py"
        ).read_bytes()
        source_hash = hashlib.sha256(source).hexdigest()
        for task_root in self.task_roots():
            copied = (task_root / "tests" / "verify_task.py").read_bytes()
            self.assertEqual(hashlib.sha256(copied).hexdigest(), source_hash)

    def test_job_configs_use_pi_and_do_not_cross_splits(self) -> None:
        normalized_root = self.root.as_posix()
        for split in EXPECTED_SPLITS:
            config = (self.root / f"{split}-job.yaml").read_text(encoding="utf-8")
            self.assertIn("WorkspaceWindowsPi", config)
            self.assertIn(self.expected_model, config)
            self.assertIn("delete: false", config)
            self.assertIn('version: "0.84.2"', config)
            self.assertIn('expected_version: "0.84.2"', config)
            self.assertIn("harbor_pi_wrapper.py", config)
            self.assertIn("thinking: high", config)
            self.assertIn("n_concurrent_trials: 1", config)
            self.assertIn("asciinema-real-command-video", config)
            self.assertNotIn("auth.json", config)
            self.assertIn(f"{normalized_root}/{split}", config)
            for other in EXPECTED_SPLITS:
                if other != split:
                    self.assertNotIn(f"{normalized_root}/{other}", config)

    def test_only_winapp_install_authorizes_mutation(self) -> None:
        mutated: list[str] = []
        for task_root in self.task_roots():
            contract = json.loads(
                (task_root / "tests" / "contract.json").read_text(encoding="utf-8")
            )
            if contract["authorizedMutation"] != "none":
                mutated.append(contract["taskId"])
                self.assertEqual(contract["taskId"], "dev-winget-install-winapp")
                self.assertIn("Microsoft.WinAppCli", contract["authorizedMutation"])
        self.assertEqual(mutated, ["dev-winget-install-winapp"])

    def test_no_credentials_are_bundled(self) -> None:
        forbidden_names = {"auth.json", ".env", "credentials.json"}
        for path in self.root.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.name.casefold(), forbidden_names)
                payload = path.read_text(encoding="utf-8", errors="ignore")
                self.assertNotIn("OPENAI_API_KEY=", payload)
                self.assertNotIn("ghp_", payload)


if __name__ == "__main__":
    unittest.main()
