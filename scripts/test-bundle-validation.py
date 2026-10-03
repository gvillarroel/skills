#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Verify installed and isolated bundles cannot bypass authoring/resource gates."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SYNC = load("authoring_sync", "sync-local-skills.py")
RUNNER = load("authoring_runner", "run-pi-skill-eval.py")
VALIDATOR = load("authoring_validator", "validate-skills.py")
AUDIT = load("authoring_audit_tests", "audit-skill-authoring.py")


class BundleGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="bundle-check-", dir=Path.cwd())
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.skill = self.source / "demo-skill"
        self.skill.mkdir(parents=True)
        self.entry = self.skill / "SKILL.md"
        self.entry.write_text("---\nname: demo-skill\ndescription: Reviews Demo. Use for changes in Demo.\n---\n\n# Review\n\nInspect changes.\n", encoding="utf-8")
        self.destination = self.root / "installed"

    def synchronize(self, *, check: bool = False) -> int:
        argv = ["sync-local-skills.py", "--source", str(self.source), "--destination", str(self.destination)]
        if check:
            argv.append("--check")
        # The controlled fixture is ignored test output, so give sync its exact
        # source inventory instead of publishing it to a real Git repository.
        with mock.patch.object(sys, "argv", argv), mock.patch.object(SYNC, "source_files", side_effect=lambda source: sorted(path for path in source.rglob("*") if path.is_file())), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return SYNC.main()

    def test_valid_installed_bundle_and_check_pass(self) -> None:
        self.assertEqual(self.synchronize(), 0)
        self.assertEqual((self.destination / "demo-skill/SKILL.md").read_bytes(), self.entry.read_bytes())
        self.assertEqual(self.synchronize(check=True), 0)

    def test_invalid_source_is_rejected_before_copy(self) -> None:
        self.entry.write_text("Missing metadata", encoding="utf-8")
        self.assertEqual(self.synchronize(), 1)
        self.assertFalse(self.destination.exists())

    def test_missing_entry_in_an_additional_source_bundle_is_rejected(self) -> None:
        incomplete = self.source / "missing-entry"
        incomplete.mkdir()
        (incomplete / "reference.md").write_text("Incomplete bundle\n", encoding="utf-8")
        self.assertEqual(self.synchronize(), 1)
        self.assertFalse(self.destination.exists())

    def test_extra_unrouted_installed_reference_fails_check(self) -> None:
        self.assertEqual(self.synchronize(), 0)
        extra = self.destination / "demo-skill/references/obsolete.md"
        extra.parent.mkdir()
        extra.write_text("# Obsolete\n", encoding="utf-8")
        self.assertEqual(self.synchronize(check=True), 1)
        self.assertTrue(extra.exists())

    def test_actual_runtime_copy_has_valid_structure(self) -> None:
        fixture = self.skill / "assets/examples/input.txt"
        fixture.parent.mkdir(parents=True)
        fixture.write_text("Acceptance fixture", encoding="utf-8")
        target = self.root / "runtime/demo-skill"
        RUNNER.copy_skill_only(self.skill, target, "runtime")
        findings = []
        VALIDATOR.validate_skill_dir(target, self.root, findings, profile="runtime")
        self.assertEqual(findings, [])
        self.assertFalse((target / "assets/examples").exists())

    def test_both_profiles_exclude_dependencies_and_caches(self) -> None:
        for directory in RUNNER.COPY_IGNORE:
            path = self.skill / directory / "discard.txt"
            path.parent.mkdir(parents=True)
            path.write_text("Transient dependency or cache", encoding="utf-8")
        for profile in ("runtime", "full"):
            target = self.root / profile / "demo-skill"
            RUNNER.copy_skill_only(self.skill, target, profile)
            self.assertEqual({path.name for path in target.iterdir()}, {"SKILL.md"})

    def test_missing_required_runtime_resource_is_rejected(self) -> None:
        fixture = self.skill / "assets/examples/input.txt"
        fixture.parent.mkdir(parents=True)
        fixture.write_text("Acceptance fixture", encoding="utf-8")
        self.entry.write_text(self.entry.read_text(encoding="utf-8") + "\nRead [required input](assets/examples/input.txt).\n", encoding="utf-8")
        RUNNER.validate_bundle(self.skill)
        target = self.root / "runtime/demo-skill"
        RUNNER.copy_skill_only(self.skill, target, "runtime")
        with self.assertRaises(ValueError):
            RUNNER.validate_bundle(target, "runtime")

    def test_audit_rejects_a_source_changed_during_copy(self) -> None:
        copier = AUDIT.RUNNER.copy_skill_only

        def change_source(source, target, profile):
            copier(source, target, profile)
            self.entry.write_text(self.entry.read_text(encoding="utf-8") + "\nChanged during copy.\n", encoding="utf-8")

        with mock.patch.object(AUDIT.RUNNER, "copy_skill_only", side_effect=change_source):
            report = AUDIT.audit(self.source, bundles=True, temporary_parent=self.root / "copies")
        self.assertFalse(report["passed"])
        self.assertIn("source-changed", report["issueCounts"])

    def test_audit_rejects_a_valid_but_modified_copied_entry(self) -> None:
        copier = AUDIT.RUNNER.copy_skill_only

        def change_copy(source, target, profile):
            copier(source, target, profile)
            entry = target / "SKILL.md"
            entry.write_text(entry.read_text(encoding="utf-8") + "\nChanged copy.\n", encoding="utf-8")

        with mock.patch.object(AUDIT.RUNNER, "copy_skill_only", side_effect=change_copy):
            report = AUDIT.audit(self.source, bundles=True, temporary_parent=self.root / "copies")
        self.assertFalse(report["passed"])
        self.assertEqual(report["issueCounts"]["bundle-copy-mismatch"], 2)

    def test_audit_rejects_late_mutation_of_a_previously_checked_skill(self) -> None:
        second = self.source / "zeta-skill"
        second.mkdir()
        (second / "SKILL.md").write_text(self.entry.read_text(encoding="utf-8").replace("demo-skill", "zeta-skill"), encoding="utf-8")
        copier = AUDIT.RUNNER.copy_skill_only

        def change_earlier_source(source, target, profile):
            copier(source, target, profile)
            if source == second:
                self.entry.write_text(self.entry.read_text(encoding="utf-8") + "\nLater edit.\n", encoding="utf-8")

        with mock.patch.object(AUDIT.RUNNER, "copy_skill_only", side_effect=change_earlier_source):
            report = AUDIT.audit(self.source, bundles=True, temporary_parent=self.root / "copies")
        self.assertFalse(report["passed"])
        self.assertEqual(report["issueCounts"]["source-changed"], 1)

    def test_audit_rejects_a_skill_added_after_inventory_freeze(self) -> None:
        copier = AUDIT.RUNNER.copy_skill_only

        def add_source(source, target, profile):
            copier(source, target, profile)
            extra = self.source / "zeta-skill"
            extra.mkdir(exist_ok=True)
            (extra / "SKILL.md").write_text(self.entry.read_text(encoding="utf-8").replace("demo-skill", "zeta-skill"), encoding="utf-8")

        with mock.patch.object(AUDIT.RUNNER, "copy_skill_only", side_effect=add_source):
            report = AUDIT.audit(self.source, bundles=True, temporary_parent=self.root / "copies")
        self.assertFalse(report["passed"])
        self.assertEqual(report["issueCounts"]["source-inventory-changed"], 1)


if __name__ == "__main__":
    unittest.main()
