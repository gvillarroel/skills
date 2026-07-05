#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.45.0"]
# ///

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Metro tonal, composition, rendered-frame, and mute-test audits as one reusable suite."
    )
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--source-package", type=Path)
    parser.add_argument("--style-output", type=Path, help="metro-style-audit.json path.")
    parser.add_argument("--composition-output", type=Path, help="metro-composition-audit.json path.")
    parser.add_argument("--rendered-frame-output", type=Path, help="metro-rendered-frame-audit.json path.")
    parser.add_argument("--mute-test-output", type=Path, help="metro-mute-test-audit.json path.")
    parser.add_argument("--output", type=Path, help="Optional suite JSON report path.")
    parser.add_argument("--allow-colorset2", action="store_true")
    parser.add_argument("--install-browser", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--audit-timeout-seconds", type=int, default=240)
    parser.add_argument(
        "--mute-test-samples",
        type=int,
        default=4,
        help=(
            "Number of hidden-text samples for suite mute-test runs. "
            "The default keeps long-video suites bounded while still requiring all three adjacent pairs to change."
        ),
    )
    return parser.parse_args()


def fill_default_outputs(args: argparse.Namespace) -> None:
    if args.output:
        args.style_output = args.style_output or args.output.parent / "metro-style-audit.json"
        args.composition_output = args.composition_output or args.output.parent / "metro-composition-audit.json"
        args.rendered_frame_output = args.rendered_frame_output or args.output.parent / "metro-rendered-frame-audit.json"
        args.mute_test_output = args.mute_test_output or args.output.parent / "metro-mute-test-audit.json"
    if not all([args.style_output, args.composition_output, args.rendered_frame_output, args.mute_test_output]):
        raise ValueError(
            "Metro audit suite requires style, composition, rendered-frame, and mute-test output paths; "
            "pass --output to derive the four default child reports."
        )


def audit_command(script_name: str, args: list[str]) -> list[str]:
    return [sys.executable, str(SCRIPT_DIR / script_name), *args]


def uv_audit_command(script_name: str, args: list[str]) -> list[str] | None:
    uv = shutil.which("uv")
    if not uv:
        return None
    return [uv, "run", "--script", str(SCRIPT_DIR / script_name), *args]


def read_json(path: Path | None) -> dict[str, Any] | None:
    if not path or not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"manifestReadError": str(exc)}
    return data if isinstance(data, dict) else {"manifestReadError": "Manifest root is not an object."}


def read_tail(path: Path, limit: int = 1000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[-limit:]
    except OSError:
        return ""


def run_child_command(cmd: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    temp_dir = Path(tempfile.mkdtemp(prefix="metro-audit-child-"))
    stdout_path = temp_dir / "stdout.txt"
    stderr_path = temp_dir / "stderr.txt"
    try:
        with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout_file, stderr_path.open(
            "w", encoding="utf-8", errors="replace"
        ) as stderr_file:
            try:
                result = subprocess.run(
                    cmd,
                    text=True,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    check=False,
                    timeout=timeout_seconds,
                )
            except subprocess.TimeoutExpired as exc:
                exc.stdout = read_tail(stdout_path)
                exc.stderr = read_tail(stderr_path)
                raise
        result.stdout = read_tail(stdout_path)
        result.stderr = read_tail(stderr_path)
        return result
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_audit(
    *,
    script_name: str,
    code: str,
    output: Path | None,
    base_args: argparse.Namespace,
    extra_args: list[str] | None = None,
) -> dict[str, Any] | None:
    if not output:
        return None
    args = [
        "--html",
        base_args.html.as_posix(),
        "--output",
        output.as_posix(),
    ]
    if base_args.source_package:
        args.extend(["--source-package", base_args.source_package.as_posix()])
    if extra_args:
        args.extend(extra_args)
    cmd = audit_command(script_name, args)
    attempts = 2 if code in {"metro-rendered-frame", "metro-mute-test"} else 1
    timed_out_once = False
    retried_after_failure = False
    manifest: dict[str, Any] | None = None
    for attempt in range(attempts):
        try:
            result = run_child_command(cmd, base_args.audit_timeout_seconds)
            manifest = read_json(output)
            passed = result.returncode == 0 and bool(manifest and manifest.get("passed") is True)
            if passed or attempt + 1 >= attempts:
                break
            retried_after_failure = True
        except subprocess.TimeoutExpired as exc:
            timed_out_once = True
            if attempt + 1 < attempts:
                continue
            fallback_cmd = uv_audit_command(script_name, args)
            if fallback_cmd and code in {"metro-rendered-frame", "metro-mute-test"}:
                try:
                    result = run_child_command(fallback_cmd, base_args.audit_timeout_seconds)
                    manifest = read_json(output)
                    passed = result.returncode == 0 and bool(manifest and manifest.get("passed") is True)
                    if passed:
                        return {
                            "ran": True,
                            "code": code,
                            "manifest": output.as_posix(),
                            "command": fallback_cmd,
                            "returnCode": result.returncode,
                            "attempts": attempt + 2,
                            "retryAfterTimeout": True,
                            "timeoutFallback": "uv-run-script",
                            "stdoutTail": result.stdout[-1000:],
                            "stderrTail": result.stderr[-1000:],
                            "passed": True,
                            "manifestPassed": manifest.get("passed") if manifest else None,
                            "findings": manifest.get("findings") if manifest else None,
                        }
                except subprocess.TimeoutExpired:
                    pass
            if output:
                timeout_manifest = {
                    "passed": False,
                    "html": base_args.html.as_posix(),
                    "sourcePackage": base_args.source_package.as_posix() if base_args.source_package else None,
                    "findings": [
                        {
                            "code": f"{code}-timeout",
                            "message": f"{script_name} exceeded {base_args.audit_timeout_seconds} seconds.",
                        }
                    ],
                    "timedOut": True,
                    "attempts": attempt + 1,
                }
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(timeout_manifest, indent=2), encoding="utf-8")
            return {
                "ran": True,
                "code": code,
                "manifest": output.as_posix(),
                "command": cmd,
                "returnCode": None,
                "stdoutTail": (exc.stdout or "")[-1000:] if isinstance(exc.stdout, str) else "",
                "stderrTail": (exc.stderr or "")[-1000:] if isinstance(exc.stderr, str) else "",
                "timedOut": True,
                "attempts": attempt + 1,
                "passed": False,
            }
    else:
        raise RuntimeError("unreachable audit retry state")
    report: dict[str, Any] = {
        "ran": True,
        "code": code,
        "manifest": output.as_posix(),
        "command": cmd,
        "returnCode": result.returncode,
        "attempts": 2 if (timed_out_once or retried_after_failure) else 1,
        "retryAfterTimeout": timed_out_once,
        "retryAfterFailure": retried_after_failure,
        "stdoutTail": result.stdout[-1000:],
        "stderrTail": result.stderr[-1000:],
        "passed": result.returncode == 0 and bool(manifest and manifest.get("passed") is True),
    }
    if manifest is None:
        report["manifestMissing"] = True
        report["passed"] = False
    else:
        report["manifestPassed"] = manifest.get("passed")
        report["findings"] = manifest.get("findings")
        if "manifestReadError" in manifest:
            report["manifestReadError"] = manifest["manifestReadError"]
            report["passed"] = False
    return report


def append_failure(findings: list[dict[str, str]], report: dict[str, Any] | None, code: str) -> None:
    if not report or report.get("passed") is True:
        return
    findings.append(
        {
            "code": f"{code}-failed",
            "path": str(report.get("manifest") or ""),
            "message": f"{code} audit failed or did not write a passing manifest.",
        }
    )


def main() -> int:
    args = parse_args()
    fill_default_outputs(args)
    if args.mute_test_samples < 4:
        raise ValueError("--mute-test-samples must be at least 4 so the three hidden changing-pair gate remains meaningful.")

    rendered_args: list[str] = []
    if not args.install_browser:
        rendered_args.append("--no-install-browser")
    mute_test_args = [*rendered_args, "--samples", str(args.mute_test_samples)]
    style_args = ["--allow-colorset2"] if args.allow_colorset2 else []
    style = run_audit(
        script_name="audit_metro_tonal_style.py",
        code="metro-style",
        output=args.style_output,
        base_args=args,
        extra_args=style_args,
    )
    composition = run_audit(
        script_name="audit_metro_composition.py",
        code="metro-composition",
        output=args.composition_output,
        base_args=args,
    )
    rendered = run_audit(
        script_name="audit_metro_rendered_frames.py",
        code="metro-rendered-frame",
        output=args.rendered_frame_output,
        base_args=args,
        extra_args=rendered_args,
    )
    mute_test = run_audit(
        script_name="audit_metro_mute_test.py",
        code="metro-mute-test",
        output=args.mute_test_output,
        base_args=args,
        extra_args=mute_test_args,
    )

    findings: list[dict[str, str]] = []
    append_failure(findings, style, "metro-style")
    append_failure(findings, composition, "metro-composition")
    append_failure(findings, rendered, "metro-rendered-frame")
    append_failure(findings, mute_test, "metro-mute-test")
    report = {
        "passed": not findings,
        "html": args.html.as_posix(),
        "sourcePackage": args.source_package.as_posix() if args.source_package else None,
        "styleAudit": style,
        "compositionAudit": composition,
        "renderedFrameAudit": rendered,
        "muteTestAudit": mute_test,
        "muteTestSamples": args.mute_test_samples,
        "findings": findings,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"run_metro_audit_suite.py: {exc}", file=sys.stderr)
        raise SystemExit(2)
