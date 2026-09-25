#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check preservation of source records and the hand-calculated portfolio case."""

import argparse
import json
import math
from html.parser import HTMLParser
from pathlib import Path


class Payload(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active, self.parts = False, []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == "hierarchy-data":
            self.active = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = False

    def handle_data(self, value):
        if self.active:
            self.parts.append(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("html", type=Path)
    parser.add_argument("--portfolio", action="store_true")
    parser.add_argument("--count", type=int)
    args = parser.parse_args()
    raw = json.loads(args.source.read_text(encoding="utf-8"))
    payload = Payload()
    payload.feed(args.html.read_text(encoding="utf-8"))
    rendered = json.loads("".join(payload.parts))
    original = {n["id"]: n for n in raw["nodes"]}
    nodes = {n["id"]: n for n in rendered["nodes"]}
    assert len(original) == len(raw["nodes"]) == len(nodes) == len(rendered["nodes"])
    assert original.keys() == nodes.keys()
    if args.count is not None:
        assert len(nodes) == args.count
    for identity, node in nodes.items():
        assert node["label"] == original[identity]["label"]
        assert node["parentId"] == original[identity]["parentId"]
        assert all(node["values"][d["key"]] == original[identity].get("values", {}).get(d["key"]) for d in raw["dimensions"])
    root = next(n for n in nodes.values() if n["parentId"] is None)
    for dimension in raw["dimensions"]:
        if dimension.get("aggregation") != "sum":
            continue
        key = dimension["key"]
        values = [n.get("values", {}).get(key) for n in original.values()]
        known = [v for v in values if v is not None]
        assert root["aggregates"][key]["known"] == len(known)
        total = root["aggregates"][key]["value"]
        assert total is None if not known else total is not None and math.isclose(total, math.fsum(known), rel_tol=1e-12, abs_tol=1e-9)
    if args.portfolio:
        expected = {"portfolio": (None, 25), "materials": ("portfolio", 100), "ecology": ("portfolio", 50),
                    "battery": ("materials", 400), "polymer": ("materials", 0), "soil": ("ecology", None),
                    "canopy": ("ecology", 250), "coast": ("ecology", 125)}
        assert set(nodes) == set(expected)
        metric = next(d for d in raw["dimensions"] if d["type"] == "numeric")
        for identity, (parent, value) in expected.items():
            assert nodes[identity]["parentId"] == parent
            assert nodes[identity]["values"][metric["key"]] == value
        assert root["aggregates"][metric["key"]] == {"value": 950, "known": 7}
        assert nodes["ecology"]["aggregates"][metric["key"]] == {"value": 425, "known": 3}
        assert nodes["materials"]["aggregates"][metric["key"]] == {"value": 500, "known": 3}
    print(json.dumps({"ok": True, "records": len(nodes), "portfolioOracle": args.portfolio}))


if __name__ == "__main__":
    main()
