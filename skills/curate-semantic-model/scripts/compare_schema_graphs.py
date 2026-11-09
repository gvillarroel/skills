#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema==4.25.1", "referencing==0.36.2"]
# ///
"""Check equality of bounded Draft 7 validation graphs."""

from argparse import ArgumentParser
from collections import Counter
from decimal import Decimal
from hashlib import sha256
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError

DRAFT7 = {"http://json-schema.org/draft-07/schema", "https://json-schema.org/draft-07/schema"}
METADATA = {"$schema", "$id", "$comment", "title", "description", "default", "examples",
            "readOnly", "writeOnly", "format", "contentEncoding", "contentMediaType",
            "markdownDescription", "enumDescriptions", "markdownEnumDescriptions",
            "deprecationMessage", "deprecated", "doNotSuggest", "suggestSortText", "x-intellij-enum-metadata"}
MAPS = {"definitions", "properties", "patternProperties"}
SINGLE = {"additionalProperties", "additionalItems", "propertyNames", "contains", "not", "if", "then", "else"}
GROUPS = {"allOf", "anyOf", "oneOf"}
ATOMS = {"type", "enum", "const", "required", "maximum", "minimum", "exclusiveMinimum",
         "exclusiveMaximum", "multipleOf", "minLength", "maxLength", "pattern", "minItems",
         "maxItems", "uniqueItems", "minProperties", "maxProperties"}


class Unsupported(ValueError):
    """The semantic view cannot establish this input's meaning."""


def stable(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":"))


def pointer(path):
    return "#" + "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in path)


def parse_pointer(value):
    if type(value) is not str or not value.startswith("#"):
        raise Unsupported("nonlocal reference")
    if re.search(r"%(?![a-fA-F0-9]{2})", value):
        raise Unsupported("malformed reference escape")
    try:
        fragment = unquote(value[1:], errors="strict")
    except UnicodeDecodeError as exc:
        raise Unsupported("invalid UTF-8 reference fragment") from exc
    if fragment == "":
        return ()
    if not fragment.startswith("/") or re.search(r"~(?![01])", fragment):
        raise Unsupported("reference fragment is not a supported JSON Pointer")
    return tuple(token.replace("~1", "/").replace("~0", "~") for token in fragment[1:].split("/"))


def dialect(schema, assume):
    if type(schema) is bool or "$schema" not in schema:
        if not assume:
            raise Unsupported("Draft 7 must be declared or explicitly selected")
        return
    value = schema["$schema"]
    if not isinstance(value, str) or value.removesuffix("#") not in DRAFT7:
        raise Unsupported("unsupported dialect")


def children(schema):
    """Yield only documented schema-bearing positions."""
    for key in sorted(schema):
        value = schema[key]
        if key in MAPS:
            for name, child in sorted(value.items()):
                yield (key, name), child
        elif key in SINGLE:
            yield (key,), value
        elif key in GROUPS or (key == "items" and type(value) is list):
            for index, child in enumerate(value):
                yield (key, str(index)), child
        elif key == "items":
            yield (key,), value
        elif key == "dependencies":
            for name, child in sorted(value.items()):
                if type(child) is not list:
                    yield (key, name), child


def schema_index(root):
    index = {}

    def visit(schema, path):
        if len(index) >= 40000 or len(path) > 150:
            raise Unsupported("schema indexing budget")
        index[path] = schema
        if type(schema) is not dict:
            return
        if path and ("$id" in schema or "$schema" in schema):
            raise Unsupported(f"nested resource or dialect at {pointer(path)}")
        for relative, child in children(schema):
            visit(child, path + relative)

    visit(root, ())
    return index


def exact_float(token):
    if len(token) > 280:
        raise ValueError("numeric precision budget exceeded")
    number = Decimal(token)
    if abs(number.adjusted()) > 256:
        raise ValueError("numeric exponent budget exceeded")
    if number == number.to_integral_value():
        return int(number)
    value = float(token)
    if not math.isfinite(value) or Decimal(str(value)) != number:
        raise ValueError("numeric input cannot be represented with the declared parser precision")
    return value


def bounded_int(token):
    if len(token.lstrip("-")) > 257:
        raise ValueError("numeric precision budget exceeded")
    return int(token)


def no_duplicate(items):
    obj = dict(items)
    if len(obj) != len(items):
        raise ValueError("duplicate JSON object key")
    return obj


def reject_constant(token):
    raise ValueError(f"invalid JSON constant {token}")


def read_json(path):
    raw = path.read_bytes()
    if len(raw) > 2_000_000:
        raise ValueError("JSON byte budget exceeded")
    value = json.loads(raw, parse_float=exact_float, parse_int=bounded_int,
                       parse_constant=reject_constant, object_pairs_hook=no_duplicate)
    try:
        json.dumps(value, ensure_ascii=False).encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("unpaired Unicode surrogate in JSON input") from exc
    return raw, value


DESCENT = {"properties", "patternProperties", "additionalProperties", "items", "contains"}


def prune_one_of(shape, counts):
    """Remove a duplicate conjunct from branch predicates under the same parent."""
    if shape.get("type") != "object" or "oneOf" not in shape:
        return shape
    outer = shape.get("properties", {})
    branches = []
    for branch in shape["oneOf"]:
        if type(branch) is not dict or not branch.keys() <= {"type", "properties", "required"}:
            branches.append(branch)
            continue
        revised = dict(branch)
        if revised.get("type") == "object":
            revised.pop("type")
            counts["outer-object-type"] += 1
        if "properties" in revised:
            scoped = {name: rule for name, rule in revised["properties"].items()
                      if name not in outer or stable(rule) != stable(outer[name])}
            counts["duplicate-property-condition"] += len(revised["properties"]) - len(scoped)
            if scoped:
                revised["properties"] = scoped
            else:
                revised.pop("properties")
        branches.append(revised)
    return {**shape, "oneOf": sorted(branches, key=stable)}


def normalize(root, *, assume=False):
    if type(root) not in (dict, bool):
        raise Unsupported("schema must be an object or boolean")
    dialect(root, assume)
    Draft7Validator.check_schema(root)
    index = schema_index(root)
    rules, bindings = Counter(), set()
    operations = 0

    def visit(path, active, depth):
        nonlocal operations
        operations += 1
        if operations > 50000 or len(active) > 130:
            raise Unsupported("guarded graph traversal budget")
        if path in active:
            if depth <= active[path]:
                raise Unsupported(f"unguarded reference cycle at {pointer(path)}")
            bindings.add(path)
            rules["guarded-cycle"] += 1
            return {"@cycle": pointer(path)}
        active = {**active, path: depth}
        schema = index[path]
        if type(schema) is bool:
            return {} if schema else False
        if "$ref" in schema:
            target = parse_pointer(schema["$ref"])
            if target not in index:
                raise Unsupported(f"reference target is not an indexed subschema at {pointer(path)}")
            rules["local-reference"] += 1
            shape = visit(target, active, depth)
        else:
            shape = {}
            for keyword, value in sorted(schema.items()):
                if keyword in METADATA or keyword == "definitions":
                    continue
                if keyword in {"enum", "required", "type"} and isinstance(value, list):
                    shape[keyword] = sorted(value, key=stable)
                elif keyword in ATOMS:
                    shape[keyword] = value
                elif keyword == "dependencies":
                    sequences = {name: sorted(item) for name, item in value.items() if isinstance(item, list)}
                    if sequences:
                        shape[keyword] = sequences
                elif keyword not in MAPS | SINGLE | GROUPS | {"items"}:
                    raise Unsupported(f"unknown keyword {keyword} at {pointer(path)}")
            for (keyword, *relative), _ in children(schema):
                if keyword == "definitions":
                    continue
                child = visit((*path, keyword, *relative), active, depth + (keyword in DESCENT))
                if not relative:
                    shape[keyword] = child
                elif keyword in GROUPS | {"items"}:
                    shape.setdefault(keyword, []).append(child)
                else:
                    shape.setdefault(keyword, {})[relative[0]] = child
            for keyword in GROUPS & shape.keys():
                shape[keyword].sort(key=stable)
            if set(shape) == {"allOf"} and len(shape["allOf"]) == 2:
                first, second = shape["allOf"]
                if type(first) is dict and type(second) is dict:
                    for choices, parent in ((first, second), (second, first)):
                        if set(choices) == {"oneOf"} and "oneOf" not in parent and not any(
                                name.startswith("@") for name in parent):
                            shape = {**parent, **choices}
                            rules["same-instance-one-of-conjunction"] += 1
                            break
            shape = prune_one_of(shape, rules)
        return {"@binder": pointer(path), "@body": shape} if path in bindings else shape

    return visit((), {}, 0), dict(sorted(rules.items()))


def compare(old, new, *, assume=False):
    result = {
        "relation": "unknown",
        "certificate": None,
        "diagnostics": [],
        "validation_policy": {
            "dialect": "draft7",
            "format": "annotation",
            "content_keywords": "annotation",
            "references": "offline-local-json-pointer",
        },
    }
    try:
        first, first_rules = normalize(old, assume=assume)
        second, second_rules = normalize(new, assume=assume)
        before, after = stable(first), stable(second)
        result["views"] = {"before_sha256": sha256(before.encode()).hexdigest(),
                           "after_sha256": sha256(after.encode()).hexdigest()}
        result["rules"] = {"before": first_rules, "after": second_rules}
        if before == after:
            result["relation"] = "equivalent"
            result["certificate"] = "identical-guarded-validation-graph"
    except (Unsupported, SchemaError, RecursionError) as exc:
        result["diagnostics"].append({"kind": type(exc).__name__, "message": str(exc).splitlines()[0]})
    return result


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("before", type=Path)
    cli.add_argument("after", type=Path)
    cli.add_argument("--assume-draft7", action="store_true")
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    source_before, before = read_json(args.before)
    source_after, after = read_json(args.after)
    result = compare(before, after, assume=args.assume_draft7)
    result["sources"] = {"before_sha256": sha256(source_before).hexdigest(),
                         "after_sha256": sha256(source_after).hexdigest()}
    with args.output.open("xb") as handle:
        handle.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode())
    print(result["relation"], result["diagnostics"], flush=True)


if __name__ == "__main__":
    main()
