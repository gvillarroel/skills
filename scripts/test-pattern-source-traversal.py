#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Verify pattern validation coverage without traversing ignored payloads."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SPEC = importlib.util.spec_from_file_location(
    "pattern_validator", Path(__file__).with_name("validate-pattern-ids.py")
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class SourceTraversalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write(self, relative: str, text: str = "source") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def sources(self) -> set[str]:
        return {path.relative_to(self.root).as_posix() for path in VALIDATOR.iter_active_sources(self.root)}

    def test_retains_runtime_examples_and_durable_evaluations(self) -> None:
        expected = {
            "skills/demo/SKILL.md",
            "skills/demo/references/pattern.md",
            "skills/demo/assets/examples/gallery/index.html",
            "skills/demo/assets/examples/gallery/nested/module.TS",
            "skills/demo/runs/authored.json",
            "evaluations/demo/summary.md",
            "evaluations/pi-prompts/demo.md",
        }
        for name in expected:
            self.write(name)
        self.write("skills/demo/image.png")
        self.write("projects/private/data.json")
        self.assertEqual(self.sources(), expected)

    def test_does_not_enter_ignored_subtrees(self) -> None:
        kept = self.write("skills/demo/SKILL.md")
        ignored = [
            "skills/demo/node_modules/library/deep/file.js",
            "skills/demo/assets/examples/gallery/dist/generated.html",
            "evaluations/runs/large/workspace/trace.json",
            "evaluations/archive/runs/old/trace.json",
            "evaluations/demo/node_modules/tool/file.js",
        ]
        for name in ignored:
            self.write(name)
        real_scandir = os.scandir

        def guarded_scandir(path):
            relative = Path(path).relative_to(self.root)
            self.assertFalse({"node_modules", "dist", "runs"}.intersection(relative.parts), str(relative))
            return real_scandir(path)

        with mock.patch.object(VALIDATOR.os, "scandir", side_effect=guarded_scandir):
            self.assertEqual(list(VALIDATOR.iter_active_sources(self.root)), [kept])

    def test_invalid_ids_in_authored_examples_are_still_detected(self) -> None:
        path = self.write(
            "skills/demo/assets/examples/gallery/index.html",
            '<div data-pattern-id="d3-invalid-pattern-id"></div>',
        )
        findings = []
        observed, count = VALIDATOR.collect_explicit_ids(self.root, findings)
        self.assertEqual(count, 1)
        self.assertIn("d3-invalid-pattern-id", observed)
        self.assertTrue(any(finding.path == path and "generic segment" in finding.message for finding in findings))

    def test_missing_source_roots_are_empty(self) -> None:
        self.assertEqual(self.sources(), set())

    def test_directory_symlink_is_not_followed(self) -> None:
        self.write("skills/demo/SKILL.md")
        target = self.write("outside/secret.md").parent
        link = self.root / "skills" / "demo" / "linked"
        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlinks unavailable: {error}")
        self.assertEqual(self.sources(), {"skills/demo/SKILL.md"})


if __name__ == "__main__":
    unittest.main()
