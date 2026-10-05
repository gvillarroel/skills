#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regenerate the two published compositions from their authored briefs."""

import argparse
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
FIXTURE = Path(__file__).resolve().parent.parent
SCRIPTS = FIXTURE.parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import compile_synchronized_svg_plan as compiler
import compose_synchronized_svg as composer


def repair_inference_layout(plan):
    """Retain complete control labels and keep feedback outside the header."""
    original = copy.deepcopy(plan)
    module = next(item for item in plan["modules"] if item["id"] == "adaptive-control")
    verification = next(item for item in plan["modules"] if item["id"] == "speculative-verify")
    # The old 16-panel fixture's six root cards could not fit complete labels in
    # its equal 370-pixel row. Put its 394-pixel panel in the final feedback row,
    # six pixels above its peers, and put verification in the former control
    # slot. This avoids a same-row feedback return through the timeline header.
    # A 24-pixel route band and 48 extra footer pixels keep all returns visible.
    module["region"] = list(verification["region"])
    module["region"][1] -= 6
    module["region"][3] = max(module["region"][3], 394)
    verification["region"] = next(list(item["region"]) for item in original["modules"]
                                   if item["id"] == module["id"])
    plan["layout"]["gap"] = 24
    plan["viewBox"][3] += 48
    plan["layout"]["safeArea"][3] += 24
    plan["layout"]["readingOrder"] = [item["id"] for item in sorted(
        plan["modules"], key=lambda item: (item["region"][1], item["region"][0]))]
    x, y, width, height = module["region"]
    for other in plan["modules"]:
        if other is module:
            continue
        ox, oy, ow, oh = other["region"]
        if x < ox + ow and ox < x + width and y < oy + oh and oy < y + height:
            raise ValueError("The fixture panel repair overlaps another module; review its source layout")
    expected = copy.deepcopy(original)
    for adjusted in (module, verification):
        next(item for item in expected["modules"] if item["id"] == adjusted["id"])["region"] = adjusted["region"]
    expected["viewBox"] = plan["viewBox"]
    for key in ("gap", "safeArea", "readingOrder"):
        expected["layout"][key] = plan["layout"][key]
    if plan != expected:
        raise ValueError("The fixture repair changed content beyond its declared geometry")
    compiler.scaffold.validate_plan(plan)
    return {"regions": [{"moduleId": item["id"], "before": next(source["region"]
            for source in original["modules"] if source["id"] == item["id"]), "after": list(item["region"])}
            for item in (module, verification)], "routeBand": 24, "extraFooterHeight": 48}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True,
                        help="Task-owned folder for generated plans and reports, outside the skill")
    parser.add_argument("--force", action="store_true", help="Replace the two owned fixture SVGs")
    args = parser.parse_args()
    artifacts = args.artifacts.resolve()
    if artifacts.is_relative_to(FIXTURE.parent.parent.parent):
        parser.error("Keep generated plans and reports outside the skill bundle")
    artifacts.mkdir(parents=True, exist_ok=True)
    results = []
    for brief_name, stem in (("composition-brief.json", "inference-pulse"),
                             ("heatwave-tree-brief.json", "heatwave-tree")):
        plan, normalizations = compiler.compile_brief(compiler.load_brief(FIXTURE / brief_name))
        adjustment = repair_inference_layout(plan) if stem == "inference-pulse" else None
        spec = artifacts / f"{stem}-plan.json"
        compiler.write_atomic(spec, (json.dumps(plan, indent=2) + "\n").encode("utf-8"), args.force)
        result = composer.compose(SimpleNamespace(spec=spec, output=FIXTURE / f"{stem}.svg",
                                  report=artifacts / f"{stem}-compose.json", force=args.force))
        results.append({"brief": brief_name, "output": f"{stem}.svg", "normalizations": normalizations,
                        "panelAdjustment": adjustment, "moduleCount": result["moduleCount"]})
    summary = {"ok": True, "compositions": results}
    compiler.write_atomic(artifacts / "regeneration.json",
                          (json.dumps(summary, indent=2) + "\n").encode("utf-8"), args.force)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
