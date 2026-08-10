#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for D3 runtime-payload staging."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from stage_runtime_skill import stage


class RuntimeSkillStagingTests(unittest.TestCase):
    def test_stages_runtime_files_and_excludes_acceptance_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "d3"
            output = root / "staged" / "d3"
            manifest = root / "staged" / "manifest.json"
            (source / "references").mkdir(parents=True)
            (source / "scripts" / "__pycache__").mkdir(parents=True)
            (source / "assets" / "examples" / "gallery").mkdir(parents=True)
            (source / "assets" / "palettes").mkdir(parents=True)
            (source / "assets" / "vendor" / "node_modules" / "pkg").mkdir(parents=True)
            (source / "SKILL.md").write_text("---\nname: d3\ndescription: Test.\n---\n", encoding="utf-8")
            (source / "references" / "contract.md").write_text("contract", encoding="utf-8")
            (source / "scripts" / "check.py").write_text("print('ok')\n", encoding="utf-8")
            (source / "scripts" / "__pycache__" / "check.pyc").write_bytes(b"cache")
            (source / "assets" / "examples" / "gallery" / "index.html").write_text("fixture", encoding="utf-8")
            (source / "assets" / "palettes" / "colors.json").write_text("{}", encoding="utf-8")
            (source / "assets" / "vendor" / "node_modules" / "pkg" / "index.js").write_text("vendor", encoding="utf-8")

            result = stage(source, output, manifest)

            self.assertTrue((output / "SKILL.md").is_file())
            self.assertTrue((output / "references" / "contract.md").is_file())
            self.assertTrue((output / "scripts" / "check.py").is_file())
            self.assertTrue((output / "assets" / "palettes" / "colors.json").is_file())
            self.assertFalse((output / "assets" / "examples").exists())
            self.assertFalse((output / "assets" / "vendor" / "node_modules").exists())
            self.assertFalse((output / "scripts" / "__pycache__").exists())
            self.assertTrue(result["sourceUnchanged"])
            self.assertEqual(result["fileCount"], 4)
            self.assertTrue(manifest.is_file())

    def test_refuses_nonempty_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "d3"
            output = root / "out"
            source.mkdir()
            output.mkdir()
            (source / "SKILL.md").write_text("---\nname: d3\ndescription: Test.\n---\n", encoding="utf-8")
            (output / "keep.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                stage(source, output, root / "manifest.json")


if __name__ == "__main__":
    unittest.main()
