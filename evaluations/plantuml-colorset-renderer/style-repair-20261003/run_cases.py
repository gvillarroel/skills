#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run frozen PlantUML style-release cases with exact isolated artifact gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SKILL = "plantuml-colorset-renderer"


def installed_tool_preflight(bin_dir: Path, environment: dict[str, str]) -> dict:
    """Prove bare Bash lookup and the Python renderer's normal CLI lookup."""
    python_cli = shutil.which("plantuml", path=environment["PATH"])
    if not python_cli:
        raise ValueError("The Python renderer cannot discover the local plantuml command.")
    bash_candidates = [Path(environment.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"]
    if environment.get("ProgramFiles(x86)"):
        bash_candidates.append(Path(environment["ProgramFiles(x86)"]) / "Git/bin/bash.exe")
    bash = next((path for path in bash_candidates if path.is_file()), None)
    if bash is None:
        raise ValueError("The evaluator's Pi-compatible Git Bash shell is unavailable.")
    checks = []
    for name, command in [
        ("pythonCliLookup", [python_cli, "-version"]),
        ("bareBashCommand", [str(bash), "-c", "plantuml -version"]),
    ]:
        process = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True,
                                 text=True, encoding="utf-8", errors="replace", check=False)
        checks.append({"name": name, "command": command, "exitCode": process.returncode,
                       "stdout": process.stdout, "stderr": process.stderr})
        if process.returncode or "PlantUML version 1.2026.6" not in process.stdout:
            raise ValueError(f"The local PlantUML 1.2026.6 {name} preflight failed: {process.stderr}")
    jar = ROOT / "projects/plantuml-colorset-renderer/artifacts/tools/plantuml-1.2026.6.jar"
    return {"version": checks[0]["stdout"].splitlines()[0],
            "jarSha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
            "cmdSha256": hashlib.sha256((bin_dir / "plantuml.cmd").read_bytes()).hexdigest(),
            "bashShimSha256": hashlib.sha256((bin_dir / "plantuml").read_bytes()).hexdigest(),
            "checks": checks}


def expected_outputs(case: dict) -> list[str]:
    outputs = ["render-report.json", "validation.json", "review.md"]
    for name in case["fixtures"]:
        outputs.extend([
            f"input/{name}.puml",
            f"rendered/svg/{name}.svg",
            f"rendered/png/{name}.png",
        ])
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=["baseline", "boundary", "generalization"], required=True)
    parser.add_argument("--cohort", required=True, help="New retained cohort label; never reuse a run workspace.")
    parser.add_argument("--plantuml-bin", type=Path, default=ROOT / "projects/visual-asset-composition/artifacts/tools")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--tool-preflight-only", action="store_true", help="Check Bash and Python CLI lookup without creating a Pi workspace.")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.cohort):
        parser.error("Cohort must use lowercase hyphen-case.")
    definitions = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    case = definitions["cases"][args.case]
    environment = dict(os.environ)
    environment["PATH"] = str(args.plantuml_bin.resolve()) + os.pathsep + environment["PATH"]
    tool = None
    if not args.dry_run:
        try:
            tool = installed_tool_preflight(args.plantuml_bin.resolve(), environment)
        except (ValueError, OSError) as error:
            parser.error(str(error))
        preflight_path = HERE / f"tool-preflight-{args.cohort}-{args.case}.json"
        preflight_path.write_text(json.dumps(tool, indent=2) + "\n", encoding="utf-8")
    if args.tool_preflight_only:
        if args.dry_run:
            parser.error("--tool-preflight-only cannot be combined with --dry-run.")
        print(json.dumps({"passed": True, "preflight": preflight_path.relative_to(ROOT).as_posix()}))
        return 0
    results = []
    for repetition in range(1, case["repetitions"] + 1):
        run_id = f"20261003-plantuml-style-{args.case}-{args.cohort}-{repetition}"
        command = [
            "uv", "run", "--script", "scripts/run-pi-skill-eval.py", SKILL,
            "--prompt-file", (HERE / f"{args.case}.md").relative_to(ROOT).as_posix(),
            "--model", definitions["model"], "--thinking", definitions["thinking"],
            "--profile", definitions["profile"], "--mode", "json", "--strict",
            "--run-id", run_id, "--timeout-seconds", str(args.timeout_seconds),
        ]
        if case["requireExactCommand"]:
            command.append("--require-exact-command-from-prompt")
        for output in expected_outputs(case):
            command.extend(["--expect-output", output])
        count = len(case["fixtures"])
        fields = {
            "render-report.json::ok": True,
            "render-report.json::colorset": case["colorset"],
            "render-report.json::engine": "cli",
            "render-report.json::sourceDiagramCount": count,
            "render-report.json::renderedDiagramCount": count,
            "render-report.json::renderedOutputCount": count * 2,
            "render-report.json::failedDiagramCount": 0,
            "validation.json::ok": True,
            "validation.json::checkedDiagramCount": count,
        }
        for key, value in fields.items():
            encoded = json.dumps(value) if not isinstance(value, str) else value
            command.extend(["--expect-output-json-field", f"{key}={encoded}"])
        row = {"runId": run_id, "case": args.case, "repetition": repetition, "command": command}
        print(json.dumps(row), flush=True)
        if args.dry_run:
            continue
        process = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        run_dir = ROOT / "evaluations/runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "dispatch-log.txt").write_text(process.stdout + "\n" + process.stderr, encoding="utf-8")
        row["exitCode"] = process.returncode
        row["localRenderer"] = tool
        row["promptSha256"] = hashlib.sha256((HERE / f"{args.case}.md").read_bytes()).hexdigest()
        results.append(row)
        (run_dir / "release-dispatch.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"runId": run_id, "exitCode": process.returncode}), flush=True)
    return int(any(row["exitCode"] for row in results))


if __name__ == "__main__":
    raise SystemExit(main())
