#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently check native quantitative indexes, containment and association."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
LABELS = ["Low", "Medium-low", "Medium", "Medium-high", "High"]


def contains(outer, inner, tolerance=.5):
    return (inner["x"] >= outer["x"]-tolerance and inner["y"] >= outer["y"]-tolerance
            and inner["right"] <= outer["right"]+tolerance and inner["bottom"] <= outer["bottom"]+tolerance)


def rectangle_distance_squared(a, b):
    dx = max(a["x"]-b["right"], b["x"]-a["right"], 0)
    dy = max(a["y"]-b["bottom"], b["y"]-a["bottom"], 0)
    return dx*dx + dy*dy


def inspect(native):
    findings = []
    marks = native["quantitative"]
    if len(marks) != 5 or sorted(mark["index"] for mark in marks) != list(range(5)):
        findings.append("quantitative indexes must be exactly 0 through 4")
        return findings
    marks = sorted(marks, key=lambda mark: mark["index"])
    for mark in marks:
        rect = mark["rect"]
        if rect["width"] <= 0 or rect["height"] <= 0 or not contains(native["stage"], rect):
            findings.append(f"quantitative body {mark['index']} is empty or outside the SVG stage")
    for index, text in enumerate(LABELS):
        captions = [label for label in native["allText"] if label["text"] == text]
        if len(captions) != 1:
            findings.append(f"quantitative caption identity is ambiguous: {text}")
            continue
        caption = captions[0]["rect"]
        own = marks[index]["rect"]
        if contains(own, caption):
            continue
        distances = [rectangle_distance_squared(caption, mark["rect"]) for mark in marks]
        nearest = [i for i, distance in enumerate(distances) if abs(distance-min(distances)) <= .25]
        if len(nearest) > 1:
            # A broad caption may extend across neighboring columns while its
            # center is clearly aligned to one swatch; use that relevant axis.
            cx, cy = (caption["x"]+caption["right"])/2, (caption["y"]+caption["bottom"])/2
            axis = "x" if caption["bottom"] <= own["y"]+.5 or caption["y"] >= own["bottom"]-.5 else "y"
            centers = [(mark["rect"][axis] + mark["rect"]["right" if axis == "x" else "bottom"])/2 for mark in marks]
            offsets = [abs((cx if axis == "x" else cy)-centers[i]) for i in nearest]
            nearest = [i for i, offset in zip(nearest, offsets) if abs(offset-min(offsets)) <= .5]
        if nearest != [index]:
            findings.append(f"outside quantitative caption {text} is not uniquely associated with swatch {index}")
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="projects/grayscale-interleave/artifacts/reviews/forward-native/r4-canvas-repair-results.json")
    parser.add_argument("--output", default="projects/grayscale-interleave/artifacts/reviews/prefix-quantitative-review.json")
    args = parser.parse_args()
    report = ROOT / args.report
    rows = []
    for row in json.loads(report.read_bytes()):
        if row["family"] != "naturalistic":
            continue
        findings = inspect(row["native"]) if row.get("native") else ["native quantitative evidence missing"]
        rows.append({"runId": row["runId"], "passed": not findings, "findings": findings})
    result = {"nativeReport": report.relative_to(ROOT).as_posix(),
              "nativeReportSha256": hashlib.sha256(report.read_bytes()).hexdigest(),
              "reviewerSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "scope": "Actual native quantitative indexes 0..4, positive in-stage swatches, and matching inside/nearest axis-associated captions.",
              "runCount": len(rows), "bodyCount": sum(len(row.get("native", {}).get("quantitative", [])) for row in json.loads(report.read_bytes()) if row.get("native")),
              "passed": all(row["passed"] for row in rows), "rows": rows}
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit("Preserve the existing quantitative review and choose a new output path.")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("runCount", "bodyCount", "passed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
