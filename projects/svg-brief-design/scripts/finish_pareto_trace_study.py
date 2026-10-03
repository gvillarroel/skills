#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Close an inconclusive native Pareto pilot without opening its private gate.

The frozen study's failed baseline measurement cannot be recovered by the native
external-failure contract. Preserve candidates and report actual native results;
do not install an unvalidated bundle or manufacture an overall quality gain.
"""
import json
from pathlib import Path
import sys

from seal_technique_evolution import REPO, org, sha

ROOT = REPO / "evaluations/runs/svt6"


def read(path): return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)


def tree(path):
    return {p.relative_to(path).as_posix(): sha(p) for p in sorted(path.rglob("*")) if p.is_file()}


def main():
    generation = int(sys.argv[1])
    selection_path = ROOT / f"selection-g{generation}.json"
    selection = read(selection_path)
    assert selection["selected"] is None and not selection["validation_opened"]
    assert not (ROOT / "pareto/holdout").exists()
    archive_path = ROOT / f"pareto/development/generation-{generation:03d}/pareto-archive.json"
    archive = read(archive_path)
    assert not archive["archive"], "This closure is only for an empty qualified frontier"
    records = {r["candidateId"]: r for r in archive["candidateResults"]}
    assert "b" in records and set(records) <= {"b", "i", "t", "p"}
    audits = {arm: read(ROOT / f"audit-{arm}.json") for arm in records}
    assert any(audits["b"]["critic_provider_failures"])
    baseline_tree = tree(ROOT / "inputs/b/svg-brief-design")
    assert tree(REPO / "skills/svg-brief-design") == tree(REPO / ".agents/skills/svg-brief-design") == baseline_tree
    rows = []
    for arm, record in records.items():
        audit = audits[arm]
        external = bool(audit["critic_provider_failures"])
        rows.append({"candidate": arm, "files": len(tree(ROOT / f"inputs/{arm}/svg-brief-design")),
            "trials": audit["trials"], "errors": audit["errors"], "critic_provider_failures": len(audit["critic_provider_failures"]),
            "quality_mean": None if external else record["summary"]["meanReward"],
            "native_diagnostic_mean": record["summary"]["meanReward"],
            "qualified": record["qualification"]["passed"], "archive_member": any(a["candidateId"] == arm for a in archive["archive"]),
            "harbor_digest": record["skillDigest"], "model_aliases": audit["observed_generator_aliases"]})
    result = {"status": "no-qualified-pareto-candidate-and-incomplete-control", "installed": False,
        "methods": ["harbor-reflective-pareto-search", "harbor-trace-distillation"],
        "trace_role": "Native schema-1 diagnostic materialization; not Trace promotion",
        "generator": "openai-codex/gpt-6-luna", "thinking": "medium", "evaluator": "Jev 6.3 unchanged",
        "generation": generation, "new_generator_calls": sum(r["trials"] for r in rows), "retries": 0,
        "candidate_rows": rows, "native_archive_sha256": sha(archive_path), "selection_sha256": sha(selection_path),
        "unaffected_family_guards": {arm: values["unaffected_family_visual_guard"] for arm, values in selection["candidates"].items()},
        "protocol_sha256": sha(ROOT / "protocol.json"), "private_gate_opened": False,
        "reserved_family_count": 2, "reserved_cohort_consumed": False,
        "canonical_and_local_unchanged": True, "canonical_realizer_digest": "sha256:2ab3beca48e69f2c12c482a15a09821ff1794e2b1c44bbdbdd9f2388668e0318",
        "scope": "Six public semantic families with three fixed attempts. Every arm has a preserved execution error, so the native qualified Pareto frontier is empty and no descendant can be selected under the declared method. A missing provider-backed baseline review additionally prevents a complete paired claim. Error-derived native zeros are diagnostic bookkeeping, not Jev judgments.",
        "stopping_reason": "No qualified native archive member exists; the predeclared workflow stops before generation one and leaves independent validation unopened.",
        "generator_and_observer_cost": None, "cost_limitation": "Pi does not supply a reliable billed USD total; zero reported tokens/cost in the failed observer is not a price estimate for the experiment."}
    put(ROOT / "final-decision.json", result)
    evidence = [("native-pareto", "evolution-report", "development", archive_path),
                ("selection", "decision", "development", selection_path),
                ("trace-native", "evolution-report", "development", REPO / "evaluations/runs/svp5-trace-prep/trace-native-candidate-01"),
                ("trace-notes", "other", "development", REPO / "evaluations/runs/svp5-trace-prep/trace-patch-decisions.md"),
                ("recovery-audit", "other", "diagnostic", ROOT / "recovery-feasibility.md"),
                ("final-decision", "decision", "decision", ROOT / "final-decision.json")]
    for arm in records:
        evidence += [(f"job-{arm}", "native-job", "development", ROOT / f"jobs/{arm}"),
                     (f"input-{arm}", "candidate", "lineage", ROOT / f"inputs/{arm}/svg-brief-design")]
    for identifier, kind, role, path in evidence:
        org("record-evidence", ROOT / "study", "--evidence-id", identifier, "--stage-id", "evolve",
            "--kind", kind, "--role", role, "--visibility", "private", "--path", path)
    org("transition", ROOT / "study", "--stage-id", "evolve", "--status", "completed")
    org("transition", ROOT / "study", "--stage-id", "validate", "--status", "stopped")
    org("verify", ROOT / "study", "--render")
    destination = REPO / "evaluations/svg-brief-design/pareto-trace-20260926.json"
    put(destination, result)
    labels = {"b": "Installed baseline", "i": "Information editing", "t": "Trace recipe interface", "p": "Pareto reflection/merge"}
    table = []
    for row in rows:
        score = "Unavailable" if row["quality_mean"] is None else f'{100*row["quality_mean"]:.2f}'
        table.append(f'| {labels[row["candidate"]]} | {row["trials"]} | {row["errors"]} | {score} | {row["archive_member"]} |')
    text = f'''# SVG skill: native Pareto and parallel Trace, 2026-09-26

The requested methods were executed. Native Trace materialized an evidence-bound
candidate while a fresh GPT-6 Luna baseline ran; native Pareto compared all
frozen variants. **No variant qualified: every arm retained at least one
execution error, so the native Pareto frontier is empty.** The method therefore
has no eligible parent for its next generation. One baseline visual observer
also failed from provider overload, preventing a complete paired quality claim.
The source and local installation remain unchanged; the
fresh two-family validation cohort was not opened or consumed.

## Actual execution

Every artifact generator used **openai-codex/gpt-6-luna**, medium reasoning,
through Pi 0.84.2. The visual-observer/curator role uses the existing separate
Astra context; Jev 6.3 remains the unchanged score owner. There were
**{result['new_generator_calls']} fresh generator attempts**, six public semantic
families and three attempts per candidate, with no semantic retries.

| Variant | Attempts | Execution/evaluation errors | Native mean, 0–100 | Pareto member |
| --- | ---: | ---: | ---: | --- |
{chr(10).join(table)}

An error-derived zero in native bookkeeping is not a Jev quality judgment. The
baseline total is intentionally unavailable here because its external observer
failure has no measured quality. Means for any other unqualified variant also
include its native failure zeros and must not be read as professional grades.
The scorer estimates coded comparative technique utility, not pixel similarity
or absolute excellence. Three repetitions do not create three independent
families. See the native archive and all family-level guards for dispersion.

The predeclared sensitivity check keeps the three baseline families whose three
attempts all qualified: expressive figure, HUD and printed diagram. On this
limited subset the baseline mean is 62.79, information editing is 69.59
(+6.80 points), and Trace is 64.66 (+1.87). The information signal is concentrated
in HUD (+20.12); figure (+0.04) and printed diagram (+0.24) are nearly unchanged.
Trace's printed-diagram mean falls 2.45 points. These are development diagnostics,
not complete paired results, statistical significance, or evidence of general
professional mastery. They do not rescue either candidate's qualification error.

## What Trace changed

The actual Trace executable imported 24 immutable public baseline trials from
the preceding studies. Its one accepted proposal cites five trials across two
semantic families, including successful behavior and counterexamples. It adds
17 net lines only to the scaffold recipe reference: legal numeric stroke range,
the distinction from SVG no-stroke painting, supported detail attributes, and
direct SVG finishing when a valid attribute is outside the recipe interface.
All geometry and scripts remain unchanged. This is an operational hypothesis;
the new model results, not the patch's plausibility, determine its utility.

Historical raw retry locks omit a field required by Trace schema 2. They were
not repaired. Trace therefore used its native schema-1 **analyze-only** route
for diagnosis/materialization, with the outer frozen Pareto study owning new
execution and the independent gate. Its native `not-evaluated` receipt does not
claim Trace promotion. The complete accepted/rejected patch notes preserve six
directions that lacked sufficient support.

## Isolation and disposition

The initial three-family reserve was rejected before any artifact generation.
A new authoring version independently reviewed the same random inventory under
a predeclared two-family pilot claim and approved it. No scoring/profile/source
exclusion was relaxed and no candidate result entered curation. Both reserved
families remain unused; a future study must explicitly account for this reserve.

The provider-overload evidence was independently audited against the native
external-recovery contract. Its generic RuntimeError and critic event log do
not meet the exact structured eligibility inputs; verifier-only recovery also
excludes a provider failure after verification began. No failure record was
rewritten, no review replayed, and no new baseline draw substituted.

The frozen final-selection rule requires an error-free eligible candidate and
a complete evaluable comparison. Neither condition is met. No candidate was
installed and no private task was exposed to select another. Generation one
was not fabricated from an ineligible parent, and the unused third-candidate
slot was not used to restart the search under a changed rule.
The canonical/local nine-file realizer digest remains
`2ab3beca48e69f2c12c482a15a09821ff1794e2b1c44bbdbdd9f2388668e0318`.
The earlier three-rejection campaign remains closed; this bounded study is
separate and does not relabel an external outage as a failed artistic mutation.

## Evidence

- [Frozen protocol](../runs/svt6/protocol.json)
- [Native Pareto archive](../runs/svt6/pareto/development/generation-{generation:03d}/pareto-archive.json)
- [Native reflection plan](../runs/svt6/pareto/development/generation-{generation:03d}/reflection-plan.json)
- [Declared selection guards](../runs/svt6/selection-g{generation}.json)
- [Trace accepted/rejected decisions](../runs/svp5-trace-prep/trace-patch-decisions.md)
- [Native Trace report](../runs/svp5-trace-prep/trace-native-candidate-01/report.md)
- [Recovery feasibility audit](../runs/svt6/recovery-feasibility.md)
- [Final decision](../runs/svt6/final-decision.json)
- [Study status](../runs/svt6/study/status.md)
- [All information-candidate outputs](../runs/svt6/gallery-i/index.html)
- [All Trace-candidate outputs](../runs/svt6/gallery-t/index.html)

Both responsive galleries contain all three fixed attempts per family. A failed
attempt that preserved an SVG is rendered afterward outside the immutable job
for human review, explicitly without a quality score. Native mechanical/failure
zeros are never labeled as Jev judgments, and families with a failed attempt do
not display an aggregate visual gain. Earlier failed/draft gallery builds were
preserved locally; no model, original artifact, or verifier was replayed.

Validation: Trace's 13 scaffold tests, information candidate's 13 scaffold plus
four proof tests, structural/independence/payload checks, and the 52-path audit
against six public references passed. No source SVG, stored artwork or copied
long source path entered the candidate bundles. Repository pattern IDs, skill
validation, independence and payload gates passed. Pi billing totals are not
available; reported zero cost is not interpreted as free execution.
'''
    report = destination.with_suffix(".md")
    with report.open("x", encoding="utf-8") as handle:
        handle.write(text)
    print(json.dumps({"report": str(report), "new_generator_calls": result["new_generator_calls"],
        "installed": False, "private_gate_opened": False, "canonical_unchanged": True}))


if __name__ == "__main__":
    main()
