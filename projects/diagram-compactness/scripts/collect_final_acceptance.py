#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind reviewed release cases to exact retained strict results and final hashes."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from source_integrity import runtime_digest


ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "evaluations/runs"
REPORTS = ROOT / "evaluations/diagram-compactness"


def numbered(prefix: str, numbers: tuple[int, ...]) -> list[str]:
    return [prefix + str(number) for number in numbers]


def reviewed_case(run: str, independent: bool) -> dict:
    folder = RUNS / run
    manifest = json.loads((folder / "run-manifest.json").read_text(encoding="utf-8"))
    result = json.loads((folder / "evaluation-result.json").read_text(encoding="utf-8"))
    if manifest["skill"]["profile"] != "runtime" or not manifest["eventPolicy"]["strict"]:
        raise ValueError(f"Case is not a strict runtime trial: {run}")
    return {"run": run, "strictPass": result["passed"], "independentPass": independent,
            "jointPass": result["passed"] and independent,
            "payloadSha256": manifest["skill"]["payloadSha256"], "model": manifest["pi"]["model"],
            "expectedOutputs": manifest["expectedOutputs"],
            "strictResult": f"evaluations/runs/{run}/evaluation-result.json"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slidev-contract", required=True)
    parser.add_argument("--slidev-prefix", required=True)
    parser.add_argument("--audit-prefix", default="compact-slidev-quality-audit-20261004-trial-release-")
    parser.add_argument("--independent-failure", action="append", default=[])
    args = parser.parse_args()
    # True here means evaluator-owned browser/paint and delivery-size review,
    # supported by the linked component report. It never overrides strict.
    cohorts = [
        ("mermaid", "20261004-compaction-mermaid-contract-luna-2", numbered("20261004-compaction-mermaid-natural-luna-", (4, 5, 6)), "renderers-20261004.md", ["20261004-compaction-mermaid-boundary-luna-1"]),
        ("plantuml-colorset-renderer", "20261004-compaction-plantuml-contract-luna-2", numbered("20261004-compaction-plantuml-natural-luna-", (3, 4, 5)), "renderers-20261004.md", []),
        ("usefulcharts-style", "20261004-compaction-usefulcharts-contract-luna-2", numbered("20261004-compaction-usefulcharts-natural-luna-", (3, 4, 5)), "renderers-20261004.md", ["20261004-compaction-usefulcharts-boundary-luna-1"]),
        ("d3", "20261004-diagram-compact-d3-contract-luna-2", numbered("20261004-diagram-compact-d3-natural-luna-", (1, 2, 3)), "svg-runtime-20261004.md", ["20261004-diagram-compact-d3-network-contract-luna-1"]),
        ("svg-brief-design", "20261004-diagram-compact-svg-contract-luna-3", numbered("20261004-diagram-compact-svg-natural-luna-", (4, 5, 6)), "svg-runtime-20261004.md", []),
        ("procedural-svg-animation", "20261004-diagram-compact-procedural-connected-contract-luna-1", numbered("20261004-diagram-compact-procedural-natural-luna-", (4, 5, 6)), "svg-runtime-20261004.md", ["20261004-diagram-compact-procedural-contract-luna-3"]),
        ("diagram-composition", "20261004-composition-compactness-diagram-contract-luna-1", numbered("20261004-composition-compactness-diagram-natural-luna-", (1, 2, 3)), "composition-20261004.md", []),
        ("compose-synchronized-svg", "20261004-composition-compactness-compose-complete-label-contract-1", numbered("20261004-composition-compactness-compose-complete-label-natural-", (1, 2, 3)), "composition-20261004.md", ["20261004-composition-compactness-compose-complete-label-boundary-1"]),
        ("threejs-animated-3d", "20261004-composition-compactness-threejs-contract-luna-1", numbered("20261004-composition-compactness-threejs-natural-luna-", (1, 2, 3)), "composition-20261004.md", []),
        ("hyperframes-explainer", "20261004-composition-compactness-hyperframes-contract-luna-1", numbered("20261004-composition-compactness-hyperframes-natural-luna-", (1, 2, 3)), "composition-20261004.md", []),
        ("echarts-animated-svg", "compact-echarts-animated-svg-20261004-sol-literal-final-contract", numbered("compact-echarts-animated-svg-20261004-sol-literal-final-natural-", (1, 2, 3)), "consumer-audit-20261004.md", []),
        ("video", "compact-video-20261004-sol-semantic-final-contract", numbered("compact-video-20261004-sol-semantic-final-natural-", (1, 2, 3)), "video-runtime-20261004.md", []),
        ("slidev-animejs", "compact-slidev-animejs-20261004-painted-contract", numbered("compact-slidev-animejs-20261004-sol-release2-natural-", (1, 2, 3)), "slidev-animejs-runtime-20261004.md", ["compact-slidev-animejs-20261004-boundary-contract"]),
        ("slidev-echarts", args.slidev_contract, numbered(args.slidev_prefix + "natural-", (1, 2, 3)), "consumer-audit-20261004.md", []),
        ("slidev-quality-audit", args.audit_prefix + "contract", numbered(args.audit_prefix + "natural-", (1, 2, 3)), "slidev-quality-20261004.md", []),
    ]
    audit = json.loads((ROOT / "projects/diagram-compactness/artifacts/reviews/final-authoring-audit.json").read_text(encoding="utf-8"))
    if not audit["passed"]:
        raise ValueError("Standalone-bundle authoring audit is not passing.")
    current = {row["skill"]: row["payloadSha256"] for row in audit["results"] if row["profile"] == "runtime"}
    for skill, *_ in cohorts:
        if runtime_digest(skill) != current[skill]:
            raise ValueError(f"Saved standalone audit is stale; rerun it before acceptance: {skill}")
    rows = []
    independently_failed = set(args.independent_failure) | {"20261004-compaction-usefulcharts-natural-luna-4"}
    for skill, contract_run, natural_runs, report, extras in cohorts:
        if not (REPORTS / report).is_file():
            raise ValueError(f"Missing independent component report: {report}")
        contract = reviewed_case(contract_run, True)
        naturals = [reviewed_case(run, run not in independently_failed) for run in natural_runs]
        additional = [reviewed_case(run, True) for run in extras]
        if not contract["jointPass"] or not all(case["jointPass"] for case in additional):
            raise ValueError(f"Contract is not jointly accepted: {skill}")
        if sum(case["jointPass"] for case in naturals) < 2:
            raise ValueError(f"Natural repetition gate is not jointly accepted: {skill}")
        for case in [contract, *additional]:
            if case["payloadSha256"] != current[skill]:
                raise ValueError(f"Final contract does not match the current runtime source: {case['run']}")
        natural_hashes = {case["payloadSha256"] for case in naturals}
        if len(natural_hashes) != 1:
            raise ValueError(f"Natural cohort is not one frozen payload: {skill}")
        narrow = None
        if natural_hashes != {current[skill]}:
            if skill != "slidev-animejs":
                raise ValueError(f"Natural cohort does not match final runtime source: {skill}")
            narrow = json.loads((ROOT / "projects/diagram-compactness/artifacts/reviews/anime-paint-comparison.json").read_text(encoding="utf-8"))
            if not (narrow["passed"] and narrow["geometrySourceByteIdentical"]
                    and natural_hashes == {narrow["beforePayloadSha256"]}
                    and current[skill] == narrow["afterPayloadSha256"]):
                raise ValueError("Anime narrow paint repair lacks exact geometry lineage.")
        models = {case["model"] for case in [contract, *naturals, *additional]}
        if len(models) != 1:
            raise ValueError(f"Inconsistent declared release model: {skill}")
        rows.append({"skill": skill, "model": next(iter(models)), "sourcePayloadSha256": current[skill],
                     "independentReport": f"evaluations/diagram-compactness/{report}",
                     "contract": contract, "naturals": naturals, "additionalContracts": additional,
                     "narrowRepair": narrow})
    registry = {"schemaVersion": 1, "date": "2026-10-04",
                "completedAtUtc": datetime.now(timezone.utc).isoformat(), "reviewedInventoryCount": 34,
                "changedBundleCount": 15, "passed": True, "skills": rows,
                "limits": "Representative topology contracts and native delivery-size review; no global packing optimum or arbitrary-output certification."}
    output = REPORTS / "acceptance-20261004.json"
    output.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "skills": len(rows), "output": str(output),
                      "jointNaturalPasses": sum(case["jointPass"] for row in rows for case in row["naturals"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
