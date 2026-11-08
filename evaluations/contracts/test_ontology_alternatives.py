#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib[html]==7.6.0", "pyshacl==0.40.0", "owlrl==7.6.2"]
# ///
"""Exercise OWL alternatives, SHACL choice scopes, and evidence preservation."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from owlrl import DeductiveClosure, OWLRL_Semantics
from pyshacl import validate
from rdflib import Graph, Namespace, RDF, SH


ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "skills" / skill / "scripts") for skill in ("extract-ontologies", "extract-with-ontology")]
import check_extraction as checker
import validate_semantic_artifacts as authoring_validator


EX = Namespace("urn:ontology-alternatives:")
PREFIXES = """
@prefix : <urn:ontology-alternatives:> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
"""
CLASSES = """
:Record a owl:Class .
:Alpha a owl:Class .
:Beta a owl:Class .
:AllowedTarget a owl:Class ; owl:equivalentClass [ a owl:Class ; owl:unionOf (:Alpha :Beta) ] .
"""
INSTANCE_TYPES = """
:left a :Alpha .
:secondLeft a :Alpha .
:right a :Beta .
:overlap a :Alpha, :Beta .
:other a :Unrelated .
"""
VALUE_BRANCHES = "([ sh:class :Alpha ] [ sh:class :Beta ])"
RECORD_BRANCHES = """(
    [ sh:property [ sh:path :email ; sh:minCount 1 ] ]
    [ sh:property [ sh:path :sms ; sh:minCount 1 ] ]
)"""

# Expected columns are independent assertions about the fixture inputs.
# Pointwise columns: optional or, optional xone, required or, exactly one value in the union.
VALUE_CASES = {
    "no-value": ("", (True, True, False, False)),
    "alpha": ("; :target :left", (True, True, True, True)),
    "beta": ("; :target :right", (True, True, True, True)),
    "one-overlap": ("; :target :overlap", (True, False, True, True)),
    "two-distinct-branches": ("; :target :left, :right", (True, True, True, False)),
    "two-values-same-branch": ("; :target :left, :secondLeft", (True, True, True, False)),
    "known-neither": ("; :target :other", (False, False, False, False)),
    "untyped-target": ("; :target :untyped", (False, False, False, False)),
    "one-valid-one-untyped": ("; :target :left, :untyped", (False, False, False, False)),
}
# Record columns: at least one, exactly one, or at most one field has a value.
RECORD_CASES = {
    "neither": ("", (False, False, True)),
    "email": ('; :email "address"', (True, True, True)),
    "sms": ('; :sms "number"', (True, True, True)),
    "both": ('; :email "address" ; :sms "number"', (True, False, False)),
    "both-with-same-rdf-value": ('; :email "shared" ; :sms "shared"', (True, False, False)),
    "one-branch-with-two-values": ('; :email "first", "second"', (True, True, True)),
}


def graph(body):
    return Graph().parse(data=PREFIXES + body, format="turtle")


def pointwise(operator, counts="", target="sh:targetClass :Record"):
    return f"""\n:RecordShape a sh:NodeShape ; {target} ;
        sh:property [ sh:path :target ; {counts} sh:{operator} {VALUE_BRANCHES} ] .\n"""


def record_choice(operator):
    return f"\n:RecordShape a sh:NodeShape ; sh:targetClass :Record ; sh:{operator} {RECORD_BRANCHES} .\n"


class OntologyAlternatives(unittest.TestCase):
    def shacl(self, data, shapes):
        data_before = set(data)
        # pySHACL's meta-validation adds RDFS triples to its in-memory shapes graph.
        conforms, results, _ = validate(data, shacl_graph=Graph() + shapes, inference="none", meta_shacl=True)
        self.assertIs(type(conforms), bool)
        self.assertIsInstance(results, Graph)
        self.assertEqual(set(data), data_before)
        return conforms, results

    def test_pointwise_choice_and_value_counts(self):
        shapes = [graph(body) for body in (pointwise("or"), pointwise("xone"),
                  pointwise("or", "sh:minCount 1 ;"), pointwise("or", "sh:minCount 1 ; sh:maxCount 1 ;"))]
        for case, (fields, expected) in VALUE_CASES.items():
            data = graph(f":record a :Record {fields} .\n" + INSTANCE_TYPES)
            for column, (shape, conforms) in enumerate(zip(shapes, expected, strict=True)):
                with self.subTest(case=case, shape=column):
                    self.assertIs(self.shacl(data, shape)[0], conforms)

    def test_record_choice_counts_matching_branches(self):
        shapes = {
            "or": graph(record_choice("or")),
            "xone": graph(record_choice("xone")),
            "at-most-one": graph(f":RecordShape a sh:NodeShape ; sh:targetClass :Record ; "
                                 f"sh:not [ sh:and {RECORD_BRANCHES} ] ."),
        }
        for case, (fields, expected) in RECORD_CASES.items():
            data = graph(f":record a :Record {fields} .\n")
            for (operator, shape), conforms in zip(shapes.items(), expected, strict=True):
                with self.subTest(case=case, operator=operator):
                    self.assertIs(self.shacl(data, shape)[0], conforms)

    def test_alternative_path_value_count_can_hide_two_selected_fields(self):
        data = graph(':record a :Record ; :email "shared" ; :sms "shared" .')
        value_count = graph("""
:RecordShape a sh:NodeShape ; sh:targetClass :Record ;
    sh:property [ sh:path [ sh:alternativePath (:email :sms) ] ; sh:minCount 1 ; sh:maxCount 1 ] .
""")
        self.assertTrue(self.shacl(data, value_count)[0])
        self.assertFalse(self.shacl(data, graph(record_choice("xone")))[0])

    def test_missing_record_is_invisible_to_subjects_of_its_missing_property(self):
        data = graph(":missing a :Record .\n:present a :Record ; :target :left .\n" + INSTANCE_TYPES)
        existing_edges = graph(pointwise("or", "sh:minCount 1 ;", "sh:targetSubjectsOf :target"))
        all_records = graph(pointwise("or", "sh:minCount 1 ;"))
        self.assertTrue(self.shacl(data, existing_edges)[0])
        conforms, report = self.shacl(data, all_records)
        self.assertFalse(conforms)
        results = list(report.subjects(RDF.type, SH.ValidationResult))
        self.assertEqual(len(results), 1)
        self.assertEqual(report.value(results[0], SH.focusNode), EX.missing)
        self.assertEqual(report.value(results[0], SH.sourceConstraintComponent), SH.MinCountConstraintComponent)

    def test_owlrl_union_accepts_overlap_without_selecting_a_disjunct(self):
        data = graph(CLASSES + INSTANCE_TYPES + "\n:opaque a :AllowedTarget .\n")
        DeductiveClosure(OWLRL_Semantics).expand(data)
        for value in (EX.left, EX.right, EX.overlap):
            with self.subTest(value=value):
                self.assertIn((value, RDF.type, EX.AllowedTarget), data)
        self.assertNotIn((EX.opaque, RDF.type, EX.Alpha), data)
        self.assertNotIn((EX.opaque, RDF.type, EX.Beta), data)

    def test_owlrl_repeated_ranges_produce_both_types(self):
        common = CLASSES + "\n:record :target :untyped .\n"
        union = graph(common + ":target a owl:ObjectProperty ; rdfs:range :AllowedTarget .\n")
        both = graph(common + ":target a owl:ObjectProperty ; rdfs:range :Alpha, :Beta .\n")
        for data in (union, both):
            DeductiveClosure(OWLRL_Semantics).expand(data)
            self.assertIn((EX.untyped, RDF.type, EX.AllowedTarget), data)
        for branch in (EX.Alpha, EX.Beta):
            self.assertNotIn((EX.untyped, RDF.type, branch), union)
            self.assertIn((EX.untyped, RDF.type, branch), both)

    def test_guided_evidence_and_authoring_validation_report_independently(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source, ontology_path, data_path, shapes, report_path = (
                root / name for name in ("register.txt", "ontology.ttl", "data.ttl", "shapes.ttl", "report.ttl")
            )
            quote = "Record links to the target classified as both Alpha and Beta."
            missing_quote = "The second record has no target entered."
            source.write_bytes((quote + "\n" + missing_quote + "\n").encode())
            ontology_path.write_bytes((PREFIXES + CLASSES + ":target a owl:ObjectProperty .\n").encode())
            data_path.write_bytes((PREFIXES + ":record a :Record ; :target :overlap .\n"
                                   ":overlap a :Alpha, :Beta .\n:missing a :Record .\n").encode())
            shapes.write_bytes((PREFIXES + pointwise("xone", "sh:minCount 1 ;")).encode())
            ontology, checksum = checker.parse_graph(ontology_path)
            data, data_checksum = checker.parse_graph(data_path)
            evidence = {
                "ontology_sha256": checksum,
                "sources": [{"id": "register", "path": source.name, "sha256": checker.digest(source.read_bytes())}],
                "assertions": [{"subject": str(subject), "predicate": str(predicate), "object": {"iri": str(object_)},
                                "source_id": "register", "locator": "line 2" if subject == EX.missing else "line 1",
                                "quote": missing_quote if subject == EX.missing else quote}
                               for subject, predicate, object_ in data],
            }
            extraction = checker.check(ontology, checksum, data, evidence, root)
            self.assertEqual(extraction["status"], "passed")
            self.assertEqual(extraction["evidence_covered_triples"], 5)
            shape_checksum = checker.digest(shapes.read_bytes())
            with redirect_stdout(io.StringIO()) as output:
                exit_code = authoring_validator.main([
                    "--data", str(data_path), "--ontology", str(ontology_path), "--shapes", str(shapes),
                    "--inference", "none", "--report", str(report_path), "--output-format", "json",
                ])
            self.assertEqual(exit_code, 1, output.getvalue())
            validation = json.loads(output.getvalue())
            self.assertEqual(validation["status"], "nonconformant")
            report = Graph().parse(report_path, format="turtle")
            results = list(report.subjects(RDF.type, SH.ValidationResult))
            self.assertEqual(len(results), 2)
            by_focus = {report.value(result, SH.focusNode): result for result in results}
            self.assertEqual(set(by_focus), {EX.record, EX.missing})
            self.assertEqual(report.value(by_focus[EX.record], SH.value), EX.overlap)
            self.assertEqual(report.value(by_focus[EX.record], SH.sourceConstraintComponent), SH.XoneConstraintComponent)
            self.assertEqual(report.value(by_focus[EX.missing], SH.sourceConstraintComponent), SH.MinCountConstraintComponent)
            self.assertEqual(checker.digest(data_path.read_bytes()), data_checksum)
            self.assertEqual(checker.digest(shapes.read_bytes()), shape_checksum)
            self.assertEqual(checker.check(ontology, checksum, data, evidence, root), extraction)


if __name__ == "__main__":
    unittest.main()
