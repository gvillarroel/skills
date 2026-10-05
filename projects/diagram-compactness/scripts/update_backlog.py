#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record this audit's validation state without rewriting historical notes."""
from pathlib import Path

root = Path(__file__).resolve().parents[3]
skills = {
    "mermaid", "plantuml-colorset-renderer", "usefulcharts-style", "d3",
    "procedural-svg-animation", "svg-brief-design", "diagram-composition",
    "compose-synchronized-svg", "threejs-animated-3d", "hyperframes-explainer",
    "video", "slidev-animejs", "slidev-echarts", "echarts-animated-svg",
    "slidev-quality-audit",
}
path = root / "SKILLS.md"
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
marker = "Diagram compactness revision 2026-10-04:"
note = (
    marker + " default to the smallest readable connected layout; preserve "
    "labels, full arrowheads, traceable endpoints, separate lanes and motion "
    "clearance. Quantitative charts retain useful data dimensions and scales. "
    "Validation in progress. Recorded forward-test model exception for this "
    "audit: `openai-codex/gpt-5.6-luna`, after Spark was rejected as unsupported "
    "with this ChatGPT account before any tool call. Exact-output, isolation, "
    "zero-tool-error and immutable-payload gates remain required. "
    "[Scope, commands and outcomes](evaluations/diagram-compactness/validation-20261004.md). "
)
for index, line in enumerate(lines):
    if not line.startswith("| "):
        continue
    cells = line.rstrip("\r\n").split("|")
    if cells[1].strip() not in skills:
        continue
    cells[2] = " `validating` "
    if marker not in cells[-2]:
        cells[-2] = cells[-2].rstrip() + " " + note
    lines[index] = "|".join(cells) + "\n"
path.write_text("".join(lines), encoding="utf-8", newline="")
print(f"Recorded validation state for {len(skills)} diagram-producing/audit skills.")
