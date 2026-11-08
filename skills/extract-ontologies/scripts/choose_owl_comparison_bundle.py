#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Choose a stable representation among already admitted OWL axiom bundles."""

from argparse import ArgumentParser
import json
from pathlib import Path


def unique_object(pairs):
    value = dict(pairs)
    if len(pairs) != len(value):
        raise ValueError("duplicate JSON key")
    return value


def bundle_key(lines):
    if type(lines) is not list or any(
        type(line) is not str or not line.strip() or "\n" in line or "\r" in line for line in lines
    ):
        raise ValueError("a bundle must be a list of canonical axiom lines")
    return tuple(sorted(line.encode("utf-8") for line in lines))


def choose(groups):
    if type(groups) is not dict:
        raise ValueError("expected an object of review groups")
    selected = {}
    for group_id, candidates in sorted(groups.items()):
        if not group_id.strip() or type(candidates) is not dict:
            raise ValueError("expected a named group with an object of candidates")
        keys = {}
        for label, bundle in candidates.items():
            if not label.strip() or label == "NONE":
                raise ValueError("invalid candidate label")
            keys[label] = bundle_key(bundle), label.encode("utf-8")
        selected[group_id] = min(keys, key=keys.__getitem__, default="NONE")
    return selected


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("admitted_options", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        groups = json.loads(args.admitted_options.read_bytes(), object_pairs_hook=unique_object)
        selected = choose(groups)
        rendered = json.dumps(selected, ensure_ascii=False, indent=2) + "\n"
        args.out.write_text(rendered, encoding="utf-8", newline="\n")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")
