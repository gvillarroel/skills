#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compile typed observations or compare typed snapshots with exact line evidence."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from semantic_model import EngineError, parse_json_text, exact_json_equal, nonempty, read_json, require, write_new
from typed_snapshot_delta import compare_snapshots
from boolean_rule_pair import check_consequence, compare_rules
from reviewed_relation_delta import compare_relations


def source_path(filename):
    path = Path(filename)
    require(path.is_file(), "Document must be a regular file", str(path), "DOCUMENT_INPUT")
    return path


def source_lines(text, path):
    require("\x00" not in text, "Document must be UTF-8 text without NUL", str(path), "DOCUMENT_INPUT")
    return text.removesuffix("\n").split("\n") if text else []


def read_lines(filename):
    path = source_path(filename)
    return source_lines(path.read_text(encoding="utf-8-sig"), path)


def compare_bound_snapshots(args):
    require(args.snapshot_pair is not None, "Class identity requires --snapshot-pair",
            "/class_identity", "INVALID_CLASS_IDENTITY")
    identity = read_json(args.class_identity, exact_numbers=True)
    pair = Path(args.snapshot_pair).read_bytes()
    paths = {side: source_path(getattr(args, side)) for side in ("base", "head")}
    sources = {side: path.read_bytes() for side, path in paths.items()}
    binding = {"source_sha256": {side: sha256(raw).hexdigest() for side, raw in sources.items()},
               "snapshot_pair_sha256": sha256(pair).hexdigest()}
    lines = {side: source_lines(raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n"), paths[side])
             for side, raw in sources.items()}
    snapshot = parse_json_text(pair.decode("utf-8-sig"), args.snapshot_pair, exact_numbers=True)
    return compare_snapshots(snapshot, lines["base"], lines["head"],
                             class_identity=identity, input_sha256=binding)


def bound_source_lines(args):
    paths = {side: source_path(getattr(args, side)) for side in ("base", "head")}
    sources = {side: path.read_bytes() for side, path in paths.items()}
    digests = {side: sha256(raw).hexdigest() for side, raw in sources.items()}
    lines = {side: source_lines(raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n"),
                               paths[side]) for side, raw in sources.items()}
    return lines, digests


def evaluate_boolean_pair(args, proposal):
    lines, digests = bound_source_lines(args)
    pair = read_json(proposal, exact_numbers=True)
    evaluate = check_consequence if args.boolean_consequence is not None else compare_rules
    return evaluate(pair, lines, digests)


def evaluate_relation_pair(args, proposal):
    lines, digests = bound_source_lines(args)
    raw = Path(proposal).read_bytes()
    pair = parse_json_text(raw.decode("utf-8-sig"), proposal, exact_numbers=True)
    return compare_relations(pair, lines, digests) | {"relation_pair_sha256": sha256(raw).hexdigest()}


def compile_state(state, source, path):
    require(isinstance(state, dict) and state.keys() == {"value", "lines"},
            "State needs only value and lines", path, "INVALID_DRAFT")
    value, ranges = state["value"], state["lines"]
    require(isinstance(ranges, list) and (ranges or value is None),
            "Lines must be an array, with evidence for each present value", path, "INVALID_RANGE")
    for span in ranges:
        require(isinstance(span, list) and len(span) == 2
                and all(type(line) is int for line in span)
                and 1 <= span[0] <= span[1] <= len(source),
                "Evidence needs two inclusive in-bounds line numbers", path, "INVALID_RANGE")
    evidence = []
    previous_end = 0
    for start, end in sorted(ranges):
        require(start > previous_end, "Evidence ranges must not overlap", path, "INVALID_RANGE")
        quote = "\n".join(source[start - 1:end])
        require(bool(quote.strip()), "Evidence must contain source text", path, "INVALID_RANGE")
        evidence.append({"start_line": start, "end_line": end, "quote": quote})
        previous_end = end
    return {"value": value, "evidence": evidence}


def compile_observations(draft, base, head):
    require(isinstance(draft, dict) and draft.keys() == {"observations"}
            and isinstance(draft["observations"], list),
            "Draft needs only an observations array", "/", "INVALID_DRAFT")
    compiled = {}
    for index, row in enumerate(draft["observations"]):
        path = f"/observations/{index}"
        require(isinstance(row, dict) and row.keys() == {"id", "before", "after"},
                "Observation needs only id, before and after", path, "INVALID_DRAFT")
        identifier = row["id"]
        require(nonempty(identifier) and identifier not in compiled,
                "Observation ID must be nonempty and unique", path, "INVALID_DRAFT")
        before = compile_state(row["before"], base, path + "/before")
        after = compile_state(row["after"], head, path + "/after")
        left, right = before["value"], after["value"]
        if exact_json_equal(left, right):
            change = "unchanged"
        elif left is None:
            change = "added"
        elif right is None:
            change = "removed"
        else:
            change = "modified"
        compiled[identifier] = {"id": identifier, "before": before, "after": after, "change": change}
    return {"observations": [compiled[identifier] for identifier in sorted(compiled)]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--draft")
    mode.add_argument("--snapshot-pair")
    mode.add_argument("--relation-pair", help="Compare source-pinned reviewed relations")
    mode.add_argument("--boolean-pair")
    mode.add_argument("--boolean-consequence", help="Check whether base rules entail the head candidate")
    parser.add_argument("--class-identity", help="Reviewed base/head class pairs for snapshot comparison")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    boolean_path = args.boolean_pair if args.boolean_pair is not None else args.boolean_consequence
    try:
        proposal = next(path for path in (boolean_path, args.relation_pair, args.snapshot_pair, args.draft)
                        if path is not None)
        if boolean_path is not None or args.relation_pair is not None:
            require(args.class_identity is None, "--class-identity applies only to --snapshot-pair",
                    "/class_identity", "INVALID_CLASS_IDENTITY")
            evaluate = evaluate_relation_pair if args.relation_pair is not None else evaluate_boolean_pair
            result = evaluate(args, proposal)
        elif args.class_identity is None:
            compile_pair = compare_snapshots if args.snapshot_pair is not None else compile_observations
            result = compile_pair(read_json(proposal, exact_numbers=True), read_lines(args.base), read_lines(args.head))
        else:
            result = compare_bound_snapshots(args)
        inputs = {Path(path).resolve() for path in (args.base, args.head, proposal)}
        if args.class_identity is not None:
            inputs.add(Path(args.class_identity).resolve())
        write_new(args.output, result, inputs, sort_keys=True)
    except EngineError as exc:
        print(json.dumps({"engine_status": "error", "semantic_status": "not_run",
                          "error": {"code": exc.code, "path": exc.path, "message": str(exc)}}))
        return 2
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"engine_status": "error", "semantic_status": "not_run",
                          "error": {"code": "DOCUMENT_INPUT", "message": str(exc)}}))
        return 2
    summary = {"engine_status": "completed", "semantic_status": "not_run"}
    if boolean_path is not None:
        status_key = "boolean_pair_status" if args.boolean_pair is not None else "boolean_consequence_status"
        summary[status_key] = result["status"]
        summary["classification"] = result["classification"]
    elif args.relation_pair is not None:
        summary["relation_status"] = result["status"]
        summary.update({key: len(result[key]) for key in ("added", "removed", "modified", "unresolved")})
    elif args.snapshot_pair is not None:
        summary["snapshot_status"] = result["status"]
        summary.update({key: len(result[key]) for key in ("added", "removed", "modified")})
    else:
        summary["observations"] = len(result["observations"])
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
