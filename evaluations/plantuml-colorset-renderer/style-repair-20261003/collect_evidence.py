#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect compact immutable identities and completed release-run gate evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.cohort):
        parser.error("Cohort must use lowercase hyphen-case.")
    cases = read_json(HERE / "cases.json")["cases"]
    runs = []
    for name, case in cases.items():
        for repetition in range(1, case["repetitions"] + 1):
            run_id = f"20261003-plantuml-style-{name}-{args.cohort}-{repetition}"
            run_dir = ROOT / "evaluations/runs" / run_id
            manifest = read_json(run_dir / "run-manifest.json")
            result = read_json(run_dir / "evaluation-result.json")
            event = read_json(run_dir / "event-check.json")
            integrity = read_json(run_dir / "skill-integrity-check.json")
            independent = read_json(run_dir / "independent-validation.json")
            dispatch = read_json(run_dir / "release-dispatch.json")
            command_audit_path = run_dir / "command-audit.json"
            command_audit = read_json(command_audit_path)
            identities = []
            for diagram in independent["diagrams"]:
                source = run_dir / "workspace/input" / f"{diagram['diagram']}.puml"
                identities.append({
                    "diagram": diagram["diagram"], "nativeFamily": diagram["type"],
                    "dimensions": diagram["dimensions"], "sourceSha256": sha256(source),
                    "svgSha256": diagram["svgSha256"], "pngSha256": diagram["pngSha256"],
                    "svgScreenshotSha256": sha256(run_dir / "independent-screenshots" / f"{diagram['diagram']}-svg.png"),
                    "minimumTextContrast": min(item["minimumContrast"] for item in diagram["textChecks"]),
                    "minimumConnectorContrast": min((item["minimumContrast"] for item in diagram["arrowChecks"]), default=None),
                })
            review = run_dir / "direct-visual-review.md"
            runs.append({
                "runId": run_id, "case": name, "repetition": repetition,
                "model": manifest["pi"], "startedAtUtc": result["startedAtUtc"],
                "finishedAtUtc": result["finishedAtUtc"], "durationSeconds": result["durationSeconds"],
                "payload": manifest["skill"], "prompt": manifest["prompt"],
                "localRenderer": dispatch["localRenderer"], "runtimePassed": result["passed"],
                "runtimeGates": result["gates"], "observedModels": event["observedModels"],
                "eventFindings": event["findings"], "payloadIntegrity": integrity,
                "readPaths": [item["path"] for item in event["calls"] if item["tool"] == "read"],
                "traceSummarySha256": sha256(run_dir / "read-surface.json"),
                "commandAudit": {"path": command_audit_path.relative_to(ROOT).as_posix(),
                                 "sha256": sha256(command_audit_path), "passed": command_audit["passed"],
                                 "isolationPassed": command_audit["isolationPassed"],
                                 "strictRuntimePassed": command_audit["strictRuntimePassed"],
                                 "sourceAssessment": command_audit.get("sourceAssessment"),
                                 "observations": command_audit.get("observations", []),
                                 "findings": command_audit.get("findings", [])},
                "independentPassed": independent["passed"], "independentFindings": independent["findings"],
                "directReview": {"path": review.relative_to(ROOT).as_posix(), "sha256": sha256(review)},
                "diagrams": identities,
            })
    payloads = sorted({run["payload"]["payloadSha256"] for run in runs})
    evidence = {"schemaVersion": 1, "skill": "plantuml-colorset-renderer", "cohort": args.cohort,
                "runCount": len(runs), "diagramCount": sum(len(run["diagrams"]) for run in runs),
                "consistentPayload": len(payloads) == 1, "payloadSha256": payloads, "runs": runs}
    output = HERE / f"{args.cohort}-artifact-identities.json"
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": output.relative_to(ROOT).as_posix(), "runCount": len(runs),
                      "diagramCount": evidence["diagramCount"], "consistentPayload": evidence["consistentPayload"]}))
    return int(not evidence["consistentPayload"])


if __name__ == "__main__":
    raise SystemExit(main())
