#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib[html]==7.6.0", "pyshacl==0.40.0", "owlrl==7.6.2"]
# ///
"""Verify RDF literal term identity through the supported SHACL CLI."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from xml.sax.saxutils import escape

import rdflib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/extract-ontologies/scripts"))
import validate_semantic_artifacts as validator

NS = "urn:literal-audit:"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XSD = "http://www.w3.org/2001/XMLSchema#"
SH = "http://www.w3.org/ns/shacl#"
VALUES = {
    "numeric": [("1", "integer"), ("01", "integer")],
    "booleans": [("true", "boolean"), ("1", "boolean")],
    "strings": [("alpha", None), ("alpha", "string")],
    "language": [("hello", "@en-US"), ("hello", "@EN-us")],
    "requiredLexical": [("1", "integer")],
    "plainOnly": [("alpha", None)],
}
COUNTED = {"numeric", "booleans", "strings", "language"}
SHAPES = """
@prefix : <urn:literal-audit:> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:Count a sh:NodeShape ; sh:targetClass :Record ;
    sh:property [ sh:path :value ; sh:maxCount 1 ] .
:ExactLexical a sh:NodeShape ; sh:targetNode :requiredLexical ;
    sh:property [ sh:path :value ; sh:hasValue "01"^^xsd:integer ] .
:SameString a sh:NodeShape ; sh:targetNode :plainOnly ;
    sh:property [ sh:path :value ; sh:hasValue "alpha"^^xsd:string ] .
"""


def text_graph():
    rows = []
    for name, values in VALUES.items():
        if name in COUNTED:
            rows.append(f"<{NS}{name}> <{RDF}type> <{NS}Record> .")
        for lexical, datatype in values:
            suffix = "" if datatype is None else datatype if datatype.startswith("@") else f"^^<{XSD}{datatype}>"
            rows.append(f"<{NS}{name}> <{NS}value> {json.dumps(lexical)}{suffix} .")
    return "\n".join(rows) + "\n"


def jsonld_graph():
    nodes = []
    for name, values in VALUES.items():
        record = {"@id": NS + name, NS + "value": []}
        if name in COUNTED:
            record["@type"] = NS + "Record"
        for lexical, datatype in values:
            term = {"@value": lexical}
            if datatype and datatype.startswith("@"):
                term["@language"] = datatype[1:]
            elif datatype:
                term["@type"] = XSD + datatype
            record[NS + "value"].append(term)
        nodes.append(record)
    return json.dumps(nodes) + "\n"


def xml_graph():
    parts = [f'<rdf:RDF xmlns:rdf="{RDF}" xmlns:a="{NS}">']
    for name, values in VALUES.items():
        parts.append(f'<rdf:Description rdf:about="{NS}{name}">')
        if name in COUNTED:
            parts.append(f'<rdf:type rdf:resource="{NS}Record"/>')
        for lexical, datatype in values:
            attributes = ""
            if datatype and datatype.startswith("@"):
                attributes = f' xml:lang="{datatype[1:]}"'
            elif datatype:
                attributes = f' rdf:datatype="{XSD}{datatype}"'
            parts.append(f"<a:value{attributes}>{escape(lexical)}</a:value>")
        parts.append("</rdf:Description>")
    return "\n".join([*parts, "</rdf:RDF>", ""])


class LiteralValidation(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def write(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def invoke(self, *arguments):
        with redirect_stdout(io.StringIO()) as stdout:
            code = validator.main([*map(str, arguments), "--output-format", "json"])
        return code, json.loads(stdout.getvalue())

    def test_counts_and_has_value_use_rdf_term_identity(self):
        shapes = self.write("shapes.ttl", SHAPES)
        formats = {"ttl": text_graph(), "nt": text_graph(), "n3": text_graph(),
                   "rdf": xml_graph(), "jsonld": jsonld_graph()}
        expected = {
            (NS + "numeric", SH + "MaxCountConstraintComponent"),
            (NS + "booleans", SH + "MaxCountConstraintComponent"),
            (NS + "requiredLexical", SH + "HasValueConstraintComponent"),
        }
        for extension, text in formats.items():
            with self.subTest(format=extension):
                data = self.write(f"data.{extension}", text)
                before = rdflib.NORMALIZE_LITERALS
                code, result = self.invoke("--data", data, "--shapes", shapes, "--inference", "none")
                actual = {(row["focus_node"]["value"], row["source_constraint_component"]["value"])
                          for row in result["results"]}
                self.assertEqual(code, 1)
                self.assertEqual(actual, expected)
                self.assertEqual(result["summary"]["data_triples"], 12)
                self.assertIs(rdflib.NORMALIZE_LITERALS, before)

    def test_canonical_strings_deduplicate_across_input_files(self):
        first = self.write("plain.nt", f'<{NS}s> <{NS}value> "alpha" .\n')
        second = self.write("typed.ttl", f'<{NS}s> <{NS}value> "alpha"^^<{XSD}string> .\n')
        code, result = self.invoke("--data", first, "--data", second)
        self.assertEqual(code, 0)
        self.assertEqual(result["summary"]["data_triples"], 1)
        self.assertEqual([item["triples"] for item in result["files"]], [1, 1])

    def test_parser_error_restores_rdflib_configuration(self):
        data = self.write("bad.ttl", '<urn:s> <urn:p> "unclosed')
        before = rdflib.NORMALIZE_LITERALS
        code, _ = self.invoke("--data", data)
        self.assertEqual(code, 2)
        self.assertIs(rdflib.NORMALIZE_LITERALS, before)


if __name__ == "__main__":
    unittest.main()
