#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Freeze the bounded Pareto search and parallel diagnostic Trace branch."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from seal_technique_evolution import REPO, main as seal, read, sha, write, wsl


def receipt(root, arm):
    skill = root / f"inputs/{arm}/svg-brief-design"
    code = "from pathlib import Path; from harbor.skills import compute_skill_digest; import sys; print(compute_skill_digest(Path(sys.argv[1])))"
    digest = subprocess.check_output(["wsl", "-e", "/home/villa/.local/share/uv/tools/harbor/bin/python", "-B", "-c", code, wsl(skill)], text=True).strip()
    destination = root / f"input-{arm}.json"
    assert not destination.exists()
    write(destination, {"arm": arm, "source": str(skill), "harbor_digest": digest,
        "files": {p.relative_to(skill).as_posix(): sha(p) for p in sorted(skill.rglob("*")) if p.is_file()}})


def configuration(root, name, arms, generation=0, previous=None, parents=None):
    config = {
        "schemaVersion": 1,
        "search": {"id": "svg-pareto-trace-20260926", "baselineSkill": wsl(root / "inputs/b/svg-brief-design"),
                   "baselineCandidate": "b", "outputDir": wsl(root / "pareto"), "generation": generation},
        "harbor": {"developmentJob": wsl(root / "templates/development.json"), "holdoutJob": wsl(root / "templates/validation.json"),
                   "rewardKey": "technique_quality", "passThreshold": 0, "requiredRewards": {"artifact_valid": 1}, "requiredEnv": ["OPENROUTER_API_KEY"]},
        "candidates": [{"id": arm, "skill": wsl(root / f"inputs/{arm}/svg-brief-design"),
                        "parents": (parents or {}).get(arm, [] if arm == "b" else ["b"]),
                        "rationale": {"b": "Frozen installed baseline", "i": "Prior public information-editing candidate, freshly evaluated", "t": "Native diagnostic Trace candidate from public evidence", "p": "One native Pareto reflection or complementary merge"}[arm],
                        "jobDirectory": wsl(root / f"jobs/{arm}")} for arm in arms],
        "promotion": {"minimumMeanGain": .02, "allowCaseRegressions": True, "requireNoErrors": True},
    }
    if previous:
        config["search"]["previousGenerationLog"] = wsl(previous)
    assert not (root / f"pareto-{name}.json").exists()
    write(root / f"pareto-{name}.json", config)


def main():
    root = REPO / "evaluations/runs/svt6"
    assert read(root / "curation-status.json")["passed"]
    assert read(root / "curation-status.json")["selected_count"] == 2
    protocol = {
        "claim": "Bounded public Pareto skill evolution with a parallel native diagnostic Trace proposal and one fresh two-family independent pilot gate. No professional parity or broad transfer claim.",
        "development": {"attempts": 3},
        "validation": {"cases": 2, "construction_families": 2, "source_packs": 2, "attempts": 3,
                       "scope": "Two newly and affirmatively curated construction/source groups from the same publisher, excluded from public development and previously consumed packs. This small pilot does not establish broad professional generalization."},
        "budget": {"max_development_generation_calls": 72, "max_validation_generation_calls": 12,
                   "baseline_calls": 18, "max_candidates": 3, "calls_per_candidate": 18,
                   "observer_calls_max": 84, "jev_calls_max": 84, "retries": 0,
                   "curator_calls": 1, "prior_rejected_authoring_curator_calls": 1, "maximum_generations": 2,
                   "trace_model_calls": 0, "reflection_model_calls": 0},
        "selection": {
            "rule": "Use only the native Harbor reflective Pareto archive. Preserve all eligible non-dominated options. Select the highest native aggregate mean among changed archive members meeting gain >=0.02 and maximum family loss <=0.08 versus the same fresh baseline; ties prefer fewer SKILL.md lines then lexical ID. Every candidate must be complete, qualified and error-free. If baseline has attributable agent errors, retain the native zero/error evidence and additionally require >=0.02 gain and <=0.08 maximum loss across all completely error-free baseline families; require at least three such families. External or unclassified failures make comparison inconclusive. No semantic retries. Validate only this one fixed finalist. Independent gate requires native promote plus both arms error-free, every artifact valid, complete coverage, gain >=0.02 and no family loss >0.08. No alternate finalist after release.",
            "uncertainty": "Equal family means; three repetitions are not three independent families. Report all public family deltas and a descriptive bootstrap by six independent public families. Independent gate has only two groups: report their range and make no significance claim.",
        },
        "stopping": "Generation zero: frozen baseline, prior information candidate, and one evidence-supported native Trace candidate if available. Generation one: at most one new coherent reflection or merge justified by the native Pareto archive, retaining completed comparable jobs without replay. Stop after that generation or earlier if no safe supported mutation/qualified archive exists. At most three changed candidates; never exceed three consecutive rejected attempts. Freeze one development finalist before the one-use private gate; no later same-study evolution, reselection, or semantic reruns.",
        "method": {"selection_owner": "harbor-reflective-pareto-search", "parallel_proposal_owner": "harbor-trace-distillation",
                   "trace_mode": "Native schema-1 --analyze-only diagnosis/materialization; historical raw retry lock omissions prohibit schema-2 promotion. Outer Pareto study owns all new generation, selection, independent validation and installation.",
                   "execution": "Native Pareto execute_job for each frozen arm followed by the native --analyze-only archive. Skill source equals exact locked input path; no source-alias mapping. Its standard live holdout runs only after frozen selection."},
        "candidate_ids": ["b", "i", "t", "p"],
        "pareto_adapter_sha256": sha(Path(__file__).parent / "run_procedural_pareto.py"),
        "pareto_engine_sha256": sha(Path("C:/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py")),
        "trace_engine_sha256": sha(Path("C:/Users/villa/.codex/skills/harbor-trace-distillation/scripts/distill_harbor_traces.py")),
        "prior_authoring": {"path": str(REPO / "evaluations/runs/svt5"), "outcome": "three-family requirement rejected before any candidate inference", "redesign": "same random inventory, affirmative independent review for two families before evolution; fixed scoring and exclusion rules"},
    }
    seal(root, REPO / "skills/svg-brief-design", max_candidates=3, prepare_candidate=False,
         protocol_updates=protocol, attempts=3, evolution_owner="harbor-reflective-pareto-search")
    # Public-only ancestry is frozen separately before either mutation branch.
    memory = {"allowed_jobs": [str(REPO / f"evaluations/runs/{study}/jobs/{arm}") for study, arms in [("svt3", "bcde"), ("svt4", "bc")] for arm in arms],
        "allowed_notes": [str(REPO / "evaluations/runs/svt4/public-visual-review.md"), str(REPO / "projects/svg-brief-design/evaluation/information-editing-research-20260926.md")],
        "excluded": ["private", "private-jobs", "research-decision.json", "validation results and reports"],
        "scope": "Only the six public development task families; all private outcomes excluded from mutation."}
    write(root / "development-memory.json", memory)
    from seal_technique_evolution import org
    org("record-evidence", root / "study", "--evidence-id", "development-memory", "--stage-id", "evolve", "--kind", "other", "--role", "development", "--visibility", "private", "--path", root / "development-memory.json")
    shutil.copytree(REPO / "evaluations/runs/svt4/inputs/c/svg-brief-design", root / "inputs/i/svg-brief-design")
    receipt(root, "b")
    receipt(root, "i")
    configuration(root, "preflight", ["b", "i"])
    write(root / "freeze-receipt.json", {"frozen": True, "protocol_sha256": sha(root / "protocol.json"),
        "development_memory_sha256": sha(root / "development-memory.json"), "study": str(root / "study"),
        "validation_opened": False, "validation_cases": 2, "development_cases": 6, "attempts": 3,
        "trace_authoring_authorized": True, "canonical_unchanged": True})
    print(json.dumps({"ready": True, "protocol_sha256": sha(root / "protocol.json"), "validation_opened": False, "maximum_generation_calls": 84}))


if __name__ == "__main__":
    main()
