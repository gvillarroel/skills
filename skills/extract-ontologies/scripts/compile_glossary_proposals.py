#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compile exact source spans into a review-only glossary proposal ledger."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import re
from unicodedata import category

TOKEN = re.compile(r"\w+(?:[-’']\w+)*|[^\w\s]", re.UNICODE)
KINDS = ("definition", "alias", "attestation")
LANES = ("entity", "predicate", "unspecified")


def unique_fields(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def token_ranges(text):
    # Match on base characters and map each token back to the exact source.
    base, offsets = [], []
    for index, char in enumerate(text):
        if category(char).startswith("M") and base and not base[-1].isspace():
            continue
        base.append(char)
        offsets.append(index)
    offsets.append(len(text))
    return [(offsets[token.start()], offsets[token.end()])
            for token in TOKEN.finditer("".join(base))]


def locate(fragment, citation, starts, ends, offset, field):
    if (not isinstance(fragment, dict) or "quote" not in fragment
            or not fragment.keys() <= {"quote", "first_char", "prefix", "suffix"}):
        raise ValueError(f"{field} needs a quote and may include first_char, prefix or suffix")
    quote = fragment["quote"]
    if not isinstance(quote, str) or not re.search(r"\w", quote):
        raise ValueError(f"{field} needs nonblank lexical text")
    first = fragment.get("first_char")
    if "first_char" in fragment and (type(first) is not int or first not in starts):
        raise ValueError(f"{field} first_char must be an in-bounds token start")
    for side in ("prefix", "suffix"):
        if side in fragment and (not isinstance(fragment[side], str) or not fragment[side]):
            raise ValueError(f"{field} {side} must be nonempty exact text")
    prefix, suffix = fragment.get("prefix", ""), fragment.get("suffix", "")
    candidates = (first,) if first is not None else sorted(starts)
    locations = [start for start in candidates
                 if start + len(quote) in ends and citation.startswith(quote, start)
                 and start >= len(prefix) and citation.startswith(prefix, start - len(prefix))
                 and citation.startswith(suffix, start + len(quote))]
    if len(locations) != 1:
        raise ValueError(f"{field} must locate one exact token-aligned occurrence")
    start = offset + locations[0]
    return {"quote": quote, "start": start, "end": start + len(quote)}


def compile_row(row, lines, offsets):
    if not isinstance(row, dict) or row.keys() != {"kind", "lane", "term", "value", "evidence"}:
        raise ValueError("A proposal needs kind, lane, term, value and evidence")
    kind, lane, evidence = row["kind"], row["lane"], row["evidence"]
    if kind not in KINDS or lane not in LANES:
        raise ValueError("Unknown proposal kind or vocabulary lane")
    if not isinstance(evidence, dict) or evidence.keys() != {"start_line", "end_line"}:
        raise ValueError("Evidence needs start_line and end_line")
    first, last = evidence["start_line"], evidence["end_line"]
    if not (type(first) is int and type(last) is int and 1 <= first <= last <= len(lines) and last - first <= 10):
        raise ValueError("Evidence must span one to eleven in-bounds lines")
    quote = "\n".join(lines[first - 1:last])
    tokens = token_ranges(quote)
    starts, ends = {start for start, _ in tokens}, {end for _, end in tokens}
    term = locate(row["term"], quote, starts, ends, offsets[first - 1], "term")
    value = row["value"]
    if kind == "attestation":
        if value is not None:
            raise ValueError("An attestation needs a null value")
    else:
        value = locate(value, quote, starts, ends, offsets[first - 1], "value")
        if term["start"] < value["end"] and value["start"] < term["end"]:
            raise ValueError("The term and value spans must be separate")
    return {"kind": kind, "lane": lane, "term": term, "value": value,
            "evidence": evidence | {"quote": quote}, "status": "candidate"}


def proposal_order(row):
    term, value = row["term"], row["value"]
    return (term["start"], term["end"], row["kind"], row["lane"],
            value["start"] if value else -1, value["end"] if value else -1)


def compile_ledger(source_bytes, draft):
    source_sha256 = sha256(source_bytes).hexdigest()
    if (not isinstance(draft, dict) or draft.keys() != {"source_sha256", "proposals"}
            or not isinstance(draft["proposals"], list)):
        raise ValueError("Draft needs source_sha256 and a proposals array")
    if draft["source_sha256"] != source_sha256:
        raise ValueError("Draft source digest does not match the original bytes")
    text = source_bytes.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if "\x00" in text:
        raise ValueError("Source must be UTF-8 text without NUL")
    lines = text.removesuffix("\n").split("\n") if text else []
    offsets, offset = [], 0
    for line in lines:
        offsets.append(offset)
        offset += len(line) + 1
    entries = []
    seen = set()
    for index, row in enumerate(draft["proposals"]):
        try:
            entry = compile_row(row, lines, offsets)
        except ValueError as error:
            raise ValueError(f"Proposal {index}: {error}") from error
        key = proposal_order(entry)
        if key in seen:
            raise ValueError(f"Proposal {index}: duplicate source-bound proposal")
        seen.add(key)
        entries.append(entry)
    return {"source_sha256": source_sha256, "proposals": sorted(entries, key=proposal_order)}


def main(argv=None):
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--draft", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        raw_draft = args.draft.read_bytes()
        draft = json.loads(raw_draft.decode("utf-8-sig"), object_pairs_hook=unique_fields)
        result = compile_ledger(args.source.read_bytes(), draft)
        result["draft_sha256"] = sha256(raw_draft).hexdigest()
        raw_output = (json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
        with args.output.open("xb") as stream:
            stream.write(raw_output)
    except (OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 2
    print(json.dumps({"status": "compiled", "proposals": len(result["proposals"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
