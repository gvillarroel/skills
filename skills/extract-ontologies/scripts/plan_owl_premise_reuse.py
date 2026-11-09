#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Plan reuse of reviewed ontology premises under versioned authority dependencies."""

from argparse import ArgumentParser
from collections import deque
from hashlib import sha256
import json
from pathlib import Path
import re

ID = re.compile(r"p[0-9]{2,4}")
SELECTOR = re.compile(r"[a-z][a-z0-9-]{0,63}")
SHA256 = re.compile(r"[a-f0-9]{64}")
MAX_READS = 512


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def fingerprint(value):
    return sha256(canonical(value)).hexdigest()


def text_hash(value):
    return sha256(value.encode("utf-8")).hexdigest()


def source_parts(source):
    if type(source) is not dict or set(source) != {"id", "namespace", "ontology_iri", "scope", "segments"}:
        raise ValueError("expected a versioned ontology source packet")
    if any(type(source[key]) is not str or not source[key].strip()
           for key in ("id", "namespace", "ontology_iri", "scope")):
        raise ValueError("source identity, namespace and projection must be nonblank text")
    segments = source["segments"]
    if type(segments) is not list or not 1 <= len(segments) <= 5000:
        raise ValueError("invalid source segment roster")
    texts = {}
    for item in segments:
        if (type(item) is not dict or set(item) != {"id", "text"} or type(item["id"]) is not str
                or type(item["text"]) is not str or not item["text"].strip() or item["id"] in texts):
            raise ValueError("invalid or duplicate source segment")
        texts[item["id"]] = text_hash(item["text"])
    if next(iter(texts)) != "term-registry" or any(not ID.fullmatch(pid) for pid in list(texts)[1:]):
        raise ValueError("expected term registry followed by numbered premises")
    profile = {key: source[key] for key in ("namespace", "ontology_iri", "scope")}
    profile["term_registry_sha256"] = texts.pop("term-registry")
    return texts, profile


def roster(value, key, matcher):
    items = value[key]
    if type(items) is not list or any(type(item) is not str or not matcher.fullmatch(item) for item in items):
        raise ValueError(f"malformed {key} roster")
    if len(set(items)) != len(items):
        raise ValueError(f"duplicate IDs in {key}")
    return tuple(sorted(items))


def review_side(value, texts):
    if type(value) is not dict or set(value) != {"rows", "selectors"}:
        raise ValueError("expected row and selector reviews")
    if type(value["rows"]) is not dict or type(value["selectors"]) is not dict:
        raise ValueError("row and selector reviews must be objects")
    rows, selectors = {}, {}
    for key, record in value["rows"].items():
        if (key not in texts or type(record) is not dict or set(record) != {"complete", "reads", "watches"}
                or type(record["complete"]) is not bool):
            raise ValueError("invalid reviewed row")
        rows[key] = {"complete": record["complete"], "reads": roster(record, "reads", ID),
                     "watches": roster(record, "watches", SELECTOR)}
    for key, record in value["selectors"].items():
        if (not SELECTOR.fullmatch(key) or type(record) is not dict or set(record) != {"complete", "members"}
                or type(record["complete"]) is not bool):
            raise ValueError("invalid reviewed selector")
        selectors[key] = {"complete": record["complete"], "members": roster(record, "members", ID)}
    return rows, selectors


def trace(pid, texts, reviewed, positions):
    rows, selectors = reviewed
    pending, queued, effects, missing = deque([pid]), {pid}, {}, set()

    def schedule(ids):
        for identifier in ids:
            if identifier not in queued:
                queued.add(identifier)
                pending.append(identifier)
    selector_effects = {}
    while pending:
        reader = pending.popleft()
        if len(effects) >= MAX_READS:
            missing.add("closure-budget-exceeded")
            break
        if reader not in texts:
            missing.add(f"missing-source:{reader}")
            continue
        row = rows.get(reader)
        if row is None or not row["complete"]:
            missing.add(f"incomplete-row:{reader}")
            continue
        reads = row["reads"]
        absent = set(reads) - texts.keys()
        missing.update(f"missing-source:{ref}" for ref in absent)
        record = {"own": texts[reader], "reads": {ref: texts[ref] for ref in reads if ref in texts}}
        schedule(reads)
        record["watch"] = list(row["watches"])
        for selector in row["watches"]:
            if selector in selector_effects:
                continue
            reviewed_selector = selectors.get(selector)
            if reviewed_selector is None or not reviewed_selector["complete"]:
                missing.add(f"incomplete-selector:{selector}")
                continue
            members = reviewed_selector["members"]
            for member in set(members) - texts.keys():
                missing.add(f"missing-selector-member:{selector}/{member}")
            selector_effects[selector] = sorted(
                (ref for ref in members if ref in texts), key=positions.__getitem__)
            schedule(members)
        effects[reader] = record
    evidence_names = set(effects).union(*(data["reads"] for data in effects.values()))
    order = sorted(evidence_names, key=positions.__getitem__)
    return {"rows": effects, "selectors": selector_effects, "order": order}, sorted(missing)


def compare(before, after, review, approved, *, profile_changed):
    old, old_profile = source_parts(before)
    new, new_profile = source_parts(after)
    if before["id"] != after["id"]:
        raise ValueError("source packets belong to different version lineages")
    if type(review) is not dict or set(review) != {"before", "after"}:
        raise ValueError("expected two reviewed dependency snapshots")
    old_review = review_side(review["before"], old)
    new_review = review_side(review["after"], new)
    old_order = {pid: index for index, pid in enumerate(old)}
    new_order = {pid: index for index, pid in enumerate(new)}
    changed_profile = sorted(key for key in old_profile if old_profile[key] != new_profile[key])
    if profile_changed:
        changed_profile.append("authoring_profile")
    approved_rows = ledger_rows(approved, old)
    output = {}
    for pid in new:
        decision = {"action": "recompute", "reason": None}
        if pid not in old:
            decision["reason"] = "new-premise"
        elif old[pid] != new[pid]:
            decision["reason"] = "premise-bytes-edited"
        elif approved_rows[pid]["gap"] is not None:
            decision["reason"] = "approved-ledger-row-unresolved"
        elif changed_profile:
            decision["reason"] = "projection-or-vocabulary-edited"
        else:
            prior, earlier_gaps = trace(pid, old, old_review, old_order)
            current, current_gaps = trace(pid, new, new_review, new_order)
            decision["trace"] = {"before_sha256": fingerprint(prior), "after_sha256": fingerprint(current),
                                 "before_gaps": earlier_gaps, "after_gaps": current_gaps}
            if earlier_gaps or current_gaps:
                decision["reason"] = "incomplete-dependency-review"
            elif prior == current:
                decision.update(action="reuse", reason="reviewed-dependencies-identical")
            else:
                decision["reason"] = "dependency-or-selector-edited"
                decision["changed_reads"] = sorted(
                    name for name in prior["rows"].keys() | current["rows"].keys()
                    if prior["rows"].get(name) != current["rows"].get(name))
                decision["changed_selectors"] = sorted(
                    name for name in prior["selectors"].keys() | current["selectors"].keys()
                    if prior["selectors"].get(name) != current["selectors"].get(name))
                decision["order_changed"] = prior["order"] != current["order"]
        output[pid] = decision
    return {"mode": "reviewed-dependency-closure", "before": fingerprint(before), "after": fingerprint(after),
            "dependency_review": fingerprint(review),
            "changed_profile": changed_profile, "removed_premises": sorted(old.keys() - new.keys()),
            "decisions": output}


def ledger_rows(value, source_ids):
    if type(value) is not dict or set(value) != {"premises"} or type(value["premises"]) is not list:
        raise ValueError("expected a numbered premise ledger")
    output = {}
    for row in value["premises"]:
        if (type(row) is not dict or set(row) != {"id", "axioms", "gap"}
                or type(row["id"]) is not str or row["id"] not in source_ids or row["id"] in output
                or type(row["axioms"]) is not list
                or any(type(axiom) is not str or not axiom.strip() for axiom in row["axioms"])
                or (row["gap"] is not None and (type(row["gap"]) is not str or not row["gap"].strip()
                                               or row["axioms"]))):
            raise ValueError("invalid prior premise ledger row")
        output[row["id"]] = row
    if set(output) != set(source_ids):
        raise ValueError("prior ledger roster differs from the prior source")
    return output


def no_duplicates(items):
    value = dict(items)
    if len(items) != len(value):
        raise ValueError("duplicate JSON object key")
    return value


def no_constant(token):
    raise ValueError(f"invalid JSON constant {token}")


def read_packet(path):
    with path.open("rb") as stream:
        raw = stream.read(4_000_001)
    if len(raw) > 4_000_000:
        raise ValueError("input exceeds the source byte budget")
    value = json.loads(raw, object_pairs_hook=no_duplicates, parse_constant=no_constant)
    return value, sha256(raw).hexdigest()


def plan(before_path, after_path, approved_path, review_path):
    before, before_hash = read_packet(before_path)
    after, after_hash = read_packet(after_path)
    approved, approved_hash = read_packet(approved_path)
    review, review_hash = read_packet(review_path)
    pins = {"before_source_sha256": before_hash, "after_source_sha256": after_hash,
            "approved_ledger_sha256": approved_hash}
    fields = set(pins) | {"before_profile_sha256", "after_profile_sha256", "dependencies"}
    if type(review) is not dict or set(review) != fields:
        raise ValueError("expected pinned prior, current and approved-ledger review inputs")
    if any(review[field] != value for field, value in pins.items()):
        raise ValueError("review does not pin the exact source and approved ledger bytes")
    profile = [review[field] for field in ("before_profile_sha256", "after_profile_sha256")]
    if any(type(value) is not str or not SHA256.fullmatch(value) for value in profile):
        raise ValueError("authoring profiles require SHA-256 digests")
    result = compare(before, after, review["dependencies"], approved,
                     profile_changed=profile[0] != profile[1])
    result["input_pins"] = {**pins, "review_sha256": review_hash,
                            "before_profile_sha256": profile[0], "after_profile_sha256": profile[1]}
    return result


def main(argv=None):
    cli = ArgumentParser(description=__doc__)
    for name in ("before", "after", "approved-ledger", "review", "output"):
        cli.add_argument(f"--{name}", type=Path, required=True)
    args = cli.parse_args(argv)
    try:
        result = plan(args.before, args.after, args.approved_ledger, args.review)
        raw = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        with args.output.open("xb") as stream:
            stream.write(raw)
    except (OSError, ValueError, RecursionError) as exc:
        cli.exit(2, f"Reuse plan failed: {exc}\n")


if __name__ == "__main__":
    main()
