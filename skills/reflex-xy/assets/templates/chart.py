#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Editable XY starter. Run with uv; outputs go to --output-dir."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import xy


def load_colorsets(helper_path: Path | None = None):
    if helper_path is None:
        adjacent = Path(__file__).resolve().with_name("xy_colorsets.py")
        bundled = Path(__file__).resolve().parents[2] / "scripts" / "xy_colorsets.py"
        helper_path = adjacent if adjacent.is_file() else bundled
    if not helper_path.is_file():
        raise ValueError("Pass --colorset-helper pointing to xy_colorsets.py, or copy it and colorsets.json beside this script")
    spec = importlib.util.spec_from_file_location("xy_colorsets", helper_path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the colorset helper")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def build_chart(colorset: str, helper) -> xy.Chart:
    rng = np.random.default_rng(17)
    x = rng.normal(size=500)
    y = 0.6 * x + rng.normal(scale=0.5, size=x.size)
    paints = helper.binned_colors(np.hypot(x, y), colorset)
    marks = []
    for index, paint in enumerate(helper.sequential_colors(colorset)):
        keep = np.array([value == paint for value in paints])
        marks.append(xy.scatter(x[keep], y[keep], color=paint, size=6,
                                opacity=1, stroke_width=0,
                                name=f"Magnitude bin {index + 1}"))
    return xy.scatter_chart(
        *marks,
        xy.x_axis(label="Input (units)"),
        xy.y_axis(label="Response (units)"),
        xy.legend(title="Magnitude", style=helper.legend_style(colorset)),
        helper.theme(colorset),
        title="Correlated observations", width=960, height=540,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    parser.add_argument("--colorset-helper", type=Path, help="Path to the bundled or copied xy_colorsets.py")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    helper = load_colorsets(args.colorset_helper)
    chart = build_chart(args.colorset, helper)
    chart.to_html(args.output_dir / "chart.html", custom_css=helper.css(args.colorset))
    chart.write_image(args.output_dir / "chart.svg")
    chart.write_image(args.output_dir / "chart.png", scale=2)
    (args.output_dir / "memory.json").write_text(
        json.dumps(chart.memory_report(), indent=2) + "\n", encoding="utf-8"
    )
    print(f"Created {args.colorset} HTML, SVG, PNG, and memory report in {args.output_dir}")


if __name__ == "__main__":
    main()
