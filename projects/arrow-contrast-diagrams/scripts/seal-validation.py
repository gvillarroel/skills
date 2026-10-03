#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind compact native arrow evidence to current runtime payloads and fixtures."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "projects/arrow-contrast-diagrams/artifacts"
DESTINATION = ROOT / "evaluations/arrow-contrast-diagrams/validation-20261003.json"
SKILLS = ["mermaid", "plantuml-colorset-renderer", "slidev-quality-audit"]


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


spec = importlib.util.spec_from_file_location("pi_harness", ROOT / "scripts/run-pi-skill-eval.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
ledger = []
for skill in SKILLS:
    for attempt in [1, 2]:
        run_id = f"arrow-native-{skill}-luna{attempt}-20261003"
        run = ROOT / "evaluations/runs" / run_id
        manifest = read(run / "run-manifest.json")
        result = read(run / "evaluation-result.json")
        integrity = read(run / "skill-integrity-check.json")
        events = read(run / "event-check.json")
        entry = {
            "skill": skill,
            "runId": run_id,
            "selected": attempt == 2,
            "passed": result["passed"],
            "startedAtUtc": result["startedAtUtc"],
            "finishedAtUtc": result["finishedAtUtc"],
            "model": manifest["pi"]["model"],
            "profile": manifest["skill"]["profile"],
            "payloadSha256": manifest["skill"]["payloadSha256"],
            "unchangedPayload": integrity["passed"],
            "strictGates": result["gates"],
            "toolErrorCount": sum(call.get("isError", False) for call in events["calls"]),
            "eventFindings": events["findings"],
            "expectedOutputs": manifest["expectedOutputs"],
            "artifacts": read(run / "artifact-check.json")["outputs"],
            "promptSha256": manifest["prompt"]["sha256"],
        }
        if attempt == 2:
            with tempfile.TemporaryDirectory(prefix=f"seal-{skill}-", dir=ARTIFACTS) as temporary:
                copied = Path(temporary) / skill
                harness.copy_skill_only(ROOT / "skills" / skill, copied, "runtime")
                current = harness.snapshot_digest(harness.snapshot_tree(copied))
            entry["currentSourcePayloadSha256"] = current
            entry["currentSourceMatchesAccepted"] = current == manifest["skill"]["payloadSha256"]
            assert result["passed"] and entry["currentSourceMatchesAccepted"], entry
        elif skill == "mermaid":
            entry["classification"] = "Strict runtime failure: source was edited after styling, then checked before restyling; one tool error. Repaired outputs retained. Snapshot also predates final native caption repairs."
        elif skill == "plantuml-colorset-renderer":
            entry["classification"] = "Passed but superseded: manual PNG review exposed transparent raster canvas; final producer uses an explicit opaque white canvas."
        else:
            entry["classification"] = "Passed but superseded: the final producer additionally composites translucent HTML ancestor canvas paint; a tenth actual browser regression covers it."
        ledger.append(entry)

rows = read(ARTIFACTS / "native-arrow-inventory.json")
summary = read(ARTIFACTS / "native-arrow-summary.json")
markers = 0
occluded_markers = 0
occluded_shafts = Counter()
transient_shafts = Counter()
marker_samples = 0
minimum = []
for row in rows:
    for record in row["records"]:
        projected = record.get("markers", [])
        markers += len({(sample["ref"], sample["role"]) for sample in projected})
        marker_samples += len(projected)
        occluded_markers += sum(sample.get("occluded", False) for sample in projected)
        for sample in record.get("samples", []):
            key = f'{row["renderer"]}:{row["family"]}:{row["state"]}'
            if sample.get("occluded"):
                occluded_shafts[key] += 1
            if sample.get("transientOcclusion"):
                transient_shafts[key] += 1
        if not record["revealIntentional"] and record["minContrast"] is not None:
            minimum.append(record["minContrast"])
assert not any(row["findings"] for row in summary)
assert occluded_markers == 0

fixtures = sorted((ROOT / "skills/mermaid/assets/examples/mermaid-max-complexity/svg").rglob("*.svg"))
for folder in ["plantuml-colorset-renderer", "plantuml-colorset-renderer-cs1"]:
    fixtures.extend(sorted((ROOT / "skills/plantuml-colorset-renderer/assets/examples" / folder / "svg").glob("*.svg")))
cr_files = []
git_mismatches = []
for path in fixtures:
    if b"\r" in path.read_bytes():
        cr_files.append(path.relative_to(ROOT).as_posix())
    raw = subprocess.check_output(["git", "hash-object", "--no-filters", str(path)], cwd=ROOT, text=True).strip()
    normalized = subprocess.check_output(["git", "hash-object", f"--path={path.relative_to(ROOT).as_posix()}", str(path)], cwd=ROOT, text=True).strip()
    if raw != normalized:
        git_mismatches.append(path.relative_to(ROOT).as_posix())
assert not cr_files and not git_mismatches
quality = read(ARTIFACTS / "quality-arrow-probe.json")
assert quality["passed"] and not quality["errors"]
result = {
    "schemaVersion": 1,
    "date": "2026-10-03",
    "behaviorChangedBundles": SKILLS,
    "unchangedInspectedBundle": "slidev-animejs",
    "parentOwnedBundles": ["echarts-animated-svg", "slidev-echarts"],
    "minimumNonTextContrast": 3,
    "nativeEvidence": {
        "states": len(rows),
        "statesByRenderer": dict(Counter(row["renderer"] for row in rows)),
        "shaftInstances": sum(row["shaftCount"] for row in rows),
        "explicitHeadInstances": sum(row["headCount"] for row in rows),
        "referencedMarkerInstances": markers,
        "referencedMarkerSamples": marker_samples,
        "coveredMarkerSamples": occluded_markers,
        "contrastFindingCount": sum(len(row["findings"]) for row in summary),
        "minimumReadableSampleContrast": min(minimum),
        "occludedShaftSamplesByFamilyState": dict(occluded_shafts),
        "transientShaftSamplesByFamilyState": dict(transient_shafts),
        "occlusionClassification": {
            "gitGraph": "Native branch shafts terminate beneath commit dots; the visible branch route remains continuous and its native chronology is preserved.",
            "mindmap": "Native radial branch shafts meet solid label/root silhouettes; these connections have no directional marker to hide.",
            "timeline": "Native vertical dotted connectors pass behind date/event boxes; the delivered backbone and heads remain clear.",
            "architecture": "Native shafts begin beneath service icon silhouettes, while complete target heads remain in their exterior gutters.",
            "wardley": "Native links meet procurement glyph overlays; these retain their meaningful layered symbol geometry.",
            "plantumlEBNFAndREGEX": "Railroad links meet white terminal contours; loop arrows and direction remain visibly complete.",
            "plantumlGANTT": "Task dependency shafts end at native task silhouettes; the directional polygon remains outside the task body.",
            "transient": "Eight samples at mid-reveal contact partially revealing GitGraph commit, Timeline event and Architecture service shapes. They are explicitly recorded apart from readable final samples.",
            "manualReview": "All eight semantic occlusion families were also inspected in actual browser screenshots. No referenced head sample is covered.",
        },
        "inventorySha256": sha(ARTIFACTS / "native-arrow-inventory.json"),
        "summarySha256": sha(ARTIFACTS / "native-arrow-summary.json"),
    },
    "qualityBrowserRegression": {
        "passed": quality["passed"],
        "caseCount": len(quality["results"]),
        "caseIds": [entry["id"] for entry in quality["results"]],
        "errors": quality["errors"],
        "sha256": sha(ARTIFACTS / "quality-arrow-probe.json"),
    },
    "fixtureBoundary": {
        "svgCount": len(fixtures),
        "crFiles": cr_files,
        "gitNormalizedBlobMismatches": git_mismatches,
        "mermaidGallerySha256": sha(ROOT / "skills/mermaid/assets/examples/mermaid-max-complexity/gallery.json"),
    },
    "runtimeTrials": ledger,
    "limitations": [
        "The native producer samples supported straight, quadratic, cubic and elliptical-arc paths and actual polygon contours; C4 and event routes target native renderer geometry, not arbitrary transformed SVG imports.",
        "Hollow cardinality symbols are judged by their visible native rims, while white voids retain semantics. Complete glyphs and animation marker identities are preserved.",
        "Imported source SVGs, Ditaa and standalone mathematical raster diagrams preserve source fidelity; finished authored SVG-capable PlantUML diagrams share SVG and PNG geometry with an opaque white raster canvas.",
        "Gradients, complex masks/clips/filters, custom marker hierarchies and narrow connector crossings still require explicit actual rendered inspection; automatic sampling is supplementary, not a universal clearance proof.",
    ],
}
DESTINATION.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"selectedTrials": 3, "nativeEvidence": result["nativeEvidence"], "qualityCases": len(quality["results"]), "fixtureBoundary": result["fixtureBoundary"]}, indent=2))
