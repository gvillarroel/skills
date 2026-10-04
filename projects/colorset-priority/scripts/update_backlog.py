#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Track the narrow CS1 priority revision without changing unrelated backlog history."""

import argparse
from pathlib import Path

root = Path(__file__).resolve().parents[3]
path = root / "SKILLS.md"
owners = {"d3", "mermaid", "plantuml-colorset-renderer", "echarts-animated-svg", "slidev-echarts", "threejs-animated-3d", "procedural-svg-animation", "vectorize-art-patterns"}
noted_owners = owners | {palette.parents[2].name for palette in (root / "skills").glob("*/assets/palettes/colorsets.json")}
note = " Colorset 1 priority revision 2026-10-04: [primary red, grays, black, white, remaining colors and validation](evaluations/colorset-priority-20261004.md)."
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--phase", choices=("validating", "done"), default="validating")
args = parser.parse_args()
text = path.read_text(encoding="utf-8")
lines = text.splitlines()
for index, line in enumerate(lines):
    if not line.startswith("| "):
        continue
    name = line.split("|")[1].strip()
    if name not in noted_owners:
        continue
    fields = line.split("|")
    if name in owners:
        fields[2] = f" `{args.phase}` "
    if note.strip() not in fields[-2]:
        fields[-2] = fields[-2].rstrip() + note + " "
    lines[index] = "|".join(fields)
text = "\n".join(lines) + "\n"
heading = "### Colorset 1 Category Priority — 2026-10-04"
if heading not in text:
    text = text.replace("## Recent Validation Notes\n", "## Recent Validation Notes\n\n" + heading + "\n\n- The explicit category order is primary red, all grays, black, white, then the remaining red variants and pink. Both shared sequences and all 30 bundled copies use the complete 17-token order; exact canvas paints are excluded only when needed for a visible categorical body. Named semantic roles and source-artwork fidelity remain separate from category assignment.\n- Renderer defaults and published CS1 fixtures are being checked through actual body paints, native text contrast, and complete arrow geometry. The revision remains under validation until frozen isolated runs and Pages publication finish. Current commands, evidence, and retained failures: [priority revision](evaluations/colorset-priority-20261004.md).\n", 1)
if args.phase == "done":
    before, section = text.split(heading, 1)
    current, separator, after = section.partition("\n### ")
    current = current.replace(
        "Renderer defaults and published CS1 fixtures are being checked through actual body paints, native text contrast, and complete arrow geometry. The revision remains under validation until frozen isolated runs and Pages publication finish. Current commands, evidence, and retained failures:",
        "Renderer defaults, existing galleries, and new isolated outputs pass the corrected category order, native text contrast, and complete arrow geometry gates. Frozen forward tests, repository checks, local installation, exact-commit Pages deployment, and public browser/resource verification are complete. Commands, evidence, model exceptions, and retained failed candidates:",
    )
    text = before + heading + current + separator + after
path.write_text(text, encoding="utf-8", newline="\n")
print(f"Updated the CS1 priority owners to {args.phase}.")
