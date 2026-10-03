#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML==6.0.2", "resvg-py==0.2.6", "Pillow==11.3.0", "defusedxml==0.7.1"]
# ///
"""Freeze a separate Astra profile without changing the historical Luna study."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from prepare_information_study import tree
from prepare_pareto_trace_study import receipt
from seal_technique_evolution import REPO, org, read, sha, write, wsl

HERE = Path(__file__).parent
ROOT = REPO / "evaluations/runs/svt8"
RESEARCH = REPO / "projects/svg-brief-design/evaluation/purpose-techniques-astra-20260926.md"

GUIDE = """# Select marks by their job

Use this guide for monochrome editorial figures, linked ornament, technical
accents, compact labels and illustrative diagrams. Select the relevant branch;
do not apply every treatment to every drawing. Preserve the complete brief.

## Establish the intended reading

Write one short construction sentence: what the viewer should recognize first,
what relationship makes it recognizable, and which information is secondary.
Distinguish an expressive illustration from a pictogram, a label from a control
panel, and an explanatory diagram from a measured chart. These need different
amounts and kinds of information. Do not invent a surrounding fictional system.

Choose each mark's job: outer boundary, occluding edge, plane change, structural
joint, explanatory trace, identifier, or requested ornament. If removing a mark
does not affect one of these jobs, omit it unless it contributes an intentional
rhythm. A smooth path with no job can still weaken the drawing.

## Resolve the construction that matters

- **Expressive figures:** locate the distinctive landmarks and their proportions
  before drawing small mechanisms. Connect them through an enclosing form and
  a few consistent plane changes. Let selected edges disappear into the empty
  ground while adjacent contours imply the continuation. Avoid outlining every
  part twice or replacing expression with familiar symbols. Preserve the mood
  and characteristic proportions rather than forcing a product-icon grid.
- **Linked ornament:** settle one band and its neighboring void before repeating
  it. At each encounter decide whether the bands merge, stay separate, or pass
  over and under. For a crossing, interrupt the hidden band clearly on both
  sides; for a union, remove the internal seam. Follow each band through the
  finished form. Repair a branch that loses its direction, a trapped sliver or
  an unintended collision. Share a width/taper profile across related bands;
  do not let independently drawn edges invent extra pockets.
- **Open mechanical forms:** use a common axis and a small set of plane directions
  to align the separated masses. The opening between two masses should continue
  the body's direction or explain a joint. Let an exterior opening stay open.
  Prefer a meaningful gap between connected-looking planes to puncturing one
  large slab with decorative slots. Keep enough shared contour direction that
  the parts still read as one object.
- **Technical accents and compact labels:** place the required information or
  aperture first, then fit its container. Group things by use, with one dominant
  reading cue and subordinate supporting marks. Repeated cuts share a direction
  and spacing logic and terminate cleanly into the structure. Do not add fields,
  pseudo-telemetry or a frame around every group to occupy unused space. Preserve
  required codes; do not claim a decorative barcode is scannable.
- **Illustrative scientific diagrams:** construct the explained relationship,
  then its axes, then the necessary reference notation. For a sparse printed
  idiom, choose a confident trace, quieter but robust axes, and related terminals;
  shape them as a family rather than aging a modern plot with a font or jitter.
  Add notation only where it identifies a relationship. For quantitative work,
  retain the true function, scale and labels needed to interpret it.

## Make a local correction after rendering

Use the documented renderer and inspect the image. Name the largest concrete
problem: an ambiguous overlap, a lost feature, a clogged opening, a useless
annotation, or a band that changes identity. Correct that relationship in the
SVG before polishing smaller marks. Zooming into a junction should confirm the
same structure seen at thumbnail size. Do not make every line heavier or every
empty area larger as a substitute for locating the problem.

Related background: [shape-conveying lines](https://gfx.cs.princeton.edu/proj/sugcon/index.html),
[joining and trimming](https://www.adobe.com/learn/illustrator/web/join-trim-paths-lines),
and [purpose-led layout](https://www.nps.gov/subjects/hfc/wayside-exhibit-design.htm).
These are adapted principles, not copied geometry or a formula for every style.
"""


def version_runtime():
    """Create auditable versioned files; do not alter old locked adapters."""
    plans = [
        ("pi_svg_procedural.py", "pi_svg_astra.py", [
            ("PiSvgProcedural", "PiSvgAstra"), ("pi-svg-procedural", "pi-svg-astra"),
            ("gpt-6-luna", "gpt-6-astra"), ("GPT-6 Luna", "GPT-6 Astra")]),
        ("run_procedural_pareto.py", "run_astra_pareto.py", [("gpt-6-luna", "gpt-6-astra")]),
        ("inspect_pareto_study.py", "inspect_astra_pareto.py", [("svt6", "svt8"), ("gpt-6-luna", "gpt-6-astra")]),
        ("seal_technique_evolution.py", "seal_astra_techniques.py", [
            ("svt1", "svt8"), ("luna-medium", "astra-medium"), ("gpt-6-luna", "gpt-6-astra"),
            ('"pi_svg_procedural.py"', '"pi_svg_astra.py"'),
            ('"run_procedural_population.py"', '"run_astra_pareto.py"'),
            ('    template = read(PRIOR / "future-job.json")',
             '    template = read(PRIOR / "future-job.json")\n'
             '    template["agents"][0].update(name="pi-svg-astra", import_path="pi_svg_astra:PiSvgAstra", model_name="openai-codex/gpt-6-astra")')]),
    ]
    result = {}
    for original, target, substitutions in plans:
        source = (HERE / original).read_text(encoding="utf-8")
        altered = source
        for before, after in substitutions:
            assert before in altered, (original, before)
            altered = altered.replace(before, after)
        destination = HERE / target
        if destination.exists():
            assert destination.read_text(encoding="utf-8") == altered
        else:
            destination.write_text(altered, encoding="utf-8")
        compile(altered, str(destination), "exec")
        result[target] = {"source": original, "source_sha256": sha(HERE / original),
                          "version_sha256": sha(destination), "substitutions": substitutions}
    return result


def main():
    runtime = version_runtime()
    prior = REPO / "evaluations/runs/svt7"
    closed = read(prior / "final-decision.json")
    assert not closed["private_gate_opened"] and not closed["reserved_cohort_consumed"]
    assert all(not (prior / p).exists() for p in ["validation-release-ready.json", "gate-started.json", "private-jobs", "pareto/holdout"])
    ROOT.mkdir(exist_ok=False)
    for name in ["development", "evaluator", "private"]:
        shutil.copytree(prior / name, ROOT / name)
        assert tree(prior / name) == tree(ROOT / name)
    for name in ["curation-status.json", "evaluator-extension.json"]:
        shutil.copy2(prior / name, ROOT / name)
    write(ROOT / "runtime-versioning.json", runtime)
    adoption = {"source_study": str(prior), "source_protocol_sha256": sha(prior / "protocol.json"),
        "source_closed_decision_sha256": sha(prior / "final-decision.json"), "private_tree_sha256": tree(ROOT / "private"),
        "cohort_was_unreleased": True, "cohort_was_unrun": True, "optimizer_content_read": False, "new_curation_calls": 0}
    write(ROOT / "cohort-adoption.json", adoption)
    previous = read(prior / "protocol.json")
    protocol = {
        "claim": "Separate Astra transfer profile: unchanged installed skill versus a purpose-matched mark-selection guide. Historical Luna comparison is descriptive, never pooled in Pareto.",
        "development": {"attempts": 3}, "validation": previous["validation"],
        "budget": {"max_development_generation_calls": 36, "max_validation_generation_calls": 12, "baseline_calls": 18,
                   "max_candidates": 1, "calls_per_candidate": 18, "observer_calls_max": 48, "jev_calls_max": 48,
                   "retries": 0, "curator_calls": 0, "maximum_generations": 1, "reflection_model_calls": 0},
        "selection": previous["selection"],
        "runtime": {"model": "openai-codex/gpt-6-astra", "model_revision_limitation": "Observed gpt-6-astra alias; no immutable provider checkpoint. Medium effort and 16384 output cap match the historical Luna profile."},
        "stopping": "One fixed changed candidate and one development generation. Freeze at most one eligible finalist for the once-only reserved gate. No same-study mutation, reselection or semantic retries. Preserve the baseline if qualification or guards fail.",
        "method": {"selection_owner": "harbor-reflective-pareto-search", "execution": "Unmodified native Pareto execute_job and analyze-only under an Astra-only comparison profile."},
        "candidate_ids": ["b", "c"], "pareto_adapter_sha256": sha(HERE / "run_astra_pareto.py"),
        "pareto_engine_sha256": sha(Path("C:/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py")),
        "cohort_adoption": adoption,
        "research": {"path": str(RESEARCH), "sha256": sha(RESEARCH), "status": "Unproven development hypothesis"},
        "historical_model_comparison": {"source": str(prior / "jobs/b"), "same_skill_bytes": True, "same_public_briefs": True,
            "contemporaneous": False, "paired_random_seeds": False, "pooled_native_selection": False},
    }
    from seal_astra_techniques import main as seal
    seal(ROOT, REPO / "skills/svg-brief-design", 1, False, protocol, attempts=3, evolution_owner="harbor-reflective-pareto-search")
    memory = {"research": {"path": str(RESEARCH), "sha256": sha(RESEARCH)},
              "allowed_public_evidence": {str(prior / p): sha(prior / p) for p in ["public-visual-review-g0.json", "public-print-review-g0.json", "pareto/development/generation-000/pareto-archive.json"]},
              "excluded": ["private tasks/outcomes", "source geometry", "evaluator preferences in generator input"]}
    write(ROOT / "development-memory.json", memory)
    org("record-evidence", ROOT / "study", "--evidence-id", "development-memory", "--stage-id", "evolve", "--kind", "other", "--role", "development", "--visibility", "private", "--path", ROOT / "development-memory.json")
    baseline = ROOT / "inputs/b/svg-brief-design"
    target = ROOT / "inputs/c/svg-brief-design"
    shutil.copytree(baseline, target)
    original = (target / "SKILL.md").read_text(encoding="utf-8")
    route = "For these illustration tasks, read `references/mark-selection.md` to select\na construction by purpose and assign each mark a job before adding detail.\n\n"
    assert original.count("## Build a useful base") == 1
    updated = original.replace("## Build a useful base", route + "## Build a useful base")
    (target / "SKILL.md").write_text(updated, encoding="utf-8")
    (target / "references/mark-selection.md").write_text(GUIDE, encoding="utf-8")
    for arm in ["b", "c"]:
        skill = ROOT / f"inputs/{arm}/svg-brief-design"
        subprocess.run([sys.executable, "-B", "scripts/test_scaffold.py"], cwd=skill, check=True)
        subprocess.run([sys.executable, "-B", "C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py", str(skill)], check=True)
        receipt(ROOT, arm)
    config = {"schemaVersion": 1,
        "search": {"id": "svg-purpose-astra-20260926", "baselineSkill": wsl(baseline), "baselineCandidate": "b", "outputDir": wsl(ROOT / "pareto"), "generation": 0},
        "harbor": {"developmentJob": wsl(ROOT / "templates/development.json"), "holdoutJob": wsl(ROOT / "templates/validation.json"), "rewardKey": "technique_quality", "passThreshold": 0, "requiredRewards": {"artifact_valid": 1}, "requiredEnv": ["OPENROUTER_API_KEY"]},
        "candidates": [{"id": arm, "skill": wsl(ROOT / f"inputs/{arm}/svg-brief-design"), "parents": [] if arm == "b" else ["b"],
            "rationale": "Installed skill unchanged on Astra" if arm == "b" else "Purpose-matched mark functions and local junction correction", "jobDirectory": wsl(ROOT / f"jobs/{arm}")} for arm in ["b", "c"]],
        "promotion": {"minimumMeanGain": .02, "allowCaseRegressions": True, "requireNoErrors": True}}
    write(ROOT / "pareto-g0.json", config)
    changes = {}
    for file in sorted(target.rglob("*")):
        if file.is_file():
            relative = file.relative_to(target)
            parent = baseline / relative
            if not parent.exists() or sha(parent) != sha(file):
                changes[relative.as_posix()] = "added" if not parent.exists() else "modified"
    assert changes == {"SKILL.md": "modified", "references/mark-selection.md": "added"}
    write(ROOT / "candidate-diff-audit.json", {"changes": changes, "scripts_unchanged": True, "runtime_model_independent_payload": True})
    from audit_procedural_payload import audit
    write(ROOT / "public-path-audit.json", {arm: audit(ROOT / f"inputs/{arm}/svg-brief-design", ROOT / "development") for arm in ["b", "c"]})
    write(ROOT / "freeze-receipt.json", {"frozen": True, "protocol_sha256": sha(ROOT / "protocol.json"), "development_memory_sha256": sha(ROOT / "development-memory.json"), "research_sha256": sha(RESEARCH), "validation_opened": False, "development_cases": 6, "attempts": 3, "canonical_unchanged": True})
    patch = "".join(difflib.unified_diff(original.splitlines(True), updated.splitlines(True), fromfile="a/SKILL.md", tofile="b/SKILL.md"))
    patch += "".join(difflib.unified_diff([], GUIDE.splitlines(True), fromfile="/dev/null", tofile="b/references/mark-selection.md"))
    (REPO / "evaluations/svg-brief-design/purpose-astra-c-20260926.patch").write_text(patch, encoding="utf-8")
    print(json.dumps({"ready": True, "root": str(ROOT), "public_generation_calls": 36, "model": "gpt-6-astra"}))


if __name__ == "__main__":
    main()
