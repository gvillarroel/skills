#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Unit tests for the pricing benchmark verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("verify_task.py")
SPEC = importlib.util.spec_from_file_location("pricing_verify_task", MODULE_PATH)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class VerifyTaskTests(unittest.TestCase):
    def setUp(self) -> None:
        self.expected = {
            "answers": [
                {"id": "q-1", "answer": {"price": "0.1", "regions": ["a", "b"]}},
                {"id": "q-2", "answer": {"count": 3}},
            ]
        }

    def test_exact_answers_receive_full_reward(self) -> None:
        result = VERIFY.score(self.expected, self.expected)
        self.assertTrue(result["ok"])
        self.assertEqual(result["reward"], 1.0)

    def test_wrong_decimal_string_receives_partial_reward_without_value_leak(self) -> None:
        actual = {
            "answers": [
                {"id": "q-1", "answer": {"price": "0.10", "regions": ["a", "b"]}},
                {"id": "q-2", "answer": {"count": 3}},
            ]
        }
        result = VERIFY.score(self.expected, actual)
        self.assertEqual(result["reward"], 0.5)
        serialized = repr(result["mismatches"])
        self.assertIn("answer.price:value", serialized)
        self.assertNotIn("0.1", serialized)

    def test_missing_and_extra_fields_fail_shape(self) -> None:
        actual = {
            "answers": [
                {"id": "q-1", "answer": {"price": "0.1", "extra": True}},
                {"id": "q-2", "answer": {"count": 3}},
            ]
        }
        result = VERIFY.score(self.expected, actual)
        self.assertFalse(result["ok"])
        self.assertIn("answer.regions:missing", result["mismatches"]["q-1"])
        self.assertIn("answer.extra:unexpected", result["mismatches"]["q-1"])


if __name__ == "__main__":
    unittest.main()

