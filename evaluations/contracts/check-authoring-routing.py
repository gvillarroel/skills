#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Test selection from all canonical metadata without force-loading a skill."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CASES = {
    "ambientcg-material-search": "Find ambientCG concrete PBR materials and download the chosen 2K JPG package.",
    "animated-svg-to-gif": "Turn this existing CSS-animated SVG into a looping GIF with browser-accurate frames.",
    "asciinema-real-command-video": "Record a real interactive command-line session and provide its authentic asciicast plus an MP4.",
    "compose-synchronized-svg": "Create one large standalone interactive SVG atlas whose many modules propagate one shared causal state and camera focus.",
    "d3": "Create a custom offline D3 lollipop chart with data joins, an interactive brush, and a portable settled SVG.",
    "destockd-video-search": "Browse Destockd for archival industrial footage, show previews, and download the chosen shot.",
    "diagram-composition": "Plan and compose a compact explanatory page from several related subdiagrams with a shared semantic key and deliberate grid spans.",
    "echarts-animated-svg": "Animate already-rendered ECharts SVG charts without rebuilding their geometry, and add replay controls.",
    "google-cloud-sku-pricing": "Compare Google Cloud SKU tier prices by region using the offline Parquet catalog and generate exact estimates.",
    "harbor-author-evaluation-datasets": "Author a native Harbor dataset with semantic-family development, sealed validation, and holdout splits before study registration.",
    "hierarchy-lens": "Explore an organization hierarchy offline with compact organic cells, explicit placement priorities, and switchable color lenses.",
    "hyperframes-explainer": "Create a minimal HyperFrames explanatory video where one causal event updates a mechanism and several measurements in sync, with sparse labels and colorset1 by default.",
    "iconify-icon-search": "Find a consistent free Iconify icon family, preview alternatives, and export selected SVG icons with licenses.",
    "jev-batch-decisions": "Batch a large document collection into typed Jev classification decisions through OpenRouter and aggregate complete coverage.",
    "kenney-asset-search": "Find a free Kenney platformer game asset pack and extract selected sprites with its license.",
    "manim-svg-video": "Render these existing SVG files as a standalone SVG-only Manim MP4 with an exact-duration composition manifest.",
    "mermaid": "Create and render a Mermaid sequence diagram from these interactions, preserving accessible metadata and the source relationships.",
    "one-bit-dither-svg": "Restyle a local illustration as an Obra Dinn-inspired one-bit dithered engraving in a self-contained pixel SVG.",
    "pexels-media-search": "Search Pexels for free stock video previews and download the exact selected rendition with creator credit.",
    "pixel-art-image-video": "Convert a local video to crisp retro pixel art with a chosen virtual resolution and retained audio.",
    "plantuml-colorset-renderer": "Render PlantUML source with its bundled colorset theme and verify a deterministic SVG render report.",
    "polyhaven-asset-search": "Find a Poly Haven HDRI, preview candidates, and download the chosen EXR resolution.",
    "procedural-svg-animation": "Create a seeded generative SVG motion study driven by oscillators and recursive geometry, with a seamless deterministic loop.",
    "repository-reviewer-creator": "Generate a reusable standalone repository reviewer skill from this project's architecture, contracts, tests, and security boundaries.",
    "simulation-data-lab": "Build and execute an offline mathematical queueing model and produce explorable simulated data with explicit assumptions and conditional uncertainty.",
    "slidev-animejs": "Implement scoped Anime.js lifecycle animations driven by clicks inside an existing Slidev presentation.",
    "slidev-echarts": "Add reusable Vue ECharts chart components and click-driven data updates to an existing Slidev deck.",
    "slidev-quality-audit": "Audit an existing Slidev deck in Playwright for text overlap, clipping, poor contrast, blank charts, and unchanged click states.",
    "svg-brief-design": "Design an original editable SVG floral emblem from a brief using deliberate curves, line hierarchy, and negative space.",
    "technical-logo-assets": "Export verified vector-only AWS and programming-language brand logos with labeled monochrome variants and license provenance.",
    "threejs-animated-3d": "Build an interactive Three.js WebGL scene with a moving camera, depth, lighting, and instanced particles.",
    "usefulcharts-style": "Create a UsefulCharts-inspired educational genealogy poster with compact family trees, semantic colors, and readable print labels.",
    "vectorize-art-patterns": "Vectorize this openly licensed raster painting into editable organic SVG art using contour tracing and palette reduction.",
    "video": "Compose a mixed-media multi-scene MP4 from existing charts, raster images, narration, and 3D clips with one master clock and cross-element interactions.",
}
NEGATIVES = {
    "ordinary-pr-review": "Review this pull request for introduced bugs and provide findings; do not create a reusable reviewer skill.",
    "plain-summary": "Summarize these three short paragraphs in plain text.",
    "text-rename": "Rename a local plain-text file from notes.txt to meeting.txt.",
    "pdf-extraction": "Extract plain text from a PDF without charts or visualizations.",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,120}", args.run_id):
        parser.error("Invalid run ID")
    spec = importlib.util.spec_from_file_location("authoring_routing_harness", ROOT / "scripts/run-pi-skill-eval.py")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    run = ROOT / "evaluations/runs" / args.run_id
    workspace = run / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)
    catalog = [yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1]) for path in sorted((ROOT / "skills").glob("*/SKILL.md"))]
    if {entry["name"] for entry in catalog} != set(CASES):
        parser.error("Routing cases must cover the complete canonical catalog")
    # Opaque IDs keep the expected selection out of the model-visible requests.
    labeled = [(name, request) for name, request in CASES.items()] + [("none", request) for request in NEGATIVES.values()]
    requests = {f"c{index:03d}": request for index, (_, request) in enumerate(labeled, 1)}
    expected = {f"c{index:03d}": name for index, (name, _) in enumerate(labeled, 1)}
    prompt = "This is a metadata selection test. No skill is loaded, and you must not perform any request or invoke a skill. Select one catalog name, or none when no capability applies, using only its declared purpose and triggers. Write routing.json as {\"choices\":{\"case-id\":\"skill-name-or-none\"}}. Do not read other files or use the network.\n\nCatalog:\n" + json.dumps(catalog, indent=2) + "\n\nSynthetic requests:\n" + json.dumps(requests, indent=2)
    (run / "prompt.md").write_text(prompt, encoding="utf-8")
    model = "openai-codex/gpt-5.6-luna"
    command = [*harness.pi_command_prefix(), "--model", model, "--thinking", "high", "--mode", "json", "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-session", "--print", "Read ../prompt.md first, then perform only its metadata classification task."]
    result = subprocess.run(command, cwd=workspace, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    events = run / "events.jsonl"
    events.write_text(result.stdout, encoding="utf-8")
    (run / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    event_check = harness.event_check_report(events_path=events, prompt=prompt, require_prompt_read_first=True, require_exact_command_from_prompt=False, require_observed_model=True, requested_model=model, fail_on_invalid_json=True, fail_on_tool_error=True, forbid_read_regex=harness.STRICT_COMMON_FORBIDDEN_READ_PATTERNS, forbid_command_regex=[])
    choices = json.loads((workspace / "routing.json").read_text(encoding="utf-8")).get("choices", {}) if (workspace / "routing.json").is_file() else {}
    checks = [{"case": case, "request": requests[case], "expected": expected[case], "actual": choices.get(case)} for case in requests]
    report = {"passed": result.returncode == 0 and event_check["passed"] and all(check["expected"] == check["actual"] for check in checks), "model": model, "scope": "Metadata selection only; no skill workflow is executed, including simulation-data-lab.", "checks": checks, "events": event_check}
    (run / "routing-result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "caseCount": len(checks), "failed": [check for check in checks if check["actual"] != check["expected"]]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
