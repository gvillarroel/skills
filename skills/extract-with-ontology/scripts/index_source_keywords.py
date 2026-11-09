#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Index literal keyword witnesses inside approved units of a pinned text source."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import re


def keyword_pattern(keywords):
    if (not isinstance(keywords, list) or not keywords
            or any(not isinstance(word, str) or not re.fullmatch(r"\w+(?: \w+)*", word)
                   for word in keywords)
            or len(set(keywords)) != len(keywords)):
        raise ValueError("keywords must be distinct words or single-space-separated phrases")
    alternatives = [r"\s+".join(re.escape(word) for word in phrase.split())
                    for phrase in sorted(keywords, key=lambda phrase: (-len(phrase), phrase))]
    return re.compile(r"(?<!\w)(?:" + "|".join(alternatives) + r")(?!\w)")


def index(raw, plan):
    digest = sha256(raw).hexdigest()
    if not isinstance(plan, dict) or set(plan) != {"source_sha256", "units", "keywords"}:
        raise ValueError("plan must contain source_sha256, units, and keywords")
    if plan["source_sha256"] != digest:
        raise ValueError("source digest differs from plan")
    pattern = keyword_pattern(plan["keywords"])
    text = raw.decode("utf-8")
    units = plan["units"]
    if not isinstance(units, list):
        raise ValueError("units must be a list")
    unit_ids = set()
    for unit in units:
        if not isinstance(unit, dict) or set(unit) != {"id", "start", "end"}:
            raise ValueError("unit must contain id, start, and end")
        name, start, end = (unit[key] for key in ("id", "start", "end"))
        if (not isinstance(name, str) or not name.strip() or name in unit_ids
                or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text)):
            raise ValueError("unit has a duplicate ID or invalid coordinates")
        unit_ids.add(name)

    witnesses = []
    previous_end = 0
    matches_in_source = iter(pattern.finditer(text))
    match = next(matches_in_source, None)
    for unit in sorted(units, key=lambda item: item["start"]):
        start, end = unit["start"], unit["end"]
        if start < previous_end:
            raise ValueError("unit coordinates overlap")
        previous_end = end
        matches = []
        while match is not None and match.start() < end:
            if start <= match.start() and match.end() <= end:
                matches.append(match)
            match = next(matches_in_source, None)
        for position, hit in enumerate(matches):
            left = matches[position - 1].end() if position else start
            right = matches[position + 1].start() if position + 1 < len(matches) else end
            context_start = max(left, hit.start() - 75)
            context_end = min(right, hit.end() + 175)
            witnesses.append({
                "id": f"w{len(witnesses) + 1:05d}",
                "unit": unit["id"],
                "keyword": " ".join(hit[0].split()),
                "start": hit.start(),
                "end": hit.end(),
                "quote": hit[0],
                "context": {"start": context_start, "end": context_end, "quote": text[context_start:context_end]},
            })
    return {"source_sha256": digest, "witnesses": witnesses}


def unique_object(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("plan contains duplicate JSON keys")
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.output.resolve() in (args.source.resolve(), args.plan.resolve()):
            raise ValueError("output would replace an input")
        plan = json.loads(args.plan.read_bytes(), object_pairs_hook=unique_object)
        payload = index(args.source.read_bytes(), plan)
        args.output.write_bytes((json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Cannot index source witnesses. {error}\n")


if __name__ == "__main__":
    main()
