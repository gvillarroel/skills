#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Keep durable state summaries while retaining detailed samples in project artifacts."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ("echarts-final-20261003.json", "slidev-routes-20261003.json",
           "echarts-runtime-artifacts-20261003.json", "slidev-runtime-component-20261003.json")


def main():
    compacted = []
    for name in REPORTS:
        target = ROOT / "evaluations/arrow-contrast" / name
        if not target.is_file():
            continue
        data = target.read_bytes()
        report = json.loads(data)
        if report.get("detailedSampleEvidence"):
            continue
        detail = ROOT / "projects/arrow-contrast/artifacts/reviews" / ("detailed-" + name)
        detail.parent.mkdir(parents=True, exist_ok=True)
        detail.write_bytes(data)
        for state in report.get("states", []):
            for record in state.get("records", []):
                points = record.pop("points", [])
                record["sampleCount"] = len(points)
                record["coveredSampleCount"] = sum(bool(point.get("covered")) for point in points)
                record["distinctLocalBackings"] = sorted({tuple(point.get("bg", point.get("backing", []))) for point in points})
        report["detailedSampleEvidence"] = {"path": detail.relative_to(ROOT).as_posix(),
                                            "sha256": hashlib.sha256(data).hexdigest(),
                                            "sizeBytes": len(data)}
        target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        compacted.append({"report": name, "beforeBytes": len(data), "afterBytes": target.stat().st_size})
    print(json.dumps({"compacted": compacted}, indent=2))


if __name__ == "__main__":
    main()
