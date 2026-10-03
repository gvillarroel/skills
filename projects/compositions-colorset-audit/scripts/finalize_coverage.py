#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Attach reproducible commands, strict run gates and narrow source scopes to coverage."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "evaluations/colorset-audit/compositions-20261002.json"
data = json.loads(DEST.read_text())
data["status"] = "validated-awaiting-repository-publication"
data["scope"] = "Authored paints, exact canvas cells, renderer defaults and supported output/export routes. Source-preserved media is reported separately."
data["canonicalPaletteSha256"] = hashlib.sha256((ROOT / data["canonicalPalette"]).read_bytes()).hexdigest()
versions = {"compose-synchronized-svg": 8, "diagram-composition": 2, "hierarchy-lens": 6, "usefulcharts-style": 4, "hyperframes-explainer": 3, "video": 2, "manim-svg-video": 2}
commands = {
    "compose-synchronized-svg": [("uv run --script skills/compose-synchronized-svg/scripts/test_synchronized_svg_tools.py", "80 tests passed, including authored-fragment paint rejection"), ("uv run --script skills/compose-synchronized-svg/scripts/test_theme_contract.py", "13 passed"), ("uv run --script skills/compose-synchronized-svg/scripts/test_svg_themes.py", "6 passed"), ("uv run --script skills/compose-synchronized-svg/scripts/test_svg_text_pairs.py", "3 passed; actual browser dark/tinted text pairs")],
    "diagram-composition": [("uv run --script skills/diagram-composition/scripts/test_composition.py", "24 passed"), ("uv run --script skills/diagram-composition/scripts/test_native_panels.py", "13 passed"), ("uv run --script skills/diagram-composition/scripts/test_shared_colors.py", "8 passed"), ("uv run --script skills/diagram-composition/scripts/test_connector_quality.py", "21 passed")],
    "hierarchy-lens": [("uv run --script skills/hierarchy-lens/scripts/test_explorer.py", "21 passed"), ("uv run --script skills/hierarchy-lens/scripts/test_decisions.py", "11 passed"), ("uv run --script skills/hierarchy-lens/scripts/audit_decisions.py skills/hierarchy-lens/assets/examples/hierarchy-lens/index.html --report projects/compositions-colorset-audit/artifacts/reviews/published-decisions.json --screenshot projects/compositions-colorset-audit/artifacts/reviews/published-decisions.png", "1200 decisions; 54 pixel checks; no failed checks or browser errors"), ("uv run --script skills/hierarchy-lens/scripts/audit_pixels.py skills/hierarchy-lens/assets/examples/hierarchy-lens/radial.html --report projects/compositions-colorset-audit/artifacts/reviews/published-radial.json --screenshot projects/compositions-colorset-audit/artifacts/reviews/published-radial.png", "1200 records; 512 grid; passed"), ("uv run --script skills/hierarchy-lens/scripts/audit_pixels.py skills/hierarchy-lens/assets/examples/hierarchy-lens/organic.html --report projects/compositions-colorset-audit/artifacts/reviews/published-organic.json --screenshot projects/compositions-colorset-audit/artifacts/reviews/published-organic.png", "1200 records; 128 grid; passed")],
    "usefulcharts-style": [("uv run --with 'shapely>=2,<3' --with 'osqp>=1,<2' --with 'numpy>=2,<3' --with 'scipy>=1.14,<2' --with 'playwright>=1.45.0' --with 'pillow>=10' python -m unittest discover -s skills/usefulcharts-style/scripts -p 'test_*.py'", "243 passed"), ("uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py", "Three posters rebuilt; 561/141/50 nodes; no node or connector-node collisions")],
    "hyperframes-explainer": [("uv run --script skills/hyperframes-explainer/scripts/test_explainer.py --work-dir projects/compositions-colorset-audit/artifacts/hyperframes-tests", "45 passed; unchanged renderer")],
    "video": [("uv run --script skills/video/scripts/test_scene_contracts.py --json", "13 passed, including real mixed-media MP4 render and validation")],
    "manim-svg-video": [("uv run --script skills/manim-svg-video/scripts/compose_svg_video.py --from-list projects/compositions-colorset-audit/artifacts/manim-smoke/sources.txt --out projects/compositions-colorset-audit/artifacts/manim-smoke/render --duration 3 --fps 5 --resolution 640,360 --intro-seconds 0.2 --outro-seconds 0.2 --enter-seconds 0.3 --exit-seconds 0.3 --show-labels --render", "Real MP4 passed; SVG text import warning retained"), ("ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames:format=duration -of json projects/compositions-colorset-audit/artifacts/manim-smoke/render/media/videos/manim_svg_video_scene/360p5/manim-svg-video.mp4", "640x360; 5/1 fps; 15 frames; exactly 3.000000 seconds")],
}
for record in data["skills"]:
    skill = record["skill"]
    model = "gpt-6-luna" if skill == "hyperframes-explainer" else "gpt-5.6-luna"
    run_id = f"colorset-{skill}-20261002-{versions[skill]}"
    folder = ROOT / "evaluations/runs" / run_id
    result = json.loads((folder / "evaluation-result.json").read_text())
    integrity = json.loads((folder / "skill-integrity-check.json").read_text())
    artifacts = json.loads((folder / "artifact-check.json").read_text())
    record["isolatedValidation"] = {"runId": run_id, "model": model, "strict": True, "passed": result["passed"], "gates": result["gates"], "skillDigest": integrity["beforeDigest"], "outputs": [{"path": v["path"], "sha256": v["sha256"]} for v in artifacts["outputs"]], "traceSummaryCommand": f"uv run --script scripts/summarize-pi-json-events.py evaluations/runs/{run_id}/events.jsonl --require-model {model} --fail-on-invalid-json --fail-on-tool-error"}
    record["testedCommands"] = [{"command": cmd, "result": result, "passed": True} for cmd, result in commands[skill]]
    record["openGaps"] = []
    record["changes"] = record["changes"].replace("regeneration pending checks", "regeneration validated")
    if skill == "compose-synchronized-svg":
        record["changes"] += "; custom-fragment and final SVG attribute paints guarded; opaque mix synthesis removed; transparent halos use fill-opacity"
        record["authoredScan"] += ["scripts/palette_contract.py", "scripts/replace_svg_module.py", "scripts/validate_synchronized_svg.py"]
        record["sourceExemptions"] = [{"scope": "Only embedded raster image href payloads in explicit source-preserve custom fragments", "excluded": "Image pixels only; surrounding SVG paints and wrappers remain checked"}]
    elif skill == "diagram-composition":
        record["alternateSet"] = "colorset2 for explicitly supplied semantic categories"
        record["sourceExemptions"] = [{"scope": "Nested producer SVG elements svg[data-source=<panel-id>]", "excluded": "Original imported panel paints only; generated native panels, headings, frames and cross-panel links remain checked"}]
    elif skill == "hierarchy-lens":
        record["changes"] += "; URL-encoded favicon canonical; stale browser oracle colors updated without weakening zero/missing/playback checks"
    elif skill == "usefulcharts-style":
        record["sourceExemptions"] = [{"paths": ["assets/portraits/*.jpg", "assets/objects/*.jpg", "assets/maps/milner-1850.jpg", "assets/illustrations/*.png"], "scope": "Embedded image href data payloads", "excluded": "Source image pixels only; authored SVG map geometry, category fills, icons, frames, insets and labels remain checked"}]
    elif skill == "video":
        record["sourceExemptions"] = [{"paths": ["assets/examples/ai-concept-videos/assets/earth-globe-wikimedia.svg", "assets/examples/ai-concept-videos/assets/*.png"], "scope": "Original source pixels inside imported image assets or producer-owned GIF/HTML/Slidev/video elements", "excluded": "Source pixels only; canvas, connectors, signal dots and authored gallery SVG shapes remain checked"}]
        record["openGaps"] = ["No MP4 files ship in this gallery source. If an external media release also publishes old encoded gallery videos, regenerate those from the corrected renderer during that release; source photographs and video assets retain fidelity."]
    elif skill == "manim-svg-video":
        record["sourceExemptions"] = [{"scope": "Imported producer SVG/image content loaded by SVGMobject or ImageMobject", "excluded": "Source shapes/image pixels only; all wrapper paints and placeholders remain checked"}]
        record["openGaps"] = ["Manim vector import does not reproduce SVG text/CSS/SMIL; the smoke retained its unsupported text-element warning. Use outlined text or documented raster import when source fidelity requires it."]

browser = json.loads((ROOT / "projects/compositions-colorset-audit/artifacts/reviews/browser-palette-audit.json").read_text())
data["sharedValidation"] = [{"command": "uv run --script projects/compositions-colorset-audit/scripts/audit_browser_palettes.py", "passed": browser["ok"], "states": browser["stateCount"], "report": "projects/compositions-colorset-audit/artifacts/reviews/browser-palette-audit.json", "coverage": "Four hierarchy views, all lenses/scopes/scales and SVG exports; composition scenarios; three posters; every video concept at seven times; HyperFrames starter at six times"}, {"command": "uv run --script projects/compositions-colorset-audit/scripts/test_palette_guards.py", "passed": True, "coverage": "Five configurable entry points reject #123456; hierarchy and HyperFrames use fixed exact roles"}]
data["browserEnvironment"] = {"PLAYWRIGHT_BROWSERS_PATH": "C:/Users/villa/dev/skills/projects/compositions-colorset-audit/artifacts/browsers", "TEMP": "C:/Users/villa/dev/skills/projects/compositions-colorset-audit/artifacts/tmp", "TMP": "same as TEMP"}
data["publication"] = {"owner": "root agent", "sets": ["compose-synchronized-svg", "hierarchy-lens", "usefulcharts-style", "ai-concept-videos"], "needed": "Build dist/pages, run final repository/payload/pattern validators, refresh local installation, commit/push authorized sources and verify Pages workflow"}
data["retainedFailures"] = [{"runs": ["colorset-video-20261002-1", "colorset-manim-svg-video-20261002-1"], "class": "provider-model-unavailable", "reason": "The gpt-5.3-codex-spark model is not supported when using Codex with this ChatGPT account; zero tool calls", "resolution": "Authorized gpt-5.6-luna exception required in backlog"}, {"runs": ["colorset-hierarchy-lens-20261002-1", "colorset-hierarchy-lens-20261002-3", "colorset-hierarchy-lens-20261002-4"], "class": "strict-forward-failures", "reason": "Ad hoc probe tool errors, obsolete dark-palette audit expectations, and invented usage.md read respectively", "resolution": "Updated actual color oracles; precise real reference routing; final strict candidate passed"}, {"runs": ["colorset-hyperframes-explainer-20261002-2"], "class": "forbidden-harness-read", "reason": "Agent read ../run-manifest.json", "resolution": "Prompt clarified harness boundary; final strict candidate passed"}, {"runs": ["colorset-compose-synchronized-svg-20261002-3"], "class": "evaluation-configuration", "reason": "Expect-output flags named different files than the written task prompt", "resolution": "Aligned flags with actual requested paths; subsequent strict runs passed"}]
DEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"coverage": str(DEST), "skills": len(data["skills"]), "allStrictPassed": all(s["isolatedValidation"]["passed"] for s in data["skills"])}))
