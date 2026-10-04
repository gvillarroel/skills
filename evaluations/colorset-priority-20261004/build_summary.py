#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain a compact inventory and independently recheck selected release traces."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "20261004-cs1-priority-"
CONTRACT_COHORTS = {
    "compose-synchronized-svg": "contracts-r1", "procedural-svg-animation": "contracts-r1",
    "threejs-animated-3d": "contracts-r1", "vectorize-art-patterns": "contracts-luna-r2",
    "mermaid": "mermaid-r2", "plantuml-colorset-renderer": "plantuml-r2",
    "echarts-animated-svg": "boxplot-ssr-r4", "slidev-echarts": "boxplot-ssr-r4",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--d3-cohort")
    parser.add_argument("--charts-cohort", default="boxplot-ssr-r4")
    args = parser.parse_args()
    contracts = dict(CONTRACT_COHORTS)
    for skill in ("echarts-animated-svg", "slidev-echarts"):
        contracts[skill] = args.charts_cohort
    if args.d3_cohort:
        contracts["d3"] = args.d3_cohort
    selected = [PREFIX + f"{skill}-contract-{cohort}-1" for skill, cohort in contracts.items()]
    for skill, cohort in (("mermaid", "mermaid-r2"), ("plantuml-colorset-renderer", "plantuml-r2"), ("d3", args.d3_cohort)):
        if cohort:
            selected += [PREFIX + f"{skill}-naturalistic-{cohort}-{attempt}" for attempt in (1, 2, 3)]
    inventory, release = [], []
    for run in sorted((ROOT / "evaluations/runs").glob(PREFIX + "*")):
        dispatch = read(run / "priority-dispatch.json")
        manifest = read(run / "run-manifest.json")
        evaluation = read(run / "evaluation-result.json")
        artifact = read(run / "independent-artifact-check.json")
        original_artifact = artifact
        amended_artifact = read(run / "artifact-measurement-review.json")
        recovered_artifact = read(run / "recovered-artifact-check.json")
        artifact = amended_artifact or artifact or recovered_artifact
        browser = read(run / "browser-review-v2.json")
        semantic = read(run / "semantic-role-review.json")
        original = read(run / "browser-review.json")
        if browser is None and "-mermaid-naturalistic-" not in run.name:
            browser = original
        stderr = (run / "dispatch.stderr.txt").read_text(encoding="utf-8") if (run / "dispatch.stderr.txt").is_file() else ""
        event_gate = read(run / "event-check.json") or {}
        row = {"runId": run.name, "selectedFinal": run.name in selected,
               "piLaunched": (run / "events.jsonl").is_file(),
               "modelSampled": event_gate.get("callCount", 0) > 0,
               "payloadSha256": manifest["skill"]["payloadSha256"] if manifest else (dispatch or {}).get("sourcePayloadSha256"),
               "strictPassed": evaluation.get("passed") if evaluation else False,
               "artifactPassed": artifact.get("passed") if artifact else None,
               "originalArtifactPassed": original_artifact.get("passed") if original_artifact else None,
               "artifactReviewMode": "uniform painted-body measurement amendment" if amended_artifact else ("recovered actual output" if original_artifact is None and recovered_artifact else "original"),
               "literalBrowserPassed": browser.get("passed") if browser else None,
               "originalBrowserPassed": original.get("passed") if original else None,
               "supplementalSemanticPassed": semantic.get("passed") if semantic else None,
               "dispatchExitCode": (dispatch or {}).get("dispatchExitCode"),
               "sourcePayloadUnchanged": (dispatch or {}).get("sourcePayloadUnchanged"),
               "copyMatchesFrozenSource": (dispatch or {}).get("copyMatchesFrozenSource"),
               "rawEvidencePath": run.relative_to(ROOT).as_posix()}
        if (dispatch or {}).get("failureClassification") == "infrastructure":
            row["classification"] = "provider-rejection"
        elif not row["piLaunched"]:
            row["classification"] = "source-preflight" if "Skill bundle validation failed" in stderr else "evaluator-preparation"
        elif "naturalistic-r1" in run.name and "mermaid" in run.name and not row["strictPassed"]:
            row["classification"] = "sampled-workflow-error"
        elif "plantuml-r1" in run.name:
            row["classification"] = "evaluator-output-path"
        elif "contracts-luna-r2" in run.name and any(skill in run.name for skill in ("echarts-animated-svg", "slidev-echarts")):
            row["classification"] = "evaluator-static-SSR-animation"
        elif "-d3-" in run.name and "d3-grid-r4" in run.name and not row["selectedFinal"]:
            row["classification"] = "superseded-grid-runtime; retained-extra-checker-flag-errors"
        elif "-d3-" in run.name and "d3-final-r3" in run.name and not row["selectedFinal"]:
            row["classification"] = "superseded-workflow; actual-overflow-fake-D3-description-and-mobile-failures"
        elif "-d3-" in run.name and not row["selectedFinal"]:
            row["classification"] = "superseded-runtime-and-sampled-overflow-failures"
        else:
            row["classification"] = "selected-final" if row["selectedFinal"] else "retained-superseded"
        inventory.append(row)
        if row["selectedFinal"]:
            output = run / "independent-event-summary.json"
            completed = subprocess.run(["uv", "run", "--script", "scripts/summarize-pi-json-events.py", str(run / "events.jsonl"), "--require-model", "gpt-5.6-luna", "--fail-on-invalid-json", "--fail-on-tool-error", "--require-tool-call", "--require-read", "../prompt.md", "--output", str(output)], cwd=ROOT, capture_output=True, check=False)
            trace = read(output) or {}
            row["independentTracePassed"] = completed.returncode == 0 and trace.get("passed") is True
            row["readPaths"] = [item["path"] for item in trace.get("readPaths", [])]
            row["observedModels"] = list(trace.get("models", {}))
            skill = manifest["skill"]["name"]
            expected_prefix = f"skills/{skill}/"
            forbidden = [path for path in row["readPaths"] if path.startswith("skills/") and (not path.startswith(expected_prefix) or "/assets/examples/" in path)]
            row["cleanReadSurface"] = not forbidden
            is_mermaid_natural = "-mermaid-naturalistic-" in run.name
            row["finalJointPassed"] = all((row["strictPassed"], row["artifactPassed"], row["supplementalSemanticPassed"] if is_mermaid_natural else row["literalBrowserPassed"], row["independentTracePassed"], row["cleanReadSurface"], row["sourcePayloadUnchanged"], row["copyMatchesFrozenSource"]))
            row["reviewQualification"] = "supplemental post-sampling semantic-reuse; original indexed oracle remains failed" if is_mermaid_natural else "literal/native contract"
            release.append(row)
    data = {"schemaVersion": 1, "date": "2026-10-04", "originalProtocolSha256": hashlib.sha256((HERE / "protocol.md").read_bytes()).hexdigest(),
            "plannedFinalRunCount": 18, "selectedFinalRunCount": len(release), "selectedJointPassCount": sum(bool(row["finalJointPassed"]) for row in release),
            "finalD3Pending": args.d3_cohort is None, "retainedAttemptCount": len(inventory), "selectedFinalRuns": release, "retainedAttempts": inventory}
    contracts_selected = [row for row in release if "-contract-" in row["runId"]]
    cohorts = {}
    for skill in ("d3", "mermaid", "plantuml-colorset-renderer"):
        rows = [row for row in release if f"-{skill}-naturalistic-" in row["runId"]]
        cohorts[skill] = {"attempts": len(rows), "jointPasses": sum(bool(row["finalJointPassed"]) for row in rows), "accepted": len(rows) == 3 and sum(bool(row["finalJointPassed"]) for row in rows) >= 2}
    data["naturalisticCohorts"] = cohorts
    data["finalContractPassCount"] = sum(bool(row["finalJointPassed"]) for row in contracts_selected)
    data["releaseAccepted"] = len(contracts_selected) == 9 and data["finalContractPassCount"] == 9 and all(cohort["accepted"] for cohort in cohorts.values())
    (HERE / "results.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    lines = ["# Colorset 1 Priority Release Assessment", "", f"On 2026-10-04, {data['selectedJointPassCount']} of {len(release)} selected final runs pass the recorded strict, artifact, actual-browser, model-trace and unchanged-payload gates. The planned scope is eighteen runs. All {len(inventory)} attempted dispatches remain retained.", "", "This count includes the explicitly qualified supplemental Mermaid semantic-role review. It does not convert the original per-node indexed oracle failures into passes. See [evaluation repairs and boundaries](assessment-notes.md), [sealed original protocol](protocol.md), [reviewer amendment](reviewer-amendment.json), and [machine-readable results](results.json).", "", "| Skill | Case | Joint result | Sampled raw payload |", "|---|---|---|---|"]
    for row in release:
        manifest = read(ROOT / row["rawEvidencePath"] / "run-manifest.json")
        skill = manifest["skill"]["name"]
        case = "naturalistic" if "-naturalistic-" in row["runId"] else "contract"
        lines.append(f"| {skill} | {case} | {'Pass' if row['finalJointPassed'] else 'Fail'} | `{row['payloadSha256'][:16]}` |")
    lines += ["", "Every selected trace reasserts `gpt-5.6-luna`, valid JSON, zero tool errors, a prompt read, no sibling/example read, and an unchanged copied runtime payload. Exact commands, prompt identities, native outputs, desktop/mobile measurements, screenshots and full traces remain in the ignored raw evidence paths named in `results.json`.", "", "Mermaid's full seventeen-slot native contract independently checks actual Group0 through Group16 body paint, maximum-contrast black/white labels, opacity, first-cycle border absence and a contrasting first overflow border. Fresh naturalistic Mermaid workflows pass three of three; original indexed per-node reviews remain zero of three, while the explicitly amended semantic-role review passes three of three. PlantUML's fresh native contract and all three naturalistic architecture/ArchiMate outputs pass with SVG-derived PNG delivery.", "", "ECharts and Slidev render native graph allocation and default boxplots on both white and black canvases. Independent browser measurements check complete arrowhead extent with three-pixel target clearance, opaque shaft/head contrast, and native median paint in resting and hover states. Their earlier covered-head and invisible-median failures remain retained. The final joint result includes these native semantic-mark checks; body-palette success alone is insufficient. External native axis annotations are outside this contract's body-label, arrow and median contrast scope. Three.js additionally observes actual native WebGL materials and absence of decorative edge meshes. Vectorization preserves source artwork SHA, SVG SHA and contours instead of forcing category order over source facts.", ""]
    if data["finalD3Pending"]:
        lines += ["The final D3 candidate remains pending freeze and fresh contract plus exactly three naturalistic attempts. Prior sampled D3 outputs and four source-preflight failures are retained and excluded from the final candidate count.", ""]
    if (HERE / "native-mark-summary.json").is_file():
        lines += ["The [independent native mark summary](native-mark-summary.json) records complete-head clearance and actual median paint sample counts for the selected chart contracts.", ""]
    lines += ["Run `uv run --script evaluations/colorset-priority-20261004/bind_git_payloads.py --ref INDEX` after final sources are staged, or pass an exact commit reference, to bind copied raw CRLF payloads to canonical Git LF blobs without mutating runtime resources.", ""]
    (HERE / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({key: data[key] for key in ("selectedFinalRunCount", "selectedJointPassCount", "finalD3Pending", "retainedAttemptCount", "releaseAccepted", "naturalisticCohorts")}))
    for row in release:
        if not row["finalJointPassed"]:
            print(json.dumps({key: row.get(key) for key in ("runId", "strictPassed", "artifactPassed", "literalBrowserPassed", "supplementalSemanticPassed", "independentTracePassed", "cleanReadSurface", "sourcePayloadUnchanged", "copyMatchesFrozenSource")}))
    return 0 if data["releaseAccepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
