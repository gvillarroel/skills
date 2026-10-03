#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Exercise evidence, portability, and malformed generated-bundle boundaries."""

from __future__ import annotations

import copy
import contextlib
import io
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from validate_reviewer import main, validate


PROFILE = {
    "schema_version": 1,
    "repository": {"name": "Demo", "identity": "fixture/demo", "revision": "snapshot-1", "inspected_at": "2026-10-01", "fingerprint_paths": ["pyproject.toml"]},
    "sources": [{"id": "code", "kind": "implementation", "location": "src/service.py#lookup", "status": "read", "note": "Lookup contract"}],
    "components": [{"name": "API", "paths": ["src/"], "purpose": "Serve records", "evidence": ["code"]}],
    "rules": [{"id": "demo-scope", "kind": "observed-contract", "paths": ["src/**"], "when": "Lookup changes", "invariant": "Scope records by owner", "failure": "Cross-owner lookup leaks a record", "pass_case": "Equivalent scoped query", "evidence": ["code"]}],
    "checks": [{"name": "Static scope", "command": "Trace lookup predicates and callers", "cwd": ".", "execution": "manual-only", "purpose": "Validate owner isolation", "side_effects": "No code execution or writes", "evidence": ["code"]}],
    "coverage_gaps": [],
}


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        # Keep all test writes inside the caller's writable workspace.
        self.temp = tempfile.TemporaryDirectory(prefix="reviewer-check-", dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "demo-reviewer"
        (self.root / "references").mkdir(parents=True)
        self.profile = copy.deepcopy(PROFILE)
        self.skill = "---\nname: demo-reviewer\ndescription: Reviews Demo changes.\n---\n\nRead [rules](references/review-rules.md) and [safety](references/safety-and-checks.md).\n"

    def run_validation(self) -> dict:
        (self.root / "SKILL.md").write_text(self.skill, encoding="utf-8")
        (self.root / "references/repository-profile.json").write_text(json.dumps(self.profile), encoding="utf-8")
        for name in ("review-rules.md", "safety-and-checks.md"):
            (self.root / "references" / name).write_text("# Reference\n\nConcrete guidance.\n", encoding="utf-8")
        return validate(self.root)

    def test_valid_bundle(self) -> None:
        self.assertTrue(self.run_validation()["passed"])

    def test_unknown_source_rejected(self) -> None:
        self.profile["rules"][0]["evidence"] = ["fiction"]
        self.assertFalse(self.run_validation()["passed"])

    def test_unavailable_source_cannot_support_rule(self) -> None:
        self.profile["sources"][0]["status"] = "unavailable"
        self.assertFalse(self.run_validation()["passed"])

    def test_unavailable_check_can_cite_unavailable_evidence(self) -> None:
        self.profile["sources"].append({"id": "history", "kind": "history", "location": ".git", "status": "unavailable", "note": "Snapshot has no Git history"})
        self.profile["checks"].append({"name": "History", "command": "Inspect target Git history when a checkout is supplied", "cwd": ".", "execution": "unavailable", "purpose": "Historical context", "side_effects": "Not executed; history was not supplied", "evidence": ["history"]})
        self.assertTrue(self.run_validation()["passed"])

    def test_executable_check_cannot_cite_unavailable_evidence(self) -> None:
        self.profile["sources"].append({"id": "history", "kind": "history", "location": ".git", "status": "unavailable", "note": "Snapshot has no Git history"})
        self.profile["checks"][0]["evidence"] = ["history"]
        self.assertFalse(self.run_validation()["passed"])

    def test_diagnostic_mode_preserves_failed_result(self) -> None:
        self.profile["rules"][0]["evidence"] = ["fiction"]
        self.run_validation()
        output = io.StringIO()
        with patch("sys.argv", ["validate_reviewer.py", str(self.root), "--report-only"]), contextlib.redirect_stdout(output):
            self.assertEqual(main(), 0)
        self.assertFalse(json.loads(output.getvalue())["passed"])

    def test_default_exit_rejects_invalid_bundle(self) -> None:
        self.profile["rules"][0]["evidence"] = ["fiction"]
        self.run_validation()
        with patch("sys.argv", ["validate_reviewer.py", str(self.root)]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(), 1)

    def test_duplicate_rule_rejected(self) -> None:
        self.profile["rules"].append(copy.deepcopy(self.profile["rules"][0]))
        self.assertFalse(self.run_validation()["passed"])

    def test_duplicate_source_rejected(self) -> None:
        self.profile["sources"].append(copy.deepcopy(self.profile["sources"][0]))
        self.assertFalse(self.run_validation()["passed"])

    def test_absolute_path_rejected(self) -> None:
        self.profile["components"][0]["paths"] = ["C:/private/project"]
        self.assertFalse(self.run_validation()["passed"])

    def test_parent_path_rejected(self) -> None:
        self.profile["checks"][0]["cwd"] = "../project"
        self.assertFalse(self.run_validation()["passed"])

    def test_unresolved_template_rejected(self) -> None:
        self.profile["rules"][0]["invariant"] = "{{RULE}}"
        self.assertFalse(self.run_validation()["passed"])

    def test_upstream_expression_is_not_a_placeholder(self) -> None:
        self.profile["rules"][0]["invariant"] = "Do not interpolate ${{ github.event.pull_request.title }} into shell code."
        self.assertTrue(self.run_validation()["passed"])

    def test_external_markdown_dependency_rejected(self) -> None:
        self.skill += "Read [other](../another-skill/SKILL.md).\n"
        self.assertFalse(self.run_validation()["passed"])

    def test_missing_reference_rejected(self) -> None:
        self.skill += "Read [missing](references/missing.md).\n"
        self.assertFalse(self.run_validation()["passed"])

    def test_frontmatter_extra_field_rejected(self) -> None:
        self.skill = self.skill.replace("description:", "metadata: extra\ndescription:")
        self.assertFalse(self.run_validation()["passed"])

    def test_oversized_description_rejected(self) -> None:
        self.skill = self.skill.replace("Reviews Demo changes.", "a" * 1025)
        self.assertFalse(self.run_validation()["passed"])

    def test_description_xml_rejected(self) -> None:
        self.skill = self.skill.replace("Reviews Demo changes.", "Reviews <Demo> changes.")
        self.assertFalse(self.run_validation()["passed"])

    def test_duplicate_description_rejected(self) -> None:
        self.skill = self.skill.replace("description:", "description: First value.\ndescription:")
        self.assertFalse(self.run_validation()["passed"])

    def test_oversized_entrypoint_rejected(self) -> None:
        self.skill += "Guidance.\n" * 500
        self.assertFalse(self.run_validation()["passed"])

    def test_unrouted_reference_rejected(self) -> None:
        self.run_validation()
        (self.root / "references/additional.md").write_text("# Additional rules\n", encoding="utf-8")
        self.assertFalse(validate(self.root)["passed"])

    def test_long_reference_without_contents_rejected(self) -> None:
        self.run_validation()
        (self.root / "references/review-rules.md").write_text("# Rules\n\n## Contracts\n" + "Concrete guidance.\n" * 101, encoding="utf-8")
        self.assertFalse(validate(self.root)["passed"])

    def test_name_mismatch_rejected(self) -> None:
        self.skill = self.skill.replace("name: demo-reviewer", "name: other-reviewer")
        self.assertFalse(self.run_validation()["passed"])

    def test_bad_date_rejected(self) -> None:
        self.profile["repository"]["inspected_at"] = "October"
        self.assertFalse(self.run_validation()["passed"])

    def test_url_credentials_rejected(self) -> None:
        self.profile["sources"][0]["location"] = "https://user:password@example.org/spec"
        self.assertFalse(self.run_validation()["passed"])

    def test_schema_boolean_rejected(self) -> None:
        self.profile["schema_version"] = True
        self.assertFalse(self.run_validation()["passed"])

    def test_missing_required_file_rejected(self) -> None:
        self.run_validation()
        (self.root / "references/review-rules.md").unlink()
        self.assertFalse(validate(self.root)["passed"])

    def test_invalid_profile_type_rejected(self) -> None:
        self.profile = []
        self.assertFalse(self.run_validation()["passed"])

    def test_bad_execution_classification_rejected(self) -> None:
        self.profile["checks"][0]["execution"] = "run-anywhere"
        self.assertFalse(self.run_validation()["passed"])

    def test_rule_requires_passing_counterexample(self) -> None:
        del self.profile["rules"][0]["pass_case"]
        self.assertFalse(self.run_validation()["passed"])

    def test_non_string_classifications_rejected(self) -> None:
        for section, field in (("sources", "status"), ("rules", "kind"), ("checks", "execution")):
            with self.subTest(section=section):
                self.profile = copy.deepcopy(PROFILE)
                self.profile[section][0][field] = []
                self.assertFalse(self.run_validation()["passed"])

    def test_missing_profile_fields_rejected(self) -> None:
        for field in ("repository", "sources", "components", "rules", "checks", "coverage_gaps"):
            with self.subTest(field=field):
                self.profile = copy.deepcopy(PROFILE)
                del self.profile[field]
                self.assertFalse(self.run_validation()["passed"])


if __name__ == "__main__":
    unittest.main()
