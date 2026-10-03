#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Seal the explicitly reviewed final arrow runs; never auto-select a newer pass."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("arrow_runtime", Path(__file__).with_name("audit_runtime.py"))
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)
NATIVE = "evaluations/arrow-contrast-diagrams/validation-20261003.json"
CUSTOM = "evaluations/arrow-contrast-custom/results-20261003.json"
COMPOSITION = "evaluations/arrow-contrast-composition/validation-20261003.json"
CHARTS = "evaluations/arrow-contrast/echarts-runtime-artifacts-20261003.json"
REVIEWED = [
    ("mermaid", "arrow-native-mermaid-luna2-20261003", [NATIVE]),
    ("plantuml-colorset-renderer", "arrow-native-plantuml-colorset-renderer-luna2-20261003", [NATIVE]),
    ("slidev-quality-audit", "arrow-native-slidev-quality-audit-luna2-20261003", [NATIVE]),
    ("d3", "custom-arrow-d3-naturalistic-20261003-luna-4", [CUSTOM, "evaluations/arrow-contrast-custom/d3-independent-final-20261003.json"]),
    ("threejs-animated-3d", "custom-arrow-threejs-animated-3d-naturalistic-20261003-luna-1", [CUSTOM]),
    ("procedural-svg-animation", "custom-arrow-procedural-svg-animation-naturalistic-20261003-luna-1", [CUSTOM]),
    ("svg-brief-design", "custom-arrow-svg-brief-design-naturalistic-20261003-luna-1", [CUSTOM]),
    ("echarts-animated-svg", "20261003-arrow-echarts-animated-svg-final-11", [CHARTS]),
    ("slidev-echarts", "20261003-arrow-slidev-echarts-final-8", [CHARTS]),
    ("compose-synchronized-svg", "arrow-composition-compose-synchronized-svg-20261003-2", [COMPOSITION]),
    ("diagram-composition", "arrow-composition-diagram-composition-20261003-2", [COMPOSITION]),
    ("usefulcharts-style", "arrow-composition-usefulcharts-style-20261003-2", [COMPOSITION]),
    ("hyperframes-explainer", "arrow-composition-hyperframes-explainer-20261003-2", [COMPOSITION]),
    ("video", "arrow-composition-video-20261003-8", [COMPOSITION]),
    ("manim-svg-video", "arrow-composition-manim-svg-video-20261003-6", [COMPOSITION, "evaluations/arrow-contrast/manim-backing-independent-20261003.json"]),
]


def main():
    # This allowlist records independent reviewer acceptance, not strict-pass
    # discovery. A changed run ID requires a new explicit artifact review.
    rows = []
    for skill, run_id, evidence in REVIEWED:
        run = ROOT / "evaluations/runs" / run_id
        manifest = json.loads((run / "run-manifest.json").read_text())
        result = json.loads((run / "evaluation-result.json").read_text())
        digest, count = AUDIT.runtime_snapshot(ROOT / "skills" / skill)
        if (not result["passed"] or manifest["eventPolicy"]["strict"] is not True
                or manifest["skill"]["name"] != skill
                or manifest["skill"]["payloadSha256"] != digest):
            raise SystemExit(f"Reviewed run does not pass against the current payload: {run_id}")
        hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in evidence}
        rows.append({"skill": skill, "runId": run_id, "payloadSha256": digest,
                     "runtimeFileCount": count, "independentlyPassed": True,
                     "evidencePaths": evidence, "evidenceSha256": hashes})
    report = {"date": "2026-10-03", "passed": len(rows) == 15, "runs": rows,
              "scope": "Explicit final reviewer allowlist: current strict trial and independently accepted actual outputs. Failed, superseded, output-rejected and unfinalized trials are excluded regardless of strict-pass discovery."}
    destination = ROOT / "evaluations/arrow-contrast/accepted-arrow-runs-20261003.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "approvedCurrentRuns": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
