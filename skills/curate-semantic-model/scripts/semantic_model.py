#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Typed local model contracts, incremental staging and conservative reduction.

Python 3.11+, standard library only. This is not an OWL reasoner or a semantic
equivalence detector. Commands never edit their input files.
"""
import argparse
import copy
import json
import math
import os
import sys
from collections import defaultdict, deque
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION = "1.0.1"
CONTRACT_KEYS = {"schema_version", "id", "version", "types", "relations", "require_source_bindings", "checks"}
TYPE_KEYS = {"attributes", "required_attributes", "closed_attributes", "min_sources", "outgoing"}
ATTRIBUTE_KEYS = {"type", "enum", "min_length", "max_length", "minimum", "maximum", "items_type"}
RELATION_KEYS = {"from_types", "to_types", "acyclic", "symmetric", "review_required", "transitive", "reduce_closure", "exclusive_with"}
MODEL_KEYS = {"schema_version", "contract_id", "contract_version", "sources", "nodes", "relations", "bindings", "history", "metadata"}
NODE_KEYS = {"id", "type", "label", "definition", "source_ids", "attributes", "aliases"}
EDGE_KEYS = {"id", "type", "from", "to", "source_ids", "review"}
VALUE_TYPES = {"string", "integer", "number", "boolean", "array", "object"}


class EngineError(Exception):
    def __init__(self, code, message, path="/", actual=None):
        super().__init__(message)
        self.code, self.path, self.actual = code, path, actual


def require(condition, message, path="/", code="INVALID_CONTRACT", actual=None):
    if not condition:
        raise EngineError(code, message, path, actual)


def parse_json_text(text, filename, *, exact_numbers=False):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise EngineError("JSON_DUPLICATE_KEY", "Duplicate JSON object key", actual=key)
            out[key] = value
        return out
    def invalid(value):
        raise EngineError("INVALID_JSON_NUMBER", "Non-finite JSON number", actual=value)
    def exact_float(token):
        value = float(token)
        if not math.isfinite(value):
            raise EngineError("INVALID_JSON_NUMBER", "Non-finite JSON number", str(filename), token)
        try:
            if Decimal(token) != Decimal(str(value)):
                raise EngineError("JSON_NUMBER_PRECISION_LOSS",
                                  "JSON number cannot be represented without decimal precision loss",
                                  str(filename), token)
        except InvalidOperation as exc:
            raise EngineError("INVALID_JSON_NUMBER", "Invalid JSON number", str(filename), token) from exc
        return value
    try:
        options = {"parse_float": exact_float} if exact_numbers else {}
        value = json.loads(text, object_pairs_hook=unique, parse_constant=invalid, **options)
        # Also rejects exponents that overflow to infinity.
        json.dumps(value, allow_nan=False)
        return value
    except EngineError:
        raise
    except (OSError, ValueError, TypeError) as exc:
        raise EngineError("INPUT_ERROR", str(exc), str(filename)) from exc


def read_json(filename, *, exact_numbers=False):
    try:
        text = Path(filename).read_text(encoding="utf-8-sig")
    except (OSError, ValueError, TypeError) as exc:
        raise EngineError("INPUT_ERROR", str(exc), str(filename)) from exc
    return parse_json_text(text, filename, exact_numbers=exact_numbers)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def string_list(value):
    return isinstance(value, list) and all(nonempty(x) for x in value)


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def exact_json_equal(left, right):
    """Compare JSON recursively without coercing booleans or numeric types."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(exact_json_equal(value, right[key]) for key, value in left.items())
    if isinstance(left, list):
        return len(left) == len(right) and all(exact_json_equal(a, b) for a, b in zip(left, right))
    return left == right


def unknown(obj, allowed, path):
    require(isinstance(obj, dict), "Expected an object", path)
    extra = set(obj) - allowed
    require(not extra, "Unsupported contract keys; validation was not completed", path,
            "UNSUPPORTED_CONSTRAINT", sorted(extra))


def check_contract(contract):
    unknown(contract, CONTRACT_KEYS, "/contract")
    require(contract.get("schema_version") == "1", "Supported contract schema_version is 1")
    require(nonempty(contract.get("id")) and nonempty(contract.get("version")), "Contract id and version are required")
    types, rules = contract.get("types"), contract.get("relations")
    require(isinstance(types, dict) and bool(types), "Declare at least one type", "/types")
    require(isinstance(rules, dict), "relations must be an object", "/relations")
    require(isinstance(contract.get("require_source_bindings", True), bool), "require_source_bindings must be boolean")
    for name, profile in types.items():
        path = "/types/" + name
        require(nonempty(name), "Type names must be nonempty", path)
        unknown(profile, TYPE_KEYS, path)
        attrs = profile.get("attributes", {})
        require(isinstance(attrs, dict), "attributes must be an object", path)
        required = profile.get("required_attributes", [])
        require(string_list(required) and set(required) <= set(attrs), "Required attributes must be declared", path)
        require(isinstance(profile.get("closed_attributes", False), bool), "closed_attributes must be boolean", path)
        minimum = profile.get("min_sources", 1)
        require(integer(minimum) and minimum >= 0, "min_sources must be a nonnegative integer", path)
        for attr, spec in attrs.items():
            unknown(spec, ATTRIBUTE_KEYS, path + "/attributes/" + attr)
            require(isinstance(spec.get("type"), str) and spec["type"] in VALUE_TYPES, "Unsupported attribute type", path)
            if "enum" in spec:
                require(isinstance(spec["enum"], list) and bool(spec["enum"]), "enum must be nonempty", path)
                require(all(matches(v, spec["type"]) for v in spec["enum"]), "enum values must match the attribute type", path)
            for limit in ("min_length", "max_length"):
                if limit in spec:
                    require(integer(spec[limit]) and spec[limit] >= 0 and spec["type"] in ("string", "array"), "Length bound incompatible with attribute", path)
            for limit in ("minimum", "maximum"):
                if limit in spec:
                    require(type(spec[limit]) in (int, float) and spec["type"] in ("integer", "number"), "Numeric bound incompatible with attribute", path)
            require(spec.get("min_length", 0) <= spec.get("max_length", math.inf), "Inverted length bounds", path)
            require(spec.get("minimum", -math.inf) <= spec.get("maximum", math.inf), "Inverted numeric bounds", path)
            if "items_type" in spec:
                require(spec["type"] == "array" and isinstance(spec["items_type"], str) and spec["items_type"] in VALUE_TYPES, "items_type requires array", path)
        outgoing = profile.get("outgoing", {})
        require(isinstance(outgoing, dict), "outgoing must be an object", path)
        for predicate, bounds in outgoing.items():
            require(predicate in rules, "Unknown outgoing predicate", path)
            unknown(bounds, {"min", "max"}, path)
            require(all(integer(v) and v >= 0 for v in bounds.values()) and bounds.get("min", 0) <= bounds.get("max", math.inf), "Invalid cardinality bounds", path)
    for name, rule in rules.items():
        path = "/relations/" + name
        require(nonempty(name), "Relation names must be nonempty", path)
        unknown(rule, RELATION_KEYS, path)
        for field in ("from_types", "to_types"):
            require(string_list(rule.get(field)) and bool(rule[field]) and set(rule[field]) <= set(types), "Relation endpoint types must be declared", path)
        for field in ("acyclic", "symmetric", "review_required", "transitive", "reduce_closure"):
            require(isinstance(rule.get(field, False), bool), field + " must be boolean", path)
        require(not rule.get("reduce_closure") or (rule.get("transitive") and rule.get("acyclic") and not rule.get("symmetric")), "Closure reduction requires an explicitly transitive, acyclic, directional predicate", path)
        require(string_list(rule.get("exclusive_with", [])) and set(rule.get("exclusive_with", [])) <= set(rules), "Unknown exclusive predicate", path)
    checks = contract.get("checks", [])
    require(isinstance(checks, list), "checks must be an array")
    seen = set()
    for test in checks:
        unknown(test, {"id", "query", "expect"}, "/checks")
        require(nonempty(test.get("id")) and test["id"] not in seen, "Competency-test IDs must be unique")
        seen.add(test["id"])
        require(string_list(test.get("expect")), "expect must be an array of IDs")
        query = test.get("query")
        require(isinstance(query, dict), "query must be an object")
        op = query.get("op")
        fields = {"nodes_of_type": {"op", "type"}, "nodes_where": {"op", "type", "equals"}, "bindings": {"op", "source_id"}, "neighbors": {"op", "from", "relation"}, "reachable": {"op", "from", "relation"}}
        require(isinstance(op, str) and op in fields, "Unsupported competency query", "/checks", "UNSUPPORTED_CONSTRAINT", op)
        unknown(query, fields[op], "/checks/query")
        require(set(query) == fields[op] and all(nonempty(v) for k, v in query.items() if k != "equals"), "Incomplete competency query")
        if "relation" in query:
            require(query["relation"] in rules, "Query predicate is undeclared")
        if "type" in query:
            require(query["type"] in types, "Query type is undeclared")
        if op == "nodes_where":
            equals = query["equals"]
            require(isinstance(equals, dict) and bool(equals), "nodes_where requires a nonempty equals object")
            attrs = types[query["type"]].get("attributes", {})
            require(set(equals) <= set(attrs), "Query filters must name declared attributes")
            require(all(type(v) in (str, int, float, bool) and matches(v, attrs[k]["type"]) for k, v in equals.items()), "Query filters require scalar values matching the declared attribute type")


def adjacency(edges, predicate):
    graph = defaultdict(set)
    for edge in edges:
        if edge.get("type") == predicate and nonempty(edge.get("from")) and nonempty(edge.get("to")):
            graph[edge["from"]].add(edge["to"])
    return graph


def path_between(graph, start, target):
    queue, previous = deque([start]), {start: None}
    while queue:
        node = queue.popleft()
        for other in sorted(graph.get(node, [])):
            if other in previous:
                continue
            previous[other] = node
            if other == target:
                path = [target]
                while previous[path[-1]] is not None:
                    path.append(previous[path[-1]])
                return path[::-1]
            queue.append(other)
    return None


def cycle_witness(graph):
    state = {}
    for start in sorted(graph):
        if state.get(start):
            continue
        trail, stack = [start], [(start, iter(sorted(graph[start])))]
        state[start] = 1
        while stack:
            node, iterator = stack[-1]
            try:
                other = next(iterator)
            except StopIteration:
                state[node] = 2
                stack.pop()
                trail.pop()
                continue
            if state.get(other) == 1:
                return trail[trail.index(other):] + [other]
            if not state.get(other):
                state[other] = 1
                trail.append(other)
                stack.append((other, iter(sorted(graph.get(other, [])))))
    return None


def query_result(model, query):
    op = query["op"]
    if op == "nodes_of_type":
        return sorted(n["id"] for n in model["nodes"] if n.get("type") == query["type"])
    if op == "nodes_where":
        return sorted(n["id"] for n in model["nodes"] if n.get("type") == query["type"] and all(k in n.get("attributes", {}) and type(n["attributes"][k]) is type(value) and n["attributes"][k] == value for k, value in query["equals"].items()))
    if op == "bindings":
        return sorted(set(model.get("bindings", {}).get(query["source_id"], [])))
    graph = adjacency(model["relations"], query["relation"])
    if op == "neighbors":
        return sorted(graph.get(query["from"], []))
    seen, queue = set(), deque(graph.get(query["from"], []))
    while queue:
        node = queue.popleft()
        if node not in seen:
            seen.add(node)
            queue.extend(graph.get(node, []))
    return sorted(seen)


def matches(value, kind):
    return {"string": lambda: isinstance(value, str), "integer": lambda: integer(value), "number": lambda: type(value) in (int, float), "boolean": lambda: isinstance(value, bool), "array": lambda: isinstance(value, list), "object": lambda: isinstance(value, dict)}[kind]()


def validate(model, contract, baseline=None):
    check_contract(contract)
    errors, warnings = [], []
    def issue(code, path, expected, actual, entity=None, node_type=None, severity="error", message=None):
        item = {"code": code, "path": path, "entity": entity, "type": node_type, "expected": expected, "actual": actual, "severity": severity, "message": message or code, "contract": contract["id"], "rule_version": contract["version"]}
        (warnings if severity == "warning" else errors).append(item)
    require(isinstance(model, dict), "Model must be an object", code="MODEL_PARSE_ERROR")
    extra = set(model) - MODEL_KEYS
    if extra:
        issue("UNKNOWN_MODEL_FIELD", "/", sorted(MODEL_KEYS), sorted(extra))
    for field, kind in [("history", list), ("metadata", dict)]:
        if field in model and not isinstance(model[field], kind):
            issue("MODEL_FIELD_TYPE", "/" + field, kind.__name__, model[field])
    for field, expected in [("schema_version", "1"), ("contract_id", contract["id"]), ("contract_version", contract["version"])]:
        if model.get(field) != expected:
            issue("CONTRACT_MISMATCH", "/" + field, expected, model.get(field))
    records = {}
    for collection in ("sources", "nodes", "relations"):
        entries = model.get(collection)
        if not isinstance(entries, list):
            issue("COLLECTION_TYPE", "/" + collection, "array", entries)
            entries = []
        index = {}
        for i, entry in enumerate(entries):
            path = "/" + collection + "/" + str(i)
            if not isinstance(entry, dict) or not nonempty(entry.get("id")):
                issue("INVALID_RECORD_ID", path, "object with nonempty string id", entry)
                continue
            if entry["id"] in index:
                issue("DUPLICATE_ID", path + "/id", "unique ID within collection", entry["id"])
            else:
                index[entry["id"]] = entry
        records[collection] = index
    sources, nodes, edges = records["sources"], records["nodes"], records["relations"]
    for sid, source in sources.items():
        for field in ("text", "locator"):
            if not nonempty(source.get(field)):
                issue("SOURCE_FIELD_REQUIRED", "/sources/" + sid + "/" + field, "nonempty string", source.get(field), sid)
    def provenance(record, path, minimum=1):
        ids = record.get("source_ids")
        if not string_list(ids):
            issue("PROVENANCE_TYPE", path + "/source_ids", "array of source IDs", ids, record["id"], record.get("type"))
        elif len(set(ids)) < minimum or len(ids) != len(set(ids)) or not set(ids) <= set(sources):
            issue("PROVENANCE_SCOPE", path + "/source_ids", {"minimum_distinct": minimum, "known_sources": sorted(sources)}, ids, record["id"], record.get("type"))
    for nid, node in nodes.items():
        path, kind = "/nodes/" + nid, node.get("type")
        if set(node) - NODE_KEYS:
            issue("UNKNOWN_NODE_FIELD", path, sorted(NODE_KEYS), sorted(set(node) - NODE_KEYS), nid, kind)
        for field in ("label", "definition"):
            if not nonempty(node.get(field)):
                issue("MISSING_REQUIRED_FIELD", path + "/" + field, "nonempty string", node.get(field), nid, kind)
        if not isinstance(kind, str) or kind not in contract["types"]:
            issue("UNDECLARED_TYPE", path + "/type", sorted(contract["types"]), kind, nid, kind)
            provenance(node, path)
            continue
        profile = contract["types"][kind]
        provenance(node, path, profile.get("min_sources", 1))
        aliases = node.get("aliases", [])
        if not string_list(aliases):
            issue("ALIASES_TYPE", path + "/aliases", "array of nonempty strings", aliases, nid, kind)
        attrs = node.get("attributes", {})
        if not isinstance(attrs, dict):
            issue("ATTRIBUTES_TYPE", path + "/attributes", "object", attrs, nid, kind)
            continue
        specs = profile.get("attributes", {})
        for field in profile.get("required_attributes", []):
            if field not in attrs:
                issue("MISSING_ATTRIBUTE", path + "/attributes/" + field, specs[field], None, nid, kind)
        for field, value in attrs.items():
            if field not in specs:
                if profile.get("closed_attributes", False):
                    issue("UNKNOWN_ATTRIBUTE", path + "/attributes/" + field, sorted(specs), value, nid, kind)
                continue
            spec, apath = specs[field], path + "/attributes/" + field
            if not matches(value, spec["type"]):
                issue("ATTRIBUTE_TYPE", apath, spec["type"], value, nid, kind)
                continue
            if "enum" in spec and not any(exact_json_equal(value, v) for v in spec["enum"]):
                issue("ATTRIBUTE_ENUM", apath, spec["enum"], value, nid, kind)
            if "min_length" in spec and len(value) < spec["min_length"] or "max_length" in spec and len(value) > spec["max_length"]:
                issue("ATTRIBUTE_LENGTH", apath, spec, value, nid, kind)
            if "minimum" in spec and value < spec["minimum"] or "maximum" in spec and value > spec["maximum"]:
                issue("ATTRIBUTE_RANGE", apath, spec, value, nid, kind)
            if "items_type" in spec and not all(matches(x, spec["items_type"]) for x in value):
                issue("ATTRIBUTE_ITEMS_TYPE", apath, spec["items_type"], value, nid, kind)
    edge_index, outgoing = {}, defaultdict(lambda: defaultdict(set))
    usable = []
    for rid, edge in edges.items():
        path, predicate = "/relations/" + rid, edge.get("type")
        if set(edge) - EDGE_KEYS:
            issue("UNKNOWN_RELATION_FIELD", path, sorted(EDGE_KEYS), sorted(set(edge) - EDGE_KEYS), rid, predicate)
        if not isinstance(predicate, str) or predicate not in contract["relations"]:
            issue("UNDECLARED_RELATION", path + "/type", sorted(contract["relations"]), predicate, rid, predicate)
            continue
        rule = contract["relations"][predicate]
        provenance(edge, path)
        left, right = edge.get("from"), edge.get("to")
        if not nonempty(left) or not nonempty(right) or left not in nodes or right not in nodes:
            issue("DANGLING_REFERENCE", path, "two declared node IDs", [left, right], rid, predicate)
            continue
        usable.append(edge)
        if nodes[left].get("type") not in rule["from_types"] or nodes[right].get("type") not in rule["to_types"]:
            issue("RELATION_TYPE_MISMATCH", path, {"from_types": rule["from_types"], "to_types": rule["to_types"]}, [nodes[left].get("type"), nodes[right].get("type")], rid, predicate)
        review = edge.get("review", {})
        if rule.get("review_required") and (not isinstance(review, dict) or review.get("decision") != "accepted" or not nonempty(review.get("reviewer")) or not nonempty(review.get("rationale"))):
            issue("REVIEW_REQUIRED", path + "/review", "accepted review with reviewer and rationale", review, rid, predicate)
        pair = tuple(sorted((left, right))) if rule.get("symmetric") else (left, right)
        key = (predicate, pair)
        if key in edge_index:
            issue("REDUNDANT_RELATION", path, "one assertion per identical predicate and endpoint pair", [edge_index[key]["id"], rid], rid, predicate, "warning")
        edge_index[key] = edge
        outgoing[left][predicate].add(right)
    for predicate, rule in contract["relations"].items():
        graph = adjacency(usable, predicate)
        witness = cycle_witness(graph) if rule.get("acyclic") else None
        if witness:
            issue("CYCLE_FORBIDDEN", "/relations/" + predicate, "DAG for this declared predicate", witness, node_type=predicate)
        for edge in (x for x in usable if x["type"] == predicate):
            for other in rule.get("exclusive_with", []):
                pairs = {(edge["from"], edge["to"])}
                if rule.get("symmetric") or contract["relations"][other].get("symmetric"):
                    pairs.add((edge["to"], edge["from"]))
                if contract["relations"][other].get("symmetric"):
                    pairs = {tuple(sorted(pair)) for pair in pairs}
                if any((other, pair) in edge_index for pair in pairs):
                    issue("INCOMPATIBLE_RELATION", "/relations/" + edge["id"], "mutually exclusive predicates cannot hold for the same pair", [predicate, other], edge["id"], predicate)
    for nid, node in nodes.items():
        profile = contract["types"].get(node.get("type"), {}) if isinstance(node.get("type"), str) else {}
        for predicate, bounds in profile.get("outgoing", {}).items():
            count = len(outgoing[nid][predicate])
            if count < bounds.get("min", 0) or count > bounds.get("max", math.inf):
                issue("CARDINALITY_VIOLATION", "/nodes/" + nid + "/outgoing/" + predicate, bounds, count, nid, node.get("type"))
    bindings = model.get("bindings", {})
    if not isinstance(bindings, dict):
        issue("BINDINGS_TYPE", "/bindings", "source ID to node-ID array", bindings)
        bindings = {}
    for sid, targets in bindings.items():
        if sid not in sources or not string_list(targets) or not targets or not set(targets) <= set(nodes):
            issue("INVALID_BINDING", "/bindings/" + sid, "known source mapped to one or more existing nodes", targets, sid)
    if contract.get("require_source_bindings", True):
        for sid in sources:
            if not bindings.get(sid):
                issue("SOURCE_UNREPRESENTED", "/bindings/" + sid, "explicit nonempty representation mapping", bindings.get(sid), sid)
    if baseline is not None:
        require(isinstance(baseline, dict), "Baseline must be an object", code="INVALID_BASELINE")
        base_report = validate(baseline, contract)
        require(base_report["contract_status"] == "valid", "Baseline does not conform to the contract", code="INVALID_BASELINE", actual=[e["code"] for e in base_report["errors"]])
        old_sources = baseline.get("sources", [])
        for source in old_sources:
            if source["id"] not in sources:
                issue("SOURCE_LOSS", "/sources/" + source["id"], source, None, source["id"])
            elif not exact_json_equal(source, sources[source["id"]]):
                issue("SOURCE_MUTATION", "/sources/" + source["id"], source, sources[source["id"]], source["id"])
        for key, value in baseline.get("metadata", {}).items():
            metadata = model.get("metadata", {})
            if not isinstance(metadata, dict) or key not in metadata or not exact_json_equal(metadata[key], value):
                issue("METADATA_LOSS", "/metadata/" + key, value, metadata.get(key) if isinstance(metadata, dict) else metadata)
    outcomes = []
    if not errors:
        for test in contract.get("checks", []):
            actual, expected = query_result(model, test["query"]), sorted(set(test["expect"]))
            outcomes.append({"id": test["id"], "passed": actual == expected, "expected": expected, "actual": actual})
            if actual != expected:
                issue("COMPETENCY_CHECK_FAILED", "/checks/" + test["id"], expected, actual)
    if not contract.get("checks"):
        issue("NO_COMPETENCY_TESTS", "/checks", "declare queries before claiming preservation or reducing", [], severity="warning")
    return {"tool": "curate-semantic-model", "version": VERSION, "engine_status": "completed", "contract_status": "invalid" if errors else "valid", "semantic_status": "not_run", "semantic_note": "Checks validate declared structure, provenance and query answers. They do not determine semantic identity or truth; declared reviews are not independently verified.", "contract": {"id": contract["id"], "version": contract["version"]}, "errors": errors, "warnings": warnings, "competency_checks": outcomes, "counts": {"sources": len(sources), "nodes": len(nodes), "relations": len(edges), "bound_sources": sum(bool(v) for v in bindings.values()), "used_node_types": len({n.get("type") for n in nodes.values() if isinstance(n.get("type"), str)})}}


def stage(base, addition, contract):
    initial = validate(base, contract)
    if initial["contract_status"] != "valid":
        initial["phase"] = "baseline"
        return None, initial
    unknown(addition, {"sources", "nodes", "relations", "bindings"}, "/addition")
    candidate = copy.deepcopy(base)
    for field in ("sources", "nodes", "relations"):
        require(isinstance(addition.get(field, []), list), "Addition collections must be arrays", "/addition/" + field, "INVALID_ADDITION")
        candidate[field].extend(copy.deepcopy(addition.get(field, [])))
    require(isinstance(addition.get("bindings", {}), dict), "Addition bindings must be an object", code="INVALID_ADDITION")
    for sid, targets in addition.get("bindings", {}).items():
        require(string_list(targets), "Addition bindings must contain ID arrays", code="INVALID_ADDITION")
        candidate.setdefault("bindings", {})[sid] = sorted(set(candidate.get("bindings", {}).get(sid, [])) | set(targets))
    report = validate(candidate, contract, base)
    report["phase"] = "candidate"
    return (candidate if report["contract_status"] == "valid" else None), report


def reduce_model(model, contract):
    report = validate(model, contract)
    if report["contract_status"] != "valid":
        return None, report
    require(bool(contract.get("checks")), "Reduction requires explicit competency tests", "/checks", "PRESERVATION_NOT_SPECIFIED")
    candidate, operations, skipped = copy.deepcopy(model), [], []
    seen = {}
    for edge in list(candidate["relations"]):
        # ID and provenance are retained in history; all other fields must agree.
        key = json.dumps({k: v for k, v in edge.items() if k not in ("id", "source_ids")}, sort_keys=True)
        if key in seen:
            keeper = seen[key]
            keeper["source_ids"] = sorted(set(keeper["source_ids"]) | set(edge["source_ids"]))
            candidate["relations"].remove(edge)
            operations.append({"operation": "deduplicate_relation", "retained_id": keeper["id"], "original_assertion": copy.deepcopy(edge)})
        else:
            seen[key] = edge
    for edge in sorted(list(candidate["relations"]), key=lambda x: x["id"]):
        if not contract["relations"][edge["type"]].get("reduce_closure"):
            continue
        index = candidate["relations"].index(edge)
        candidate["relations"].pop(index)
        proof = path_between(adjacency(candidate["relations"], edge["type"]), edge["from"], edge["to"])
        check = validate(candidate, contract, model) if proof else None
        if proof and check["contract_status"] == "valid":
            operations.append({"operation": "remove_derived_relation", "proof_path": proof, "original_assertion": copy.deepcopy(edge)})
        else:
            candidate["relations"].insert(index, edge)
            if proof:
                skipped.append({"relation_id": edge["id"], "reason": "would change declared contract or competency answers", "error_codes": sorted({e["code"] for e in check["errors"]})})
    candidate.setdefault("history", []).extend(operations)
    final = validate(candidate, contract, model)
    final["reduction"] = {"before": report["counts"], "after": final["counts"], "operations": operations, "skipped": skipped, "global_optimum_proved": False, "scope": "Heuristic local reduction of duplicate assertions and explicitly permitted transitive closure materialization. Nodes and source records are never merged or deleted. Full removed assertions remain in history; total archive bytes can increase."}
    return (candidate if final["contract_status"] == "valid" else None), final


def write_new(filename, value, forbidden, *, sort_keys=False):
    output = Path(filename).resolve()
    require(not aliases_input(output, forbidden), "An output cannot overwrite an input", str(output), "INPUT_OVERWRITE_FORBIDDEN")
    try:
        serialized = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, sort_keys=sort_keys) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise EngineError("OUTPUT_SERIALIZATION_ERROR", str(exc), str(output)) from exc
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("xb") as stream:
            stream.write(serialized)
    except OSError as exc:
        raise EngineError("OUTPUT_ERROR", str(exc), str(output)) from exc


def aliases_input(filename, forbidden):
    """Resolve textual paths and existing hard links before any write."""
    target = Path(filename).resolve()
    for source in forbidden:
        if target == source:
            return True
        try:
            if os.path.samefile(target, source):
                return True
        except (FileNotFoundError, OSError):
            pass
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "stage", "reduce"):
        command = sub.add_parser(name)
        command.add_argument("--contract", required=True)
        command.add_argument("--model" if name != "stage" else "--base", required=True)
        command.add_argument("--report")
        if name == "validate":
            command.add_argument("--baseline")
        else:
            command.add_argument("--candidate", required=True)
        if name == "stage":
            command.add_argument("--addition", required=True)
    args = parser.parse_args(argv)
    forbidden = {Path(v).resolve() for k, v in vars(args).items() if k in ("model", "base", "baseline", "contract", "addition") and v}
    report_forbidden = forbidden | ({Path(args.candidate).resolve()} if args.command != "validate" else set())
    try:
        require(not args.report or not aliases_input(args.report, report_forbidden), "A report cannot overwrite an input or candidate", code="INPUT_OVERWRITE_FORBIDDEN")
        if args.command != "validate":
            require(not aliases_input(args.candidate, forbidden) and (not args.report or not aliases_input(args.candidate, {Path(args.report).resolve()})), "Candidate output collides with an input or report", code="INPUT_OVERWRITE_FORBIDDEN")
        contract = read_json(args.contract)
        model = read_json(args.base if args.command == "stage" else args.model)
        if args.command == "validate":
            report = validate(model, contract, read_json(args.baseline) if args.baseline else None)
        elif args.command == "stage":
            candidate, report = stage(model, read_json(args.addition), contract)
        else:
            candidate, report = reduce_model(model, contract)
        exit_code = 0 if report["contract_status"] == "valid" else 1
        if args.command != "validate" and candidate is not None:
            write_new(args.candidate, candidate, forbidden)
            report["candidate_path"] = str(Path(args.candidate).resolve())
            report["accepted_model_modified"] = False
    except EngineError as exc:
        report = {"tool": "curate-semantic-model", "version": VERSION, "engine_status": "error", "contract_status": None, "semantic_status": "not_run", "errors": [{"code": exc.code, "path": exc.path, "message": str(exc), "actual": exc.actual, "severity": "error"}], "warnings": []}
        exit_code = 2
    if args.report:
        # Reports may be refreshed, but input and candidate paths are protected.
        try:
            require(not aliases_input(args.report, report_forbidden), "A report cannot overwrite an input or candidate", code="INPUT_OVERWRITE_FORBIDDEN")
            Path(args.report).parent.mkdir(parents=True, exist_ok=True)
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        except (EngineError, OSError) as exc:
            print(json.dumps({"engine_status": "error", "contract_status": None, "semantic_status": "not_run", "errors": [{"code": exc.code if isinstance(exc, EngineError) else "REPORT_WRITE_ERROR", "message": str(exc)}]}))
            return 2
    print(json.dumps(report, ensure_ascii=False, allow_nan=False))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
