#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check the supplied cross-panel palette against final forward-test artifacts."""

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def check(run, case, browser_report):
    out = run / "workspace" / "out"
    spec = json.loads((out / "plan.json").read_text(encoding="utf-8-sig"))
    report = json.loads((out / "report.json").read_text(encoding="utf-8-sig"))
    audited = json.loads(browser_report.read_text(encoding="utf-8-sig"))
    raw = (out / "figure.svg").read_bytes()
    root = ET.fromstring(raw)
    findings = []

    def need(condition, message):
        if not condition:
            findings.append(message)

    expected = {"grains": "#276bc8", "legumes": "#9e1b32"}
    concepts = {}
    for name, color in expected.items():
        matches = [c for c in spec.get("concepts", []) if name in c["label"].lower()]
        need(len(matches) == 1, f"Expected one canonical {name} concept")
        if len(matches) != 1:
            continue
        cid = matches[0]["id"]
        concepts[cid] = color
        need(matches[0].get("color", "").lower() == color, f"Supplied {name} color changed")
        need(report.get("semanticColors", {}).get(cid) == color, f"Composition registry differs for {name}")

    height, count = (500, 2) if case == "contract" else (780, 3)
    c = spec["canvas"]
    need(tuple(c[k] for k in ("width", "height", "displayWidth", "minTextPx")) == (1200, height, 1200, 14), "Requested canvas or viewing scale changed")
    need([float(v) for v in root.get("viewBox", "").split()] == [0, 0, 1200, height], "Wrong final viewport")
    need(len(spec["panels"]) == count, "Wrong number of subdiagrams")
    need(audited.get("ok") is True, "Independent browser audit failed")
    need(audited.get("sourceSha256") == hashlib.sha256(raw).hexdigest(), "Audit is stale")
    need(audited.get("semanticColors", {}).get("status") == "checked", "Color check was not active")
    occurrences = audited.get("semanticColors", {}).get("occurrences", [])
    for p in spec["panels"]:
        need(set(concepts) <= set(p.get("concepts", [])), f"Missing identity in {p['id']}")
        source = (out / p["source"]).resolve()
        need(source.is_relative_to((out / "panels").resolve()), "Source path outside requested panel folder")
        item = next((r for r in report["panels"] if r["id"] == p["id"]), {})
        need(item.get("sourceSha256") == hashlib.sha256(source.read_bytes()).hexdigest(), "Source hash mismatch")
        for cid, color in concepts.items():
            wanted = "rgb(" + ", ".join(str(int(color[i:i+2], 16)) for i in (1, 3, 5)) + ")"
            marks = [o for o in occurrences if o["panel"] == p["id"] and o["concept"] == cid]
            need(bool(marks), f"No rendered color for {cid} in {p['id']}")
            need(all(o["actual"] == wanted and o["visible"] for o in marks), f"Wrong actual paint for {cid} in {p['id']}")
    if case == "naturalistic":
        text = " ".join("".join(e.itertext()) for e in root.iter() if e.tag.endswith("}text")).lower()
        for term in ("oats", "barley", "peas", "beans", "jar", "envelope", "dry"):
            need(term in text, f"Required supplied fact not visibly stated: {term}")
    return {"runId": run.name, "case": case, "ok": not findings, "findings": findings,
            "panelCount": len(spec["panels"]), "palette": concepts,
            "colorOccurrences": len(occurrences), "sourceSha256": hashlib.sha256(raw).hexdigest(),
            "manualSemanticReviewRequired": True}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run", type=Path)
    ap.add_argument("--case", choices=("contract", "naturalistic"), required=True)
    ap.add_argument("--browser-report", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = check(args.run, args.case, args.browser_report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
