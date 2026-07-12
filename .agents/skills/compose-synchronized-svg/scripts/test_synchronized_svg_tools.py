#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Regression tests for the synchronized SVG scaffold and authoring tools."""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
import xml.etree.ElementTree as ET


sys.dont_write_bytecode = True

import compose_synchronized_svg as composer  # noqa: E402
import compile_synchronized_svg_plan as compiler  # noqa: E402
import audit_worker_supervisor as audit_supervisor  # noqa: E402
from compact_audit_report import compact_report  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SCAFFOLD = SCRIPT_DIR / "scaffold_synchronized_svg.py"
COMPOSER = SCRIPT_DIR / "compose_synchronized_svg.py"
COMPILER = SCRIPT_DIR / "compile_synchronized_svg_plan.py"
PREFLIGHT = SCRIPT_DIR / "preflight_svg_brief.py"
REPLACER = SCRIPT_DIR / "replace_svg_module.py"
VALIDATOR = SCRIPT_DIR / "validate_synchronized_svg.py"
AUDITOR = SCRIPT_DIR / "audit_synchronized_svg.py"
PLAN_TEMPLATE = SKILL_DIR / "assets" / "templates" / "composition-plan.json"
BRIEF_TEMPLATE = SKILL_DIR / "assets" / "templates" / "composition-brief.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fmt_number(value: object) -> str:
    return f"{float(value):.6f}".rstrip("0").rstrip(".") or "0"


class SynchronizedSvgToolTests(unittest.TestCase):
    """Exercise the public command-line behavior with isolated temporary files."""

    @classmethod
    def setUpClass(cls) -> None:
        for path in (
            SCAFFOLD,
            COMPOSER,
            COMPILER,
            PREFLIGHT,
            REPLACER,
            VALIDATOR,
            AUDITOR,
            PLAN_TEMPLATE,
            BRIEF_TEMPLATE,
        ):
            if not path.is_file():
                raise AssertionError(f"Required bundled test input is missing: {path}")

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="synchronized-svg-tools-")
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)

    def test_audit_supervisor_configures_both_standard_streams_as_utf8(self) -> None:
        class ConfigurableStream:
            def __init__(self) -> None:
                self.calls: list[dict[str, str]] = []

            def reconfigure(self, **options: str) -> None:
                self.calls.append(options)

        stdout = ConfigurableStream()
        stderr = ConfigurableStream()
        with (
            mock.patch.object(audit_supervisor.sys, "stdout", stdout),
            mock.patch.object(audit_supervisor.sys, "stderr", stderr),
        ):
            audit_supervisor.configure_utf8_standard_streams()

        expected = [{"encoding": "utf-8", "errors": "backslashreplace"}]
        self.assertEqual(stdout.calls, expected)
        self.assertEqual(stderr.calls, expected)

    def test_audit_supervisor_bounds_configured_and_explicit_timeouts(self) -> None:
        cases = {
            "invalid": 180.0,
            "nan": 180.0,
            "inf": 180.0,
            "12": 30.0,
            "45": 45.0,
            "1e308": audit_supervisor.MAX_ATTEMPT_TIMEOUT_SECONDS,
        }
        for configured, expected in cases.items():
            with self.subTest(configured=configured):
                with mock.patch.dict(
                    audit_supervisor.os.environ,
                    {"SYNC_SVG_AUDIT_ATTEMPT_TIMEOUT_SECONDS": configured},
                ):
                    self.assertEqual(audit_supervisor.configured_attempt_timeout(), expected)

        for explicit in (0, -1, float("nan"), float("inf"), 1e308):
            with self.subTest(explicit=explicit):
                with self.assertRaisesRegex(ValueError, "finite, greater than zero"):
                    audit_supervisor.supervise_worker(
                        ["worker"],
                        timeout_seconds=explicit,
                        popen_factory=mock.Mock(),
                    )

    def test_audit_supervisor_preserves_worker_output_and_exit_code(self) -> None:
        for returncode in (0, 17):
            with self.subTest(returncode=returncode):
                process = mock.Mock()
                process.communicate.return_value = ("salida ✓\n", "diagnóstico β\n")
                process.returncode = returncode
                factory = mock.Mock(return_value=process)
                stdout = io.StringIO()
                stderr = io.StringIO()

                observed = audit_supervisor.supervise_worker(
                    ["worker"],
                    timeout_seconds=0.1,
                    popen_factory=factory,
                    stdout=stdout,
                    stderr=stderr,
                )

                self.assertEqual(observed, returncode)
                self.assertEqual(stdout.getvalue(), "salida ✓\n")
                self.assertEqual(stderr.getvalue(), "diagnóstico β\n")
                factory.assert_called_once()
                process.communicate.assert_called_once_with(timeout=0.1)

    def test_audit_supervisor_retries_one_drained_timeout_then_succeeds(self) -> None:
        first = mock.Mock()
        first.communicate.side_effect = [
            subprocess.TimeoutExpired(
                ["worker"],
                0.1,
                output="partial stdout",
                stderr="partial stderr",
            ),
            ("drained stdout", "drained stderr"),
        ]
        second = mock.Mock()
        second.communicate.return_value = ("successful retry\n", "")
        second.returncode = 0
        factory = mock.Mock(side_effect=[first, second])
        stdout = io.StringIO()
        stderr = io.StringIO()

        with mock.patch.object(audit_supervisor, "terminate_process_tree") as terminate:
            observed = audit_supervisor.supervise_worker(
                ["worker"],
                timeout_seconds=0.1,
                popen_factory=factory,
                stdout=stdout,
                stderr=stderr,
            )

        self.assertEqual(observed, 0)
        self.assertEqual(factory.call_count, 2)
        terminate.assert_called_once_with(first)
        self.assertEqual(first.communicate.call_count, 2)
        self.assertEqual(stdout.getvalue(), "successful retry\n")
        self.assertIn("attempt 1 timed out; retrying once", stderr.getvalue())
        self.assertNotIn("drained stderr", stderr.getvalue())

    def test_audit_supervisor_double_timeout_returns_124_with_diagnostics(self) -> None:
        processes = []
        for index in (1, 2):
            process = mock.Mock()
            process.communicate.side_effect = [
                subprocess.TimeoutExpired(
                    ["worker"],
                    0.1,
                    output=f"partial {index}",
                    stderr=f"partial error {index}",
                ),
                (f"drained {index}\n", f"drained error {index}\n"),
            ]
            processes.append(process)
        factory = mock.Mock(side_effect=processes)
        stderr = io.StringIO()

        with mock.patch.object(audit_supervisor, "terminate_process_tree") as terminate:
            observed = audit_supervisor.supervise_worker(
                ["worker"],
                timeout_seconds=0.1,
                popen_factory=factory,
                stdout=io.StringIO(),
                stderr=stderr,
            )

        self.assertEqual(observed, 124)
        self.assertEqual(factory.call_count, 2)
        self.assertEqual(terminate.call_count, 2)
        self.assertIn("[browser-audit attempt 1 stdout]", stderr.getvalue())
        self.assertIn("drained error 2", stderr.getvalue())
        self.assertIn("timed out twice after 0.1 seconds per attempt", stderr.getvalue())

    def test_audit_supervisor_cancellation_cleans_up_and_reraises(self) -> None:
        process = mock.Mock()
        process.communicate.side_effect = [KeyboardInterrupt(), ("drained", "diagnostic")]
        factory = mock.Mock(return_value=process)

        with mock.patch.object(audit_supervisor, "terminate_process_tree") as terminate:
            with self.assertRaises(KeyboardInterrupt):
                audit_supervisor.run_worker_attempt(
                    ["worker"],
                    0.1,
                    popen_factory=factory,
                )

        terminate.assert_called_once_with(process)
        self.assertEqual(process.communicate.call_count, 2)

    def test_audit_supervisor_attach_cancellation_cleans_up_and_reraises(self) -> None:
        process = mock.Mock()
        factory = mock.Mock(return_value=process)

        with (
            mock.patch.object(
                audit_supervisor,
                "attach_worker_containment",
                side_effect=KeyboardInterrupt(),
            ),
            mock.patch.object(audit_supervisor, "terminate_and_drain") as cleanup,
        ):
            with self.assertRaises(KeyboardInterrupt):
                audit_supervisor.run_worker_attempt(
                    ["worker"],
                    0.1,
                    popen_factory=factory,
                )

        cleanup.assert_called_once_with(process)

    def test_audit_supervisor_result_cancellation_still_closes_containment(self) -> None:
        process = mock.Mock()
        process.communicate.return_value = ("complete", "")
        process.returncode = 0

        with (
            mock.patch.object(
                audit_supervisor,
                "_normalize_returncode",
                side_effect=KeyboardInterrupt(),
            ),
            mock.patch.object(audit_supervisor, "terminate_and_drain"),
            mock.patch.object(audit_supervisor, "close_worker_containment") as close,
        ):
            with self.assertRaises(KeyboardInterrupt):
                audit_supervisor.run_worker_attempt(
                    ["worker"],
                    0.1,
                    popen_factory=mock.Mock(return_value=process),
                )

        close.assert_called_once_with(process)

    def test_audit_supervisor_posix_cleanup_ignores_mock_pid(self) -> None:
        process = mock.Mock()
        with (
            mock.patch.object(audit_supervisor.os, "name", "posix"),
            mock.patch.object(audit_supervisor.os, "killpg", create=True) as killpg,
        ):
            audit_supervisor.close_worker_containment(process)
        killpg.assert_not_called()

    def test_audit_supervisor_timeout_drains_large_real_pipes(self) -> None:
        command = [
            sys.executable,
            "-c",
            (
                "import sys,time;"
                "sys.stderr.reconfigure(encoding='utf-8',errors='strict');"
                "sys.stdout.write('x'*300000);sys.stdout.flush();"
                "sys.stderr.write('unicode-diagnostic-β\\n');sys.stderr.flush();"
                "time.sleep(30)"
            ),
        ]

        result = audit_supervisor.run_worker_attempt(command, 2.0)

        self.assertIs(result.timed_out, True)
        self.assertEqual(result.returncode, 124)
        self.assertGreaterEqual(len(result.stdout), 300000)
        self.assertIn("unicode-diagnostic-β", result.stderr)

    def test_audit_supervisor_reaps_a_real_surviving_grandchild(self) -> None:
        command = [
            sys.executable,
            "-c",
            (
                "import subprocess,sys,time;time.sleep(0.2);"
                "child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],"
                "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);"
                "print(child.pid,flush=True);time.sleep(0.3)"
            ),
        ]
        grandchild_pid = -1

        def process_exists(pid: int) -> bool:
            if os.name == "nt":
                observed = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    check=False,
                )
                return str(pid) in observed.stdout
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return False
            except PermissionError:
                return True
            return True

        try:
            result = audit_supervisor.run_worker_attempt(command, 5)
            self.assertIs(result.timed_out, False)
            self.assertEqual(result.returncode, 0)
            grandchild_pid = int(result.stdout.strip())
            for _ in range(30):
                if not process_exists(grandchild_pid):
                    break
                time.sleep(0.1)
            self.assertIs(process_exists(grandchild_pid), False)
        finally:
            if grandchild_pid > 0 and process_exists(grandchild_pid):
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(grandchild_pid), "/T", "/F"],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    try:
                        os.kill(grandchild_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_browser_audit_compaction_keeps_failures_and_drops_passing_details(self) -> None:
        full_report = {
            "ok": False,
            "artifact": "atlas.svg",
            "report": "browser-audit.json",
            "screenshot": "overview.png",
            "failures": ["broken-check: mismatch"],
            "warnings": [],
            "browserErrors": {"console": [], "page": [], "request": []},
            "metrics": {"negativeControlComparisons": 513},
            "checks": [
                {"id": "passing-check", "ok": True, "details": {"large": list(range(100))}},
                {"id": "broken-check", "ok": False, "errors": ["mismatch"], "details": {"value": 2}},
            ],
            "snapshots": {"initial": {"revision": 0}, "scenarios": {"baseline": {}}, "timeline": []},
        }
        compact = compact_report(full_report)

        self.assertIs(compact.get("ok"), False)
        self.assertEqual(compact.get("failures"), ["broken-check: mismatch"])
        self.assertEqual(compact.get("failedChecks"), [full_report["checks"][1]])
        self.assertEqual(
            compact.get("checkSummary"),
            {
                "total": 2,
                "passed": 1,
                "failed": 1,
                "passedIds": ["passing-check"],
                "failedIds": ["broken-check"],
            },
        )
        self.assertEqual(compact.get("snapshotSummary"), {"initial": 1, "scenarios": 1, "timeline": 0})
        self.assertNotIn("large", json.dumps(compact))

    def test_extended_canonical_palette_never_wraps_silently(self) -> None:
        colors = [composer.scaffold.color_for_index(index) for index in range(96)]
        self.assertEqual(len(colors), len(set(colors)))
        self.assertTrue(all(re.fullmatch(r"#[0-9a-f]{6}", color) for color in colors))

    def test_literal_formatting_matches_en_us_intl_contract(self) -> None:
        format_value = composer.scaffold.format_value
        self.assertEqual(
            format_value(
                2.5,
                {"style": "currency", "currency": "USD", "maximumFractionDigits": 0},
                "en-US",
            ),
            "$3",
        )
        self.assertEqual(
            format_value(
                -2.5,
                {"style": "currency", "currency": "USD", "maximumFractionDigits": 0},
                "en-US",
            ),
            "-$3",
        )
        self.assertEqual(
            format_value(1234.5, {"style": "decimal", "maximumFractionDigits": 1}, "en-US"),
            "1,234.5",
        )
        self.assertEqual(
            format_value(0.25, {"style": "percent", "maximumFractionDigits": 2}, "en-US"),
            "25%",
        )
        self.assertEqual(format_value(1.2345, {"style": "decimal"}, "en-US"), "1.235")
        self.assertEqual(
            format_value(12.5, {"style": "currency", "currency": "INR"}, "en-US"),
            "INR\u00a012.50",
        )
        self.assertEqual(
            format_value(12.5, {"style": "currency", "currency": "KRW"}, "en-US"),
            "KRW\u00a012.50",
        )
        self.assertEqual(
            format_value(12, {"style": "currency", "currency": "JPY"}, "en-US"),
            "¥12.00",
        )
        tiny_formats = [
            (
                8e-10,
                {"style": "decimal", "maximumFractionDigits": 2, "suffix": " units"},
                "8E-10 units",
            ),
            (
                -8e-10,
                {"style": "currency", "currency": "USD", "maximumFractionDigits": 2},
                "-$8E-10",
            ),
            (
                8e-10,
                {"style": "percent", "maximumFractionDigits": 1},
                "8E-8%",
            ),
        ]
        for value, format_spec, expected in tiny_formats:
            with self.subTest(value=value, format=format_spec):
                self.assertEqual(format_value(value, format_spec, "en-US"), expected)

        self.assertEqual(compiler.clean_number(5e-13), 5e-13)
        self.assertEqual(compiler.clean_number(1.0000000000005), 1.0000000000005)
        self.assertEqual(composer.scaffold.canonical_number_text(8e-10), "8e-10")
        self.assertEqual(composer.scaffold.canonical_number_text(-0.0), "0")
        for node, expected in (
            ({"op": "round", "args": [2.5]}, 3.0),
            ({"op": "round", "args": [-2.5]}, -2.0),
            ({"op": "round", "args": [1.25, 1]}, 1.3),
        ):
            with self.subTest(round_node=node):
                self.assertEqual(composer.scaffold.eval_node(node, {}), expected)
        self.assertEqual(compiler.flow_reconciliation(8e-10, [8e-10]), (True, 8e-10))
        overflow_reconciles, overflow_total = compiler.flow_reconciliation(1e308, [-1e308])
        self.assertIs(overflow_reconciles, False)
        self.assertEqual(overflow_total, -1e308)

        brief = self.edge_brief()
        brief["locale"] = "de-DE"
        brief_path = self.write_plan("unsupported-locale-brief.json", brief)
        output = self.workspace / "unsupported-locale-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(output),
            "--json",
        )
        report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 1)
        self.assertIn("locale must be 'en-US'", str(report.get("error")))
        self.assertFalse(output.exists())

    def test_radial_gauge_readout_preserves_opaque_identity_cue(self) -> None:
        brief = self.edge_brief()
        brief["concepts"].extend(
            [
                {
                    "id": "tax-rate",
                    "label": "Effective tax rate",
                    "unit": "fraction",
                    "default": 0.22,
                    "domain": [0, 0.6],
                },
                {
                    "id": "tax-annual",
                    "label": "Annual tax",
                    "unit": "USD/year",
                    "default": 22000,
                    "domain": [0, 100000],
                },
            ]
        )
        for scenario in brief["scenarios"]:
            scenario["values"]["tax-rate"] = 0.22 if scenario["id"] == "baseline" else 0.24
            scenario["values"]["tax-annual"] = 22000 if scenario["id"] == "baseline" else 32400
        brief["modules"].append(
            {
                "id": "effective-tax-rate",
                "question": "What bounded rate controls the deduction model?",
                "claim": "The effective tax rate stays inspectable as a bounded policy input.",
                "assetType": "radial-gauge",
                "selectionRationale": "A radial gauge exposes the bounded fractional input directly.",
                "rejectedAlternative": "A second table would hide the bounded rate posture.",
                "values": ["tax-rate"],
                "focusGroups": ["pressure-story"],
            }
        )
        pressure_group = next(
            group for group in brief["focusGroups"] if group["id"] == "pressure-story"
        )
        pressure_group["moduleIds"].append("effective-tax-rate")
        brief_path = self.write_plan("opaque-gauge-brief.json", brief)
        plan_path = self.workspace / "opaque-gauge-plan.json"
        output = self.workspace / "opaque-gauge.svg"

        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        cue = plan["identity"]["tax-rate"]["nonColor"][0]
        self.assertRegex(cue, r"^cue\d{2}$")
        gauge = next(module for module in plan["modules"] if module["id"] == "effective-tax-rate")
        tax_bindings = [binding for binding in gauge["bindings"] if binding["value"] == "tax-rate"]
        self.assertEqual(len(tax_bindings), 2)
        self.assertTrue(all(cue in binding["selector"] for binding in tax_bindings))

        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        validated, report = self.validate_json(output, "--require-time-sync")
        self.assertEqual(validated.returncode, 0, msg=validated.stderr or validated.stdout)
        self.assertIs(report.get("ok"), True)

    def test_composed_svg_supports_seventeen_independent_tokens_and_scaled_aliases(self) -> None:
        brief = self.edge_brief()
        extra_ids = [f"independent-signal-{index:02d}" for index in range(1, 7)]
        for index, value_id in enumerate(extra_ids, start=1):
            brief["concepts"].append(
                {
                    "id": value_id,
                    "label": f"Independent signal {index}",
                    "unit": "score",
                    "default": index,
                    "domain": [0, 20],
                }
            )
            for scenario in brief["scenarios"]:
                scenario["values"][value_id] = index + (
                    1 if scenario["id"] == "surge" else 0
                )
        brief["derived"].append(
            {
                "id": "request-rate-per-minute",
                "label": "Request rate per minute",
                "unit": "requests/minute",
                "compute": {
                    "op": "multiply",
                    "args": [{"ref": "request-rate"}, 60],
                },
            }
        )
        ledger = next(module for module in brief["modules"] if module["id"] == "edge-ledger")
        ledger["values"].extend([*extra_ids, "request-rate-per-minute"])
        brief_path = self.write_plan("extended-palette-brief.json", brief)
        plan_path = self.workspace / "extended-palette-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        request_alias = next(
            alias
            for alias in plan["identityAliases"]
            if "request-rate-per-minute" in alias["values"]
        )
        self.assertEqual(
            request_alias["values"],
            ["request-rate", "request-rate-per-minute"],
        )
        self.assertEqual(
            plan["identity"][request_alias["identity"]]["colorToken"],
            "request-rate",
        )
        self.assertEqual(
            len({record["colorToken"] for record in plan["identity"].values()}),
            17,
        )
        output = self.workspace / "extended-palette.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        validated, report = self.validate_json(output, "--require-time-sync")
        self.assertEqual(validated.returncode, 0, msg=validated.stderr or validated.stdout)
        identity_metrics = report.get("metrics", {}).get("identity", {})
        self.assertEqual(identity_metrics.get("canonicalIdentityCount"), 17)
        self.assertEqual(identity_metrics.get("physicalColorTokenCount"), 17)
        self.assertEqual(identity_metrics.get("physicalColorCollisions"), {})

    def run_tool(self, script: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *arguments],
            cwd=self.workspace,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

    def parse_json_stdout(self, result: subprocess.CompletedProcess[str]) -> dict[str, object]:
        try:
            value = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            self.fail(
                "Tool output was not valid JSON. "
                f"Exit code: {result.returncode}; stdout: {result.stdout!r}; stderr: {result.stderr!r}; error: {error}"
            )
        self.assertIsInstance(value, dict)
        return value

    def write_plan(self, name: str, plan: dict[str, object]) -> Path:
        path = self.workspace / name
        path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n")
        return path

    def template_plan(self) -> dict[str, object]:
        value = json.loads(PLAN_TEMPLATE.read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return value

    def edge_brief(self) -> dict[str, object]:
        return {
            "compositionId": "edge-delivery-atlas",
            "title": "Edge Delivery Atlas",
            "subtitle": "One request model expressed through topology, flow, load, and delay",
            "provenance": "Synthetic edge-delivery values supplied solely for deterministic regression coverage.",
            "initialScenario": "baseline",
            "armature": "asymmetric-flow-spine",
            "concepts": [
                {
                    "id": "request-rate",
                    "label": "Request rate",
                    "unit": "requests/second",
                    "default": 1200,
                    "domain": [0, 3000],
                },
                {
                    "id": "edge-capacity",
                    "label": "Edge capacity",
                    "unit": "requests/second",
                    "default": 1600,
                    "domain": [0, 3000],
                },
                {
                    "id": "cache-hit-rate",
                    "label": "Cache hit rate",
                    "unit": "fraction",
                    "default": 0.72,
                    "domain": [0, 1],
                },
                {
                    "id": "edge-latency",
                    "label": "Edge latency",
                    "unit": "milliseconds",
                    "default": 18,
                    "domain": [1, 200],
                },
                {
                    "id": "origin-latency",
                    "label": "Origin latency",
                    "unit": "milliseconds",
                    "default": 110,
                    "domain": [1, 500],
                },
            ],
            "derived": [
                {
                    "id": "edge-served-rate",
                    "label": "Edge-served requests",
                    "unit": "requests/second",
                    "compute": {
                        "op": "multiply",
                        "args": [{"ref": "request-rate"}, {"ref": "cache-hit-rate"}],
                    },
                },
                {
                    "id": "origin-rate",
                    "label": "Origin requests",
                    "unit": "requests/second",
                    "compute": {
                        "op": "multiply",
                        "args": [
                            {"ref": "request-rate"},
                            {
                                "op": "subtract",
                                "args": [1, {"ref": "cache-hit-rate"}],
                            },
                        ],
                    },
                },
                {
                    "id": "edge-load-ratio",
                    "label": "Demand / edge capacity",
                    "unit": "fraction",
                    "compute": {
                        "op": "divide",
                        "args": [{"ref": "request-rate"}, {"ref": "edge-capacity"}],
                    },
                },
                {
                    "id": "overload",
                    "label": "Excess demand",
                    "unit": "requests/second",
                    "compute": {
                        "op": "max",
                        "args": [
                            {
                                "op": "subtract",
                                "args": [{"ref": "request-rate"}, {"ref": "edge-capacity"}],
                            },
                            0,
                        ],
                    },
                },
                {
                    "id": "blended-latency",
                    "label": "Blended latency",
                    "unit": "milliseconds",
                    "compute": {
                        "op": "add",
                        "args": [
                            {
                                "op": "multiply",
                                "args": [{"ref": "cache-hit-rate"}, {"ref": "edge-latency"}],
                            },
                            {
                                "op": "multiply",
                                "args": [
                                    {
                                        "op": "subtract",
                                        "args": [1, {"ref": "cache-hit-rate"}],
                                    },
                                    {"ref": "origin-latency"},
                                ],
                            },
                        ],
                    },
                },
                {
                    "id": "headroom",
                    "label": "Capacity headroom",
                    "unit": "requests/second",
                    "compute": {
                        "op": "subtract",
                        "args": [{"ref": "edge-capacity"}, {"ref": "request-rate"}],
                    },
                },
            ],
            "scenarios": [
                {
                    "id": "baseline",
                    "label": "Baseline",
                    "values": {
                        "request-rate": 1200,
                        "edge-capacity": 1600,
                        "cache-hit-rate": 0.72,
                        "edge-latency": 18,
                        "origin-latency": 110,
                    },
                },
                {
                    "id": "surge",
                    "label": "Traffic surge",
                    "values": {
                        "request-rate": 2600,
                        "edge-capacity": 1900,
                        "cache-hit-rate": 0.61,
                        "edge-latency": 42,
                        "origin-latency": 280,
                    },
                },
            ],
            "modules": [
                {
                    "id": "traffic-topology",
                    "question": "Which values govern the edge-to-origin delivery system?",
                    "claim": "Request, capacity, and routing values form one shared topology.",
                    "assetType": "network-diagram",
                    "selectionRationale": "A network exposes the shared edge-delivery dependencies.",
                    "rejectedAlternative": "A table would hide the dependency structure.",
                    "values": ["request-rate", "edge-capacity", "edge-served-rate", "origin-rate"],
                    "focusGroups": ["routing-story"],
                },
                {
                    "id": "service-mix",
                    "question": "How is incoming traffic split between edge and origin?",
                    "claim": "The same request rate resolves into edge-served and origin traffic.",
                    "assetType": "stacked-bar-chart",
                    "selectionRationale": "A stack reconciles the service split to one total.",
                    "rejectedAlternative": "Separate bars would weaken the part-to-whole reading.",
                    "values": ["edge-served-rate", "origin-rate"],
                    "stackTotal": "request-rate",
                    "focusGroups": ["routing-story"],
                },
                {
                    "id": "load-ratio-bullet",
                    "question": "How close is request demand to edge capacity?",
                    "claim": "The load ratio responds to both request rate and the capacity divisor.",
                    "assetType": "bullet-chart",
                    "selectionRationale": "A bullet chart centers the capacity threshold comparison.",
                    "rejectedAlternative": "A radial gauge would obscure the threshold axis.",
                    "values": ["edge-load-ratio"],
                    "focusGroups": ["pressure-story"],
                },
                {
                    "id": "request-flow",
                    "question": "Where does each incoming request go?",
                    "claim": "Edge service and origin service reconcile to one incoming stream.",
                    "assetType": "sankey-diagram",
                    "selectionRationale": "A flow diagram preserves the shared incoming stream.",
                    "rejectedAlternative": "A pie chart would not show routing direction.",
                    "values": ["request-rate", "edge-served-rate", "origin-rate"],
                    "focusGroups": ["routing-story", "pressure-story"],
                },
                {
                    "id": "latency-consequence",
                    "question": "How do edge and origin delay combine for users?",
                    "claim": "Blended latency changes with both routing share and endpoint delay.",
                    "assetType": "bar-chart",
                    "selectionRationale": "Bars support direct delay comparison on a common scale.",
                    "rejectedAlternative": "A map would add geography that the data does not supply.",
                    "values": ["edge-latency", "origin-latency", "blended-latency"],
                    "focusGroups": ["pressure-story"],
                },
                {
                    "id": "edge-ledger",
                    "question": "What exact values describe the current edge state?",
                    "claim": "The ledger keeps topology and flow readings numerically inspectable.",
                    "assetType": "comparison-table",
                    "selectionRationale": "A table supports exact cross-checks of shared state.",
                    "rejectedAlternative": "Another chart would make exact lookup slower.",
                    "values": [
                        "request-rate",
                        "edge-capacity",
                        "edge-load-ratio",
                        "headroom",
                        "blended-latency",
                    ],
                    "focusGroups": ["pressure-story"],
                },
                {
                    "id": "load-response",
                    "question": "Which outcomes move as edge pressure rises?",
                    "claim": "Load ratio, overload, and blended latency expose the surge response.",
                    "assetType": "line-chart",
                    "selectionRationale": "A line family shows coordinated movement through the timeline.",
                    "rejectedAlternative": "Static bars would weaken the temporal reading.",
                    "values": ["edge-load-ratio", "overload", "blended-latency"],
                    "focusGroups": ["pressure-story"],
                },
            ],
            "focusGroups": [
                {
                    "id": "routing-story",
                    "label": "Request routing",
                    "moduleIds": ["traffic-topology", "service-mix", "request-flow"],
                },
                {
                    "id": "pressure-story",
                    "label": "Capacity pressure",
                    "moduleIds": [
                        "load-ratio-bullet",
                        "request-flow",
                        "latency-consequence",
                        "edge-ledger",
                        "load-response",
                    ],
                },
            ],
            "timeline": {
                "durationMs": 12000,
                "phases": [
                    {
                        "id": "baseline-phase",
                        "focusId": "routing-story",
                        "values": {"request-rate": 1200, "edge-capacity": 1600},
                    },
                    {
                        "id": "surge-phase",
                        "focusId": "pressure-story",
                        "values": {"request-rate": 2600, "edge-capacity": 1900},
                    },
                    {
                        "id": "recovery-phase",
                        "values": {"request-rate": 1450, "edge-capacity": 2200},
                    },
                    {
                        "id": "return-phase",
                        "focusId": "routing-story",
                        "values": {"request-rate": 1200, "edge-capacity": 1600},
                    },
                ],
            },
        }

    def tiny_edge_brief(self) -> dict[str, object]:
        brief = self.edge_brief()
        factor = 5e-13
        scaled_ids = {"request-rate", "edge-capacity"}
        brief["concepts"].extend(
            [
                {
                    "id": "tiny-cost",
                    "label": "Tiny annual cost",
                    "unit": "INR/year",
                    "default": -8e-10,
                    "domain": [-1e-9, 1e-9],
                },
                {
                    "id": "tiny-probability",
                    "label": "Tiny probability",
                    "unit": "fraction",
                    "default": 8e-10,
                    "domain": [0, 1e-8],
                },
            ]
        )
        for concept in brief["concepts"]:
            if concept["id"] in scaled_ids:
                concept["default"] *= factor
                concept["domain"] = [value * factor for value in concept["domain"]]
        for scenario in brief["scenarios"]:
            for value_id in scaled_ids:
                scenario["values"][value_id] *= factor
            scenario["values"]["tiny-cost"] = -8e-10 if scenario["id"] == "baseline" else 8e-10
            scenario["values"]["tiny-probability"] = 8e-10 if scenario["id"] == "baseline" else 2e-9
        for phase in brief["timeline"]["phases"]:
            for value_id in scaled_ids:
                if value_id in phase["values"]:
                    phase["values"][value_id] *= factor
        ledger = next(module for module in brief["modules"] if module["id"] == "edge-ledger")
        ledger["values"].extend(["tiny-cost", "tiny-probability"])
        return brief

    def scaffold_template(self, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = self.run_tool(
            SCAFFOLD,
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(output.relative_to(self.workspace)),
            "--json",
        )
        report = self.parse_json_stdout(result)
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIs(report.get("ok"), True)
        return result, report

    def validate_json(self, svg: Path, *arguments: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = self.run_tool(VALIDATOR, str(svg), *arguments, "--json")
        return result, self.parse_json_stdout(result)

    def test_template_scaffold_passes_structural_validation(self) -> None:
        requested = self.workspace / "requested" / "nested" / "compensation-atlas.svg"
        _, scaffold_report = self.scaffold_template(requested)

        self.assertEqual(Path(str(scaffold_report["output"])), requested.resolve())
        self.assertTrue(requested.is_file())
        self.assertEqual(sorted(self.workspace.rglob("*.svg")), [requested])

        validation_path = self.workspace / "reports" / "exact-static-report.json"
        result, report = self.validate_json(
            requested,
            "--allow-placeholders",
            "--require-time-sync",
            "--output",
            str(validation_path.relative_to(self.workspace)),
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIs(report.get("ok"), True)
        self.assertTrue(validation_path.is_file())
        self.assertEqual(json.loads(validation_path.read_text(encoding="utf-8")), report)
        metrics = report.get("metrics")
        self.assertIsInstance(metrics, dict)
        assert isinstance(metrics, dict)
        self.assertEqual(metrics.get("compositionId"), "workshop-throughput-atlas")
        self.assertEqual(metrics.get("moduleCount"), 6)
        self.assertGreaterEqual(int(metrics.get("assetTypeCount", 0)), 3)
        self.assertGreater(int(metrics.get("bindingCount", 0)), 0)

    def test_composer_creates_deterministic_final_svg(self) -> None:
        output = self.workspace / "final" / "compensation-atlas.svg"
        report_path = self.workspace / "reports" / "composition.json"
        arguments = (
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(output.relative_to(self.workspace)),
            "--report",
            str(report_path.relative_to(self.workspace)),
            "--json",
        )

        first = self.run_tool(COMPOSER, *arguments)
        first_report = self.parse_json_stdout(first)
        self.assertEqual(first.returncode, 0, msg=first.stderr or first.stdout)
        self.assertIs(first_report.get("ok"), True)
        self.assertEqual(Path(str(first_report["output"])), output.resolve())
        self.assertEqual(first_report.get("containsPlaceholders"), False)
        modules = first_report.get("modules")
        self.assertIsInstance(modules, list)
        assert isinstance(modules, list)
        self.assertEqual(len(modules), 6)
        self.assertGreaterEqual(len({item["family"] for item in modules if isinstance(item, dict)}), 4)
        self.assertTrue(output.is_file())
        self.assertTrue(report_path.is_file())
        first_hash = sha256(output)

        validation, validation_report = self.validate_json(output, "--require-time-sync")
        self.assertEqual(validation.returncode, 0, msg=validation.stderr or validation.stdout)
        self.assertIs(validation_report.get("ok"), True)
        metrics = validation_report.get("metrics")
        self.assertIsInstance(metrics, dict)
        assert isinstance(metrics, dict)
        self.assertEqual(metrics.get("placeholderCount"), 0)
        self.assertEqual(metrics.get("moduleCount"), 6)
        self.assertEqual(metrics.get("bindingCount"), 22)
        self.assertEqual(metrics.get("accessibleBindingCount"), 22)

        root = ET.parse(output).getroot()
        self.assertEqual(root.get("role"), "group")
        module_groups = [element for element in root.iter() if element.get("data-module-id")]
        self.assertEqual(len(module_groups), 6)
        self.assertTrue(all(element.get("role") == "group" for element in module_groups))
        bound_marks = [element for element in root.iter() if element.get("data-bind")]
        self.assertEqual(len(bound_marks), 22)
        self.assertTrue(all(element.get("role") in {"img", "meter"} for element in bound_marks))

        conflict = self.run_tool(COMPOSER, *arguments)
        conflict_report = self.parse_json_stdout(conflict)
        self.assertEqual(conflict.returncode, 1)
        self.assertIs(conflict_report.get("ok"), False)
        self.assertEqual(sha256(output), first_hash)

        forced = self.run_tool(COMPOSER, *arguments[:-1], "--force", "--json")
        forced_report = self.parse_json_stdout(forced)
        self.assertEqual(forced.returncode, 0, msg=forced.stderr or forced.stdout)
        self.assertIs(forced_report.get("ok"), True)
        self.assertEqual(sha256(output), first_hash)
        self.assertEqual(sorted(self.workspace.rglob("*.svg")), [output])

    def test_composer_semantic_annotations_and_layout_hooks_are_deterministic(self) -> None:
        output = self.workspace / "semantic" / "workshop-throughput.svg"
        result = self.run_tool(
            COMPOSER,
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(output.relative_to(self.workspace)),
            "--json",
        )
        report = self.parse_json_stdout(result)
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIs(report.get("ok"), True)

        root = ET.parse(output).getroot()
        elements = [element for element in root.iter() if isinstance(element.tag, str)]
        provenance = next(element for element in elements if element.get("class") == "provenance")
        self.assertEqual(
            provenance.text,
            "Illustrative values supplied in this brief; all outputs are synthetic planning estimates.",
        )
        visible_text = {" ".join((element.text or "").split()) for element in elements if element.tag.endswith("text")}
        for expected in (
            "Incoming work",
            "Processing capacity",
            "First pass success",
            "Capacity applied",
            "Completed work",
            "First pass failures",
            "Excess arrivals",
            "Demand / capacity",
            "100% target",
        ):
            self.assertIn(expected, visible_text)
        forbidden = {
            "Input Rate Text",
            "Capacity Cue02 Text",
            "Success Rate Transform",
            "Processed Rate Height",
            "Completed Rate Width",
            "Unserved Rate Width",
        }
        self.assertTrue(forbidden.isdisjoint(visible_text))

        stack_plots = [element for element in elements if element.get("data-sync-layout") == "stack"]
        self.assertEqual(stack_plots, [])

        waterfalls = [element for element in elements if element.get("data-sync-layout") == "waterfall"]
        self.assertEqual(len(waterfalls), 1)
        waterfall_items = [element for element in waterfalls[0] if element.get("data-sync-layout-item") == "waterfall"]
        connectors = [element for element in waterfalls[0] if element.get("data-sync-layout-connector") is not None]
        self.assertEqual(len(waterfall_items), 3)
        self.assertEqual(len(connectors), 2)
        self.assertIn("scale(1 -", str(waterfall_items[0].get("transform")))
        self.assertNotIn("scale(1 -", str(waterfall_items[1].get("transform")))
        self.assertIn("scale(1 -", str(waterfall_items[2].get("transform")))

        flow_plots = [element for element in elements if element.get("data-sync-layout") == "flow"]
        self.assertEqual(len(flow_plots), 1)
        flow_items = [element for element in flow_plots[0] if element.get("data-sync-layout-item") == "flow"]
        expected_flow_directions = {
            "completed-rate-width": "forward",
            "first-pass-failure-rate-width": "forward",
            "unserved-rate-width": "zero",
        }
        self.assertEqual(
            {item.get("data-layout-bound-role") for item in flow_items},
            set(expected_flow_directions),
        )
        for item in flow_items:
            paths = [child for child in item if child.get("data-sync-flow-path") is not None]
            self.assertEqual(len(paths), 1)
            role = item.get("data-layout-bound-role") or ""
            direction = expected_flow_directions[role]
            self.assertEqual(item.get("data-flow-direction"), direction)
            if direction == "zero":
                self.assertEqual(float(str(paths[0].get("stroke-width"))), 0)
            else:
                self.assertGreater(float(str(paths[0].get("stroke-width"))), 0)
            self.assertIsNone(paths[0].get("marker-end"))
            self.assertIsNone(paths[0].get("stroke-dasharray"))
            sign_label = next(child for child in item if child.get("data-flow-sign-label") == "true")
            self.assertEqual((sign_label.text or "").strip(), "")
            value_label = next(child for child in item if child.get("data-flow-value-label") == "true")
            self.assertTrue((value_label.text or "").strip())
            roles = {child.get("data-role") for child in item.iter() if child.get("data-role") is not None}
            self.assertIn(role, roles)
        flow_sources = [element for element in flow_plots[0] if element.get("data-flow-source") == "true"]
        self.assertEqual(len(flow_sources), 1)
        self.assertIn("input-rate-width", {child.get("data-role") for child in flow_sources[0].iter()})
        source_frame = next(element for element in flow_sources[0] if element.get("data-flow-source-frame") == "true")
        source_label = next(element for element in flow_plots[0] if element.get("data-flow-source-label") == "true")
        source_label_gap = float(source_frame.get("y", "0")) - float(source_label.get("y", "0"))
        self.assertGreaterEqual(source_label_gap, 6)
        self.assertLessEqual(source_label_gap, 12)

        waterfall_ratios = []
        for item in waterfall_items:
            mark = next(child for child in item if child.get("data-bind") is not None)
            raw = abs(float(mark.get("data-current-value", "nan")))
            rendered = float(mark.get("height", "nan"))
            scale_match = re.search(r"scale\(1\s+(-?[0-9.]+)\)", item.get("transform", ""))
            self.assertIsNotNone(scale_match)
            assert scale_match is not None
            if raw > 1e-9:
                waterfall_ratios.append(abs(rendered * float(scale_match.group(1))) / raw)
            else:
                self.assertAlmostEqual(float(scale_match.group(1)), 0.0)
        self.assertLess(max(waterfall_ratios) - min(waterfall_ratios), 1e-7)

        target_markers = [element for element in elements if element.get("data-target-ratio") == "1"]
        self.assertEqual(len(target_markers), 1)
        self.assertEqual(target_markers[0].get("aria-label"), "100% target")
        quality_needles = [
            element
            for element in elements
            if element.get("data-bind") == "success-rate" and element.get("data-channel") == "transform"
        ]
        self.assertEqual(len(quality_needles), 1)
        self.assertEqual(quality_needles[0].get("transform"), "rotate(-32.4 240 190)")
        for expected in ("75% current", "150% max"):
            self.assertIn(expected, visible_text)

        flow_starts = []
        for item in flow_items:
            path = next(child for child in item if child.get("data-sync-flow-path") is not None)
            start = re.match(r"M[-0-9.]+\s+([-0-9.]+)", path.get("d", ""))
            self.assertIsNotNone(start)
            assert start is not None
            flow_starts.append(float(start.group(1)))
        self.assertEqual(len(set(flow_starts)), len(flow_starts))

        expected_identity_tokens = {
            "input-rate": "--concept-input-rate",
            "capacity": "--concept-capacity",
            "success-rate": "--concept-success-rate",
            "completed-rate": "--concept-completed-rate",
            "unserved-rate": "--concept-unserved-rate",
            "demand-capacity-ratio": "--concept-demand-capacity-ratio",
        }
        for value_id, token in expected_identity_tokens.items():
            bound = [element for element in elements if element.get("data-bind") == value_id]
            self.assertTrue(bound, msg=f"missing rendered binding for {value_id}")
            self.assertTrue(
                any(token in " ".join(str(value) for value in element.attrib.values()) for element in bound),
                msg=f"{value_id} did not retain canonical identity token {token}",
            )

        bound_elements = [element for element in elements if element.get("data-bind") is not None]
        self.assertEqual(len(bound_elements), 22)
        for element in bound_elements:
            value_id = element.get("data-bind") or ""
            accessible_value = element.get("data-accessible-value") or ""
            aria_label = element.get("aria-label") or ""
            self.assertTrue(element.get("data-accessible-label"))
            self.assertTrue(accessible_value)
            self.assertIn(accessible_value, aria_label)
            if "-" in value_id:
                self.assertNotIn(value_id, aria_label)
            if element.get("role") == "meter":
                self.assertEqual(element.get("aria-valuetext"), accessible_value)
                for attribute in ("aria-valuemin", "aria-valuemax", "aria-valuenow"):
                    self.assertIsNotNone(element.get(attribute))
            else:
                self.assertIsNone(element.get("aria-valuetext"))
        by_role = {element.get("data-role"): element for element in bound_elements}
        self.assertEqual(by_role["input-rate-width"].get("aria-label"), "Incoming work: 60 items/hour")
        self.assertEqual(by_role["success-rate-transform"].get("aria-label"), "First pass success: 82%")
        self.assertEqual(by_role["unserved-rate-width"].get("aria-label"), "Excess arrivals: 0 items/hour")
        self.assertEqual(
            composer.accessible_value_text(-0.0, {}, "items/hour", "en-US"),
            "0 items/hour",
        )
        self.assertEqual(
            composer.accessible_value_text(-0.0, {}, "fraction", "en-US"),
            "0%",
        )

        explicit_sizes = [
            float(element.get("font-size"))
            for element in elements
            if element.tag.endswith("text") and element.get("font-size") is not None
        ]
        self.assertTrue(explicit_sizes)
        self.assertGreaterEqual(min(explicit_sizes), 10)
        script = next(element for element in elements if element.tag.endswith("script"))
        runtime = script.text or ""
        for hook in (
            "function layoutStack",
            "function layoutWaterfall",
            "function layoutFlow",
            "layoutModule(group)",
            "data-flow-source-frame",
            "data-flow-source-label",
            "data-flow-direction",
            "const rawValue = numeric(mark.dataset.currentValue",
            "const scaled = Math.abs(rendered)",
            "const zero = rawValue === 0",
            "DEFICIT",
            "data-progress-current",
            "formatAccessibleValue",
            "function updatePlaybackControl",
        ):
            self.assertIn(hook, runtime)
        style = next(element for element in elements if element.tag.endswith("style"))
        style_text = style.text or ""
        self.assertNotIn('data-focused="false"] { opacity:', style_text)
        self.assertIn("filter: opacity(48%) saturate(58%)", style_text)
        focus_controls = [
            element for element in elements if element.get("data-module-focus-id") is not None
        ]
        expected_focus_controls = sum(
            len(module.get("focusGroups", [])) for module in self.template_plan()["modules"]
        )
        self.assertEqual(len(focus_controls), expected_focus_controls)
        self.assertTrue(all(control.get("role") == "button" for control in focus_controls))
        self.assertTrue(all(control.get("tabindex") == "0" for control in focus_controls))
        self.assertTrue(all(control.get("aria-pressed") == "false" for control in focus_controls))
        self.assertTrue(all(control.get("aria-label", "").startswith("Toggle ") for control in focus_controls))
        self.assertTrue(all(control.get("id", "").startswith("module-focus-toggle-") for control in focus_controls))
        module_groups = [element for element in elements if element.get("data-module-id")]
        self.assertTrue(all(group.get("role") == "group" for group in module_groups))
        self.assertTrue(all(group.get("tabindex") is None for group in module_groups))
        self.assertEqual(
            [group.get("data-module-id") for group in module_groups],
            self.template_plan()["layout"]["readingOrder"],
        )
        self.assertIn('.module-focus-control[aria-pressed="true"]', style_text)
        self.assertIn(".focus-region-label", style_text)
        self.assertIn(".focus-region-label-plaque", style_text)
        focus_region_layers = [
            element
            for element in elements
            if element.get("id") in {"composition-focus-regions", "composition-focus-region-labels"}
        ]
        self.assertEqual(len(focus_region_layers), 2)
        self.assertTrue(all(layer.get("pointer-events") == "none" for layer in focus_region_layers))
        focus_label_groups = [
            element for element in elements if element.get("class") == "focus-region-label-group"
        ]
        self.assertTrue(focus_label_groups)
        for group in focus_label_groups:
            plaque = next(child for child in group if child.get("class") == "focus-region-label-plaque")
            label = next(child for child in group if child.get("class") == "focus-region-label")
            self.assertEqual(label.get("data-clearance-mask"), "true")
            self.assertEqual(list(group).index(plaque) + 1, list(group).index(label))
        timeline_track = next(element for element in elements if element.get("class") == "timeline-track")
        timeline_bottom = float(timeline_track.get("y", "nan")) + float(
            timeline_track.get("height", "nan")
        )
        first_plaque_top = min(
            float(plaque.get("y", "nan"))
            for group in focus_label_groups
            for plaque in group
            if plaque.get("class") == "focus-region-label-plaque"
        )
        self.assertLess(timeline_bottom, first_plaque_top)
        raw_svg = output.read_text(encoding="utf-8")
        self.assertLess(raw_svg.index('id="composition-focus-regions"'), raw_svg.index('id="composition-relationships"'))
        self.assertLess(raw_svg.index('id="composition-relationships"'), raw_svg.index('id="composition-focus-region-labels"'))
        self.assertLess(raw_svg.index('id="composition-focus-region-labels"'), raw_svg.index('id="composition-modules"'))
        play_control = next(element for element in elements if element.get("id") == "control-play")
        self.assertEqual(play_control.get("aria-label"), "Play the master timeline")
        self.assertEqual(play_control.get("aria-pressed"), "false")
        self.assertEqual(play_control.get("aria-disabled"), "false")

        relationships = [element for element in elements if element.get("data-relationship-id")]
        self.assertEqual(
            {element.get("data-relationship-id") for element in relationships},
            {"system-to-routing", "system-to-overflow", "overflow-to-system-feedback"},
        )

    def test_browser_controls_ignore_focus_layers_and_accept_loop_seam_progress(self) -> None:
        plan = self.template_plan()
        plan["timeline"]["durationMs"] = 210
        for phase, (start_ms, end_ms) in zip(
            plan["timeline"]["phases"],
            ((0, 70), (70, 140), (140, 210)),
            strict=True,
        ):
            phase["startMs"] = start_ms
            phase["endMs"] = end_ms
        spec = self.write_plan("short-loop-plan.json", plan)
        output = self.workspace / "short-loop.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(spec),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        report_path = self.workspace / "short-loop-browser.json"
        screenshot_path = self.workspace / "short-loop.png"
        audited = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(AUDITOR),
                str(output),
                "--report",
                str(report_path),
                "--screenshot",
                str(screenshot_path),
                "--json",
            ],
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(audited.returncode, 0, msg=audited.stderr or audited.stdout)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIs(report.get("ok"), True)
        real_inputs = next(
            check for check in report["checks"] if check.get("id") == "real-input-controls"
        )
        details = real_inputs["details"]
        pointer = details["timeline"]
        playback = details["playback"]
        self.assertIs(pointer["pointerHit"]["insideTimelineRail"], True)
        self.assertAlmostEqual(pointer["pointerTimeMs"], 157.5, delta=6.3)
        self.assertGreater(playback["afterRevision"], playback["beforeRevision"])
        self.assertEqual(playback["pressedAfterPlay"], "true")
        self.assertLess(playback["after"], playback["before"])

    def test_long_header_copy_is_explicitly_truncated_and_accessible(self) -> None:
        plan = self.template_plan()
        module = plan["modules"][0]
        long_question = (
            "How does this deliberately long viewer question preserve every source word "
            "for assistive technology while fitting a stable public module shell, maintaining a readable "
            "overview, avoiding overlap with the explanatory claim, and retaining the exact original wording "
            "even when the available header width cannot display every phrase?"
        )
        long_claim = (
            "This deliberately long explanatory claim must never disappear silently when it exceeds "
            "the three visible header lines available above the deterministic module content body, "
            "and the complete source statement must remain accessible."
        )
        module["question"] = long_question
        module["claim"] = long_claim
        spec = self.write_plan("long-copy-plan.json", plan)
        output = self.workspace / "long-copy.svg"

        result = self.run_tool(
            COMPOSER,
            "--spec",
            str(spec),
            "--output",
            str(output.relative_to(self.workspace)),
            "--json",
        )
        report = self.parse_json_stdout(result)
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIs(report.get("ok"), True)

        root = ET.parse(output).getroot()
        module_element = next(element for element in root.iter() if element.get("data-module-id") == module["id"])
        question_element = next(element for element in module_element if element.get("class") == "module-question")
        claim_element = next(element for element in module_element if element.get("class") == "module-claim")
        self.assertTrue("".join(question_element.itertext()).endswith("…"))
        self.assertTrue("".join(claim_element.itertext()).endswith("…"))
        self.assertEqual(question_element.get("aria-label"), long_question)
        self.assertEqual(claim_element.get("aria-label"), long_claim)
        self.assertEqual(module_element.get("data-content-top"), "160")
        title = next(element for element in module_element if element.tag.endswith("title"))
        description = next(element for element in module_element if element.tag.endswith("desc"))
        self.assertEqual(title.text, long_claim)
        self.assertEqual(description.text, long_question)

    def test_composer_rejects_gauge_sweep_that_disagrees_with_semicircle(self) -> None:
        plan = self.template_plan()
        gauge = next(module for module in plan["modules"] if module["assetType"] == "radial-gauge")
        needle = next(binding for binding in gauge["bindings"] if binding["channel"] == "transform")
        needle["transform"]["range"] = [-120, 120]
        spec = self.write_plan("invalid-gauge-sweep.json", plan)
        output = self.workspace / "invalid-gauge.svg"

        result = self.run_tool(
            COMPOSER,
            "--spec",
            str(spec),
            "--output",
            str(output.relative_to(self.workspace)),
            "--json",
        )
        report = self.parse_json_stdout(result)
        self.assertEqual(result.returncode, 1)
        self.assertIs(report.get("ok"), False)
        self.assertIn("semicircle", str(report.get("error")).lower())
        self.assertIn("[-180, 0]", str(report.get("error")))
        self.assertFalse(output.exists())

    def test_percentage_point_gauges_and_progress_do_not_multiply_by_one_hundred_twice(self) -> None:
        brief = json.loads(BRIEF_TEMPLATE.read_text(encoding="utf-8"))
        brief["derived"].extend(
            [
                {
                    "id": "success-rate-percent",
                    "label": "First-pass success",
                    "unit": "percent",
                    "compute": {"op": "multiply", "args": [{"ref": "success-rate"}, 100]},
                },
                {
                    "id": "demand-capacity-percent",
                    "label": "Demand / capacity",
                    "unit": "percent",
                    "compute": {
                        "op": "multiply",
                        "args": [{"ref": "demand-capacity-ratio"}, 100],
                    },
                },
            ]
        )
        next(module for module in brief["modules"] if module["id"] == "quality-yield")[
            "values"
        ] = ["success-rate-percent"]
        next(module for module in brief["modules"] if module["id"] == "capacity-pressure")[
            "values"
        ] = ["demand-capacity-percent"]
        brief_path = self.write_plan("percentage-points-brief.json", brief)
        plan_path = self.workspace / "percentage-points-plan.json"
        output = self.workspace / "percentage-points.svg"

        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        # Force one real connector through a focus label. The cartographic plaque
        # must protect the rendered label while the audit records the occlusion.
        svg_text = output.read_text(encoding="utf-8")
        label_match = re.search(
            r'<text class="focus-region-label"[^>]*\sx="([-0-9.]+)"\sy="([-0-9.]+)"',
            svg_text,
        )
        self.assertIsNotNone(label_match)
        assert label_match is not None
        label_x, label_y = (float(value) for value in label_match.groups())
        crossing_path = (
            f'M{fmt_number(label_x - 16)} {fmt_number(label_y - 4)} '
            f'H{fmt_number(label_x + 320)}'
        )
        svg_text, replacement_count = re.subn(
            r'(<path id="relationship-[^"]+" class="relationship-path" d=")[^"]+(" )',
            rf'\g<1>{crossing_path}\g<2>',
            svg_text,
            count=1,
        )
        self.assertEqual(replacement_count, 1)
        output.write_text(svg_text, encoding="utf-8", newline="\n")

        root = ET.parse(output).getroot()
        visible_text = {
            " ".join((element.text or "").split())
            for element in root.iter()
            if isinstance(element.tag, str) and element.tag.endswith("text")
        }
        for expected in ("0%", "100%", "75% current", "150% max"):
            self.assertIn(expected, visible_text)
        self.assertNotIn("10000%", " ".join(visible_text))
        self.assertNotIn("7500%", " ".join(visible_text))
        runtime = next(element for element in root.iter() if element.tag.endswith("script")).text or ""
        self.assertIn('mark.dataset.valueUnit === "percent"', runtime)

        browser_report = self.workspace / "percentage-points-browser.json"
        browser_screenshot = self.workspace / "percentage-points.png"
        audited = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(AUDITOR),
                str(output),
                "--report",
                str(browser_report),
                "--screenshot",
                str(browser_screenshot),
                "--json",
            ],
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(audited.returncode, 0, msg=audited.stderr or audited.stdout)
        audit_payload = json.loads(browser_report.read_text(encoding="utf-8"))
        self.assertIs(audit_payload.get("ok"), True)
        progress_records = [
            record
            for check in audit_payload.get("checks", [])
            if check.get("id") == "initial-quantitative-semantics"
            for record in check.get("details", {}).get("progress", [])
        ]
        self.assertEqual(len(progress_records), 1)
        self.assertEqual(progress_records[0].get("unit"), "percent")
        self.assertAlmostEqual(progress_records[0].get("shownPercent"), 75)
        self.assertAlmostEqual(progress_records[0].get("expectedPercent"), 75)
        self.assertAlmostEqual(progress_records[0].get("expectedVisualRatio"), 0.75)
        self.assertAlmostEqual(progress_records[0].get("actualVisualRatio"), 0.75, delta=0.03)
        clearance = next(
            check
            for check in audit_payload.get("checks", [])
            if check.get("id") == "initial-relationship-clearance"
        )
        self.assertEqual(clearance.get("details", {}).get("maskIssues"), [])
        self.assertEqual(clearance.get("details", {}).get("issues"), [])
        self.assertGreater(clearance.get("details", {}).get("protectedCrossingCount", 0), 0)

    def test_dense_modules_and_cumulative_waterfall_pass_browser_isolation(self) -> None:
        brief = self.edge_brief()
        brief["derived"].extend(
            [
                {
                    "id": "edge-latency-with-hop",
                    "label": "Edge latency plus hop",
                    "unit": "milliseconds",
                    "compute": {"op": "add", "args": [{"ref": "edge-latency"}, 5]},
                },
                {
                    "id": "origin-latency-with-hop",
                    "label": "Origin latency plus hop",
                    "unit": "milliseconds",
                    "compute": {"op": "add", "args": [{"ref": "origin-latency"}, 5]},
                },
                {
                    "id": "blended-latency-with-hop",
                    "label": "Blended latency plus hop",
                    "unit": "milliseconds",
                    "compute": {"op": "add", "args": [{"ref": "blended-latency"}, 5]},
                },
                {
                    "id": "latency-ceiling",
                    "label": "Latency ceiling",
                    "unit": "milliseconds",
                    "compute": {
                        "op": "max",
                        "args": [{"ref": "edge-latency"}, {"ref": "origin-latency"}],
                    },
                },
            ]
        )
        modules = {module["id"]: module for module in brief["modules"]}
        modules["traffic-topology"]["values"] = [
            "request-rate",
            "edge-capacity",
            "cache-hit-rate",
            "edge-served-rate",
            "origin-rate",
            "overload",
            "blended-latency",
        ]
        modules["latency-consequence"]["values"] = [
            "edge-latency",
            "origin-latency",
            "blended-latency",
            "edge-latency-with-hop",
            "origin-latency-with-hop",
            "blended-latency-with-hop",
            "latency-ceiling",
        ]
        modules["edge-ledger"]["values"] = [
            "request-rate",
            "edge-capacity",
            "cache-hit-rate",
            "edge-latency",
            "origin-latency",
            "edge-served-rate",
            "origin-rate",
            "edge-load-ratio",
            "overload",
            "blended-latency",
        ]
        modules["load-response"].update(
            {
                "assetType": "waterfall-chart",
                "values": [
                    "request-rate",
                    "edge-served-rate",
                    "origin-rate",
                ],
            }
        )
        for source_id, module_id, question, claim in (
            (
                "load-ratio-bullet",
                "capacity-threshold-copy",
                "Which threshold provides a compact capacity cross-check?",
                "The copied threshold view preserves the same canonical load ratio.",
            ),
            (
                "service-mix",
                "service-reconciliation-copy",
                "How can the service split be reconciled in a second exact facet?",
                "The reconciliation facet retains the same edge and origin partition.",
            ),
        ):
            clone = json.loads(json.dumps(modules[source_id]))
            clone.update({"id": module_id, "question": question, "claim": claim})
            brief["modules"].append(clone)
        brief_path = self.write_plan("dense-waterfall-brief.json", brief)
        plan_path = self.workspace / "dense-waterfall-plan.json"
        output = self.workspace / "dense-waterfall.svg"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        compiled_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        compiled_modules = {module["id"]: module for module in compiled_plan["modules"]}
        self.assertEqual(len(compiled_modules), 9)
        self.assertLess(compiled_modules["latency-consequence"]["region"][3], 300)
        self.assertLess(compiled_modules["edge-ledger"]["region"][3], 300)
        self.assertLess(compiled_modules["traffic-topology"]["region"][3], 300)
        waterfall_bindings = compiled_modules["load-response"]["bindings"]
        waterfall_domains = {
            tuple(binding["transform"]["domain"]) for binding in waterfall_bindings
        }
        self.assertEqual(len(waterfall_domains), 1)
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        report_path = self.workspace / "dense-waterfall-browser.json"
        screenshot_path = self.workspace / "dense-waterfall.png"
        audited = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(AUDITOR),
                str(output),
                "--report",
                str(report_path),
                "--screenshot",
                str(screenshot_path),
                "--json",
            ],
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(audited.returncode, 0, msg=audited.stderr or audited.stdout)
        audit_payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIs(audit_payload.get("ok"), True)
        metrics = audit_payload.get("metrics", {})
        for metric in (
            "geometryEscapeCount",
            "textOverlapCount",
            "headerBodyOverlapCount",
            "invalidTextCount",
        ):
            self.assertEqual(metrics.get(metric), 0)
        self.assertGreater(metrics.get("negativeControlComparisons", 0), 0)
        initial_quantitative = next(
            check
            for check in audit_payload.get("checks", [])
            if check.get("id") == "initial-quantitative-semantics"
        )
        self.assertGreaterEqual(initial_quantitative.get("details", {}).get("stackCount", 0), 1)
        self.assertEqual(initial_quantitative.get("details", {}).get("issues"), [])
        real_inputs = next(
            check
            for check in audit_payload.get("checks", [])
            if check.get("id") == "real-input-controls"
        )
        control_records = real_inputs.get("details", {}).get("focusControls", [])
        expected_control_count = sum(
            len(module.get("focusGroups", [])) for module in compiled_plan["modules"]
        )
        self.assertEqual(len(control_records), expected_control_count)
        self.assertEqual(
            {
                record.get("focusId")
                for record in control_records
                if record.get("moduleId") == "request-flow"
            },
            {"routing-story", "pressure-story"},
        )

    def test_template_extremes_preserve_unclamped_progress_and_signed_gap(self) -> None:
        plan = self.template_plan()
        values = {item["id"]: float(item["default"]) for item in plan["concepts"]}
        values.update({"input-rate": 160, "capacity": 100, "success-rate": 0.8})
        pending = {item["id"]: item for item in plan["derived"]}
        while pending:
            progressed = False
            for value_id, item in list(pending.items()):
                if set(item["dependsOn"]) <= set(values):
                    values[value_id] = composer.scaffold.eval_node(item["compute"], values)
                    del pending[value_id]
                    progressed = True
            self.assertTrue(progressed, msg=f"unresolved derived values: {sorted(pending)}")

        self.assertAlmostEqual(values["processed-rate"], 100)
        self.assertAlmostEqual(values["completed-rate"], 80)
        self.assertAlmostEqual(values["first-pass-failure-rate"], 20)
        self.assertAlmostEqual(values["demand-capacity-ratio"], 1.6)
        self.assertAlmostEqual(values["capacity-gap"], -60)
        self.assertAlmostEqual(values["unserved-rate"], 60)

    def test_subunit_waterfall_steps_keep_one_exact_pixel_scale(self) -> None:
        plan = self.template_plan()
        capacity = next(item for item in plan["concepts"] if item["id"] == "capacity")
        capacity["domain"] = [0.1, capacity["domain"][1]]
        initial = next(
            scenario
            for scenario in plan["scenarios"]
            if scenario["id"] == plan["initialScenario"]
        )
        initial["values"].update({"input-rate": 0.6, "capacity": 0.2})
        plan_path = self.write_plan("subunit-waterfall-plan.json", plan)
        output = self.workspace / "subunit-waterfall.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        root = ET.parse(output).getroot()
        items = [
            element
            for element in root.iter()
            if element.get("data-sync-layout-item") == "waterfall"
        ]
        ratios: list[float] = []
        for item in items:
            mark = next(child for child in item if child.get("data-bind") is not None)
            raw = abs(float(mark.get("data-current-value", "nan")))
            if raw <= 1e-9:
                continue
            rendered_extent = float(mark.get("height", "nan"))
            scale_match = re.search(r"scale\(1\s+(-?[0-9.]+)\)", item.get("transform", ""))
            self.assertIsNotNone(scale_match)
            assert scale_match is not None
            ratios.append(abs(rendered_extent * float(scale_match.group(1))) / raw)
        self.assertGreaterEqual(len(ratios), 3)
        self.assertLess(max(ratios) - min(ratios), 1e-7)

    def test_large_magnitude_waterfall_survives_legal_browser_perturbations(self) -> None:
        brief = json.loads(BRIEF_TEMPLATE.read_text(encoding="utf-8"))
        factor = 10_000
        scaled_ids = {"input-rate", "capacity"}
        for concept in brief["concepts"]:
            if concept["id"] not in scaled_ids:
                continue
            concept["default"] *= factor
            concept["domain"] = [value * factor for value in concept["domain"]]
        for scenario in brief["scenarios"]:
            for value_id in scaled_ids:
                scenario["values"][value_id] *= factor
        for phase in brief["timeline"]["phases"]:
            for value_id in scaled_ids:
                phase["values"][value_id] *= factor

        brief_path = self.write_plan("large-waterfall-brief.json", brief)
        plan_path = self.workspace / "large-waterfall-plan.json"
        output = self.workspace / "large-waterfall.svg"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        waterfall = next(
            element
            for element in ET.parse(output).getroot().iter()
            if element.get("data-sync-layout") == "waterfall"
        )
        serialized_scale = float(waterfall.get("data-layout-scale", "nan"))
        max_visual_value = float(waterfall.get("data-layout-max-value", "nan"))
        self.assertGreater(serialized_scale, 0)
        self.assertLess(serialized_scale, 0.001)
        self.assertGreaterEqual(max_visual_value, 1_200_000)

        report_path = self.workspace / "large-waterfall-browser.json"
        screenshot_path = self.workspace / "large-waterfall.png"
        audited = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(AUDITOR),
                str(output),
                "--report",
                str(report_path),
                "--screenshot",
                str(screenshot_path),
                "--compact-report",
                "--json",
            ],
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(audited.returncode, 0, msg=audited.stderr or audited.stdout)
        audit_payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIs(audit_payload.get("ok"), True)
        self.assertEqual(audit_payload.get("metrics", {}).get("quantitativeSemanticsIssueCount"), 0)

    def test_exact_zero_flows_render_without_thickness_or_deficit_cues(self) -> None:
        plan = self.template_plan()
        initial_id = plan["initialScenario"]
        initial = next(item for item in plan["scenarios"] if item["id"] == initial_id)
        initial["values"]["input-rate"] = -0.0
        spec = self.write_plan("zero-flow-plan.json", plan)
        output = self.workspace / "zero-flow.svg"

        result = self.run_tool(
            COMPOSER,
            "--spec",
            str(spec),
            "--output",
            str(output.relative_to(self.workspace)),
            "--json",
        )
        report = self.parse_json_stdout(result)
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIs(report.get("ok"), True)

        root = ET.parse(output).getroot()
        flow_items = {
            element.get("data-layout-bound-role"): element
            for element in root.iter()
            if element.get("data-sync-layout-item") == "flow"
        }
        for role in ("completed-rate-width", "first-pass-failure-rate-width", "unserved-rate-width"):
            item = flow_items[role]
            self.assertEqual(item.get("data-flow-direction"), "zero")
            path = next(
                child for child in item
                if child.get("data-sync-flow-path") is not None
            )
            self.assertEqual(float(path.get("stroke-width", "nan")), 0.0)
            self.assertIsNone(path.get("stroke-dasharray"))
            self.assertIsNone(path.get("marker-end"))
            mark = next(element for element in item.iter() if element.get("data-bind") is not None)
            self.assertEqual(mark.get("data-current-value"), "0")
            self.assertNotIn("-0", mark.get("data-accessible-value", ""))

    def test_tiny_nonzero_flows_preserve_canonical_sign_and_static_fallback(self) -> None:
        brief_path = self.write_plan("tiny-flow-brief.json", self.tiny_edge_brief())
        plan_path = self.workspace / "tiny-flow-plan.json"
        output = self.workspace / "tiny-flow.svg"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        root = ET.parse(output).getroot()
        flow_items = [
            element
            for element in root.iter()
            if element.get("data-sync-layout-item") == "flow"
        ]
        self.assertGreaterEqual(len(flow_items), 2)
        for item in flow_items:
            mark = next(
                element
                for element in item.iter()
                if element.get("data-bind") is not None
            )
            raw_text = mark.get("data-current-value", "")
            self.assertNotEqual(raw_text, "0")
            self.assertGreater(float(raw_text), 0.0)
            self.assertIn("E-", mark.get("data-accessible-value", ""))
            self.assertEqual(item.get("data-flow-direction"), "forward")
            path = next(
                child for child in item
                if child.get("data-sync-flow-path") is not None
            )
            self.assertGreaterEqual(float(path.get("stroke-width", "nan")), 2.5)
            self.assertIsNone(path.get("stroke-dasharray"))
            self.assertIsNone(path.get("marker-end"))

    def test_tiny_nonconserving_flow_is_rejected_at_its_own_scale(self) -> None:
        brief = self.tiny_edge_brief()
        origin = next(item for item in brief["derived"] if item["id"] == "origin-rate")
        origin["compute"] = 0
        brief_path = self.write_plan("tiny-nonconserving-brief.json", brief)
        plan_path = self.workspace / "tiny-nonconserving-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 1)
        report = self.parse_json_stdout(compiled)
        self.assertIn("does not conserve", str(report.get("error")))
        self.assertFalse(plan_path.exists())

    def test_tiny_negative_flow_preserves_reverse_deficit_cues(self) -> None:
        brief = self.tiny_edge_brief()
        service_mix = next(item for item in brief["modules"] if item["id"] == "service-mix")
        service_mix["assetType"] = "comparison-table"
        service_mix.pop("stackTotal", None)
        edge_served = next(item for item in brief["derived"] if item["id"] == "edge-served-rate")
        origin = next(item for item in brief["derived"] if item["id"] == "origin-rate")
        origin["compute"] = {
            "op": "multiply",
            "args": [{"ref": "request-rate"}, -0.5],
        }
        edge_served["compute"] = {
            "op": "subtract",
            "args": [{"ref": "request-rate"}, {"ref": "origin-rate"}],
        }
        brief_path = self.write_plan("tiny-negative-flow-brief.json", brief)
        plan_path = self.workspace / "tiny-negative-flow-plan.json"
        output = self.workspace / "tiny-negative-flow.svg"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        root = ET.parse(output).getroot()
        item = next(
            element
            for element in root.iter()
            if element.get("data-sync-layout-item") == "flow"
            and str(element.get("data-layout-bound-role", "")).startswith("origin-rate-")
        )
        role = item.get("data-layout-bound-role")
        mark = next(child for child in root.iter() if child.get("data-role") == role)
        self.assertLess(float(mark.get("data-current-value", "nan")), 0.0)
        self.assertIn("-", mark.get("data-accessible-value", ""))
        self.assertEqual(item.get("data-flow-direction"), "reverse")
        path = next(child for child in item if child.get("data-sync-flow-path") is not None)
        self.assertGreaterEqual(float(path.get("stroke-width", "nan")), 2.5)
        self.assertEqual(path.get("stroke-dasharray"), "7 5")
        self.assertIsNotNone(path.get("marker-end"))
        sign_label = next(child for child in item if child.get("data-flow-sign-label") == "true")
        self.assertEqual((sign_label.text or "").strip(), "DEFICIT")

    def test_tiny_runtime_formatting_and_nonrepresentable_zero_diagnostic(self) -> None:
        brief = self.tiny_edge_brief()
        brief["concepts"].extend(
            [
                {
                    "id": "root-control",
                    "label": "Root control",
                    "unit": "score",
                    "default": 1,
                    "domain": [1, 2],
                },
                {
                    "id": "root-total",
                    "label": "Root total",
                    "unit": "score",
                    "default": 10,
                    "domain": [9, 11],
                },
            ]
        )
        brief["derived"].extend(
            [
                {
                    "id": "irrational-flow",
                    "label": "Irrational-root flow",
                    "unit": "score",
                    "compute": {
                        "op": "subtract",
                        "args": [
                            {
                                "op": "multiply",
                                "args": [{"ref": "root-control"}, {"ref": "root-control"}],
                            },
                            2,
                        ],
                    },
                },
                {
                    "id": "irrational-remainder",
                    "label": "Irrational remainder",
                    "unit": "score",
                    "compute": {
                        "op": "subtract",
                        "args": [{"ref": "root-total"}, {"ref": "irrational-flow"}],
                    },
                },
            ]
        )
        for scenario in brief["scenarios"]:
            scenario["values"]["root-control"] = 1 if scenario["id"] == "baseline" else 2
            scenario["values"]["root-total"] = 10
        brief["modules"].append(
            {
                "id": "irrational-root-flow",
                "question": "Can the floating-point control land on the mathematical square root boundary?",
                "claim": "Adjacent representable controls straddle the root without producing canonical zero.",
                "assetType": "sankey-diagram",
                "selectionRationale": "A signed flow exposes both sides of the nonrepresentable zero boundary.",
                "rejectedAlternative": "A table would not expose the change in flow direction.",
                "values": ["root-total", "irrational-flow", "irrational-remainder"],
            }
        )
        brief_path = self.write_plan("tiny-runtime-brief.json", brief)
        plan_path = self.workspace / "tiny-runtime-plan.json"
        output = self.workspace / "tiny-runtime.svg"
        report_path = self.workspace / "tiny-runtime-browser.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        audited = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(AUDITOR),
                str(output),
                "--report",
                str(report_path),
                "--json",
            ],
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(audited.returncode, 0, msg=audited.stderr or audited.stdout)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        check = next(
            item for item in report["checks"]
            if item.get("id") == "initial-quantitative-semantics"
        )
        accessibility = check["details"]["accessibility"]
        observed = {
            value_id: {item["accessibleValue"] for item in accessibility if item["valueId"] == value_id}
            for value_id in ("tiny-cost", "tiny-probability", "edge-served-rate")
        }
        self.assertEqual(observed["tiny-cost"], {"-INR\u00a08E-10 per year"})
        self.assertEqual(observed["tiny-probability"], {"8E-8%"})
        self.assertEqual(observed["edge-served-rate"], {"4.32E-10 requests/second"})
        diagnostics = report["snapshots"]["zeroFlowDiagnostics"]
        self.assertEqual(diagnostics["irrational-flow"]["reason"], "noExactRepresentableRoot")

    def test_zero_flow_audit_finds_two_interior_roots_with_equal_endpoint_signs(self) -> None:
        brief = self.edge_brief()
        brief["concepts"].append(
            {
                "id": "flow-control",
                "label": "Flow control",
                "unit": "score",
                "default": 0,
                "domain": [0, 1],
            }
        )
        brief["derived"].extend(
            [
                {
                    "id": "flow-offset-one",
                    "label": "Flow offset one",
                    "unit": "requests/second",
                    "compute": {
                        "op": "subtract",
                        "args": [{"ref": "flow-control"}, 0.5001],
                    },
                },
                {
                    "id": "flow-offset-two",
                    "label": "Flow offset two",
                    "unit": "requests/second",
                    "compute": {
                        "op": "subtract",
                        "args": [{"ref": "flow-control"}, 0.5002],
                    },
                },
                {
                    "id": "interior-zero-flow",
                    "label": "Interior zero flow",
                    "unit": "requests/second",
                    "compute": {
                        "op": "multiply",
                        "args": [
                            {"ref": "flow-offset-one"},
                            {"ref": "flow-offset-two"},
                        ],
                    },
                },
                {
                    "id": "flow-remainder",
                    "label": "Flow remainder",
                    "unit": "requests/second",
                    "compute": {
                        "op": "subtract",
                        "args": [
                            {"ref": "request-rate"},
                            {"ref": "interior-zero-flow"},
                        ],
                    },
                },
            ]
        )
        for scenario in brief["scenarios"]:
            scenario["values"]["flow-control"] = 0 if scenario["id"] == "baseline" else 1
        flow = next(module for module in brief["modules"] if module["id"] == "request-flow")
        flow["values"] = ["request-rate", "interior-zero-flow", "flow-remainder"]
        brief_path = self.write_plan("interior-zero-flow-brief.json", brief)
        plan_path = self.workspace / "interior-zero-flow-plan.json"
        svg = self.workspace / "interior-zero-flow.svg"

        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(svg),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        report_path = self.workspace / "interior-zero-flow-browser.json"
        audited = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(AUDITOR),
                str(svg),
                "--report",
                str(report_path),
                "--json",
            ],
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(audited.returncode, 0, msg=audited.stderr or audited.stdout)
        audit_payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIs(audit_payload.get("ok"), True)
        self.assertIn("interior-zero-flow", audit_payload.get("snapshots", {}).get("zeroFlows", {}))

    def test_final_promotion_retries_transient_access_denied(self) -> None:
        source = self.workspace / "promotion-source.svg"
        destination = self.workspace / "promotion-final.svg"
        source.write_bytes(b"stable-payload")
        calls: list[int] = []
        delays: list[float] = []

        def flaky_replace(source_path: Path, destination_path: Path) -> None:
            calls.append(len(calls) + 1)
            if len(calls) < 3:
                raise PermissionError(13, "transient access denied")
            os.replace(source_path, destination_path)

        composer.replace_with_retry(
            source,
            destination,
            attempts=4,
            initial_delay=0,
            replace_func=flaky_replace,
            sleep_func=delays.append,
        )
        self.assertEqual(calls, [1, 2, 3])
        self.assertEqual(delays, [0, 0])
        self.assertFalse(source.exists())
        self.assertEqual(destination.read_bytes(), b"stable-payload")

    def test_validator_rejects_scaffold_placeholders_by_default(self) -> None:
        svg = self.workspace / "default-placeholder-rejection.svg"
        self.scaffold_template(svg)

        result, report = self.validate_json(svg)
        self.assertEqual(result.returncode, 1)
        self.assertIs(report.get("ok"), False)
        failures = report.get("failures")
        self.assertIsInstance(failures, list)
        self.assertTrue(any("placeholder" in str(item).lower() for item in failures))

    def test_validator_distinguishes_javascript_comments_from_remote_dependencies(self) -> None:
        output = self.workspace / "commented-runtime.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(output.relative_to(self.workspace)),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        valid_result, valid_report = self.validate_json(output, "--require-time-sync")
        self.assertEqual(valid_result.returncode, 0, msg=valid_result.stderr or valid_result.stdout)
        self.assertIs(valid_report.get("ok"), True)

        remote = self.workspace / "remote-runtime.svg"
        remote.write_text(
            output.read_text(encoding="utf-8").replace(
                "// Keep the bound height",
                'fetch("https://example.com/data"); // Keep the bound height',
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        remote_result, remote_report = self.validate_json(remote, "--require-time-sync")
        self.assertEqual(remote_result.returncode, 1)
        self.assertIn(
            "external or network dependencies",
            "\n".join(str(item) for item in remote_report.get("failures", [])),
        )

    def test_validator_rejects_nonfinite_relationship_ports_and_corrupted_route_metadata(self) -> None:
        output = self.workspace / "relationship-contract.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(output.relative_to(self.workspace)),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        source = output.read_text(encoding="utf-8")
        relationship_paths = list(
            re.finditer(
                r'<path id="relationship-[^"]+" class="relationship-path" d="([^"]+)"',
                source,
            )
        )
        self.assertGreaterEqual(len(relationship_paths), 2)
        second_span = relationship_paths[1].span(1)
        overlapping_routes = (
            source[: second_span[0]]
            + relationship_paths[0].group(1)
            + source[second_span[1] :]
        )
        mutations = {
            "nonfinite-port": (
                re.sub(r'data-source-port="[^"]+"', 'data-source-port="nan"', source, count=1),
                "port must be finite",
            ),
            "noncanonical-lane": (
                source.replace('data-route-lane="0"', 'data-route-lane="0.0"', 1),
                "canonical deterministic route lane",
            ),
            "unstable-marker": (
                source.replace('markerUnits="userSpaceOnUse"', 'markerUnits="strokeWidth"', 1),
                "userSpaceOnUse",
            ),
            "false-key-label": (
                re.sub(
                    r'data-relationship-key-label="[^"]+"',
                    'data-relationship-key-label="Wrong relationship"',
                    source,
                    count=1,
                ),
                "key",
            ),
            "overlapping-routes": (
                overlapping_routes,
                "relationship routes overlap",
            ),
        }
        for mutation_id, (payload, expected) in mutations.items():
            with self.subTest(mutation=mutation_id):
                mutated = self.workspace / f"{mutation_id}.svg"
                mutated.write_text(payload, encoding="utf-8", newline="\n")
                result, report = self.validate_json(mutated, "--require-time-sync")
                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    expected,
                    "\n".join(str(item) for item in report.get("failures", [])),
                )

    def test_relationship_router_allocates_unique_lanes_beyond_three_routes(self) -> None:
        plan = self.template_plan()
        top = ["operating-system", "quality-yield", "capacity-pressure"]
        bottom = ["work-routing", "operating-ledger", "capacity-overflow-bridge"]
        endpoints = [
            (top[0], bottom[0]),
            (top[0], bottom[2]),
            (top[1], bottom[0]),
            (top[2], bottom[0]),
            (top[1], bottom[2]),
            (top[2], bottom[1]),
            (top[0], bottom[1]),
            (bottom[0], bottom[2]),
        ]
        plan["relationships"] = [
            {
                "id": f"dense-route-{index}",
                "source": source,
                "target": target,
                "kind": "dependency",
                "label": f"Dense route {index} retains its own deterministic lane",
            }
            for index, (source, target) in enumerate(endpoints)
        ]
        plan_path = self.write_plan("dense-route-plan.json", plan)
        output = self.workspace / "dense-route.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        relationship_paths: dict[str, str] = {}
        route_lanes: set[str] = set()
        for group in ET.parse(output).getroot().iter():
            relationship_id = group.get("data-relationship-id")
            if relationship_id is None:
                continue
            route_lanes.add(group.get("data-route-lane", ""))
            path = next(
                child
                for child in group
                if "relationship-path" in child.get("class", "").split()
            )
            relationship_paths[relationship_id] = path.get("d", "")
        self.assertEqual(len(relationship_paths), 8)
        self.assertEqual(route_lanes, {str(index) for index in range(8)})

        def first_horizontal_lane(path: str) -> float:
            match = re.search(r"V([-+0-9.eE]+) H", path)
            self.assertIsNotNone(match, msg=path)
            assert match is not None
            return float(match.group(1))

        self.assertNotEqual(
            first_horizontal_lane(relationship_paths["dense-route-1"]),
            first_horizontal_lane(relationship_paths["dense-route-4"]),
        )
        self.assertNotEqual(
            first_horizontal_lane(relationship_paths["dense-route-3"]),
            first_horizontal_lane(relationship_paths["dense-route-6"]),
        )
        self.assertLess(
            first_horizontal_lane(relationship_paths["dense-route-7"]),
            float(plan["modules"][3]["region"][1]),
        )
        validated, report = self.validate_json(output, "--require-time-sync")
        self.assertEqual(validated.returncode, 0, msg=validated.stderr or validated.stdout)
        self.assertIs(report.get("ok"), True)
        self.assertEqual(report.get("metrics", {}).get("relationshipCount"), 8)

    def test_relationship_ports_keep_physical_clearance_and_feedback_lanes_stay_unique(self) -> None:
        plan = self.template_plan()
        source, target, alternate = "operating-system", "quality-yield", "capacity-pressure"
        feedback_endpoints = [
            (source, target),
            (source, alternate),
            (target, source),
            (alternate, source),
        ]
        plan["relationships"] = [
            *[
                {
                    "id": f"feedback-parallel-{index}",
                    "source": relationship_source,
                    "target": relationship_target,
                    "kind": "feedback",
                    "label": f"Feedback lane {index}",
                }
                for index, (relationship_source, relationship_target) in enumerate(feedback_endpoints)
            ],
            {
                "id": "dependency-parallel-0",
                "source": source,
                "target": target,
                "kind": "dependency",
                "label": "Dependency lane 0",
            },
            {
                "id": "dependency-parallel-1",
                "source": source,
                "target": target,
                "kind": "flow",
                "label": "Flow lane 1",
            },
        ]
        plan_path = self.write_plan("parallel-route-plan.json", plan)
        output = self.workspace / "parallel-route.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(output),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        paths: dict[str, str] = {}
        for group in ET.parse(output).getroot().iter():
            relationship_id = group.get("data-relationship-id")
            if relationship_id is None:
                continue
            path = next(
                child
                for child in group
                if "relationship-path" in child.get("class", "").split()
            )
            paths[relationship_id] = path.get("d", "")

        feedback_lanes = []
        for index in range(4):
            path = paths[f"feedback-parallel-{index}"]
            match = re.search(r" V([-+0-9.eE]+) H", path)
            self.assertIsNotNone(match, msg=path)
            assert match is not None
            feedback_lanes.append(float(match.group(1)))
        self.assertEqual(len(set(feedback_lanes)), len(feedback_lanes))

        dependency_source_ports = []
        for index in range(2):
            path = paths[f"dependency-parallel-{index}"]
            match = re.match(r"M[-+0-9.eE]+ ([-+0-9.eE]+) H", path)
            self.assertIsNotNone(match, msg=path)
            assert match is not None
            dependency_source_ports.append(float(match.group(1)))
        self.assertTrue(
            all(
                abs(first - second) >= 15.0
                for index, first in enumerate(dependency_source_ports)
                for second in dependency_source_ports[index + 1 :]
            )
        )

        validated, report = self.validate_json(output, "--require-time-sync")
        self.assertEqual(validated.returncode, 0, msg=validated.stderr or validated.stdout)
        self.assertIs(report.get("ok"), True)

    def test_scaffold_rejects_malformed_json_without_output(self) -> None:
        malformed = self.workspace / "malformed.json"
        malformed.write_text('{"version": 1,', encoding="utf-8")
        output = self.workspace / "must-not-exist.svg"

        result = self.run_tool(
            SCAFFOLD,
            "--spec",
            str(malformed),
            "--output",
            str(output),
            "--json",
        )
        report = self.parse_json_stdout(result)
        self.assertEqual(result.returncode, 1)
        self.assertIs(report.get("ok"), False)
        self.assertIn("not valid JSON", str(report.get("error")))
        self.assertFalse(output.exists())

    def test_scaffold_rejects_cycles_and_unknown_bindings(self) -> None:
        cycle_plan = self.template_plan()
        derived = cycle_plan["derived"]
        assert isinstance(derived, list) and isinstance(derived[0], dict)
        derived[0]["dependsOn"] = ["completed-rate"]
        derived[0]["compute"] = {"ref": "completed-rate"}

        unknown_plan = self.template_plan()
        modules = unknown_plan["modules"]
        assert isinstance(modules, list) and isinstance(modules[0], dict)
        bindings = modules[0]["bindings"]
        assert isinstance(bindings, list) and isinstance(bindings[0], dict)
        bindings[0]["value"] = "unknown-source-value"

        cases = (
            ("cycle", cycle_plan, "cycle"),
            ("unknown-binding", unknown_plan, "unknown value"),
        )
        for name, plan, expected_error in cases:
            with self.subTest(name=name):
                spec = self.write_plan(f"{name}.json", plan)
                output = self.workspace / f"{name}.svg"
                result = self.run_tool(
                    SCAFFOLD,
                    "--spec",
                    str(spec),
                    "--output",
                    str(output),
                    "--json",
                )
                report = self.parse_json_stdout(result)
                self.assertEqual(result.returncode, 1)
                self.assertIs(report.get("ok"), False)
                self.assertIn(expected_error, str(report.get("error")).lower())
                self.assertFalse(output.exists())

    def test_scaffold_rejects_missing_module_decision_fields(self) -> None:
        for field in ("selectionRationale", "rejectedAlternative"):
            with self.subTest(field=field):
                plan = self.template_plan()
                modules = plan["modules"]
                assert isinstance(modules, list) and isinstance(modules[0], dict)
                del modules[0][field]
                spec = self.write_plan(f"missing-{field}.json", plan)
                output = self.workspace / f"missing-{field}.svg"
                fragments = self.workspace / f"missing-{field}-fragments"

                result = self.run_tool(
                    SCAFFOLD,
                    "--spec",
                    str(spec),
                    "--output",
                    str(output),
                    "--fragments-dir",
                    str(fragments),
                    "--json",
                )
                report = self.parse_json_stdout(result)
                self.assertEqual(result.returncode, 1)
                self.assertIs(report.get("ok"), False)
                self.assertIn(field.lower(), str(report.get("error")).lower())
                self.assertFalse(output.exists())
                self.assertFalse(fragments.exists())

    def test_scaffold_rejects_missing_visible_provenance(self) -> None:
        plan = self.template_plan()
        del plan["provenance"]
        spec = self.write_plan("missing-provenance.json", plan)
        output = self.workspace / "missing-provenance.svg"

        result = self.run_tool(
            SCAFFOLD,
            "--spec",
            str(spec),
            "--output",
            str(output),
            "--json",
        )
        report = self.parse_json_stdout(result)
        self.assertEqual(result.returncode, 1)
        self.assertIs(report.get("ok"), False)
        self.assertIn("provenance", str(report.get("error")).lower())
        self.assertFalse(output.exists())

    def test_scaffold_fragments_have_exact_names_and_stable_markers(self) -> None:
        output = self.workspace / "authoring" / "scaffold.svg"
        fragments = self.workspace / "authoring" / "fragments"
        result = self.run_tool(
            SCAFFOLD,
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(output.relative_to(self.workspace)),
            "--fragments-dir",
            str(fragments.relative_to(self.workspace)),
            "--json",
        )
        report = self.parse_json_stdout(result)
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIs(report.get("ok"), True)

        plan = self.template_plan()
        modules = plan["modules"]
        assert isinstance(modules, list)
        module_ids = [str(module["id"]) for module in modules if isinstance(module, dict)]
        expected_names = sorted(f"{module_id}.svg" for module_id in module_ids)
        self.assertEqual(sorted(path.name for path in fragments.iterdir()), expected_names)
        self.assertEqual(Path(str(report["fragmentsDirectory"])), fragments.resolve())
        self.assertEqual(report.get("fragmentCount"), len(module_ids))

        svg = output.read_bytes()
        svg_root = ET.fromstring(svg)
        source_modules = {
            element.get("data-module-id"): element
            for element in svg_root.iter()
            if element.get("data-module-id") is not None
        }
        planned_modules = {
            str(module["id"]): module for module in modules if isinstance(module, dict)
        }
        for module_id in module_ids:
            start = f"<!-- sync-content-start:{module_id} -->".encode()
            end = f"<!-- sync-content-end:{module_id} -->".encode()
            self.assertEqual(svg.count(start), 1)
            self.assertEqual(svg.count(end), 1)
            self.assertLess(svg.index(start), svg.index(end))

            fragment = fragments / f"{module_id}.svg"
            raw_fragment = fragment.read_bytes()
            self.assertTrue(raw_fragment.startswith(b'<?xml version="1.0" encoding="UTF-8"?>'))
            fragment_root = ET.fromstring(raw_fragment)
            self.assertEqual(fragment_root.tag.rsplit("}", 1)[-1], "g")
            self.assertEqual(fragment_root.get("class"), "module-content")
            self.assertEqual(fragment_root.get("data-module-content-for"), module_id)
            self.assertEqual(fragment_root.get("data-placeholder"), "true")

            source_module = source_modules[module_id]
            content_top = source_module.get("data-content-top")
            self.assertIsNotNone(content_top)
            assert content_top is not None
            region = planned_modules[module_id]["region"]
            assert isinstance(region, list)
            content_width = fmt_number(region[2])
            content_height = fmt_number(float(region[3]) - float(content_top))
            expected_transform = f"translate(0 {content_top})"
            self.assertEqual(fragment_root.get("transform"), expected_transform)
            self.assertEqual(fragment_root.get("data-content-origin"), f"0 {content_top}")
            self.assertEqual(fragment_root.get("data-content-width"), content_width)
            self.assertEqual(fragment_root.get("data-content-height"), content_height)

            source_content = [
                child
                for child in source_module
                if isinstance(child.tag, str) and child.get("data-module-content-for") == module_id
            ]
            self.assertEqual(len(source_content), 1)
            self.assertEqual(source_content[0].get("class"), "module-content module-placeholder")
            self.assertEqual(source_content[0].get("transform"), expected_transform)
            self.assertEqual(source_content[0].get("data-content-origin"), f"0 {content_top}")
            self.assertEqual(source_content[0].get("data-content-width"), content_width)
            self.assertEqual(source_content[0].get("data-content-height"), content_height)

            if module_id == "compensation-mix":
                fragment_positions = [
                    element.get("y")
                    for element in fragment_root.iter()
                    if element.get("data-role") is not None
                ]
                source_positions = [
                    element.get("y")
                    for element in source_content[0].iter()
                    if element.get("data-role") is not None
                ]
                self.assertEqual(fragment_positions, ["10", "40", "70", "114"])
                self.assertEqual(source_positions, fragment_positions)

    def test_single_module_replacement_is_atomic_and_byte_preserving(self) -> None:
        output = self.workspace / "authoring" / "scaffold.svg"
        fragments = self.workspace / "authoring" / "fragments"
        scaffold_result = self.run_tool(
            SCAFFOLD,
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(output.relative_to(self.workspace)),
            "--fragments-dir",
            str(fragments.relative_to(self.workspace)),
            "--json",
        )
        scaffold_report = self.parse_json_stdout(scaffold_result)
        self.assertEqual(scaffold_result.returncode, 0, msg=scaffold_result.stderr or scaffold_result.stdout)
        self.assertIs(scaffold_report.get("ok"), True)

        plan = self.template_plan()
        modules = plan["modules"]
        assert isinstance(modules, list) and modules and isinstance(modules[0], dict)
        module_ids = [str(module["id"]) for module in modules if isinstance(module, dict)]
        target_module = modules[0]
        target_id = str(target_module["id"])
        generated_fragment = fragments / f"{target_id}.svg"
        original = output.read_bytes()

        rejected = self.run_tool(
            REPLACER,
            str(output),
            str(generated_fragment),
            "--module",
            target_id,
            "--in-place",
        )
        rejected_report = self.parse_json_stdout(rejected)
        self.assertEqual(rejected.returncode, 1)
        self.assertIs(rejected_report.get("ok"), False)
        self.assertIn("data-placeholder", str(rejected_report.get("error")))
        self.assertEqual(output.read_bytes(), original)

        fragment_text = generated_fragment.read_text(encoding="utf-8")
        self.assertEqual(fragment_text.count('data-placeholder="true"'), 2)
        authored_text = fragment_text.replace('data-placeholder="true"', "", 1)
        authored_text = authored_text.replace("Editable content fragment", "Authored regression content", 1)
        authored_text = authored_text.replace("placeholder-mark", "authored-mark")
        authored_text = authored_text.replace("placeholder-value", "authored-value")
        authored_text = authored_text.replace(
            '<!-- Remove data-placeholder="true" from this root only after the visual is complete. -->',
            "<!-- Contract-preserving authored fragment. -->",
            1,
        )
        self.assertNotEqual(authored_text, fragment_text)
        authored_fragment = self.workspace / "authoring" / f"{target_id}-authored.svg"
        authored_fragment.write_text(authored_text, encoding="utf-8", newline="\n")
        authored_root = ET.parse(authored_fragment).getroot()
        self.assertIsNone(authored_root.get("data-placeholder"))

        updated = self.workspace / "authoring" / "updated.svg"
        replaced = self.run_tool(
            REPLACER,
            str(output),
            str(authored_fragment),
            "--module",
            target_id,
            "--output",
            str(updated.relative_to(self.workspace)),
        )
        replaced_report = self.parse_json_stdout(replaced)
        self.assertEqual(replaced.returncode, 0, msg=replaced.stderr or replaced.stdout)
        self.assertIs(replaced_report.get("ok"), True)
        self.assertEqual(Path(str(replaced_report["output"])), updated.resolve())
        bindings = target_module["bindings"]
        assert isinstance(bindings, list)
        self.assertEqual(replaced_report.get("bindingCount"), len(bindings))
        self.assertEqual(output.read_bytes(), original)

        fragment_bytes = authored_fragment.read_bytes()
        declaration = re.match(
            rb"^[ \t\r\n]*<\?xml[ \t\r\n]+[^?]*\?>[ \t\r\n]*",
            fragment_bytes,
            re.IGNORECASE,
        )
        self.assertIsNotNone(declaration)
        assert declaration is not None
        inserted = fragment_bytes[declaration.end() :]
        start_marker = f"<!-- sync-content-start:{target_id} -->".encode()
        end_marker = f"<!-- sync-content-end:{target_id} -->".encode()
        start_end = original.index(start_marker) + len(start_marker)
        end_start = original.index(end_marker)
        expected = original[:start_end] + inserted + original[end_start:]
        module_tag = re.search(
            rb'<g\b(?=[^>]*data-module-id="' + re.escape(target_id.encode()) + rb'")[^>]*>',
            expected,
        )
        self.assertIsNotNone(module_tag)
        assert module_tag is not None
        placeholder = re.search(
            rb"[ \t\r\n]+data-placeholder[ \t\r\n]*=[ \t\r\n]*([\"'])true\1",
            module_tag.group(),
        )
        self.assertIsNotNone(placeholder)
        assert placeholder is not None
        placeholder_start = module_tag.start() + placeholder.start()
        placeholder_end = module_tag.start() + placeholder.end()
        expected = expected[:placeholder_start] + expected[placeholder_end:]
        self.assertEqual(updated.read_bytes(), expected)

        updated_root = ET.parse(updated).getroot()
        updated_modules = {
            element.get("data-module-id"): element
            for element in updated_root.iter()
            if element.get("data-module-id") is not None
        }
        self.assertEqual(set(updated_modules), set(module_ids))
        for module_id in module_ids:
            if module_id == target_id:
                self.assertIsNone(updated_modules[module_id].get("data-placeholder"))
            else:
                self.assertEqual(updated_modules[module_id].get("data-placeholder"), "true")
        inserted_shells = [
            element
            for element in updated_modules[target_id]
            if isinstance(element.tag, str) and element.get("data-module-content-for") == target_id
        ]
        self.assertEqual(len(inserted_shells), 1)
        for attribute in (
            "class",
            "transform",
            "data-module-content-for",
            "data-content-origin",
            "data-content-width",
            "data-content-height",
        ):
            self.assertEqual(inserted_shells[0].get(attribute), authored_root.get(attribute))

        updated_bytes = updated.read_bytes()
        for module_id in module_ids:
            for kind in ("start", "end"):
                marker = f"<!-- sync-content-{kind}:{module_id} -->".encode()
                self.assertEqual(original.count(marker), 1)
                self.assertEqual(updated_bytes.count(marker), 1)
            if module_id == target_id:
                continue
            block_start = f"<!-- sync-module-start:{module_id} -->".encode()
            block_end = f"<!-- sync-module-end:{module_id} -->".encode()
            original_start = original.index(block_start)
            original_end = original.index(block_end) + len(block_end)
            updated_start = updated_bytes.index(block_start)
            updated_end = updated_bytes.index(block_end) + len(block_end)
            self.assertEqual(
                original[original_start:original_end],
                updated_bytes[updated_start:updated_end],
            )

        validation, validation_report = self.validate_json(updated, "--allow-placeholders")
        self.assertEqual(validation.returncode, 0, msg=validation.stderr or validation.stdout)
        self.assertIs(validation_report.get("ok"), True)

    def test_replacer_rejects_wrong_or_missing_local_content_shell(self) -> None:
        source = self.workspace / "shell-contract" / "scaffold.svg"
        fragments = self.workspace / "shell-contract" / "fragments"
        scaffold_result = self.run_tool(
            SCAFFOLD,
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(source.relative_to(self.workspace)),
            "--fragments-dir",
            str(fragments.relative_to(self.workspace)),
            "--json",
        )
        self.assertEqual(scaffold_result.returncode, 0, msg=scaffold_result.stderr or scaffold_result.stdout)

        plan = self.template_plan()
        modules = plan["modules"]
        assert isinstance(modules, list) and modules and isinstance(modules[0], dict)
        target_id = str(modules[0]["id"])
        generated = (fragments / f"{target_id}.svg").read_text(encoding="utf-8")
        authored = generated.replace('data-placeholder="true"', "", 1)
        authored = authored.replace("placeholder-mark", "authored-mark")
        authored = authored.replace("placeholder-value", "authored-value")
        authored = authored.replace(
            '<!-- Remove data-placeholder="true" from this root only after the visual is complete. -->',
            "<!-- Authored local-coordinate fragment. -->",
            1,
        )
        authored_root = ET.fromstring(authored.encode("utf-8"))
        expected_transform = authored_root.get("transform")
        self.assertIsNotNone(expected_transform)
        assert expected_transform is not None
        content_top = float(str(authored_root.get("data-content-origin")).split()[1])
        wrong_transform = f"translate(0 {fmt_number(content_top + 1)})"

        declaration = re.match(
            r"^[ \t\r\n]*<\?xml[ \t\r\n]+[^?]*\?>[ \t\r\n]*",
            authored,
            re.IGNORECASE,
        )
        self.assertIsNotNone(declaration)
        assert declaration is not None
        body = authored[declaration.end() :]
        opening = re.match(r"<g\b[^>]*>[ \t\r\n]*", body, re.DOTALL)
        self.assertIsNotNone(opening)
        assert opening is not None
        closing = body.rfind("</g>")
        self.assertGreater(closing, opening.end())
        without_shell = authored[: declaration.end()] + body[opening.end() : closing]

        cases = {
            "wrong-transform": authored.replace(expected_transform, wrong_transform, 1),
            "missing-transform": authored.replace(f'   transform="{expected_transform}"\n', "", 1),
            "missing-shell": without_shell,
            "changed-width": authored.replace(
                f'data-content-width="{authored_root.get("data-content-width")}"',
                'data-content-width="1"',
                1,
            ),
        }
        original = source.read_bytes()
        for name, fragment_text in cases.items():
            with self.subTest(name=name):
                fragment = self.workspace / "shell-contract" / f"{name}.svg"
                fragment.write_text(fragment_text, encoding="utf-8", newline="\n")
                result = self.run_tool(
                    REPLACER,
                    str(source),
                    str(fragment),
                    "--module",
                    target_id,
                    "--in-place",
                )
                report = self.parse_json_stdout(result)
                self.assertEqual(result.returncode, 1)
                self.assertIs(report.get("ok"), False)
                self.assertIn("shell", str(report.get("error")).lower())
                self.assertEqual(source.read_bytes(), original)

        source_root = ET.fromstring(original)
        target_module = next(
            element for element in source_root.iter() if element.get("data-module-id") == target_id
        )
        expected_top = target_module.get("data-content-top")
        self.assertIsNotNone(expected_top)
        assert expected_top is not None
        changed_source = self.workspace / "shell-contract" / "changed-source-shell.svg"
        changed_source.write_bytes(
            original.replace(
                f'data-content-top="{expected_top}"'.encode(),
                f'data-content-top="{fmt_number(float(expected_top) + 1)}"'.encode(),
                1,
            )
        )
        valid_fragment = self.workspace / "shell-contract" / "valid-authored.svg"
        valid_fragment.write_text(authored, encoding="utf-8", newline="\n")
        rejected_output = self.workspace / "shell-contract" / "must-not-exist.svg"
        result = self.run_tool(
            REPLACER,
            str(changed_source),
            str(valid_fragment),
            "--module",
            target_id,
            "--output",
            str(rejected_output.relative_to(self.workspace)),
        )
        report = self.parse_json_stdout(result)
        self.assertEqual(result.returncode, 1)
        self.assertIs(report.get("ok"), False)
        self.assertIn("source module shell", str(report.get("error")).lower())
        self.assertFalse(rejected_output.exists())

    def test_validator_rejects_runtime_method_removal_and_orphan_binding(self) -> None:
        source = self.workspace / "source.svg"
        self.scaffold_template(source)
        original = source.read_text(encoding="utf-8")

        missing_method = self.workspace / "missing-runtime-method.svg"
        missing_method.write_text(
            original.replace("serializeSnapshot", "removedSerializeMethod"),
            encoding="utf-8",
            newline="\n",
        )
        orphan = self.workspace / "orphan-binding.svg"
        orphan_markup = (
            '  <text id="orphan-binding" data-role="orphan-value" '
            'data-bind="base-salary-annual" data-channel="text" '
            'data-current-value="90000" data-sync-revision="0">$90,000</text>\n'
        )
        orphan.write_text(
            original.replace("  <script>", orphan_markup + "  <script>", 1),
            encoding="utf-8",
            newline="\n",
        )
        tampered_body = self.workspace / "tampered-body-shell.svg"
        tampered_body_text = re.sub(
            r'data-content-width="[^"]+"',
            'data-content-width="1"',
            original,
            count=1,
        )
        self.assertNotEqual(tampered_body_text, original)
        tampered_body.write_text(
            tampered_body_text,
            encoding="utf-8",
            newline="\n",
        )
        invalid_plan = self.workspace / "invalid-embedded-plan.svg"
        invalid_plan_text = original.replace('"modules":[', '"notModules":[', 1)
        self.assertNotEqual(invalid_plan_text, original)
        invalid_plan.write_text(
            invalid_plan_text,
            encoding="utf-8",
            newline="\n",
        )

        cases = (
            (missing_method, ("missing methods", "serializesnapshot")),
            (orphan, ("dom bindings not declared",)),
            (tampered_body, ("body width differs",)),
            (invalid_plan, ("embedded composition plan is invalid",)),
        )
        for svg, expected_fragments in cases:
            with self.subTest(svg=svg.name):
                result, report = self.validate_json(svg, "--allow-placeholders")
                self.assertEqual(result.returncode, 1)
                self.assertIs(report.get("ok"), False)
                failures = "\n".join(str(item).lower() for item in report.get("failures", []))
                for fragment in expected_fragments:
                    self.assertIn(fragment, failures)

    def test_published_compact_brief_with_relationships_runs_full_chain(self) -> None:
        brief = json.loads(BRIEF_TEMPLATE.read_text(encoding="utf-8"))
        brief_path = self.write_plan("published-composition-brief.json", brief)
        plan_path = self.workspace / "published-composition-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        compiled_report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        self.assertIs(compiled_report.get("ok"), True)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        self.assertEqual(len(plan["relationships"]), len(brief["relationships"]))

        svg = self.workspace / "published-composition.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(svg),
            "--json",
        )
        composed_report = self.parse_json_stdout(composed)
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        self.assertIs(composed_report.get("ok"), True)
        validation, validation_report = self.validate_json(
            svg,
            "--min-modules",
            "6",
            "--min-asset-types",
            "4",
            "--require-time-sync",
        )
        self.assertEqual(validation.returncode, 0, msg=validation.stderr or validation.stdout)
        self.assertIs(validation_report.get("ok"), True)

    def test_compact_edge_brief_compiles_deterministically_and_composes(self) -> None:
        self.assertLess(BRIEF_TEMPLATE.stat().st_size, 10 * 1024)
        template_brief = json.loads(BRIEF_TEMPLATE.read_text(encoding="utf-8"))
        self.assertIsInstance(template_brief, dict)
        generic_id = str(template_brief.get("compositionId", ""))
        for overfit_token in ("compensation", "cloud", "edge"):
            self.assertNotIn(overfit_token, generic_id)
        generic_plan = self.workspace / "generic-plan.json"
        generic_result = self.run_tool(
            COMPILER,
            "--brief",
            str(BRIEF_TEMPLATE),
            "--output",
            str(generic_plan),
            "--json",
        )
        generic_report = self.parse_json_stdout(generic_result)
        self.assertEqual(generic_result.returncode, 0, msg=generic_result.stderr or generic_result.stdout)
        self.assertIs(generic_report.get("ok"), True)
        self.assertTrue(generic_plan.is_file())
        compiled_generic = json.loads(generic_plan.read_text(encoding="utf-8"))
        generic_modules = {module["id"]: module for module in compiled_generic["modules"]}
        overview = generic_modules["operating-system"]
        self.assertEqual(
            {binding["channel"] for binding in overview["bindings"]},
            {"text"},
        )
        self.assertTrue(all("transform" not in binding for binding in overview["bindings"]))
        generic_identity = compiled_generic["identity"]
        generic_value_ids = [
            item["id"]
            for item in [*compiled_generic["concepts"], *compiled_generic["derived"]]
        ]
        self.assertEqual(
            [generic_identity[value_id]["colorToken"] for value_id in generic_value_ids],
            generic_value_ids,
        )
        self.assertEqual(
            len({generic_identity[value_id]["colorToken"] for value_id in generic_value_ids}),
            len(generic_value_ids),
        )
        generic_load = generic_modules["capacity-pressure"]
        self.assertEqual(generic_load["assetType"], "bullet-chart")
        self.assertEqual(
            [(binding["value"], binding["channel"]) for binding in generic_load["bindings"]],
            [("demand-capacity-ratio", "width"), ("demand-capacity-ratio", "text")],
        )
        self.assertLessEqual(
            generic_load["bindings"][0]["transform"]["domain"][0],
            1,
        )
        self.assertGreaterEqual(
            generic_load["bindings"][0]["transform"]["domain"][1],
            1,
        )

        brief_path = self.write_plan("edge-brief.json", self.edge_brief())
        original_brief = brief_path.read_bytes()
        first_plan = self.workspace / "compiled" / "edge-plan-a.json"
        second_plan = self.workspace / "compiled" / "edge-plan-b.json"
        first_result = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(first_plan),
            "--json",
        )
        second_result = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(second_plan),
            "--json",
        )
        first_report = self.parse_json_stdout(first_result)
        second_report = self.parse_json_stdout(second_result)
        self.assertEqual(first_result.returncode, 0, msg=first_result.stderr or first_result.stdout)
        self.assertEqual(second_result.returncode, 0, msg=second_result.stderr or second_result.stdout)
        self.assertIs(first_report.get("ok"), True)
        self.assertIs(second_report.get("ok"), True)
        self.assertEqual(first_plan.read_bytes(), second_plan.read_bytes())
        self.assertEqual(first_report.get("sha256"), second_report.get("sha256"))
        self.assertEqual(brief_path.read_bytes(), original_brief)

        normalizations = first_report.get("normalizations")
        self.assertIsInstance(normalizations, list)
        assert isinstance(normalizations, list)
        capacity_normalization = next(
            item for item in normalizations if isinstance(item, dict) and item.get("sourceId") == "edge-capacity"
        )
        self.assertEqual(capacity_normalization.get("oldDomain"), [0, 3000])
        new_domain = capacity_normalization.get("newDomain")
        self.assertIsInstance(new_domain, list)
        assert isinstance(new_domain, list)
        self.assertGreater(float(new_domain[0]), 0)

        plan = json.loads(first_plan.read_text(encoding="utf-8"))
        self.assertEqual(plan["viewBox"], [0, 0, 1600, 1000])
        self.assertEqual(plan["syncModes"], ["semantic", "state", "focus", "time"])
        self.assertEqual(len(plan["modules"]), 7)
        self.assertEqual(
            next(item for item in plan["derived"] if item["id"] == "edge-load-ratio")["dependsOn"],
            ["edge-capacity", "request-rate"],
        )
        self.assertEqual(
            next(item for item in plan["derived"] if item["id"] == "blended-latency")["dependsOn"],
            ["cache-hit-rate", "edge-latency", "origin-latency"],
        )

        regions = [module["region"] for module in plan["modules"]]
        left = min(float(region[0]) for region in regions)
        top = min(float(region[1]) for region in regions)
        right = max(float(region[0]) + float(region[2]) for region in regions)
        bottom = max(float(region[1]) + float(region[3]) for region in regions)
        self.assertGreaterEqual(right - left, 0.70 * 1600)
        self.assertGreaterEqual(bottom - top, 0.70 * 1000)
        self.assertTrue(all(float(region[2]) >= 230 for region in regions))
        self.assertTrue(all(float(region[3]) >= 360 for region in regions))
        self.assertGreater(max(float(region[2]) for region in regions), 1.5 * min(float(region[2]) for region in regions))
        by_module = {module["id"]: module for module in plan["modules"]}
        for module_id in ("traffic-topology", "request-flow", "edge-ledger"):
            self.assertGreaterEqual(float(by_module[module_id]["region"][2]), 352)
            self.assertGreaterEqual(float(by_module[module_id]["region"][3]), 360)
        topology = by_module["traffic-topology"]
        self.assertEqual({binding["channel"] for binding in topology["bindings"]}, {"text"})
        service_mix = by_module["service-mix"]
        self.assertEqual(service_mix.get("stackTotal"), "request-rate")
        self.assertEqual(
            [binding["value"] for binding in service_mix["bindings"]],
            ["edge-served-rate", "origin-rate"],
        )
        self.assertEqual(
            {tuple(binding["transform"]["domain"]) for binding in service_mix["bindings"]},
            {(0, 3000)},
        )
        self.assertEqual(
            {tuple(binding["transform"]["range"]) for binding in service_mix["bindings"]},
            {(0, 240)},
        )
        latency_bars = by_module["latency-consequence"]
        self.assertEqual(
            {tuple(binding["transform"]["domain"]) for binding in latency_bars["bindings"]},
            {(0, 500)},
        )
        self.assertEqual(
            {tuple(binding["transform"]["range"]) for binding in latency_bars["bindings"]},
            {(0, 240)},
        )
        load_bullet = by_module["load-ratio-bullet"]
        self.assertEqual(
            [(binding["value"], binding["channel"]) for binding in load_bullet["bindings"]],
            [("edge-load-ratio", "width"), ("edge-load-ratio", "text")],
        )
        self.assertNotIn("transform", load_bullet["bindings"][1])
        self.assertEqual(load_bullet["bindings"][0]["format"], load_bullet["bindings"][1]["format"])
        self.assertEqual(
            [plan["identity"][value_id]["colorToken"] for value_id in plan["identity"]],
            list(plan["identity"]),
        )

        timeline = plan["timeline"]
        self.assertEqual(
            [(phase["startMs"], phase["endMs"]) for phase in timeline["phases"]],
            [(0, 3000), (3000, 6000), (6000, 9000), (9000, 12000)],
        )
        for module in plan["modules"]:
            roles = [binding["selector"] for binding in module["bindings"]]
            self.assertEqual(len(roles), len(set(roles)))

        svg = self.workspace / "rendered" / "edge-atlas.svg"
        compose_report = self.workspace / "rendered" / "compose-report.json"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(first_plan),
            "--output",
            str(svg),
            "--report",
            str(compose_report),
            "--json",
        )
        composed_report = self.parse_json_stdout(composed)
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        self.assertIs(composed_report.get("ok"), True)
        self.assertTrue(svg.is_file())
        validation, validation_report = self.validate_json(
            svg,
            "--min-modules",
            "6",
            "--min-asset-types",
            "4",
            "--require-time-sync",
        )
        self.assertEqual(validation.returncode, 0, msg=validation.stderr or validation.stdout)
        self.assertIs(validation_report.get("ok"), True)
        self.assertEqual(validation_report.get("failures"), [])
        corrupted_plan = json.loads(json.dumps(plan))
        corrupted_latency = next(
            module for module in corrupted_plan["modules"] if module["id"] == "latency-consequence"
        )
        corrupted_latency["bindings"][0]["transform"]["domain"][1] = 1000
        corrupted_plan_path = self.write_plan("corrupted-bar-scale.json", corrupted_plan)
        rejected_svg = self.workspace / "rendered" / "corrupted-bar-scale.svg"
        rejected_bar_scale = self.run_tool(
            COMPOSER,
            "--spec",
            str(corrupted_plan_path),
            "--output",
            str(rejected_svg),
            "--json",
        )
        rejected_bar_report = self.parse_json_stdout(rejected_bar_scale)
        self.assertEqual(rejected_bar_scale.returncode, 1)
        self.assertIn("shared scale", str(rejected_bar_report.get("error")))
        self.assertFalse(rejected_svg.exists())
        rendered_root = ET.parse(svg).getroot()
        network_group = next(
            element
            for element in rendered_root.iter()
            if element.get("id") == "traffic-topology-network-plot"
        )
        node_cards = [
            element
            for element in network_group
            if element.tag.endswith("rect") and element.get("stroke", "").startswith("var(--concept-")
        ]
        self.assertEqual(len(node_cards), len(topology["bindings"]))
        self.assertEqual(
            {(card.get("width"), card.get("height")) for card in node_cards},
            {(node_cards[0].get("width"), node_cards[0].get("height"))},
        )
        dependency_edges = {
            element.get("data-dependency-edge")
            for element in network_group
            if element.get("data-dependency-edge")
        }
        self.assertEqual(
            dependency_edges,
            {"request-rate:edge-served-rate", "request-rate:origin-rate"},
        )
        visible_network_copy = " ".join(
            text.strip()
            for text in network_group.itertext()
            if text and text.strip()
        )
        self.assertIn("requests/second", visible_network_copy)
        self.assertEqual(
            len([element for element in rendered_root.iter() if element.get("data-timeline-label") == "true"]),
            1,
        )

        rejected = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(first_plan),
            "--json",
        )
        rejected_report = self.parse_json_stdout(rejected)
        self.assertEqual(rejected.returncode, 1)
        self.assertIs(rejected_report.get("ok"), False)
        stable_bytes = first_plan.read_bytes()
        forced = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(first_plan),
            "--force",
            "--json",
        )
        forced_report = self.parse_json_stdout(forced)
        self.assertEqual(forced.returncode, 0, msg=forced.stderr or forced.stdout)
        self.assertIs(forced_report.get("ok"), True)
        self.assertEqual(first_plan.read_bytes(), stable_bytes)

        same_path = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(brief_path),
            "--force",
            "--json",
        )
        same_path_report = self.parse_json_stdout(same_path)
        self.assertEqual(same_path.returncode, 1)
        self.assertIs(same_path_report.get("ok"), False)
        self.assertIn("never mutates", str(same_path_report.get("error")))
        self.assertEqual(brief_path.read_bytes(), original_brief)

    def test_comparative_bar_compiler_rejects_mixed_units_and_signed_envelopes(self) -> None:
        mixed = self.edge_brief()
        mixed_module = next(module for module in mixed["modules"] if module["id"] == "latency-consequence")
        mixed_module["values"] = ["edge-latency", "edge-load-ratio"]
        mixed_path = self.write_plan("mixed-unit-bars.json", mixed)
        mixed_output = self.workspace / "mixed-unit-bars-plan.json"
        mixed_result = self.run_tool(
            COMPILER,
            "--brief",
            str(mixed_path),
            "--output",
            str(mixed_output),
            "--json",
        )
        mixed_report = self.parse_json_stdout(mixed_result)
        self.assertEqual(mixed_result.returncode, 1)
        self.assertIn("must share one unit", str(mixed_report.get("error")))
        self.assertFalse(mixed_output.exists())

        signed = self.edge_brief()
        signed_source = next(concept for concept in signed["concepts"] if concept["id"] == "edge-latency")
        signed_source["domain"] = [-10, 200]
        signed_path = self.write_plan("signed-bars.json", signed)
        signed_output = self.workspace / "signed-bars-plan.json"
        signed_result = self.run_tool(
            COMPILER,
            "--brief",
            str(signed_path),
            "--output",
            str(signed_output),
            "--json",
        )
        signed_report = self.parse_json_stdout(signed_result)
        self.assertEqual(signed_result.returncode, 1)
        self.assertIn("nonnegative values on one zero baseline", str(signed_report.get("error")))
        self.assertFalse(signed_output.exists())

    def test_flow_compiler_rejects_nonconserving_branches(self) -> None:
        brief = self.edge_brief()
        flow = next(module for module in brief["modules"] if module["id"] == "request-flow")
        flow["values"].append("edge-capacity")
        brief_path = self.write_plan("nonconserving-flow-brief.json", brief)
        output = self.workspace / "nonconserving-flow-plan.json"

        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(output),
            "--json",
        )
        report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 1)
        self.assertIn("flow does not conserve", str(report.get("error")))
        self.assertIn("use a table/network", str(report.get("error")))
        self.assertFalse(output.exists())

    def test_brief_preflight_reports_expected_defects_without_tool_failure(self) -> None:
        invalid = self.edge_brief()
        flow = next(module for module in invalid["modules"] if module["id"] == "request-flow")
        flow["values"].append("edge-capacity")
        invalid_path = self.write_plan("preflight-invalid-brief.json", invalid)
        invalid_sha = sha256(invalid_path)

        rejected = self.run_tool(
            PREFLIGHT,
            "--brief",
            str(invalid_path),
            "--json",
        )
        rejected_report = self.parse_json_stdout(rejected)
        self.assertEqual(rejected.returncode, 0, msg=rejected.stderr or rejected.stdout)
        self.assertIs(rejected_report.get("ok"), False)
        self.assertIn("flow does not conserve", str(rejected_report.get("finding")))
        self.assertEqual(sha256(invalid_path), invalid_sha)
        self.assertFalse(any(self.workspace.glob("*plan*.json")))

        malformed = self.workspace / "preflight-malformed.json"
        malformed.write_text('{"compositionId":', encoding="utf-8", newline="\n")
        malformed_result = self.run_tool(
            PREFLIGHT,
            "--brief",
            str(malformed),
            "--json",
        )
        malformed_report = self.parse_json_stdout(malformed_result)
        self.assertEqual(malformed_result.returncode, 0)
        self.assertIs(malformed_report.get("ok"), False)
        self.assertIn("not valid JSON", str(malformed_report.get("finding")))

        duplicate = self.workspace / "preflight-duplicate-key.json"
        duplicate.write_text(
            '{"compositionId":"first","compositionId":"second"}\n',
            encoding="utf-8",
            newline="\n",
        )
        duplicate_result = self.run_tool(
            PREFLIGHT,
            "--brief",
            str(duplicate),
            "--json",
        )
        duplicate_report = self.parse_json_stdout(duplicate_result)
        self.assertEqual(duplicate_result.returncode, 0)
        self.assertIs(duplicate_report.get("ok"), False)
        self.assertEqual(duplicate_report.get("stage"), "syntax")
        self.assertIn("duplicate JSON object key", str(duplicate_report.get("finding")))

        accepted_path = self.write_plan("preflight-valid-brief.json", self.edge_brief())
        accepted = self.run_tool(
            PREFLIGHT,
            "--brief",
            str(accepted_path),
            "--json",
        )
        accepted_report = self.parse_json_stdout(accepted)
        self.assertEqual(accepted.returncode, 0, msg=accepted.stderr or accepted.stdout)
        self.assertIs(accepted_report.get("ok"), True)
        self.assertEqual(accepted_report.get("moduleCount"), 7)

    def test_brief_preflight_strict_exit_only_changes_rejection_status(self) -> None:
        invalid = self.edge_brief()
        invalid["locale"] = "fr-FR"
        invalid_path = self.write_plan("strict-preflight-invalid.json", invalid)
        strict_rejection = self.run_tool(
            PREFLIGHT,
            "--brief",
            str(invalid_path),
            "--strict-exit",
            "--json",
        )
        rejected_report = self.parse_json_stdout(strict_rejection)
        self.assertEqual(strict_rejection.returncode, 1)
        self.assertIs(rejected_report.get("ok"), False)
        self.assertEqual(rejected_report.get("stage"), "semantic")
        self.assertFalse(any(self.workspace.glob("*plan*.json")))

        valid_path = self.write_plan("strict-preflight-valid.json", self.edge_brief())
        strict_acceptance = self.run_tool(
            PREFLIGHT,
            "--brief",
            str(valid_path),
            "--strict-exit",
            "--json",
        )
        accepted_report = self.parse_json_stdout(strict_acceptance)
        self.assertEqual(strict_acceptance.returncode, 0)
        self.assertIs(accepted_report.get("ok"), True)
        self.assertEqual(accepted_report.get("moduleCount"), 7)
        self.assertFalse(any(self.workspace.glob("*plan*.json")))

    def test_compiler_rejects_unknown_renderer_and_missing_network_bridge(self) -> None:
        fallback = self.edge_brief()
        fallback_module = next(
            module for module in fallback["modules"] if module["id"] == "latency-consequence"
        )
        fallback_module["assetType"] = "metric-card"
        fallback_output = self.workspace / "fallback-renderer-plan.json"
        fallback_result = self.run_tool(
            COMPILER,
            "--brief",
            str(self.write_plan("fallback-renderer-brief.json", fallback)),
            "--output",
            str(fallback_output),
            "--json",
        )
        fallback_report = self.parse_json_stdout(fallback_result)
        self.assertEqual(fallback_result.returncode, 1)
        self.assertIn("does not select a supported renderer family", str(fallback_report.get("error")))
        self.assertFalse(fallback_output.exists())

        bridged = self.edge_brief()
        bridged["derived"].append(
            {
                "id": "service-total",
                "label": "Total routed service",
                "unit": "requests/second",
                "compute": {
                    "op": "add",
                    "args": [
                        {"ref": "edge-served-rate"},
                        {"ref": "origin-rate"},
                    ],
                },
            }
        )
        network = next(module for module in bridged["modules"] if module["id"] == "traffic-topology")
        network["values"] = ["request-rate", "edge-capacity", "headroom", "service-total"]
        bridge_output = self.workspace / "missing-network-bridge-plan.json"
        bridge_result = self.run_tool(
            COMPILER,
            "--brief",
            str(self.write_plan("missing-network-bridge-brief.json", bridged)),
            "--output",
            str(bridge_output),
            "--json",
        )
        bridge_report = self.parse_json_stdout(bridge_result)
        self.assertEqual(bridge_result.returncode, 1)
        self.assertIn("omits intermediate node", str(bridge_report.get("error")))
        self.assertFalse(bridge_output.exists())

    def test_eight_module_compiler_uses_balanced_four_by_four_layout(self) -> None:
        brief = self.edge_brief()
        brief["modules"].append(
            {
                "id": "capacity-summary",
                "question": "Which exact demand and capacity values anchor the current state?",
                "claim": "A compact matrix keeps demand and capacity readable beside the visual views.",
                "assetType": "capacity-matrix",
                "selectionRationale": "A matrix supports exact lookup without adding another magnitude encoding.",
                "rejectedAlternative": "Another bar chart would duplicate the existing comparison task.",
                "values": ["request-rate", "edge-capacity"],
            }
        )
        brief_path = self.write_plan("eight-module-layout-brief.json", brief)
        plan_path = self.workspace / "eight-module-layout-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        self.assertIs(report.get("ok"), True)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        rows: dict[float, int] = {}
        for module in plan["modules"]:
            rows[float(module["region"][1])] = rows.get(float(module["region"][1]), 0) + 1
        self.assertEqual(sorted(rows.values()), [4, 4])

    def test_flow_compiler_rejects_total_plus_branch_double_count(self) -> None:
        brief = self.edge_brief()
        brief["derived"].append(
            {
                "id": "double-counted-request-total",
                "label": "Incorrect request total",
                "unit": "requests/second",
                "compute": {
                    "op": "add",
                    "args": [
                        {"ref": "request-rate"},
                        {"ref": "edge-served-rate"},
                        {"ref": "origin-rate"},
                    ],
                },
            }
        )
        brief_path = self.write_plan("double-counted-flow-brief.json", brief)
        output = self.workspace / "double-counted-flow-plan.json"

        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(output),
            "--json",
        )
        report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 1)
        self.assertIn("double-counts conserved partition", str(report.get("error")))
        self.assertIn("request-rate", str(report.get("error")))
        self.assertFalse(output.exists())

        # A signed reconciliation identity is legal because branches are
        # subtracted from the source instead of added as peer totals.
        reconciled = self.edge_brief()
        reconciled["derived"].append(
            {
                "id": "request-reconciliation-gap",
                "label": "Request reconciliation gap",
                "unit": "requests/second",
                "compute": {
                    "op": "subtract",
                    "args": [
                        {"ref": "request-rate"},
                        {"ref": "edge-served-rate"},
                        {"ref": "origin-rate"},
                    ],
                },
            }
        )
        reconciled_path = self.write_plan("reconciled-flow-brief.json", reconciled)
        reconciled_output = self.workspace / "reconciled-flow-plan.json"
        accepted = self.run_tool(
            COMPILER,
            "--brief",
            str(reconciled_path),
            "--output",
            str(reconciled_output),
            "--js",
        )
        accepted_report = self.parse_json_stdout(accepted)
        self.assertEqual(accepted.returncode, 0, msg=accepted.stderr or accepted.stdout)
        self.assertIs(accepted_report.get("ok"), True)
        self.assertTrue(reconciled_output.is_file())

    def test_compiler_detects_residual_partition_outside_flow_renderer(self) -> None:
        brief = self.edge_brief()
        brief["derived"].append(
            {
                "id": "double-counted-capacity-check",
                "label": "Incorrect capacity check",
                "unit": "requests/second",
                "compute": {
                    "op": "add",
                    "args": [
                        {"ref": "edge-capacity"},
                        {"ref": "request-rate"},
                        {"ref": "headroom"},
                    ],
                },
            }
        )
        ledger = next(module for module in brief["modules"] if module["id"] == "edge-ledger")
        ledger["values"].append("double-counted-capacity-check")
        brief_path = self.write_plan("network-residual-double-count.json", brief)
        output = self.workspace / "network-residual-double-count-plan.json"

        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(output),
            "--json",
        )
        report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 1)
        self.assertIn("double-counts conserved partition", str(report.get("error")))
        self.assertIn("edge-capacity", str(report.get("error")))
        self.assertFalse(output.exists())

    def test_browser_audit_rejects_independently_normalized_comparative_bars(self) -> None:
        brief_path = self.write_plan("bar-audit-brief.json", self.edge_brief())
        plan_path = self.workspace / "bar-audit-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        svg = self.workspace / "bar-audit.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(svg),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        payload = svg.read_text(encoding="utf-8")
        shared_scale = '"domain":[0,500],"range":[0,240]'
        independent_scale = '"domain":[0,1000],"range":[0,240]'
        self.assertIn(shared_scale, payload)
        corrupted = self.workspace / "bar-audit-corrupted.svg"
        corrupted.write_text(
            payload.replace(shared_scale, independent_scale, 1),
            encoding="utf-8",
            newline="\n",
        )
        report_path = self.workspace / "bar-audit-browser.json"
        screenshot_path = self.workspace / "bar-audit.png"
        audited = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(AUDITOR),
                str(corrupted),
                "--report",
                str(report_path),
                "--screenshot",
                str(screenshot_path),
                "--compact-report",
                "--json",
            ],
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(audited.returncode, 1, msg=audited.stderr or audited.stdout)
        audit_payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIs(audit_payload.get("ok"), False)
        self.assertIn("bar-shared-scale", json.dumps(audit_payload, sort_keys=True))

    def test_browser_audit_rejects_stale_flow_labels_and_phase_progress(self) -> None:
        brief_path = self.write_plan("flow-label-brief.json", self.edge_brief())
        plan_path = self.workspace / "flow-label-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        svg = self.workspace / "flow-label.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(svg),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        payload = svg.read_text(encoding="utf-8")
        source_update = "sourceLabel.textContent = value ? `${base} · ${value}` : base;"
        branch_update = (
            'valueLabel.textContent = mark?.dataset.accessibleValue || '
            'mark?.dataset.currentValue || "";'
        )
        phase_update = "phaseProgress = sample.progress;"
        self.assertIn(source_update, payload)
        self.assertIn(branch_update, payload)
        self.assertIn(phase_update, payload)
        corrupted = self.workspace / "flow-label-corrupted.svg"
        corrupted.write_text(
            payload.replace(
                source_update,
                "sourceLabel.textContent = sourceLabel.textContent;",
            ).replace(
                branch_update,
                "valueLabel.textContent = valueLabel.textContent;",
            ).replace(
                phase_update,
                "phaseProgress = 0;",
            ),
            encoding="utf-8",
            newline="\n",
        )
        report_path = self.workspace / "flow-label-browser.json"
        screenshot_path = self.workspace / "flow-label.png"
        audited = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(AUDITOR),
                str(corrupted),
                "--report",
                str(report_path),
                "--screenshot",
                str(screenshot_path),
                "--compact-report",
                "--json",
            ],
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(audited.returncode, 1, msg=audited.stderr or audited.stdout)
        audit_payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIs(audit_payload.get("ok"), False)
        self.assertIn(
            "flow branch label must mirror the current accessible value",
            json.dumps(audit_payload, sort_keys=True),
        )
        self.assertIn("phaseProgress", json.dumps(audit_payload, sort_keys=True))

    def test_multiple_flow_modules_share_one_runtime_and_pass_browser_audit(self) -> None:
        brief = self.edge_brief()
        primary = next(module for module in brief["modules"] if module["id"] == "request-flow")
        secondary = json.loads(json.dumps(primary))
        secondary.update(
            {
                "id": "request-flow-secondary",
                "question": "How does the same routing split read as an operational handoff?",
                "claim": "A second flow view must reuse the canonical request split without duplicating runtime declarations.",
                "assetType": "flow-diagram",
                "selectionRationale": "A second flow view stress-tests shared runtime behavior across repeated renderer families.",
                "rejectedAlternative": "A static table would not exercise flow geometry or synchronized branch labels.",
                "focusGroups": ["routing-story"],
            }
        )
        brief["modules"].append(secondary)
        routing_group = next(group for group in brief["focusGroups"] if group["id"] == "routing-story")
        routing_group["moduleIds"].append(secondary["id"])

        brief_path = self.write_plan("multi-flow-brief.json", brief)
        plan_path = self.workspace / "multi-flow-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)

        svg = self.workspace / "multi-flow.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(svg),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        payload = svg.read_text(encoding="utf-8")
        self.assertEqual(payload.count("function layoutFlow(plot, group)"), 1)
        self.assertEqual(
            payload.count('const sourceLabel = plot.querySelector("[data-flow-source-label]");'),
            1,
        )
        root = ET.parse(svg).getroot()
        self.assertEqual(
            sum(1 for element in root.iter() if element.get("data-sync-layout") == "flow"),
            2,
        )

        report_path = self.workspace / "multi-flow-browser.json"
        screenshot_path = self.workspace / "multi-flow.png"
        audited = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(AUDITOR),
                str(svg),
                "--report",
                str(report_path),
                "--screenshot",
                str(screenshot_path),
                "--compact-report",
                "--json",
            ],
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(audited.returncode, 0, msg=audited.stderr or audited.stdout)
        audit_payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIs(audit_payload.get("ok"), True)

    def test_compiler_enforces_sign_stable_waterfalls_and_nonnegative_stack_parts(self) -> None:
        signed = self.edge_brief()
        signed["derived"].append(
            {
                "id": "edge-served-deduction",
                "label": "Edge-served deduction",
                "unit": "requests/second",
                "compute": {
                    "op": "multiply",
                    "args": [{"ref": "edge-served-rate"}, -1],
                },
            }
        )
        signed_module = next(
            module for module in signed["modules"] if module["id"] == "load-response"
        )
        signed_module.update(
            {
                "assetType": "waterfall-chart",
                "values": ["request-rate", "edge-served-deduction", "origin-rate"],
            }
        )
        signed_plan_path = self.workspace / "signed-waterfall-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(self.write_plan("signed-waterfall-brief.json", signed)),
            "--output",
            str(signed_plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        signed_plan = json.loads(signed_plan_path.read_text(encoding="utf-8"))
        signed_alias = next(
            alias
            for alias in signed_plan["identityAliases"]
            if "edge-served-deduction" in alias["values"]
        )
        self.assertEqual(
            signed_alias["values"],
            ["edge-served-rate", "edge-served-deduction"],
        )
        self.assertEqual(
            signed_plan["identity"][signed_alias["identity"]]["colorToken"],
            "edge-served-rate",
        )
        waterfall = next(
            module for module in signed_plan["modules"] if module["id"] == "load-response"
        )
        self.assertEqual(waterfall["bindings"][1]["transform"]["range"], [180, 0])
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(signed_plan_path),
            "--output",
            str(self.workspace / "signed-waterfall.svg"),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)

        crossing = self.edge_brief()
        crossing_module = next(
            module for module in crossing["modules"] if module["id"] == "load-response"
        )
        crossing_module.update(
            {
                "assetType": "waterfall-chart",
                "values": ["request-rate", "headroom", "origin-rate"],
            }
        )
        crossing_result = self.run_tool(
            COMPILER,
            "--brief",
            str(self.write_plan("crossing-waterfall-brief.json", crossing)),
            "--output",
            str(self.workspace / "must-not-cross.json"),
            "--json",
        )
        self.assertEqual(crossing_result.returncode, 1)
        self.assertIn("crosses zero", crossing_result.stdout)

        negative_stack = self.edge_brief()
        stack_module = next(
            module for module in negative_stack["modules"] if module["id"] == "service-mix"
        )
        stack_module["values"] = ["headroom", "origin-rate"]
        stack_result = self.run_tool(
            COMPILER,
            "--brief",
            str(self.write_plan("negative-stack-brief.json", negative_stack)),
            "--output",
            str(self.workspace / "must-not-stack.json"),
            "--json",
        )
        self.assertEqual(stack_result.returncode, 1)
        self.assertIn("generated stacks require nonnegative", stack_result.stdout)

    def test_compiler_promotes_mentioned_stack_subtotals_to_text_only_bindings(self) -> None:
        brief = self.edge_brief()
        for index, value_id in enumerate(("part-a", "part-b", "part-c"), start=1):
            brief["concepts"].append(
                {
                    "id": value_id,
                    "label": f"Part {chr(64 + index)}",
                    "unit": "requests/second",
                    "default": index * 100,
                    "domain": [0, 1000],
                }
            )
            for scenario in brief["scenarios"]:
                scenario["values"][value_id] = index * 100
        brief["derived"].extend(
            [
                {
                    "id": "parts-subtotal",
                    "label": "Parts subtotal",
                    "unit": "requests/second",
                    "compute": {
                        "op": "add",
                        "args": [{"ref": "part-a"}, {"ref": "part-b"}],
                    },
                },
                {
                    "id": "parts-total",
                    "label": "Parts total",
                    "unit": "requests/second",
                    "compute": {
                        "op": "add",
                        "args": [{"ref": "parts-subtotal"}, {"ref": "part-c"}],
                    },
                },
            ]
        )
        stack = next(module for module in brief["modules"] if module["id"] == "service-mix")
        stack.pop("stackTotal", None)
        stack["values"] = ["part-a", "part-b", "part-c"]
        stack["claim"] = "Parts subtotal and parts total reconcile the three primitive contributions."
        plan_path = self.workspace / "promoted-stack-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(self.write_plan("promoted-stack-brief.json", brief)),
            "--output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        module = next(item for item in plan["modules"] if item["id"] == "service-mix")
        self.assertEqual(module.get("stackTotal"), "parts-total")
        self.assertEqual(
            [(binding["value"], binding["channel"]) for binding in module["bindings"]],
            [
                ("part-a", "width"),
                ("part-b", "width"),
                ("part-c", "width"),
                ("parts-subtotal", "text"),
                ("parts-total", "text"),
            ],
        )

    def test_compiler_zero_anchors_stack_with_positive_total_domain_minimum(self) -> None:
        brief = self.edge_brief()
        request = next(item for item in brief["concepts"] if item["id"] == "request-rate")
        request["domain"] = [100, 3000]
        brief_path = self.write_plan("positive-minimum-stack-brief.json", brief)
        plan_path = self.workspace / "positive-minimum-stack-plan.json"

        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        self.assertIs(report.get("ok"), True)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        stack = next(module for module in plan["modules"] if module["id"] == "service-mix")
        transformed = [binding for binding in stack["bindings"] if "transform" in binding]
        self.assertTrue(transformed)
        self.assertTrue(all(binding["transform"]["domain"][0] == 0 for binding in transformed))

    def test_compact_brief_compiler_rejects_unknown_refs_and_cycles_atomically(self) -> None:
        base = self.edge_brief()
        unknown = json.loads(json.dumps(base))
        unknown["derived"][0]["compute"] = {"ref": "missing-value"}
        cycle = json.loads(json.dumps(base))
        cycle["derived"][0]["compute"] = {"ref": "origin-rate"}
        cycle["derived"][1]["compute"] = {"ref": "edge-served-rate"}
        timeline_zero = json.loads(json.dumps(base))
        timeline_zero["timeline"]["phases"][0]["values"]["edge-capacity"] = 0
        false_utilization = json.loads(json.dumps(base))
        load_ratio = next(
            item for item in false_utilization["derived"] if item["id"] == "edge-load-ratio"
        )
        load_ratio["id"] = "utilization"
        load_ratio["label"] = "Edge utilization"
        unrelated_color = json.loads(json.dumps(base))
        next(
            item for item in unrelated_color["derived"] if item["id"] == "edge-load-ratio"
        )["colorSource"] = "edge-latency"
        unbounded_radial = json.loads(json.dumps(base))
        radial_module = next(
            item for item in unbounded_radial["modules"] if item["id"] == "load-ratio-bullet"
        )
        radial_module["assetType"] = "radial-gauge"
        duplicate_relationship = json.loads(json.dumps(base))
        duplicate_relationship["relationships"] = [
            {
                "id": "first-link",
                "source": "traffic-topology",
                "target": "request-flow",
                "kind": "flow",
                "label": "Traffic enters the request flow",
            },
            {
                "id": "second-link",
                "source": "traffic-topology",
                "target": "request-flow",
                "kind": "flow",
                "label": "Duplicate traffic link",
            },
        ]
        missing_relationship_label = json.loads(json.dumps(base))
        missing_relationship_label["relationships"] = [
            {
                "id": "unlabeled-link",
                "source": "traffic-topology",
                "target": "request-flow",
                "kind": "flow",
            }
        ]
        missing_armature = json.loads(json.dumps(base))
        missing_armature.pop("armature", None)
        cases = (
            ("unknown", unknown, "unknown value"),
            ("cycle", cycle, "cycle"),
            ("timeline-zero", timeline_zero, "zero default, scenario, or timeline value"),
            ("false-utilization", false_utilization, "named utilization"),
            ("unrelated-color", unrelated_color, "not a semantic ancestor"),
            ("unbounded-radial", unbounded_radial, "use a bullet/progress asset"),
            ("duplicate-relationship", duplicate_relationship, "duplicate relationship endpoints"),
            ("missing-relationship-label", missing_relationship_label, "label must be a non-empty string"),
            ("missing-armature", missing_armature, "armature must be a non-empty string"),
        )
        for name, brief, expected_error in cases:
            with self.subTest(name=name):
                brief_path = self.write_plan(f"{name}-brief.json", brief)
                original = brief_path.read_bytes()
                output = self.workspace / "invalid" / f"{name}-plan.json"
                result = self.run_tool(
                    COMPILER,
                    "--brief",
                    str(brief_path),
                    "--output",
                    str(output),
                    "--json",
                )
                report = self.parse_json_stdout(result)
                self.assertEqual(result.returncode, 1)
                self.assertIs(report.get("ok"), False)
                self.assertIn(expected_error, str(report.get("error")).lower())
                self.assertFalse(output.exists())
                self.assertEqual(brief_path.read_bytes(), original)

    def test_top_level_focus_groups_are_the_only_membership_authority(self) -> None:
        brief = json.loads(BRIEF_TEMPLATE.read_text(encoding="utf-8"))
        self.assertTrue(all("focusGroups" not in module for module in brief["modules"]))
        # Legacy module-level copies may be stale. They must never compete with
        # the validated top-level membership map.
        brief["modules"][0]["focusGroups"] = ["stale-legacy-copy"]
        brief_path = self.write_plan("legacy-focus-copy-brief.json", brief)
        plan_path = self.workspace / "legacy-focus-copy-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        self.assertIs(report.get("ok"), True)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        memberships = {module["id"]: module["focusGroups"] for module in plan["modules"]}
        self.assertEqual(memberships["operating-system"], ["drivers-story"])
        self.assertNotIn("stale-legacy-copy", memberships["operating-system"])

    def test_open_loop_compiles_and_exact_duration_wraps_to_zero(self) -> None:
        brief = self.edge_brief()
        brief["timeline"]["phases"][-1]["values"]["request-rate"] = 1900
        brief_path = self.write_plan("open-loop-brief.json", brief)
        plan_path = self.workspace / "open-loop-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        self.assertIs(report.get("ok"), True)
        svg = self.workspace / "open-loop.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(svg),
            "--json",
        )
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        script = next(element for element in ET.parse(svg).getroot().iter() if element.tag.endswith("script"))
        self.assertIn("nextTime > 0 && nextTime >= duration", script.text or "")

    def test_compact_brief_compiles_sixteen_module_megacanvas_with_relationships(self) -> None:
        brief = json.loads(BRIEF_TEMPLATE.read_text(encoding="utf-8"))
        templates = brief["modules"]
        modules: list[dict[str, object]] = []
        module_ids: list[str] = []
        for index in range(16):
            module = json.loads(json.dumps(templates[index % len(templates)]))
            module_id = f"loop-stage-{index + 1:02d}"
            module_ids.append(module_id)
            module["id"] = module_id
            module["question"] = f"What does stage {index + 1} reveal about the shared loop?"
            module["claim"] = f"Stage {index + 1} remains synchronized with the same operating state."
            module["selectionRationale"] = (
                f"The selected {module['assetType']} answers the stage {index + 1} reading task."
            )
            module["rejectedAlternative"] = (
                "A generic table was rejected because it would erase the intended visual comparison."
            )
            module["focusGroups"] = ["whole-loop"]
            modules.append(module)
        brief["compositionId"] = "sixteen-stage-loop"
        brief["title"] = "Sixteen Stage Loop"
        brief["armature"] = "causal-flow-spine-with-feedback"
        brief["modules"] = modules
        brief["focusGroups"] = [
            {"id": "whole-loop", "label": "Whole loop", "moduleIds": module_ids}
        ]
        brief["relationships"] = [
            {
                "id": f"stage-link-{index + 1:02d}",
                "source": module_ids[index],
                "target": module_ids[index + 1],
                "kind": "flow",
                "label": f"Stage {index + 1} hands state to stage {index + 2}",
            }
            for index in range(15)
        ] + [
            {
                "id": "stage-loop-feedback",
                "source": module_ids[-1],
                "target": module_ids[0],
                "kind": "feedback",
                "label": "The final stage closes the operating loop",
            },
            {
                "id": "stage-long-row-dependency",
                "source": module_ids[0],
                "target": module_ids[3],
                "kind": "dependency",
                "label": "The primary stage informs the end of the first row",
            },
            {
                "id": "stage-long-column-dependency",
                "source": module_ids[1],
                "target": module_ids[9],
                "kind": "dependency",
                "label": "An early stage informs a later-row stage",
            },
        ]
        for phase in brief["timeline"]["phases"]:
            phase["focusId"] = "whole-loop"

        brief_path = self.write_plan("sixteen-stage-brief.json", brief)
        plan_path = self.workspace / "sixteen-stage-plan.json"
        compiled = self.run_tool(
            COMPILER,
            "--brief",
            str(brief_path),
            "--output",
            str(plan_path),
            "--json",
        )
        compiled_report = self.parse_json_stdout(compiled)
        self.assertEqual(compiled.returncode, 0, msg=compiled.stderr or compiled.stdout)
        self.assertIs(compiled_report.get("ok"), True)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        self.assertEqual(plan["viewBox"], [0, 0, 2400, 1800])
        self.assertEqual(plan["layout"]["safeArea"], [48, 128, 2304, 1624])
        self.assertEqual([module["id"] for module in plan["modules"]], module_ids)
        self.assertEqual(len({module["region"][1] for module in plan["modules"]}), 4)
        self.assertEqual(len(plan["relationships"]), 18)
        self.assertEqual(plan["relationships"][-3]["kind"], "feedback")

        svg = self.workspace / "sixteen-stage-loop.svg"
        composed = self.run_tool(
            COMPOSER,
            "--spec",
            str(plan_path),
            "--output",
            str(svg),
            "--json",
        )
        composed_report = self.parse_json_stdout(composed)
        self.assertEqual(composed.returncode, 0, msg=composed.stderr or composed.stdout)
        self.assertIs(composed_report.get("ok"), True)
        root = ET.parse(svg).getroot()
        relationship_groups = [
            element for element in root.iter() if element.get("data-relationship-id")
        ]
        self.assertEqual(len(relationship_groups), 18)
        self.assertTrue(
            all(
                any(child.get("data-relationship-pulse") == "true" for child in group)
                for group in relationship_groups
            )
        )
        relationship_path_data = {
            group.get("data-relationship-id"): next(
                child for child in group if "relationship-path" in child.get("class", "").split()
            ).get("d", "")
            for group in relationship_groups
        }
        long_row_path = relationship_path_data["stage-long-row-dependency"]
        self.assertGreaterEqual(long_row_path.count("V"), 2)
        self.assertIn(" H", long_row_path)
        long_column_path = relationship_path_data["stage-long-column-dependency"]
        outside_lane = re.search(r"H(-?[0-9.]+)", long_column_path)
        self.assertIsNotNone(outside_lane)
        assert outside_lane is not None
        self.assertLess(float(outside_lane.group(1)), float(plan["layout"]["safeArea"][0]))
        relationship_paths = [
            child
            for group in relationship_groups
            for child in group
            if "relationship-path" in child.get("class", "").split()
        ]
        self.assertEqual(len(relationship_paths), 18)
        self.assertTrue(all(path.get("stroke") == "#526176" for path in relationship_paths))
        relationship_style = next(element for element in root.iter() if element.tag.endswith("style"))
        self.assertIn(".relationship-path { vector-effect: non-scaling-stroke; opacity: 0.86;", relationship_style.text or "")
        self.assertIn('[data-kind="feedback"] .relationship-path { stroke: #8a4b08; }', relationship_style.text or "")
        validation, validation_report = self.validate_json(
            svg,
            "--min-modules",
            "16",
            "--min-renderer-families",
            "5",
            "--require-time-sync",
        )
        self.assertEqual(
            validation.returncode,
            0,
            msg=(validation.stderr or validation.stdout)
            + "\nDense route diagnostics: "
            + json.dumps(
                {
                    route_id: relationship_path_data[route_id]
                    for route_id in ("stage-link-12", "stage-loop-feedback")
                },
                sort_keys=True,
            ),
        )
        self.assertIs(validation_report.get("ok"), True)
        self.assertEqual(validation_report.get("metrics", {}).get("relationshipCount"), 18)

        rendered = svg.read_text(encoding="utf-8")
        relationship_mutations = (
            (
                "wrong-relationship-endpoint",
                rendered.replace(
                    'data-source-module="loop-stage-01"',
                    'data-source-module="loop-stage-16"',
                    1,
                ),
                "data-source-module differs from the plan",
            ),
            (
                "missing-relationship-pulse",
                rendered.replace(
                    'data-relationship-pulse="true"',
                    'data-relationship-pulse="false"',
                    1,
                ),
                "needs exactly one pulse circle",
            ),
        )
        for name, mutated_text, expected_error in relationship_mutations:
            with self.subTest(name=name):
                self.assertNotEqual(mutated_text, rendered)
                mutated_svg = self.workspace / f"{name}.svg"
                mutated_svg.write_text(mutated_text, encoding="utf-8", newline="\n")
                mutated_result, mutated_report = self.validate_json(
                    mutated_svg,
                    "--min-modules",
                    "16",
                    "--require-time-sync",
                )
                self.assertEqual(mutated_result.returncode, 1)
                self.assertIs(mutated_report.get("ok"), False)
                self.assertIn(expected_error, "\n".join(mutated_report.get("failures", [])))

    def test_exact_output_path_and_forced_rerun_are_deterministic(self) -> None:
        output = self.workspace / "exact" / "requested-name.svg"
        self.scaffold_template(output)
        initial_hash = sha256(output)
        initial_bytes = output.read_bytes()

        rejected = self.run_tool(
            SCAFFOLD,
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(output.relative_to(self.workspace)),
            "--json",
        )
        rejected_report = self.parse_json_stdout(rejected)
        self.assertEqual(rejected.returncode, 1)
        self.assertIs(rejected_report.get("ok"), False)
        self.assertIn("already exists", str(rejected_report.get("error")))
        self.assertEqual(output.read_bytes(), initial_bytes)

        forced = self.run_tool(
            SCAFFOLD,
            "--spec",
            str(PLAN_TEMPLATE),
            "--output",
            str(output.relative_to(self.workspace)),
            "--force",
            "--json",
        )
        forced_report = self.parse_json_stdout(forced)
        self.assertEqual(forced.returncode, 0, msg=forced.stderr or forced.stdout)
        self.assertIs(forced_report.get("ok"), True)
        self.assertEqual(Path(str(forced_report["output"])), output.resolve())
        self.assertEqual(sha256(output), initial_hash)
        self.assertEqual(sorted(self.workspace.rglob("*.svg")), [output])

        validation_collision = self.run_tool(
            VALIDATOR,
            str(output),
            "--output",
            str(output),
            "--json",
        )
        validation_collision_report = self.parse_json_stdout(validation_collision)
        self.assertEqual(validation_collision.returncode, 1)
        self.assertIs(validation_collision_report.get("ok"), False)
        self.assertIn(
            "must not overwrite the input SVG",
            "\n".join(validation_collision_report.get("failures", [])),
        )
        self.assertEqual(output.read_bytes(), initial_bytes)

        local_plan = self.write_plan("local-plan.json", self.template_plan())
        local_plan_bytes = local_plan.read_bytes()
        scaffold_collision = self.run_tool(
            SCAFFOLD,
            "--spec",
            str(local_plan),
            "--output",
            str(local_plan),
            "--force",
            "--json",
        )
        scaffold_collision_report = self.parse_json_stdout(scaffold_collision)
        self.assertEqual(scaffold_collision.returncode, 1)
        self.assertIs(scaffold_collision_report.get("ok"), False)
        self.assertIn("must not overwrite the input plan", str(scaffold_collision_report.get("error")))
        self.assertEqual(local_plan.read_bytes(), local_plan_bytes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
