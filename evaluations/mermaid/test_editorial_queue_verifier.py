#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the editorial review-queue semantic verifier."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("verify_editorial_queue.py")


def load_verifier():
    spec = importlib.util.spec_from_file_location("editorial_queue_verifier_test", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VERIFIER = load_verifier()


def valid_source() -> str:
    return """flowchart LR
  accTitle: Review queue
  accDescr: Four producers enter a capacity-two queue; review completes at one item per hour, with Approved and Deferred outcomes.
  web[Web]
  mobile[Mobile]
  partner[Partner API]
  batch[Batch import]
  gateway[Gateway]
  queue[Review queue]
  reviewers[Reviewers]
  approved[Approved]
  deferred[Deferred]
  web --> gateway
  mobile --> gateway
  partner --> gateway
  batch --> gateway
  gateway -->|capacity 2 items| queue
  queue -->|1 item per hour| reviewers
  queue -->|overflow| deferred
  reviewers --> approved
"""


def valid_ledger() -> str:
    lines = [
        "| Source item | Decision | Drawn as or target | Reason |",
        "| --- | --- | --- | --- |",
    ]
    for source_item, (decision, destination) in VERIFIER.EXPECTED_LEDGER.items():
        lines.append(f"| {source_item} | {decision} | {destination} | Preserved contract. |")
    return "\n".join(lines)


class EditorialQueueVerifierTests(unittest.TestCase):
    def test_valid_contract_passes(self) -> None:
        self.assertEqual(VERIFIER.verify(valid_source(), valid_ledger()), [])

    def test_invented_operational_edge_fails(self) -> None:
        source = valid_source() + "  metrics[Metrics hook]\n  reviewers --> metrics\n"
        errors = VERIFIER.verify(source, valid_ledger())
        joined = "\n".join(errors)
        self.assertIn("Node IDs differ", joined)
        self.assertIn("Directed relations differ", joined)
        self.assertIn("Moved detail appears", joined)

    def test_missing_or_misclassified_ledger_row_fails(self) -> None:
        ledger = valid_ledger().replace(
            "| Audit archive | Moved to detail | operations-detail.mmd | Preserved contract. |",
            "| Audit archive | Kept | audit | |",
        )
        errors = VERIFIER.verify(valid_source(), ledger)
        joined = "\n".join(errors)
        self.assertIn("Ledger decision", joined)
        self.assertIn("Ledger destination", joined)

    def test_wrong_visible_label_fails(self) -> None:
        source = valid_source().replace("web[Web]", "web[Unrelated database]")
        errors = VERIFIER.verify(source, valid_ledger())
        self.assertTrue(any("visible label for node 'web'" in error for error in errors))

    def test_repeated_identical_node_declarations_and_pipe_optional_table_pass(self) -> None:
        source = valid_source().replace(
            "  mobile --> gateway\n",
            "  mobile[Mobile] --> gateway[Gateway]\n",
        )
        ledger = "\n".join(
            line.strip().strip("|").strip() for line in valid_ledger().splitlines()
        )
        self.assertEqual(VERIFIER.verify(source, ledger), [])

    def test_chained_relation_is_fully_parsed(self) -> None:
        source = valid_source().replace(
            "  web --> gateway\n",
            "  web --> gateway --> mobile\n",
        )
        errors = VERIFIER.verify(source, valid_ledger())
        self.assertTrue(any("Directed relations differ" in error for error in errors))

    def test_non_solid_relation_is_not_ignored(self) -> None:
        source = valid_source() + "  approved -.-> deferred\n"
        errors = VERIFIER.verify(source, valid_ledger())
        joined = "\n".join(errors)
        self.assertIn("required --> form", joined)
        self.assertIn("Directed relations differ", joined)

    def test_implicit_node_and_duplicate_relation_fail(self) -> None:
        implicit_errors = VERIFIER.verify(
            valid_source() + "  approved --> shadow\n", valid_ledger()
        )
        self.assertTrue(any("Node IDs differ" in error and "shadow" in error for error in implicit_errors))
        self.assertTrue(any("Directed relations differ" in error for error in implicit_errors))

        duplicate_errors = VERIFIER.verify(
            valid_source() + "  web --> gateway\n", valid_ledger()
        )
        self.assertTrue(any("relations must appear exactly once" in error for error in duplicate_errors))

    def test_visible_facts_must_label_the_correct_relations(self) -> None:
        source = valid_source().replace(
            "gateway -->|capacity 2 items| queue",
            "gateway --> queue",
        ).replace(
            "web --> gateway",
            "web -->|capacity 2 items| gateway",
        ).replace(
            "queue -->|1 item per hour| reviewers",
            "queue --> reviewers",
        ).replace(
            "mobile --> gateway",
            "mobile -->|1 item per hour| gateway",
        )
        errors = VERIFIER.verify(source, valid_ledger())
        joined = "\n".join(errors)
        self.assertIn("must label relation gateway --> queue", joined)
        self.assertIn("must label relation queue --> reviewers", joined)


if __name__ == "__main__":
    unittest.main()
