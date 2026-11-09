#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate a bounded, premise-local Boolean comparison ledger.

Keep the original ontology and evidence. Qualify this view against the
original with an independent reasoner before drawing a semantic conclusion.
"""

from argparse import ArgumentParser
from dataclasses import dataclass
from functools import cache, reduce
from itertools import combinations
import json
import operator
from pathlib import Path
import re
import sys


class Unrendered(ValueError):
    """An expression falls outside the bounded Functional Syntax profile."""


MAX_EXPRESSION_LENGTH = 65536
MAX_DEPTH = 64
TOKEN = re.compile(r'"(?:[^"\\\r\n]|\\["\\])*"|<[^<>\s]+>|\^\^|[()]|[^\s()"<>^]+')
NAME = re.compile(r"(?:[A-Za-z_][A-Za-z0-9_.-]*)?:[A-Za-z_][A-Za-z0-9_.-]*|<[^<>\s]+>")
OPERATOR = re.compile(r"[A-Za-z][A-Za-z0-9]*")
NATURAL = re.compile(r"[0-9]+")
INTEGER_BOUND = re.compile(r"[+-]?[0-9]{1,64}")
BOOLEAN = {
    "ObjectIntersectionOf": "and", "ObjectUnionOf": "or", "ObjectComplementOf": "not",
    "DataIntersectionOf": "data_and", "DataUnionOf": "data_or", "DataComplementOf": "data_not",
}
VALUES = {
    "ObjectSomeValuesFrom": "some", "ObjectAllValuesFrom": "all", "ObjectHasValue": "value",
    "DataSomeValuesFrom": "data_some", "DataAllValuesFrom": "data_all", "DataHasValue": "data_value",
}
COUNTS = {
    f"{prefix}{force}Cardinality": marker + force.lower()
    for prefix, marker in (("Object", ""), ("Data", "data_"))
    for force in ("Min", "Max", "Exact")
}
FACETS = {"xsd:minInclusive", "xsd:minExclusive", "xsd:maxInclusive", "xsd:maxExclusive"}


@dataclass(frozen=True)
class Call:
    op: str
    args: tuple


@dataclass(frozen=True)
class Literal:
    datatype: str
    lexical: str


def lex(text):
    if type(text) is not str or len(text) > MAX_EXPRESSION_LENGTH:
        raise Unrendered("invalid Functional Syntax input length")
    cursor = 0
    tokens = []
    for match in TOKEN.finditer(text):
        if text[cursor:match.start()].strip():
            raise Unrendered("unrecognized Functional Syntax token")
        tokens.append(match[0])
        cursor = match.end()
    if text[cursor:].strip():
        raise Unrendered("unrecognized Functional Syntax suffix")
    return tokens


class Parser:
    def __init__(self, text):
        self.tokens = lex(text)
        self.index = 0

    def peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def take(self):
        token = self.peek()
        if token is None:
            raise Unrendered("unexpected end of Functional Syntax")
        self.index += 1
        return token

    def expression(self, depth=0):
        if depth > MAX_DEPTH:
            raise Unrendered("Functional Syntax nesting limit exceeded")
        head = self.take()
        if head.startswith('"'):
            try:
                lexical = json.loads(head)
            except ValueError as exc:
                raise Unrendered("unsupported quoted lexical form") from exc
            if self.peek() == "^^":
                self.take()
                return Literal(self.take(), lexical)
            if self.peek() and self.peek().startswith("@"):
                raise Unrendered("language-tagged literals require the verbatim surface")
            return Literal("xsd:string", lexical)
        if self.peek() == "(":
            if not OPERATOR.fullmatch(head):
                raise Unrendered("invalid Functional Syntax operator")
            self.take()
            arguments = []
            while self.peek() != ")":
                arguments.append(self.expression(depth + 1))
            self.take()
            return Call(head, tuple(arguments))
        if head in {"(", ")", "^^"}:
            raise Unrendered("unexpected Functional Syntax punctuation")
        return head


def arity(call, *lengths):
    if len(call.args) not in lengths:
        raise Unrendered(f"unexpected arity for {call.op!r}")
    return call.args


def atom(value):
    if type(value) is not str or not NAME.fullmatch(value):
        raise Unrendered("expected a named term")
    return value.removeprefix(":")


def class_atom(value):
    name = atom(value)
    if name in ("top", "bottom"):
        return value
    return {"owl:Thing": "top", "owl:Nothing": "bottom",
            "<http://www.w3.org/2002/07/owl#Thing>": "top",
            "<http://www.w3.org/2002/07/owl#Nothing>": "bottom"}.get(name, name)


def literal(value):
    if not isinstance(value, Literal):
        raise Unrendered("expected a literal")
    return ["lit", atom(value.datatype), value.lexical]


def relation(value):
    if isinstance(value, Call) and value.op == "ObjectInverseOf":
        inner, = arity(value, 1)
        return ["inverse", atom(inner)]
    return atom(value)


def datatype(value):
    if not isinstance(value, Call):
        name = atom(value)
        return "rdfs:Literal" if name == "<http://www.w3.org/2000/01/rdf-schema#Literal>" else name
    op = value.op
    if op in {"DataIntersectionOf", "DataUnionOf", "DataComplementOf"}:
        return boolean(value, datatype)
    if op == "DataOneOf" and value.args:
        return ["data_one_of", *map(literal, value.args)]
    if op == "DatatypeRestriction" and len(value.args) >= 3 and len(value.args) % 2 == 1:
        base, *constraints = value.args
        facets = []
        for name, bound in zip(constraints[::2], constraints[1::2], strict=True):
            name = atom(name)
            if name not in FACETS:
                raise Unrendered("unsupported datatype facet")
            facets.append([name.removeprefix("xsd:"), literal(bound)])
        return ["restrict", atom(base), *facets]
    raise Unrendered(f"unsupported data range {op!r}")


def boolean(value, convert):
    args = value.args
    if value.op.endswith("ComplementOf"):
        arity(value, 1)
    elif len(args) < 2:
        raise Unrendered("Boolean expression needs multiple arguments")
    return [BOOLEAN[value.op], *map(convert, args)]


def restriction(value):
    op = value.op
    is_data = op.startswith("Data")
    prop = atom if is_data else relation
    filler = datatype if is_data else class_ast
    if op in VALUES:
        property_id, condition = arity(value, 2)
        if op.endswith("HasValue"):
            filler = literal if is_data else atom
        return [VALUES[op], prop(property_id), filler(condition)]
    number, property_id, *condition = arity(value, 2, 3)
    if type(number) is not str or not NATURAL.fullmatch(number) or len(number) > 12:
        raise Unrendered("unsupported cardinality")
    top = "rdfs:Literal" if is_data else "top"
    return [COUNTS[op], int(number), prop(property_id), filler(condition[0]) if condition else top]


def class_ast(value):
    if not isinstance(value, Call):
        return class_atom(value)
    op = value.op
    if op in {"ObjectIntersectionOf", "ObjectUnionOf", "ObjectComplementOf"}:
        return boolean(value, class_ast)
    if op in VALUES or op in COUNTS:
        return restriction(value)
    if op == "ObjectOneOf" and value.args:
        return ["one_of", *map(atom, value.args)]
    if op == "ObjectHasSelf":
        prop, = arity(value, 1)
        return ["self", relation(prop)]
    raise Unrendered(f"unsupported class expression {op!r}")


MAX_ATOMS = 10
MAX_AXIOMS = 32
MAX_AXIOM_OPERANDS = 20
MAX_BUNDLE_BYTES = 65_536
MAX_OUTPUT_BYTES = 16_384
SUPPORTED = {"SubClassOf", "EquivalentClasses", "DisjointClasses"}
OUTER = re.compile(r"\s*([A-Za-z][A-Za-z0-9]*)\s*\(")
CLASS_BOOLEAN = {"ObjectIntersectionOf": "and", "ObjectUnionOf": "or", "ObjectComplementOf": "not"}
COMMUTATIVE = {
    "ObjectIntersectionOf", "ObjectUnionOf", "ObjectOneOf", "DataIntersectionOf", "DataUnionOf", "DataOneOf",
}
BUILTINS = {
    "<http://www.w3.org/2002/07/owl#Thing>": "owl:Thing",
    "<http://www.w3.org/2002/07/owl#Nothing>": "owl:Nothing",
    "<http://www.w3.org/2000/01/rdf-schema#Literal>": "rdfs:Literal",
}


def byte_key(value):
    return value.encode("utf-8")


def ofn(head, *args):
    return f"{head}({' '.join(args)})"


def merge_integer_interval(value):
    """Combine exactly one integer lower bound and one integer upper bound."""
    if len(value.args) != 2:
        return value
    bounds = {}
    for child in value.args:
        if not isinstance(child, Call) or child.op != "DatatypeRestriction" or len(child.args) != 3:
            return value
        base, facet, bound = child.args
        if (base != "xsd:integer" or facet not in FACETS or not isinstance(bound, Literal)
                or bound.datatype != base or not INTEGER_BOUND.fullmatch(bound.lexical)):
            return value
        side = "lower" if facet.startswith("xsd:min") else "upper"
        if side in bounds:
            return value
        bounds[side] = (facet, bound)
    lower_facet, lower = bounds["lower"]
    upper_facet, upper = bounds["upper"]
    first = int(lower.lexical) + (lower_facet == "xsd:minExclusive")
    last = int(upper.lexical) - (upper_facet == "xsd:maxExclusive")
    if first > last:
        return value
    return Call("DatatypeRestriction", ("xsd:integer", lower_facet, lower, upper_facet, upper))


def surface(value):
    """Canonicalize spelling within validated atoms without changing lexical values."""
    if isinstance(value, Literal):
        return f"{json.dumps(value.lexical, ensure_ascii=False)}^^{value.datatype}"
    if not isinstance(value, Call):
        return BUILTINS.get(value, value)
    if value.op == "DataIntersectionOf":
        value = merge_integer_interval(value)
    operands = list(map(surface, value.args))
    if value.op in COMMUTATIVE:
        operands.sort(key=byte_key)
    elif value.op == "DatatypeRestriction":
        base, *facets = operands
        pairs = sorted(zip(facets[::2], facets[1::2], strict=True), key=lambda pair: byte_key(pair[0]))
        operands = [base, *(arg for pair in pairs for arg in pair)]
    elif value.op in COUNTS and len(operands) == 2:
        operands.append("rdfs:Literal" if value.op.startswith("Data") else "owl:Thing")
    return ofn(value.op, *operands)


def logic(value, atoms):
    """Split only the surrounding class Booleans; treat restrictions as atoms."""
    if isinstance(value, Call) and value.op in CLASS_BOOLEAN:
        op = CLASS_BOOLEAN[value.op]
        if (op == "not" and len(value.args) != 1) or (op != "not" and len(value.args) < 2):
            raise Unrendered("invalid class Boolean arity")
        return (op, *(logic(child, atoms) for child in value.args))
    class_ast(value)
    text = surface(value)
    if text == "owl:Thing":
        return True
    if text == "owl:Nothing":
        return False
    atoms.add(text)
    if len(atoms) > MAX_ATOMS:
        raise Unrendered("Boolean atom limit exceeded")
    return text


def imply(left, right):
    return ("or", ("not", left), right)


def formula(axiom, atoms):
    parser = Parser(axiom)
    value = parser.expression()
    if (not isinstance(value, Call) or value.op not in SUPPORTED or parser.peek() is not None
            or not 2 <= len(value.args) <= MAX_AXIOM_OPERANDS
            or (value.op == "SubClassOf" and len(value.args) != 2)):
        raise Unrendered("unsupported or malformed class axiom")
    terms = tuple(logic(arg, atoms) for arg in value.args)
    first, *others = terms
    if value.op == "SubClassOf":
        return imply(first, others[0])
    if value.op == "EquivalentClasses":
        return ("and", *(condition for item in others
                          for condition in (imply(first, item), imply(item, first))))
    return ("and", *(("not", ("and", left, right)) for left, right in combinations(terms, 2)))


def truth(form, masks, universe):
    if form is True:
        return universe
    if form is False:
        return 0
    if isinstance(form, str):
        return masks[form]
    op, *children = form
    values = (truth(child, masks, universe) for child in children)
    if op == "not":
        return universe ^ next(values)
    if op == "and":
        return reduce(operator.and_, values, universe)
    return reduce(operator.or_, values, 0)


def decision(formulas, atoms):
    """Build a reduced ordered decision diagram from a bounded truth table."""
    assignments = 1 << len(atoms)
    universe = (1 << assignments) - 1
    masks = {atom: sum(1 << assignment for assignment in range(assignments)
                       if assignment & (1 << (len(atoms) - index - 1)))
             for index, atom in enumerate(atoms)}
    table = reduce(operator.and_, (truth(row, masks, universe) for row in formulas), universe)

    @cache
    def build(level, values):
        width = 1 << (len(atoms) - level)
        if not values:
            return False
        if values == (1 << width) - 1:
            return True
        half = width // 2
        low = build(level + 1, values & ((1 << half) - 1))
        high = build(level + 1, values >> half)
        if low == high:
            return low
        return atoms[level], low, high

    return build(0, table)


def render(tree):
    if tree is True:
        return "owl:Thing"
    if tree is False:
        raise Unrendered("the premise has no propositional model")
    atom, low, high = tree
    negated = ofn("ObjectComplementOf", atom)
    if low is False and high is True:
        result = atom
    elif low is True and high is False:
        result = negated
    elif low is False:
        result = ofn("ObjectIntersectionOf", atom, render(high))
    elif high is False:
        result = ofn("ObjectIntersectionOf", negated, render(low))
    elif low is True:
        result = ofn("ObjectUnionOf", negated, render(high))
    elif high is True:
        result = ofn("ObjectUnionOf", atom, render(low))
    else:
        result = ofn("ObjectUnionOf", ofn("ObjectIntersectionOf", negated, render(low)),
                     ofn("ObjectIntersectionOf", atom, render(high)))
    if len(byte_key(result)) > MAX_OUTPUT_BYTES:
        raise Unrendered("Boolean rendering exceeds the output bound")
    return result


def supported(axiom):
    match = OUTER.match(axiom)
    return match is not None and match[1] in SUPPORTED


def normalize_row(row):
    axioms = row["axioms"]
    if (row.get("gap") is not None or not axioms or len(axioms) > MAX_AXIOMS
            or sum(len(byte_key(axiom)) for axiom in axioms) > MAX_BUNDLE_BYTES):
        return row
    indices = [index for index, axiom in enumerate(axioms) if supported(axiom)]
    if not indices:
        return row
    try:
        atoms = set()
        formulas = [formula(axioms[index], atoms) for index in indices]
        tree = decision(formulas, sorted(atoms, key=byte_key))
        normalized = ofn("SubClassOf", "owl:Thing", render(tree))
        if len(byte_key(normalized)) > MAX_OUTPUT_BYTES:
            return row
    except Unrendered:
        return row
    replace = set(indices)
    result = [normalized if index == indices[0] else axiom
              for index, axiom in enumerate(axioms) if index == indices[0] or index not in replace]
    return {**row, "axioms": result}


def normalize(ledger):
    """Return a comparison ledger with original rows, IDs, and gaps preserved."""
    if (type(ledger) is not dict or type(ledger.get("premises")) is not list
            or any(type(row) is not dict or type(row.get("axioms")) is not list
                   or any(type(axiom) is not str for axiom in row["axioms"]) for row in ledger["premises"])):
        raise ValueError("invalid OWL premise ledger")
    return {**ledger, "premises": [normalize_row(row) for row in ledger["premises"]]}


def unique_object(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON object key")
    return result


def write_view(input_path, output_path):
    ledger = json.loads(input_path.read_bytes(), object_pairs_hook=unique_object)
    view = normalize(ledger)
    encoded = (json.dumps(view, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    handle = output_path.open("xb")
    try:
        with handle:
            handle.write(encoded)
    except OSError:
        output_path.unlink(missing_ok=True)
        raise


def main(argv=None):
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True, help="Existing compiled OWL premise ledger")
    parser.add_argument("--comparison-view", type=Path, required=True,
                        help="New output JSON path for the comparison view")
    args = parser.parse_args(argv)
    try:
        write_view(args.ledger, args.comparison_view)
    except (OSError, ValueError) as exc:
        print(f"Comparison view could not be written: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
