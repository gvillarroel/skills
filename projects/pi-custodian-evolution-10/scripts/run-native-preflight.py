#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise actual native paired copies with labeled faux decisions before search."""

from __future__ import annotations

import hashlib
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path("C:/Users/villa/dev/.pi/durable/repo-custodian")
AREA = ROOT / "projects/pi-custodian-evolution-10"
REQUEST_ID = "custodian-evo10-preflight-20261025"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_inventory():
    result = {}
    excluded = {"node_modules", ".git", "state", "dist", ".cache", "artifacts", "evolution", "environment.env"}
    for folder in ("src", "prompts", "scripts"):
        for path in (PROJECT / folder).rglob("*"):
            local = path.relative_to(PROJECT)
            if path.is_file() and not any(part in excluded or part.startswith(".env") for part in local.parts):
                result[local.as_posix()] = sha(path)
    for name in ("package.json", "package-lock.json", "tsconfig.json", "config.json", "config.evo10.json", "config.evo10.models.json"):
        result[name] = sha(PROJECT / name)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", choices=["v1", "v2", "v3"], default="v1")
    revision = parser.parse_args().revision
    suffix = "" if revision == "v1" else "-" + revision
    request_id = REQUEST_ID + suffix
    prefix = "evaluation/evo10-preflight" + suffix
    output = AREA / ("artifacts/native-preflight" + suffix)
    output.mkdir(parents=True, exist_ok=False)
    preflight = PROJECT / prefix
    preflight.mkdir(parents=True, exist_ok=False)
    before = source_inventory()
    (output / "source-before.json").write_text(json.dumps(before, indent=2) + "\n")
    for name in ("verifier.mjs", "decision-grader.ts", "worker-benchmark.py", "worker-fixtures.json"):
        shutil.copy2(PROJECT / "evaluation/evo10" / name, preflight / name)
    shutil.copy2(PROJECT / "config.evo10.json", preflight / "config.evo10.json")
    development = AREA / "artifacts/development/decision-cases.json"
    shutil.copy2(development, preflight / "decision-cases.json")
    benchmark = load(development)
    public_fields = {"action", "reasonCodes", "requiredChecks", "missingChecks", "missingEvidence", "claimedOutcome"}
    scripted = {"cases": [
        {key: value for key, value in item["expected"].items() if key in public_fields}
        | {"id": item["id"], "nextAction": "Follow the supplied observations without executing actions in this setup check."}
        for item in benchmark["cases"]
    ]}
    settings = load(PROJECT / "evaluation/evo10/evaluation-settings.json")
    settings.update(mode="faux", enableModelCalls=False, fauxResponse=scripted)
    (preflight / "evaluation-settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    fixture_names = ["evaluation-settings.json", "config.evo10.json", "decision-cases.json", "decision-grader.ts", "worker-benchmark.py", "worker-fixtures.json"]
    request_input = {
        "id": request_id, "agentId": "repo-custodian",
        "goal": "Setup mechanics only: exercise native immutable paired source copies with scripted faux decisions and isolated worker fixtures. No real model quality or release improvement is claimed.",
        "allowedPaths": ["prompts/repo-custodian.md"],
        "verifierPath": prefix + "/verifier.mjs",
        "fixturePaths": [prefix + "/" + name for name in fixture_names],
        "minimumImprovement": 0.01, "timeoutMs": 360000,
    }
    request_path = output / "request-input.json"
    request_path.write_text(json.dumps(request_input, indent=2) + "\n")
    config = PROJECT / "config.evo10.json"
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node is unavailable.")

    def command(action, *arguments):
        args = [node, str(PROJECT / "dist/src/evolve-cli.js"), action, "--config", str(config), *map(str, arguments)]
        result = subprocess.run(args, cwd=PROJECT, capture_output=True, text=True, encoding="utf-8", timeout=800)
        (output / (action + ".stdout.json")).write_text(result.stdout, encoding="utf-8")
        (output / (action + ".stderr.txt")).write_text(result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError("Native " + action + " failed; retained setup receipt must be inspected.")
        return json.loads(result.stdout)

    request = command("request", "--input", request_path)
    prompt = PROJECT / "prompts/repo-custodian.md"
    proposal_input = {
        "requestId": request["id"], "evidenceIds": [request["evidence"][0]["id"]],
        "hypothesis": "A harmless whitespace-only patch should preserve all setup behavior and demonstrate no measured improvement.",
        "decision": "Run only a labeled native-engine preflight, outside the ten real development attempts.",
        "expectedBenefit": "Discover path, fixture and serialization failures before consuming real candidate attempts.",
        "regressionRisks": ["Windows deep-path subprocess behavior may require an evaluator-only correction before development."],
        "changes": [{"path": "prompts/repo-custodian.md", "beforeHash": sha(prompt), "content": prompt.read_bytes().decode("utf-8") + "\n"}],
    }
    proposal_path = output / "proposal-input.json"
    proposal_path.write_text(json.dumps(proposal_input, indent=2) + "\n")
    proposal = command("propose", "--request", request["id"], "--input", proposal_path)
    evaluation = command("evaluate", "--proposal", proposal["id"])
    after = source_inventory()
    (output / "source-after.json").write_text(json.dumps(after, indent=2) + "\n")
    arms = {}
    for name in ("baseline", "candidate"):
        arm = evaluation[name]
        grade = arm.get("verification", {})
        arms[name] = {
            "buildExitCode": arm["build"]["exitCode"],
            "verifierExitCode": arm.get("verifier", {}).get("exitCode"),
            "hardPass": grade.get("passed"), "score": grade.get("score"),
            "cases": len(grade.get("cases", [])),
            "failedCases": [item["id"] for item in grade.get("cases", []) if not item["passed"]],
        }
    success = before == after and all(a["buildExitCode"] == 0 and a["verifierExitCode"] == 0 and a["hardPass"] for a in arms.values())
    report = {"passed": success, "setupMechanicsOnly": True, "countsTowardTenIterations": False,
              "sourceUnchanged": before == after, "requestId": request["id"], "proposalId": proposal["id"],
              "nativeEvaluationPassed": evaluation["passed"],
              "expectedNativeNonImprovement": evaluation["passed"] is False,
              "arms": arms}
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    return 0 if success else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"passed": False, "setupMechanicsOnly": True, "errorCategory": type(error).__name__, "message": str(error)}))
        raise SystemExit(1)
