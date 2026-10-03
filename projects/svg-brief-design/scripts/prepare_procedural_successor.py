#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Register a disjoint development cohort after a proven storage failure."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from prepare_procedural_study import REPO, ROOT as PARENT, hashes, wsl, write

ROOT = REPO / "evaluations/runs/svp2"
BENCHMARK = Path("C:/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1")


def main():
    ROOT.mkdir(parents=True, exist_ok=False)
    prior = json.loads((PARENT / "protocol.json").read_text())
    probe = json.loads((PARENT / "artifact-mount-probe.json").read_text())
    assert probe["rows"][0]["visible"] and probe["rows"][1]["errno"] == 5
    failed_job = PARENT / "population/generation-000/candidates/baseline/harbor-jobs/harbor-pop-g000-baseline"
    executed = []
    for path in failed_job.glob("*/agent/pi.txt"):
        events = [json.loads(line) for line in path.read_text().splitlines() if line.startswith("{")]
        if any(e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant" for e in events):
            executed.append(path.parent.parent.name.split("__")[0])
    assert len(executed) == 3
    rows = [json.loads(line) for line in (BENCHMARK / "dataset-v1.1.jsonl").read_text(encoding="utf-8-sig").splitlines()]
    public = [r for r in rows if r["split"] == "development"]
    selected = []
    for family in sorted({r["family"] for r in public}):
        available = [r for r in public if r["family"] == family and r["native_task_id"] not in executed]
        assert available, "No unexecuted case in this family; a fresh cohort is required"
        selected.append(min(available, key=lambda r: hashlib.sha256(("original-procedural-short-v1|" + r["id"]).encode()).hexdigest()))
    for candidate in ("baseline", "procedural-v1"):
        source = PARENT / candidate / "skills/svg-brief-design"
        shutil.copytree(source, ROOT / candidate / "skills/svg-brief-design")
    for name in ("development", "validation"):
        template = json.loads((PARENT / f"templates/{name}.json").read_text())
        template["jobs_dir"] = wsl(ROOT / "jobs")
        if name == "development":
            template["datasets"][0]["task_names"] = [r["native_task_id"] for r in selected]
        write(ROOT / f"templates/{name}.json", template)
    prior.update(study=ROOT.name, registered_at=datetime.now(timezone.utc).isoformat(),
                 parent_protocol_sha256=hashlib.sha256((PARENT / "protocol.json").read_bytes()).hexdigest(),
                 predecessor=str(PARENT),
                 storage_remediation={"probe_sha256": hashlib.sha256((PARENT / "artifact-mount-probe.json").read_bytes()).hexdigest(),
                                      "finding": "A deep host bind mount reliably raises errno 5 while its container is alive; a short host path works. Neither probe calls a model or Harbor.",
                                      "predecessor_disposition": "Incomplete failed native root preserved. Three completed baseline generations have no verifier result. They are not retried or converted into synthetic native results; the supported recovery contract requires a selective-resume ledger that is absent.",
                                      "excluded_completed_case_ids": sorted(executed)},
                 development_selection={"algorithm": "Minimum SHA-256(original-procedural-short-v1|id) per public family after excluding every case with a completed generation in the failed predecessor.",
                                        "cases": [{"task": r["native_task_id"], "family": r["family"]} for r in selected],
                                        "scores_seen_before_selection": False})
    prior["budget"].update(max_development_calls=54, predecessor_model_calls=3,
                           cumulative_development_cap=72,
                           rule="One 36-call generation; at most one 18-call development revision with the frozen contemporaneous baseline reused through native artifact analysis. All three predecessor calls remain charged. No retry of its completed cases, no budget reset, no semantic reruns, and no mutation after validation.")
    prior["templates"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "templates").glob("*.json")}
    for name in ("execute_procedural_generation.py", "execute_procedural_successor.py", "prepare_procedural_successor.py"):
        prior["runtime"]["helpers"][name] = hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
    write(ROOT / "protocol.json", prior)
    argv = json.loads((PARENT / "generation-000-argv.json").read_text())
    argv = [v.replace(wsl(PARENT), wsl(ROOT)) for v in argv]
    write(ROOT / "generation-000-argv.json", argv)
    write(PARENT / "failure-disposition.json", {"terminal": True, "native_root_complete": False, "recovered": False,
           "model_calls": 3, "no_scores_observed": True, "recovery_ineligible": "Missing sealed selective-resume ledger; incomplete root with cancellation.",
           "successor": wsl(ROOT), "excluded_cases": sorted(executed), "automatic_retries": 0})
    print(json.dumps({"study": str(ROOT), "cases": prior["development_selection"]["cases"], "excluded": sorted(executed), "private_gate": "closed"}))


if __name__ == "__main__":
    main()
