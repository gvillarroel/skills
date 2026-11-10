#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyshacl==0.40.0"]
# ///
"""Exercise the GitHub inventory shapes without fetching sources."""

from pathlib import Path
import unittest

from pyshacl import validate
from rdflib import Graph

ROOT = Path(__file__).resolve().parent
PREFIX = "@prefix pf: <https://example.org/product-features#> .\n"
PRODUCT = "<urn:example:product:github>"
OWNER = f"{PRODUCT} a pf:Product ; pf:hasFeature <urn:f> .\n"
TYPED = OWNER + "<urn:f> a pf:AIFeature ."


class InventoryShapesTests(unittest.TestCase):
    def test_shape_witnesses(self):
        cases = (
            ("ai", TYPED, True),
            ("non-ai", OWNER + "<urn:f> a pf:NonAIFeature .", True),
            ("unclassified", OWNER + "<urn:f> a pf:UnclassifiedFeature .", True),
            ("empty", "", False),
            ("untagged", OWNER, False),
            ("two-classes", TYPED + "<urn:f> a pf:NonAIFeature .", False),
            ("unowned", TYPED + "<urn:g> a pf:UnclassifiedFeature .", False),
            ("wrong-owner", f"{PRODUCT} pf:hasFeature <urn:f> . <urn:f> a pf:AIFeature .", False),
            ("two-owners", TYPED + "<urn:q> a pf:Product ; pf:hasFeature <urn:f> .", False),
            ("dangling-relation", TYPED + "<urn:f> pf:relatedFeature <urn:q> .", False),
            ("self-relation", TYPED + "<urn:f> pf:relatedFeature <urn:f> .", False),
            ("linked-relation", TYPED + f"{PRODUCT} pf:hasFeature <urn:q> . "
             "<urn:f> pf:relatedFeature <urn:q> . <urn:q> a pf:NonAIFeature .", True),
        )
        for name, triples, expected in cases:
            with self.subTest(name=name):
                graph = Graph().parse(data=PREFIX + triples, format="turtle")
                actual, _, report = validate(
                    graph, shacl_graph=str(ROOT / "shapes.ttl"),
                    ont_graph=str(ROOT / "ontology.ttl"), inference="none",
                )
                self.assertEqual(actual, expected, report)


if __name__ == "__main__":
    unittest.main()
