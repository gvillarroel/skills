#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build an offline D3 line chart with readable direct labels and honest gaps."""

import argparse
from html import escape
import json
import math
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

from build_contract_artifact import json_script, palette_for


SKILL = Path(__file__).resolve().parents[1]
ID = re.compile(r"[A-Za-z][\w-]{0,63}", re.ASCII)


def data_for(path, emphasis, svg_id):
    data = json.loads(path.read_text(encoding="utf-8"))
    categories, series = data["categories"], data["series"]
    if not isinstance(categories, list) or not 2 <= len(categories) <= 18 or not all(
        isinstance(label, str) and label.strip() for label in categories
    ) or len(set(categories)) != len(categories):
        raise ValueError("Use 2–18 distinct, nonempty category labels.")
    if not isinstance(series, list) or not 1 <= len(series) <= 5:
        raise ValueError("Use 1–5 ordered series.")
    reserved = {svg_id, f"{svg_id}-title", f"{svg_id}-description", "d3-runtime", "line-data"}
    ids = set(reserved)
    labels = set()
    for row in series:
        key, label, values = (row[field] for field in ("id", "label", "values"))
        if not ID.fullmatch(key) or key in ids or not isinstance(label, str) or not label.strip() or label in labels:
            raise ValueError("Series must have distinct IDs and nonempty distinct labels.")
        if not isinstance(values, list) or len(values) != len(categories) or all(value is None for value in values):
            raise ValueError(f"Series {key} requires a sample for at least one category and one value per category.")
        if any(value is not None and (type(value) not in {float, int} or not math.isfinite(value) or value < 0)
               for value in values):
            raise ValueError(f"Series {key} values must be nonnegative finite numbers or null.")
        ids.add(key)
        labels.add(label)
    if emphasis is not None and emphasis not in ids - reserved:
        raise ValueError("The emphasis must name a series ID.")
    return {"categories": categories, "series": series, "emphasis": emphasis or series[0]["id"]}


def build(args, data):
    runtime = (SKILL / "assets/vendor/d3.v7.9.0.min.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    renderer = (SKILL / "assets/templates/direct-line.js").read_text(encoding="utf-8")
    model = data | {
        "title": args.title, "unit": args.unit, "width": args.width, "height": args.height,
        "palette": palette_for(args.colorset),
    }
    title, description = map(escape, (args.title, args.description))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>body{{margin:0}}svg{{display:block;max-width:100%;height:auto;font-family:Arial,sans-serif}}</style>
</head><body data-colorset="{args.colorset}">
<svg id="{args.id}" width="{args.width}" height="{args.height}" viewBox="0 0 {args.width} {args.height}"
     data-colorset="{args.colorset}" data-pattern-id="d3-line-missing-data" data-renderer="d3"
     role="img" aria-labelledby="{args.id}-title {args.id}-description">
<title id="{args.id}-title">{title}</title><desc id="{args.id}-description">{description}</desc>
</svg>
<script id="d3-runtime">/* D3 v7.9.0, BSD-3-Clause */\n{runtime}</script>
<script id="line-data" type="application/json">{json_script(model)}</script>
<script>{renderer}</script>
</body></html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, metavar="PATH", required=True,
                        help="Path to a local JSON file containing categories and series.")
    parser.add_argument("--id", required=True, help="Stable SVG ID.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--unit", required=True, help="Displayed measurement unit.")
    parser.add_argument("--emphasis", help="Series ID to emphasize. Defaults to the first series.")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=320)
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if (not ID.fullmatch(args.id) or args.id in {"d3-runtime", "line-data"}
                or not all(value.strip() for value in (args.title, args.description, args.unit))):
            raise ValueError("Use a stable SVG ID and nonempty title, description, and unit.")
        if not 420 <= args.width <= 2400 or not 260 <= args.height <= 1600:
            raise ValueError("Use a width of 420–2400 and a height of 260–1600 CSS pixels.")
        data = data_for(args.data, args.emphasis, args.id)
        result = build(args, data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as error:
        parser.exit(1, f"Direct line chart failed. {error}\n")
    print(f"Built offline D3 line chart at {args.output}.")


if __name__ == "__main__":
    main()
