#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Close this revision only after its independently accepted run registry exists."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

from source_integrity import runtime_digest


ROOT = Path(__file__).resolve().parents[3]
MARKER = "Diagram compactness revision 2026-10-04:"
REPORT = "evaluations/diagram-compactness/validation-20261004.md"
REGISTRY = ROOT / "evaluations/diagram-compactness/acceptance-20261004.json"
EXPECTED = {"mermaid", "plantuml-colorset-renderer", "usefulcharts-style", "d3",
            "svg-brief-design", "procedural-svg-animation", "diagram-composition",
            "compose-synchronized-svg", "threejs-animated-3d", "hyperframes-explainer",
            "video", "slidev-animejs", "slidev-echarts", "echarts-animated-svg",
            "slidev-quality-audit"}


def original_statuses() -> dict[str, str]:
    source = subprocess.run(["git", "show", "HEAD:SKILLS.md"], cwd=ROOT, check=True,
                            capture_output=True, text=True, encoding="utf-8").stdout
    return {cells[1].strip(): cells[2].strip()
            for line in source.splitlines() if line.startswith("| ")
            for cells in [line.split("|")] if len(cells) >= 6}


def validate_registry() -> dict[str, dict]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows = {row["skill"]: row for row in registry["skills"]}
    if set(rows) != EXPECTED or not registry["passed"]:
        raise ValueError("The final accepted registry must cover exactly the 15 changed bundles.")
    for skill, row in rows.items():
        if runtime_digest(skill) != row["sourcePayloadSha256"]:
            raise ValueError(f"Accepted registry no longer matches live canonical source: {skill}")
        naturals = row["naturals"]
        if len(naturals) != 3 or sum(case["jointPass"] for case in naturals) < 2:
            raise ValueError(f"Incomplete natural repetition gate: {skill}")
        for case in [row["contract"], *row.get("additionalContracts", []), *naturals]:
            result_path = ROOT / "evaluations/runs" / case["run"] / "evaluation-result.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if case["strictPass"] != result["passed"]:
                raise ValueError(f"Registry disagrees with the retained strict result: {case['run']}")
            if case["jointPass"] and not (result["passed"] and case["independentPass"]):
                raise ValueError(f"Joint pass lacks strict or independent evidence: {case['run']}")
        if not row["contract"]["jointPass"] or not all(case["jointPass"] for case in row.get("additionalContracts", [])):
            raise ValueError(f"Incomplete deterministic contract gate: {skill}")
    return rows


def main() -> int:
    rows = validate_registry()
    original = original_statuses()
    path = ROOT / "SKILLS.md"
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = []
    for index, line in enumerate(lines):
        if not line.startswith("| "):
            continue
        cells = line.rstrip("\r\n").split("|")
        skill = cells[1].strip()
        if skill not in rows:
            continue
        if MARKER not in cells[-2]:
            raise ValueError(f"Audit marker missing from backlog: {skill}")
        status = original[skill]
        if status not in {"`done`", "`validating`"}:
            raise ValueError(f"Unexpected original status: {skill}: {status}")
        cells[2] = f" {status} "
        count = sum(case["jointPass"] for case in rows[skill]["naturals"])
        model = rows[skill]["model"]
        note = (f"{MARKER} default to the smallest readable connected layout; preserve full labels, "
                "complete heads, traceable endpoints, independent lanes and motion clearance. "
                "Quantitative charts retain useful data dimensions and scales. Scoped revision passes "
                f"its strict/independent contract and {count}/3 natural repetitions, with documented boundaries "
                "and retained unsuccessful attempts. "
                f"Forward-test model: `{model}`, the recorded exception after Spark was unsupported "
                "with this ChatGPT account before tools. ")
        if model.endswith("gpt-5.6-sol"):
            note += "The consumer Sol exception follows retained Luna execution/visual failures; strict gates are unchanged. "
        if skill == "slidev-animejs":
            note += "The geometry cohort and byte-identical narrow paint repair have separately identified hashes and exact final contracts. "
        if status == "`validating`":
            note += "Broader historical validation questions remain open; this scoped pass does not clear them. "
        note += f"[Scope, commands, evidence and limits]({REPORT}). "
        cells[-2] = cells[-2].split(MARKER, 1)[0].rstrip() + " " + note
        lines[index] = "|".join(cells) + "\n"
        changed.append(skill)
    if set(changed) != EXPECTED:
        raise ValueError("Not all expected backlog rows were updated.")
    path.write_text("".join(lines), encoding="utf-8", newline="")
    print(json.dumps({"updatedSkills": len(changed), "restoredDone": sum(original[name] == "`done`" for name in changed),
                      "retainedBroaderValidating": sum(original[name] == "`validating`" for name in changed)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
