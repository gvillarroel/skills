#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Review the frozen SVG-family palette changes and retained native evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
BASE = "daaee75353c63ed6dde204d57cfdbae6b9936586"
OWNERS = ("d3", "procedural-svg-animation", "svg-brief-design", "threejs-animated-3d")
EXPECTED = ["#9e1b32", "#000000", "#828282", "#1c1c1c", "#9c9c9c", "#363636", "#b5b5b5", "#333e48", "#cfcfcf", "#4f4f4f", "#e7e7e7", "#696969", "#f7f7f7", "#ffffff", "#6d1222", "#e8002a", "#ffccd5"]


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT).decode("utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    output = args.report.resolve()
    if not output.is_relative_to(ROOT / "projects/grayscale-interleave/artifacts"):
        parser.error("Report must be inside this project's artifacts directory")
    findings, contracts = [], []
    harness = runpy.run_path(str(ROOT / "scripts/run-pi-skill-eval.py"))
    runtime = []
    for owner in OWNERS:
        source = ROOT / f"skills/{owner}"
        snapshot = {}
        for current_dir, directories, files in os.walk(source):
            current_dir = Path(current_dir)
            directories[:] = [name for name in directories if name not in harness["COPY_IGNORE"]
                              and (current_dir / name).relative_to(source) not in harness["RUNTIME_EXCLUDED_DIRS"]]
            for name in files:
                path = current_dir / name
                if name not in harness["COPY_IGNORE"] and path.suffix.lower() not in harness["SNAPSHOT_IGNORED_SUFFIXES"]:
                    snapshot[path.relative_to(source).as_posix()] = {"sizeBytes": path.stat().st_size,
                                                                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        runtime.append({"skill": owner, "fileCount": len(snapshot), "payloadSha256": harness["snapshot_digest"](snapshot)})
        relative = f"skills/{owner}/assets/palettes/colorsets.json"
        current = read_json(ROOT / relative)["colorsets"]
        previous = json.loads(git("show", BASE + ":" + relative))["colorsets"]
        ok = (current["colorset1"]["sequence"] == EXPECTED == current["colorset1"]["solidSequence"]
              and current["colorset1"]["categoryPriority"] == ["primary-red", "grays", "white", "remaining-colors"]
              and current["colorset1"]["roles"] == previous["colorset1"]["roles"]
              and current["colorset1"]["allowed"] == previous["colorset1"]["allowed"]
              and current["colorset1"]["textOnFill"] == previous["colorset1"]["textOnFill"]
              and current["colorset2"] == previous["colorset2"])
        contracts.append({"skill": owner, "passed": ok, "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()})
        if not ok:
            findings.append(f"Palette or semantic boundary mismatch: {owner}")
    engine_relative = "skills/d3/assets/templates/logo-engine.js"
    engine = (ROOT / engine_relative).read_text(encoding="utf-8")
    previous_engine = git("show", BASE + ":" + engine_relative)
    expression = re.compile(r'(colorset1:\s*\{[\s\S]*?sequence:\s*)\[[^\]]+\]')
    engine_unchanged = expression.sub(r'\1CATEGORY_SEQUENCE', engine) == expression.sub(r'\1CATEGORY_SEQUENCE', previous_engine)
    if not engine_unchanged:
        findings.append("Canonical logo engine changed beyond the CS1 category sequence")
    fixture_root = ROOT / "skills/procedural-svg-animation/assets/examples/procedural-svg-animation/patterns"
    geometry_changes, differences, ink_timing = [], [], []
    for path in sorted(fixture_root.glob("*.svg")):
        relative = path.relative_to(ROOT).as_posix()
        previous = git("show", BASE + ":" + relative)
        mask_paint = lambda value: re.sub(r"#[0-9a-fA-F]{6}\b", "#TOKEN", value)
        current = path.read_text(encoding="utf-8")
        if mask_paint(current) != mask_paint(previous):
            before_xml, after_xml = ET.fromstring(previous), ET.fromstring(current)
            before_nodes, after_nodes = list(before_xml.iter()), list(after_xml.iter())
            before_parents = {child: parent for parent in before_xml.iter() for child in parent}
            after_parents = {child: parent for parent in after_xml.iter() for child in parent}
            if len(before_nodes) == len(after_nodes):
                for old, new in zip(before_nodes, after_nodes):
                    if (old.tag == new.tag == "{http://www.w3.org/2000/svg}animate"
                            and old.get("attributeName") == new.get("attributeName") == "fill"
                            and before_parents[old].tag == after_parents[new].tag == "{http://www.w3.org/2000/svg}text"
                            and set(old.get("values", "").split(";")) <= {"#000000", "#ffffff"}
                            and set(new.get("values", "").split(";")) <= {"#000000", "#ffffff"}
                            and old.get("keyTimes") != new.get("keyTimes")):
                        times = [float(value) for value in new.get("keyTimes", "").split(";")]
                        if times == sorted(times) and times[0] == 0 and times[-1] == 1:
                            ink_timing.append({"path": relative, "previous": old.get("keyTimes"), "current": new.get("keyTimes")})
                            old.set("keyTimes", "ADAPTIVE_TEXT_INK")
                            new.set("keyTimes", "ADAPTIVE_TEXT_INK")
            first, second = mask_paint(ET.tostring(before_xml, encoding="unicode")), mask_paint(ET.tostring(after_xml, encoding="unicode"))
            if first == second:
                continue
            geometry_changes.append(relative)
            mismatch = next((index for index, pair in enumerate(zip(first, second)) if pair[0] != pair[1]), min(len(first), len(second)))
            differences.append({"path": relative, "previous": first[max(0, mismatch - 80):mismatch + 180],
                                "current": second[max(0, mismatch - 80):mismatch + 180]})
    if geometry_changes:
        findings.append("Procedural fixtures differ beyond hex paint tokens")
    retained = ROOT / "projects/colorset1-gray-order/artifacts"
    native_files = {"logo": retained / "reviews/logo-native-final.json",
                    "threejs": retained / "reviews/threejs-interleaved.json"}
    native = {}
    for name, path in native_files.items():
        data = read_json(path)
        ok = bool(data.get("clean", data.get("passed", data.get("ok", False))))
        native[name] = {"path": path.relative_to(ROOT).as_posix(), "passed": ok,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "findings": data.get("findings", [])}
        if not ok:
            findings.append(f"Retained native evidence did not pass: {name}")
    scopes = [f"skills/{owner}" for owner in OWNERS]
    paths = set(git("diff", BASE, "--name-only", "--", *scopes).splitlines())
    paths.update(git("ls-files", "--others", "--exclude-standard", "--", *scopes).splitlines())
    owned = sorted(path for path in paths if not path.endswith("/assets/palettes/colorsets.json"))
    report = {"baselineCommit": BASE, "passed": not findings, "findings": findings, "paletteCopies": contracts,
              "runtimeSnapshots": runtime,
              "logoEngineOnlyCS1SequenceChanged": engine_unchanged,
              "proceduralFixtureCount": len(list(fixture_root.glob("*.svg"))),
              "proceduralChangesBeyondHexPaint": geometry_changes,
              "proceduralDifferenceSamples": differences,
              "adaptiveBlackWhiteTextInkTiming": ink_timing,
              "nativeEvidence": native, "ownedCanonicalCandidateCount": len(owned),
              "ownedCanonicalCandidates": owned,
              "additionalAuthoredCandidates": ["projects/grayscale-interleave/scripts/svg-review-native-evidence.py",
                                                "projects/grayscale-interleave/scripts/svg-review-primary-logo.py",
                                                "evaluations/grayscale-interleave/svg-native-summary.md",
                                                "evaluations/grayscale-interleave/primary-logo-validation.json",
                                                "evaluations/grayscale-interleave/primary-logo-validation.md"],
              "excludedOwnership": "All palette JSON copies are root-owned; bulky retained artifacts remain ignored."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in ("ownedCanonicalCandidates", "nativeEvidence")}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
