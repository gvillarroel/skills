#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent structure/fidelity checks; semantic screenshot review remains separate."""

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def explicit_uncertainty(content):
    return bool(re.search(r"\b(?:unknown|unresolved|unspecified|not (?:supplied|specified|provided))\b", content, re.I))


def check(run, case):
    out = run / "workspace" / "out"
    plan = json.loads((out / "plan.json").read_text(encoding="utf-8-sig"))
    report = json.loads((out / "report.json").read_text(encoding="utf-8-sig"))
    audit = json.loads((out / "audit.json").read_text(encoding="utf-8-sig"))
    raw = (out / "figure.svg").read_bytes()
    svg = ET.fromstring(raw)
    findings = []

    def need(condition, message):
        if not condition: findings.append(message)

    expected = {"contract": (1000, 700, 1000, 14), "naturalistic": (1200, 780, 1000, 14),
                "generalization": (760, 1100, 760, 15), "transfer": (760, 1100, 760, 15), "boundary": (900, 660, 900, 14)}[case]
    c = plan["canvas"]
    need(tuple(c[k] for k in ("width", "height", "displayWidth", "minTextPx")) == expected, "Canvas/display/type contract changed")
    viewbox = [float(x) for x in svg.get("viewBox", "").replace(",", " ").split()]
    need(viewbox == [0, 0, expected[0], expected[1]], "SVG viewport differs from requested canvas")
    panels = plan["panels"]
    need(len(panels) == 3, "Expected three requested explanations")
    need(len({p["family"] for p in panels}) >= 2, "Semantically different explanations collapsed into one form")
    occupied = set()
    for p in panels:
        s = p["span"]
        cells = {(r, col) for r in range(s["row"], s["row"] + s["rows"])
                 for col in range(s["column"], s["column"] + s["columns"])}
        need(not occupied.intersection(cells), "Grid panels overlap")
        occupied |= cells
        need(bool(p["reason"].strip()) and bool(p["alternative"].strip()), "Missing selection rationale")
        path = (out / p["source"]).resolve()
        need(path.is_relative_to((run / "workspace").resolve()), "Panel source outside isolated workspace")
        need(path.is_relative_to((out / "panels").resolve()), "Panel source outside requested out/panels directory")
        record = next((r for r in report["panels"] if r["id"] == p["id"]), {})
        need(record.get("sourceSha256") == hashlib.sha256(path.read_bytes()).hexdigest(), "Source hash mismatch")
    if case == "naturalistic":
        spans = {tuple(p["span"][k] for k in ("row", "column", "rows", "columns")) for p in panels}
        need(spans == {(1, 1, 1, 2), (2, 1, 1, 2), (1, 3, 2, 2)}, "User's exact grid spans changed")
    nodes = list(svg.iter())
    ids = [n.get("id") for n in nodes if n.get("id")]
    need(len(ids) == len(set(ids)), "Duplicate assembled SVG IDs")
    known = set(ids)
    for node in nodes:
        local = node.tag.rsplit("}", 1)[-1]
        need(local not in {"image", "script", "foreignObject", "style", "animate", "animateTransform"}, "Nonportable or dynamic element")
        for key, value in node.attrib.items():
            if key.rsplit("}", 1)[-1] == "href":
                need(value.startswith("#") and value[1:] in known, "Unresolved/local-external href")
            for ref in re.findall(r"url\(['\"]?([^)'\"]+)", value):
                need(ref.startswith("#") and ref[1:] in known, "Unresolved paint/clip reference")
    content = " ".join("".join(n.itertext()) for n in nodes if n.tag.endswith("}text") or n.tag.endswith("}title") or n.tag.endswith("}desc")).lower()
    terms = {"contract": ["peer", "library", "read", "write", "service"],
             "naturalistic": ["editor", "assistant", "ci", "review", "source", "build", "propos"],
             "generalization": ["oats", "barley", "peas", "beans", "inspect", "return", "keep", "envelope", "jar"],
             "transfer": ["camera", "recorder", "lense", "binocular", "clean", "inspect", "stor", "yellow", "purple", "padded", "rigid"],
             "boundary": ["copilot", "cloud", "workspace"]}[case]
    for term in terms: need(term in content, f"Required semantic term not visible/accessible: {term}")
    if case == "boundary":
        need(explicit_uncertainty(content), "Missing explicit unknown/unresolved qualifier or visible equivalent")
        need("github copilot" not in content and "microsoft copilot" not in content, "Unresolved Copilot identity invented")
    need(audit.get("ok") is True, "Agent's final browser report has findings")
    need(audit.get("sourceSha256") == hashlib.sha256(raw).hexdigest(), "Audit does not correspond to final SVG")
    need(audit.get("minimumObservedPx", 0) >= expected[3] - 0.11, "Minimum rendered font below threshold")
    result = {"runId": run.name, "case": case, "ok": not findings, "findings": findings,
              "familyChoices": [p["family"] for p in panels], "sourceSha256": hashlib.sha256(raw).hexdigest(),
              "minimumObservedPx": audit.get("minimumObservedPx"), "manualSemanticReviewRequired": True}
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run", type=Path)
    ap.add_argument("--case", choices=["contract", "naturalistic", "generalization", "transfer", "boundary"], required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    try:
        result = check(args.run, args.case)
    except (ValueError, KeyError, OSError, StopIteration) as exc:
        result = {"runId": args.run.name, "ok": False, "findings": [str(exc)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
