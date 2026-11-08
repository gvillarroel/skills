#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyshacl==0.40.0", "rdflib==7.6.0"]
# ///
"""Grade isolated authoring and fixed-ontology forward tests."""

from argparse import ArgumentParser
import csv
import json
from pathlib import Path
import re
import sys

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, OWL, RDF, RDFS, SH, XSD

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/extract-with-ontology/scripts"))
import check_extraction as checker

MODEL = Namespace("urn:manifest-model:")
RECORD = Namespace("urn:manifest-record:")
INTAKE = Namespace("urn:intake:")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def findings(report):
    return {
        (report.value(result, SH.focusNode), report.value(result, SH.sourceConstraintComponent),
         report.value(result, SH.sourceShape))
        for result in report.objects(None, SH.result)
    }


def read_graph(path):
    return Graph().parse(path, format="turtle")


def register_evidence(assertion, source_path, rows):
    if source_path != "manifest-register.csv":
        return False
    key = assertion["subject"].removeprefix(str(RECORD))
    if key not in rows:
        return False
    number, raw, cells = rows[key]
    if raw in assertion["quote"].splitlines():
        return True
    column = "type" if assertion["predicate"] == str(RDF.type) else assertion["predicate"].removeprefix(str(MODEL))
    position = rf"\brow\s+{number}\b"
    field = rf"(?:\b{re.escape(column)}\s+column\b|\bcolumn\s+{re.escape(column)}\b)"
    locator = assertion["locator"]
    return (assertion["quote"] == cells.get(column) and bool(re.search(position, locator, re.IGNORECASE))
            and bool(re.search(field, locator, re.IGNORECASE)))


def grade_guided(workspace):
    prompt = (ROOT / "evaluations/pi-prompts/ontology-guided-alternatives.md").read_text(encoding="utf-8")
    for name in ("manifest-model.ttl", "manifest-shapes.ttl", "manifest-register.csv"):
        block = re.search(rf"`{re.escape(name)}`\n\n```\w+\n(.*?)\n```", prompt, re.DOTALL)
        require((workspace / name).read_text(encoding="utf-8").rstrip("\n") == block[1],
                f"supplied input changed: {name}")

    data, _ = checker.parse_graph(workspace / "data.ttl")
    expected = {(RECORD[f"M{i}"], RDF.type, MODEL.Manifest) for i in range(1, 6)}
    expected.add((RECORD.S1, RDF.type, MODEL.Supplement))
    expected.update(
        (RECORD[key], MODEL[prop], Literal(value))
        for key, prop, value in (
            ("M1", "truckID", "TR-1"), ("M2", "flightID", "FL-2"),
            ("M3", "truckID", "TR-3"), ("M3", "flightID", "FL-3"),
            ("S1", "truckID", "TR-9"), ("S1", "flightID", "FL-9"),
        )
    )
    normalized = {(subject, prop, checker.canonical_object(value)) for subject, prop, value in data}
    require(normalized == expected, "asserted facts differ from the reference graph")
    ontology, checksum = checker.parse_graph(workspace / "manifest-model.ttl")
    ledger = json.loads((workspace / "evidence.json").read_text(encoding="utf-8"))
    evidence = checker.check(ontology, checksum, data, ledger, workspace)
    require(evidence["status"] == "passed", f"evidence check failed: {evidence['issues']}")
    submitted_check = json.loads((workspace / "checks.json").read_text(encoding="utf-8"))
    require(submitted_check == evidence, "submitted evidence check differs from its independent replay")
    register = (workspace / "manifest-register.csv").read_text(encoding="utf-8").splitlines()
    rows = {cells["key"]: (number, raw, cells)
            for number, (raw, cells) in enumerate(zip(register[1:], csv.DictReader(register), strict=True), 2)}
    paths = {entry["id"]: entry["path"] for entry in ledger["sources"]}
    covered = {
        (checker.iri(row["subject"]), checker.iri(row["predicate"]), checker.object_term(row["object"]))
        for row in ledger["assertions"]
        if register_evidence(row, paths[row["source_id"]], rows)
    }
    require(covered == expected, "every accepted fact must cite its own row or exact located cell")

    shapes = read_graph(workspace / "manifest-shapes.ttl")
    conforms, replay, _ = validate(data, shacl_graph=shapes, inference="none")
    submitted = read_graph(workspace / "validation.ttl")
    expected_findings = {(RECORD[key], SH.XoneConstraintComponent, MODEL.TransportChoice)
                         for key in ("M3", "M4", "M5")}
    require(not conforms and Literal(False) in submitted.objects(None, SH.conforms),
            "both reports must record nonconformance")
    require(findings(replay) == findings(submitted) == expected_findings,
            "expected exactly three xone violations on the correct records")
    review = (workspace / "review.md").read_text(encoding="utf-8")
    require(all(token in review for token in ("M3", "M4", "M5", "TR-5", "TR-6")),
            "review must include the three failed records and both unresolved candidate IDs")
    return {"supported_facts": len(covered), "exact_findings": len(expected_findings)}


def grade_authoring(workspace):
    ontology = read_graph(workspace / "ontology.ttl")
    classes = [INTAKE.IdentityDocument, INTAKE.DigitalCredential, INTAKE.PaperCredential, INTAKE.Submission]
    require(all((term, RDF.type, OWL.Class) in ontology for term in classes), "required class missing")
    props = [INTAKE.digitalCode, INTAKE.signature, INTAKE.paperCode, INTAKE.seal]
    for prop in props:
        require((prop, RDF.type, OWL.DatatypeProperty) in ontology, f"missing datatype property {prop}")
    rhs = list(ontology.objects(INTAKE.IdentityDocument, RDFS.subClassOf))
    require(len(rhs) == 1, "expected one forward IdentityDocument axiom")
    union = ontology.value(rhs[0], OWL.unionOf)
    require(union is not None and set(ontology.items(union)) == set(classes[1:3]), "expected the two-class union")
    require(set(ontology.subject_objects(RDFS.subClassOf)) == {(INTAKE.IdentityDocument, rhs[0])},
            "unexpected additional subclass axiom")
    for predicate in (OWL.disjointWith, OWL.disjointUnionOf, OWL.equivalentClass, OWL.complementOf):
        require(not any(ontology.triples((None, predicate, None))), f"unexpected class axiom {predicate}")
    require(not any(ontology.subjects(RDF.type, OWL.AllDisjointClasses)), "unexpected disjointness")

    shapes = read_graph(workspace / "shapes.ttl")
    digital, paper = props[:2], props[2:]
    cases = {
        "Digital": (digital, True, True),
        "Paper": (paper, True, True),
        "Both": (props, True, False),
        "Neither": ([], True, False),
        "MixedIncomplete": ([digital[0], paper[1]], True, False),
        "DigitalAndPartialPaper": (digital + paper[:1], True, True),
        "NumericDigitalCode": (digital, True, False),
        "NumericPaperSeal": (paper, True, False),
        "Outside": (props, False, True),
    }
    numeric_fields = {"NumericDigitalCode": digital[0], "NumericPaperSeal": paper[1]}
    for case, (fields, target, expected) in cases.items():
        data = Graph()
        node = INTAKE[case]
        data.add((node, RDF.type, INTAKE.Submission if target else INTAKE.IdentityDocument))
        for prop in fields:
            value = Literal(123) if numeric_fields.get(case) == prop else Literal("valid text", datatype=XSD.string)
            data.add((node, prop, value))
        conforms, report, _ = validate(data, shacl_graph=shapes, inference="none")
        require(conforms == expected, f"{case}: expected conformance {expected}")
        if not expected:
            require({row[0] for row in findings(report)} == {node}, f"{case}: incorrect focus node")
    return {"inclusive_forward_class_axioms": 1, "record_validation_cases": len(cases)}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("guided", "authoring"))
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    try:
        grade = {"guided": grade_guided, "authoring": grade_authoring}[args.case]
        print(json.dumps({"passed": True, **grade(args.workspace.resolve())}, indent=2))
    except ValueError as error:
        print(json.dumps({"passed": False, "error": str(error)}, indent=2))
        raise SystemExit(1) from error
