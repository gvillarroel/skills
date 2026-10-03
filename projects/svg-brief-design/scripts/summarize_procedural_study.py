#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Export completed population results and public audits without reading private content."""
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svp3"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def files(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def main():
    run = read(ROOT / "run.json")
    assert run["selectedWinner"] == "q"
    disposition = read(ROOT / "independent-gate-disposition.json")
    assert disposition["status"] == "inconclusive-infrastructure-failure"
    assert disposition["promoted"] is False
    audit = read(ROOT / "revision-review/audit.json")
    forward = read(ROOT / "forward/summary.json")
    visual = read(ROOT / "public-visual-review.json")
    arms = {}
    task_scores = defaultdict(dict)
    for arm in ("b", "q"):
        rows = [r for r in audit["records"] if r["candidate"] == arm]
        assert len(rows) == 18
        arms[arm] = {
            "trials": len(rows), "runtime_passes": sum(r["runtime_valid"] for r in rows),
            "mean_visual_similarity": statistics.mean(r["reward"]["visual_similarity"] for r in rows),
            "mean_shape_similarity": statistics.mean(r["reward"]["shape_similarity"] for r in rows),
            "mean_style_similarity": statistics.mean(r["reward"]["style_similarity"] for r in rows),
            "renderer_used": sum(r["renderer_helper_used"] for r in rows),
            "preview_opened": sum(r["preview_read"] for r in rows),
            "scaffold_used": sum(r["scaffold_helper_used"] for r in rows),
            "mean_reported_trace_tokens": statistics.mean(r["total_tokens"] for r in rows),
        }
        for task in sorted({r["task"] for r in rows}):
            task_scores[task][arm] = statistics.mean(r["reward"]["visual_similarity"] for r in rows if r["task"] == task)
    for value in task_scores.values():
        value["gain"] = value["q"] - value["b"]
    gain = arms["q"]["mean_visual_similarity"] - arms["b"]["mean_visual_similarity"]
    selected_files = files(ROOT / "inputs/q/svg-brief-design")
    payload = read(ROOT / "q-payload-audit.json")
    canonical = files(REPO / "skills/svg-brief-design")
    installed = files(REPO / ".agents/skills/svg-brief-design")
    result = {
        "schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "study": "svp3", "model": "openai-codex/gpt-6-luna", "thinking": "medium", "transport": "sse",
        "condition": "Matched read/write/bash access and pinned renderer dependencies in both arms",
        "selected_candidate": "q", "ranking": run["ranking"],
        "development": {"arms": arms, "absolute_gain": gain,
                        "relative_gain": gain / arms["b"]["mean_visual_similarity"],
                        "task_means": dict(task_scores)},
        "independent_gate": {k: v for k, v in disposition.items() if k not in {"trials", "native_tree_sha256"}},
        "native_population_gate": run["holdout"],
        "forward": {"calls": forward["calls"], "automatic_passes": sum(r["passed"] for r in forward["rows"]),
                    "manual_positive_passes": sum(r["manual_brief_pass"] for r in visual["forward"]),
                    "negative_routing_pass": forward["rows"][-1]["passed"]},
        "budget": {"predecessor_development_calls": 3, "successor_development_calls": 54,
                   "validation_calls": disposition["observed_validation_agent_executions"],
                   "validation_planned_cap": 18, "forward_calls": 7, "semantic_retries": 0,
                   "earlier_independent_pilot_excluded": True,
                   "private_prelaunch_failure_model_calls": 0},
        "bundle": {"files": selected_files, "file_count": len(selected_files),
                   "canonical_equals_selected": canonical == selected_files,
                   "local_install_equals_selected": installed == selected_files,
                   "stored_artwork_files": payload["stored_artwork_files"],
                   "development_references_audited": payload["unique_development_references"],
                   "long_paths_compared": payload["long_paths_compared"]},
        "source_artifacts": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
            "protocol.json", "run.json", "q-mutation.json", "q-payload-audit.json",
            "revision-review/audit.json", "public-visual-review.json", "forward/protocol.json",
            "forward/summary.json", "private-gate-started.json", "private-path-gate-started.json",
            "independent-gate-disposition.json")},
        "limitations": [
            "Visual similarity is a shape/style proxy, not semantic correctness or a confidence estimate.",
            "Neither development arm was blinded to the guide; no pooled historical writing-only scores.",
            "Scaffold availability was tested as part of the bundle, but none of the measured development trials called it.",
            "Render-and-open adherence was 12/18 for the selected development arm, not universal.",
            "Trace token totals are not billed-token or price estimates.",
            "Exact path-string checks cannot exclude every transformed copy; source geometry was manually reviewed as original.",
            "No candidate mutation followed the private gate; the additional organic reserve remains unopened.",
        ],
    }
    target = REPO / "evaluations/svg-brief-design/procedural-20260926.json"
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "promoted": disposition["promoted"],
                      "development_gain": gain, "installed_selected": installed == selected_files}))


if __name__ == "__main__":
    main()
