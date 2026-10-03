#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Check predeclared controls without changing their expectations after scoring."""
import argparse
from pathlib import Path
from svg_excellence import read, write


def check(prepared, result):
    private = read(Path(prepared)/"coordinator-only.json")
    rows = {row["id"]: row for row in result["results"]}
    by_name = {item["name"]: rows[item["id"]] for item in private}
    checks = []
    for item in private:
        result_row = rows[item["id"]]
        expected = item["expected"]
        score = result_row["score_100"]
        passed = score is not None
        observations = {"score": score}
        for key, value in expected.items():
            if key == "minimum_score":
                passed &= score is not None and score >= value
            elif key.startswith("maximum_") and key.endswith("_level"):
                dim = {"maximum_brief_level": "brief_adherence", "maximum_legibility_level": "legibility"}[key]
                actual = result_row.get("dimensions", {}).get(dim)
                observations[dim] = actual
                passed &= actual is not None and actual <= value
            elif key == "hard_failure":
                passed &= result_row["status"] == "artifact_failure" and score == 0 and not result_row["model_called"]
        if "below" in expected:
            peer = by_name[expected["below"]]["score_100"]
            observations["gap"] = peer-score if peer is not None and score is not None else None
            passed &= observations["gap"] is not None and observations["gap"] >= expected["minimum_gap"]
        if "equivalent_to" in expected:
            peer = by_name[expected["equivalent_to"]]["score_100"]
            observations["difference"] = abs(peer-score) if peer is not None and score is not None else None
            passed &= observations["difference"] is not None and observations["difference"] <= expected["maximum_difference"]
        checks.append({"name": item["name"], "passed": bool(passed), "expected": expected, "observed": observations})
    return {"passed": all(row["passed"] for row in checks), "passed_controls": sum(row["passed"] for row in checks),
            "total_controls": len(checks), "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = check(args.prepared, read(args.results))
    write(args.out, result)
    print(result)
