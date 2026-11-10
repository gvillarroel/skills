#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare reviewed, source-pinned relationships and their qualifiers."""
from collections import defaultdict
from datetime import date
from hashlib import sha256
import json
import re

from semantic_model import require
from typed_snapshot_delta import LOCAL_ID, SHA256, validate_citation, validate_review

INVALID = "INVALID_RELATION_PAIR"
ROLES = {"subject": "entities", "predicate": "predicates", "object": "entities"}
QUALIFIERS = ("polarity", "modality", "time", "scope")
MODALITIES = {"asserted", "required", "recommended", "permitted", "prohibited"}
STABLE_ID = re.compile(r"[^\s\x00-\x1f\x7f\ud800-\udfff]{1,200}")
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def valid_id(value, pattern):
    return isinstance(value, str) and bool(pattern.fullmatch(value))


def checked_date(value, path):
    if value is None:
        return None
    require(valid_id(value, ISO_DATE), "Expected a date in YYYY-MM-DD format or null", path, INVALID)
    try:
        return date.fromisoformat(value)
    except ValueError:
        require(False, "Invalid calendar date", path, INVALID)


def check_qualifiers(value, path):
    require(isinstance(value, dict) and value.keys() == set(QUALIFIERS),
            "Qualifiers need polarity, modality, time and scope", path, INVALID)
    require(value["polarity"] in ("positive", "negative"), "Invalid polarity", f"{path}/polarity", INVALID)
    require(isinstance(value["modality"], str) and value["modality"] in MODALITIES,
            "Invalid modality", f"{path}/modality", INVALID)
    require(value["scope"] is None or valid_id(value["scope"], STABLE_ID),
            "Scope must be a stable ID or null", f"{path}/scope", INVALID)
    time = value["time"]
    if time is None:
        return
    require(isinstance(time, dict) and time.keys() == {"start", "end"},
            "Time needs inclusive start and exclusive end, or null", f"{path}/time", INVALID)
    start = checked_date(time["start"], f"{path}/time/start")
    end = checked_date(time["end"], f"{path}/time/end")
    require((start is not None or end is not None) and (start is None or end is None or start < end),
            "Time must have at least one bound and start before end", f"{path}/time", INVALID)


def check_vocabulary(mapping, lines, path):
    require(isinstance(mapping, dict), "Vocabulary bindings must be an object", path, INVALID)
    for alias, binding in mapping.items():
        location = f"{path}/{alias}"
        require(valid_id(alias, LOCAL_ID) and isinstance(binding, dict) and binding.keys() == {"id", "evidence"}
                and valid_id(binding["id"], STABLE_ID),
                "Binding needs a local ID, a stable ID and exact evidence", location, INVALID)
        validate_citation(binding["evidence"], lines, f"{location}/evidence")


def semantic_key(roles, qualifiers):
    return json.dumps({"roles": roles, "qualifiers": qualifiers},
                      ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def compile_side(side, lines, name):
    path = f"/{name}"
    require(isinstance(side, dict) and side.keys() == {"entities", "predicates", "relations"},
            "Side needs entity bindings, predicate bindings and relations", path, INVALID)
    for lane in ("entities", "predicates"):
        check_vocabulary(side[lane], lines, f"{path}/{lane}")
    require(isinstance(side["relations"], list), "Relations must be an array", f"{path}/relations", INVALID)
    records, indexed, unresolved = [], {}, []
    for index, row in enumerate(side["relations"]):
        location = f"{path}/relations/{index}"
        require(isinstance(row, dict) and row.keys() == {*ROLES, "qualifiers", "evidence"}
                and all(valid_id(row[role], LOCAL_ID) for role in ROLES),
                "Relation needs local role IDs, qualifiers and evidence", location, INVALID)
        check_qualifiers(row["qualifiers"], f"{location}/qualifiers")
        validate_citation(row["evidence"], lines, f"{location}/evidence")
        bindings = {role: side[lane][row[role]] for role, lane in ROLES.items() if row[role] in side[lane]}
        roles = {role: binding["id"] for role, binding in bindings.items()}
        records.append({"local_roles": {role: row[role] for role in ROLES}, "roles": roles,
                        "qualifiers": row["qualifiers"], "evidence": row["evidence"],
                        "binding_evidence": {role: binding["evidence"] for role, binding in bindings.items()}})
        if len(roles) != len(ROLES):
            unresolved.append({"side": name, "index": index, "roles": sorted(ROLES.keys() - roles.keys())})
            continue
        key = semantic_key(roles, row["qualifiers"])
        require(key not in indexed, "Duplicate resolved relation", location, INVALID)
        indexed[key] = index
    return records, indexed, unresolved


def graph_fingerprint(indexed):
    return sha256(b"[" + b",".join(sorted(indexed)) + b"]").hexdigest()


def role_slots(keys, index, records):
    slots = defaultdict(list)
    for key in keys:
        roles = records[index[key]]["roles"]
        slots[tuple(roles[role] for role in ROLES)].append(key)
    return slots


def relation_delta(records, indexes):
    base, head = indexes["base"], indexes["head"]
    removed, added = base.keys() - head.keys(), head.keys() - base.keys()
    previous = role_slots(removed, base, records["base"])
    current = role_slots(added, head, records["head"])
    modified = []
    for slot in sorted(previous.keys() & current.keys()):
        before, after = previous[slot], current[slot]
        if len(before) == len(after) == 1:
            old, new = before[0], after[0]
            removed.remove(old)
            added.remove(new)
            old_qualifiers = records["base"][base[old]]["qualifiers"]
            new_qualifiers = records["head"][head[new]]["qualifiers"]
            modified.append({"before": base[old], "after": head[new],
                             "qualifiers": [field for field in QUALIFIERS if old_qualifiers[field] != new_qualifiers[field]]})
    return {"added": [head[key] for key in sorted(added)],
            "removed": [base[key] for key in sorted(removed)],
            "modified": modified}


def compare_relations(pair, lines, source_sha256):
    required = {"base", "head", "source_sha256"}
    require(isinstance(pair, dict) and required <= pair.keys() <= required | {"review"},
            "Relation pair needs base, head, source digests and optional review", "/", INVALID)
    pins = pair["source_sha256"]
    require(isinstance(pins, dict) and pins.keys() == {"base", "head"},
            "Source digests need base and head", "/source_sha256", INVALID)
    records, indexes, unresolved = {}, {}, []
    for side in ("base", "head"):
        path = f"/source_sha256/{side}"
        require(valid_id(pins[side], SHA256), "Expected a lowercase SHA-256 digest", path, INVALID)
        require(pins[side] == source_sha256[side], "Source digest does not match current bytes", path,
                "RELATION_PAIR_BINDING_MISMATCH")
        records[side], indexes[side], missing = compile_side(pair[side], lines[side], side)
        unresolved.extend(missing)
    result = {"source_sha256": pins, "relations": records, "unresolved": unresolved, "review": pair.get("review")}
    if "review" in pair:
        validate_review(pair["review"], lines)
    if unresolved or "review" in pair:
        return result | {"status": "abstain", "graph_sha256": None, "added": [], "removed": [], "modified": []}
    delta = relation_delta(records, indexes)
    return result | delta | {
        "status": "changed" if any(delta.values()) else "unchanged",
        "graph_sha256": {side: graph_fingerprint(index) for side, index in indexes.items()},
    }
