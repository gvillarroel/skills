#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check the decisions in the independent OWL comparison review fixture."""

from argparse import ArgumentParser
import json
from pathlib import Path


def decisions(whole, local):
    return {"whole_equivalent": whole, "all_premises_equivalent": local, "publish": whole and local}


def branches(neither):
    return {"a_only": True, "b_only": True, "both": False, "neither": neither}


EXPECTED = {
    "S01": decisions(True, True),
    "S02": decisions(True, False),
    "S03": decisions(False, False),
    "S04": decisions(False, False),
    "S05": decisions(True, True),
    "S06": {"ontology_consistent": True, "class_satisfiable": False},
    "S07": branches(False),
    "S08": branches(True),
}


def unique_object(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def check(path):
    data = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    if type(data) is not dict:
        raise ValueError("expected a JSON object")
    invalid = sorted(case for case, expected in EXPECTED.items() if type(data.get(case)) is not dict
                     or data[case].keys() != expected.keys()
                     or any(data[case][field] is not value for field, value in expected.items()))
    extra = sorted(data.keys() - EXPECTED.keys())
    return {"passed": not invalid and not extra, "checks": len(EXPECTED),
            "correct": len(EXPECTED) - len(invalid), "incorrect_cases": invalid, "unexpected_cases": extra}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("reviews", type=Path)
    args = parser.parse_args()
    try:
        report = check(args.reviews)
    except (OSError, ValueError) as exc:
        report = {"passed": False, "error": str(exc)}
    print(json.dumps(report, indent=2))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
