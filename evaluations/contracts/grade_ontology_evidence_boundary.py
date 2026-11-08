#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check whether the reviewed claims use complete and applicable evidence."""

from argparse import ArgumentParser
import json
from pathlib import Path

EXPECTED = {
    "count": {"decision": "admit", "span_id": "a2"},
    "variants": {"decision": "admit", "span_id": "b2"},
    "guard": {"decision": "hold", "span_id": None},
}


def unique_object(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    try:
        actual = json.loads(args.evidence.read_bytes(), object_pairs_hook=unique_object)
        if type(actual) is not dict:
            raise ValueError("expected a JSON object")
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, indent=2))
        return 1
    incorrect = sorted(key for key in EXPECTED if actual.get(key) != EXPECTED[key])
    extras = sorted(actual.keys() - EXPECTED.keys())
    passed = not incorrect and not extras
    print(json.dumps({"passed": passed, "correct": len(EXPECTED) - len(incorrect),
                      "checks": len(EXPECTED), "incorrect": incorrect, "unexpected": extras}, indent=2))
    return int(not passed)


if __name__ == "__main__":
    raise SystemExit(main())
