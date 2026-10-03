#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Produce a compact durable summary from retained independent browser evidence."""

import hashlib
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/"projects/treemap-tones"


def evidence(path):
    target=ROOT/path
    return {"path":path,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"bytes":target.stat().st_size}


def main() -> int:
    directories={"baseline":"baseline","colorset1":"final-cs1","colorset2":"final-cs2","base":"final-base"}
    reports={name:json.loads((PROJECT/f"artifacts/{directory}/verification.json").read_text(encoding="utf-8")) for name,directory in directories.items()}
    geometry=json.loads((PROJECT/"artifacts/geometry-comparison.json").read_text(encoding="utf-8"))
    controls=json.loads((PROJECT/"artifacts/negative-controls-cs1/verification.json").read_text(encoding="utf-8"))
    summary={
        "schemaVersion":1,"date":"2026-10-03","patternId":"d3-treemap-cs1",
        "reviewer":"Independent read-only visual review agent; verifier inspects native bound D3 data and computed browser paint rather than trusting new authored classes.",
        "outcome":"pass",
        "rootCause":"All descendants inherited the same branch fill. Removing the old white strokes left identically painted parent underlays in child padding gaps, merging each branch into one block.",
        "scope":["d3-treemap-cs1","d3-treemap-cs2","d3-treemap"],
        "stateMatrix":{"viewportWidths":[1440,390],"height":1100,"motionModes":["normal","reduced"],"settledReplays":[0,1,2],"statesPerGallery":12,"finalPositiveStates":36,"additionalControlSetupStates":1},
        "baseline":{"states":len(reports["baseline"]["states"]),"findings":sum(len(state["findings"]) for state in reports["baseline"]["states"]),"findingsPerState":15,"browserErrors":reports["baseline"]["errors"],"classifications":["Repeated sibling paint in all three branches","Zero sibling luminance steps in all three branches","All nine sibling gaps reveal the same paint as their leaves"],"originalFills":{"Learn":["#9e1b32"]*3,"Create":["#696969"]*3,"Serve":["#4f4f4f"]*3}},
        "finalGalleries":{},
        "geometryComparison":{"clean":geometry["clean"],"states":sum(item["states"] for item in geometry["comparisons"]),"nodeComparisons":sum(item["nodeComparisons"] for item in geometry["comparisons"]),"findings":geometry["findings"],"fields":["name","depth","value","branch","x0","y0","x1","y1","painted width","painted height"]},
        "negativeControls":{"colorset1":controls["negativeControls"],"base":reports["base"]["negativeControls"],"mutations":"Native DOM paint/geometry mutations are inspected immediately, before the automatic style normalizer repairs them; originals are restored after each control."},
        "manualReview":{"independent":True,"outcome":"pass","inspected":[f"projects/treemap-tones/artifacts/{directory}/treemap-{width}-normal-card.png" for directory in directories.values() for width in [1440,390]],"baselineObservation":"Three flat branch blocks with child labels floating inside; child rectangles cannot be seen.","finalObservation":"All nine leaf rectangles are immediately distinguishable in desktop and mobile views. Dark/base/bright or grayscale steps preserve branch families. White spaces expose separation without adding decorative outlines. Black/white labels remain visible and inside cells.","limits":"The review covers the named fixture's three branches and nine leaves at documented finite states. It does not certify arbitrary hierarchy cardinalities or all future data."},
        "commands":[
            "uv run --script projects/treemap-tones/scripts/verify_treemap.py skills/d3/assets/examples/d3-animated-svg-cs1/index.html --output-directory projects/treemap-tones/artifacts/baseline --baseline",
            "uv run --script projects/treemap-tones/scripts/verify_treemap.py skills/d3/assets/examples/d3-animated-svg-cs1/index.html --output-directory projects/treemap-tones/artifacts/final-cs1",
            "uv run --script projects/treemap-tones/scripts/verify_treemap.py skills/d3/assets/examples/d3-animated-svg-colorset2/index.html --output-directory projects/treemap-tones/artifacts/final-cs2",
            "uv run --script projects/treemap-tones/scripts/verify_treemap.py skills/d3/assets/examples/d3-animated-svg/index.html --output-directory projects/treemap-tones/artifacts/final-base --compare-reference projects/treemap-tones/artifacts/baseline/verification.json",
            "uv run --script projects/treemap-tones/scripts/compare_treemap_reports.py projects/treemap-tones/artifacts/baseline/verification.json projects/treemap-tones/artifacts/final-cs1/verification.json projects/treemap-tones/artifacts/final-cs2/verification.json projects/treemap-tones/artifacts/final-base/verification.json --output projects/treemap-tones/artifacts/geometry-comparison.json",
            "uv run --script projects/treemap-tones/scripts/verify_treemap.py skills/d3/assets/examples/d3-animated-svg-cs1/index.html --output-directory projects/treemap-tones/artifacts/negative-controls-cs1 --negative-controls-only --compare-reference projects/treemap-tones/artifacts/baseline/verification.json"
        ],
        "baselineProvenance":"Baseline capture completed before the shared gallery patch. Complete pre-change source folders are frozen under ignored projects/treemap-tones/artifacts/baseline-source/. Reproduction must use that copy; the original baseline command targeted canonical files before their update.",
        "verifierEvolution":"The independent positive paint/geometry scanner is unchanged across baseline and final captures. Negative-control and optional report-comparison support were added after the CS1/CS2 positive runs; the base and additional CS1 control runs use the final verifier.",
        "sourceHashes":{},"artifactHashes":[]
    }
    for name in ["colorset1","colorset2","base"]:
        report=reports[name]
        states=report["states"]
        labels=[label for state in states for node in state["nodes"] for label in node["labels"]]
        gaps=[gutter for state in states for gutter in state["gutters"]]
        summary["finalGalleries"][name]={"clean":report["clean"],"states":len(states),"findings":sum(len(state["findings"]) for state in states),"browserErrors":report["errors"],"branches":3,"leaves":9,"opaqueBorderlessFaces":True,"labelsPerState":12,"allLabelsMaximumContrastBlackWhite":True,"minimumLabelContrast":min(label["contrast"] for label in labels),"labelContainmentPassed":True,"ramps":states[0]["ramps"],"gutters":{"samples":len(gaps),"perState":9,"widths":sorted(set(gutter["width"] for gutter in gaps)),"fills":sorted(set(gutter["fill"] for gutter in gaps))}}
    source_paths=[
        "projects/treemap-tones/artifacts/baseline-source/d3-animated-svg/gallery.js",
        "skills/d3/assets/examples/d3-animated-svg/gallery.js",
        "skills/d3/references/patterns/treemap.md",
        "skills/d3/assets/examples/d3-animated-svg/solid-style.js",
        "skills/d3/assets/examples/d3-animated-svg/index.html",
        "skills/d3/assets/examples/d3-animated-svg-cs1/index.html",
        "skills/d3/assets/examples/d3-animated-svg-cs1/cs1-config.js",
        "skills/d3/assets/examples/d3-animated-svg-colorset2/index.html",
        "skills/d3/assets/examples/d3-animated-svg-colorset2/colorset2-config.js",
        "skills/d3/assets/palettes/colorsets.json",
        "projects/treemap-tones/scripts/verify_treemap.py",
        "projects/treemap-tones/scripts/compare_treemap_reports.py"
    ]
    summary["sourceHashes"]={path:evidence(path) for path in source_paths}
    for directory in directories.values():
        base=f"projects/treemap-tones/artifacts/{directory}"
        summary["artifactHashes"].append(evidence(f"{base}/verification.json"))
        for width in [1440,390]:
            for extension in ["-card.png","-svg.png",".svg"]:
                summary["artifactHashes"].append(evidence(f"{base}/treemap-{width}-normal{extension}"))
    summary["artifactHashes"].extend(evidence(path) for path in ["projects/treemap-tones/artifacts/geometry-comparison.json","projects/treemap-tones/artifacts/negative-controls-cs1/verification.json"])
    assert summary["baseline"]["findings"]==180
    assert summary["geometryComparison"]["nodeComparisons"]==432 and geometry["clean"]
    assert all(item["clean"] and item["findings"]==0 for item in summary["finalGalleries"].values())
    assert all(item["rejected"] for key in ["colorset1","base"] for item in summary["negativeControls"][key])
    destination=ROOT/"evaluations/d3/treemap-tones-visual-20261003.json"
    destination.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"outcome":summary["outcome"],"report":str(destination),"sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),"states":36,"baselineFindings":180,"nodeComparisons":432},indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
