#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize independent native mark observations from selected chart runs."""
import json
from pathlib import Path
from validate_artifacts import contrast

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    results = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    owners = []
    for row in results["selectedFinalRuns"]:
        if not any(f"-{skill}-contract-" in row["runId"] for skill in ("echarts-animated-svg", "slidev-echarts")):
            continue
        report = json.loads((ROOT / row["rawEvidencePath"] / "browser-review-v2.json").read_text(encoding="utf-8"))
        clearances, arrow_contrasts, rest_contrasts, hover_contrasts = [], [], [], []
        rest_boxes = hover_boxes = 0
        for surface in report["surfaces"]:
            state = surface["state"]
            canvas = "#000000" if ".dark." in surface["route"] else "#ffffff"
            for head in state.get("arrowHeads", []):
                clearances.append(head["closestTarget"]["clearance"])
                arrow_contrasts.append(contrast(head["fill"], canvas))
            for shaft in state.get("arrowShafts", []):
                arrow_contrasts.append(contrast(shaft["stroke"], canvas))
            for box in state.get("boxes", []):
                rest_boxes += 1
                rest_contrasts.extend(contrast(sample["paint"], box["fill"]) for sample in box["medianSamples"])
            for box in state.get("hoverMedianObservations", []):
                hover_boxes += 1
                hover_contrasts.extend(contrast(sample["paint"], box["fill"]) for sample in box["medianSamples"])
        owners.append({"skill": report["skill"], "runId": row["runId"], "payloadSha256": row["payloadSha256"],
                       "browserPassed": report["passed"], "surfaceCount": len(report["surfaces"]),
                       "completeHeadObservations": len(clearances), "minimumCompleteHeadClearancePx": min(clearances),
                       "minimumArrowContrast": min(arrow_contrasts), "restingBoxObservations": rest_boxes,
                       "restingMedianSamples": len(rest_contrasts), "minimumRestingMedianContrast": min(rest_contrasts),
                       "hoverBoxObservations": hover_boxes, "hoverMedianSamples": len(hover_contrasts),
                       "minimumHoverMedianContrast": min(hover_contrasts)})
    result = {"date": "2026-10-04", "source": "independent actual DOM paint and native geometry observations", "owners": owners}
    (HERE / "native-mark-summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
