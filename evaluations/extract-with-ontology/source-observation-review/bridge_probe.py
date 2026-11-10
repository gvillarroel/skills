"""Test whether authorized intervening lines supply the missing reference context."""

from argparse import ArgumentParser
from pathlib import Path
import re

from referent_probe import summarize, verify
from study import ROOT, bind_span, digest, encode, load, load_sources, opaque, store


SECTION_BOUNDARY = re.compile(r"^\s*(?:#{1,6}\s|\.\.\s+(?:function|class|method)::|<(?:term|sect[0-9])\b)", re.I)


def bridge(packet, locations, sources):
    if len(locations) != 2:
        return None
    (source, first, previous), (following, start, last) = locations
    if source != following or not 1 <= start - previous - 1 <= 12:
        return None
    lines = sources[source]
    if any(SECTION_BOUNDARY.match(line) for line in lines[previous:start - 1]):
        return None
    text = "\n".join(lines[first - 1:last])
    if len(text) > 1600:
        return None
    return {
        "id": opaque("w", "contiguous", packet["id"]),
        "document": packet["windows"][0]["document"],
        "lines": [first, last],
        "text": text,
    }


def freeze(run, actors, extra):
    run.mkdir()
    for batch, rows in actors.items():
        store(run / f"{batch}-actor.json", rows)
    files = ("bridge_probe.py", "referent_probe.py", "referent-fixture.json", "fixtures.json", "run-model.mjs", "study.py", "follow_up.py")
    store(run / "freeze.json", {
        "code_sha256": {name: digest((ROOT / name).read_bytes()) for name in files},
        "input_sha256": {batch: digest((run / f"{batch}-actor.json").read_bytes()) for batch in actors},
        **extra,
    })


def prepare(base, run):
    verify(base)
    pins = load(ROOT / "fixtures.json")["sources"]
    sources = load_sources(pins)
    locations = {
        opaque("p", "referent", case["name"]): case["windows"]
        for case in load(ROOT / "referent-fixture.json")
    }
    actors, bridged = {}, []
    for batch in ("a", "b"):
        rows = load(base / f"{batch}-actor.json")
        for row in rows:
            extra = bridge(row, locations[row["id"]], sources)
            if extra is not None:
                row["windows"].append(extra)
                bridged.append({"packet": row["id"], "characters": len(extra["text"])})
        actors[batch] = rows
    freeze(run, actors, {
        "scope": "Same reader and cases. Add exact contiguous text within the two original same-document windows.",
        "cap_characters": 1600, "gap_max_lines": 12, "attempts_per_batch": 1,
        "bridged": bridged,
    })
    print(encode({"bridged": len(bridged), "freeze": digest((run / "freeze.json").read_bytes())}))


def project(base, expanded, result):
    verify(base)
    verify(expanded)
    actors = {batch: load(base / f"{batch}-actor.json") for batch in ("a", "b")}
    freeze(result, actors, {"projection": "Retain only exact quotes in one of the original windows."})
    removed = []
    for batch, packets in actors.items():
        responses = load(expanded / f"{batch}-bindings.json")
        for packet in packets:
            key = packet["id"]
            binding = responses[key]
            windows = {window["id"]: window["text"] for window in packet["windows"]}
            if binding is None or binding["window"] in windows:
                continue
            original = [window for window, text in windows.items() if binding["quote"] in text]
            if len(original) == 1:
                responses[key] = bind_span({"window": original[0], "quote": binding["quote"]}, windows)
            else:
                removed.append(key)
                responses[key] = None
        store(result / f"{batch}-bindings.json", responses)
    store(result / "projection.json", {"unprojectable_bindings": removed})
    print(encode({"unprojectable_bindings": len(removed)}))
    summarize(result)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("base", type=Path)
    prep.add_argument("run", type=Path)
    replay = sub.add_parser("project")
    replay.add_argument("base", type=Path)
    replay.add_argument("expanded", type=Path)
    replay.add_argument("result", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.base, args.run)
    else:
        project(args.base, args.expanded, args.result)
