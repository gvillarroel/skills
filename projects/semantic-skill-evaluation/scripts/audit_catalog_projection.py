#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit explicitly selected catalog fields across a JSON projection boundary."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from decimal import Decimal
from pathlib import Path
import re
import sys

MISSING = object()

class ContractError(ValueError):
    pass

def pairs(rows):
    result = {}
    for key, value in rows:
        if key in result:
            raise ContractError("Duplicate JSON key: " + key)
        result[key] = value
    return result

def decimal_float(text):
    value = float(text)
    if not math.isfinite(value) or Decimal(str(value)) != Decimal(text):
        raise ContractError("JSON decimal cannot roundtrip without precision loss")
    return value

def decode(raw):
    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=pairs,
                      parse_float=decimal_float,
                      parse_constant=lambda _: (_ for _ in ()).throw(ContractError("Nonfinite JSON")))

def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":"))

def fingerprint(value):
    return sha256(encode(value).encode()).hexdigest()

def pointer_parts(text):
    if not isinstance(text, str) or (text and not text.startswith("/")):
        raise ContractError("Expected an RFC 6901 pointer")
    if re.search(r"~(?![01])", text):
        raise ContractError("Invalid JSON pointer escape")
    parts = [] if text == "" else [p.replace("~1", "/").replace("~0", "~") for p in text[1:].split("/")]
    if len(parts) > 50:
        raise ContractError("Pointer nesting exceeds 50")
    return parts

def lookup(value, pointer):
    for part in pointer_parts(pointer):
        if isinstance(value, dict):
            if part not in value:
                return MISSING
            value = value[part]
        elif isinstance(value, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", part):
                raise ContractError("Array pointer needs a canonical nonnegative index")
            index = int(part)
            if index >= len(value):
                return MISSING
            value = value[index]
        else:
            return MISSING
    return value

def normalize(value, mode):
    if mode == "unordered" and value is not None:
        if not isinstance(value, list):
            raise ContractError("An unordered field must be an array or null")
        return sorted(value, key=encode)
    return value

def stable_id(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ContractError("Record identities must be nonblank strings of at most 200 characters")
    return value

def records(document, location, id_path, bindings):
    collection = lookup(document, location)
    if isinstance(collection, dict):
        rows = list(collection.items())
    elif isinstance(collection, list):
        rows = []
        for row in collection:
            if not isinstance(row, dict):
                raise ContractError("Catalog rows must be objects")
            identity = lookup(row, id_path)
            rows.append((stable_id(identity), row))
    else:
        raise ContractError("Record pointer must identify an object or array")
    local_ids = [stable_id(identity) for identity, _ in rows]
    if len(set(local_ids)) != len(local_ids):
        raise ContractError("Duplicate record identity; do not silently deduplicate")
    if bindings is not None:
        if not isinstance(bindings, dict) or set(bindings) != set(local_ids):
            raise ContractError("A supplied identity bridge must cover exactly its record collection")
        for value in bindings.values():
            stable_id(value)
        if len(set(bindings.values())) != len(bindings):
            raise ContractError("Identity bridge would merge distinct records")
    result = {}
    for identity, row in rows:
        if not isinstance(row, dict):
            raise ContractError("Catalog rows must be objects")
        result[bindings[identity] if bindings is not None else identity] = row
    return result

def validate_contract(contract, source_sha256, projected_sha256):
    allowed = {"schema_version", "source_records", "projected_records", "id_path",
               "source_id_path", "projected_id_path",
               "bindings", "fields", "source_sha256", "allow_empty_source"}
    if not isinstance(contract, dict) or set(contract) - allowed:
        raise ContractError("Unsupported contract fields")
    if type(contract.get("schema_version")) is not int or contract["schema_version"] != 1:
        raise ContractError("Expected contract schema_version 1")
    for key in ("source_records", "projected_records"):
        pointer_parts(contract.get(key))
    pointer_parts(contract.get("id_path", "/id"))
    for side in ("source", "projected"):
        if side + "_id_path" in contract:
            pointer_parts(contract[side + "_id_path"])
    expected = contract.get("source_sha256")
    if not isinstance(expected, dict) or set(expected) != {"source", "projected"}:
        raise ContractError("Pin both raw source hashes")
    if expected != {"source": source_sha256, "projected": projected_sha256}:
        raise ContractError("Source bytes do not match the pinned contract")
    fields = contract.get("fields")
    if not isinstance(fields, list) or not fields:
        raise ContractError("Declare at least one field")
    names = set()
    for field in fields:
        if not isinstance(field, dict) or set(field) - {"name", "source", "projected", "mode", "category"}:
            raise ContractError("Invalid field contract")
        name = stable_id(field.get("name"))
        if name in names:
            raise ContractError("Duplicate field name")
        names.add(name)
        pointer_parts(field.get("source"))
        pointer_parts(field.get("projected"))
        if field.get("mode", "ordered") not in {"ordered", "unordered"}:
            raise ContractError("Unknown collection mode")
        if field.get("category", "semantic") not in {"semantic", "review", "provenance"}:
            raise ContractError("Unknown field category")
    bridge = contract.get("bindings", {})
    if not isinstance(bridge, dict) or set(bridge) - {"source", "projected"}:
        raise ContractError("Invalid bridge sides")
    if any(not isinstance(side, dict) for side in bridge.values()):
        raise ContractError("Every supplied identity bridge side must be an object")
    if type(contract.get("allow_empty_source", False)) is not bool:
        raise ContractError("allow_empty_source must be Boolean")

def audit(source_raw, projected_raw, contract_raw):
    source_sha, projected_sha = sha256(source_raw).hexdigest(), sha256(projected_raw).hexdigest()
    source, projected, contract = map(decode, (source_raw, projected_raw, contract_raw))
    validate_contract(contract, source_sha, projected_sha)
    bridge = contract.get("bindings", {})
    source_rows = records(source, contract["source_records"], contract.get("source_id_path", contract.get("id_path", "/id")), bridge.get("source"))
    projected_rows = records(projected, contract["projected_records"], contract.get("projected_id_path", contract.get("id_path", "/id")), bridge.get("projected"))
    if not source_rows and not contract.get("allow_empty_source", False):
        raise ContractError("No authoritative records; preservation is not established")
    field_changes, record_changes, unchecked = [], [], []
    source_view, projected_view = {}, {}
    preserved = 0
    checked = 0
    for identity in sorted(set(source_rows) | set(projected_rows)):
        before, after = source_rows.get(identity, MISSING), projected_rows.get(identity, MISSING)
        if before is MISSING or after is MISSING:
            record_changes.append({"id":identity,"status":"introduced-record" if before is MISSING else "lost-record"})
        if before is not MISSING:
            source_view[identity] = {}
        if after is not MISSING:
            projected_view[identity] = {}
        for field in contract["fields"]:
            old = MISSING if before is MISSING else lookup(before, field["source"])
            new = MISSING if after is MISSING else lookup(after, field["projected"])
            name = field["name"]
            mode = field.get("mode", "ordered")
            if old is not MISSING:
                old = normalize(old, mode)
                source_view[identity][name] = old
                checked += 1
            if new is not MISSING:
                new = normalize(new, mode)
                projected_view[identity][name] = new
            if old is MISSING and new is MISSING:
                unchecked.append({"id":identity,"field":name,"reason":"both-absent"})
                continue
            if old is not MISSING and new is not MISSING and encode(old) == encode(new):
                preserved += 1
                continue
            status = "introduced-field" if old is MISSING else "lost-field" if new is MISSING else "changed-field"
            row = {"id":identity,"field":name,"category":field.get("category","semantic"),"status":status,
                   "source_pointer":field["source"],"projected_pointer":field["projected"]}
            if old is not MISSING: row["before"] = old
            if new is not MISSING: row["after"] = new
            field_changes.append(row)
    if source_rows and checked == 0:
        raise ContractError("None of the declared authoritative fields exist")
    field_changes.sort(key=lambda row:(row["id"],row["field"],row["status"]))
    differences = bool(field_changes or record_changes)
    category_fingerprints = {}
    for category in ("semantic", "review", "provenance"):
        names = sorted(field["name"] for field in contract["fields"] if field.get("category", "semantic") == category)
        if not names:
            category_fingerprints[category] = {"fields": [], "status": "not_selected", "source": None, "projected": None}
            continue
        views = [{identity: {name: row[name] for name in names if name in row}
                  for identity, row in view.items()} for view in (source_view, projected_view)]
        before_hash, after_hash = map(fingerprint, views)
        known = sum(len(row) for row in views[0].values())
        state = "differences" if before_hash != after_hash else "preserved" if known else "not_checked"
        category_fingerprints[category] = {"fields": names, "status": state, "source": before_hash,
                                           "projected": after_hash, "authoritative_fields_checked": known}
    result = {"schema_version":1,"projection_status":"differences" if differences else "preserved",
              "semantic_status":"not_checked","scope":"declared catalog fields",
              "source_sha256":{"source":source_sha,"projected":projected_sha},
              "contract_sha256":sha256(contract_raw).hexdigest(),
              "field_scope":sorted(field["name"] for field in contract["fields"]),
              "counts":{"source_records":len(source_rows),"projected_records":len(projected_rows),
                        "authoritative_fields_checked":checked,"preserved_fields":preserved,
                        "record_changes":len(record_changes),"field_changes":len(field_changes)},
              "field_changes":field_changes,"record_changes":record_changes,"unchecked_fields":unchecked,
              "category_fingerprints":category_fingerprints,
              "fingerprints":{"source_declared_fields":fingerprint(source_view),
                              "projected_declared_fields":fingerprint(projected_view)}}
    return result, int(differences)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source","projected","contract","report"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        inputs = [args.source.resolve(), args.projected.resolve(), args.contract.resolve()]
        if args.report.resolve() in inputs:
            raise ContractError("The report cannot overwrite an input")
        if args.report.exists():
            raise ContractError("The report destination already exists")
        report, code = audit(*(path.read_bytes() for path in inputs))
        with args.report.open("x",encoding="utf-8",newline="\n") as stream:
            stream.write(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n")
        print(encode({"projection_status":report["projection_status"],"semantic_status":"not_checked",**report["counts"]}))
        return code
    except (ContractError, ValueError, OSError, TypeError, KeyError) as error:
        print(encode({"projection_status":"not_checked","engine_status":"error","error":str(error)}),file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
