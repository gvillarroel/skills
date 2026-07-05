#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
EXAMPLE_DIR = SKILL_DIR / "assets" / "examples" / "base"
STYLE_SCRIPT = SCRIPT_DIR / "style_mermaid_directory.py"


def load_styler():
    spec = importlib.util.spec_from_file_location("style_mermaid_directory", STYLE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load style_mermaid_directory.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    styler = load_styler()
    theme = styler.theme_variables("colorset2", "sequenceDiagram")
    assert_true("fontFamily" not in theme, "Mermaid 11.16.0 ignores themeVariables when fontFamily is present.")
    assert_true(theme["actorBkg"] == styler.PALETTES["colorset2"]["primary_light"], "Sequence actors should visibly carry the colorset primary fill.")
    assert_true(theme["actorLineColor"] == styler.PALETTES["colorset2"]["primary"], "Sequence lifelines should visibly carry the colorset primary stroke.")
    core_theme = styler.theme_variables("colorset2")
    assert_true("actorBkg" not in core_theme, "Core themeVariables should not include sequence-only settings.")
    assert_true("git0" not in core_theme, "Core themeVariables should not include GitGraph-only settings.")
    assert_true("pie1" not in core_theme, "Core themeVariables should not include Pie-only settings.")
    frontmatter = styler.colorset_frontmatter("colorset2", "sequenceDiagram")
    assert_true(frontmatter.startswith("---\n"), "Styled diagrams should use YAML frontmatter.")
    assert_true('theme: "base"' in frontmatter, "Styled YAML frontmatter must use the Mermaid base theme.")
    assert_true("themeVariables:" in frontmatter, "Styled YAML frontmatter should include themeVariables.")
    legacy_source = '%%{init: {"theme":"base","mermaid-colorset-styler":{"colorset":"colorset1"}}}%%\nflowchart LR\n  A[Old]:::csPrimary\n'
    migrated, _migrated_meta = styler.style_mermaid_block(legacy_source, "colorset2")
    assert_true("%%{init:" not in migrated, "Legacy generated JSON init directives should be migrated away.")
    assert_true('colorset: "colorset2"' in migrated, "Migrated output should use the requested colorset in YAML metadata.")
    existing_frontmatter = """---
title: Existing title
config:
  layout: elk
  theme: forest
  themeVariables:
    primaryColor: "#111111"
---
flowchart LR
  A[Start]:::csPrimary --> B[Done]
"""
    merged, _merged_meta = styler.style_mermaid_block(existing_frontmatter, "colorset2")
    assert_true("title: Existing title" in merged, "Existing frontmatter title should be preserved.")
    assert_true("layout: elk" in merged, "Existing non-style config should be preserved.")
    assert_true(merged.count("\nconfig:") == 1, "Existing config should be merged rather than duplicated.")
    assert_true("theme: forest" not in merged, "Existing theme should be replaced by the requested base theme.")
    assert_true("#111111" not in merged, "Existing themeVariables should be replaced by the requested colorset variables.")

    with tempfile.TemporaryDirectory(prefix="mermaid-colorset-styler-") as tmp:
        workspace = Path(tmp) / "workspace"
        shutil.copytree(EXAMPLE_DIR, workspace)

        report1 = Path(tmp) / "colorset1-report.json"
        result = run_command(
            [
                sys.executable,
                str(STYLE_SCRIPT),
                str(workspace),
                "--colorset",
                "colorset1",
                "--write",
                "--report",
                str(report1),
            ],
            cwd=Path(tmp),
        )
        assert_true(result.returncode == 0, result.stderr or result.stdout)
        data = json.loads(report1.read_text(encoding="utf-8"))
        assert_true(data["diagramCount"] >= len(styler.OFFICIAL_DECLARATIONS), "Expected all official declarations to be represented.")
        for declaration in styler.OFFICIAL_DECLARATIONS:
            assert_true(declaration in data["declarationsSeen"], f"Missing fixture declaration: {declaration}")
        fixture_classes = {class_name for diagram in data["diagrams"] for class_name in diagram["referenced_classes"]}
        assert_true(fixture_classes == styler.COLOR_CLASSES, f"Fixture should reference every supported color class: {sorted(fixture_classes)}")
        assert_true(data["changedFileCount"] > 0, "First write should change copied fixtures.")
        assert_true(data["missingStyleCount"] == 0, "Every diagram should have colorset YAML frontmatter after writing.")

        for diagram in data["diagrams"]:
            inserted = diagram["inserted_class_defs"]
            skipped = diagram["skipped_class_defs"]
            family = diagram["family"]
            if family in styler.CLASSDEF_FAMILIES:
                assert_true(inserted == diagram["referenced_classes"], f"Expected exact classDef coverage for {diagram}")
                assert_true(not skipped, f"ClassDef-capable family should not skip classes: {diagram}")
            else:
                assert_true(not inserted, f"Non-classDef family received classDefs: {diagram}")

        report_check = Path(tmp) / "colorset1-check.json"
        result = run_command(
            [
                sys.executable,
                str(STYLE_SCRIPT),
                str(workspace),
                "--colorset",
                "colorset1",
                "--check",
                "--report",
                str(report_check),
            ],
            cwd=Path(tmp),
        )
        assert_true(result.returncode == 0, result.stderr or result.stdout)
        check_data = json.loads(report_check.read_text(encoding="utf-8"))
        assert_true(check_data["changedFileCount"] == 0, "Second colorset1 pass should be idempotent.")

        report2 = Path(tmp) / "colorset2-report.json"
        result = run_command(
            [
                sys.executable,
                str(STYLE_SCRIPT),
                str(workspace),
                "--colorset",
                "colorset2",
                "--write",
                "--report",
                str(report2),
            ],
            cwd=Path(tmp),
        )
        assert_true(result.returncode == 0, result.stderr or result.stdout)
        data2 = json.loads(report2.read_text(encoding="utf-8"))
        assert_true(data2["colorset"] == "colorset2", "Colorset2 report should identify colorset2.")
        assert_true(data2["changedFileCount"] > 0, "Switching to colorset2 should update copied fixtures.")
        sample = (workspace / "all-types.md").read_text(encoding="utf-8")
        assert_true('theme: "base"' in sample, "Styled diagrams must use Mermaid base theme.")
        assert_true("config:\n" in sample, "Styled diagrams should use Mermaid YAML frontmatter config.")
        assert_true("mermaid-colorset-styler" in sample, "Styled diagrams should carry generated colorset metadata.")

    print("Mermaid colorset styler coverage passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
