#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Audit, package and report the separate Astra profile without rescoring."""
from collections import Counter
import json
from pathlib import Path
import re
import statistics
import sys
import xml.etree.ElementTree as ET
import zipfile

from inspect_technique_evolution import collect, sha
from seal_technique_evolution import org, read, write

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svt8"
PRIOR = REPO / "evaluations/runs/svt7"


def put(path, value):
    assert not path.exists(), path
    write(path, value)


def preflight():
    current = read(ROOT / "templates/development.json")
    historical = read(PRIOR / "templates/development.json")
    expected = json.loads(json.dumps(historical).replace("/svt7/", "/svt8/"))
    expected["agents"][0].update(name="pi-svg-astra", import_path="pi_svg_astra:PiSvgAstra", model_name="openai-codex/gpt-6-astra")
    assert current == expected
    assert read(ROOT / "input-b.json")["files"] == read(PRIOR / "input-b.json")["files"]
    assert read(ROOT / "input-b.json")["harbor_digest"] == read(PRIOR / "input-b.json")["harbor_digest"]
    for arm in ["b", "c"]:
        skill = ROOT / f"inputs/{arm}/svg-brief-design"
        assert read(ROOT / f"input-{arm}.json")["files"] == {p.relative_to(skill).as_posix(): sha(p) for p in skill.rglob("*") if p.is_file()}
    references, paths = set(), set()
    for task in sorted((ROOT / "development").iterdir()):
        if not task.is_dir():
            continue
        spec = read(task / "tests/quality-anchor.json")
        source = (ROOT / "evaluator" / spec["file"]).resolve()
        assert source.is_relative_to((ROOT / "evaluator").resolve())
        assert sha(source) == spec["sha256"].removeprefix("sha256:")
        references.add(sha(source))
        for node in ET.fromstring(source.read_bytes()).iter():
            data = re.sub(r"\s+", " ", node.get("d", "")).strip()
            if len(data) >= 80:
                paths.add(data)
    arms = {}
    for arm in ["b", "c"]:
        skill = ROOT / f"inputs/{arm}/svg-brief-design"
        content = re.sub(r"\s+", " ", "\n".join(p.read_text(encoding="utf-8") for p in skill.rglob("*") if p.is_file()))
        assert not any(path in content for path in paths)
        arms[arm] = {"source_references": len(references), "long_paths_compared": len(paths), "exact_copies": 0}
    put(ROOT / "public-reference-check.json", {"passed": True, "arms": arms, "private_sources_read": False,
        "scope": "Packaging and exact long-path reuse checks; cannot exclude every transformed reconstruction."})
    put(ROOT / "model-transfer-audit.json", {"passed": True, "same_baseline_skill_digest": True,
        "same_job_config_except_model_adapter_identity_and_root": True, "same_medium_effort_and_output_cap": True,
        "historical_source": str(PRIOR), "historical_comparison_not_contemporaneous": True})
    print(json.dumps({"passed": True, "public_references": len(references), "long_paths": len(paths)}))


def progress():
    result = {}
    for arm in ["b", "c"]:
        job = ROOT / f"jobs/{arm}"
        models, stops = Counter(), Counter()
        for trace in job.glob("*/agent/pi.txt"):
            for line in trace.read_text(encoding="utf-8").splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                message = event.get("message", {})
                if event.get("type") == "message_end" and message.get("role") == "assistant":
                    models[message.get("model")] += 1
                    stops[message.get("stopReason")] += 1
        rows = collect(job)
        result[arm] = {"terminal_trials": len(rows), "errors": sum(bool(r["exception"]) for r in rows),
            "observed_models": dict(models), "assistant_stops": dict(stops),
            "job_finished": (job / "result.json").exists() and bool(read(job / "result.json").get("finished_at"))}
    print(json.dumps(result))


def summarize():
    sets = {"luna_b_historical": collect(PRIOR / "jobs/b", 18), "astra_b": collect(ROOT / "jobs/b", 18), "astra_c": collect(ROOT / "jobs/c", 18)}
    families = {}
    for task in sorted({row["task"] for rows in sets.values() for row in rows}):
        families[task] = {}
        for arm, rows in sets.items():
            cases = [r for r in rows if r["task"] == task]
            valid = [r for r in cases if not r["exception"] and r["reward"].get("artifact_valid") == 1 and r["overall"] is not None and "technique_quality" in r["reward"]]
            families[task][arm] = {"attempts": len(cases), "scored": len(valid),
                "mean_100": statistics.mean(r["reward"]["technique_quality"] for r in valid)*100 if len(valid) == 3 else None,
                "scores_100": [r["reward"].get("technique_quality", 0)*100 if r in valid else None for r in cases]}
            measures = [read(Path(r["verifier_path"]) / "metrics.json") for r in valid]
            dimensions = sorted({key for m in measures for key in m.get("dimension_expected_points", {})})
            families[task][arm]["dimensions_100"] = {
                key: statistics.mean(m["dimension_expected_points"][key] for m in measures)
                for key in dimensions if len(valid) == 3 and all(key in m.get("dimension_expected_points", {}) for m in measures)}
            preferences = Counter()
            for r in valid:
                choice = r["overall"]
                preference = "generated" if choice == r["candidate_side"] else "reference" if choice in {"A", "B"} else str(choice)
                preferences[preference] += 1
            families[task][arm]["judged_preferences"] = dict(preferences)
    totals = {}
    for arm, rows in sets.items():
        means = [f[arm]["mean_100"] for f in families.values()]
        totals[arm] = {"mean_100": statistics.mean(means) if all(v is not None for v in means) else None,
            "errors": sum(bool(r["exception"]) for r in rows), "review_flags": sum(bool(r["review_recommended"]) for r in rows),
            "preview_reads": sum(r["preview_reads"] > 0 for r in rows), "scaffold_uses": sum(r["scaffold_used"] for r in rows)}
    common = [task for task, f in families.items() if f["luna_b_historical"]["mean_100"] is not None and f["astra_b"]["mean_100"] is not None]
    model_change = {"complete_families": len(common), "historical_not_causal": True,
        "mean_delta_100": statistics.mean(families[t]["astra_b"]["mean_100"] - families[t]["luna_b_historical"]["mean_100"] for t in common) if common else None}
    guide_reads = 0
    for trace in (ROOT / "jobs/c").glob("*/agent/pi.txt"):
        calls = []
        for line in trace.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "tool_execution_start":
                calls.append(json.dumps(event.get("args", {})))
        guide_reads += any("references/mark-selection.md" in c for c in calls)
    result = {"families": families, "totals": totals, "model_change": model_change, "candidate_guide_reads": guide_reads,
        "source_jobs": {"luna_b_historical": str(PRIOR / "jobs/b"), "astra_b": str(ROOT / "jobs/b"), "astra_c": str(ROOT / "jobs/c")},
        "selection": read(ROOT / "selection-g0.json"), "same_model_pareto_only": True, "evaluator_unchanged": True}
    put(ROOT / "comparison-summary.json", result)
    print(json.dumps({"totals": totals, "model_change": model_change, "guide_reads": guide_reads, "families": families}, indent=2))


def packages():
    output = ROOT / "packages"
    output.mkdir(exist_ok=False)
    for arm, version in [("b", "current"), ("c", "purpose-guide-experimental")]:
        skill = ROOT / f"inputs/{arm}/svg-brief-design"
        destination = output / f"svg-brief-design-astra-{version}.zip"
        with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(skill.rglob("*")):
                if file.is_file():
                    archive.write(file, "svg-brief-design/" + file.relative_to(skill).as_posix())
        with zipfile.ZipFile(destination) as archive:
            import hashlib
            assert {n.removeprefix("svg-brief-design/"): hashlib.sha256(archive.read(n)).hexdigest() for n in archive.namelist()} == read(ROOT / f"input-{arm}.json")["files"]
    profile = {"provider": "openai-codex", "model": "gpt-6-astra", "thinking": "medium", "pi_version": "0.84.2",
        "skill_name": "svg-brief-design", "skill_selects_model": False,
        "versions": {arm: {"status": "installed-content" if arm == "b" else "experimental-not-promoted", **read(ROOT / f"input-{arm}.json")} for arm in ["b", "c"]},
        "reproduction_config": str(ROOT / "templates/development.json"), "no_purchased_artwork_in_archives": True}
    write(output / "astra-profile.json", profile)
    print(json.dumps({"packages": str(output), "zip_contents_verified": True}))


def close_without_promotion():
    selection = read(ROOT / "selection-g0.json")
    assert selection["selected"] is None
    assert not (ROOT / "validation-release-ready.json").exists()
    assert not (ROOT / "pareto/holdout").exists()
    archive_path = ROOT / "pareto/development/generation-000/pareto-archive.json"
    archive = read(archive_path)
    summary = read(ROOT / "comparison-summary.json")
    expected = read(ROOT / "input-b.json")["files"]
    for skill in [REPO / "skills/svg-brief-design", REPO / ".agents/skills/svg-brief-design"]:
        assert {p.relative_to(skill).as_posix(): sha(p) for p in skill.rglob("*") if p.is_file()} == expected
    result = {"status": "no-selected-improvement", "model": "openai-codex/gpt-6-astra", "thinking": "medium",
        "new_generator_calls": 36, "retries": 0, "evaluator": "Jev 6.3 unchanged", "installed": False,
        "canonical_and_local_unchanged": True, "private_gate_opened": False, "reserved_cohort_consumed": False,
        "archive": [r["candidateId"] for r in archive["archive"]],
        "native_archive_sha256": sha(archive_path), "selection_sha256": sha(ROOT / "selection-g0.json"),
        "protocol_sha256": sha(ROOT / "protocol.json"), "summary_sha256": sha(ROOT / "comparison-summary.json"),
        "model_change": summary["model_change"], "totals": summary["totals"],
        "candidate_guide_reads": summary["candidate_guide_reads"],
        "candidate_guards": selection["candidates"],
        "cost": None, "cost_note": "No reliable provider invoice supplied by this adapter; no cost estimate presented as measured."}
    put(ROOT / "final-decision.json", result)
    evidence = [("native-pareto", "evolution-report", "development", archive_path),
                ("selection", "decision", "development", ROOT / "selection-g0.json"),
                ("final-decision", "decision", "decision", ROOT / "final-decision.json"),
                ("reference-audit", "other", "diagnostic", ROOT / "public-reference-check.json"),
                ("model-transfer", "other", "diagnostic", ROOT / "model-transfer-audit.json"),
                ("comparison", "other", "development", ROOT / "comparison-summary.json")]
    for arm in ["b", "c"]:
        assert len(collect(ROOT / f"jobs/{arm}", 18)) == 18
        evidence.extend([(f"job-{arm}", "native-job", "development", ROOT / f"jobs/{arm}"),
                         (f"bundle-{arm}", "candidate", "lineage", ROOT / f"inputs/{arm}/svg-brief-design")])
    for identity, kind, role, path in evidence:
        org("record-evidence", ROOT / "study", "--stage-id", "evolve", "--evidence-id", identity,
            "--kind", kind, "--role", role, "--visibility", "private", "--path", path)
    org("transition", ROOT / "study", "--stage-id", "evolve", "--status", "completed")
    org("transition", ROOT / "study", "--stage-id", "validate", "--status", "stopped",
        "--note", "No candidate passes the frozen selection guards. Astra versions retained; original installed skill and unconsumed reserve preserved.")
    org("verify", ROOT / "study")
    put(REPO / "evaluations/svg-brief-design/purpose-astra-20260926.json", result)
    print(json.dumps({"closed": True, "installed": False, "private_gate_opened": False}))


def export_outputs():
    destination = ROOT / "packages/astra-generated-svg.zip"
    manifest = {"model": "gpt-6-astra", "thinking": "medium", "purchased_artwork_included": False,
        "failed_attempts_are_not_quality_grades": True, "outputs": []}
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for arm, label in [("b", "current"), ("c", "experimental")]:
            for row in collect(ROOT / f"jobs/{arm}", 18):
                text = (ROOT / "development" / row["task"] / "instruction.md").read_text(encoding="utf-8")
                required = re.findall(r"`(/logs/artifacts/[^`]+\.svg)`", text)
                assert len(set(required)) == 1
                trial = ROOT / f"jobs/{arm}" / row["trial"]
                source = trial / "artifacts" / required[0].lstrip("/")
                assert source.resolve().is_relative_to((trial / "artifacts").resolve())
                scored = not row["exception"] and row["reward"].get("artifact_valid") == 1 and row["overall"] is not None
                name = f'{label}/{row["trial"]}.svg' if source.is_file() else None
                if name:
                    archive.write(source, name)
                manifest["outputs"].append({"file": name, "trial": row["trial"], "version": label,
                    "sha256": sha(source) if name else None, "jev_scored": scored,
                    "score_100": row["reward"].get("technique_quality", 0)*100 if scored else None,
                    "error_type": row["exception"]["exception_type"] if row["exception"] else None})
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
    put(ROOT / "generated-export.json", {"zip": str(destination), "sha256": sha(destination),
        "attempt_slots": len(manifest["outputs"]), "svg_files": sum(bool(r["file"]) for r in manifest["outputs"]),
        "purchased_artwork_included": False})
    print(json.dumps(read(ROOT / "generated-export.json")))


def markdown_report():
    summary = read(ROOT / "comparison-summary.json")
    decision = read(ROOT / "final-decision.json")
    labels = {"004": "Expressive figure", "011": "Integrated ornament", "019": "Compact HUD",
              "020": "Compact label", "024": "Vintage diagram", "030": "Open space insignia"}
    rows = []
    for task, measures in summary["families"].items():
        cells = []
        for arm in ["luna_b_historical", "astra_b", "astra_c"]:
            value = measures[arm]
            cells.append(f'{value["mean_100"]:.2f}' if value["mean_100"] is not None else f'Unavailable ({value["scored"]}/3 judged)')
        b, c = measures["astra_b"]["mean_100"], measures["astra_c"]["mean_100"]
        delta = f'{c-b:+.2f}' if b is not None and c is not None else "Unavailable"
        rows.append("| " + " | ".join([labels[task.split("--")[0][-3:]], *cells, delta]) + " |")
    audit = {arm: read(ROOT / f"audit-{arm}.json") for arm in ["b", "c"]}
    native = read(ROOT / "pareto/development/generation-000/pareto-archive.json")
    qualification = {r["candidateId"]: r["qualification"]["passed"] for r in native["candidateResults"]}
    current = read(ROOT / "input-b.json")
    candidate = read(ROOT / "input-c.json")
    text = f'''# Purpose-matched techniques and the same SVG skill on Astra

Date: 2026-09-26. Status: completed public comparison; no skill promotion.

The installed skill was evaluated unchanged on exact GPT-6 Astra medium. One
experimental variant adds a conditional mark-selection guide, leaving all helper
code unchanged. Both full bundles and every public attempt are preserved.

## Results

Scores below are native Jev 6.3 expected reference-relative utility, scaled to
100. They are not absolute design grades or pixel similarity. The reference
parity convention is 90, and uncertainty across categories affects the scalar.
Every displayed family mean requires all three scored, error-free attempts.

| Family | Luna current skill, historical | Astra current skill | Astra new guide | Guide minus current on Astra |
| --- | ---: | ---: | ---: | ---: |
''' + "\n".join(rows) + f'''

The same-skill historical model contrast has {summary["model_change"]["complete_families"]}
complete shared families and a mean difference of
{summary["model_change"]["mean_delta_100"]:+.2f} points. This is a descriptive model
transfer result, not a randomized contemporaneous model comparison. Missing
families are disclosed above and are not silently assigned zeros or partial means.
The full per-attempt values, native dimensions and reference preferences are in
[the comparison data](../runs/svt8/comparison-summary.json).

## Native Pareto decision and failures

| Arm | Attempts | Trial errors | Tool-error events | Visual-provider failures | Native qualified |
| --- | ---: | ---: | ---: | ---: | --- |
| Current | 18 | {audit["b"]["errors"]} | {len(audit["b"]["tool_failures"])} | {len(audit["b"]["critic_provider_failures"])} | {qualification["b"]} |
| New guide | 18 | {audit["c"]["errors"]} | {len(audit["c"]["tool_failures"])} | {len(audit["c"]["critic_provider_failures"])} | {qualification["c"]} |

Native archive: {decision["archive"]}. No finalist passes the frozen guards.
The baseline contains an external visual-observer service failure; that leaves
one generated SVG without a quality judgment and makes the full comparison
inconclusive under the frozen rule. The candidate's two preserved tool failures
occurred in label tasks: a font-resource probe exited unsuccessfully, and a
render operation rejected an invalid SVG size. They are separate from the
observer service failure. Native diagnostic means can contain failure zeros; they are
not presented as visual-quality means here. There were no retries, rescoring,
post-hoc evaluator changes, or private gate calls.

The installed and local skill remain unchanged. The adopted two-family private
reserve was neither opened nor consumed. The one-generation experiment is closed;
the earlier three-rejection campaign has not been reset.

## What changed and why

The earlier contour/print proposals supplied broad advice that did not reliably
select the right construction. The new guide chooses by intended use and assigns
each mark a representational function: boundary, occlusion, plane change, joint,
trace, identifier or requested ornament. It then addresses local construction:

- Expressive figures: landmarks and meaningful plane relationships, preserving
  mood rather than forcing a generic pictogram grid.
- Interlaced ornament: resolve a band's adjacent void and each union, separation
  or crossing before repeating it; coordinate both band edges.
- Open mechanical forms: align separated masses and exterior channels along
  a shared directional structure.
- Compact technical graphics: actual content or aperture determines the frame,
  with one reading cue and only functional supporting marks.
- Editorial scientific diagrams: the relationship determines axes and notation;
  printed mark character must come from related traces and terminals.

This is an experimental synthesis. Princeton/Rutgers research supports selecting
shape-conveying lines; Adobe documents joining, trimming and variable width;
NPS design guidance ties layout and label hierarchy to purpose. None establishes
that these instructions improve generated SVGs. IBM's fixed pictogram grid was
explicitly rejected as a general style recipe. See the
[source review and applicability limits](../../projects/svg-brief-design/evaluation/purpose-techniques-astra-20260926.md).

Only `SKILL.md` routing and `references/mark-selection.md` differ from the parent.
The guide was observed in {summary["candidate_guide_reads"]}/18 candidate traces.
The [exact patch](purpose-astra-c-20260926.patch) and
[file-difference audit](../runs/svt8/candidate-diff-audit.json) preserve the change.

## Visual interpretation

The current Astra outputs show better controlled mechanical planes and compact
layout in several cases, while the reviewed ornament still uses uniform strands
and the vintage diagram still resembles a modern mathematical plot. The new
guide's first ornament retains thin interrupted curves, with weak terminal and
band relationships; the first diagram retains uniform treatment. Cleaner SVG
geometry and fewer labels are insufficient evidence of editorial finish.

These are located public observations, not additional scores. They were recorded
after the candidate was frozen and did not change it or the evaluation. See
[the baseline observations](../runs/svt8/public-visual-review-b.json) and the
all-attempt galleries below. A high utility score in one family does not establish
professional parity across the portfolio.

## Versions and outputs

- [Current skill archive for Astra](../runs/svt8/packages/svg-brief-design-astra-current.zip)
  contains the exact installed nine-file bundle.
- [Experimental guide archive for Astra](../runs/svt8/packages/svg-brief-design-astra-purpose-guide-experimental.zip)
  contains the ten-file variant. It is not promoted or installed.
- [Usage instructions](../runs/svt8/packages/USAGE.md) explain loading one bundle
  and selecting Astra externally; the skill does not choose its own model.
- [Exact Astra profile and file hashes](../runs/svt8/packages/astra-profile.json).
- [Luna/Astra generated-output gallery](../runs/svt8/gallery-models/index.html)
  contains all 54 historical/current/experimental attempt slots and no purchased
  artwork. Rows are display pairings, not shared random seeds.
- [Astra comparison with purchased reference previews](../runs/svt8/gallery-c/index.html)
  is for the owner's local review. It includes all 36 Astra attempt slots.
- [Editable generated SVG package](../runs/svt8/packages/astra-generated-svg.zip)
  includes available generated files and a manifest distinguishing scored and
  failed attempts; purchased references are excluded.

Native bundle digests:

- Current: `{current["harbor_digest"]}`.
- Experimental: `{candidate["harbor_digest"]}`.

## Controls and scope

The runtime adapter is a versioned Astra counterpart; old sealed Luna helpers and
jobs were not rewritten. The [transfer audit](../runs/svt8/model-transfer-audit.json)
checks identical baseline bytes and native configuration except model/adapter
identity and study paths. Both profiles retain Pi 0.84.2, medium effort, the
configured 16,384 output cap, container, tools, time limits, three attempts,
concurrency three and unchanged Jev 6.3. The new guide has not been tested on Luna.

All 36 new traces report `gpt-6-astra`. Input isolation and unchanged-bundle
receipts pass for both arms. Both 13-test scaffold suites and skill quick
validation pass. A packaging and public-reference audit found zero exact reuse
among 52 long paths from six public sources; this does not exclude every possible
transformed reconstruction. No purchased SVG, benchmark identities or recorded
answers are inside either skill archive. Archive contents were checked against
the frozen file hashes.

Native evidence: [protocol](../runs/svt8/protocol.json),
[Pareto archive](../runs/svt8/pareto/development/generation-000/pareto-archive.json),
[selection](../runs/svt8/selection-g0.json),
[final decision](../runs/svt8/final-decision.json),
[organizer status](../runs/svt8/study/status.md).
The judge includes subjective and low-confidence fields, the cohorts are small,
and the models are provider aliases without an immutable checkpoint. No broad
statistical superiority, independent effect of individual rules, or measured
provider cost is claimed.
'''
    destination = REPO / "evaluations/svg-brief-design/purpose-astra-20260926.md"
    assert not destination.exists()
    destination.write_text(text, encoding="utf-8")
    print(json.dumps({"report": str(destination)}))


if __name__ == "__main__":
    {"preflight": preflight, "progress": progress, "summarize": summarize, "packages": packages,
     "close": close_without_promotion, "export-outputs": export_outputs, "report": markdown_report}[sys.argv[1]]()
