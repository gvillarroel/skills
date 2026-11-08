#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib==7.6.0", "pyshacl==0.40.0"]
# ///
"""Check emitted SHACL against an independent value-count matrix."""

from argparse import ArgumentParser
import json
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace, RDF, RDFS, SH

EX = Namespace("urn:count-scope:")
POLICIES = (EX.Minimum, EX.OneMatch, EX.OneTotal)
CASES = {
    "no-member": ((), (False, False, False)),
    "one-a": ((EX.left,), (True, True, True)),
    "one-b": ((EX.right,), (True, True, True)),
    "one-overlap": ((EX.overlap,), (True, True, True)),
    "two-qualified": ((EX.left, EX.right), (True, False, False)),
    "one-qualified-one-other": ((EX.left, EX.other), (True, True, False)),
    "one-other": ((EX.other,), (False, False, False)),
}
TYPES = (
    (EX.left, RDF.type, EX.EligibleA),
    (EX.right, RDF.type, EX.EligibleB),
    (EX.overlap, RDF.type, EX.EligibleA),
    (EX.overlap, RDF.type, EX.EligibleB),
    (EX.other, RDF.type, EX.Other),
)


def check(shapes_path):
    shapes = Graph().parse(shapes_path, format="turtle")
    failures, total = [], 0
    for index, policy in enumerate(POLICIES):
        for case, (members, expected) in CASES.items():
            data = Graph()
            for triple in (*TYPES, (EX.record, RDF.type, policy)):
                data.add(triple)
            for member in members:
                data.add((EX.record, EX.member, member))
            conforms, report, _ = validate(data, shacl_graph=shapes, inference="none")
            expected_focus = set() if expected[index] else {EX.record}
            if conforms != expected[index] or set(report.objects(None, SH.focusNode)) != expected_focus:
                failures.append(f"{policy}/{case}")
            total += 1
    data = Graph()
    for triple in ((EX.Imported, RDFS.subClassOf, EX.OneTotal), (EX.child, RDF.type, EX.Imported),
                   (EX.outside, RDF.type, EX.Other)):
        data.add(triple)
    conforms, report, _ = validate(data, shacl_graph=shapes, inference="none")
    if conforms or set(report.objects(None, SH.focusNode)) != {EX.child}:
        failures.append("subclass and outside target")
    return {"passed": not failures, "checks": total + 1, "failures": failures}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("shapes", type=Path)
    result = check(parser.parse_args().shapes)
    print(json.dumps(result, indent=2))
    raise SystemExit(not result["passed"])
