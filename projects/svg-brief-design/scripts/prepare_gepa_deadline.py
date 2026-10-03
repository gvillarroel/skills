#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Register one additive prompt-binding experiment within the user's timebox."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from prepare_gepa_study import BENCHMARK, REPO, digest, wsl, write_once

PARENTS = [REPO / "evaluations/runs" / name for name in ("svg-brief-design-gepa-20260925", "svg-brief-design-mechanics-20260925")]
STUDY = REPO / "evaluations/runs/svg-brief-design-deadline-20260926"


def main():
    old_tasks = set()
    parent_evidence = []
    for parent in PARENTS:
        run = json.loads((parent / "run-async-compatible/run.json").read_text())
        assert run["validation"].get("reason") == "selected-candidate-unchanged"
        assert run["holdout"].get("reason") == "selected-candidate-unchanged"
        config = json.loads((parent / "evolution-async-compatible.json").read_text())
        old_tasks.update(Path(path).name for path in config["splits"]["evolution"])
        parent_evidence.append({"study":parent.name,"run_sha256":digest(parent / "run-async-compatible/run.json"),"audit_sha256":digest(parent / "audit.json")})
    protocol = json.loads((PARENTS[-1] / "protocol.json").read_text())
    rows = [json.loads(line) for line in (BENCHMARK / "dataset-v1.1.jsonl").read_text(encoding="utf-8-sig").splitlines()]
    development = [row for row in rows if row["split"] == "development"]
    selected = []
    for family in sorted({row["family"] for row in development}):
        family_rows = [row for row in development if row["family"] == family]
        choices = [row for row in family_rows if row["native_task_id"] not in old_tasks] or family_rows
        selected.append(min(choices, key=lambda row:hashlib.sha256(("svg-prompt-binding-v1|" + row["id"]).encode()).hexdigest()))
    assert len(selected) == 6
    evolution = [BENCHMARK / "datasets-v1.1/development" / row["native_task_id"] for row in selected]
    background = (
        "Two completed development-only campaigns tested nine rewrites across twelve cases. None beat the unchanged guide. "
        "The rewrites broadly paraphrased silhouette, restraint, or anchor advice and changed many sentences at once. "
        "Some reference differences are legitimate because the human briefs do not specify every geometric choice. "
        "Do not learn omitted reference topology, counts, offsets, or specimen shapes. The original curator saw sources when authoring the briefs. "
        "New hypothesis: explicit noun-modifier binding before geometry, followed by one prompt-derived coverage check. "
        "Make a minimal ADDITIVE change to the original guide: retain every existing word in order. Add at most two compact paragraphs, "
        "30 to 180 words total, without rewriting existing prose. First identify the main object and bind each descriptive phrase to the object, "
        "part, or relationship it modifies; distinguish explicit requirements from open choices. Before writing the SVG, check that the dominant "
        "masses and contours still express the requested object and arrangement when secondary marks are mentally removed, and each explicit "
        "modifier has a visible geometric decision. Missing requirements should change the dominant form rather than add unrelated ornament. "
        "This is an unproven transferable procedure, not an asset-specific recipe. No example drawings, coordinates, style target values, "
        "task IDs, asset links, source geometry, or reconstruction instructions may enter the skill. "
        "Six development briefs are hash-selected before inference, one per known family: prefer previously untested cases, "
        "and reuse a previously exposed task only where the public family has no unused case. Both arms are freshly measured. "
        "Prior development scores and visual observations are discovery exposure. Private instructions, outcomes, and diagnostics remain unavailable."
    )
    config["evolution"].update(id=STUDY.name, outputDir=wsl(STUDY / "run-async-compatible"), background=background)
    config["harbor"]["concurrency"] = 3
    config["gepa"].update(maxMetricCalls=18, maxCandidateProposals=1, seed=2606)
    config["splits"]["evolution"] = [wsl(root) for root in evolution]
    private_paths = set(config["splits"]["validation"] + config["splits"]["holdout"])
    protocol["task_files"] = {root:values for root,values in protocol["task_files"].items() if root in private_paths}
    for root in evolution:
        protocol["task_files"][wsl(root)] = {p.relative_to(root).as_posix():digest(p) for p in root.rglob("*") if p.is_file()}
    protocol.update(
        created_at=datetime.now(timezone.utc).isoformat(), study_id=STUDY.name,
        source_study=PARENTS[-1].name, new_user_instruction="Improve the skill as much as possible until 06:00 America/New_York on 2026-09-26.",
        scope="One minimal additive prompt-binding experiment; old evidence and rewards remain unchanged.",
        user_deadline_utc="2026-09-26T10:00:00+00:00", trial_admission_cutoff_utc="2026-09-26T09:55:00+00:00",
        prior_optimizer_exposure=background,
        followup_stop="One proposal. No trials admitted at or after 09:55 UTC; any incomplete campaign is not eligible for promotion. Preserve every started trial.",
        budgets={"gepa_metric_calls":18,"gepa_proposals":1,"validation_trials":18,"holdout_trials":12,"maximum_native_trials":48,"native_retries":0},
        development_selection={"algorithm":"minimum SHA-256(svg-prompt-binding-v1|id) per development family; prefer unused cases, otherwise use the full public family", "families":[row["family"] for row in selected],"previous_task_ids":sorted(old_tasks),"new_task_count":sum(row["native_task_id"] not in old_tasks for row in selected)},
        parent_evidence=parent_evidence,
        launcher_sha256=digest(Path(__file__).with_name("run_gepa_deadline.py")), preparation_sha256=digest(Path(__file__)),
        runtime_metadata_boundary={"GIT_CEILING_DIRECTORIES":"/mnt/c/Users/villa/dev/skills/evaluations/runs/svg-brief-design-gepa-20260925/runtime-env/lib", "purpose":"Prevent a package's Versioneer metadata query from treating its unrelated parent repository as package source; no package version is injected."},
        mutation_contract="Keep all baseline tokens in order; add 30–180 English words. Existing resources and metadata remain identical.",
    )
    baseline = REPO / "skills/svg-brief-design"
    assert protocol["baseline_files"] == {p.relative_to(baseline).as_posix():digest(p) for p in baseline.rglob("*") if p.is_file()}
    STUDY.mkdir(parents=True, exist_ok=False)
    write_once(STUDY / "evolution-async-compatible.json", config)
    write_once(STUDY / "protocol.json", protocol)
    print(json.dumps({"study":str(STUDY),"maximum_native_trials":48,"concurrency":3,"deadline_utc":protocol["user_deadline_utc"],"private_gates_still_unopened":True}))


if __name__ == "__main__":
    main()
