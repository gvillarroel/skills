#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0.2",
# ]
# ///

"""Focused regressions for repository-level skill backlog validation."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR_PATH = Path(__file__).with_name("validate-skills.py")
SPEC = importlib.util.spec_from_file_location("validate_skills", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


def skill_row(name: str, status: str) -> str:
    return f"| {name} | {status} | purpose | resources | validation |"


class SkillBacklogValidationTests(unittest.TestCase):
    def validate(self, rows: list[str], directories: tuple[str, ...] = ("alpha-skill",)):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "skills").mkdir()
            for name in directories:
                (root / "skills" / name).mkdir()
            (root / "SKILLS.md").write_text(
                "\n".join(
                    [
                        "| Skill | Status | Purpose | Resources | Validation |",
                        "| --- | --- | --- | --- | --- |",
                        *rows,
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            findings = []
            VALIDATOR.validate_skill_backlog(root, findings)
            return [finding.message for finding in findings]

    def test_canonical_row_passes(self) -> None:
        self.assertEqual(self.validate([skill_row("alpha-skill", "`done`")]), [])

    def test_escaped_backticks_fail(self) -> None:
        messages = self.validate([skill_row("alpha-skill", r"\`validating\`")])
        self.assertEqual(len(messages), 1)
        self.assertIn("canonical unescaped backticks", messages[0])

    def test_invalid_status_fails(self) -> None:
        messages = self.validate([skill_row("alpha-skill", "`complete`")])
        self.assertEqual(len(messages), 1)
        self.assertIn("status is invalid", messages[0])

    def test_missing_and_unknown_rows_fail(self) -> None:
        messages = self.validate(
            [skill_row("orphan-skill", "`planned`")],
            directories=("alpha-skill",),
        )
        self.assertEqual(len(messages), 2)
        self.assertTrue(any("missing skill row: alpha-skill" in item for item in messages))
        self.assertTrue(
            any("no matching skill directory: orphan-skill" in item for item in messages)
        )

    def test_duplicate_rows_fail(self) -> None:
        row = skill_row("alpha-skill", "`validating`")
        messages = self.validate([row, row])
        self.assertEqual(len(messages), 1)
        self.assertIn("must be unique", messages[0])


if __name__ == "__main__":
    unittest.main()
