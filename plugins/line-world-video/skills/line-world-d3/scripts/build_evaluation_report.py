#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a deterministic D3/SVG composition evaluation and decision record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Pass every public required term exactly as written with a repeated
--required-term flag. Do not normalize spaces, punctuation, selectors, or case.

Example:
  python3 build_evaluation_report.py \\
    --output deliverables/evaluation.md \\
    --decision-output deliverables/decision.json \\
    --artifact visual.svg --score 72 --colorset colorset1 \\
    --pattern-id d3-composition-audit --reason "Composition audit route." \\
    --required-term "reading path" --required-term "implementation contract" \\
    --composition-finding "#label overlaps #node and obscures the reading path." \\
    --implementation-finding "implementation contract: add a nonzero leader." \\
    --validation "Render in Chromium and inspect label clearance."
""",
    )
    parser.add_argument("--output", type=Path, required=True, help="Exact Markdown output path.")
    parser.add_argument("--decision-output", type=Path, required=True, help="Exact decision JSON path.")
    parser.add_argument("--artifact", required=True, help="Artifact identifier; becomes the exact first line.")
    parser.add_argument("--score", type=int, required=True, help="Reconciled integer score from 0 through 100.")
    parser.add_argument("--route", default="evaluation", choices=("evaluation",))
    parser.add_argument("--colorset", required=True, choices=("colorset1", "colorset2"))
    parser.add_argument("--pattern-id", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--required-term", action="append", default=[], metavar="EXACT-LITERAL")
    parser.add_argument("--composition-finding", action="append", default=[], metavar="TEXT")
    parser.add_argument("--implementation-finding", action="append", default=[], metavar="TEXT")
    parser.add_argument("--validation", action="append", default=[], metavar="CHECK")
    parser.add_argument("--force", action="store_true")
    return parser


def build(args: argparse.Namespace) -> tuple[str, dict[str, str]]:
    if not 0 <= args.score <= 100:
        raise ValueError("--score must be between 0 and 100")
    if not args.composition_finding:
        raise ValueError("At least one --composition-finding is required")
    if not args.implementation_finding:
        raise ValueError("At least one --implementation-finding is required")
    if not args.validation:
        raise ValueError("At least one --validation check is required")
    if any(not value.strip() for value in (
        args.artifact,
        args.pattern_id,
        args.reason,
        *args.required_term,
        *args.composition_finding,
        *args.implementation_finding,
        *args.validation,
    )):
        raise ValueError("Report literals and findings must be non-empty")

    def bullets(values: list[str]) -> str:
        return "\n".join(f"- {value}" for value in values)

    sections = [
        f"Artifact: {args.artifact}",
        "",
        "# Composition evaluation",
        "",
        "## Composition findings",
        "",
        bullets(args.composition_finding),
        "",
        "## Implementation contract findings",
        "",
        bullets(args.implementation_finding),
    ]
    if args.required_term:
        sections.extend((
            "",
            "## Required contract coverage",
            "",
            bullets(args.required_term),
        ))
    sections.extend((
        "",
        f"Overall composition score: {args.score}/100",
        "",
        "## Validation",
        "",
        bullets(args.validation),
        "",
    ))
    decision = {
        "route": args.route,
        "colorset": args.colorset,
        "patternId": args.pattern_id,
        "reason": args.reason,
    }
    return "\n".join(sections), decision


def main() -> int:
    args = make_parser().parse_args()
    if args.output.resolve() == args.decision_output.resolve():
        raise SystemExit("--output and --decision-output must differ")
    for path in (args.output, args.decision_output):
        if path.exists() and not args.force:
            raise SystemExit(f"Refusing existing output without --force: {path}")
    try:
        report, decision = build(args)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.decision_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8", newline="\n")
    args.decision_output.write_text(
        json.dumps(decision, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"output": str(args.output), "decision": str(args.decision_output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
