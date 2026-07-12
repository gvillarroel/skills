#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Advisory validation for a compact synchronized-SVG brief."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any


sys.dont_write_bytecode = True

import compile_synchronized_svg_plan as compiler  # noqa: E402


class JsonArgumentParser(argparse.ArgumentParser):
    """Keep argument failures machine-readable for automation."""

    def error(self, message: str) -> None:
        print(json.dumps({"ok": False, "error": f"argument error: {message}"}, indent=2))
        raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = JsonArgumentParser(
        description=(
            "Validate a compact synchronized-SVG brief without publishing a plan or turning "
            "expected authoring findings into a failing tool call."
        )
    )
    parser.add_argument("--brief", required=True, type=Path, help="Compact brief JSON to inspect")
    parser.add_argument(
        "--strict-exit",
        action="store_true",
        help="Return exit code 1 for an invalid brief; intended for CI, not iterative authoring",
    )
    parser.add_argument("--json", action="store_true", help="Print the compact JSON result")
    return parser.parse_args()


def invalid_result(brief_path: Path, error: Exception) -> dict[str, Any]:
    syntax_error = isinstance(error, compiler.DuplicateKeyError) or isinstance(
        error.__cause__, json.JSONDecodeError
    )
    result: dict[str, Any] = {
        "ok": False,
        "brief": str(brief_path),
        "stage": "syntax" if syntax_error else "semantic",
        "finding": str(error),
    }
    cause = error.__cause__
    if isinstance(cause, json.JSONDecodeError):
        result["location"] = {
            "line": cause.lineno,
            "column": cause.colno,
            "position": cause.pos,
        }
    return result


def print_result(result: dict[str, Any], json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if result["ok"]:
        print(f"Preflight passed for {result['brief']}")
    else:
        print(f"Preflight finding: {result['finding']}")


def main() -> int:
    args = parse_args()
    brief_path = args.brief.resolve()
    try:
        brief = compiler.load_brief(brief_path)
        plan, normalizations = compiler.compile_brief(copy.deepcopy(brief))
        result = {
            "ok": True,
            "brief": str(brief_path),
            "compositionId": brief.get("compositionId"),
            "moduleCount": len(plan["modules"]),
            "normalizations": normalizations,
        }
        print_result(result, args.json)
        return 0
    except (compiler.BriefError, OSError) as exc:
        result = invalid_result(brief_path, exc)
        print_result(result, args.json)
        return 1 if args.strict_exit else 0


if __name__ == "__main__":
    raise SystemExit(main())
