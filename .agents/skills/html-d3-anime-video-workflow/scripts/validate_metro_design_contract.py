#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_SECTIONS = [
    "# Metro Design Production Plan",
    "## Source Facts",
    "## Megacanvas Composition",
    "## Pattern Selection",
    "## Beat Plan",
    "## Text Budget",
    "## Motion Systems",
    "## Camera Path",
    "## Rejection Gate",
]

REQUIRED_CONTRACT_VALUES: dict[str, Any] = {
    "passed": True,
    "style": "Metro Minimal Tonal Motion",
    "colorset": "colorset1",
    "roundedBorders": False,
    "internalBoxPadding": False,
    "titleBandsAllowed": False,
}


def read_json(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [{"code": "contract-read-failed", "path": str(path), "error": str(exc)}]
    if not isinstance(data, dict):
        return {}, [{"code": "contract-not-object", "path": str(path)}]
    return data, []


def check_contract(contract: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    for key, expected in REQUIRED_CONTRACT_VALUES.items():
        actual = contract.get(key)
        if actual != expected:
            findings.append({"code": "contract-value-mismatch", "field": key, "expected": expected, "actual": actual})

    numeric_minimums = {
        "minimumFunctionalZones": args.min_functional_zones,
        "minimumSemanticMotionSystems": args.min_semantic_motion_systems,
        "minimumCameraEvents": args.min_camera_events,
    }
    for key, minimum in numeric_minimums.items():
        actual = contract.get(key)
        if not isinstance(actual, (int, float)) or actual < minimum:
            findings.append({"code": "contract-minimum-too-low", "field": key, "minimum": minimum, "actual": actual})

    pattern_ids = contract.get("patternIdsNamed")
    if not isinstance(pattern_ids, list) or len([item for item in pattern_ids if isinstance(item, str) and item]) < args.min_patterns_named:
        findings.append(
            {
                "code": "too-few-pattern-ids-named",
                "minimum": args.min_patterns_named,
                "actual": pattern_ids if isinstance(pattern_ids, list) else None,
            }
        )

    used_patterns = contract.get("patternsUsedInBeats")
    if not isinstance(used_patterns, list) or len([item for item in used_patterns if isinstance(item, str) and item]) < args.min_patterns_used:
        findings.append(
            {
                "code": "too-few-patterns-used-in-beats",
                "minimum": args.min_patterns_used,
                "actual": used_patterns if isinstance(used_patterns, list) else None,
            }
        )

    if isinstance(pattern_ids, list) and isinstance(used_patterns, list):
        missing = sorted({item for item in used_patterns if isinstance(item, str)} - {item for item in pattern_ids if isinstance(item, str)})
        if missing:
            findings.append({"code": "used-patterns-not-named", "missing": missing})

    mute_test = contract.get("muteTestExpectedInference")
    if not isinstance(mute_test, str) or len(mute_test.strip()) < args.min_mute_test_chars:
        findings.append(
            {
                "code": "mute-test-too-thin",
                "minimumChars": args.min_mute_test_chars,
                "actualChars": len(mute_test.strip()) if isinstance(mute_test, str) else 0,
            }
        )

    return findings


def check_plan(plan_text: str, args: argparse.Namespace, contract: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    for section in REQUIRED_SECTIONS:
        if section not in plan_text:
            findings.append({"code": "missing-required-section", "section": section})

    lower = plan_text.lower()
    required_phrases = [
        "megacanvas",
        "no internal box padding",
        "4 px",
        "corner radius",
        "camera",
        "grayscale",
        "colorset1",
    ]
    for phrase in required_phrases:
        if phrase not in lower:
            findings.append({"code": "missing-design-phrase", "phrase": phrase})

    for literal in args.require_text:
        if literal not in plan_text:
            findings.append({"code": "missing-required-text", "text": literal})

    for pattern in contract.get("patternsUsedInBeats", []):
        if isinstance(pattern, str) and pattern and pattern not in plan_text:
            findings.append({"code": "used-pattern-not-in-plan", "pattern": pattern})

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Metro Minimal Tonal Motion design plan and contract JSON.")
    parser.add_argument("--plan", "--markdown", dest="plan", type=Path, help="Path to production-plan.md.")
    parser.add_argument("--contract", type=Path, help="Path to design-contract.json.")
    parser.add_argument("--output", "--out", dest="output", type=Path, help="Path to write validation JSON. If omitted, JSON is printed to stdout.")
    parser.add_argument("--min-functional-zones", type=int, default=3)
    parser.add_argument("--min-semantic-motion-systems", type=int, default=3)
    parser.add_argument("--min-camera-events", type=int, default=2)
    parser.add_argument("--min-patterns-named", type=int, default=6)
    parser.add_argument("--min-patterns-used", type=int, default=3)
    parser.add_argument("--min-mute-test-chars", type=int, default=80)
    parser.add_argument("--require-text", action="append", nargs="+", default=[])
    parser.add_argument("paths", nargs="*", help="Optional positional plan and contract paths.")
    args = parser.parse_args()
    if args.plan is None and args.paths:
        args.plan = Path(args.paths[0])
    if args.contract is None and len(args.paths) > 1:
        args.contract = Path(args.paths[1])
    if args.plan is None or args.contract is None:
        parser.error("provide --plan/--markdown and --contract, or positional PLAN CONTRACT")
    args.require_text = [item for group in args.require_text for item in group]

    findings: list[dict[str, Any]] = []
    try:
        plan_text = args.plan.read_text(encoding="utf-8")
    except OSError as exc:
        plan_text = ""
        findings.append({"code": "plan-read-failed", "path": str(args.plan), "error": str(exc)})

    contract, contract_findings = read_json(args.contract)
    findings.extend(contract_findings)
    if contract:
        findings.extend(check_contract(contract, args))
    if plan_text:
        findings.extend(check_plan(plan_text, args, contract))

    report = {
        "passed": not findings,
        "plan": str(args.plan),
        "contract": str(args.contract),
        "checks": {
            "requiredSectionCount": len(REQUIRED_SECTIONS),
            "minFunctionalZones": args.min_functional_zones,
            "minSemanticMotionSystems": args.min_semantic_motion_systems,
            "minCameraEvents": args.min_camera_events,
            "minPatternsNamed": args.min_patterns_named,
            "minPatternsUsed": args.min_patterns_used,
        },
        "findings": findings,
    }
    rendered_report = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered_report, encoding="utf-8")
    else:
        print(rendered_report)
    if findings:
        if args.output:
            print(f"Metro design contract validation failed: {args.output}", file=sys.stderr)
        return 1
    if args.output:
        print(f"Metro design contract validation passed: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
