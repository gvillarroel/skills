#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Freeze one bounded mechanism-focused follow-up without opening private tasks."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json

from prepare_gepa_study import BENCHMARK, REPO, digest, wsl, write_once

PREVIOUS = REPO / "evaluations/runs/svg-brief-design-gepa-20260925"
STUDY = REPO / "evaluations/runs/svg-brief-design-mechanics-20260925"


def main():
    previous_run = json.loads((PREVIOUS / "run-async-compatible/run.json").read_text())
    assert previous_run["validation"].get("reason") == "selected-candidate-unchanged"
    assert previous_run["holdout"].get("reason") == "selected-candidate-unchanged"
    assert not any((PREVIOUS / "run-async-compatible/harbor-trials").glob("validation-*"))
    assert not any((PREVIOUS / "run-async-compatible/harbor-trials").glob("holdout-*"))
    config = json.loads((PREVIOUS / "evolution-async-compatible.json").read_text())
    protocol = json.loads((PREVIOUS / "protocol.json").read_text())
    old_tasks = {Path(path).name for path in config["splits"]["evolution"]}
    rows = [json.loads(line) for line in (BENCHMARK / "dataset-v1.1.jsonl").read_text(encoding="utf-8-sig").splitlines()]
    remaining = [row for row in rows if row["split"] == "development" and row["native_task_id"] not in old_tasks]
    selected = []
    for family in sorted({row["family"] for row in remaining}):
        choices = [row for row in remaining if row["family"] == family]
        selected.append(min(choices, key=lambda row: hashlib.sha256(("svg-gepa-mechanics-v1|" + row["id"]).encode()).hexdigest()))
    assert len(selected) == 6
    evolution = [BENCHMARK / "datasets-v1.1/development" / row["native_task_id"] for row in selected]
    background = (
        "This is one prospectively bounded follow-up to a completed six-proposal GEPA campaign. "
        "The original guide remained best at 0.520698; its two fully evaluated rewrites scored 0.513628 and 0.499111. "
        "Development-only visual review found that most proposals paraphrased the same advice without changing geometric construction. "
        "Recurring defects included repeated contours, distorted subject proportions, decorative framing replacing an intended arrangement, "
        "and curves whose placement did not express their relationship to axes. These are curator observations, not extra reward values. "
        "Test a more actionable mechanism: commit to a compact visual model before writing, derive geometry from shared anchors and relations, "
        "use a coherent coordinate frame and weight hierarchy, and check a small set of geometric and semantic invariants before delivery. "
        "For diagrams, derive curves and marks from their actual relationships to axes and endpoints. For organic or emblematic subjects, "
        "preserve defining proportions and connected or separated masses without adding a generic enclosing badge. "
        "Make one or two linked procedural changes per proposal; avoid another wording-only rewrite. "
        "Do not encode task-specific counts, numerical target styles, coordinate recipes, subject lookup tables, or specimen shapes. "
        "Six additional human-like requests from the same development families are selected by a predeclared hash order, not by observed results. "
        "The previous six tasks are prior discovery exposure. No private instructions, scores, artifacts, or diagnostics are available to reflection. "
        "Original briefs were authored by the curator, so this is internal transfer rather than external independent curation."
    )
    config["evolution"].update(id=STUDY.name, outputDir=wsl(STUDY / "run-async-compatible"), background=background)
    config["gepa"].update(maxMetricCalls=42, maxCandidateProposals=3, seed=2519)
    config["splits"]["evolution"] = [wsl(root) for root in evolution]
    protocol = copy.deepcopy(protocol)
    protocol.update(
        created_at=datetime.now(timezone.utc).isoformat(), study_id=STUDY.name,
        source_study=PREVIOUS.name, new_user_instruction="Continue the requested evaluation-guided skill evolution.",
        scope="One mechanism-focused follow-up on six additional development tasks. No old outcomes are retried, replaced, pooled, or hidden.",
        prior_optimizer_exposure=background,
        followup_stop="At most three new proposals; preserve the baseline on unchanged selection or any failed private gate. No further search in this follow-up.",
        budgets={"gepa_metric_calls":42,"gepa_proposals":3,"validation_trials":18,"holdout_trials":12,"maximum_native_trials":72,"native_retries":0},
        development_selection={"algorithm":"minimum SHA-256(svg-gepa-mechanics-v1|id) per development family, excluding earlier GEPA tasks", "families":[row["family"] for row in selected],"previous_task_ids":sorted(old_tasks)},
        parent_evidence={"run_sha256":digest(PREVIOUS / "run-async-compatible/run.json"),"audit_sha256":digest(PREVIOUS / "audit.json"),"private_gates_unopened":True},
        launcher_sha256=digest(Path(__file__).with_name("run_gepa_mechanics.py")),
        preparation_sha256=digest(Path(__file__)),
    )
    protocol["task_files"] = {root: values for root, values in protocol["task_files"].items() if Path(root).name not in old_tasks}
    for root in evolution:
        protocol["task_files"][wsl(root)] = {p.relative_to(root).as_posix():digest(p) for p in root.rglob("*") if p.is_file()}
    baseline = REPO / "skills/svg-brief-design"
    assert protocol["baseline_files"] == {p.relative_to(baseline).as_posix():digest(p) for p in baseline.rglob("*") if p.is_file()}
    STUDY.mkdir(parents=True, exist_ok=False)
    write_once(STUDY / "evolution-async-compatible.json", config)
    write_once(STUDY / "protocol.json", protocol)
    print(json.dumps({"study":str(STUDY),"split_counts":protocol["split_counts"],"maximum_native_trials":72,"private_gates_reused_unopened":True}))


if __name__ == "__main__":
    main()
