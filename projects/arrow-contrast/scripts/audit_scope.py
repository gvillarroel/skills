#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record all bundle arrow ownership and source-preservation review boundaries."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
GROUPS = {
    "diagrams": {"mermaid", "plantuml-colorset-renderer", "echarts-animated-svg", "slidev-echarts", "slidev-animejs", "slidev-quality-audit"},
    "custom": {"d3", "threejs-animated-3d", "procedural-svg-animation", "svg-brief-design", "vectorize-art-patterns"},
    "composition": {"compose-synchronized-svg", "diagram-composition", "hierarchy-lens", "usefulcharts-style", "hyperframes-explainer", "video", "manim-svg-video"},
}
SOURCE = {"ambientcg-material-search", "iconify-icon-search", "kenney-asset-search", "pexels-media-search", "polyhaven-asset-search", "destockd-video-search", "technical-logo-assets"}
CONVERTERS = {"animated-svg-to-gif", "asciinema-real-command-video", "one-bit-dither-svg", "pixel-art-image-video"}
MATCH = re.compile(r"marker-(?:end|start)|ArrowHelper|edgeSymbol|arrowhead|draw_arrow|drawArrow|[→←↔]", re.I)


def main():
    original = json.loads((ROOT / "evaluations/colorset-audit/coverage.json").read_text(encoding="utf-8"))
    rows = []
    for entry in original["skills"]:
        name = entry["skill"]
        owner = next((group for group, names in GROUPS.items() if name in names), "root-support")
        if entry["scope"] == "nonvisual":
            boundary = "No authored visual arrows; retain nonvisual data/report contracts."
        elif name in SOURCE:
            boundary = "Retrieved/source logo or icon arrows preserve identity; authored preview chrome uses existing binary contrast. No semantic connector route is generated."
        elif name in CONVERTERS:
            boundary = "Conversion/capture preserves supplied arrow artwork and timing; verify representative exported arrow visibility rather than inventing a semantic route."
        elif name == "harbor-author-evaluation-datasets":
            boundary = "Two authored directional arrow glyphs in axis captions; actual stage/text contrast review."
        elif name in {"hierarchy-lens", "vectorize-art-patterns"}:
            boundary = "No native semantic arrow producer; inspect navigation/source-derived geometry without adding unrelated arrows."
        else:
            boundary = "Owning group reviews authored shafts, heads, terminals and relevant renderer/import/auditor behavior."
        matches = []
        for path in sorted((ROOT / "skills" / name).rglob("*")):
            rel = path.relative_to(ROOT / "skills" / name)
            if (not path.is_file() or path.suffix.lower() not in {".py", ".ts", ".js", ".mjs", ".svg", ".vue", ".html"}
                    or any(part in {"node_modules", "vendor", "logos", "dist", "__pycache__", ".git"} for part in rel.parts)
                    or rel.parts[:2] == ("assets", "examples")):
                continue
            try:
                count = len(MATCH.findall(path.read_text(encoding="utf-8")))
            except UnicodeError:
                continue
            if count:
                matches.append({"path": rel.as_posix(), "indicatorCount": count})
        rows.append({"skill": name, "owner": owner, "outputScope": entry["scope"], "boundary": boundary,
                     "runtimeCodeIndicators": matches})
    report = {"date": "2026-10-03", "bundleCount": len(rows), "skills": rows,
              "scope": "Full 34-bundle inventory and manual ownership boundaries. Text indicators locate candidates, not proof that an arrow is generated or passes actual contrast. Owning rendered/isolated evidence supplies acceptance."}
    target = ROOT / "evaluations/arrow-contrast/coverage-20261003.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded arrow ownership and source boundaries for {len(rows)} bundles.")


if __name__ == "__main__":
    main()
