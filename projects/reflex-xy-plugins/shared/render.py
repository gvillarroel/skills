#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Bounded JSON-to-XY bridge. Never evaluate submitted code or read data URLs."""

from __future__ import annotations

import argparse
import ast
import contextlib
from copy import deepcopy
import importlib.util
import inspect
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET

from presets import PRESETS, expand

VERSION = "0.0.8"
MAX_BYTES = 1_048_576
MAX_SCALARS = 40_000
MARKS = {"scatter", "line", "area", "bar", "column", "hist", "histogram", "step", "stairs",
         "stem", "ecdf", "box", "violin", "errorbar", "error_band", "heatmap", "hexbin",
         "contour", "segments", "triangle_mesh", "ribbon", "funnel"}
FACTORIES = {"chart", "scatter_chart", "line_chart", "area_chart", "bar_chart", "column_chart",
             "histogram_chart", "step_chart", "stairs_chart", "stem_chart", "ecdf_chart",
             "box_chart", "violin_chart", "errorbar_chart", "error_band_chart", "heatmap_chart",
             "hexbin_chart", "contour_chart", "segments_chart", "triangle_mesh_chart", "funnel_chart",
             "sankey_chart", "polar_chart", "polar_bar_chart", "radar_chart", "pie_chart", "wind_rose", "facet_chart"}
COMPONENTS = {"x_axis", "y_axis", "theta_axis", "r_axis", "legend", "colorbar", "tooltip", "modebar",
              "interaction_config", "export_config", "animation", "text", "label", "hline", "vline",
              "x_band", "y_band", "arrow", "callout", "threshold", "threshold_zone", "marker", "theme"}
TOP_KEYS = {"version", "title", "colorset", "factory", "args", "data", "marks", "components", "options",
            "width", "height", "description"}
BLOCKED_KEYS = {"render", "src", "href", "url", "path", "output_dir", "custom_css", "module", "script",
                "__class__", "__dict__", "__globals__", "__builtins__"}
LIMITED_OPTIONS = {"bins": 128, "gridsize": 128, "sectors": 64, "levels": 32, "iterations": 32, "cols": 6}


class SpecError(ValueError):
    pass


def load_module(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    if spec is None or spec.loader is None:
        raise SpecError("Cannot load the packaged XY skill resource")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def skill_path(explicit=None):
    candidate = explicit or os.environ.get("XY_SKILL_DIR")
    here = Path(__file__).resolve().parent
    options = [Path(candidate)] if candidate else [here / "skill/reflex-xy", here.parent / "skills/reflex-xy"]
    for folder in options:
        if (folder / "SKILL.md").is_file() and (folder / "scripts/xy_colorsets.py").is_file():
            return folder.resolve()
    raise SpecError("The runtime skill is missing. Build a distribution or pass --skill-dir to the canonical reflex-xy bundle.")


def guard_json(value):
    count = 0

    def visit(item, depth=0):
        nonlocal count
        if depth > 12:
            raise SpecError("JSON nesting exceeds 12 levels")
        if isinstance(item, dict):
            if len(item) > 96:
                raise SpecError("An object contains more than 96 fields")
            for key, child in item.items():
                if not isinstance(key, str) or key.startswith("_") or key.startswith("on_") or key in BLOCKED_KEYS:
                    raise SpecError(f"Field is not permitted: {key}")
                if len(key) > 100:
                    raise SpecError("Field name is too long")
                if key in LIMITED_OPTIONS and isinstance(child, (int, float)) and not isinstance(child, bool):
                    if not 1 <= child <= LIMITED_OPTIONS[key]:
                        raise SpecError(f"{key} must be between 1 and {LIMITED_OPTIONS[key]}")
                if key in {"bins", "levels", "speed_bins"} and isinstance(child, list) and len(child) > 129:
                    raise SpecError(f"{key} contains too many thresholds")
                visit(child, depth+1)
        elif isinstance(item, list):
            if len(item) > 20_000:
                raise SpecError("An array contains more than 20000 items")
            for child in item:
                visit(child, depth+1)
        elif item is None or isinstance(item, (str, bool, int, float)):
            count += 1
            if isinstance(item, str) and len(item) > 4096:
                raise SpecError("A string exceeds 4096 characters")
            if isinstance(item, (int, float)) and not isinstance(item, bool) and (abs(item) > 1e16 or not math.isfinite(item)):
                raise SpecError("Numbers must be finite and within ±1e16; use null for a missing observation")
        else:
            raise SpecError("Only JSON values are accepted")
        if count > MAX_SCALARS:
            raise SpecError("The request exceeds 40000 scalar values")
    visit(value)
    return count


def dimensions(spec):
    width, height = spec.get("width", 960), spec.get("height", 540)
    if type(width) is not int or not 320 <= width <= 2000:
        raise SpecError("width must be an integer from 320 to 2000")
    if type(height) is not int or not 240 <= height <= 1400:
        raise SpecError("height must be an integer from 240 to 1400")
    return width, height


def normalize(request):
    if not isinstance(request, dict):
        raise SpecError("The chart request must be a JSON object")
    guard_json(request)
    spec = expand(request) if "preset" in request else deepcopy(request)
    if set(spec)-TOP_KEYS:
        raise SpecError(f"Unknown chart fields: {', '.join(sorted(set(spec)-TOP_KEYS))}")
    if type(spec.get("version", 1)) is not int or spec.get("version", 1) != 1:
        raise SpecError("Only chart spec version 1 is supported")
    if spec.get("colorset", "colorset1") not in {"colorset1", "colorset2"}:
        raise SpecError("colorset must be colorset1 or colorset2")
    for key, limit in (("title", 160), ("description", 400)):
        value = spec.get(key, "XY chart" if key == "title" else "")
        if not isinstance(value, str) or len(value) > limit:
            raise SpecError(f"{key} must be a string with at most {limit} characters")
        spec[key] = value
    if spec.get("factory", "chart") not in FACTORIES:
        raise SpecError("Unknown or unsupported chart factory; request capabilities for supported names")
    spec.setdefault("factory", "chart")
    spec.setdefault("colorset", "colorset1")
    for key in ("marks", "components", "args"):
        spec.setdefault(key, [])
        if not isinstance(spec[key], list) or len(spec[key]) > 32:
            raise SpecError(f"{key} must be a list of at most 32 entries")
    spec.setdefault("options", {})
    if not isinstance(spec["options"], dict):
        raise SpecError("options must be an object")
    if "data" in spec:
        if not isinstance(spec["data"], dict) or not spec["data"] or len(spec["data"]) > 32:
            raise SpecError("data must contain from 1 to 32 named array columns")
        if any(not isinstance(v, list) for v in spec["data"].values()):
            raise SpecError("data columns must be JSON arrays")
        if len({len(v) for v in spec["data"].values()}) > 1:
            raise SpecError("Named data columns must have matching row counts")
    dimensions(spec)
    return spec


def resolve(value, helper, palette):
    colors = helper.categorical_colors(palette)
    roles = helper.load_palette(palette)["roles"]
    ink = colors[0] if palette == "colorset1" else colors[1]
    tokens = {"$ink": ink, "$primary": roles["primary"], "$muted": roles["muted"],
              "$dark": roles["inkDark"], "$soft": helper.sequential_colors(palette)[0],
              "$on-ink": helper.text_on(ink), "$series": colors, "$ramp": helper.sequential_colors(palette)}
    if isinstance(value, str) and value.startswith("$"):
        if value in tokens:
            return tokens[value]
        if re.fullmatch(r"\$series:\d+", value):
            index = int(value.split(":")[1])
            if index < len(colors):
                return colors[index]
        raise SpecError(f"Unknown palette token: {value}")
    if isinstance(value, list):
        return [resolve(v, helper, palette) for v in value]
    if isinstance(value, dict):
        return {k: resolve(v, helper, palette) for k, v in value.items()}
    return value


def checked_kwargs(function, kwargs):
    signature = inspect.signature(function)
    accepts_extra = any(p.kind == p.VAR_KEYWORD for p in signature.parameters.values())
    if not accepts_extra:
        unknown = set(kwargs)-set(signature.parameters)
        if unknown:
            raise SpecError(f"Unsupported {function.__name__} parameters: {', '.join(sorted(unknown))}")
    for key, value in kwargs.items():
        if key in {"style", "styles", "whisker_style", "median_style", "outlier_style"}:
            def safe_style(item):
                if isinstance(item, dict):
                    for k, v in item.items():
                        if str(k).startswith("on") or (isinstance(v, str) and re.search(r"url\s*\(|javascript:|expression\s*\(|@import|[<>]", v, re.I)):
                            raise SpecError("Executable or external style values are not supported")
                        safe_style(v)
            safe_style(value)
        if key in {"color", "stroke", "fill", "background", "plot_background"} and isinstance(value, str) and re.search(r"url\s*\(|javascript:|[<>]", value, re.I):
            raise SpecError("External or executable paint values are not supported")
    return kwargs


def build_chart(spec, helper):
    import xy
    palette = spec["colorset"]
    theme_obj = helper.theme(palette)
    expressions = []
    children = []
    component_kinds = set()
    resolved_marks = []

    def construct(descriptor, allowed):
        if not isinstance(descriptor, dict) or set(descriptor)-{"kind", "args", "kwargs"}:
            raise SpecError("A component must contain kind, optional args and kwargs only")
        kind = descriptor.get("kind")
        if kind not in allowed:
            raise SpecError(f"Unsupported component kind: {kind}")
        args = resolve(descriptor.get("args", []), helper, palette)
        kwargs = resolve(descriptor.get("kwargs", {}), helper, palette)
        if not isinstance(args, list) or not isinstance(kwargs, dict):
            raise SpecError("Component args must be a list and kwargs an object")
        fn = getattr(xy, kind)
        params = inspect.signature(fn).parameters
        if kind in MARKS:
            if "color" in params and "color" not in kwargs and "colors" not in kwargs:
                kwargs["color"] = resolve("$ink", helper, palette)
            if "colormap" in params:
                kwargs.setdefault("colormap", helper.sequential_colors(palette))
            if "opacity" in params:
                kwargs.setdefault("opacity", 1)
            if "density" in params and kind == "scatter":
                kwargs.setdefault("density", False)
            if "stroke_width" in params:
                kwargs.setdefault("stroke_width", 0)
            if kind == "area":
                kwargs.setdefault("line_width", 0)
        if kind in {"legend", "colorbar"}:
            merged = helper.legend_style(palette) if kind == "legend" else {}
            merged.update(kwargs.get("style") or {})
            kwargs["style"] = merged
        checked_kwargs(fn, kwargs)
        try:
            signature = inspect.signature(fn)
            signature.bind(*args, **kwargs)
            obj = fn(*args, **kwargs)
        except (TypeError, ValueError) as error:
            raise SpecError(f"Invalid {kind} arguments: {error}") from error
        return obj, f"xy.{kind}(*{args!r}, **{kwargs!r})", {"kind": kind, "args": args, "kwargs": kwargs}

    for descriptor in spec["marks"]:
        obj, expr, normalized = construct(descriptor, MARKS)
        children.append(obj); expressions.append(expr); resolved_marks.append(normalized)
    for descriptor in spec["components"]:
        kind = descriptor.get("kind") if isinstance(descriptor, dict) else None
        component_kinds.add(kind)
        if kind == "theme":
            if set(descriptor)-{"kind", "args", "kwargs"} or descriptor.get("args", []) != []:
                raise SpecError("A theme component accepts kind, optional empty args and kwargs only")
            kwargs = resolve(descriptor.get("kwargs", {}), helper, palette)
            if not isinstance(kwargs, dict):
                raise SpecError("Theme kwargs must be an object")
            checked_kwargs(xy.theme, kwargs)
            theme_obj = helper.theme(palette, **kwargs)
        else:
            obj, expr, _ = construct(descriptor, COMPONENTS)
            children.append(obj); expressions.append(expr)
    is_polar = spec["factory"] in {"polar_chart", "polar_bar_chart", "radar_chart", "pie_chart", "wind_rose"}
    is_fixed = spec["factory"] in {"sankey_chart", "funnel_chart", "pie_chart", "wind_rose", "radar_chart"}
    if not is_polar and spec["factory"] != "sankey_chart":
        for kind, label in (("x_axis", "Input"), ("y_axis", "Response")):
            if kind not in component_kinds:
                children.append(getattr(xy, kind)(label=label))
                expressions.append(f"xy.{kind}(label={label!r})")
    if "legend" not in component_kinds:
        children.append(xy.legend(show=False)); expressions.append("xy.legend(show=False)")
    if spec["description"]:
        # A native title avoids relying on unsupported subtitle/callback APIs.
        title = f"{spec['title']} · {spec['description']}"
    else:
        title = spec["title"]
    width, height = dimensions(spec)
    options = resolve(spec["options"], helper, palette)
    if any(k in options for k in {"title", "width", "height", "data"}):
        raise SpecError("Put title, width, height and data in their top-level fields")
    if spec["factory"] == "facet_chart":
        by = options.get("by")
        groups = spec.get("data", {}).get(by, []) if isinstance(by, str) else by
        if isinstance(groups, list) and len({str(v) for v in groups}) > 24:
            raise SpecError("A facet request supports at most 24 groups")
    options.update(title=title, width=width if spec["factory"] == "facet_chart" else "100%", height=height)
    options.setdefault("padding", [48, 28, 60, 64])
    if spec["factory"] == "pie_chart" and spec["args"]:
        options.setdefault("colors", [resolve(f"$series:{i}", helper, palette) for i in range(len(spec["args"][0]))])
    if is_fixed:
        options.setdefault("navigation", False)
    if "data" in spec:
        options["data"] = spec["data"]
    if spec["factory"] == "sankey_chart" and "theme" not in component_kinds:
        theme_obj = helper.theme(palette, annotation_text="#ffffff")
        nodes = options.get("nodes", [])
        if nodes:
            colors = helper.categorical_colors(palette)
            options.setdefault("colors", [colors[i % 2] for i in range(len(nodes))])
    children.append(theme_obj)
    expressions.append(f"xy.theme(style={theme_obj.style!r}, palette={theme_obj.palette!r})")
    args = resolve(spec["args"], helper, palette)
    factory = getattr(xy, spec["factory"])
    try:
        chart = factory(*args, *children, **options)
    except (TypeError, ValueError) as error:
        raise SpecError(f"Invalid {spec['factory']} arguments: {error}") from error
    # Factory-owned pie/wind-rose marks otherwise inherit alpha/strokes that
    # silently change exact canonical fills. Preserve their native geometry.
    for child in getattr(chart, "children", ()):
        if spec["factory"] in {"pie_chart", "wind_rose"} and isinstance(child, xy.Mark):
            child.props["opacity"] = 1
            child.props["stroke_width"] = 0
    expr = f"xy.{spec['factory']}(*{args!r},\n    " + ",\n    ".join(expressions) + f",\n    **{options!r})"
    return chart, expr, resolved_marks


def portable_source(expr, css, width, height, factory, compat_source):
    tree = ast.parse(compat_source)
    pieces = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef)):
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                continue
            pieces.append(ast.get_source_segment(compat_source, node))
    compatibility = "\n\n".join(pieces)
    return f'''#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Editable standalone XY chart; run with uv run --script chart.py."""
from __future__ import annotations
{compatibility}
import xy
from pathlib import Path

chart = {expr}
for child in getattr(chart, "children", ()):
    if {factory!r} in {{"pie_chart", "wind_rose"}} and isinstance(child, xy.Mark):
        child.props["opacity"] = 1
        child.props["stroke_width"] = 0
output = Path(__file__).resolve().parent
chart.to_html(output / "chart.html", custom_css={css!r})
svg = chart.to_svg({'' if factory == 'facet_chart' else f'width={width}, height={height}'})
svg, repaired = repair_duplicate_line_symbol_fill(svg)
(output / "chart.svg").write_text(svg, encoding="utf-8")
chart.write_image(output / "chart.png"{'' if factory == 'facet_chart' else f', width={width}, height={height}'})
print("Created chart.html, chart.svg and chart.png")
'''


def render(request, output, skill):
    import importlib.metadata
    import xy
    output = output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise SpecError("The trusted output directory must be empty; existing artifacts are preserved")
    if importlib.metadata.version("xy") != VERSION:
        raise SpecError(f"This bridge requires xy=={VERSION}")
    helper = load_module("xy_bridge_colorsets", skill / "scripts/xy_colorsets.py")
    compat_file = skill / "scripts/xy_svg_compat.py"
    compat = load_module("xy_bridge_svg_compat", compat_file)
    spec = normalize(request)
    chart, expr, resolved_marks = build_chart(spec, helper)
    width, height = dimensions(spec)
    svg = chart.to_svg() if spec["factory"] == "facet_chart" else chart.to_svg(width=width, height=height)
    svg, repairs = compat.repair_duplicate_line_symbol_fill(svg)
    ET.fromstring(svg)
    html = chart.to_html(custom_css=helper.css(spec["colorset"]))
    png = chart.to_png() if spec["factory"] == "facet_chart" else chart.to_png(width=width, height=height)
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise SpecError("The native renderer did not return a valid PNG")
    png_width, png_height = struct.unpack(">II", png[16:24])
    source = portable_source(expr, helper.css(spec["colorset"]), width, height, spec["factory"], compat_file.read_text(encoding="utf-8"))
    compile(source, "chart.py", "exec")
    output.mkdir(parents=True, exist_ok=True)
    files = {"html": "chart.html", "svg": "chart.svg", "png": "chart.png", "source": "chart.py", "spec": "spec.json"}
    (output / files["html"]).write_text(html, encoding="utf-8", newline="\n")
    (output / files["svg"]).write_text(svg, encoding="utf-8", newline="\n")
    (output / files["png"]).write_bytes(png)
    (output / files["source"]).write_text(source, encoding="utf-8", newline="\n")
    (output / files["spec"]).write_text(json.dumps(spec, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    derived = spec["factory"] in {"sankey_chart", "wind_rose"} or any(m["kind"] in {"heatmap", "hexbin", "contour"} or m["kwargs"].get("density") or m["kwargs"].get("opacity", 1) != 1 for m in resolved_marks)
    warnings = ["Standalone HTML is an interactive snapshot; Python callbacks and future updates need a live host."]
    if derived:
        warnings.append("Native interpolation, density or alpha can produce palette-derived tones.")
    if repairs:
        warnings.append(f"Applied the bundled narrow XY 0.0.8 SVG compatibility repair to {repairs} line-symbol paths.")
    if len(svg) > 131072:
        warnings.append("SVG exceeds the Claude Mods Svg limit; use PNG or open the interactive HTML.")
    if spec["factory"] == "funnel_chart":
        warnings.append("XY 0.0.8 funnel label contrast uses two native paints outside the selected palette.")
    if len(spec["title"])+len(spec["description"]) > 65:
        warnings.append("Long title/description text should be inspected at the target viewport size.")
    array_lengths = [len(v) for v in spec.get("data", {}).values()]
    array_lengths.extend(len(a) for m in spec["marks"] for a in m.get("args", []) if isinstance(a, list))
    array_lengths.extend(len(a) for a in spec["args"] if isinstance(a, list))
    return {"schema_version": 1, "title": spec["title"], "palette": spec["colorset"], "width": width,
            "height": height, "factory": spec["factory"], "files": files, "svg_bytes": len(svg.encode()),
            "png_bytes": len(png), "png_width": png_width, "png_height": png_height,
            "svg_compat_repairs": repairs, "warnings": warnings,
            "paint_scope": "native-contrast-exception" if spec["factory"] == "funnel_chart" else "derived" if derived else "canonical-defaults; explicit request colors preserved",
            "counts": {"marks": len(spec["marks"]), "rows": max(array_lengths, default=0)}}


def capabilities():
    fields = {}
    for name in PRESETS:
        if name in {"line", "scatter", "area", "step", "stem", "polar", "polar-bars", "log-scale", "animation", "annotations", "hexbin"}:
            fields[name] = ["x", "y"]
        elif name in {"bar", "horizontal-bars"}:
            fields[name] = ["categories", "values"]
        elif name in {"grouped-bars", "stacked-bars", "normalized-bars"}:
            fields[name] = ["categories", "values", "series"]
        elif name in {"histogram", "ecdf", "box", "violin"}:
            fields[name] = ["values"]
        else:
            fields[name] = {"stairs": ["values", "edges"], "error-bars": ["x", "center", "lower", "upper"],
                "error-band": ["x", "center", "lower", "upper"], "heatmap": ["x", "y", "z"],
                "contour": ["x", "y", "z"], "filled-contour": ["x", "y", "z"],
                "segments": ["x0", "y0", "x1", "y1"], "triangle-mesh": ["x0", "y0", "x1", "y1", "x2", "y2"],
                "ribbon": ["x0", "x1", "source_lo", "source_hi", "target_lo", "target_hi"],
                "sankey": ["nodes", "links"], "funnel": ["stage", "value"], "radar": ["categories", "values"],
                "pie": ["labels", "values"], "donut": ["labels", "values"], "wind-rose": ["direction", "speed"],
                "facets": ["x", "y", "group"]}[name]
    return {"version": VERSION, "spec_version": 1, "default_colorset": "colorset1",
            "colorset_policy": "Every new chart defaults to colorset1, including after a previous colorset2 chart. Use colorset2 only for an explicit user request or palette selection; category count does not change the default.",
            "presets": list(PRESETS), "factories": sorted(FACTORIES),
            "marks": sorted(MARKS), "components": sorted(COMPONENTS),
            "preset_data_columns": fields,
            "preset_contract": "Supply every listed column for a preset or omit data for labelled synthetic defaults. Grouped values are rows by series; grid z is y rows by x columns. Uncertainty lower/upper are absolute bounds. Sankey links are [source,target,value] triples; nodes are ordered labels.",
            "generic_contract": {"version": 1, "factory": "allowlisted factory", "args": "optional positional JSON arguments for factory-owned data", "data": "optional named equal-length array columns", "marks": [{"kind": "allowlisted mark", "args": [], "kwargs": {}}], "components": [{"kind": "allowlisted component", "args": [], "kwargs": {}}], "options": "public chart/factory keyword arguments; consult focused skill references", "width": 960, "height": 540},
            "limits": {"request_bytes": MAX_BYTES, "scalars": MAX_SCALARS, "marks": 32, "components": 32,
                       "width": [320, 2000], "height": [240, 1400], "facets": 24},
            "palette_tokens": ["$ink", "$primary", "$muted", "$dark", "$soft", "$on-ink", "$series", "$series:N", "$ramp"],
            "example": {"version": 1, "title": "Supplied trend", "colorset": "colorset1", "factory": "chart",
                        "marks": [{"kind": "line", "args": [[1, 2, 3], [4, 7, 5]], "kwargs": {"color": "$ink", "width": 2}}]},
            "scope": "Declarative native XY construction only; no arbitrary code, registered plugins, live Python callbacks, or source URL loading."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--skill-dir", type=Path)
    parser.add_argument("--capabilities", action="store_true")
    args = parser.parse_args()
    try:
        if args.capabilities:
            result = capabilities()
        else:
            if args.output_dir is None:
                raise SpecError("Pass a trusted --output-dir")
            data = sys.stdin.buffer.read(MAX_BYTES+1)
            if len(data) > MAX_BYTES:
                raise SpecError("Request exceeds 1 MiB")
            def reject_constant(value):
                raise SpecError(f"Nonstandard JSON number {value}; use null for missing values")
            request = json.loads(data, parse_constant=reject_constant)
            with contextlib.redirect_stdout(sys.stderr):
                result = render(request, args.output_dir, skill_path(args.skill_dir))
        print(json.dumps(result, allow_nan=False))
        return 0
    except Exception as error:
        # Native validators can raise IndexError/AttributeError for malformed
        # chart data. Preserve the CLI's structured-error protocol for clients.
        print(json.dumps({"error": {"code": "invalid_chart_request", "message": str(error)[:600]}}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
