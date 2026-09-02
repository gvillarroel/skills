#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for scene content budgets and fidelity ledgers."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = (
    REPO_ROOT
    / "skills"
    / "video"
    / "scripts"
    / "validate_scene_composition_plan.py"
)


def load_validator():
    spec = importlib.util.spec_from_file_location("scene_content_accounting_test", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def valid_scene() -> dict[str, object]:
    return {
        "id": "scene-01",
        "sourceAnchors": ["Gateway"],
        "contentBudget": {
            "mode": "editorial-overview",
            "nodeItems": ["Web", "Mobile", "Gateway", "Workers x2"],
            "edgeItems": [
                {"from": "Web", "to": "Gateway"},
                {"from": "Mobile", "to": "Gateway"},
                {"from": "Gateway", "to": "Workers x2"},
            ],
            "focalItems": ["Gateway"],
            "annotationItems": [],
            "plannedNodeCount": 4,
            "plannedEdgeCount": 3,
            "focalElementCount": 1,
            "overflowStrategy": "Move operational detail to scene-02.",
        },
        "contentAccounting": {
            "sourceItems": ["Web", "Mobile", "Gateway", "Worker A", "Worker B", "Audit"],
            "kept": ["Web", "Mobile", "Gateway"],
            "merged": [
                {
                    "sourceItems": ["Worker A", "Worker B"],
                    "into": "Workers x2",
                    "reason": "The replicas share one role and route.",
                }
            ],
            "omitted": [],
            "movedToDetail": [
                {
                    "item": "Audit",
                    "target": {"kind": "scene", "id": "scene-02"},
                    "reason": "It is secondary to the request path.",
                }
            ],
        },
    }


class ContentAccountingTests(unittest.TestCase):
    def test_valid_partition_passes(self) -> None:
        self.assertEqual(VALIDATOR._validate_content_accounting("scene-01", valid_scene()), [])

    def test_duplicate_and_missing_dispositions_fail(self) -> None:
        scene = valid_scene()
        accounting = scene["contentAccounting"]
        accounting["movedToDetail"] = []
        accounting["omitted"] = [
            {"item": "Gateway", "reason": "Incorrectly removed required anchor."}
        ]

        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        joined = "\n".join(errors)
        self.assertIn("multiple dispositions: Gateway", joined)
        self.assertIn("source items are not accounted for: Audit", joined)

    def test_required_anchor_cannot_be_merged(self) -> None:
        scene = valid_scene()
        accounting = scene["contentAccounting"]
        accounting["kept"].remove("Gateway")
        accounting["merged"][0]["sourceItems"].append("Gateway")

        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        self.assertTrue(
            any("required source anchors present in sourceItems must be kept: Gateway" in error for error in errors)
        )

    def test_local_anchor_cannot_bypass_the_content_ledger(self) -> None:
        scene = valid_scene()
        scene["contentAccounting"]["sourceItems"].remove("Gateway")
        scene["contentAccounting"]["kept"].remove("Gateway")

        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        self.assertTrue(
            any("local source anchors must appear" in error and "Gateway" in error for error in errors)
        )

    def test_editorial_overview_budget_is_bounded(self) -> None:
        scene = valid_scene()
        budget = scene["contentBudget"]
        budget["plannedNodeCount"] = 10
        budget["plannedEdgeCount"] = 13
        budget["focalElementCount"] = 3

        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        joined = "\n".join(errors)
        self.assertIn("plannedNodeCount must not exceed 9", joined)
        self.assertIn("plannedEdgeCount must not exceed 12", joined)
        self.assertIn("focalElementCount must not exceed 2", joined)

    def test_declared_counts_must_match_explicit_drawn_items(self) -> None:
        scene = valid_scene()
        budget = scene["contentBudget"]
        budget["plannedNodeCount"] = 1
        budget["plannedEdgeCount"] = 1
        budget["focalElementCount"] = 0

        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        joined = "\n".join(errors)
        self.assertIn("plannedNodeCount must equal len(nodeItems) (4)", joined)
        self.assertIn("plannedEdgeCount must equal len(edgeItems) (3)", joined)
        self.assertIn("focalElementCount must equal len(focalItems) (1)", joined)

    def test_kept_items_cannot_hide_outside_the_count_basis(self) -> None:
        scene = valid_scene()
        scene["contentAccounting"]["sourceItems"].append("Hidden node")
        scene["contentAccounting"]["kept"].append("Hidden node")

        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        self.assertTrue(
            any("missing from contentBudget count basis" in error and "Hidden node" in error for error in errors)
        )

    def test_budget_and_disposition_text_fields_require_strings(self) -> None:
        scene = valid_scene()
        scene["contentBudget"]["overflowStrategy"] = True
        scene["contentAccounting"]["omitted"] = [
            {"item": 1, "reason": True}
        ]

        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        joined = "\n".join(errors)
        self.assertIn("overflowStrategy must be a non-empty string", joined)
        self.assertIn("needs a non-empty string item", joined)

    def test_moved_required_item_must_be_kept_by_target_scene(self) -> None:
        source = valid_scene()
        source["contentAccounting"]["sourceItems"].append("Audit stream")
        source["contentAccounting"]["movedToDetail"].append(
            {
                "item": "Audit stream",
                "target": {"kind": "scene", "id": "scene-02"},
                "reason": "The detail scene owns audit internals.",
            }
        )
        target = {
            "id": "scene-02",
            "contentAccounting": {
                "sourceItems": ["Audit", "Audit stream"],
                "kept": ["Audit", "Audit stream"],
                "merged": [],
                "omitted": [],
                "movedToDetail": [],
            },
        }

        self.assertEqual(
            VALIDATOR._validate_cross_scene_content_moves(
                [source, target], ["Audit stream"]
            ),
            [],
        )
        target["contentAccounting"]["kept"] = ["Audit"]
        errors = VALIDATOR._validate_cross_scene_content_moves(
            [source, target], ["Audit stream"]
        )
        joined = "\n".join(errors)
        self.assertIn("must be kept by target scene", joined)
        self.assertIn("must be kept in at least one scene", joined)

    def test_global_required_anchor_must_appear_in_a_content_ledger(self) -> None:
        errors = VALIDATOR._validate_cross_scene_content_moves(
            [valid_scene()], ["Gateway", "Missing anchor"]
        )
        self.assertTrue(
            any("absent from all" in error and "Missing anchor" in error for error in errors)
        )

    def test_plan_level_global_anchor_is_part_of_the_accounting_gate(self) -> None:
        plan = {
            "videoDirection": {"sourceAnchors": ["Gateway", "Global only"]},
            "contentTargets": [],
            "scenes": [valid_scene()],
        }
        errors = VALIDATOR.validate_plan(
            plan,
            expect_scenes=None,
            min_scenes=None,
            require_anchors=[],
            forbidden=[],
            allow_held_scenes=False,
            require_strict_alignment=False,
            require_square_edges=False,
            require_validation_contract=False,
            require_zero_box_padding=False,
            require_grayscale_hierarchy=False,
            require_content_accounting=True,
        )
        self.assertTrue(
            any("absent from all" in error and "Global only" in error for error in errors)
        )

    def test_arbitrary_scene_ids_still_require_a_real_target(self) -> None:
        source = valid_scene()
        source["id"] = "shot-01"
        source["contentAccounting"]["movedToDetail"][0]["target"] = {
            "kind": "scene",
            "id": "shot-99",
        }
        errors = VALIDATOR._validate_cross_scene_content_moves([source], [])
        self.assertTrue(any("unknown scene id 'shot-99'" in error for error in errors))

    def test_annotation_items_cannot_launder_an_unbounded_entity_list(self) -> None:
        scene = valid_scene()
        extra_items = [f"Service {index:02d}" for index in range(1, 30)]
        scene["contentAccounting"]["sourceItems"].extend(extra_items)
        scene["contentAccounting"]["kept"].extend(extra_items)
        scene["contentBudget"]["annotationItems"] = [
            {"item": item, "attachedTo": "Gateway", "kind": "fact"}
            for item in extra_items
        ]

        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        joined = "\n".join(errors)
        self.assertIn("annotationItems must not exceed 4", joined)
        self.assertIn("total visible nodeItems plus annotationItems must not exceed 12", joined)

    def test_obvious_entity_noun_cannot_pose_as_annotation_fact(self) -> None:
        scene = valid_scene()
        scene["contentAccounting"]["sourceItems"].append("Billing service")
        scene["contentAccounting"]["kept"].append("Billing service")
        scene["contentBudget"]["annotationItems"] = [
            {"item": "Billing service", "attachedTo": "Gateway", "kind": "fact"}
        ]

        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        self.assertTrue(any("looks like an entity" in error for error in errors))

    def test_required_global_and_local_anchor_sets_are_cross_enforced(self) -> None:
        plan = {
            "videoDirection": {"sourceAnchors": []},
            "contentTargets": [],
            "scenes": [valid_scene()],
        }
        errors = VALIDATOR.validate_plan(
            plan,
            expect_scenes=None,
            min_scenes=None,
            require_anchors=["Gateway"],
            forbidden=[],
            allow_held_scenes=False,
            require_strict_alignment=False,
            require_square_edges=False,
            require_validation_contract=False,
            require_zero_box_padding=False,
            require_grayscale_hierarchy=False,
            require_content_accounting=True,
        )
        joined = "\n".join(errors)
        self.assertIn("CLI required anchors must appear", joined)
        self.assertIn("local sourceAnchors are absent", joined)

        plan["videoDirection"]["sourceAnchors"] = ["Gateway"]
        plan["scenes"][0]["sourceAnchors"] = []
        errors = VALIDATOR.validate_plan(
            plan,
            expect_scenes=None,
            min_scenes=None,
            require_anchors=["Gateway"],
            forbidden=[],
            allow_held_scenes=False,
            require_strict_alignment=False,
            require_square_edges=False,
            require_validation_contract=False,
            require_zero_box_padding=False,
            require_grayscale_hierarchy=False,
            require_content_accounting=True,
        )
        self.assertTrue(any("Global source anchors must appear" in error for error in errors))

    def test_external_move_target_must_be_declared_and_receive_the_item(self) -> None:
        source = valid_scene()
        source["contentAccounting"]["movedToDetail"][0]["target"] = {
            "kind": "artifact",
            "id": "operations-detail",
        }
        errors = VALIDATOR._validate_cross_scene_content_moves([source], [], {})
        self.assertTrue(any("targets undeclared artifact" in error for error in errors))

        errors = VALIDATOR._validate_cross_scene_content_moves(
            [source],
            [],
            {("artifact", "operations-detail"): {"Different item"}},
        )
        self.assertTrue(any("is absent from declared target" in error for error in errors))

    def test_external_target_registry_requires_reachable_contract_fields(self) -> None:
        plan = {
            "contentTargets": [
                {
                    "kind": "artifact",
                    "id": "operations-detail",
                    "path": "deliverables/operations-detail.mmd",
                    "receives": ["Audit"],
                },
                {
                    "kind": "detail-view",
                    "id": "audit-zoom",
                    "ownerScene": "scene-02",
                    "receives": ["Audit stream"],
                },
            ]
        }
        registry, errors = VALIDATOR._validate_content_target_registry(
            plan, {"scene-01", "scene-02"}
        )
        self.assertEqual(errors, [])
        self.assertEqual(registry[("artifact", "operations-detail")], {"Audit"})

        plan["contentTargets"][0].pop("path")
        plan["contentTargets"][1]["ownerScene"] = "missing-scene"
        _, errors = VALIDATOR._validate_content_target_registry(
            plan, {"scene-01", "scene-02"}
        )
        joined = "\n".join(errors)
        self.assertIn("artifact needs a non-empty string path", joined)
        self.assertIn("ownerScene 'missing-scene' is unknown", joined)

    def test_external_target_receives_must_have_matching_deliveries(self) -> None:
        source = valid_scene()
        source["contentAccounting"]["movedToDetail"][0]["target"] = {
            "kind": "artifact",
            "id": "operations-detail",
        }
        errors = VALIDATOR._validate_cross_scene_content_moves(
            [source],
            [],
            {("artifact", "operations-detail"): {"Audit", "Ghost item"}},
        )
        self.assertTrue(
            any("no matching movedToDetail delivery" in error and "Ghost item" in error for error in errors)
        )

    def test_repeated_item_requires_one_exact_forward_move(self) -> None:
        first = {
            "id": "scene-01",
            "contentAccounting": {
                "sourceItems": ["Shared item"],
                "kept": ["Shared item"],
                "merged": [],
                "omitted": [],
                "movedToDetail": [],
            },
        }
        second = {
            "id": "scene-02",
            "contentAccounting": {
                "sourceItems": ["Shared item"],
                "kept": ["Shared item"],
                "merged": [],
                "omitted": [],
                "movedToDetail": [],
            },
        }
        errors = VALIDATOR._validate_cross_scene_content_moves([first, second], [])
        self.assertTrue(any("repeats across scenes without one exact forward move" in error for error in errors))

        second["contentAccounting"]["kept"] = []
        second["contentAccounting"]["movedToDetail"] = [
            {
                "item": "Shared item",
                "target": {"kind": "scene", "id": "scene-01"},
                "reason": "Invalid backward move.",
            }
        ]
        errors = VALIDATOR._validate_cross_scene_content_moves([first, second], [])
        joined = "\n".join(errors)
        self.assertIn("must target a later scene", joined)
        self.assertIn("repeats across scenes without one exact forward move", joined)

    def test_empty_non_diagram_scene_ledger_is_valid(self) -> None:
        scene = {
            "id": "title-card",
            "sourceAnchors": [],
            "contentBudget": {
                "mode": "non-diagram",
                "nodeItems": [],
                "edgeItems": [],
                "focalItems": [],
                "annotationItems": [],
                "plannedNodeCount": 0,
                "plannedEdgeCount": 0,
                "focalElementCount": 0,
                "overflowStrategy": "No enumerated source content is visible in this held transition.",
            },
            "contentAccounting": {
                "sourceItems": [],
                "kept": [],
                "merged": [],
                "omitted": [],
                "movedToDetail": [],
            },
        }
        self.assertEqual(VALIDATOR._validate_content_accounting("title-card", scene), [])

    def test_moved_item_cannot_remain_in_visible_bearing_fields(self) -> None:
        scene = valid_scene()
        scene["depthLayers"] = [
            {"name": "foreground", "content": "Audit annotation carrier"}
        ]
        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        self.assertTrue(
            any("movedToDetail source item 'Audit' still appears" in error for error in errors)
        )

    def test_moved_multiword_item_does_not_match_one_generic_token(self) -> None:
        scene = valid_scene()
        scene["contentAccounting"]["sourceItems"][-1] = "Customer service"
        scene["contentAccounting"]["movedToDetail"][0]["item"] = "Customer service"
        scene["depthLayers"] = [
            {"name": "foreground", "content": "A service gateway carries the visible request path."}
        ]
        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        self.assertFalse(any("still appears in visible-bearing" in error for error in errors))

    def test_moved_content_matching_is_unicode_exact_and_covers_text_policies(self) -> None:
        unicode_scene = valid_scene()
        unicode_scene["contentAccounting"]["sourceItems"][-1] = "审计流"
        unicode_scene["contentAccounting"]["movedToDetail"][0]["item"] = "审计流"
        unicode_scene["layout"] = "审计流 remains visible in the lower lane."
        unicode_errors = VALIDATOR._validate_content_accounting("scene-01", unicode_scene)
        self.assertTrue(any("source item '审计流' still appears" in error for error in unicode_errors))

        symbol_scene = valid_scene()
        symbol_scene["contentAccounting"]["sourceItems"][-1] = "C++"
        symbol_scene["contentAccounting"]["movedToDetail"][0]["item"] = "C++"
        symbol_scene["layout"] = "A C gateway remains visible, but the language detail is absent."
        symbol_errors = VALIDATOR._validate_content_accounting("scene-01", symbol_scene)
        self.assertFalse(any("still appears in visible-bearing" in error for error in symbol_errors))

        policy_scene = valid_scene()
        policy_scene["functionalTextPolicy"] = "Audit is a visible label."
        policy_errors = VALIDATOR._validate_content_accounting("scene-01", policy_scene)
        self.assertTrue(any("source item 'Audit' still appears" in error for error in policy_errors))

    def test_validation_check_numeric_claims_must_match_structured_counts(self) -> None:
        scene = valid_scene()
        scene["validationChecks"] = [
            {
                "method": "ledger-check",
                "target": "scene-01",
                "passCriterion": "All 5 sourceItems and exactly 2 nodes are represented.",
            }
        ]
        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        joined = "\n".join(errors)
        self.assertIn("claims 5 sourceItems", joined)
        self.assertIn("claims 2 nodeItems", joined)

    def test_numeric_claims_understand_bounds_and_relation_synonym(self) -> None:
        scene = valid_scene()
        scene["validationChecks"] = [
            {
                "method": "count-contract",
                "target": "scene-01",
                "passCriterion": "At most 9 nodes, at least 3 edges, and exactly 99 relations are visible.",
            }
        ]
        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        joined = "\n".join(errors)
        self.assertNotIn("claims 9 nodeItems", joined)
        self.assertNotIn("claims 3 edgeItems", joined)
        self.assertIn("claims 99 edgeItems", joined)

    def test_numeric_claims_accept_postfix_bounds_and_unit_first_counts(self) -> None:
        scene = valid_scene()
        scene["validationChecks"] = [
            {
                "method": "count-contract",
                "target": "scene-01",
                "passCriterion": (
                    "9 nodes maximum; node count is exactly 99; relation count is 88."
                ),
            }
        ]
        errors = VALIDATOR._validate_content_accounting("scene-01", scene)
        joined = "\n".join(errors)
        self.assertNotIn("claims 9 nodeItems", joined)
        self.assertIn("claims 99 nodeItems", joined)
        self.assertIn("claims 88 edgeItems", joined)


if __name__ == "__main__":
    unittest.main()
