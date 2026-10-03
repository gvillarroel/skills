#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Freeze a new three-split study after a task-free SSE remediation probe."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

REPO = Path(__file__).resolve().parents[3]
STUDY = REPO / "evaluations/runs/svg-brief-design-gepa-20260925"
PREVIOUS = REPO / "evaluations/runs/svg-brief-design-20260925-r2"
BENCHMARK = Path("C:/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wsl(path):
    return "/mnt/c/" + str(path.resolve()).replace("\\", "/")[3:]


def write_once(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    probe = json.loads((STUDY / "probe-sse/receipt.json").read_text())
    assert probe["passed"] and probe["transport"] == "sse"
    assert not (PREVIOUS / "search/holdout").exists()
    previous = json.loads((PREVIOUS / "jobs/development.json").read_text())
    evolution = [BENCHMARK / "datasets-v1.1/development" / name for name in previous["datasets"][0]["task_names"]]
    manifest = Path(os.environ["LOCALAPPDATA"]) / "FoxVectorBenchmark/private-v1/manifest-v1.1.private.json"
    private = [row for row in json.loads(manifest.read_text(encoding="utf-8")) if row["split"] != "development"]
    families = {family: [row for row in private if row["family"] == family] for family in sorted({row["family"] for row in private})}
    validation_family = next(f for f, rows in families.items() if len(rows) == 6)
    holdout_family = next(f for f, rows in families.items() if len(rows) == 2)
    ranked = sorted(families[validation_family], key=lambda row: hashlib.sha256(("svg-gepa-v1|" + row["id"]).encode()).hexdigest())
    validation = [Path(row["task_path"]) for row in ranked[:3]]
    holdout = [Path(row["task_path"]) for row in families[holdout_family]]
    assert len(evolution) == 6 and len(validation) == 3 and len(holdout) == 2
    memory = (
        "Prior optimizer exposure: six development families and their complete generation-zero native trials. "
        "The first guide slightly improved the visual proxy but sometimes encouraged gratuitous cutouts, repeated borders, "
        "unreadable pseudo-letter shapes, and diagrams whose relationships were geometrically unclear. "
        "Preserve readable subject structure, natural short-request interpretation, and consistent graphic treatment. "
        "Two subsequent prose hypotheses were unavailable because of provider transport failures; their partial scores are not evidence of superiority. "
        "No private score, artifact, instruction, or diagnostic is supplied to the optimizer. "
        "The curator authored the original briefs before this study, so this is internal transfer rather than independent external curation."
    )
    config = {
        "schemaVersion": 2,
        "evolution": {
            "id": "svg-brief-design-gepa-20260925", "baselineSkill": wsl(REPO / "skills/svg-brief-design"),
            "outputDir": wsl(STUDY / "run"),
            "objective": "Improve visual similarity and faithful interpretation of general human SVG briefs through concise, reusable design guidance. Preserve original editable SVG output and the user's artwork boundary. Change only the SKILL.md body, keep frontmatter and references identical, and never include SVG markup, path coordinates, task IDs, reference shapes, copied answers, fixed specimen counts, or benchmark-specific recipes.",
            "background": memory,
        },
        "harbor": {
            "agent": {"name": "pi_svg_skill_sse:PiSvgSkill", "model": "openai-codex/gpt-6-luna", "kwargs": {"version": "0.84.2"}},
            "environment": "docker", "concurrency": 2, "rewardKey": "visual_similarity",
            "validationAttempts": 3, "holdoutAttempts": 3, "requiredEnv": ["FOX_PI_AUTH"],
        },
        "gepa": {"reflectionModel": "pi-oauth/openai-codex/gpt-6-luna", "reflectionMinibatchSize": 3, "maxMetricCalls": 60, "maxCandidateProposals": 6, "seed": 2519},
        "splits": {"evolution": [wsl(p) for p in evolution], "validation": [wsl(p) for p in validation], "holdout": [wsl(p) for p in holdout]},
        "validationGate": {"minimumMeanGain": 0.015, "allowTaskRegressions": True, "requireNoErrors": True},
        "promotion": {"minimumMeanGain": 0.015, "allowTaskRegressions": True, "requireNoErrors": True},
    }
    protocol = {
        "schema_version": 2, "created_at": datetime.now(timezone.utc).isoformat(), "study_id": STUDY.name,
        "source_study": PREVIOUS.name, "new_user_instruction": "Use the evolution skill to improve the new skill.",
        "scope": "A new bounded GEPA campaign; no previous trial is replaced or retried.",
        "transport_remediation": {"transport": "sse", "probe_sha256": digest(STUDY / "probe-sse/receipt.json"), "global_settings_changed": False},
        "prior_optimizer_exposure": memory,
        "semantically_disjoint_families": {"evolution": "the existing six development families", "validation": validation_family, "holdout": holdout_family},
        "split_counts": {"evolution": 6, "validation": 3, "holdout": 2, "unused_reserve": 3},
        "budgets": {"gepa_metric_calls": 60, "gepa_proposals": 6, "validation_trials": 18, "holdout_trials": 12, "maximum_native_trials": 90, "native_retries": 0},
        "selection": "GEPA Pareto strict-improvement selection on evolution only; one changed digest frozen before private validation.",
        "gates": {"validation": config["validationGate"], "holdout": config["promotion"]},
        "additional_release_requirement": "All gate artifacts must pass artifact_valid=1.0, exact-model/input/integrity audits, guidance-only audit, ordinary repo checks, and visual review. No edits after private feedback.",
        "artwork_policy": "No SVGs, images, geometry, or benchmark answers in the skill. Reflection receives sanitized development summaries, no reference artwork or generated SVG source.",
        "metric": "Unchanged verifier 1.1.0; 0.6 shape + 0.4 style, not semantic accuracy.",
        "baseline_files": {p.relative_to(REPO / "skills/svg-brief-design").as_posix(): digest(p) for p in (REPO / "skills/svg-brief-design").rglob("*") if p.is_file()},
        "task_files": {wsl(root): {p.relative_to(root).as_posix(): digest(p) for p in root.rglob("*") if p.is_file()} for root in evolution + validation + holdout},
        "method": {"harbor": "0.18.0", "gepa": "0.1.2", "reflection": "Tool-free Pi GPT-6 Luna via GEPA's supported callable interface", "execution": "Pi GPT-6 Luna, medium, write-only, native explicit skill command, SSE"},
        "limitations": ["One vendor and small family counts", "Stochastic development measurements", "Curator prior exposure", "Visual proxy does not measure semantic correctness", "OAuth USD cost unknown"],
    }
    write_once(STUDY / "evolution.json", config)
    write_once(STUDY / "protocol.json", protocol)
    print(json.dumps({"study": str(STUDY), "split_counts": protocol["split_counts"], "maximum_native_trials": 90, "private_instructions_printed": False}))


if __name__ == "__main__":
    main()
