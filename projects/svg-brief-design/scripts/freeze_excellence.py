#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Seal the calibrated evaluator before any current-output scoring."""
from datetime import datetime, timezone
import shutil

from svg_excellence import CONFIG, REPO, DEFAULT_FONTS, aggregate, read, sha, write


def main():
    root = REPO/"evaluations/runs/svgq2"
    calibration = read(root/"calibration-check-v2.json")
    if not calibration["passed"]:
        raise ValueError("Failed calibration cannot be activated")
    outcomes = read(root/"calibration-results-v2.json")
    old = {row["id"]: row for row in outcomes["results"]}
    rubric = read(CONFIG/"rubric-v2.json")
    repeat_report = read(root/"jev-repeat-v2/report.json")
    if repeat_report["status"] != "complete" or repeat_report["completed_units"] != 3:
        raise ValueError("Repeat control incomplete")
    import json
    repeated = []
    for line in (root/"jev-repeat-v2/decisions.jsonl").read_text().splitlines():
        row = json.loads(line)
        identity = row["location"]["record_id"]
        evidence = read(root/"calibration/evidence"/(identity+".json"))
        new = aggregate(evidence, row["decisions"], rubric)
        delta = None if new["score_100"] is None else abs(new["score_100"]-old[identity]["score_100"])
        if delta is None or delta > 3:
            raise ValueError("Repeat score drift exceeds three points")
        repeated.append({"id": identity, "score_100": new["score_100"], "absolute_difference": delta})
    bundle = root/"frozen/evaluator"
    (bundle/"scripts").mkdir(parents=True, exist_ok=False)
    for name in ["svg_excellence.py", "diagnose_svg_layout.py", "evaluate_svg_jev.py"]:
        shutil.copy2(REPO/"projects/svg-brief-design/scripts"/name, bundle/"scripts"/name)
    for path in (REPO/"skills/jev-batch-decisions/scripts").glob("jev_*.py"):
        shutil.copy2(path, bundle/"scripts"/path.name)
    shutil.copytree(DEFAULT_FONTS, bundle/"fonts")
    shutil.copy2(CONFIG/"rubric-v2.json", bundle/"rubric.json")
    shutil.copy2(CONFIG/"jev-expert-v2.json", bundle/"job.json")
    shutil.copy2(CONFIG/"request-contracts.json", bundle/"request-contracts.json")
    files = {path.relative_to(bundle).as_posix(): sha(path.read_bytes()) for path in sorted(bundle.rglob("*")) if path.is_file()}
    selected = {"version": "2.1.0", "selected": "expert-categorical-v2", "primary_reward": "technical_excellence",
                "frozen_at": datetime.now(timezone.utc).isoformat(), "files": files,
                "observed_models": outcomes["observed_models"], "calibration": calibration,
                "repeat_controls": repeated,
                "semantics": "Weighted selected categories, not expected scores. Confidence below 0.3 flags review separately. Unknown means no numeric reward.",
                "selection_scope": "Original synthetic calibration only; current outputs not scored before freeze.",
                "previous_candidate": {"id": "expert-expected-v1", "passed_controls": 4, "total": 17, "disposition": "rejected"},
                "calibration_artifact_hashes": {name: sha((root/name).read_bytes()) for name in ["calibration-check-v1.json", "calibration-check-v2.json", "calibration/manifest.json", "calibration/coordinator-only.json", "jev-calibration-v1/run.json", "jev-calibration-v2/run.json", "jev-repeat-v2/run.json"]}}
    write(bundle/"lock.json", selected)
    write(CONFIG/"selected-configuration.json", {key: value for key, value in selected.items() if key != "calibration_artifact_hashes"} | {
        "local_bundle": bundle.relative_to(REPO).as_posix(), "bundle_lock_sha256": sha((bundle/"lock.json").read_bytes())})
    print("Sealed expert-categorical-v2; 17/17 controls and 3/3 repeated controls pass.")


if __name__ == "__main__":
    main()
