#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = Path(__file__).with_name("build_harbor_dataset.py")
MANIFEST_PATH = (
    REPO_ROOT
    / "skills"
    / "mermaid"
    / "assets"
    / "examples"
    / "mermaid-max-elements"
    / "manifest.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "mermaid_max_capacity_dataset_builder", BUILDER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


class MaximumCapacityDatasetTests(unittest.TestCase):
    def test_v2_profile_is_balanced_disjoint_and_unique(self) -> None:
        tasks = builder.TASK_PROFILES["max-capacity-v2"]
        development = [task for task in tasks if task.split == "development"]
        holdout = [task for task in tasks if task.split == "holdout"]
        self.assertEqual(len(development), 3)
        self.assertEqual(len(holdout), 3)
        self.assertEqual(len({task.task_id for task in tasks}), 6)
        self.assertTrue(
            {task.family for task in development}.isdisjoint(
                task.family for task in holdout
            )
        )
        self.assertEqual(len({task.prompt for task in tasks}), 6)

    def test_v2_hidden_contract_counts_match_the_acceptance_manifest(self) -> None:
        capacity_by_family = {
            case["id"]: case["fixtureElementCount"] for case in manifest["families"]
        }
        expected_terms = {
            "radar": "Radar curve ",
            "treemap": "Treemap group ",
            "kanban": "Kanban slot ",
            "timeline": "Timeline slot ",
            "pie": "Pie slot ",
            "venn": "Venn set ",
        }
        for task in builder.TASK_PROFILES["max-capacity-v2"]:
            prefix = expected_terms[task.family]
            observed = sum(term.startswith(prefix) for term in task.required_terms)
            if task.family == "treemap":
                observed += 1  # The named wrapper root owns cScale0.
            self.assertEqual(observed, capacity_by_family[task.family], task.task_id)

    def test_v2_prompts_do_not_disclose_the_hidden_terminal_count(self) -> None:
        forbidden_terminal_labels = {
            "radar": "Radar curve 12",
            "treemap": "Treemap group 11",
            "kanban": "Kanban slot 10",
            "timeline": "Timeline slot 12",
            "pie": "Pie slot 12",
            "venn": "Venn set 08",
        }
        for task in builder.TASK_PROFILES["max-capacity-v2"]:
            self.assertNotIn(forbidden_terminal_labels[task.family], task.prompt)

    def test_v1_profile_remains_available_as_historical_evidence(self) -> None:
        tasks = builder.TASK_PROFILES["max-capacity-v1"]
        self.assertEqual(len(tasks), 6)
        self.assertEqual(
            {task.family for task in tasks},
            {"mindmap", "gitGraph", "journey", "radar", "treemap", "kanban"},
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
