#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema==4.25.1", "referencing==0.36.2"]
# ///
"""Exercise the local-reference graph certificate and its proof boundary."""

from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from jsonschema import Draft7Validator

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/curate-semantic-model/scripts"))
from compare_schema_graphs import compare, exact_float, read_json

DRAFT7 = "http://json-schema.org/draft-07/schema#"


def schema(**body):
    return {"$schema": DRAFT7, **body}


def workflow():
    use = {"type": "string"}
    choices = [{"type": "object", "properties": {"uses": use}, "required": ["uses"]},
               {"type": "object", "properties": {"run": use}, "required": ["run"]}]
    parent = {"type": "object", "additionalProperties": False, "properties": {"uses": use, "run": use}}
    old = schema(allOf=[{"oneOf": choices}, parent])
    new = schema(**parent, oneOf=[{"required": ["run"]}, {"required": ["uses"]}])
    return old, new


def guarded():
    node = {"type": "object", "properties": {"next": {"$ref": "#/definitions/node"},
                                           "value": {"type": "integer"}}}
    old = schema(**{"$ref": "#/definitions/node", "definitions": {"node": node}})
    new = schema(**{"$ref": "#/definitions/alias",
                    "definitions": {"node": {**node, "description": "annotation"},
                                    "alias": {"$ref": "#/definitions/node"}}})
    return old, new


class GraphTests(unittest.TestCase):
    def test_inlining_preserves_reference_site_draft7_sibling_semantics(self):
        old = schema(properties={"a/b": {"type": "number", "minimum": 3}})
        new = schema(properties={"a/b": {"$ref": "#/definitions/a~1b", "minimum": 99}},
                     definitions={"a/b": {"type": "number", "minimum": 3}})
        self.assertEqual(compare(old, new)["relation"], "equivalent")
        self.assertTrue(Draft7Validator(new).is_valid({"a/b": 3}))

    def test_factored_one_of_retains_truth_table_and_multiplicity(self):
        old, new = workflow()
        self.assertEqual(compare(old, new)["relation"], "equivalent")
        values = [None, 0, "", "command"]
        for flags in product((False, True), repeat=2):
            for pair in product(values, repeat=2):
                instance = {name: value for name, value, present in zip(("run", "uses"), pair, flags) if present}
                self.assertEqual(Draft7Validator(old).is_valid(instance), Draft7Validator(new).is_valid(instance))
        duplicate = deepcopy(new)
        duplicate["oneOf"].append({"required": ["uses"]})
        self.assertEqual(compare(old, duplicate)["relation"], "unknown")
        self.assertFalse(Draft7Validator(duplicate).is_valid({"uses": "action"}))

    def test_unsafe_closure_migration_stays_unresolved(self):
        old = schema(allOf=[{"properties": {"x": {}}, "additionalProperties": False},
                            {"properties": {"y": {}}}])
        new = schema(properties={"x": {}, "y": {}}, additionalProperties=False)
        self.assertEqual(compare(old, new)["relation"], "unknown")
        self.assertFalse(Draft7Validator(old).is_valid({"y": 1}))
        self.assertTrue(Draft7Validator(new).is_valid({"y": 1}))

    def test_guarded_recursion_preserves_target_and_body(self):
        old, new = guarded()
        self.assertEqual(compare(old, new)["relation"], "equivalent")
        nested = {"value": 1, "next": {"value": 2, "next": {"value": 3}}}
        self.assertTrue(Draft7Validator(old).is_valid(nested))
        self.assertTrue(Draft7Validator(new).is_valid(nested))
        modified = deepcopy(new)
        modified["definitions"]["node"]["properties"]["value"] = {"type": "string"}
        self.assertEqual(compare(old, modified)["relation"], "unknown")
        self.assertFalse(Draft7Validator(modified).is_valid(nested))

    def test_scope_limits_and_opaque_literals(self):
        cycle = schema(**{"$ref": "#"})
        external = schema(**{"$ref": "https://invalid.example/schema"})
        nested = schema(properties={"x": {"$id": "other.json"}})
        modern = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object"}
        for unsupported in (cycle, external, nested, modern):
            with self.subTest(unsupported=unsupported):
                verdict = compare(unsupported, unsupported)
                self.assertEqual(verdict["relation"], "unknown")
                self.assertTrue(verdict["diagnostics"])
        left = schema(enum=[{"$ref": "#/definitions/something"}])
        right = schema(enum=[{"$ref": "#/definitions/another"}])
        self.assertEqual(compare(left, right)["relation"], "unknown")

    def test_optional_assertions_are_reported_as_annotations(self):
        old, new = [schema(type="string", format=fmt) for fmt in ("ipv4", "ipv6")]
        result = compare(old, new)
        self.assertEqual(result["relation"], "equivalent")
        self.assertEqual(result["validation_policy"]["format"], "annotation")
        checked = Draft7Validator(new, format_checker=Draft7Validator.FORMAT_CHECKER)
        self.assertFalse(checked.is_valid("127.0.0.1"))

    def test_integral_exponent_and_json_number_identity(self):
        self.assertEqual(exact_float("1e23"), 10 ** 23)
        self.assertIs(type(exact_float("1e23")), int)
        with self.assertRaises(ValueError):
            exact_float("1e2000")
        with self.assertRaises(ValueError):
            exact_float("0.11111111111111111111111111111")


    def test_json_reader_rejects_unpaired_unicode_surrogates(self):
        with TemporaryDirectory() as temporary:
            source = Path(temporary) / "schema.json"
            source.write_bytes(b'{"const":"\\ud800"}')
            with self.assertRaisesRegex(ValueError, "Unicode surrogate"):
                read_json(source)
            source.write_bytes(b'{"const":"\\ud800\\udc00"}')
            self.assertEqual(len(read_json(source)[1]["const"]), 1)

if __name__ == "__main__":
    unittest.main()
