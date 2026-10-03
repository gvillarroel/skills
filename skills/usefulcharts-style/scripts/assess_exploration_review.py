#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate reference-bound discovery evidence; do not certify aesthetic quality."""
from pathlib import Path
import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from assess_illustrated_review import assess as assess_coverage


def assess(data, base):
    failures = []

    def need(value, code):
        if not value:
            failures.append(code)

    def evidence(record, label):
        path = base / record.get("path", "")
        need(path.is_file(), "missing-" + label)
        if path.is_file():
            need(hashlib.sha256(path.read_bytes()).hexdigest() == record.get("sha256"), "stale-" + label)
        return path

    need(data.get("schema_version") == 1, "schema-version")
    coverage_path = base / data.get("illustrated_review", "")
    coverage = {}
    if coverage_path.is_file():
        raw = json.loads(coverage_path.read_text(encoding="utf-8-sig"))
        coverage = assess_coverage(raw, coverage_path.parent)
    else:
        raw = {}
    need(coverage.get("declared_illustrated_brief_pass") is True, "illustrated-coverage")
    svg = evidence(data.get("svg", {}), "svg")
    elements = {}
    if svg.is_file():
        try:
            root = ET.parse(svg).getroot()
            for element in root.iter():
                if element.get("id"):
                    need(element.get("id") not in elements, "duplicate-svg-id")
                    elements[element.get("id")] = element
        except ET.ParseError:
            need(False, "invalid-svg")
    reference = data.get("reference", {})
    need(str(reference.get("source_url", "")).startswith(("https://", "http://")), "reference-source")
    for kind in ("whole", "detail"):
        evidence(reference.get(kind, {}), "reference-" + kind)
    need(reference.get("reviewed_images") is True, "reference-not-viewed")
    need(reference.get("comparison_basis") in ("same-width-whole-and-relative-detail", "same-area-whole-and-relative-detail"), "comparison-basis")
    for kind in ("structure", "image_ownership", "color_continuity", "reading_rhythm"):
        need(bool(str(reference.get("comparisons", {}).get(kind, "")).strip()), "unexplained-reference-" + kind)
    routes = data.get("discovery_routes", [])
    need(len(routes) >= 3, "insufficient-discovery-routes")
    records = set(raw.get("record_ids", []))
    printed_records = set()
    if svg.is_file() and elements:
        for element in root.iter():
            ident = element.get("data-record-id") or element.get("data-id")
            if not ident and "record" in element.get("class", "").split():
                ident = element.get("id")
            if ident:
                printed_records.add(ident)
    need(records <= printed_records, "missing-printed-record")
    regions = set()
    route_ids = set()
    operations = set()
    for route in routes:
        identifier = route.get("id")
        need(bool(identifier) and identifier not in route_ids, "duplicate-or-missing-route")
        route_ids.add(identifier)
        anchors = set(route.get("anchors", []))
        need(len(anchors) >= 2 and anchors <= records, "unbound-discovery")
        need(bool(route.get("question")) and bool(route.get("answer")), "missing-discovery-answer")
        need(route.get("operation") in ("trace", "compare", "time"), "invalid-reading-operation")
        operations.add(route.get("operation"))
        need(route.get("region") in ("upper", "middle", "lower"), "invalid-discovery-region")
        regions.add(route.get("region"))
        need(route.get("reviewed_at_reading_size") is True, "unreviewed-discovery")
        need(route.get("requires_detached_lookup") is False, "detached-discovery")
        evidence(route.get("detail", {}), "route-detail-" + str(identifier))
        steps = route.get("steps", [])
        need(len(steps) >= 2, "missing-visible-steps")
        for step in steps:
            ids = step.get("element_ids", [])
            need(bool(ids) and all(i in elements for i in ids), "missing-printed-element")
            need(bool(str(step.get("observation", "")).strip()), "unexplained-visible-step")
            for ident in ids:
                el = elements.get(ident)
                if el is not None:
                    style = el.get("style", "").replace(" ", "")
                    need(el.get("display") != "none" and el.get("opacity") != "0" and "display:none" not in style and "opacity:0;" not in style, "hidden-printed-element")
    need(len(regions & {"upper", "middle", "lower"}) >= 2, "concentrated-discovery")
    need(len(operations & {"trace", "compare", "time"}) >= 2, "single-reading-operation")
    need(data.get("actual_pixel_review") is True, "no-pixel-review")
    need(not data.get("unresolved_composition_defects"), "unresolved-composition")
    exploratory = not failures
    density = coverage.get("reference_density_status", "pending")
    reference_pass = exploratory and reference.get("convincing_family_resemblance") is True and density == "verified" and not reference.get("remaining_differences")
    return dict(schema_version=1, illustrated_coverage_pass=coverage.get("declared_illustrated_brief_pass", False),
                declared_exploratory_composition_pass=exploratory, declared_reference_target_pass=reference_pass,
                failures=sorted(set(failures)), reference_density_status=density,
                remaining_reference_differences=reference.get("remaining_differences", []),
                evidence_boundary="Hashes and printed IDs validate evidence completeness. Pixel review and declarations are not objective aesthetic scores or a blind authorship experiment.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = assess(json.loads(args.review.read_text(encoding="utf-8-sig")), args.review.parent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["declared_exploratory_composition_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
