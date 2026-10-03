#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run: uv run --script evaluations/contracts/check-hyperframes-composer.py <run-dir> <contract|boundary>."""

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Independently inspect composer command and capacity outcomes.")
    parser.add_argument("run", type=Path)
    parser.add_argument("case", choices=["contract", "boundary"])
    args = parser.parse_args()
    deliverables = args.run / "workspace" / "deliverables"
    findings = []
    observations = {}

    def check(condition, message):
        if not condition:
            findings.append(message)

    def read(name):
        return json.loads((deliverables / name).read_text(encoding="utf-8-sig"))

    model = read("model.json")
    check(model["palette"]["mode"] == "colorset1", "The input palette changed.")
    check(model["derived"]["volume"] == {"expr": {"integrate": ["rate", "time"]}, "unit": "L"},
          "The requested zero-based integral changed.")
    output = model["output"]
    check(output["duration"] == 8 and output["fps"] == 12, "The requested temporal contract changed.")
    event = model["events"]
    check(len(event) == 1 and event[0]["at"] == 2 and event[0]["duration"] == 2,
          "The requested ramp timing changed.")

    if args.case == "boundary":
        check(output["width"] == 960 and output["height"] == 540, "Boundary output dimensions changed.")
        check(model["sources"]["rate"] == {"value": 2.0, "domain": [0, 5.0], "unit": "L/s"},
              "The rejected model's supplied rate or control domain changed.")
        check(event[0]["changes"] == {"rate": 5.0}, "The rejected model's target changed.")
        rejected = read("rejected.json")
        check(rejected.get("ok") is False, "Insufficient capacity was not rejected.")
        check("capacity" in json.dumps(rejected).lower(), "The rejection does not explain the capacity constraint.")
        absent = ["scene.json", "assets/mechanism.svg", "asset-plan.json", "explanation.mp4"]
        check(all(not (deliverables / path).exists() for path in absent),
              "Refused composition created a misleading scene, asset or movie.")
        observations = {"originalDomain": model["sources"]["rate"]["domain"],
                        "nominalFinalVolume": 31, "maximumLegalVolume": 40,
                        "requestedCapacity": 20, "absentArtifacts": absent, "rejection": rejected}
    else:
        check(output["width"] == 1280 and output["height"] == 720, "Contract output dimensions changed.")
        check(model["sources"]["rate"] == {"value": 1.0, "domain": [0, 3.0], "unit": "L/s"},
              "The contract input facts changed.")
        check(event[0]["changes"] == {"rate": 2.0}, "The contract target changed.")
        scene, assembled, plan = read("scene.json"), read("assembled.json"), read("asset-plan.json")
        for field in ["sources", "derived", "events", "output", "palette", "invariants"]:
            check(scene.get(field) == model.get(field) and assembled.get(field) == model.get(field),
                  f"Composition/import changed numerical field {field}.")
        check(len(scene["views"]) == 3 and len(assembled["views"]) == 3,
              "The composition lacks three complementary views.")
        svg = ET.parse(deliverables / "assets/mechanism.svg").getroot()
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        labels = [node.text for node in svg.findall(".//svg:text", namespace)]
        bounds = [float(part) for part in svg.attrib["viewBox"].split()]
        mechanism = next(view for view in scene["views"] if view["id"] == "mechanism")
        check(bounds == [0, 0, *mechanism["region"][2:]], "The scaled SVG viewBox differs from its actual view.")
        check("24" in labels and "0" in labels and "L" in labels, "The actual SVG lacks the requested graduated ruler.")
        check(any("bundled" in str(asset.get("producer", "")) for asset in plan["assets"]),
              "The asset plan does not identify the actual bundled producer.")
        check(read("composition.json").get("ok") is True and read("import.json").get("ok") is True,
              "The composition or import report rejected the artifacts.")
        observations = {"nominalFinalVolume": 13, "maximumLegalVolume": 24,
                        "viewBox": bounds, "graduatedRulerLabels": labels,
                        "viewCount": len(scene["views"]), "modelFieldsPreserved": True}

    report = {"ok": not findings, "case": args.case, "findings": findings, "observations": observations}
    (args.run / "independent.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "case": args.case, "findings": findings}))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
