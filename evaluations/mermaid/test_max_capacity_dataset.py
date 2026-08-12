#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import importlib.util
import json
import re
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
    def test_v6_profile_reclassifies_v5_holdout_and_seals_new_families(self) -> None:
        tasks = builder.TASK_PROFILES["max-capacity-v6-pareto"]
        development = [task for task in tasks if task.split == "development"]
        holdout = [task for task in tasks if task.split == "holdout"]
        self.assertEqual(len(development), 18)
        self.assertEqual(len(holdout), 3)
        self.assertEqual(len({task.task_id for task in tasks}), 21)
        self.assertEqual(len({task.prompt for task in tasks}), 21)
        self.assertTrue(
            {task.family for task in development}.isdisjoint(
                task.family for task in holdout
            )
        )
        self.assertEqual(
            {task.family for task in holdout},
            {"requirementDiagram", "quadrantChart", "eventmodeling"},
        )

    def test_v6_holdout_is_fresh_against_every_prior_capacity_profile(self) -> None:
        holdout = {
            task.task_id: task
            for task in builder.TASK_PROFILES["max-capacity-v6-pareto"]
            if task.split == "holdout"
        }
        prior = tuple(builder.TASK_PROFILES["max-capacity-v1"])
        prior += tuple(builder.TASK_PROFILES["max-capacity-v2"])
        prior += tuple(builder.TASK_PROFILES["max-capacity-v3-pareto"])
        prior += tuple(builder.TASK_PROFILES["max-capacity-v4-pareto"])
        prior += tuple(builder.TASK_PROFILES["max-capacity-v5-pareto"])
        self.assertTrue(set(holdout).isdisjoint(task.task_id for task in prior))
        self.assertTrue(
            {task.prompt for task in holdout.values()}.isdisjoint(
                task.prompt for task in prior
            )
        )

    def test_v6_holdout_reaches_each_family_capacity(self) -> None:
        capacity_by_family = {
            case["id"]: case["fixtureElementCount"] for case in manifest["families"]
        }
        holdout = [
            task
            for task in builder.TASK_PROFILES["max-capacity-v6-pareto"]
            if task.split == "holdout"
        ]
        self.assertEqual(
            {task.family: capacity_by_family[task.family] for task in holdout},
            {"requirementDiagram": 9, "quadrantChart": 4, "eventmodeling": 5},
        )
        requirement = next(
            task for task in holdout if task.family == "requirementDiagram"
        )
        self.assertEqual(len(requirement.patterns), 17)
        for role in builder.SEMANTIC_CLASS_ROLES:
            self.assertTrue(any(role in pattern for pattern in requirement.patterns))
        eventmodeling = next(
            task for task in holdout if task.family == "eventmodeling"
        )
        self.assertEqual(len(eventmodeling.patterns), 5)
        self.assertTrue(all("tf" in pattern for pattern in eventmodeling.patterns))

    def test_v6_exposed_prompts_encode_layout_and_visible_id_repairs(self) -> None:
        exposed = {
            task.family: task
            for task in builder.MAX_CAPACITY_V6_DEVELOPMENT_TASKS
            if task.task_id.startswith("capacity-v6-dev-exposed-")
        }
        self.assertIn("top-to-bottom", exposed["swimlane"].prompt)
        self.assertIn("visible state labels", exposed["stateDiagram"].prompt)
        self.assertIn("top-to-bottom", exposed["erDiagram"].prompt)

    def test_v5_profile_reclassifies_v4_holdout_and_seals_new_families(self) -> None:
        tasks = builder.TASK_PROFILES["max-capacity-v5-pareto"]
        development = [task for task in tasks if task.split == "development"]
        holdout = [task for task in tasks if task.split == "holdout"]
        self.assertEqual(len(development), 15)
        self.assertEqual(len(holdout), 3)
        self.assertEqual(len({task.task_id for task in tasks}), 18)
        self.assertEqual(len({task.prompt for task in tasks}), 18)
        self.assertTrue(
            {task.family for task in development}.isdisjoint(
                task.family for task in holdout
            )
        )
        self.assertEqual(
            {task.family for task in holdout},
            {"swimlane", "stateDiagram", "erDiagram"},
        )

    def test_v5_holdout_is_fresh_against_every_prior_capacity_profile(self) -> None:
        holdout = {
            task.task_id: task
            for task in builder.TASK_PROFILES["max-capacity-v5-pareto"]
            if task.split == "holdout"
        }
        prior = tuple(builder.TASK_PROFILES["max-capacity-v1"])
        prior += tuple(builder.TASK_PROFILES["max-capacity-v2"])
        prior += tuple(builder.TASK_PROFILES["max-capacity-v3-pareto"])
        prior += tuple(builder.TASK_PROFILES["max-capacity-v4-pareto"])
        self.assertTrue(set(holdout).isdisjoint(task.task_id for task in prior))
        self.assertTrue(
            {task.prompt for task in holdout.values()}.isdisjoint(
                task.prompt for task in prior
            )
        )

    def test_v5_holdout_reaches_the_nine_role_semantic_boundary(self) -> None:
        capacity_by_family = {
            case["id"]: case["fixtureElementCount"] for case in manifest["families"]
        }
        terminal_labels = {
            "swimlane": "Work checkpoint 09",
            "stateDiagram": "LifecycleState09",
            "erDiagram": "DOMAIN_09",
        }
        holdout = [
            task
            for task in builder.TASK_PROFILES["max-capacity-v5-pareto"]
            if task.split == "holdout"
        ]
        for task in holdout:
            self.assertEqual(capacity_by_family[task.family], 9, task.task_id)
            self.assertNotIn(terminal_labels[task.family], task.prompt)
            for role in builder.SEMANTIC_CLASS_ROLES:
                self.assertIn(role, task.required_terms, task.task_id)
                self.assertTrue(
                    any(role in pattern for pattern in task.patterns),
                    f"{task.task_id} does not bind {role}",
                )

    def test_v5_exposed_tasks_encode_family_specific_assignment_forms(self) -> None:
        exposed = {
            task.family: task
            for task in builder.MAX_CAPACITY_V5_DEVELOPMENT_TASKS
            if task.task_id.startswith("capacity-v5-dev-exposed-")
        }
        self.assertIn("`:::`", exposed["classDiagram"].prompt)
        self.assertIn("`:::`", exposed["flowchart"].prompt)
        self.assertIn("do not use inline `:::`", exposed["block"].prompt)
        self.assertTrue(all(task.maximum_aspect_ratio <= 8 for task in exposed.values()))

    def test_v5_gantt_contract_accepts_both_renderable_combined_orders(self) -> None:
        gantt = next(
            task
            for task in builder.MAX_CAPACITY_V5_DEVELOPMENT_TASKS
            if task.task_id == "capacity-v4-dev-exposed-gantt-roles-extended"
        )
        for source in (
            "Running blocker :crit, active, running_blocker, 2044-02-05, 1d",
            "Running blocker :active, crit, running_blocker, 2044-02-05, 1d",
        ):
            self.assertRegex(source, re.compile(gantt.patterns[4], re.IGNORECASE))
        for source in (
            "Finished blocker :crit, done, finished_blocker, 2044-02-06, 1d",
            "Finished blocker :done, crit, finished_blocker, 2044-02-06, 1d",
        ):
            self.assertRegex(source, re.compile(gantt.patterns[5], re.IGNORECASE))

    def test_v4_profile_reclassifies_v3_holdout_and_seals_new_families(self) -> None:
        tasks = builder.TASK_PROFILES["max-capacity-v4-pareto"]
        development = [task for task in tasks if task.split == "development"]
        holdout = [task for task in tasks if task.split == "holdout"]
        self.assertEqual(len(development), 12)
        self.assertEqual(len(holdout), 3)
        self.assertEqual(len({task.task_id for task in tasks}), 15)
        self.assertEqual(len({task.prompt for task in tasks}), 15)
        self.assertTrue(
            {task.family for task in development}.isdisjoint(
                task.family for task in holdout
            )
        )
        self.assertEqual(
            {task.family for task in holdout},
            {"flowchart", "classDiagram", "block"},
        )

    def test_v4_holdout_is_fresh_against_every_prior_capacity_profile(self) -> None:
        holdout = {
            task.task_id: task
            for task in builder.TASK_PROFILES["max-capacity-v4-pareto"]
            if task.split == "holdout"
        }
        prior = tuple(builder.TASK_PROFILES["max-capacity-v1"])
        prior += tuple(builder.TASK_PROFILES["max-capacity-v2"])
        prior += tuple(builder.TASK_PROFILES["max-capacity-v3-pareto"])
        self.assertTrue(set(holdout).isdisjoint(task.task_id for task in prior))
        self.assertTrue(
            {task.prompt for task in holdout.values()}.isdisjoint(
                task.prompt for task in prior
            )
        )

    def test_v4_holdout_reaches_the_nine_role_semantic_boundary(self) -> None:
        capacity_by_family = {
            case["id"]: case["fixtureElementCount"] for case in manifest["families"]
        }
        terminal_labels = {
            "flowchart": "Pipeline checkpoint 09",
            "classDiagram": "ServiceRole09",
            "block": "Delivery tile 09",
        }
        holdout = [
            task
            for task in builder.TASK_PROFILES["max-capacity-v4-pareto"]
            if task.split == "holdout"
        ]
        for task in holdout:
            self.assertEqual(len(task.patterns), 9, task.task_id)
            self.assertEqual(capacity_by_family[task.family], 9, task.task_id)
            self.assertNotIn(terminal_labels[task.family], task.prompt)
            for role in builder.SEMANTIC_CLASS_ROLES:
                self.assertIn(role, task.required_terms, task.task_id)

    def test_v4_exposed_sankey_contract_states_every_expected_weight(self) -> None:
        sankey = next(
            task
            for task in builder.MAX_CAPACITY_V4_DEVELOPMENT_TASKS
            if task.task_id == "capacity-v4-dev-exposed-sankey-extended"
        )
        for weight in (80, 70, 60, 50, 40, 30, 20):
            self.assertIn(f"`{weight}`", sankey.prompt)

    def test_v3_profile_reclassifies_exposed_cases_and_seals_new_families(self) -> None:
        tasks = builder.TASK_PROFILES["max-capacity-v3-pareto"]
        development = [task for task in tasks if task.split == "development"]
        holdout = [task for task in tasks if task.split == "holdout"]
        self.assertEqual(len(development), 9)
        self.assertEqual(len(holdout), 3)
        self.assertEqual(len({task.task_id for task in tasks}), 12)
        self.assertEqual(len({task.prompt for task in tasks}), 12)
        self.assertTrue(
            {task.family for task in development}.isdisjoint(
                task.family for task in holdout
            )
        )
        self.assertEqual(
            {task.family for task in holdout}, {"sankey", "xyChart", "gantt"}
        )

    def test_v3_holdout_is_disjoint_from_every_prior_capacity_profile(self) -> None:
        holdout = {
            task.task_id: task
            for task in builder.TASK_PROFILES["max-capacity-v3-pareto"]
            if task.split == "holdout"
        }
        prior = tuple(builder.TASK_PROFILES["max-capacity-v1"]) + tuple(
            builder.TASK_PROFILES["max-capacity-v2"]
        )
        self.assertTrue(set(holdout).isdisjoint(task.task_id for task in prior))
        self.assertTrue(
            {task.prompt for task in holdout.values()}.isdisjoint(
                task.prompt for task in prior
            )
        )

    def test_v3_holdout_contracts_reach_configured_or_semantic_boundaries(self) -> None:
        holdout = {
            task.family: task
            for task in builder.TASK_PROFILES["max-capacity-v3-pareto"]
            if task.split == "holdout"
        }
        self.assertEqual(
            sum(term.startswith("Transfer node ") for term in holdout["sankey"].required_terms),
            8,
        )
        self.assertEqual(len(holdout["xyChart"].patterns), 6)
        self.assertEqual(len(holdout["gantt"].patterns), 6)
        self.assertNotIn("Transfer node 08", holdout["sankey"].prompt)

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
