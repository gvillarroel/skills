#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check whole and premise-local decisions for borrowed-type contrasts."""

from argparse import ArgumentParser
import json
from pathlib import Path


FIELDS = ("whole_equivalent", "p02_equivalent", "safe_comparison_view")
EXPECTED = {"K01": (True, False, False), "K02": (True, True, True), "K03": (True, False, False)}


def unique_object(items):
    value = dict(items)
    if len(value) != len(items):
        raise ValueError("duplicate JSON key")
    return value


def grade(path):
    result = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    if type(result) is not dict:
        raise ValueError("expected a JSON object")
    incorrect = []
    for case, expected in EXPECTED.items():
        row = result.get(case)
        if type(row) is not dict or row.keys() != set(FIELDS) or any(
            row[field] is not value for field, value in zip(FIELDS, expected, strict=True)
        ):
            incorrect.append(case)
    extra = sorted(set(result) - set(EXPECTED))
    return {"passed": not incorrect and not extra, "correct": len(EXPECTED) - len(incorrect),
            "checks": len(EXPECTED), "incorrect": incorrect, "extra": extra}


if __name__ == "__main__":
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("artifact", type=Path)
    args = cli.parse_args()
    try:
        verdict = grade(args.artifact)
    except (OSError, ValueError) as exc:
        verdict = {"passed": False, "error": str(exc)}
    print(json.dumps(verdict, indent=2))
    raise SystemExit(not verdict["passed"])
