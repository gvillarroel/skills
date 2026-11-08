#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib==7.6.0"]
# ///
"""Regression checks for the standalone ontology-guided extraction checker."""

import contextlib
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[2] / "skills/extract-with-ontology/scripts"
sys.path.insert(0, str(SKILL))
import check_extraction as checker

PREFIXES = """
@prefix : <urn:ex:> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
"""
ONTOLOGY = PREFIXES + """
:schema a owl:Ontology ; owl:imports <urn:absent:optional> .
:Permit a owl:Class ; skos:definition "Approved authorization"@en .
:Record a owl:Class .
:Office a owl:Class .
:issuedBy a owl:ObjectProperty ; rdfs:domain :Permit, :Record ; rdfs:range :Office .
:code a owl:DatatypeProperty .
"""
DATA = [
    ":permit a :Permit .",
    ":permit :issuedBy :office .",
    ':permit :code "0003" .',
]


class ExtractionCheck(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.schema = self.write("schema.ttl", ONTOLOGY)
        self.data = self.write("data.ttl", PREFIXES + "\n".join(DATA))
        self.raw = "Office issued permit with code 0003."
        self.source = self.write("register.txt", self.raw)
        evidence = {"source_id": "register", "quote": self.raw, "locator": "line 1"}
        self.ledger = {
            "ontology_sha256": checker.digest(self.schema.read_bytes()),
            "sources": [{"id": "register", "path": "register.txt", "sha256": checker.digest(self.source.read_bytes())}],
            "assertions": [
                {"subject": "urn:ex:permit", "predicate": str(checker.RDF.type),
                 "object": {"iri": "urn:ex:Permit"}, **evidence},
                {"subject": "urn:ex:permit", "predicate": "urn:ex:issuedBy",
                 "object": {"iri": "urn:ex:office"}, **evidence},
                {"subject": "urn:ex:permit", "predicate": "urn:ex:code",
                 "object": {"value": "0003"}, **evidence},
            ],
        }

    def write(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def check(self):
        ontology, checksum = checker.parse_graph(self.schema)
        data, _ = checker.parse_graph(self.data)
        return checker.check(ontology, checksum, data, self.ledger, self.root)

    def test_inventory_preserves_scope_and_multiple_endpoints(self):
        ontology, checksum = checker.parse_graph(self.schema)
        result = checker.inventory(ontology, checksum)
        terms = {row["iri"]: row for row in result["terms"]}
        self.assertEqual(result["unresolved_imports"], ["urn:absent:optional"])
        self.assertEqual(terms["urn:ex:issuedBy"]["domain"], ["urn:ex:Permit", "urn:ex:Record"])
        self.assertEqual(terms["urn:ex:Permit"]["annotations"][0]["language"], "en")

    def test_inventory_preserves_distinct_skos_concepts_and_definition_annotations(self):
        self.write("schema.ttl", ONTOLOGY + """
:Release a skos:Concept ;
    skos:prefLabel "Release"@en, "Publicación"@es ;
    skos:altLabel "Publication"@en ;
    skos:definition "Authorized publication of a record."@en .
:ReleaseOfLien a skos:Concept ; skos:prefLabel "Release"@en .
""")
        ontology, checksum = checker.parse_graph(self.schema)
        terms = {row["iri"]: row for row in checker.inventory(ontology, checksum)["terms"]}
        release = terms["urn:ex:Release"]
        self.assertEqual(release["kinds"], ["concept"])
        self.assertEqual(
            [(row["kind"], row["language"], row["value"]) for row in release["annotations"]],
            [
                ("alias", "en", "Publication"),
                ("definition", "en", "Authorized publication of a record."),
                ("preferred_label", "en", "Release"),
                ("preferred_label", "es", "Publicación"),
            ],
        )
        self.assertEqual(release["annotations"][1]["predicate"], str(checker.SKOS.definition))
        homonym = terms["urn:ex:ReleaseOfLien"]
        self.assertEqual(homonym["kinds"], ["concept"])
        self.assertEqual([row["kind"] for row in homonym["annotations"]], ["preferred_label"])

    def test_reordered_assertions_keep_named_graph_digest(self):
        first = self.check()
        self.write("data.ttl", PREFIXES + "\n".join(reversed(DATA)))
        second = self.check()
        self.assertEqual(first["status"], "passed")
        self.assertEqual(first["evidence_covered_triples"], 3)
        self.assertEqual(first["asserted_graph_sha256"], second["asserted_graph_sha256"])

    def test_language_tag_case_does_not_change_graph_digest(self):
        rows = (':permit :code "0003"@en-US .', ':permit :code "0003"@EN-us .')
        self.ledger["assertions"][2]["object"]["language"] = "EN-US"
        reports = []
        for order in (rows, rows[::-1]):
            self.write("data.ttl", PREFIXES + "\n".join([*DATA[:2], *order]))
            report = self.check()
            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["asserted_triples"], 3)
            reports.append(report["asserted_graph_sha256"])
        self.assertEqual(*reports)

    def test_implicit_and_explicit_string_datatype_are_equivalent(self):
        datatype = "http://www.w3.org/2001/XMLSchema#string"
        typed = f':permit :code "0003"^^<{datatype}> .'
        initial = self.check()
        for statements, evidence_type in (
            ([typed], {}),
            ([DATA[2]], {"datatype": datatype}),
            ([typed, DATA[2]], {"datatype": datatype}),
        ):
            self.write("data.ttl", PREFIXES + "\n".join([*DATA[:2], *statements]))
            self.ledger["assertions"][2]["object"] = {"value": "0003", **evidence_type}
            self.assertEqual(self.check(), initial)

    def test_rejects_fake_quote_and_unasserted_evidence(self):
        self.ledger["assertions"][0]["quote"] = "unsupported text"
        self.ledger["assertions"][1]["object"] = {"iri": "urn:ex:different"}
        self.ledger["assertions"][2].update(start=2, end=len(self.raw))
        result = self.check()
        self.assertEqual(result["status"], "violations")
        self.assertEqual(result["evidence_covered_triples"], 0)
        self.assertIn("evidence cites an unasserted triple", {row["issue"] for row in result["issues"]})

    def test_rejects_source_drift_and_ontology_drift(self):
        self.write("register.txt", self.raw + " Revised.")
        self.ledger["ontology_sha256"] = "0" * 64
        issues = {row["issue"] for row in self.check()["issues"]}
        self.assertIn("source SHA-256 mismatch", issues)
        self.assertIn("ontology SHA-256 mismatch", issues)

    def test_rejects_source_path_escape(self):
        self.ledger["sources"][0]["path"] = "../register.txt"
        issues = {row["issue"] for row in self.check()["issues"]}
        self.assertIn("source path must stay under the source root", issues)

    def test_preserves_typed_literal_lexical_form(self):
        integer = "http://www.w3.org/2001/XMLSchema#integer"
        self.write("data.ttl", PREFIXES + "\n".join(DATA[:2]) + f'\n:permit :code "0003"^^<{integer}> .')
        self.ledger["assertions"][2]["object"] = {"value": "0003", "datatype": integer}
        with patch.object(checker.rdflib, "NORMALIZE_LITERALS", False):
            self.assertEqual(self.check()["status"], "passed")
            self.ledger["assertions"][2]["object"]["value"] = "3"
            self.assertEqual(self.check()["status"], "violations")

    def test_unicode_line_separator_does_not_split_rdf_records(self):
        values = ("start\u2028first\u2028second\u2028end", "start\u2028second\u2028first\u2028end")
        results = []
        for value in values:
            self.write("data.ttl", PREFIXES + "\n".join(DATA[:2]) + f'\n:permit :code "{value}" .')
            self.ledger["assertions"][2]["object"]["value"] = value
            report = self.check()
            self.assertEqual(report["status"], "passed")
            results.append(report["asserted_graph_sha256"])
        self.assertNotEqual(*results)

    def test_rejects_wrong_ledger_collection_types(self):
        self.ledger["assertions"] = ""
        with self.assertRaisesRegex(ValueError, "assertions array"):
            self.check()
        self.ledger["assertions"] = []
        self.ledger["sources"] = {}
        with self.assertRaisesRegex(ValueError, "sources array"):
            self.check()

    def test_rejects_undeclared_terms_and_wrong_property_kind(self):
        self.write("data.ttl", PREFIXES + ':permit :issuedBy "office" ; :unknown :other .\n:permit a :Unknown .')
        issues = {row["issue"] for row in self.check()["issues"]}
        self.assertIn("property outside declared vocabulary", issues)
        self.assertIn("type outside declared vocabulary", issues)
        self.assertIn("object term does not match declared property kind", issues)

    def test_rdf_type_requires_an_iri_even_with_a_matching_literal(self):
        self.write("data.ttl", PREFIXES + ':permit a "urn:ex:Permit" .')
        self.ledger["assertions"] = [self.ledger["assertions"][0]]
        self.ledger["assertions"][0]["object"] = {"value": "urn:ex:Permit"}
        report = self.check()
        self.assertEqual(report["status"], "violations")
        self.assertIn("type outside declared vocabulary", {row["issue"] for row in report["issues"]})

    def test_cli_reports_invalid_syntax_without_mutating_inputs(self):
        self.write("data.ttl", "@prefix ???")
        ledger = self.write("evidence.json", json.dumps(self.ledger))
        output = self.root / "report.json"
        cmd = [
            "check_extraction.py", "check", "--ontology", str(self.schema), "--data", str(self.data),
            "--evidence", str(ledger), "--source-root", str(self.root), "--output", str(output),
        ]
        with patch.object(sys, "argv", cmd), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(checker.main(), 2)
        self.assertFalse(output.exists())
        self.assertEqual(checker.digest(self.schema.read_bytes()), self.ledger["ontology_sha256"])


if __name__ == "__main__":
    unittest.main()
