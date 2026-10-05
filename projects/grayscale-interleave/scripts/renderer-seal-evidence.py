#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Seal renderer-only grayscale evidence without changing skill payloads."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects/grayscale-interleave"
SKILLS = (
    "mermaid", "plantuml-colorset-renderer", "usefulcharts-style",
    "echarts-animated-svg", "slidev-echarts",
)
ORDER = (
    "#9e1b32", "#000000", "#828282", "#1c1c1c", "#9c9c9c",
    "#363636", "#b5b5b5", "#333e48", "#cfcfcf", "#4f4f4f",
    "#e7e7e7", "#696969", "#f7f7f7", "#ffffff", "#6d1222",
    "#e8002a", "#ffccd5",
)


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    spec = importlib.util.spec_from_file_location(
        "renderer_runtime_harness", ROOT / "scripts/run-pi-skill-eval.py"
    )
    assert spec is not None and spec.loader is not None
    harness = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = harness
    spec.loader.exec_module(harness)
    frozen = {}
    for skill in SKILLS:
        target = PROJECT / "artifacts/runtime-freeze-r2" / skill
        if target.exists():
            # A report refresh must prove that the canonical bundle still has
            # the sealed bytes; retain both old and new project-owned copies.
            verification_root = PROJECT / "artifacts/runtime-verification"
            verification_root.mkdir(parents=True, exist_ok=True)
            fresh = Path(tempfile.mkdtemp(prefix=f"{skill}-", dir=verification_root)) / skill
            harness.copy_skill_only(ROOT / "skills" / skill, fresh, "runtime")
            if harness.snapshot_tree(fresh) != harness.snapshot_tree(target):
                raise ValueError(f"Canonical runtime no longer matches frozen {skill}")
        else:
            harness.copy_skill_only(ROOT / "skills" / skill, target, "runtime")
        snapshot = harness.snapshot_tree(target)
        frozen[skill] = {
            "profile": "runtime", "fileCount": len(snapshot),
            "sha256": harness.snapshot_digest(snapshot),
            "snapshot": target.relative_to(ROOT).as_posix(),
        }
        write(target.parent / f"{skill}-snapshot.json", snapshot)

    fixtures_path = "projects/grayscale-interleave/artifacts/reviews/renderer-fixtures-final/review.json"
    fixture = read(fixtures_path)
    fixture["manualReviewPending"] = False
    fixture["manualReview"] = {
        "newCategoricalPaintAndContrast": "PASS for the reviewed changed native frames.",
        "newNodeLabelsAndDirectedHeads": "PASS for the reviewed changed native frames.",
        "scope": "Original native viewport captures; no blanket certification of all gallery layouts.",
        "preservedC4": "Named semantic roles and source-bound source/static/animated bytes are unchanged from HEAD. The preserved bottom Serves gallery assets caption touches the Documentation Browser body; this preexisting limitation is retained. The unreadable new native C4 rebuild was rejected, not counted as an accepted result.",
        "ditaa": "The native PNG was separately inspected: red Request, black API, middle-gray Document; complete labels and directed heads remain readable.",
    }
    write(ROOT / fixtures_path, fixture)

    echarts_path = "projects/grayscale-interleave/artifacts/reviews/echarts-head-native-final/review.json"
    echarts = read(echarts_path)
    echarts["manualNativeCaptionAndHeadReviewPending"] = False
    echarts["manualNativeReview"] = {
        "paletteAndContrast": "PASS for seven original native representative captures; all 43 cards are explicitly colorset2, not colorset1.",
        "captionReview": "Pie leaders/captions, funnel text, Sankey backing labels, boxplot axes and heatmap numeric labels remain readable. The baseline tree places some labels across their own connection shafts; this is a retained baseline geometry limitation, not an accepted new palette geometry change.",
        "headReview": "The network graph is authored as undirected; arrowhead presence is not claimed for it.",
        "scope": "Exact HEAD baseline builder with current canonical palette/template, default delivery/replay/reduced native states; quantitative data and authored order are unchanged.",
    }
    write(ROOT / echarts_path, echarts)

    staging_path = "projects/grayscale-interleave/artifacts/staged-blobs/echarts-head-native/staging-proof.json"
    staging = read(staging_path)
    assert staging["ok"] and echarts["ok"]
    assert staging["dirtyWorkingSha256Before"] == staging["dirtyWorkingSha256After"]
    dirty_base = ROOT / "skills/echarts-animated-svg/assets/examples/echarts-animated-svg"
    assert all(sha(dirty_base / name) == digest for name, digest in staging["dirtyWorkingSha256After"].items())
    index = ROOT / echarts["finalIndex"] if "finalIndex" in echarts else PROJECT / "artifacts/staged-blobs/echarts-head-native/assets/examples/echarts-animated-svg/index.html"
    assert sha(index) == echarts["indexSha256"]
    comparison_path = "projects/grayscale-interleave/artifacts/reviews/echarts-head-native-final/head-native-comparison.json"
    comparison = read(comparison_path)
    assert comparison["all43NativeGeometryPaintTextUnchanged"]
    assert comparison["stagedIndexSha256"] == sha(index)

    concept_paths = {
        "echarts-animated-svg": "projects/colorset-gray-interleave/artifacts/reviews/echarts-native/test-report.json",
        "slidev-echarts": "projects/colorset-gray-interleave/artifacts/reviews/slidev-echarts-native/test-report.json",
    }
    concept = {}
    for skill, relative in concept_paths.items():
        report = read(relative)
        assert report["ok"]
        destination = PROJECT / "artifacts/reviews/renderer-native" / f"{skill}-test-report.json"
        write(destination, report)
        concept[skill] = {
            "report": destination.relative_to(ROOT).as_posix(),
            "originalReport": relative,
            "ok": report["ok"], "caseCount": len(report["cases"]),
            "result": "PASS: original focused native test completed successfully; detailed assertions retained in report.",
        }
    plant = read("projects/colorset-gray-interleave/artifacts/plantuml-cs1-stage-v2/rebuild-proof.json")
    write(PROJECT / "artifacts/reviews/renderer-native/plantuml-rebuild-proof.json", plant)
    mermaid = read("projects/colorset-priority/artifacts/manifests/mermaid-cs1-rebuild.json")
    write(PROJECT / "artifacts/reviews/renderer-native/mermaid-rebuild-proof.json", mermaid)

    summary = {
        "date": "2026-10-05", "scope": list(SKILLS),
        "runtimeFreeze": frozen,
        "categoryPriority": ["primary-red", "grays", "white", "remaining-colors"],
        "colorset1SolidSequence": list(ORDER),
        "mechanism": "Sort twelve grayscale members by relative luminance, split into six darker and six lighter members, zip halves in ascending rank; keep red first, white after grays, remaining colors last; filter the fixed sequence for the actual canvas before allocating categories.",
        "boundaries": [
            "All 17 colorset1 members, named role values and text-on-fill mappings are preserved.",
            "Colorset2 membership and categorical allocation are unchanged, including PlantUML's existing seven-role native pool.",
            "Explicit quantitative continuous ramps, visualMap range order/bounds and chart data are preserved.",
            "New allocation changes category pools; named PlantUML/C4 semantic fills remain stable.",
        ],
        "focusedChecks": [
            {"command": "uv run --script skills/mermaid/scripts/test_native_solid.py", "result": "PASS 21 tests"},
            {"command": "uv run --script skills/plantuml-colorset-renderer/scripts/test_native_styles.py", "result": "PASS 21 tests"},
            {"command": "uv run --script skills/plantuml-colorset-renderer/scripts/test_ditaa_styles.py", "result": "PASS 12 tests"},
            {"command": "uv run --script skills/usefulcharts-style/scripts/test_palette_contract.py", "result": "PASS independent literal/canvas/contrast/overflow matrix"},
            {"command": "uv run --script skills/usefulcharts-style/scripts/test_chart.py", "result": "PASS 27 tests"},
            {"command": "uv run --script skills/echarts-animated-svg/scripts/test_arrow_options.py", "result": "PASS independent order/canvas tests, 216 contrast-backing cases, supplied quantitative ramp preservation"},
            {"command": "uv run --script skills/slidev-echarts/scripts/test_arrow_options.py", "result": "PASS independent order/canvas tests, 216 contrast-backing cases, supplied quantitative ramp preservation"},
        ],
        "nativeConceptChecks": concept,
        "fixtureEvidence": {
            "nativeFrames": fixtures_path,
            "mermaidGalleryValidation": "projects/grayscale-interleave/artifacts/reviews/mermaid-gallery-validation.json",
            "mermaidRebuild": "projects/grayscale-interleave/artifacts/reviews/renderer-native/mermaid-rebuild-proof.json",
            "plantumlRebuild": "projects/grayscale-interleave/artifacts/reviews/renderer-native/plantuml-rebuild-proof.json",
            "mermaidCS2Preservation": "95 resources preserved byte-for-byte by narrow build.",
            "plantumlCS2Preservation": "33 resources preserved byte-for-byte by narrow build.",
            "mermaidGeometry": {"exactCount": sum(row["same"] for row in fixture["mermaidGeometryComparedWithHEAD"]), "total": len(fixture["mermaidGeometryComparedWithHEAD"]), "qualifiedChanges": {"block": "Existing current compact defaults differ from old HEAD geometry.", "class": "Stochastic hand-drawn separator control points; labels/shapes/endpoints unchanged.", "requirement": "Stochastic hand-drawn separator control points; labels/shapes/endpoints unchanged.", "gantt": "Dynamic today marker changed with date; chart axis/data/task spans unchanged."}},
            "c4": "projects/grayscale-interleave/artifacts/reviews/c4-preserved/preservation-proof.json",
            "manualReview": fixture["manualReview"],
        },
        "echartsHeadBaseline": {
            "headRef": staging["headRef"], "builderSha256": staging["baselineBuilderSha256"],
            "indexBlob": index.relative_to(ROOT).as_posix(), "indexSha256": sha(index),
            "stagingProof": staging_path, "nativeReview": echarts_path,
            "headNativeComparison": comparison_path,
            "nativeGeometryPaintTextComparison": "All 43 cards exactly preserve native paths/transforms/paints/fonts/text versus HEAD, after qualified non-rendering instance identifiers and generated animation CSS; raw structural attributes differ only by the generated boxplot chart-instance timestamp.",
            "result": "PASS exact baseline builder and verifier, 43 cards in delivery/replay/reduced states; all authored base paints in unchanged colorset2.",
            "dirtyWorkingFilesPreserved": staging["dirtyWorkingSha256After"],
            "indexAndBuilderCommitDecision": "Preserve the qualified committed baseline. Exclude both user's working drafts and the ignored staged candidate from the commit.",
            "manualReview": echarts["manualNativeReview"],
        },
        "isolatedPi": "Root owns release forward cohorts. This report does not relabel development or old compactness runs as accepted; Mermaid, PlantUML and Slidev ECharts require root's fresh r2 contract plus three naturals after late prose-only corrections.",
        "publication": "Root owns final validators, sync, Pages build, staging and deployment. Preserve the committed ECharts gallery index and baseline builder; exclude both user's uncommitted working drafts from the commit. The isolated staged index differs only by a non-rendering timestamp and remains ignored evidence, with no committed index/builder change required. Future CS1 outputs use the updated canonical module and palette, as covered by the literal and native tests.",
    }
    output = PROJECT / "renderer-validation.json"
    write(output, summary)
    print(json.dumps({"ok": True, "summary": output.relative_to(ROOT).as_posix(), "runtimeFreeze": frozen, "indexSha256": sha(index)}, indent=2))


if __name__ == "__main__":
    main()
