#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain final repository presentation gates and their actual command results."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/solid-colorset-style/artifacts"
COMMANDS = [
    "scripts/validate-pattern-ids.py",
    "scripts/validate-skills.py",
    "scripts/test-skill-independence.py",
    "scripts/check-repo-payload.py",
    "scripts/test-colorsets.py",
    "scripts/test-pages-output.py",
    "scripts/test-pi-eval-harness.py",
    "scripts/test-bundle-validation.py",
    "skills/repository-reviewer-creator/scripts/test_skill_authoring.py",
    "skills/repository-reviewer-creator/scripts/test_validate_reviewer.py",
    "scripts/validate-diagram-type-coverage.py",
    "scripts/validate-colorsets.py",
]


def run(script):
    command = ["uv", "run", "--script", script]
    if "diagram-type" in script:
        command.append("--disable-mermaid-browser-sandbox")
    if script.endswith("validate-colorsets.py"):
        command += ["--report", "projects/solid-colorset-style/artifacts/reviews/colorset-audit-final.json"]
    environment = os.environ.copy()
    temporary = ART / "temp"
    temporary.mkdir(parents=True, exist_ok=True)
    environment.update(TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary))
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True,
                            text=True, encoding="utf-8", errors="replace")
    log = ART / "reviews" / (Path(script).stem + "-final.log")
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    return {"script": script, "command": command, "startedAtUtc": started,
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "exitCode": result.returncode, "passed": result.returncode == 0,
            "log": log.relative_to(ROOT).as_posix(),
            "output": (result.stdout + result.stderr).strip()}


def main():
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(run, COMMANDS))
    report = {"date": "2026-10-03", "passed": all(row["passed"] for row in results), "checks": results}
    destination = ROOT / "evaluations/solid-colorset-style/final-gates-20261003.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checkCount": len(results),
                      "failures": [row for row in results if not row["passed"]]}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
