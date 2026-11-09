#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check the source-owned Boolean comparison fixture artifacts."""

from argparse import ArgumentParser
import json
from pathlib import Path

from grade_ontology_borrowed_scope import unique_object


EQUIVALENCE = "EquivalentClasses(:Flagged ObjectIntersectionOf(:Candidate :Eligible))"
FLAGGED_CANDIDATE = "SubClassOf(:Flagged :Candidate)"
ELIGIBLE_AUDITED = "SubClassOf(:Eligible :Audited)"
AUDITED_ITEM = "ClassAssertion(:Audited :item)"
RAW = {
    "left": ([FLAGGED_CANDIDATE, "SubClassOf(:Flagged :Eligible)",
              "SubClassOf(ObjectIntersectionOf(:Candidate :Eligible) :Flagged)"], [ELIGIBLE_AUDITED, AUDITED_ITEM]),
    "right": ([EQUIVALENCE, FLAGGED_CANDIDATE], [ELIGIBLE_AUDITED, AUDITED_ITEM]),
    "shifted": ([EQUIVALENCE, FLAGGED_CANDIDATE, ELIGIBLE_AUDITED], [AUDITED_ITEM]),
}


def ledger(axioms):
    return {"premises": [{"id": pid, "gap": None, "axioms": bundle}
                        for pid, bundle in zip(("p01", "p02"), axioms, strict=True)]}


def grade(workspace):
    originals = {name: json.loads((workspace / f"{name}-source.json").read_bytes(),
                                  object_pairs_hook=unique_object) for name in RAW}
    raw_views = {name: (workspace / f"{name}-view.json").read_bytes() for name in RAW}
    views = {name: json.loads(raw, object_pairs_hook=unique_object) for name, raw in raw_views.items()}
    keys_preserved = all(
        set(view) == {"premises"} and len(view["premises"]) == 2
        and all(set(row) == {"id", "axioms", "gap"} and row["id"] == pid and row["gap"] is None
                for row, pid in zip(view["premises"], ("p01", "p02"), strict=True))
        for view in views.values()
    )
    checks = {
        "source_ledgers": all(originals[name] == ledger(raw) for name, raw in RAW.items()),
        "source_rows": keys_preserved,
        "same_premise_equivalent_bytes": raw_views["left"] == raw_views["right"],
        "different_source_ownership": raw_views["right"] != raw_views["shifted"],
        "unchanged_instance_assertion": all(view["premises"][1]["axioms"].count(AUDITED_ITEM) == 1
                                           and AUDITED_ITEM not in view["premises"][0]["axioms"]
                                           for view in views.values()),
        "actual_boolean_proposals": all(view["premises"][0]["axioms"][0].startswith("SubClassOf(owl:Thing ")
                                        for view in views.values()),
    }
    return {"passed": all(checks.values()), "checks": checks}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    try:
        result = grade(parser.parse_args().workspace)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        result = {"passed": False, "error": str(exc)}
    print(json.dumps(result, indent=2))
    raise SystemExit(not result["passed"])
