#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML==6.0.2", "resvg-py==0.2.6", "Pillow==11.3.0", "defusedxml==0.7.1"]
# ///
"""Freeze a design-recommendation study using an explicitly unconsumed reserve."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from prepare_information_study import tree
from prepare_pareto_trace_study import receipt
from seal_technique_evolution import REPO, main as seal, org, read, sha, write, wsl

ROOT = REPO / "evaluations/runs/svt7"
RESEARCH = REPO / "projects/svg-brief-design/evaluation/design-craft-research-20260926.md"

CONTOUR = """# Contour and counterform decisions

Use this pass when an illustration depends on a silhouette, connected ornament,
or open internal structure. Preserve the brief's subject and required features.

## Decide the large shapes together

Before drawing small details, make a coarse material-and-void construction.
Choose the main gesture: where the form starts, changes direction and resolves.
Place its characteristic extrema and articulations along that gesture. A bounding
box and a collection of familiar icons do not establish the object's character.

Draw the important empty regions as shapes in their own right. Decide which
ones open to the exterior, where their mouths are, and which narrow necks must
remain visible. Let adjacent material share their contour directions so the eye
can continue across a gap. An internal slit cannot substitute for an open channel.
Do not maximize white area: preserve the connections needed to identify the form.

Keep this coarse pass editable, render it and inspect it before interior detail.
If it reads as one heavy slab, separate a meaningful plane or open a structural
channel. If it fragments, restore a shared direction or a necessary bridge.
Changing this large relationship is more useful than adding surface marks.

## Give contour changes a purpose

Use a broad sweep for the main motion; put corners, notches and changes of taper
where the structure changes. Avoid giving every segment the same length, every
opening the same shape, or every joint the same angle merely for consistency.
Rhythm can progress in scale or spacing while keeping a common curve character.

At each junction choose a clear union, a separated gap, or an intentional overlap.
Remove near-tangencies that almost touch and create pinched dark knots. For a
smooth Bezier join, place the adjacent control handles on opposite sides of the
shared point along one tangent; shorten them if they create an unwanted bulge.
Keep a deliberate corner when the subject needs one. Smoothness alone is not style.

For a curved band, coordinate both edges and the taper; independently decorative
curves often create accidental pockets. Inspect the space between repetitions as
carefully as their black contours. Do not close a required opening with a rim.

## Finish by subtraction and optical balance

Hide secondary groups in a working copy. The subject, gesture and required
openings should still read. Restore a mark only when it explains a plane, joint,
expression or requested information. Keep distinctive proportions; do not reduce
an expressive subject to interchangeable circles and polygons.

Check the visual weight around the focal area at thumbnail size. A protrusion or
heavy black patch can move the apparent center even inside a centered bounding
box. Adjust spacing or a secondary mass without destroying meaningful asymmetry.
At delivery size check that the narrowest meaningful channels remain open.
Do not use a universal ink percentage or symmetry score as an aesthetic target.

Use original paths and actual transparent openings. Keep the final SVG editable,
render after the final correction, and retain every relationship the user asked for.

Background principles: [Getty on design](https://www.getty.edu/education/teachers/building_lessons/formal_analysis2.html),
[The Met on relief printing](https://www.metmuseum.org/perspectives/materials-and-techniques-printmaking-woodcut),
and [SVG curve controls](https://www.w3.org/TR/SVG2/paths.html#PathDataCubicBezierCommands).
The construction pass above is a practical synthesis, not a recipe for any source image.
"""

PRINT = """# Print character and optical finishing

Use the historic section only for a requested print or vintage idiom. Use the
optical finishing pass for compact text and line art of any period. Preserve
required labels, factual relationships and the requested palette/background.

## Choose a mark-making method

Old printed images do not share one stroke style. Choose the relevant method
before adding effects. Relief-like work can use sturdy material shapes and
deliberate white cuts. Engraved work can use controlled swelling lines and spaced
hatching that follows a plane. A sparse printed technical figure may need only
an explanatory trace, axes and a few purposeful annotations, with no shading.
Do not mix these methods just to make a drawing look busier or more antique.

Give related marks a shared construction. Use a restrained family of weights;
vary a line through a continuous gesture or taper when that fits the medium.
If width variation matters, construct a filled outline rather than stacking
duplicate strokes. Coordinate arrowheads, terminal cuts and joins with the line
they belong to. Preserve a clean, confident contour before considering texture.

Do not jitter all points, pepper the canvas with damage, or distress type to
manufacture age. A historic idiom comes primarily from proportions, mark shape,
notation and spacing. Fine engraving remains a legitimate historic treatment;
thickening every element is not a universal improvement.

## Edit explanatory marks by their function

For a decorative diagram, start with the relationship the drawing explains.
Add a tick, letter, leader or symbol only if it identifies an otherwise ambiguous
part or was requested. Do not inherit a plotting program's grid, tick sequence,
legend and title by default. Keep the curve distinguishable where it approaches
an axis. If it genuinely touches or crosses, make that event intentional.

For quantitative work, preserve the actual data, scale, ticks and labels needed
to interpret it. Never move extrema, alter a function or remove an essential
measurement to improve an antique appearance. A restrained style is not an
excuse to omit the meaning of the diagram.

## Fit the content, then adjust it optically

For an identifier or small label, lay out the actual required strings first.
Let their hierarchy determine a compact occupied footprint and add the container
around it. Avoid starting with a large panel and inventing fields to fill it.
Related information shares an alignment and treatment; a rule should separate
real groups, not decorate every available edge.

Then judge visible glyph edges and nearby black masses, not only text boxes.
Adjust a small inset, tracking or baseline when the result looks crowded or
off-center. Preserve readable glyph proportions; do not squash text to fit.
Keep optical corrections small and inspect them at the intended size.

Render the final SVG and check the darkest junction, smallest essential opening,
longest label and most important curve. If ink-like marks merge at small size,
increase meaningful separation or simplify a subordinate mark. Do not add a
global blur: the deliverable remains a crisp, editable vector.

Background: [The Met on woodcut](https://www.metmuseum.org/perspectives/materials-and-techniques-printmaking-woodcut),
[The Met on engraving](https://www.metmuseum.org/perspectives/materials-and-techniques-printmaking-engraving),
and [Butterick on layout](https://practicaltypography.com/maxims-of-page-layout.html).
The SVG recommendations are a practical adaptation, not a claim that all historic
printing follows one visual formula.
"""


def configuration(name, arms, generation=0, parents=None, rationales=None):
    config = {
        "schemaVersion": 1,
        "search": {"id": "svg-design-craft-20260926", "baselineSkill": wsl(ROOT / "inputs/b/svg-brief-design"),
                   "baselineCandidate": "b", "outputDir": wsl(ROOT / "pareto"), "generation": generation},
        "harbor": {"developmentJob": wsl(ROOT / "templates/development.json"), "holdoutJob": wsl(ROOT / "templates/validation.json"),
                   "rewardKey": "technique_quality", "passThreshold": 0, "requiredRewards": {"artifact_valid": 1}, "requiredEnv": ["OPENROUTER_API_KEY"]},
        "candidates": [{"id": arm, "skill": wsl(ROOT / f"inputs/{arm}/svg-brief-design"),
                        "parents": (parents or {}).get(arm, [] if arm == "b" else ["b"]),
                        "rationale": (rationales or {}).get(arm, {"b": "Frozen installed baseline", "c": "Coarse contour and counterform construction before detail", "d": "Print-method selection and optical finishing", "p": "Development-supported Pareto reflection"}[arm]),
                        "jobDirectory": wsl(ROOT / f"jobs/{arm}")} for arm in arms],
        "promotion": {"minimumMeanGain": .02, "allowCaseRegressions": True, "requireNoErrors": True},
    }
    if generation:
        config["search"]["previousGenerationLog"] = wsl(ROOT / f"pareto/development/generation-{generation-1:03d}/pareto-archive.json")
    destination = ROOT / f"pareto-{name}.json"
    assert not destination.exists()
    write(destination, config)


def main():
    prior = REPO / "evaluations/runs/svt6"
    closed = read(prior / "final-decision.json")
    assert closed["private_gate_opened"] is False and closed["reserved_cohort_consumed"] is False
    assert all(not (prior / p).exists() for p in ["validation-release-ready.json", "gate-started.json", "private-jobs", "pareto/holdout"])
    ROOT.mkdir(exist_ok=False)
    for name in ["development", "evaluator", "private"]:
        shutil.copytree(prior / name, ROOT / name)
        assert tree(prior / name) == tree(ROOT / name)
    for name in ["curation-status.json", "evaluator-extension.json"]:
        shutil.copy2(prior / name, ROOT / name)
    adoption = {"source_study": str(prior), "source_protocol_sha256": sha(prior / "protocol.json"),
        "source_closed_decision_sha256": sha(prior / "final-decision.json"),
        "private_tree_sha256": tree(ROOT / "private"), "evaluator_lock_sha256": sha(ROOT / "evaluator/lock.json"),
        "cohort_was_unreleased": True, "cohort_was_unrun": True, "optimizer_content_read": False,
        "new_curation_calls": 0, "scope": "Provenance-preserving adoption of the unconsumed two-family svt6 reserve; not newly authored cases."}
    write(ROOT / "cohort-adoption.json", adoption)
    previous_protocol = read(prior / "protocol.json")
    protocol = {
        "claim": "Bounded native Pareto evaluation of new contour/counterform and print/optical design recommendations. No professional-parity or broad transfer claim.",
        "development": {"attempts": 3}, "validation": previous_protocol["validation"],
        "budget": {"max_development_generation_calls": 72, "max_validation_generation_calls": 12,
                   "baseline_calls": 18, "max_candidates": 3, "calls_per_candidate": 18,
                   "observer_calls_max": 84, "jev_calls_max": 84, "retries": 0,
                   "curator_calls": 0, "maximum_generations": 2, "reflection_model_calls": 0},
        "selection": previous_protocol["selection"],
        "stopping": "Generation zero compares the frozen baseline and two independent design proposals. Generation one permits at most one child supported by a qualified native Pareto parent and bounded public evidence. Retain all comparable completed jobs. Stop after that child or earlier if no safe supported mutation/qualified archive exists. At most three changed candidates. Freeze one eligible finalist before the once-only private gate. No same-study mutation or reselection after release; no semantic retries. Previous campaigns remain closed.",
        "method": {"selection_owner": "harbor-reflective-pareto-search", "execution": "Native Pareto execute_job and native analyze-only archive; unchanged strict qualification and scorer."},
        "candidate_ids": ["b", "c", "d", "p"],
        "pareto_adapter_sha256": sha(Path(__file__).with_name("run_procedural_pareto.py")),
        "pareto_engine_sha256": sha(Path("C:/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py")),
        "cohort_adoption": {"receipt_sha256": sha(ROOT / "cohort-adoption.json"), **adoption},
        "research": {"path": str(RESEARCH), "sha256": sha(RESEARCH), "status": "Hypotheses; effectiveness unproven before these jobs"},
    }
    seal(ROOT, REPO / "skills/svg-brief-design", 3, False, protocol, attempts=3, evolution_owner="harbor-reflective-pareto-search")
    memory = {"research": {"path": str(RESEARCH), "sha256": sha(RESEARCH)},
              "allowed_public_evidence": {str(prior / p): sha(prior / p) for p in ["public-visual-review-interim.json", "pareto/development/generation-000/pareto-archive.json"]},
              "excluded": ["private tasks", "private gate outcomes", "reference geometry in candidate bundles"],
              "new_mechanisms": {"c": "Decide counterforms and silhouette transitions in a coarse pass before detail", "d": "Choose a medium-specific mark grammar, then optically fit the actual information"}}
    write(ROOT / "development-memory.json", memory)
    org("record-evidence", ROOT / "study", "--evidence-id", "development-memory", "--stage-id", "evolve", "--kind", "other", "--role", "development", "--visibility", "private", "--path", ROOT / "development-memory.json")
    finish_candidates()


def finish_candidates():
    """Resume local preparation only; never rewrite sealed inputs or start a model."""
    assert not (ROOT / "freeze-receipt.json").exists()
    assert not list(ROOT.glob("started-*.json"))
    assert not list(ROOT.glob("input-*.json"))
    for arm, name, content, route in [
        ("c", "contour-counterform.md", CONTOUR, "For silhouettes, connected ornament or open internal structures, read\n[contour and counterform decisions](references/contour-counterform.md) and make\nthe coarse material-and-void pass before adding interior details.\n\n"),
        ("d", "print-optical-finish.md", PRINT, "For vintage or printed artwork, compact labels and line diagrams, read\n[print character and optical finishing](references/print-optical-finish.md)\nbefore choosing marks or laying out content.\n\n"),
    ]:
        target = ROOT / f"inputs/{arm}/svg-brief-design"
        baseline = ROOT / "inputs/b/svg-brief-design"
        text = (baseline / "SKILL.md").read_text(encoding="utf-8")
        assert text.count("## Build a useful base") == 1
        expected = text.replace("## Build a useful base", route + "## Build a useful base")
        if target.exists():
            assert (target / "SKILL.md").read_text(encoding="utf-8") == expected
            assert (target / "references" / name).read_text(encoding="utf-8") == content
            for file in baseline.rglob("*"):
                if file.is_file() and file.name != "SKILL.md":
                    assert sha(file) == sha(target / file.relative_to(baseline))
        else:
            shutil.copytree(baseline, target)
            (target / "SKILL.md").write_text(expected, encoding="utf-8")
            (target / "references" / name).write_text(content, encoding="utf-8")
        subprocess.run([sys.executable, "-B", "scripts/test_scaffold.py"], cwd=target, check=True)
        subprocess.run([sys.executable, "-B", "C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py", str(target)], check=True)
    for arm in ["b", "c", "d"]:
        receipt(ROOT, arm)
    from audit_procedural_payload import audit
    write(ROOT / "public-path-audit.json", {arm: audit(ROOT / f"inputs/{arm}/svg-brief-design", ROOT / "development") for arm in ["b", "c", "d"]})
    configuration("g0", ["b", "c", "d"])
    write(ROOT / "freeze-receipt.json", {"frozen": True, "protocol_sha256": sha(ROOT / "protocol.json"),
        "development_memory_sha256": sha(ROOT / "development-memory.json"), "research_sha256": sha(RESEARCH),
        "validation_opened": False, "new_curation_calls": 0, "development_cases": 6, "attempts": 3,
        "changed_files_per_candidate": 2, "canonical_unchanged": True})
    print(json.dumps({"ready": True, "study": str(ROOT), "first_generation_calls": 54, "max_total_calls": 84, "private_gate": "closed"}))


if __name__ == "__main__":
    if sys.argv[1:] == ["--finish-candidates"]:
        finish_candidates()
    else:
        assert not sys.argv[1:]
        main()
