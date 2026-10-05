#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Freeze a new focused gray-prefix family without changing previous cases."""
from pathlib import Path
import hashlib
import json
import collect_acceptance

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LABELS = ["Intake", "Triage", "Research", "Proposal", "Review", "Planning", "Design", "Build",
          "Test", "Repair", "Approval", "Release", "Observe"]


def main():
    target = HERE / "cases-prefix.json"
    prompts = HERE / "prompts-prefix"
    if target.exists() or prompts.exists():
        raise SystemExit("The prefix family is already frozen; preserve it and use a new revision for changes.")
    cases = json.loads((HERE / "cases.json").read_bytes())
    prompts.mkdir()
    for skill, case in cases.items():
        prompt = (
            f"Use only the copied `{skill}` bundle and normal local tools. Treat `skills/{skill}/` as read-only. "
            "This focused test authors a companion categorical key; it does not retrieve, regenerate or validate the skill's primary source media. "
            "Do not read acceptance examples, other skills, repository documents or external source files. Write all outputs in this workspace.\n\n"
            "Create a small standalone SVG key for a multi-panel explanation using Colorset1 on a white canvas. "
            "Show exactly thirteen categories in this reading order: " + ", ".join(LABELS) + ". "
            "Read the bundled palette JSON before allocating fills. Use its `solidSequence` as category order; "
            "`allowed` is membership and `roles` is semantic paint, not category order. Exclude the actual white canvas token, "
            "then assign the first thirteen usable solid fills in order. This covers primary red and the twelve-neutral prefix. "
            "Keep all thirteen bodies opaque and borderless. Put each complete label inside its body using the bundle's `textOnFill` black/white choice. "
            "Use clear spacing and at least 18 px text. Give the SVG an accessible title and description. No JavaScript or external resources are needed.\n\n"
            "Separately show a quantitative legend labeled 'Low', 'Medium-low', 'Medium', 'Medium-high', 'High', "
            "using the supplied ordered ramp #1c1c1c, #4f4f4f, #828282, #b5b5b5, #e7e7e7. Keep its quantitative order intact.\n\n"
            "Write exactly `key.svg` and `allocation.json`. Mark each actual category body with `data-category-index` from 0 to 12, "
            "and its label with `data-category-label` equal to that index. Mark each quantitative body with `data-quantitative-index` from 0 to 4. "
            "The JSON must contain `canvas`, a `categories` array of thirteen objects with `index`, `label`, `fill`, `text`, "
            "and `stroke` (use 'none'), and a `quantitativeRamp` array with the five supplied tokens. "
            "Set SVG width and height so every body and complete label is visible at its native size. Inspect the SVG structure and JSON before finishing.\n\n"
            "Keep every category and quantitative mark and label fully visible and opaque. Paint the actual canvas white. "
            "Require at least 4.5:1 contrast against the surface actually behind each label. A quantitative caption may sit outside "
            "its swatch when clear, associated with that swatch, and disjoint from all painted category and quantitative marks. "
            "This case stops after the neutral prefix; it does not test white, remaining hues or manual overflow styling.\n"
        )
        path = prompts / f"{skill}.md"
        path.write_text(prompt, encoding="utf-8", newline="\n")
        item = case["naturalistic"]
        item.update(prompt=path.relative_to(HERE).as_posix(), repetitions=3,
                    caseFamily="gray-prefix", categoryCount=13,
                    promptSha256=hashlib.sha256(prompt.encode()).hexdigest())
        case["frozenNormalizedPayloadSha256"] = collect_acceptance.digest(
            collect_acceptance.inventory(ROOT / "skills" / skill))
        case["contract"]["caseFamily"] = "complete-contract"
    target.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"revision": "r4", "owners": len(cases), "categoryCount": 13,
                      "naturalisticRepetitions": 3, "cases": target.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__":
    main()
