#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Focused regression tests for stacked-bar subtotal classification."""

from compile_synchronized_svg_plan import stack_rollup_ids


def test_disjoint_residual_branch_is_kept_as_a_stack_part() -> None:
    values = ["delivered-water", "leakage", "unmet-demand", "daily-demand"]
    computations = {
        "delivered-water": {
            "op": "subtract",
            "args": [{"ref": "processed-water"}, {"ref": "leakage"}],
        },
        "daily-demand": None,
    }
    dependencies = {
        "delivered-water": {"processed-water", "leakage"},
        "leakage": {"processed-water"},
        "unmet-demand": {"daily-demand", "processed-water"},
    }

    assert stack_rollup_ids(values, computations, dependencies) == set()


def test_additive_subtotal_is_hidden_from_stack_marks() -> None:
    values = ["part-a", "part-b", "part-c", "parts-subtotal", "parts-total"]
    computations = {
        "parts-subtotal": {
            "op": "add",
            "args": [{"ref": "part-a"}, {"ref": "part-b"}],
        },
        "parts-total": {
            "op": "add",
            "args": [{"ref": "parts-subtotal"}, {"ref": "part-c"}],
        },
    }
    dependencies = {
        "parts-subtotal": {"part-a", "part-b"},
        "parts-total": {"parts-subtotal", "part-c", "part-a", "part-b"},
    }

    assert stack_rollup_ids(values, computations, dependencies) == {
        "parts-subtotal",
        "parts-total",
    }


if __name__ == "__main__":
    test_disjoint_residual_branch_is_kept_as_a_stack_part()
    test_additive_subtotal_is_hidden_from_stack_marks()
    print("stack reconciliation regression tests passed")
