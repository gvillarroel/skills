#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare source-bound, human-reviewed propositional rule sets."""
from itertools import product
from hashlib import sha256
import json
import re

from semantic_model import require
from typed_snapshot_delta import SHA256, validate_citation


ATOM_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}")
MODES = {"if", "only-if", "iff", "unless", "plain"}
OPS = {"and", "or", "not"}
MAX_ATOMS = 10
MAX_RULES = 20
MAX_DEPTH = 12


def expression_atoms(expression, atoms, path, depth=0):
    require(depth <= MAX_DEPTH, "Boolean expression depth limit exceeded", path, "INVALID_BOOLEAN_PAIR")
    if isinstance(expression, str):
        require(expression in atoms, "Expression atom is absent from reviewed atoms", path, "INVALID_BOOLEAN_PAIR")
        return {expression}
    require(isinstance(expression, list) and len(expression) >= 2
            and isinstance(expression[0], str) and expression[0] in OPS,
            "Expression must be an atom or [and|or|not, ...]", path, "INVALID_BOOLEAN_PAIR")
    op, *children = expression
    require((op == "not" and len(children) == 1)
            or (op in {"and", "or"} and 2 <= len(children) <= MAX_ATOMS),
            "Invalid Boolean operator arity", path, "INVALID_BOOLEAN_PAIR")
    used = set()
    for index, child in enumerate(children):
        used.update(expression_atoms(child, atoms, f"{path}/{index + 1}", depth + 1))
    return used


def rule_atoms(rule, atoms, path):
    require(isinstance(rule, list) and len(rule) == 3,
            "Rule must be [mode, outcome, guard]", path, "INVALID_BOOLEAN_PAIR")
    mode, outcome, guard = rule
    require(isinstance(mode, str) and mode in MODES and ((mode == "plain") == (guard is None)),
            "Invalid rule mode or guard", path, "INVALID_BOOLEAN_PAIR")
    used = expression_atoms(outcome, atoms, path + "/1")
    if guard is not None:
        used.update(expression_atoms(guard, atoms, path + "/2"))
    return used


def evaluate(expression, assignment):
    if isinstance(expression, str):
        return assignment[expression]
    op, *children = expression
    values = [evaluate(child, assignment) for child in children]
    if op == "not":
        return not values[0]
    if op == "and":
        return all(values)
    return any(values)


def evaluate_rule(rule, assignment):
    mode, outcome, guard = rule
    result = evaluate(outcome, assignment)
    if mode == "plain":
        return result
    condition = evaluate(guard, assignment)
    if mode == "iff":
        return result == condition
    if mode == "only-if":
        return not result or condition
    if mode == "unless":
        return result or condition
    return not condition or result


def validate_pair(pair, lines_by_side, source_sha256):
    require(isinstance(pair, dict) and pair.keys() == {"source_sha256", "atoms", "base", "head"},
            "Boolean pair needs source_sha256, atoms, base and head", "/", "INVALID_BOOLEAN_PAIR")
    expected_digests = pair["source_sha256"]
    require(isinstance(expected_digests, dict) and expected_digests.keys() == {"base", "head"},
            "source_sha256 needs base and head digests", "/source_sha256", "INVALID_BOOLEAN_PAIR")
    for side in ("base", "head"):
        digest = expected_digests[side]
        require(isinstance(digest, str) and SHA256.fullmatch(digest),
                "Expected lowercase SHA-256", f"/source_sha256/{side}", "INVALID_BOOLEAN_PAIR")
        require(digest == source_sha256[side], "Rule pair does not bind current source bytes",
                f"/source_sha256/{side}", "BOOLEAN_PAIR_BINDING_MISMATCH")
    atoms = pair["atoms"]
    require(isinstance(atoms, dict) and 1 <= len(atoms) <= MAX_ATOMS
            and all(isinstance(key, str) and ATOM_ID.fullmatch(key)
                    and isinstance(value, str) and value.strip() for key, value in atoms.items()),
            "atoms needs 1 to 10 IDs with nonblank reviewed meanings", "/atoms", "INVALID_BOOLEAN_PAIR")
    for side in ("base", "head"):
        rules = pair[side]
        require(isinstance(rules, list) and 1 <= len(rules) <= MAX_RULES,
                "Each side needs 1 to 20 reviewed rules", f"/{side}", "INVALID_BOOLEAN_PAIR")
        for index, row in enumerate(rules):
            path = f"/{side}/{index}"
            require(isinstance(row, dict) and row.keys() == {"rule", "evidence"},
                    "Rule row needs rule and evidence", path, "INVALID_BOOLEAN_PAIR")
            rule_atoms(row["rule"], atoms, path + "/rule")
            validate_citation(row["evidence"], lines_by_side[side], path + "/evidence")


def truth_fingerprint(atoms, table):
    essential = []
    ignored = 0
    for offset, atom in enumerate(reversed(atoms)):
        bit = 1 << offset
        if any(value != table[index ^ bit] for index, value in enumerate(table)):
            essential.append(atom)
        else:
            ignored |= bit
    essential.reverse()
    # Project away irrelevant variables by setting each one to false.
    bits = "".join("1" if value else "0" for index, value in enumerate(table)
                   if not (index & ignored))
    payload = json.dumps({"essential_atoms": essential, "truth_bits": bits},
                         separators=(",", ":"), sort_keys=True).encode("utf-8")
    return {"essential_atoms": essential, "sha256": sha256(payload).hexdigest()}


def compare_rules(pair, lines_by_side, source_sha256):
    validate_pair(pair, lines_by_side, source_sha256)
    atoms = sorted(pair["atoms"])
    witnesses = {"base_not_head": None, "head_not_base": None, "both": None, "neither": None}
    counts = dict.fromkeys(witnesses, 0)
    truth = {"base": [], "head": []}
    total = 1 << len(atoms)
    for values in product((False, True), repeat=len(atoms)):
        assignment = dict(zip(atoms, values, strict=True))
        base = all(evaluate_rule(row["rule"], assignment) for row in pair["base"])
        head = all(evaluate_rule(row["rule"], assignment) for row in pair["head"])
        truth["base"].append(base)
        truth["head"].append(head)
        key = "both" if base and head else "base_not_head" if base else "head_not_base" if head else "neither"
        counts[key] += 1
        if witnesses[key] is None:
            witnesses[key] = assignment
    base_count = counts["base_not_head"] + counts["both"]
    head_count = counts["head_not_base"] + counts["both"]
    jointly_satisfiable = bool(counts["both"])
    if base_count in {0, total} or head_count in {0, total}:
        classification, status = "hold", "vacuous-or-tautological-rule-set"
    else:
        left, right = bool(counts["base_not_head"]), bool(counts["head_not_base"])
        classification = {(False, False): "same", (False, True): "base-implies-head",
                          (True, False): "head-implies-base", (True, True): "different"}[(left, right)]
        status = "compared"
    return {"status": status, "classification": classification,
            "atom_count": len(atoms), "region_counts": counts,
            "counterexamples": {"base_not_head": witnesses["base_not_head"],
                                "head_not_base": witnesses["head_not_base"]},
            "region_witnesses": {"both": witnesses["both"], "neither": witnesses["neither"]},
            "jointly_satisfiable": jointly_satisfiable,
            "source_sha256": pair["source_sha256"], "atoms": pair["atoms"],
            "reviewed_rules": {side: pair[side] for side in ("base", "head")},
            "fingerprints": {side: truth_fingerprint(atoms, table) for side, table in truth.items()}}
