#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compute a structural delta between two source-bound typed inventories."""

from collections import defaultdict
import re
import unicodedata

from semantic_model import nonempty, require


ROLE_FIELDS = {
    "classes": ("id",),
    "subclasses": ("child", "parent"),
    "relations": ("subject", "object"),
    "constraints": ("subject", "object"),
}
ROW_FIELDS = {
    "classes": {"id", "label", "evidence"},
    "subclasses": {"child", "parent", "evidence"},
    "relations": {"subject", "predicate", "object", "evidence"},
    "constraints": {"subject", "predicate", "object", "kind", "value", "evidence"},
}
CATEGORICAL = {"required", "forbidden"}
CARDINALITY = {"min-cardinality", "max-cardinality", "exact-cardinality"}
LOCAL_ID = re.compile(r"[A-Za-z][A-Za-z0-9_:\-]{0,99}")
INVALID = "INVALID_SNAPSHOT"
INVALID_CLASS_IDENTITY = "INVALID_CLASS_IDENTITY"
NO_CLASS_IDENTITY = object()
SHA256 = re.compile(r"[0-9a-f]{64}")


def term(value, path):
    require(nonempty(value) and len(value) <= 150,
            "Expected a nonblank name of up to 150 characters", path, INVALID)
    return " ".join(unicodedata.normalize("NFC", value).split())


def validate_citation(evidence, lines, path):
    require(isinstance(evidence, dict) and evidence.keys() == {"start_line", "end_line", "quote"},
            "Citation needs start_line, end_line and quote", path, "INVALID_SNAPSHOT_EVIDENCE")
    start, end = evidence["start_line"], evidence["end_line"]
    require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines)
            and end - start <= 10,
            "Citation needs an inclusive in-bounds span of up to 11 lines",
            path, "INVALID_SNAPSHOT_EVIDENCE")
    quote = "\n".join(lines[start - 1:end])
    require(bool(quote.strip()) and evidence["quote"] == quote,
            "Quote must match the exact nonblank source span", path, "INVALID_SNAPSHOT_EVIDENCE")


def validate_inventory(inventory, lines, path):
    require(isinstance(inventory, dict) and inventory.keys() == ROW_FIELDS.keys(),
            "Snapshot needs classes, subclasses, relations and constraints arrays", path, INVALID)
    for lane, fields in ROW_FIELDS.items():
        rows = inventory[lane]
        require(isinstance(rows, list), "Collection must be an array", f"{path}/{lane}", INVALID)
        for index, row in enumerate(rows):
            location = f"{path}/{lane}/{index}"
            require(isinstance(row, dict) and row.keys() == fields,
                    "Invalid fields for this collection", location, INVALID)
            require(all(isinstance(row[field], str) and LOCAL_ID.fullmatch(row[field])
                        for field in ROLE_FIELDS[lane]),
                    "Invalid local class ID", location, INVALID)
            validate_citation(row["evidence"], lines, f"{location}/evidence")


def class_labels(classes, path):
    labels, seen = {}, set()
    for index, row in enumerate(classes):
        location = f"{path}/classes/{index}"
        identifier = row["id"]
        label = term(row["label"], f"{location}/label")
        require(identifier not in labels, "Duplicate local class ID", location, INVALID)
        require(label not in seen, "Ambiguous repeated class label", location, INVALID)
        labels[identifier] = label
        seen.add(label)
    return labels


def constraint_value(row, path):
    kind, value = row["kind"], row["value"]
    require(isinstance(kind, str) and kind in CATEGORICAL | CARDINALITY,
            "Invalid constraint kind", f"{path}/kind", INVALID)
    if kind in CATEGORICAL:
        require(value is True, "A categorical constraint needs true", f"{path}/value", INVALID)
    else:
        require(type(value) is int and 0 <= value <= 1_000_000,
                "A cardinality needs an integer from 0 through 1000000", f"{path}/value", INVALID)
    return kind, value


def index_snapshot(inventory, lines, path):
    validate_inventory(inventory, lines, path)
    labels = class_labels(inventory["classes"], path)
    indexed = {}
    for lane, roles in ROLE_FIELDS.items():
        for index, row in enumerate(inventory[lane]):
            location = f"{path}/{lane}/{index}"
            require(all(row[role] in labels for role in roles),
                    "Dangling local class ID", location, INVALID)
            key = (lane, *(labels[row[role]] for role in roles))
            if lane in {"relations", "constraints"}:
                key += (term(row["predicate"], f"{location}/predicate"),)
            if lane == "constraints":
                key += constraint_value(row, location)
            require(key not in indexed, "Duplicate typed assertion", location, INVALID)
            indexed[key] = index
    return indexed


def checked_identity_pairs(bridge, input_sha256):
    path = "/class_identity"
    require(isinstance(bridge, dict) and bridge.keys() == {"pairs", "source_sha256", "snapshot_pair_sha256"}
            and isinstance(bridge["pairs"], list)
            and isinstance(bridge["source_sha256"], dict) and bridge["source_sha256"].keys() == {"base", "head"},
            "Class identity bridge needs pairs and digests for both sources and the snapshot pair",
            path, INVALID_CLASS_IDENTITY)
    require(input_sha256 is not None, "Class identity requires observed input digests", path, INVALID_CLASS_IDENTITY)
    bindings = [(f"source_sha256/{side}", bridge["source_sha256"][side], input_sha256["source_sha256"][side])
                for side in ("base", "head")]
    bindings.append(("snapshot_pair_sha256", bridge["snapshot_pair_sha256"], input_sha256["snapshot_pair_sha256"]))
    for name, expected, observed in bindings:
        location = f"{path}/{name}"
        require(isinstance(expected, str) and SHA256.fullmatch(expected),
                "Expected a lowercase SHA-256 digest", location, INVALID_CLASS_IDENTITY)
        require(expected == observed, "Class identity bridge does not bind the current input bytes",
                location, "CLASS_IDENTITY_BINDING_MISMATCH")
    return bridge["pairs"]


def bridged_head_index(base_classes, head_classes, indexed, pairs):
    path = "/class_identity"
    base_labels = class_labels(base_classes, "/base")
    head_labels = class_labels(head_classes, "/head")
    base_terms, head_terms = set(base_labels.values()), set(head_labels.values())
    used_base, used_head, replacement = set(), set(), {}
    for index, pair in enumerate(pairs):
        location = f"{path}/pairs/{index}"
        require(isinstance(pair, dict) and pair.keys() == {"base", "head"},
                "Identity pair needs base and head class IDs", location, INVALID_CLASS_IDENTITY)
        before, after = pair["base"], pair["head"]
        for side, identifier, labels, used in (("base", before, base_labels, used_base),
                                                ("head", after, head_labels, used_head)):
            endpoint = f"{location}/{side}"
            require(isinstance(identifier, str) and identifier in labels,
                    "Identity endpoint must be a class ID in its revision", endpoint, INVALID_CLASS_IDENTITY)
            require(identifier not in used,
                    "Identity endpoint may appear only once per revision", endpoint, INVALID_CLASS_IDENTITY)
            used.add(identifier)
        old, new = base_labels[before], head_labels[after]
        require(old == new or (old not in head_terms and new not in base_terms),
                "Identity pair conflicts with an existing literal class match", location, INVALID_CLASS_IDENTITY)
        replacement[new] = old

    remapped = {}
    for key, index in indexed.items():
        lane = key[0]
        end = 1 + len(ROLE_FIELDS[lane])
        roles = (replacement.get(label, label) for label in key[1:end])
        remapped[(lane, *roles, *key[end:])] = index
    return remapped


def validate_review(review, sources):
    require(isinstance(review, dict) and review.keys() == {"reason", "base", "head"}
            and nonempty(review["reason"]) and len(review["reason"]) <= 600,
            "Review needs a bounded reason and citations from both revisions", "/review", INVALID)
    for side, lines in sources.items():
        path = f"/review/{side}"
        citations = review[side]
        require(isinstance(citations, list) and 1 <= len(citations) <= 3,
                "Review needs one to three citations per revision", path, INVALID)
        for index, citation in enumerate(citations):
            validate_citation(citation, lines, f"{path}/{index}")


def constraint_slots(keys):
    slots = defaultdict(list)
    for key in keys:
        if key[0] == "constraints":
            family = "cardinality" if key[-2] in CARDINALITY else "categorical"
            slots[(*key[:-2], family)].append(key)
    return slots


def compare_snapshots(pair, base, head, *, class_identity=NO_CLASS_IDENTITY, input_sha256=None):
    required = {"base", "head"}
    require(isinstance(pair, dict) and required <= pair.keys() <= required | {"review"},
            "Pair needs base, head and an optional review", "/", INVALID)
    identities = [] if class_identity is NO_CLASS_IDENTITY else checked_identity_pairs(class_identity, input_sha256)
    before = index_snapshot(pair["base"], base, "/base")
    after = index_snapshot(pair["head"], head, "/head")
    if identities:
        after = bridged_head_index(pair["base"]["classes"], pair["head"]["classes"], after, identities)
    review = pair.get("review")
    if review is not None:
        validate_review(review, {"base": base, "head": head})
        return {"status": "abstain", "added": [], "removed": [], "modified": [], "review": review}

    removed, added = before.keys() - after.keys(), after.keys() - before.keys()
    old_slots, new_slots = constraint_slots(removed), constraint_slots(added)
    modified = []
    for slot in sorted(old_slots.keys() & new_slots.keys()):
        old, new = old_slots[slot], new_slots[slot]
        if len(old) == len(new) == 1:
            removed.remove(old[0])
            added.remove(new[0])
            modified.append({"collection": "constraints", "before": before[old[0]], "after": after[new[0]]})
    return {
        "status": "changed" if added or removed or modified else "unchanged",
        "added": [{"collection": key[0], "index": after[key]} for key in sorted(added)],
        "removed": [{"collection": key[0], "index": before[key]} for key in sorted(removed)],
        "modified": modified,
        "review": None,
    }
