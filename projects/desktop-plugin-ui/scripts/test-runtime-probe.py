#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently verify the standalone version-only Pi runtime probe."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / "skills/desktop-plugin-ui/scripts/probe_runtime.py"
ARTIFACTS = ROOT / "projects/desktop-plugin-ui/artifacts/runtime-probe-tests"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
assert ARTIFACTS.resolve().is_relative_to(ROOT.resolve())
RUN = ARTIFACTS / datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%S%f")
RUN.mkdir()
spec = importlib.util.spec_from_file_location("desktop_runtime_probe", HELPER)
probe_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe_module)
BEFORE = hashlib.sha256(HELPER.read_bytes()).hexdigest()
ACTUAL = {}


class RuntimeProbeTests(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp(prefix="case-", dir=RUN))
        self.calls = []
        self.lookups = []

    def lookup(self, mapping):
        def resolve(name):
            self.lookups.append(name)
            return mapping.get(name)
        return resolve

    def runner(self, argv, **kwargs):
        self.calls.append((argv, kwargs))
        self.assertEqual(argv[-1], "--version")
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(kwargs["timeout"], 10)
        if len(argv) == 3 or Path(argv[0]).stem.lower() == "pi":
            version = "1.4.0"
        elif "python" in Path(argv[0]).stem.lower():
            version = "Python 3.13.12"
        else:
            version = "v24.18.0"
        return subprocess.CompletedProcess(argv, 0, version + "\n", "")

    def wrapper(self, text, suffix=".cmd", entries=("node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js",)):
        directory = Path(tempfile.mkdtemp(prefix="launcher-", dir=self.folder))
        shim = directory / ("pi" + suffix)
        shim.write_text(text, encoding="utf-8")
        for entry in entries:
            file = directory / entry
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("// Fixture: must never execute in these mocked checks.\n", encoding="utf-8")
        return shim

    def test_posix_uses_direct_programs_and_only_version_arguments(self):
        report = probe_module.build_report(platform_name="posix", lookup=self.lookup({"node": "/tools/node", "pi": "/tools/pi"}), runner=self.runner)
        self.assertTrue(report["passed"])
        self.assertEqual([call[0] for call in self.calls], [[sys.executable, "--version"], ["/tools/node", "--version"], ["/tools/pi", "--version"]])
        self.assertEqual(self.lookups, ["node", "pi"])
        self.assertEqual(probe_module.exit_code(report), 0)

    def test_windows_executable_needs_no_shell_or_wrapper(self):
        report = probe_module.build_report(platform_name="nt", lookup=self.lookup({"node.exe": "C:/tools/node.exe", "pi.exe": "C:/tools/pi.exe"}), runner=self.runner)
        self.assertTrue(report["passed"])
        self.assertEqual(self.calls[-1][0], ["C:/tools/pi.exe", "--version"])
        self.assertEqual(self.lookups, ["node.exe", "pi.exe"])

    def test_actual_style_cmd_wrapper_resolves_local_entry(self):
        shim = self.wrapper('endLocal & "%_prog%" "%dp0%\\node_modules\\@earendil-works\\pi-coding-agent\\dist\\bundle\\cli.js" %*')
        report = probe_module.build_report(platform_name="nt", lookup=self.lookup({"node.exe": "C:/Program Files/nodejs/node.exe", "pi.cmd": str(shim)}), runner=self.runner)
        self.assertTrue(report["passed"])
        self.assertEqual(self.calls[-1][0], ["C:/Program Files/nodejs/node.exe", str(shim.parent / "node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js"), "--version"])
        self.assertEqual(report["checks"][-1]["launcher"], "windows-npm-entry")

    def test_ps1_and_extensionless_npm_shims_are_parsed_not_executed(self):
        for suffix in [".ps1", ""]:
            with self.subTest(suffix=suffix):
                shim = self.wrapper('& "node$exe" "$basedir/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js" $args', suffix)
                resolved = probe_module.resolve_pi(["node.exe"], platform_name="nt", lookup=self.lookup({"pi.ps1" if suffix else "pi": str(shim)}))
                self.assertEqual(resolved["command"], ["node.exe", str(shim.parent / "node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js")])
                self.assertNotIn(str(shim), resolved["command"])

    def test_legacy_npm_package_and_percent_dp0_entry_work(self):
        relative = "node_modules/@mariozechner/pi-coding-agent/dist/cli.js"
        shim = self.wrapper('"%~dp0\\' + relative.replace("/", "\\") + '" %*', entries=(relative,))
        resolved = probe_module.resolve_pi(["node.exe"], platform_name="nt", lookup=self.lookup({"pi.cmd": str(shim)}))
        self.assertEqual(resolved["command"], ["node.exe", str(shim.parent / relative)])

    def test_adjacent_node_can_launch_pi_without_path_node(self):
        shim = self.wrapper('"%dp0%/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js"')
        local_node = shim.parent / "node.exe"
        local_node.write_bytes(b"fixture")
        resolved = probe_module.resolve_pi(None, platform_name="nt", lookup=self.lookup({"pi.cmd": str(shim)}))
        self.assertEqual(resolved["command"][0], str(local_node))

    def test_missing_pi_is_diagnostic_unless_ci_flag_is_selected(self):
        report = probe_module.build_report(platform_name="posix", lookup=self.lookup({"node": "/tools/node"}), runner=self.runner)
        self.assertFalse(report["passed"])
        self.assertEqual(report["checks"][-1]["status"], "missing")
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(probe_module.exit_code(report), 0)
        self.assertEqual(probe_module.exit_code(report, True), 1)

    def test_missing_node_does_not_execute_a_shell_pi_wrapper(self):
        shim = self.wrapper('"%dp0%/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js"')
        report = probe_module.build_report(platform_name="nt", lookup=self.lookup({"pi.cmd": str(shim)}), runner=self.runner)
        self.assertFalse(report["passed"])
        self.assertEqual([item["status"] for item in report["checks"]], ["available", "missing", "missing"])
        self.assertEqual(len(self.calls), 1)

    def test_malformed_traversal_unrelated_and_ambiguous_wrappers_are_not_executed(self):
        examples = [
            'echo not a Pi entry',
            '"%dp0%/../node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js"',
            '"%dp0%/node_modules/unrelated-package/dist/cli.js"',
            '"%dp0%/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js" "%dp0%/node_modules/@other/pi-coding-agent/dist/bundle/cli.js"',
        ]
        for text in examples:
            with self.subTest(text=text):
                shim = self.wrapper(text)
                report = probe_module.build_report(platform_name="nt", lookup=self.lookup({"node.exe": "node.exe", "pi.cmd": str(shim)}), runner=self.runner)
                self.assertEqual(report["checks"][-1]["status"], "unresolved-wrapper")
                self.assertFalse(report["passed"])
                self.assertEqual(probe_module.exit_code(report), 0)
        self.assertTrue(all(Path(call[0][0]).stem.lower() != "pi" and not call[0][0].endswith(".cmd") for call in self.calls))

    def test_missing_or_oversized_or_non_utf8_wrapper_is_bounded(self):
        fixtures = [self.folder / "absent.cmd", self.wrapper("x" * (probe_module.MAX_WRAPPER_BYTES + 1)), self.wrapper("valid initially")]
        fixtures[-1].write_bytes(b"\xff")
        for shim in fixtures:
            with self.subTest(path=str(shim)):
                resolved = probe_module.resolve_pi(["node.exe"], platform_name="nt", lookup=self.lookup({"pi.cmd": str(shim)}))
                self.assertEqual(resolved["status"], "unresolved-wrapper")
                self.assertIsNone(resolved["command"])

    def test_missing_referenced_entry_is_not_a_success(self):
        shim = self.wrapper('"%dp0%/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js"', entries=())
        resolved = probe_module.resolve_pi(["node.exe"], platform_name="nt", lookup=self.lookup({"pi.cmd": str(shim)}))
        self.assertEqual(resolved["status"], "unresolved-wrapper")
        self.assertIsNone(resolved["command"])

    def test_nonzero_execution_is_visible_and_fails_without_ci_flag(self):
        def failed(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 7, "", "private diagnostic text is not echoed")
        result = probe_module.probe("pi", ["pi"], runner=failed)
        self.assertEqual(result["status"], "execution-failed")
        self.assertEqual(result["exit_code"], 7)
        report = {"passed": False, "checks": [result]}
        self.assertEqual(probe_module.exit_code(report), 1)
        self.assertNotIn("private diagnostic", json.dumps(result))

    def test_timeout_and_spawn_errors_are_explicit(self):
        for exception, expected in [(subprocess.TimeoutExpired(["pi", "--version"], 10), "timeout"), (OSError("unavailable"), "execution-failed")]:
            with self.subTest(expected=expected):
                def failed(argv, **kwargs):
                    raise exception
                result = probe_module.probe("pi", ["pi"], runner=failed)
                self.assertEqual(result["status"], expected)
                self.assertEqual(probe_module.exit_code({"passed": False, "checks": [result]}), 1)

    def test_empty_or_non_version_output_cannot_be_reported_available(self):
        for output in ["", "Hello", "model started", "1.4.0\nprivate extra"]:
            with self.subTest(output=output):
                result = probe_module.probe("pi", ["pi"], runner=lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, output, ""))
                self.assertEqual(result["status"], "unexpected-output")
                self.assertEqual(probe_module.exit_code({"passed": False, "checks": [result]}), 1)

    def test_no_compiler_package_manager_session_or_provider_invocation(self):
        report = probe_module.build_report(platform_name="posix", lookup=self.lookup({"node": "/tools/node", "pi": "/tools/pi"}), runner=self.runner)
        self.assertTrue(report["passed"])
        self.assertNotIn("tsc", self.lookups)
        self.assertNotIn("npm", self.lookups)
        for argv, kwargs in self.calls:
            self.assertEqual(argv[-1], "--version")
            self.assertNotIn(Path(argv[0]).stem.lower(), {"npm", "npx", "tsc", "cmd", "powershell", "pwsh"})
            self.assertFalse(any(argument in argv for argument in ["--print", "--mode", "rpc", "--model", "install", "login", "-p"]))

    def test_standalone_copy_actual_versions_and_no_workspace_writes(self):
        standalone = self.folder / "standalone"
        standalone.mkdir()
        copied = standalone / "probe_runtime.py"
        shutil.copy2(HELPER, copied)
        before = sorted(str(item.relative_to(standalone)) for item in standalone.rglob("*"))
        result = subprocess.run([sys.executable, "-B", str(copied), "--host", "pi"], cwd=standalone, capture_output=True, text=True, timeout=40)
        (RUN / "actual-stdout.json").write_text(result.stdout, encoding="utf-8")
        (RUN / "actual-stderr.txt").write_text(result.stderr, encoding="utf-8")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        report = json.loads(result.stdout)
        self.assertTrue(report["passed"])
        ACTUAL.update({item["name"]: item["version"] for item in report["checks"]})
        self.assertEqual(len(report["checks"]), 3)
        self.assertEqual(sorted(str(item.relative_to(standalone)) for item in standalone.rglob("*")), before)
        self.assertEqual(hashlib.sha256(HELPER.read_bytes()).hexdigest(), BEFORE)

    def test_missing_cli_default_and_ci_exit_contract(self):
        environment = {**os.environ, "PATH": ""}
        for flags, expected_exit in [([], 0), (["--fail-on-missing"], 1)]:
            result = subprocess.run([sys.executable, "-B", str(HELPER), "--host", "pi", *flags], cwd=self.folder, env=environment, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, expected_exit)
            self.assertEqual(result.stderr, "")
            report = json.loads(result.stdout)
            self.assertFalse(report["passed"])
            self.assertEqual([item["status"] for item in report["checks"]], ["available", "missing", "missing"])


if __name__ == "__main__":
    outcome = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeProbeTests))
    summary = {"passed": outcome.wasSuccessful(), "tests_run": outcome.testsRun,
               "failures": len(outcome.failures), "errors": len(outcome.errors), "helper_sha256": BEFORE,
               "actual_versions": ACTUAL, "artifacts": str(RUN),
               "scope": "Standalone helper, bounded wrapper parsing, explicit failure/CI statuses, safe version-only argv and real installed versions; no extension/session/model/account/configuration operation."}
    (RUN / "result.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
