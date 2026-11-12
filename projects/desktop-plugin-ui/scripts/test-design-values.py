#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise the standalone design-values CLI without accounts or network."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "skills/desktop-plugin-ui"
HELPER = BUNDLE / "scripts/design_values.py"
ARTIFACTS = REPO / "projects/desktop-plugin-ui/artifacts/design-values-tests-20261025"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
if not ARTIFACTS.resolve().is_relative_to(REPO.resolve()):
    raise RuntimeError("Temporary test workspaces must stay inside the authorized repository")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): digest(path) for path in sorted(root.rglob("*")) if path.is_file()}


def invoke(*arguments: str, helper: Path = HELPER, cwd: Path | None = None) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run([sys.executable, "-I", "-B", str(helper), *arguments], cwd=cwd or REPO,
                            capture_output=True, text=True, encoding="utf-8", timeout=15,
                            env={**os.environ, "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    if result.stderr:
        raise AssertionError(f"Unexpected diagnostic outside JSON: {result.stderr}")
    return result, json.loads(result.stdout)


def expected_paths(palette: str) -> set[str]:
    paths = {"typography.primary", "iconography.primary"}
    for group, names in {
        "colors.brand": ("primary", "neutral"),
        "colors.gray": tuple(str(value) for value in range(100, 1000, 100)),
        "interface.text": ("primary", "secondary", "inverse"),
        "interface.link": ("default", "hover"),
        "interface.background": ("page", "surface", "footer", "overlay"),
        "interface.state": ("disabled", "focus", "selected"),
        "interface.border": ("default", "light", "dark"),
    }.items():
        paths.update(f"{group}.{name}" for name in names)
    if palette == "colorset1":
        for group, names in {"colors.red": ("base", "dark", "light", "status"),
                             "colors.neutral": ("black", "white", "gray"),
                             "interface.action": ("primary", "primary_hover", "destructive")}.items():
            paths.update(f"{group}.{name}" for name in names)
        feedback = ("critical", "neutral")
    else:
        paths.update(f"colors.primary.{name}" for name in ("red", "orange", "yellow", "green", "blue", "purple", "black", "white", "gray"))
        paths.update(f"colors.{group}.{name}" for group in ("interaction", "highlight") for name in ("red", "orange", "yellow", "green", "blue", "purple"))
        paths.update(f"colors.status.{name}" for name in ("error", "warning", "caution", "success", "information", "special"))
        paths.update(f"interface.action.{name}" for name in ("primary", "primary_hover", "secondary", "secondary_hover", "positive", "destructive"))
        feedback = ("error", "warning", "caution", "success", "information", "special")
    paths.update(f"interface.feedback.{kind}.{role}" for kind in feedback for role in ("text", "background"))
    return paths


class DesignValuesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch_context = tempfile.TemporaryDirectory(prefix="isolated-", dir=ARTIFACTS)
        cls.scratch = Path(cls.scratch_context.name).resolve()
        if not cls.scratch.is_relative_to(ARTIFACTS.resolve()):
            raise RuntimeError("Resolved test workspace is outside the intended artifacts directory")
        cls.detached = cls.scratch / "standalone bundle"
        (cls.detached / "scripts").mkdir(parents=True)
        (cls.detached / "assets/palettes").mkdir(parents=True)
        shutil.copy2(HELPER, cls.detached / "scripts/design_values.py")
        for filename in ("colorset1.yml", "colorset2.yaml"):
            shutil.copy2(BUNDLE / "assets/palettes" / filename, cls.detached / "assets/palettes" / filename)
        cls.relocated_helper = cls.detached / "scripts/design_values.py"
        cls.before = snapshot(cls.detached)
        cls.caller = cls.scratch / "caller Ω without repository"
        cls.caller.mkdir()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.scratch_context.cleanup()

    def finding(self, arguments: list[str], code: str, *, helper: Path = HELPER) -> None:
        for strict in (False, True):
            with self.subTest(arguments=arguments, strict=strict):
                result, report = invoke(*arguments, *( ["--fail-on-findings"] if strict else []), helper=helper)
                self.assertEqual(result.returncode, 1 if strict else 0)
                self.assertFalse(report["passed"])
                self.assertEqual(report["findings"][0]["code"], code)
                self.assertIsInstance(report["findings"][0]["message"], str)

    def test_complete_both_palette_catalogs_and_types(self) -> None:
        for palette, count, unique_colors in (("colorset1", 42, 17), ("colorset2", 73, 37)):
            with self.subTest(palette=palette):
                result, report = invoke("--palette", palette, "--list-tokens")
                self.assertEqual(result.returncode, 0)
                self.assertTrue(report["passed"])
                self.assertEqual(report["token_count"], count)
                self.assertEqual(report["unique_color_count"], unique_colors)
                self.assertEqual({row["token_path"] for row in report["tokens"]}, expected_paths(palette))
                self.assertEqual(sum(row["value_type"] == "string" for row in report["tokens"]), 2)
                for row in report["tokens"]:
                    self.assertEqual(row["value_path"], row["token_path"] + ".value")
                    self.assertIsInstance(row["value"], str)
                    self.assertIsInstance(row["use"], str)
                    self.assertEqual(row["value_type"], "string" if row["token_path"].split(".")[0] in ("typography", "iconography") else "color")
                filename = "colorset1.yml" if palette == "colorset1" else "colorset2.yaml"
                self.assertEqual(report["source"], f"assets/palettes/{filename}")
                self.assertEqual(report["source_sha256"], digest(BUNDLE / "assets/palettes" / filename))

    def test_every_token_resolves_with_and_without_value(self) -> None:
        for palette in ("colorset1", "colorset2"):
            _, listed = invoke("--palette", palette, "--list-tokens")
            command = ["--palette", palette]
            for row in listed["tokens"]:
                command.extend(("--resolve", row["token_path"], "--resolve", row["value_path"]))
            result, report = invoke(*command)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(report["passed"])
            self.assertEqual(len(report["resolved"]), 2 * len(listed["tokens"]))
            for index, row in enumerate(listed["tokens"]):
                for resolved in report["resolved"][index * 2:index * 2 + 2]:
                    self.assertEqual({key: value for key, value in resolved.items() if key != "requested_path"}, row)

    def test_default_palette_and_source_path_example(self) -> None:
        result, report = invoke("--resolve", "colors.red.status", "--resolve", "colors.red.status.value")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["palette"], "colorset1")
        self.assertEqual([row["value"] for row in report["resolved"]], ["#e8002a", "#e8002a"])
        self.assertEqual([row["value_path"] for row in report["resolved"]], ["colors.red.status.value"] * 2)

    def test_thirteen_frozen_contrast_pairs(self) -> None:
        # Constants retained from the independently reviewed design study.
        pairs = [
            ("#cfcfcf", "#ffffff", 1.5579550563651179, 3.0, False),
            ("#9c9c9c", "#ffffff", 2.7454458936977137, 3.0, False),
            ("#e8002a", "#ffccd5", 3.326162240606473, 4.5, False),
            ("#333e48", "#ffffff", 10.918238644424665, 4.5, True),
            ("#696969", "#ffffff", 5.489814557409947, 4.5, True),
            ("#ffffff", "#9e1b32", 7.9046884551695875, 4.5, True),
            ("#ffffff", "#6d1222", 11.932745997117243, 4.5, True),
            ("#333e48", "#ffccd5", 7.720736540005823, 4.5, True),
            ("#9e1b32", "#ffccd5", 5.589730997898148, 4.5, True),
            ("#ffffff", "#007298", 5.4399561950875235, 4.5, True),
            ("#ffffff", "#45842a", 4.578174721021005, 4.5, True),
            ("#9e1b32", "#ffffff", 7.9046884551695875, 3.0, True),
            ("#007298", "#ffffff", 5.4399561950875235, 3.0, True),
        ]
        command = ["--palette", "colorset2"]
        for foreground, background, *_ in pairs:
            command.extend(("--contrast", foreground, background))
        result, report = invoke(*command)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(report["passed"])
        self.assertEqual(len(report["contrast"]), 13)
        for actual, (front, back, expected, threshold, reaches) in zip(report["contrast"], pairs):
            with self.subTest(foreground=front, background=back):
                self.assertAlmostEqual(actual["ratio_unrounded"], expected, delta=1e-12)
                requirement = "ordinary_text" if threshold == 4.5 else "essential_non_text"
                self.assertEqual(actual["requirements"][requirement]["passes"], reaches)

    def test_unrounded_threshold_failure_does_not_become_pass(self) -> None:
        result, report = invoke("--palette", "colorset2", "--contrast", "#36b300", "#4f4f4f", "--fail-on-findings")
        self.assertEqual(result.returncode, 0)  # Valid measurement; requirements are separate.
        self.assertTrue(report["passed"])
        measurement = report["contrast"][0]
        self.assertAlmostEqual(measurement["ratio_unrounded"], 2.966318252496338, delta=1e-12)
        self.assertEqual(round(measurement["ratio_unrounded"], 1), 3.0)
        self.assertFalse(measurement["requirements"]["large_text"]["passes"])
        self.assertFalse(measurement["requirements"]["essential_non_text"]["passes"])

    def test_contrast_extremes_symmetry_and_case_normalization(self) -> None:
        _, report = invoke("--contrast", "#000000", "#FFFFFF", "--contrast", "#ffffff", "#000000", "--contrast", "#333E48", "#333e48")
        self.assertEqual([row["ratio_unrounded"] for row in report["contrast"]], [21.0, 21.0, 1.0])
        self.assertEqual(report["contrast"][0]["input_background"], "#FFFFFF")
        self.assertEqual(report["contrast"][0]["background"], "#ffffff")
        self.assertEqual(report["contrast"][2]["foreground"], "#333e48")

    def test_unknown_paths_never_gain_a_missing_prefix(self) -> None:
        for value in ("red.status", "red.status.value", "interface.text", "interface.text.primary.use", "metadata.name", "colors.red.status.value.value", ".colors.red.status", "colors..red.status", "colors/red/status", " colors.red.status", "colors.red.STATUS", ""):
            self.finding(["--resolve", value], "unknown_token_path")

    def test_palette_selection_is_exact_and_cannot_traverse(self) -> None:
        for value in ("colorset3", "ColorSet1", "../colorset1", "colorset1.yml", ""):
            self.finding(["--palette", value, "--list-tokens"], "unknown_palette")

    def test_unlisted_colors_are_not_repaired_or_cross_palette(self) -> None:
        for value in ("#000001", "#007298"):
            self.finding(["--palette", "colorset1", "--contrast", value, "#ffffff"], "unlisted_color")
        result, report = invoke("--palette", "colorset2", "--contrast", "#007298", "#ffffff")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(report["passed"])

    def test_malformed_hex_is_rejected_in_either_position(self) -> None:
        for value in ("#fff", "#ffffff00", "ffffff", "white", "#gggggg", " #ffffff", "#ffffff ", "#ffffff\n"):
            self.finding(["--contrast", value, "#ffffff"], "invalid_hex")
            self.finding(["--contrast", "#ffffff", value], "invalid_hex")

    def test_json_unicode_and_no_raw_traceback(self) -> None:
        value = "colors.Ω.💥\nquoted\"path"
        result, report = invoke("--resolve", value)
        self.assertEqual(result.returncode, 0)
        self.assertFalse(report["passed"])
        self.assertEqual(report["findings"][0]["requested_path"], value)
        self.assertNotIn("Traceback", result.stdout)
        self.assertIn("exact dot-separated source token path", report["findings"][0]["message"])

    def test_invalid_command_usage_remains_nonzero_json(self) -> None:
        for arguments in ([], ["--unknown-option"], ["--resolve"], ["--contrast", "#ffffff"], ["--pal", "colorset1", "--list-tokens"]):
            result, report = invoke(*arguments)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(report["passed"])
            self.assertEqual(report["findings"][0]["code"], "invalid_arguments")

    def test_relocated_bundle_works_without_repository_or_dependencies(self) -> None:
        result, report = invoke("--palette", "colorset2", "--resolve", "colors.status.success", "--contrast", "#007298", "#ffffff", "--list-tokens", helper=self.relocated_helper, cwd=self.caller)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(report["passed"])
        self.assertEqual(report["resolved"][0]["value"], "#36b300")
        self.assertEqual(report["token_count"], 73)
        self.assertNotIn(str(REPO), result.stdout)
        self.assertEqual(snapshot(self.detached), self.before)

    def test_all_bundle_files_remain_unchanged_on_success_and_findings(self) -> None:
        before = snapshot(self.detached)
        for arguments in (["--list-tokens"], ["--resolve", "red.status"], ["--contrast", "#000001", "#ffffff", "--fail-on-findings"]):
            invoke(*arguments, helper=self.relocated_helper, cwd=self.caller)
        self.assertEqual(snapshot(self.detached), before)
        self.assertFalse(any(self.detached.rglob("__pycache__")))

    def test_controlled_yaml_parser_fails_closed(self) -> None:
        for name, text in {
            "implicit-number": 'colors:\n  red:\n    value: 123\n',
            "implicit-boolean": 'colors:\n  red:\n    value: true\n',
            "duplicate-key": 'colors:\n  red:\n    value: "#9e1b32"\n    value: "#ffffff"\n',
            "alias": 'colors:\n  red:\n    value: *unknown\n',
            "sequence": 'colors:\n  - value: "#9e1b32"\n',
            "tab": 'colors:\n\tred:\n    value: "#9e1b32"\n',
            "odd-indent": 'colors:\n   red:\n    value: "#9e1b32"\n',
            "skip-level": 'colors:\n    red:\n      value: "#9e1b32"\n',
            "under-scalar": 'colors: "not a mapping"\n  red: "#9e1b32"\n',
            "color-shorthand": 'colors:\n  red:\n    value: "#fff"\n',
            "unterminated-string": 'colors:\n  red:\n    value: "#9e1b32\n',
        }.items():
            with self.subTest(source=name):
                copy = self.scratch / name
                (copy / "scripts").mkdir(parents=True)
                (copy / "assets/palettes").mkdir(parents=True)
                shutil.copy2(HELPER, copy / "scripts/design_values.py")
                (copy / "assets/palettes/colorset1.yml").write_text(text, encoding="utf-8")
                self.finding(["--list-tokens"], "invalid_palette_source", helper=copy / "scripts/design_values.py")

    def test_missing_source_has_a_bounded_json_diagnostic(self) -> None:
        copy = self.scratch / "missing-source"
        (copy / "scripts").mkdir(parents=True)
        shutil.copy2(HELPER, copy / "scripts/design_values.py")
        self.finding(["--list-tokens"], "palette_read_failed", helper=copy / "scripts/design_values.py")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write a compact JSON test result inside the project artifacts directory.")
    args = parser.parse_args()
    if args.output and not args.output.resolve().is_relative_to(ARTIFACTS.resolve()):
        parser.error("--output must remain inside projects/desktop-plugin-ui/artifacts/design-values-tests-20261025")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DesignValuesTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"passed": result.wasSuccessful(), "tests_run": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors),
              "helper_sha256": digest(HELPER), "test_sha256": digest(Path(__file__)),
              "scope": "Local deterministic tests, exact palette/token contracts, CLI diagnostics, immutable relocated bundle and no assistant/account/network dependency."}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
