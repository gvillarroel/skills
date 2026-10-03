#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Track the style revision without discarding previous release status or evidence."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
NOTE = "Solid-fill revision 2026-10-03: [borderless priority, contrast, validation and publication](evaluations/solid-colorset-style/validation-20261003.md)."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore-validated", action="store_true")
    args = parser.parse_args()
    inventory = json.loads((ROOT / "evaluations/colorset-audit/coverage.json").read_text(encoding="utf-8"))
    visual = {row["skill"] for row in inventory["skills"] if row["scope"] != "nonvisual"}
    original = subprocess.run(["git", "show", "HEAD:SKILLS.md"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    original_status = {line.split("|")[1].strip(): line.split("|")[2].strip() for line in original.splitlines() if line.startswith("| ") and len(line.split("|")) >= 6}
    path = ROOT / "SKILLS.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("| "):
            continue
        fields = line.split("|")
        if len(fields) < 6 or fields[1].strip() not in visual:
            continue
        name = fields[1].strip()
        fields[2] = " " + (original_status[name] if args.restore_validated else "`validating`") + " "
        if name == "harbor-author-evaluation-datasets" and "assets/palettes" not in fields[4]:
            fields[4] = fields[4].replace("scripts, references,", "scripts, references, assets/palettes,")
        if NOTE not in fields[-2]:
            fields[-2] = fields[-2].rstrip() + " " + NOTE + " "
        lines[index] = "|".join(fields)
    if args.restore_validated:
        recent = "- Solid presentation revision 2026-10-03: all 30 authored-output bundles prioritize opaque solid fills without decorative outlines, maximum-contrast black/white text, and full palette exhaustion before explicit border variants. Canonical color tokens and stable pattern IDs remain unchanged. Final strict isolated runs match all 30 current runtime payloads; custom renderers additionally have 20 passing contract/naturalistic runs, with failed and superseded attempts retained. Renderer fixtures, browser/media checks, full runtime/source bundle checks, repository gates, installation and publication evidence are recorded in [the final revision report](evaluations/solid-colorset-style/validation-20261003.md). This supplementary style validation preserves prior broader release statuses and existing model exceptions."
        if recent not in lines:
            heading = lines.index("## Recent Validation Notes")
            lines.insert(heading + 2, recent)
            lines.insert(heading + 3, "")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Updated style revision state for {len(visual)} authored-output bundles.")


if __name__ == "__main__":
    main()
