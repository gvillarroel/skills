#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent controls for class Boolean form and premise preservation."""

import itertools
import unittest

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/extract-ontologies/scripts"))
from normalize_owl_comparison import Call, MAX_ATOMS, MAX_AXIOMS, Parser, normalize


def ledger(*bundles):
    return {"premises": [{"id": f"p{index:02d}", "gap": None, "axioms": list(axioms)}
                         for index, axioms in enumerate(bundles, 1)]}


def one(*axioms):
    return normalize(ledger(axioms))["premises"][0]["axioms"]


def evaluate_class(expression, model):
    if not isinstance(expression, Call):
        if expression == "owl:Thing":
            return True
        if expression == "owl:Nothing":
            return False
        return model[expression]
    operands = [evaluate_class(argument, model) for argument in expression.args]
    return {
        "ObjectIntersectionOf": lambda: all(operands),
        "ObjectUnionOf": lambda: any(operands),
        "ObjectComplementOf": lambda: not operands[0],
    }[expression.op]()


def connective(operator, operands, identity):
    if not operands:
        return identity
    if len(operands) == 1:
        return operands[0]
    return f"{operator}({' '.join(operands)})"


class NormalizeTests(unittest.TestCase):
    def test_redundant_quantifier_implication(self):
        result = "ObjectSomeValuesFrom(:requestValue :MatchingValue)"
        eq = f"EquivalentClasses(:AnyValueTrue ObjectIntersectionOf(:AnyValueTest {result}))"
        extra = f"SubClassOf(:AnyValueTrue {result})"
        self.assertEqual(one(eq), one(extra, eq))

    def test_scoped_parity_and_waiver(self):
        cover = ("SubClassOf(:Full ObjectUnionOf(ObjectIntersectionOf(:FirstNull :SecondNull) "
                 "ObjectIntersectionOf(ObjectComplementOf(:FirstNull) ObjectComplementOf(:SecondNull))))")
        first = "SubClassOf(ObjectIntersectionOf(:Full :FirstNull) :SecondNull)"
        second = "SubClassOf(ObjectIntersectionOf(:Full :SecondNull) :FirstNull)"
        waiver = "SubClassOf(ObjectIntersectionOf(:Full :FirstNull :SecondNull) :Waived)"
        self.assertEqual(one(cover, waiver), one(waiver, first, second))
        self.assertNotEqual(one(cover, waiver), one(waiver, first))

    def test_inclusive_distinct_from_exclusive(self):
        cover = "SubClassOf(:A ObjectUnionOf(:B :C))"
        scoped_exclusion = "SubClassOf(:A ObjectComplementOf(ObjectIntersectionOf(:B :C)))"
        global_exclusion = "DisjointClasses(:B :C)"
        self.assertNotEqual(one(cover), one(cover, scoped_exclusion))
        self.assertNotEqual(one(cover, scoped_exclusion), one(cover, global_exclusion))

    def test_equivalence_and_disjointness_are_order_independent(self):
        self.assertEqual(one("EquivalentClasses(:A :B :C)"),
                         one("EquivalentClasses(:C :A)", "EquivalentClasses(:B :A)"))
        self.assertEqual(one("DisjointClasses(:A :B :C)"),
                         one("DisjointClasses(:C :B)", "DisjointClasses(:A :B)", "DisjointClasses(:C :A)"))

    def test_rows_gaps_and_unsupported_axioms_are_preserved(self):
        first = "ClassAssertion(Annotation(:source \"caption\"@en) :C :example)"
        second = "ObjectPropertyDomain(:field  :D)"
        source = ledger([first, "SubClassOf(:A :B)", second, "SubClassOf(:A :C)"], [])
        source["premises"][1]["gap"] = "No evidence"
        source["premises"][0]["locator"] = {"start": 9, "end": 17}
        view = normalize(source)
        self.assertEqual(view["premises"][0]["axioms"][0], first)
        self.assertEqual(view["premises"][0]["axioms"][2], second)
        self.assertEqual(view["premises"][1], source["premises"][1])
        self.assertEqual(view["premises"][0]["locator"], source["premises"][0]["locator"])
        self.assertEqual(len(source["premises"][0]["axioms"]), 4)
        left = ledger(["SubClassOf(:A :B)"], ["SubClassOf(:B :C)"])
        right = ledger(["SubClassOf(:B :C)"], ["SubClassOf(:A :B)"])
        self.assertNotEqual(normalize(left), normalize(right))

    def test_unknown_supported_syntax_falls_back_to_original_row(self):
        unknown = "SubClassOf(Annotation(:source \"note\") :A :B)"
        valid = "SubClassOf(:A :B)"
        bad = "SubClassOf(:A)"
        language = 'SubClassOf(:A DataHasValue(:label "name"@es))'
        for other in (unknown, bad, language):
            with self.subTest(other=other):
                self.assertEqual(one(valid, other), [valid, other])

    def test_typed_literals_and_order_inside_atoms(self):
        text = r'"a (parenthesis) and \"quoted\" text"^^xsd:string'
        self.assertIn(text, one(f"SubClassOf(:A DataHasValue(:field {text}))")[0])
        def number(datatype):
            return f'SubClassOf(:A DataHasValue(:field "7"^^xsd:{datatype}))'
        self.assertNotEqual(one(number("integer")), one(number("string")))
        self.assertEqual(one("SubClassOf(:A ObjectSomeValuesFrom(:p ObjectUnionOf(:B :C)))"),
                         one("SubClassOf(:A ObjectSomeValuesFrom(:p ObjectUnionOf(:C :B)))"))
        self.assertEqual(one("SubClassOf(:A ObjectMinCardinality(1 :p))"),
                         one("SubClassOf(:A ObjectMinCardinality(1 :p owl:Thing))"))

    def test_direct_integer_intersection_and_combined_facets_share_a_view(self):
        low = 'xsd:minInclusive "-128"^^xsd:integer'
        high = 'xsd:maxInclusive "127"^^xsd:integer'
        joined = f"DatatypeRestriction(xsd:integer {low} {high})"
        split = (f"DataIntersectionOf(DatatypeRestriction(xsd:integer {high}) "
                 f"DatatypeRestriction(xsd:integer {low}))")
        def use(interval):
            return f"SubClassOf(:ByteValue DataAllValuesFrom(:number {interval}))"

        self.assertEqual(one(use(joined)), one(use(split)))
        self.assertNotEqual(normalize(ledger([use(joined)], [])), normalize(ledger([], [use(split)])))

    def test_integer_interval_join_requires_an_intersection_and_compatible_facets(self):
        low = 'DatatypeRestriction(xsd:integer xsd:minInclusive "1"^^xsd:integer)'
        high = 'DatatypeRestriction(xsd:integer xsd:maxInclusive "3"^^xsd:integer)'
        joined = 'DatatypeRestriction(xsd:integer xsd:minInclusive "1"^^xsd:integer xsd:maxInclusive "3"^^xsd:integer)'
        def use(interval):
            return f"SubClassOf(:Value DataSomeValuesFrom(:number {interval}))"

        self.assertNotEqual(one(use(joined)), one(use(f"DataUnionOf({low} {high})")))
        for other in (high.replace("xsd:integer", "xsd:decimal", 1),
                      high.replace("xsd:maxInclusive", "xsd:minInclusive"),
                      high.replace('"3"', '"0"')):
            with self.subTest(other=other):
                result = one(use(f"DataIntersectionOf({low} {other})"))
                self.assertIn("DataIntersectionOf(", result[0])

    def test_bounds_and_propositional_inconsistency_fail_closed(self):
        atom_bound = f"EquivalentClasses({' '.join(f':C{n}' for n in range(MAX_ATOMS + 1))})"
        self.assertEqual(one(atom_bound), [atom_bound])
        group = ["SubClassOf(:A :B)"] * (MAX_AXIOMS + 1)
        self.assertEqual(one(*group), group)
        inconsistent = ("DisjointClasses(owl:Thing :A)", "SubClassOf(owl:Thing :A)")
        self.assertEqual(one(*inconsistent), list(inconsistent))
        long_atom = "SubClassOf(:A :" + "A" * 17_000 + ")"
        self.assertEqual(one(long_atom), [long_atom])

    def test_all_three_variable_truth_tables(self):
        atoms = (":A", ":B", ":C")
        models = tuple(itertools.product((False, True), repeat=len(atoms)))
        for table in range(256):
            values = [bool(table & (1 << index)) for index in range(len(models))]
            dnf = [connective("ObjectIntersectionOf", [
                atom if value else f"ObjectComplementOf({atom})"
                for atom, value in zip(atoms, row, strict=True)
            ], "owl:Thing") for allowed, row in zip(values, models, strict=True) if allowed]
            cnf = [connective("ObjectUnionOf", [
                f"ObjectComplementOf({atom})" if value else atom
                for atom, value in zip(atoms, row, strict=True)
            ], "owl:Nothing") for allowed, row in zip(values, models, strict=True) if not allowed]
            first = f"SubClassOf(owl:Thing {connective('ObjectUnionOf', dnf, 'owl:Nothing')})"
            second = f"SubClassOf(owl:Thing {connective('ObjectIntersectionOf', cnf, 'owl:Thing')})"
            normalized = one(first)
            if table:
                self.assertEqual(normalized, one(second), table)
                self.assertEqual(normalized, one(*normalized), table)
            parsed = Parser(normalized[0]).expression()
            actual = [evaluate_class(parsed.args[1], dict(zip(atoms, row, strict=True))) for row in models]
            self.assertEqual(actual, values, table)


if __name__ == "__main__":
    unittest.main()
