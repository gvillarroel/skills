#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Write the durable authoring inventory from checked bundles and review notes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
NOTES = {
    "ambientcg-material-search": "Bounded API helper; exact variant inspection, atomic download receipt, visual shortlist review, and same-ID browser recovery.",
    "animated-svg-to-gif": "Parameterized browser capture and FFmpeg defaults; exact paths, width/scaling checks, timing override, ffprobe and preview feedback.",
    "asciinema-real-command-video": "Low-freedom recording lifecycle; real executable/PTY ownership, immutable attempts, plan-only boundary, cast/media verification, and preserved failures.",
    "compose-synchronized-svg": "Brief/compiler/composer route; typed canonical state, deterministic preflight, propagation/static/browser feedback, and explicit runtime-defect reporting.",
    "d3": "Deterministic supported-form builders with selective recipes; offline geometry, palette/accessibility contracts and settled browser inspection; custom geometry remains available for unsupported forms.",
    "destockd-video-search": "Bounded shot search and immutable choice identity; observed previews, exact clip receipts, source-rights limits, and concrete browser fallback.",
    "diagram-composition": "Semantic planning plus parameterized native panels; source-bound ports and colors, draft/final audit loop, missing-specialist fallback, and visual judgment.",
    "echarts-animated-svg": "Rendered geometry preserved; chart-specific reveal recipes, deterministic timing, final-frame/replay validation, and a bundled small input template.",
    "google-cloud-sku-pricing": "Source selection precedes calculation; decimal units/tiers/model contracts, exact identifiers, snapshot provenance, and incomplete-access reporting.",
    "harbor-author-evaluation-datasets": "Ordered predeclared family/split workflow; deterministic materialization, adversarial verifier controls, privacy boundaries, and aggregate-only report contracts.",
    "hierarchy-lens": "Explicit visualization routes and flat-tree contract; bounded deterministic builder, browser/policy checks, numeric/missing-data semantics, and scale limitations.",
    "hyperframes-explainer": "Minimal causal explanation, one shared state and seekable clock, explicit palette policy, pure-state extension contract, and native render/media feedback; concurrent creation tracked separately.",
    "iconify-icon-search": "One consistent family and stable exact ID; bounded previews, verified vector exports, license receipts, and same-identity browser recovery.",
    "jev-batch-decisions": "Typed rubrics and bounded map/reduce planning; declared dependencies/credentials, resumable input hashes, complete coverage gate, and sanitized partial-failure reports.",
    "kenney-asset-search": "Free-pack selection and exact member inventory; CRC/license-preserving extraction, immutable choices, and concrete free-download browser recovery.",
    "manim-svg-video": "SVG-only ownership with explicit static/animated import limitations; configurable dry run, short render, exact-duration repair, and media/manifest checks.",
    "mermaid": "Notation/fidelity-first workflow; selective family/animation references, write-then-check styling, accessible SVG rendering, and geometry/meaning review.",
    "one-bit-dither-svg": "Explicit mode and quality defaults; deterministic grid and stable animation palette, source flattening limits, native preview, and independent SVG/GIF validation.",
    "pexels-media-search": "Credential status without disclosure; exact photo/video variants, reviewed shortlist, provenance receipts, and a documented no-key browser route.",
    "pixel-art-image-video": "Feature-driven profile selection and explicit overrides; exact-color/alpha/audio constraints, bounded conversion, source/RGB/media validation and visual repair.",
    "plantuml-colorset-renderer": "Exact output-root mapping and palette/engine selection; local-private default, semantic preservation, report validation, and labeled expected-unavailable coverage.",
    "polyhaven-asset-search": "Type-aware bounded search and exact dependency-preserving variants; verified receipts, visual uncertainty, and same-ID browser recovery.",
    "procedural-svg-animation": "Time/seed/parameter contract with describe/list interfaces; deterministic solver invariants, readable fallback/reduced motion, static/browser feedback, and bounded performance guidance.",
    "repository-reviewer-creator": "Evidence-first specialization, current identity/scope, semantic rule routing, actionable-finding gate, safe command locations, structural repair, and generated-reviewer use checks.",
    "simulation-data-lab": "Mathematical-only boundary; predeclared variables and estimands, model activation/invariants, explicit uncertainty, immutable data/provenance and independent result recomputation.",
    "slidev-animejs": "Component-scoped Vue lifecycle and cleanup; deterministic click/seek behavior, task-specific recipes, copy-ready runtime assets, and build/browser feedback.",
    "slidev-echarts": "Modular chart registration and renderer/container requirements; deterministic click state, resize/dispose lifecycle, selective chart recipes, and build/browser checks.",
    "slidev-quality-audit": "Parameterized Playwright audit with local exception markers; report/selector-driven repairs, reruns, strict findings mode, and explicit rule interpretation.",
    "svg-brief-design": "High freedom for original geometry, parameterized scaffolds when suitable; subject/negative-space preservation, documented renderer/dependency fallback, and native/thumbnail visual repair.",
    "technical-logo-assets": "Compact manifest search and exact identity/variant export; vector/license/provenance checks, protected sources, and unavailable-variant reporting.",
    "threejs-animated-3d": "Meaningful 3D routing and explicit lifecycle; portable offline builder, deterministic capture, responsive canvas/motion/replay checks, and local-browser fallback.",
    "usefulcharts-style": "Data/knowledge-density and editorial decisions before geometry; selective construction routes, measured layouts, independent browser audit, rendered critique, and unsupported-structure fallback.",
    "vectorize-art-patterns": "Rights/source verification and explicit pipeline choice; deterministic tracing/palette contracts, no-reuse geometry, independent structural checks, and source/tile visual repair.",
    "video": "Producer artifacts plus one master clock; explicit dimensions/ports/state contracts, deterministic composition/rendering, source fidelity, media/contact-sheet feedback, and documented fallback routing.",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluations/skill-authoring/20261002-summary.json")
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    backlog = (ROOT / "SKILLS.md").read_text(encoding="utf-8")
    rows = []
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        name = path.parent.name
        if name not in NOTES:
            parser.error(f"Missing manual entrypoint review for {name}")
        metadata = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        match = re.search(r"^\| " + re.escape(name) + r" \| `([^`]+)` \|", backlog, re.MULTILINE)
        results = [result for result in audit["results"] if result["skill"] == name]
        rows.append({"skill": name, "backlogStatus": match[1] if match else None, "entrySha256": hashlib.sha256(path.read_bytes()).hexdigest(), "description": metadata["description"], "manualGuidanceReview": NOTES[name], "profileResults": [{key: value for key, value in result.items() if key != "limitations"} for result in results]})
    report = {"date": "2026-10-02", "source": "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices", "skillCount": len(rows), "authoringAndBundlesPassed": audit["passed"], "skills": rows, "behavioralScope": "Use prior per-skill backlog evidence and explicitly enumerated fresh routing/D3/reviewer tests. No claim of universal model compatibility or a new behavioral release of every skill."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    table = ["| Skill | Backlog status | Source / runtime / full | Manual workflow and feedback review |", "| --- | --- | --- | --- |"]
    for row in rows:
        profiles = {item["profile"]: "pass" if item["passed"] else "fail" for item in row["profileResults"]}
        table.append(f"| {row['skill']} | `{row['backlogStatus']}` | {' / '.join(profiles.get(profile, 'pending') for profile in ('source', 'runtime', 'full'))} | {row['manualGuidanceReview']} |")
    (ROOT / "projects/skill-authoring-audit/artifacts/reviews/inventory-table.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    print(json.dumps({"skillCount": len(rows), "authoringAndBundlesPassed": audit["passed"], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
