#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Grade presentation-invariant ontology option selection."""

from argparse import ArgumentParser
import json
from pathlib import Path

from grade_ontology_borrowed_scope import unique_object


EXPECTED = {"A1": "a82", "A2": "z21", "B1": "b76", "B2": "y02", "C1": "NONE", "C2": "c43"}


def grade(path):
    result = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    if type(result) is not dict:
        raise ValueError("expected a JSON object")
    incorrect = [key for key, value in EXPECTED.items() if result.get(key) != value]
    extra = sorted(result.keys() - EXPECTED.keys())
    return {"passed": not incorrect and not extra, "correct": len(EXPECTED) - len(incorrect),
            "checks": len(EXPECTED), "incorrect": incorrect, "extra": extra}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    try:
        verdict = grade(parser.parse_args().artifact)
    except (OSError, ValueError) as exc:
        verdict = {"passed": False, "error": str(exc)}
    print(json.dumps(verdict, indent=2))
    raise SystemExit(not verdict["passed"])
