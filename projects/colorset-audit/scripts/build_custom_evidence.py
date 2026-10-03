#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Materialize the bounded custom-visual audit inventory and English evidence."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "evaluations/colorset-audit"
ART = ROOT / "projects/colorset-audit/artifacts"
skill_names = ["d3", "procedural-svg-animation", "threejs-animated-3d", "svg-brief-design", "vectorize-art-patterns"]
touched = set(json.loads((ART / "data/custom-repair-paths.json").read_text()))
touched.update([
    "skills/d3/SKILL.md", "skills/d3/scripts/colorset_adapter.py", "skills/d3/scripts/test_colorset_adapter.py",
    "skills/d3/scripts/dither_d3_output.py", "skills/d3/scripts/prepare_svg_recreation_templates.py",
    "skills/d3/scripts/check_palette_contract.py",
    "skills/d3/references/palette-contract.md", "skills/d3/references/svg-replication.md", "skills/d3/references/command-reference.md",
    "skills/d3/assets/examples/d3-animated-svg/composition-sheets.html", "skills/d3/assets/examples/d3-animated-svg/composition-sheets.js",
    "skills/procedural-svg-animation/SKILL.md", "skills/procedural-svg-animation/references/runtime-and-validation.md",
    "skills/procedural-svg-animation/scripts/validate_procedural_svg.py", "skills/procedural-svg-animation/scripts/render_procedural_svg.py",
    "skills/procedural-svg-animation/assets/examples/procedural-svg-animation/index.html",
    "skills/procedural-svg-animation/assets/examples/procedural-svg-animation/gallery.css",
    "skills/procedural-svg-animation/assets/examples/procedural-svg-animation/manifest.json",
    "skills/svg-brief-design/SKILL.md", "skills/svg-brief-design/scripts/scaffold.py", "skills/svg-brief-design/scripts/render_svg.py",
    "skills/svg-brief-design/scripts/test_scaffold.py",
    "skills/threejs-animated-3d/SKILL.md", "skills/threejs-animated-3d/references/visual-tokens.md",
    "skills/threejs-animated-3d/scripts/validate_standalone_threejs.py",
    "skills/threejs-animated-3d/assets/examples/threejs-animated-3d/scripts/verify-gallery.mjs",
    "skills/vectorize-art-patterns/SKILL.md", "skills/vectorize-art-patterns/references/colorset-adaptation.md",
    "skills/vectorize-art-patterns/references/collection-generation.md",
])
touched.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "skills/procedural-svg-animation/assets/examples/procedural-svg-animation/patterns").glob("*.svg"))
required_new = [
    "skills/d3/scripts/colorset_adapter.py", "skills/d3/scripts/test_colorset_adapter.py",
    "skills/procedural-svg-animation/assets/palettes/colorsets.json", "skills/procedural-svg-animation/scripts/render_procedural_svg.py",
    "skills/svg-brief-design/assets/palettes/colorsets.json", "skills/threejs-animated-3d/assets/palettes/colorsets.json",
]
prior_publication_dependencies = [
    "skills/svg-brief-design/agents/openai.yaml", "skills/svg-brief-design/references/construction-decisions.md",
    "skills/svg-brief-design/references/detail-editing.md", "skills/svg-brief-design/references/scaffold-recipes.md",
    "skills/svg-brief-design/references/svg-mechanics.md", "skills/d3/scripts/build_speculative_decoding.py",
    "skills/d3/scripts/verify_speculative_decoding.py", "skills/d3/scripts/test_speculative_decoding.py",
    "skills/d3/references/patterns/speculative-decoding.md",
]
skills = [
    {
        "skill": "d3", "default": "colorset1", "explicit": "colorset2",
        "outputs": [
            {"route": "22 named standalone builders", "producerGlob": "scripts/build*.py containing colorset_output", "formats": ["HTML", "SVG export", "PNG capture"], "testedCases": 44},
            {"route": "bar/lollipop/network/flow/logo contract builders", "producer": "scripts/build_contract_artifact.py", "formats": ["HTML", "decision JSON"], "colorset": "explicit cs1/cs2 role table"},
            {"route": "five editable starters", "producer": "scripts/create_d3_svg_starter.py", "formats": ["HTML", "CSS", "data JS", "manifest JSON", "notes Markdown"]},
            {"route": "parametric logo studio and texture engine", "producers": ["scripts/build_logo_studio.py", "assets/templates/logo-studio.html", "assets/templates/texture-gallery.html", "assets/templates/logo-engine.js"], "formats": ["HTML", "SVG export"], "scope": "closed CLI contract choices; both UI palette modes checked"},
            {"route": "kinetic glyph deconstruction", "producer": "scripts/build_kinetic_type.py", "formats": ["HTML", "SVG export"]},
            {"route": "speculative decoding", "producer": "scripts/build_speculative_decoding.py", "formats": ["SVG", "decision JSON"], "changeOwnership": "pre-existing independent authoring; exact bundled roles confirmed"},
            {"route": "source-derived recreation", "producer": "scripts/prepare_svg_recreation_templates.py", "formats": ["seed SVG", "candidate SVG", "HTML", "source and derived signature JSON", "inventory Markdown"], "scope": "adapt derived paint; original source and its signature immutable; unsupported source paint must be normalized"},
            {"route": "dithered derivative", "producer": "scripts/dither_d3_output.py", "formats": ["SVG", "PNG preview", "JSON report"], "scope": "custom palette must be exact subset of active cs1/default or cs2/explicit; both SVG and preview APIs enforce it"},
            {"route": "render/export and evaluation", "producers": ["scripts/render_d3_svg.py", "scripts/build_evaluation_report.py"], "formats": ["SVG", "PNG", "Markdown", "decision JSON"], "scope": "render inherits validated source; metadata output contains no authored paint"},
            {"route": "225-pattern base/cs1/cs2 galleries", "sourceGlob": "assets/examples/d3-animated-svg*/**/*", "colorset": "base cs2 preserves distinct semantic categories; cs1/cs2 variants explicit"},
            {"route": "seven composition sheets/78 composition previews, hub, logo gallery90 and texture gallery40", "sourceGlobs": ["assets/examples/d3-animated-svg/composition-sheets.*", "assets/examples/d3/*", "assets/examples/d3-logo-design/*", "assets/examples/d3-logo-textures/*"], "scope": "authored chrome and actual render paint; active controls reject unapproved overrides"},
            {"route": "cardinality variants", "producer": "scripts/build_cardinality_variants.ts", "scope": "legacy off-contract authored literals replaced with exact canonical inputs"},
        ],
        "changes": ["Default named builders adapt actual paint, not only metadata", "Base gallery force-maps paint and validates config overrides", "SMIL paint endpoints use discrete canonical values", "New dither override gate and palette-compliant recreation seeds"],
    },
    {
        "skill": "procedural-svg-animation", "default": "colorset1", "explicit": "colorset2",
        "outputs": [
            {"route": "66 deterministic pattern renderers/11 families", "producer": "scripts/build_procedural_svg.py", "formats": ["standalone SVG", "config and manifest JSON"], "modes": ["single pattern", "--all", "full motion", "reduced motion", "config template"], "testedCases": 264},
            {"route": "acceptance gallery", "producer": "scripts/build_procedural_gallery.py", "formats": ["66 SVG files", "HTML", "CSS", "JS", "manifest JSON"], "colorset": "colorset1"},
            {"route": "browser capture", "producer": "scripts/render_procedural_svg.py", "formats": ["PNG", "JSON report"], "scope": "captures validated standalone source and records first/intermediate/reduced states; no added visual chrome"},
        ],
        "changes": ["Corrected cs1 gray token and removed default pink highlight", "Default generator, config and gallery switch to cs1", "Replaced unrelated neon gallery chrome", "Actual paints/gradient stops/SMIL values validated", "Portable local capture avoids forbidden host-temporary reads", "Manual capture found and repaired seven mojibake source locations"],
    },
    {
        "skill": "threejs-animated-3d", "default": "colorset1", "explicit": "colorset2",
        "outputs": [
            {"route": "portable token-orbit scene", "producer": "scripts/build_standalone_threejs.py", "formats": ["HTML", "WebGL", "PNG", "validation JSON"], "scope": "all material inputs checked against active palette"},
            {"route": "24-scene gallery", "sourceGlob": "assets/examples/threejs-animated-3d/**", "formats": ["HTML", "WebGL", "Vite build"], "colorset": "colorset2", "scope": "CSS, materials, emissive colors, lights, vertex input colors, fog and backgrounds are exact tokens"},
        ],
        "changes": ["Neutral white lights replace authored blue/yellow light inputs", "Continuous vertex color lerp becomes four exact token bands", "Standalone validator rejects off-contract material inputs", "Fixture verifier screenshot root corrected to authorized workspace"],
    },
    {
        "skill": "svg-brief-design", "default": "colorset1", "explicit": "colorset2",
        "outputs": [
            {"route": "blank/orbit/radial/globe/wave/flow/panel/frond/composition recipes", "producer": "scripts/scaffold.py", "formats": ["recipe JSON", "editable SVG"], "scope": "main, underlay, nested detail fills/strokes and root metadata checked"},
            {"route": "hand-authored SVG and preview", "producer": "scripts/render_svg.py", "formats": ["PNG", "validation JSON"], "scope": "actual paint attributes and CSS including gradients/filters checked before rendering"},
        ],
        "changes": ["Added self-contained canonical palette resource", "Scaffold and custom SVG render gate reject arbitrary paints", "uv-first renderer invocation closes isolated missing dependency failure", "15 meaningful scaffold/render contract tests pass"],
    },
    {
        "skill": "vectorize-art-patterns", "default": "colorset1", "explicit": "colorset2",
        "outputs": [
            {"route": "OpenCV organic/ink/stain/collage conversion", "producer": "scripts/vectorize_art.py", "formats": ["SVG", "provenance JSON"], "scope": "all derivative visible paint mapped to selected contract; source pixels and source palette metadata retained as evidence"},
            {"route": "VTracer high-fidelity conversion", "producer": "scripts/vectorize_with_vtracer.py", "formats": ["SVG", "provenance JSON"], "scope": "geometry locked between cs1/cs2 variants; source colors are evidence only"},
            {"route": "source acquisition", "producer": "scripts/fetch_open_image.py", "formats": ["original image", "rights/provenance JSON"], "scope": "immutable original acquisition; no authored derivative paint"},
            {"route": "30 works/60 paired variants and two abstract world maps", "producers": ["scripts/build_example_gallery.py", "assets/examples/vectorize-art-patterns/", "assets/examples/abstract-world-map/"], "formats": ["SVG", "HTML", "PNG", "manifest JSON"], "scope": "derivatives already correct; original source image previews retain fidelity and compliant chrome"},
        ],
        "changes": ["Removed unconstrained SOURCE derivative route", "Both converters default to cs1; explicit cs2 remains available", "Validator rejects data-colorset=source", "Preserved required artSequence/backgroundCandidates/ink palette fields; common canonical fields exactly equal"],
    },
]
if "--paths-only" in sys.argv:
    path = ART / "data/custom-final-touched-paths.json"
    path.write_text(json.dumps({"touchedCanonicalPaths": sorted(touched), "newRequiredBundleResources": required_new, "preExistingPublicationDependencies": prior_publication_dependencies}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "touchedCanonicalPaths": len(touched), "path": str(path)}))
    raise SystemExit(0)

accepted_ids = {
    "d3": "colorset-d3-20261002-final6",
    "procedural-svg-animation": "colorset-procedural-svg-animation-20261002-final3",
    "threejs-animated-3d": "colorset-threejs-animated-3d-20261002-1",
    "svg-brief-design": "colorset-svg-brief-design-20261002-5",
    "vectorize-art-patterns": "colorset-vectorize-art-patterns-20261002-2",
}
accepted = []
for skill, run_id in accepted_ids.items():
    folder = ROOT / "evaluations/runs" / run_id
    result = json.loads((folder / "evaluation-result.json").read_text())
    manifest = json.loads((folder / "run-manifest.json").read_text())
    accepted.append({"skill": skill, "runId": run_id, "model": "openai-codex/gpt-5.6-luna", "profile": "runtime", "strict": True, "result": result, "commandManifest": (folder / "run-manifest.json").relative_to(ROOT).as_posix(), "evidence": (folder / "event-check.json").relative_to(ROOT).as_posix()})
    assert result["passed"], run_id
attempts = []
for prefix in skill_names:
    for folder in sorted((ROOT / "evaluations/runs").glob(f"colorset-{prefix}-20261002-*")):
        result_path = folder / "evaluation-result.json"
        if result_path.exists():
            result = json.loads(result_path.read_text())
            attempts.append({"skill": prefix, "runId": folder.name, "passed": result["passed"], "durationSeconds": result["durationSeconds"], "acceptedCurrentBundle": folder.name == accepted_ids[prefix]})
deterministic = json.loads((ART / "data/custom-generated-coverage.json").read_text())
additional = json.loads((ART / "data/d3-additional-route-coverage.json").read_text())
browser = json.loads((ART / "data/custom-browser-coverage.json").read_text())
browser_counts = [{"page": row["page"], "colorset": row["colorset"], "svgCount": row["svgCount"], "ok": row["ok"]} for row in browser["results"] if "page" in row]
tests = [
    {"command": "uv run --script projects/colorset-audit/scripts/check_custom_outputs.py", "result": "PASS", "cases": deterministic["caseCount"], "evidence": "projects/colorset-audit/artifacts/data/custom-generated-coverage.json"},
    {"command": "uv run --script projects/colorset-audit/scripts/check_d3_additional_routes.py", "result": "PASS", "cases": additional["caseCount"], "evidence": "projects/colorset-audit/artifacts/data/d3-additional-route-coverage.json"},
    {"command": "uv run --script projects/colorset-audit/scripts/check_custom_browser.py", "result": "PASS", "pages": 6, "computedSvgCount": sum(r["svgCount"] for r in browser_counts), "evidence": "projects/colorset-audit/artifacts/data/custom-browser-coverage.json"},
    {"command": "uv run --script skills/d3/assets/examples/d3-animated-svg/scripts/verify_d3_gallery.py skills/d3/assets/examples/d3-animated-svg/index.html --expected 225 --replay-all --screenshot projects/colorset-audit/artifacts/images/d3-gallery.png --wait-ms 2200", "result": "PASS", "patterns": 225, "replays": 225},
    {"command": "uv run --script skills/d3/assets/examples/d3-animated-svg-cs1/scripts/verify_style_gallery.py skills/d3/assets/examples/d3-animated-svg-cs1/index.html", "result": "PASS", "patterns": 225, "badPaintCount": 0, "evidence": "projects/colorset-audit/artifacts/data/d3-cs1.json"},
    {"command": "uv run --script skills/d3/assets/examples/d3-animated-svg-colorset2/scripts/verify_colorset2_gallery.py skills/d3/assets/examples/d3-animated-svg-colorset2/index.html", "result": "PASS", "patterns": 225, "badPaintCount": 0, "evidence": "projects/colorset-audit/artifacts/data/d3-cs2.json"},
    {"command": "uv run --script skills/d3/assets/examples/d3-animated-svg/scripts/verify_composition_sheets.py skills/d3/assets/examples/d3-animated-svg/composition-sheets.html", "result": "PASS", "sheets": 7, "variants": 78, "sourcePatterns": 225},
    {"command": "uv run --script skills/d3/scripts/verify_logo_gallery.py skills/d3/assets/examples/d3-logo-design/index.html", "result": "PASS", "patterns": 90, "compositions": 90, "textures": 40, "evidence": "projects/colorset-audit/artifacts/data/d3-logo-gallery.json"},
    {"command": "uv run --script skills/d3/scripts/verify_logo_texture_gallery.py skills/d3/assets/examples/d3-logo-textures/index.html", "result": "PASS", "textures": 40, "directHashes": 40, "labels": 80, "evidence": "projects/colorset-audit/artifacts/data/d3-logo-textures.json"},
    {"command": "uv run --script skills/d3/assets/examples/d3-animated-svg/scripts/extract_gallery_pattern_references.py --check-only --expected 225", "result": "PASS"},
    {"command": "uv run --script skills/d3/scripts/test_colorset_adapter.py", "result": "PASS", "cases": 4},
    {"command": "uv run --script skills/procedural-svg-animation/scripts/test_multistrata_contracts.py", "result": "PASS", "scope": "all clean numerical families and adversarial invariant mutations"},
    {"command": "uv run --script skills/procedural-svg-animation/scripts/build_procedural_gallery.py --check", "result": "PASS", "cases": 66, "catalogHash": "49c622bd3c49a64b"},
    {"command": "uv run --script projects/colorset-audit/scripts/check_procedural_gallery_chrome.py", "result": "PASS", "states": 16, "familyHoverChecks": 22, "scope": "full document computed chrome at desktop/mobile default,hover,keyboard focus; canonical alpha bases allowed", "evidence": "projects/colorset-audit/artifacts/data/procedural-gallery-chrome.json"},
    {"command": "uv run --script scripts/validate-colorsets.py --input skills/procedural-svg-animation/assets/examples/procedural-svg-animation/gallery.css --colorset colorset1 --report projects/colorset-audit/artifacts/data/procedural-published-css.json", "result": "PASS", "offPaletteFindings": 0, "scope": "published CSS forced to its declared cs1 gallery contract"},
    {"command": "uv run --script skills/svg-brief-design/scripts/test_scaffold.py", "result": "PASS", "cases": 15},
    {"command": "uv run --script skills/vectorize-art-patterns/scripts/test_vectorize_art.py", "result": "PASS", "scope": "four modes, both colorsets, determinism, seed variation, rights and integrity"},
    {"command": "uv run --script skills/vectorize-art-patterns/scripts/test_vectorize_with_vtracer.py", "result": "PASS", "scope": "geometry-locked pair, nine paths, determinism and rights rejection"},
    {"command": "uv run --script skills/vectorize-art-patterns/scripts/validate_example_gallery.py", "result": "PASS", "works": 30, "variants": 60, "creators": 28, "geometryLockedPairs": 30},
    {"command": "uv run --script skills/vectorize-art-patterns/scripts/validate_abstract_world_map_examples.py", "result": "PASS", "variants": 2},
    {"command": "npm run build; npm run verify", "workingDirectory": "skills/threejs-animated-3d/assets/examples/threejs-animated-3d", "result": "PASS", "scenes": 24, "scope": "desktop/mobile drawing, animation, pointer and replay"},
    {"command": "uv run --script projects/colorset-audit/scripts/smoke_logo_audit_chrome.py", "result": "PASS", "viewports": [1440, 390], "rows": 12, "choices": 7, "loadedImages": 52, "evidence": "projects/colorset-audit/artifacts/data/logo-audit-chrome-smoke.json"},
    {"command": "uv run --script projects/colorset-audit/scripts/review_root_color_parser.py", "result": "PASS", "cases": 6, "evidence": "projects/colorset-audit/artifacts/data/root-color-parser-review.json"},
]
inventory = {
    "schemaVersion": 1, "date": "2026-10-02", "scope": skill_names,
    "canonicalAuditBaseline": "skills/hyperframes-explainer/assets/palettes/colorsets.json",
    "baselineSha256": hashlib.sha256((ROOT / "skills/hyperframes-explainer/assets/palettes/colorsets.json").read_bytes()).hexdigest(),
    "skills": skills, "touchedCanonicalPaths": sorted(touched), "newRequiredBundleResources": required_new,
    "preExistingPublicationDependencies": prior_publication_dependencies,
    "sourceFidelityExceptions": [
        {"skill": "d3", "scope": "immutable original SVG/raster/image bytes and separate source-signature JSON; derived seeds/HTML/SVG chrome remain palette-compliant"},
        {"skill": "vectorize-art-patterns", "scope": "original source acquisition and gallery originals; sourcePalette/quantized source paints inside provenance metadata only; no derivative visible paint exception"},
        {"skill": "threejs-animated-3d", "scope": "requested immutable photography/video/texture sources retain source pixels; authored material/light/CSS inputs comply; renderer-derived lighting/interpolation/antialiasing/composited pixels are not exact input tokens"},
    ],
    "tests": tests, "browserCoverage": browser_counts, "acceptedIsolatedRuns": accepted, "allRetainedAttempts": attempts,
    "commandCoverageCounts": {"documentedSkillAndProjectValidationGroups": len(tests), "currentAcceptedStrictForwardCommands": len(accepted), "currentAcceptedEventSummarizerCommands": len(accepted), "retainedForwardAttempts": len(attempts)},
    "publicationRequiresRebuild": ["D3 base/cs1/cs2 shared-gallery JS, composition sheets, and hub", "procedural gallery plus all 66 SVGs", "Three.js 24-scene fixture build"],
    "gapsAndLimits": [
        "Coverage closes every bundled producer and visual route; it cannot prevent a future agent from writing new off-contract code, so the instructions and paint gate must remain part of validation.",
        "Raster/browser pixels from antialiasing, alpha, gradients and WebGL illumination differ from authored token inputs; the audit validates paints, stops, light/material inputs and derived export behavior rather than enumerating every final pixel.",
        "SVG brief and vectorize retain any broader pre-existing backlog validation status; one colorset-focused forward case does not replace their larger acceptance portfolio.",
        "No commit, push, Pages deployment or root documentation/backlog mutation performed by this group; parent owns publication and repository release gates.",
        "First Three.js fixture verifier used its pre-existing incorrect six-parent root and wrote two captures outside the authorized root. This was disclosed, fixed to five parents, and rerun inside the workspace; outside files were not modified or deleted.",
    ],
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "custom-visuals-20261002.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
rows = "\n".join(f"| {row['skill']} | `{row['runId']}` | {row['result']['durationSeconds']} s | PASS |" for row in accepted)
report = f"""# Custom visual colorset audit — 2026-10-02

The five assigned bundles now constrain their authored output to colorset1 or colorset2. Colorset1 is the normal generation default. Explicit colorset2 remains available, and existing categorical D3/Three.js acceptance galleries declare colorset2 because they teach distinct semantic roles. The baseline was the exact canonical contract in `skills/hyperframes-explainer/assets/palettes/colorsets.json`, used only for audit comparison. Runtime resources live inside each owning bundle.

The machine-readable companion [custom-visuals-20261002.json](custom-visuals-20261002.json) enumerates producers, formats, palette modes, changed paths, required new resources, validation commands, retained attempts and limits. Its `touchedCanonicalPaths` list identifies only this audit's edits; it intentionally excludes unrelated pre-existing D3 pattern authoring and other agents' work.

## Corrections by bundle

- **D3:** Adapted actual HTML/SVG paint from all 22 named standalone builders, including dark backgrounds and decorative RGBA styles. Base-gallery normalization now applies to every render, and it rejects arbitrary override values or forged allowed-color lists. A browser sweep caught intermediate SMIL paint values; paint endpoints are mapped to exact tokens and use discrete timing. Composition-sheet armatures/previews and the hub declare their active contract. The later route audit also constrained custom dither palettes and PNG preview APIs, and adapted derived SVG recreation seeds while preserving original sources and source signatures. Hex-looking fragment/marker references and CSS IDs are preserved rather than recolored or misclassified as paints. Seed preparation rejects unsupported named/functional paints until explicitly normalized, and accepts SMIL lifetime `fill=freeze/remove`. Small reusable references now match the actual generated default.
- **Procedural SVG:** Replaced the incorrect gray token, removed pink from default secondary highlights, switched generator/config/gallery defaults to colorset1, and replaced unrelated neon gallery chrome. All 66 published SVGs were regenerated with the unchanged stable catalog fingerprint `49c622bd3c49a64b`. The validator checks authored fill/stroke/CSS, filter and gradient paints, and SMIL endpoints. A bundled browser capture helper makes clean isolated preview inspection possible. Manual capture found seven pre-existing mojibake locations; those labels and formulas were corrected and the fixture was regenerated again. The final expanded stylesheet gate caught two `color-mix()` outputs, replaced by finite exact tokens. A complete computed-chrome sweep additionally caught a diagnostic-pill border's colorset2-only blue alpha base; it now uses canonical colorset1 ink plus opacity. Sixteen desktop/mobile default,hover,keyboard-focus states and all 22 family-hover instances pass, including explicit red focus outlines and no horizontal overflow.
- **Three.js:** Materials, backgrounds, fog, CSS, emissive inputs and vertex colors use exact bundled tokens. Blue/yellow scene-light inputs are neutral white, and a continuous authored vertex-color lerp became four exact color bands. The standalone validator checks material colors against the selected contract. The gallery verifier's pre-existing screenshot-root calculation was corrected from six parent levels to five and rerun in the authorized workspace.
- **SVG brief design:** Added its own palette contract. Main scaffold paint, underlays and nested details reject off-contract values; the renderer also checks custom hand-authored SVG and CSS paints before PNG export. Renderer guidance now uses its declared uv environment first. All 15 scaffold and renderer tests pass, including arbitrary nested paint and gradient-stop rejection.
- **Vectorize art:** Removed the unconstrained `source` derivative mode and made OpenCV and VTracer default to colorset1. Explicit colorset2 preserves an available semantic hue mapping while keeping visible derivative colors exact. Source images and source palettes in provenance remain immutable evidence. Both converters, geometry-locked pairs, rights gates, 60 published paired SVGs and two world maps pass. Its palette file retains art-specific `artSequence`, `backgroundCandidates` and `ink` fields; common canonical fields match exactly, so replacing the entire file would break required runtime semantics.

## Deterministic and browser coverage

The complete named-builder/catalog sweep passes **309 cases**: 44 D3 HTML variants, 264 procedural SVG variants (66 patterns × two palettes × full/reduced motion) and an off-palette gradient-stop rejection. A second **33-case** sweep passes all five D3 starters, kinetic type, logo studio, five contract-builder forms, recreation/source-integrity/style-signature checks and dither SVG/PNG checks. The latter confirms that arbitrary palettes and colorset2-only palettes are rejected under the colorset1 default, and that source lifetimes are not mistaken for paint. Recreation templates embed the existing bundled D3 runtime and set an explicit root font family, so they also pass portability and style-signature gates.

Computed SVG paint checks pass on **1,079 SVG nodes across six D3 pages**, including the three 225-pattern galleries, composition sheets, logo studio/gallery and texture atlas. The dedicated native validators also exercised all 225 base replays, each colorset gallery, seven composition sheets/78 variants, 90 logo patterns/compositions, and 40 texture patterns with controls, direct hashes and unique geometry. The procedural browser capture shows distinct initial/intermediate frames and a reduced-motion state with no page errors. The 24-scene Three.js fixture builds and passes its desktop/mobile drawing, animation, pointer and replay checks. Representative captures were visually inspected; final procedural typography now displays clean separators and formula text.

The root technical-logo audit's 12-row contact sheet also passes desktop/mobile chrome and selector smoke: 52 loaded images, all seven palette choices, no horizontal overflow, no page errors, and explicit canonical select borders/foreground/background. Original brand paints were excluded under the parent's fidelity policy. The full approximately 8k SVG audit was not repeated.

Independent read-only review of the central checker found percentage RGB, unsupported functional paint, composite named paint, inline HTML SVG attributes, CSS custom-property paint, nested-gradient and SMIL-lifetime gaps. The parent corrected the central checker. All six independent parser probes now match their expected pass/reject result, and its 12 adversarial tests pass. The central static HTML gate scans actual style blocks/style attributes and inline SVG paint while excluding vendor encoders and JavaScript literal tables. Actual browser output is covered separately by this group's computed-paint checks; source text alone cannot prove dynamically rendered paint.

## Current strict isolated forward evidence

Each accepted run uses a clean runtime payload, excludes acceptance examples, loads exactly one skill, preserves its read-only payload, creates every requested exact output path, and passes model/event/artifact/integrity gates. The observed model is `openai-codex/gpt-5.6-luna`; the event summarizer was run with `--require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error`.

| Skill | Current accepted run | Elapsed | Result |
| --- | --- | ---: | --- |
{rows}

The final D3 case exercises default and explicit circuit diagrams, browser SVG/PNG export, derived recreation seeds/template/candidate and dither SVG/PNG. Procedural generates and validates both palettes and inspects a captured animated preview. SVG brief generates two palette recipes/SVGs and renders a PNG. Vectorize proves default/explicit conversion and unchanged original source bytes. Three.js generates and browser-validates both palette scenes with actual material colors and screenshots.

Failed attempts remain under `evaluations/runs/`: requested Spark is unsupported by this ChatGPT account for SVG brief and vectorize, before any artifact work; SVG brief subsequently exposed a missing bare-Python dependency and a separate agent assertion error; procedural exposed forbidden host-temporary screenshot reads; expanded D3 tests exposed the now-repaired recreation preflight's SMIL-lifetime false positive, external CDN reference and missing explicit root font family. One further D3 trace used bare Python for the dependency-declaring dither helper's help call; the SKILL now explicitly uses uv for dependency-declaring helpers while preserving its dependency-free mandatory builder first commands. These are recorded as failures, including tool errors even when an agent later repaired its output. They were not promoted to accepted evidence. The parent should record the two new Spark rejection/Luna exceptions in the backlog while preserving pre-existing model exceptions for the other bundles.

## Boundaries and publication handoff

Exact authored tokens are the contract. Alpha compositing, antialiasing, gradient interpolation and WebGL lighting naturally produce additional displayed pixel values; the audit checks authored paints, stops, materials, lights and export contracts. Source photography/artwork and immutable original signatures retain source colors only where source fidelity is required. Authored derivative SVG paint and surrounding chrome have no blanket source-color exception.

Rebuild Pages for D3's shared galleries/composition sheets/hub, the procedural 66-SVG gallery, and Three.js. No commit, push, Pages deployment or root backlog/documentation mutation was performed by this group. The parent owns those release gates. New required resources are the D3 paint adapter and regression test, three additional self-contained palette copies, and the procedural browser capture helper; no runtime sibling dependency was introduced. A clean publication checkout also needs all ten SVG-brief bundle files (the pre-existing bundle was absent from HEAD), plus the current D3 speculative-decoding builder/verifier/test/recipe referenced by its SKILL. Those are separately identified as pre-existing publication dependencies, rather than attributed as new colorset authoring. Existing D3 vendor, palette, template and catalog files are already clean HEAD-backed dependencies.

The five colorset-focused forward cases do not replace unrelated broader acceptance work already marked validating in the backlog. Preserve those status limits. The initial Three.js verifier's incorrect root wrote two captures outside the allowed workspace before the calculation was diagnosed. That event was disclosed and the verifier corrected; the final captures are inside the workspace, and outside files were neither changed nor deleted.

Full per-skill output routes, exact touched paths, commands and evidence paths are in the JSON companion. Bulky generated artifacts and traces remain in ignored project artifact and evaluation-run folders.
"""
(OUT / "custom-visuals-20261002.md").write_text(report, encoding="utf-8")
print(json.dumps({"ok": True, "skills": len(skills), "touchedCanonicalPaths": len(touched), "deterministicCases": deterministic["caseCount"] + additional["caseCount"], "computedSvgCount": sum(r["svgCount"] for r in browser_counts), "acceptedStrictRuns": len(accepted)}))
