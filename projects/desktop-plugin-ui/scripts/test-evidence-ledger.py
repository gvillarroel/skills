#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise declared-fact classification without a provider or assistant UI."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[3]
HELPER = REPO / "skills/desktop-plugin-ui/scripts/evidence_ledger.py"
ARTIFACTS = REPO / "projects/desktop-plugin-ui/artifacts/evidence-ledger-tests-20261025"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
if not ARTIFACTS.resolve().is_relative_to(REPO.resolve()):
    raise RuntimeError("Test workspaces must stay inside the authorized repository")
spec = importlib.util.spec_from_file_location("tested_evidence_ledger", HELPER)
assert spec is not None and spec.loader is not None
LEDGER = importlib.util.module_from_spec(spec)
previous_bytecode = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    spec.loader.exec_module(LEDGER)
finally:
    sys.dont_write_bytecode = previous_bytecode


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path: Path) -> dict[str, str]:
    return {item.relative_to(path).as_posix(): digest(item) for item in sorted(path.rglob("*")) if item.is_file()}


def fact(basis: str, **fields) -> dict:
    return {"id": "queue-check", "claim": "The queue behavior has a scoped result.",
            "host": "Synthetic test host", "surface": "Declared test surface", "version": "unknown",
            "layer": "Test layer", "basis": basis, **fields}


def executed(**fields) -> dict:
    return fact("execution", action="Save synthetic priority", expected="Refuse a stale version", actual="Stale version refused", outcome="pass", **fields)


class EvidenceLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context = tempfile.TemporaryDirectory(prefix="isolated-", dir=ARTIFACTS)
        cls.scratch = Path(cls.context.name).resolve()
        cls.detached = cls.scratch / "detached bundle"
        (cls.detached / "scripts").mkdir(parents=True)
        cls.relocated = cls.detached / "scripts/evidence_ledger.py"
        shutil.copy2(HELPER, cls.relocated)
        cls.relocated.chmod(stat.S_IREAD)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.relocated.chmod(stat.S_IREAD | stat.S_IWRITE)
        cls.context.cleanup()

    def setUp(self) -> None:
        self.caller = self.scratch / self._testMethodName
        self.caller.mkdir()
        self.input = self.caller / "facts.json"
        self.output = self.caller / "out/ledger.json"
        self.markdown = self.caller / "out/ledger.md"

    def invoke(self, data=None, *, extra=(), output=None, markdown=None, helper=None, write_input=True):
        if write_input:
            self.input.write_text(json.dumps(data), encoding="utf-8")
        args = [sys.executable, "-I", "-B", str(helper or self.relocated), "--input", str(self.input),
                "--output", str(output or self.output)]
        if markdown is not False:
            args.extend(["--markdown", str(markdown or self.markdown)])
        args.extend(extra)
        process = subprocess.run(args, cwd=self.caller, capture_output=True, text=True, encoding="utf-8", timeout=15,
                                 env={**os.environ, "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertFalse(process.stderr, process.stderr)
        return process, json.loads(process.stdout)

    def classified(self, row):
        result = LEDGER.classify_records({"records": [row]})
        self.assertTrue(result["passed"], result)
        return result["evidence_records"][0]

    def invalid(self, data, code):
        result = LEDGER.classify_records(data)
        self.assertFalse(result["passed"], result)
        self.assertEqual(result["evidence_records"], [])
        self.assertIn(code, {finding["code"] for finding in result["findings"]})
        return result

    def test_executed_expected_refusal_is_a_pass(self):
        row = self.classified(executed())
        self.assertEqual(row["evidence"], "observed-working")
        self.assertEqual(row["execution_state"], "executed")
        self.assertEqual(row["outcome"], "pass")

    def test_executed_failed_action_is_scoped_failure(self):
        row = executed()
        row.update(expected="Save accepted", actual="Transport timed out", outcome="fail")
        result = self.classified(row)
        self.assertEqual(result["evidence"], "observed-failed")
        self.assertEqual(result["action"], "Save synthetic priority")
        self.assertEqual(result["actual"], "Transport timed out")

    def test_boolean_false_data_is_not_cancel_or_failure_inference(self):
        row = executed()
        row.update(expected="Return the selected Boolean false", actual="false", outcome="pass")
        result = self.classified(row)
        self.assertEqual(result["evidence"], "observed-working")
        self.assertEqual(result["actual"], "false")

    def test_source_declaration_never_becomes_runtime_execution(self):
        row = self.classified(fact("source-inspection", source="widget.ts:41", claim="The Expand handler calls the fullscreen API."))
        self.assertEqual(row["evidence"], "documented")
        self.assertEqual(row["execution_state"], "not-run")
        self.assertNotIn("outcome", row)

    def test_primary_documentation_is_not_execution(self):
        row = self.classified(fact("primary-documentation", source="https://example.com/api#mode"))
        self.assertEqual(row["evidence"], "documented")
        self.assertEqual(row["execution_state"], "not-run")

    def test_reported_visible_chart_is_untested_by_agent(self):
        row = self.classified(fact("user-report", reporter="User", reported_result="The chart is expanded and visible."))
        self.assertEqual(row["evidence"], "untested")
        self.assertEqual(row["reported_result"], "The chart is expanded and visible.")
        self.assertEqual(row["execution_state"], "not-run")

    def test_unperformed_paint_is_not_observed_failed(self):
        row = self.classified(fact("not-run", reason="The user chose continuation without sign-in."))
        self.assertEqual(row["evidence"], "untested")
        self.assertEqual(row["execution_state"], "not-run")

    def test_prerequisites_and_explicit_exclusion_are_distinct(self):
        conditional = self.classified(fact("conditional", prerequisites=["A supported renderer", "Host capability negotiation"]))
        self.assertEqual(conditional["evidence"], "conditional")
        unsupported = self.classified(fact("explicit-exclusion", source="https://example.com/host#exclusions", exclusion="This named host contract excludes PiP."))
        self.assertEqual(unsupported["evidence"], "unsupported")
        self.assertEqual(unsupported["execution_state"], "not-run")

    def test_all_basis_rows_round_trip_without_mutating_input(self):
        rows = [executed(), fact("source-inspection", source="widget.ts:41"),
                fact("primary-documentation", source="https://example.com/api"),
                fact("user-report", reporter="User", reported_result="Visible"),
                fact("not-run", reason="Not requested"), fact("conditional", prerequisites=["Supported mode"]),
                fact("explicit-exclusion", source="https://example.com/api", exclusion="Explicit exclusion")]
        for number, row in enumerate(rows):
            row["id"] = f"claim-{number}"
        original = deepcopy(rows)
        first = LEDGER.classify_records({"records": rows})
        self.assertTrue(first["passed"], first)
        self.assertEqual(LEDGER.classify_records(first), first)
        self.assertEqual(rows, original)
        self.assertTrue(all(row["version"] == "unknown" for row in first["evidence_records"]))

    def test_tampered_derived_labels_fail(self):
        for field, value in {"evidence": "observed-failed", "classification": "observed-working", "execution_state": "executed"}.items():
            with self.subTest(field=field):
                row = fact("not-run", reason="Account step omitted", **{field: value})
                self.invalid({"evidence_records": [row]}, "classification_mismatch")

    def test_basis_mixing_is_rejected_without_semantic_guessing(self):
        self.invalid({"records": [fact("source-inspection", source="widget.ts:41", action="Expand", outcome="pass")]}, "unexpected_field")
        self.invalid({"records": [executed(source="widget.ts:41")]}, "unexpected_field")

    def test_missing_context_and_nonstring_values_fail(self):
        for field in ("id", "claim", "host", "surface", "version", "layer", "basis"):
            with self.subTest(field=field):
                row = fact("not-run", reason="Not run")
                row[field] = None
                result = LEDGER.classify_records({"records": [row]})
                self.assertFalse(result["passed"], result)
                self.assertEqual(result["evidence_records"], [])

    def test_outcome_must_be_explicit_pass_or_fail_string(self):
        for value in (True, False, None, 0, "not-run", "success"):
            with self.subTest(outcome=value):
                row = executed()
                row["outcome"] = value
                self.invalid({"records": [row]}, "invalid_outcome")
        row = executed()
        row["actual"] = False
        self.invalid({"records": [row]}, "missing_basis_field")

    def test_duplicate_ids_and_one_invalid_record_reject_all(self):
        self.invalid({"records": [executed(), executed()]}, "duplicate_id")
        valid = executed()
        invalid = fact("not-run", id="other", reason="")
        self.invalid({"records": [valid, invalid]}, "missing_basis_field")

    def test_invalid_roots_and_schema_versions_fail(self):
        for value in (None, [], 1, {"records": []}, {"records": {}}, {"records": ["not a record"]},
                      {"records": [executed()], "evidence_records": [executed()]},
                      {"records": [executed()], "schema_version": True},
                      {"records": [executed()], "schema_version": 2}):
            with self.subTest(value=value):
                self.assertFalse(LEDGER.classify_records(value)["passed"])

    def test_invalid_basis_prerequisites_and_field_names_fail(self):
        self.invalid({"records": [fact("imagined")]}, "invalid_basis")
        for value in ([], [""], [True], "renderer"):
            with self.subTest(prerequisites=value):
                self.invalid({"records": [fact("conditional", prerequisites=value)]}, "invalid_prerequisites")
        row = fact("not-run", reason="No action")
        row[7] = "not a JSON key"
        self.invalid({"records": [row]}, "invalid_field_name")

    def test_cli_writes_matching_json_and_escaped_markdown(self):
        row = fact("source-inspection", source="C:\\probe\\widget.ts:41", claim="Expand | code\n<not runtime> [label] `call` Ω")
        process, report = self.invoke({"records": [row]})
        self.assertEqual(process.returncode, 0)
        self.assertTrue(report["passed"], report)
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8")), report)
        markdown = self.markdown.read_text(encoding="utf-8")
        self.assertIn("Expand \\| code<br>&lt;not runtime&gt; \\[label\\] \\`call\\` Ω", markdown)
        self.assertIn("| documented | not-run; source:", markdown)
        self.assertEqual(markdown, LEDGER.render_markdown(report))
        self.assertNotIn("observed-working", markdown)

    def test_invalid_data_preserves_existing_outputs_and_exit_modes(self):
        self.output.parent.mkdir()
        self.output.write_text("previous JSON", encoding="utf-8")
        self.markdown.write_text("previous Markdown", encoding="utf-8")
        for extra, expected in (((), 0), (("--fail-on-findings",), 1)):
            process, report = self.invoke({"records": [fact("not-run", reason="No action", evidence="observed-failed")]}, extra=extra)
            self.assertEqual(process.returncode, expected)
            self.assertFalse(report["passed"])
            self.assertEqual(self.output.read_text(encoding="utf-8"), "previous JSON")
            self.assertEqual(self.markdown.read_text(encoding="utf-8"), "previous Markdown")

    def test_markdown_preserves_exact_source_urls(self):
        source = "https://example.com/source_path?field=a_b&mode=inline#method_name"
        process, report = self.invoke({"records": [fact("primary-documentation", source=source)]})
        self.assertEqual(process.returncode, 0)
        self.assertTrue(report["passed"])
        markdown = self.markdown.read_text(encoding="utf-8")
        self.assertIn(source, markdown)
        self.assertNotIn("&amp;", markdown)
        self.assertNotIn("source\\_path", markdown)

    def test_bundle_write_is_refused_before_either_output(self):
        destination = self.detached / "report.md"
        process, report = self.invoke({"records": [executed()]}, markdown=destination, extra=("--fail-on-findings",))
        self.assertEqual(process.returncode, 1)
        self.assertEqual(report["findings"][0]["code"], "bundle_write_refused")
        self.assertFalse(self.output.exists())
        self.assertFalse(destination.exists())

    def test_identical_outputs_and_input_alias_are_refused(self):
        process, report = self.invoke({"records": [executed()]}, markdown=self.output)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(report["findings"][0]["code"], "duplicate_output")
        self.assertFalse(self.output.exists())
        raw = {"records": [executed()]}
        _process, report = self.invoke(raw, output=self.input)
        self.assertEqual(report["findings"][0]["code"], "input_overwrite_refused")
        self.assertEqual(json.loads(self.input.read_text(encoding="utf-8")), raw)
        self.assertFalse(self.markdown.exists())

    def test_invalid_second_parent_does_not_commit_first_output(self):
        parent_file = self.caller / "not-a-folder"
        parent_file.write_text("preserve", encoding="utf-8")
        process, report = self.invoke({"records": [executed()]}, markdown=parent_file / "report.md", extra=("--fail-on-findings",))
        self.assertEqual(process.returncode, 1)
        self.assertFalse(report["passed"])
        self.assertFalse(self.output.exists())
        self.assertEqual(parent_file.read_text(encoding="utf-8"), "preserve")
        self.assertFalse(any(self.caller.rglob("*.tmp")))

    def test_malformed_duplicate_key_and_missing_input_are_bounded(self):
        for text, code in (("{", "input_or_output_error"), ('{"records":[],"records":[]}', "duplicate_json_key")):
            with self.subTest(source=text):
                self.input.write_text(text, encoding="utf-8")
                process, report = self.invoke(write_input=False)
                self.assertEqual(process.returncode, 0)
                self.assertFalse(report["passed"])
                self.assertEqual(report["findings"][0]["code"], code)
                self.assertFalse(self.output.exists())
        self.input.unlink()
        process, report = self.invoke(write_input=False, extra=("--fail-on-findings",))
        self.assertEqual(process.returncode, 1)
        self.assertFalse(report["passed"])

    def test_invalid_cli_arguments_exit_two_with_json_only(self):
        process = subprocess.run([sys.executable, "-I", "-B", str(self.relocated)], cwd=self.caller,
                                 capture_output=True, text=True, encoding="utf-8", timeout=15)
        self.assertEqual(process.returncode, 2)
        self.assertFalse(process.stderr)
        self.assertEqual(json.loads(process.stdout)["findings"][0]["code"], "invalid_arguments")

    def test_bom_and_unicode_input_preserve_english_claim_and_identifiers(self):
        row = fact("not-run", reason="No host action requested", claim="Keep identifier Ω-104 unchanged.")
        self.input.write_text("\ufeff" + json.dumps({"records": [row]}, ensure_ascii=False), encoding="utf-8")
        process, report = self.invoke(write_input=False, markdown=False)
        self.assertEqual(process.returncode, 0)
        self.assertTrue(report["passed"])
        self.assertEqual(report["evidence_records"][0]["claim"], row["claim"])
        self.assertFalse(self.markdown.exists())

    def test_relocated_readonly_bundle_remains_unchanged(self):
        before = snapshot(self.detached)
        self.invoke({"records": [executed()]})
        self.invoke({"records": [fact("not-run", reason="", evidence="observed-working")]})
        self.assertEqual(snapshot(self.detached), before)
        self.assertFalse(any(self.detached.rglob("__pycache__")))

    def test_report_metadata_keeps_domain_findings_separate(self):
        metadata = {"snapshot_date": "2026-10-25", "findings": [{"claim": "No paint check was run.", "evidence_ids": ["queue-check"]}],
                    "host_acceptance_verified": False, "task_empirical_tests_performed": False}
        process, checked = self.invoke({"records": [fact("not-run", reason="No account step requested")], "report": metadata})
        self.assertEqual(process.returncode, 0)
        self.assertTrue(checked["passed"])
        self.assertEqual(checked["findings"], [])
        document = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(document["findings"], metadata["findings"])
        self.assertIs(document["host_acceptance_verified"], False)
        self.assertIs(document["task_empirical_tests_performed"], False)
        self.assertEqual(document["evidence_records"], checked["evidence_records"])
        self.assertEqual(document["evidence_validation"], {"passed": True, "schema_version": 1, "findings": []})
        self.assertNotIn("passed", document)

    def test_report_metadata_cannot_override_reserved_fields(self):
        for field in ("records", "report", "passed", "schema_version", "evidence_records", "evidence_validation"):
            with self.subTest(field=field):
                process, checked = self.invoke({"records": [executed()], "report": {field: "override"}}, extra=("--fail-on-findings",))
                self.assertEqual(process.returncode, 1)
                self.assertEqual(checked["findings"][0]["code"], "reserved_report_field")
                self.assertFalse(self.output.exists())
                self.assertFalse(self.markdown.exists())

    def test_report_metadata_requires_an_object(self):
        for metadata in (None, [], "text", True, 7):
            with self.subTest(metadata=metadata):
                process, checked = self.invoke({"records": [executed()], "report": metadata})
                self.assertEqual(process.returncode, 0)
                self.assertEqual(checked["findings"][0]["code"], "invalid_report")
                self.assertFalse(self.output.exists())
                self.assertFalse(self.markdown.exists())

    def test_report_metadata_round_trips_without_changing_labels(self):
        metadata = {"recommendation": {"route": "A declared panel", "evidence_ids": ["queue-check"]},
                    "findings": [], "host_acceptance_verified": False, "task_empirical_tests_performed": False}
        raw = {"records": [fact("source-inspection", source="panel.ts:18")], "report": metadata}
        _process, checked = self.invoke(raw)
        self.assertEqual(json.loads(self.input.read_text(encoding="utf-8")), raw)
        document = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(LEDGER.classify_records(document), checked)
        replay = {"evidence_records": document["evidence_records"], "report": metadata}
        _process, replay_checked = self.invoke(replay)
        self.assertEqual(replay_checked, checked)
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8")), document)

    def test_invalid_report_metadata_preserves_existing_outputs(self):
        self.output.parent.mkdir()
        self.output.write_text("previous JSON", encoding="utf-8")
        self.markdown.write_text("previous Markdown", encoding="utf-8")
        _process, checked = self.invoke({"records": [executed()], "report": {"evidence_validation": {"passed": False}}})
        self.assertFalse(checked["passed"])
        self.assertEqual(self.output.read_text(encoding="utf-8"), "previous JSON")
        self.assertEqual(self.markdown.read_text(encoding="utf-8"), "previous Markdown")

    def test_report_metadata_does_not_change_markdown_or_bundle(self):
        before = snapshot(self.detached)
        _process, checked = self.invoke({"records": [fact("source-inspection", source="https://example.com/path_name?a=b&c=d")],
                                         "report": {"findings": ["Domain | text\n<details>"], "language": "en"}})
        self.assertTrue(checked["passed"])
        self.assertEqual(self.markdown.read_text(encoding="utf-8"), LEDGER.render_markdown(checked))
        self.assertEqual(snapshot(self.detached), before)
        self.assertFalse(any(self.detached.rglob("__pycache__")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTIFACTS / "results.json", help="Write the compact test receipt inside the owning artifact directory.")
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(ARTIFACTS.resolve()):
        parser.error("--output must remain inside projects/desktop-plugin-ui/artifacts/evidence-ledger-tests-20261025")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(EvidenceLedgerTests)
    tested = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"passed": tested.wasSuccessful(), "tests_run": tested.testsRun, "failures": len(tested.failures),
              "errors": len(tested.errors), "helper_sha256": digest(HELPER), "test_sha256": digest(Path(__file__)),
              "scope": "Typed evidence basis/outcome, no runtime inference, escaped Markdown, fail-closed outputs and immutable relocated standalone helper; no accounts, model or network."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if tested.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
