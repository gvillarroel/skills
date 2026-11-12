#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Small declarative XY examples; no renderer, repository imports or evaluation."""

from __future__ import annotations

import math
import random

PRESETS = (
    "line", "scatter", "area", "bar", "grouped-bars", "stacked-bars",
    "normalized-bars", "horizontal-bars", "histogram", "step", "stairs", "stem",
    "ecdf", "box", "violin", "error-bars", "error-band", "heatmap", "hexbin",
    "contour", "filled-contour", "segments", "triangle-mesh", "ribbon", "sankey",
    "funnel", "polar", "polar-bars", "radar", "pie", "donut", "wind-rose",
    "annotations", "facets", "log-scale", "animation",
)


def call(kind, *args, **kwargs):
    return {"kind": kind, "args": list(args), "kwargs": kwargs}


def expand(request):
    """Expand documented data contracts without replacing supplied observations."""
    name = request.get("preset")
    if name not in PRESETS:
        raise ValueError(f"Unknown preset; choose one of {', '.join(PRESETS)}")
    allowed = {"preset", "colorset", "title", "data", "width", "height", "description"}
    unknown = set(request) - allowed
    if unknown:
        raise ValueError(f"Unknown preset fields: {', '.join(sorted(unknown))}")
    supplied = request.get("data")
    if supplied is not None and not isinstance(supplied, dict):
        raise ValueError("Preset data must be an object of documented columns")
    d = supplied or {}
    used = set()

    def columns(defaults):
        used.update(defaults)
        if supplied is not None:
            missing = set(defaults) - set(d)
            if missing:
                raise ValueError(f"Preset {name} requires data columns: {', '.join(sorted(defaults))}")
        return [d.get(k, v) for k, v in defaults.items()]

    result = {"version": 1, "title": request.get("title", name.replace("-", " ").title()),
              "colorset": request.get("colorset", "colorset1"), "factory": "chart",
              "marks": [], "components": [], "options": {},
              "width": request.get("width", 960), "height": request.get("height", 540),
              "description": request.get("description", "Supplied observations" if supplied is not None else "Synthetic example data")}
    m, c, o = result["marks"], result["components"], result["options"]
    x0, y0 = [1, 2, 3, 4, 5, 6], [3, 5, 4, 7, 6, 8]
    rng = random.Random(73)
    samples0 = [rng.gauss(5, 1) for _ in range(64)]
    if name in {"line", "scatter", "area", "step", "stem", "polar", "polar-bars", "log-scale", "animation", "annotations"}:
        x, y = columns({"x": [i * 60 for i in range(6)] if name in {"polar", "polar-bars"} else x0, "y": y0})
        kind = {"polar": "line", "polar-bars": "bar", "log-scale": "line", "animation": "line", "annotations": "line"}.get(name, name)
        kw = {"color": "$ink"}
        if kind == "scatter":
            kw.update(size=7, opacity=1, density=False, stroke_width=0)
        elif kind in {"area", "bar"}:
            kw.update(opacity=1)
            kw.update({"line_width": 0} if kind == "area" else {"stroke_width": 0})
        m.append(call(kind, x, y, **kw))
        if name in {"polar", "polar-bars"}:
            result["factory"] = "polar_bar_chart" if name == "polar-bars" else "polar_chart"
        if name == "log-scale":
            c.append(call("x_axis", label="Input", type_="log"))
        if name == "animation":
            c.append(call("animation", enabled=True, duration=800, enter="reveal"))
        if name == "annotations":
            c.extend([call("hline", 5, text="Reference", color="$muted"),
                      call("text", x[-1], y[-1], "Latest", color="$ink", dx=-50, dy=-12)])
    elif name in {"bar", "horizontal-bars"}:
        categories, values = columns({"categories": ["North", "South", "West"], "values": [4, 7, 6]})
        m.append(call("bar", categories, values, color="$ink", opacity=1,
                      orientation="horizontal" if name == "horizontal-bars" else "vertical"))
    elif name in {"grouped-bars", "stacked-bars", "normalized-bars"}:
        categories, values, series = columns({"categories": ["North", "South", "West"],
                                              "values": [[4, 5, 6], [2, 3, 2], [3, 2, 4]],
                                              "series": ["Lab", "Field", "Remote"]})
        mode = {"grouped-bars": "grouped", "stacked-bars": "stacked", "normalized-bars": "normalized"}[name]
        m.append(call("bar", categories, values, series=series, colors=[f"$series:{i}" for i in range(len(series))], mode=mode, opacity=1))
        c.append(call("legend", loc="upper left", anchor=[0, -.20], ncols=min(len(series), 3)))
        o["padding"] = [44, 28, 120, 64]
    elif name in {"histogram", "ecdf", "box", "violin"}:
        values, = columns({"values": samples0})
        kind = {"histogram": "hist"}.get(name, name)
        kw = {"color": "$ink"}
        if kind != "ecdf":
            kw["opacity"] = 1
        if kind == "hist":
            kw["bins"] = 12
        if kind in {"box", "violin"}:
            kw["x"] = [0] * len(values)
        if kind == "box":
            kw.update(style={"stroke-width": 0}, whisker_style={"stroke": "$ink", "stroke-width": 1.5},
                      median_style={"stroke": "$on-ink", "stroke-width": 2})
        m.append(call(kind, values, **kw))
    elif name == "stairs":
        values, edges = columns({"values": [2, 5, 3, 6], "edges": [0, 1, 2, 3, 4]})
        m.append(call("stairs", values, edges, color="$ink", width=2))
    elif name in {"error-bars", "error-band"}:
        x, center, lower, upper = columns({"x": x0, "center": y0,
                                         "lower": [v - .6 for v in y0], "upper": [v + 1.1 for v in y0]})
        if not len(x) == len(center) == len(lower) == len(upper):
            raise ValueError("All uncertainty columns must have equal length")
        if any(lo > v or hi < v for lo, v, hi in zip(lower, center, upper)):
            raise ValueError("Supplied lower/upper boundaries must contain each center")
        if name == "error-bars":
            m.extend([call("errorbar", x, center, yerr=[[v-lo for v, lo in zip(center, lower)],
                                                        [hi-v for hi, v in zip(upper, center)]],
                           cap_size=.16, color="$ink", width=2),
                      call("scatter", x, center, color="$dark", size=5, opacity=1, density=False)])
        else:
            m.extend([call("error_band", x, lower, upper, color="$soft", opacity=1),
                      call("line", x, center, color="$ink", width=2)])
    elif name in {"heatmap", "contour", "filled-contour"}:
        xs = [-2 + i/3 for i in range(13)]
        ys = [-2 + i/3 for i in range(13)]
        grid = [[math.exp(-(x*x+y*y)) for x in xs] for y in ys]
        x, y, z = columns({"x": xs, "y": ys, "z": grid})
        kw = {"x": x, "y": y, "colormap": "$ramp", "opacity": 1}
        if name != "heatmap":
            kw.update(levels=7, filled=name == "filled-contour")
        m.append(call("heatmap" if name == "heatmap" else "contour", z, **kw))
        c.append(call("colorbar", title="Value"))
    elif name == "hexbin":
        xs = [rng.gauss(0, 1) for _ in range(800)]
        ys = [v*.65+rng.gauss(0, .5) for v in xs]
        x, y = columns({"x": xs, "y": ys})
        m.append(call("hexbin", x, y, gridsize=24, mincnt=1, colormap="$ramp", opacity=1))
        c.append(call("colorbar", title="Count"))
    elif name == "segments":
        x0, y0, x1, y1 = columns({"x0": [0, 0, 1], "y0": [0, 2, 1], "x1": [2, 1, 3], "y1": [1, 3, 0]})
        m.append(call("segments", x0, y0, x1, y1, color="$ink", width=3))
    elif name == "triangle-mesh":
        x0, y0, x1, y1, x2, y2 = columns({"x0": [0, 1], "y0": [0, 0], "x1": [1, 2], "y1": [0, 0], "x2": [.5, 1.5], "y2": [1, 1.5]})
        m.append(call("triangle_mesh", x0, y0, x1, y1, x2, y2, color="$ink", opacity=1))
    elif name == "ribbon":
        x0, x1, lo0, hi0, lo1, hi1 = columns({"x0": [0, 0], "x1": [2, 2], "source_lo": [0, 2],
                                             "source_hi": [1, 3], "target_lo": [1, 0], "target_hi": [2, 1]})
        m.append(call("ribbon", x0, x1, lo0, hi0, lo1, hi1, color="$ink", opacity=1))
    elif name == "sankey":
        nodes, links = columns({"nodes": ["Input", "Lab", "Field", "Output", "Loss"],
                               "links": [["Input", "Lab", 12], ["Input", "Field", 8],
                                         ["Lab", "Output", 10], ["Field", "Output", 8], ["Lab", "Loss", 2]]})
        result["factory"] = "sankey_chart"
        result["args"] = [links]
        o.update(nodes=nodes, colors=[f"$series:{i%2}" for i in range(len(nodes))], link_opacity=1,
                 labels=True, navigation=False)
        c.append(call("theme", annotation_text="#ffffff"))
    elif name == "funnel":
        stage, value = columns({"stage": ["Visits", "Leads", "Trials", "Paid"], "value": [1200, 780, 420, 210]})
        result["factory"] = "funnel_chart"
        m.append(call("funnel", stage, value, colors=[f"$series:{i}" for i in range(len(stage))], geometry="bar", orientation="horizontal", opacity=1))
        o["navigation"] = False
    elif name in {"pie", "donut"}:
        labels, values = columns({"labels": ["Lab", "Field", "Remote"], "values": [45, 35, 20]})
        result["factory"], result["args"] = "pie_chart", [labels, values]
        o.update(hole=0 if name == "pie" else .55, colors=[f"$series:{i}" for i in range(len(labels))], navigation=False)
    elif name == "radar":
        categories, values = columns({"categories": ["Speed", "Cost", "Reach", "Quality", "Capacity"], "values": [4, 3, 5, 4, 2]})
        result["factory"], result["args"] = "radar_chart", [categories]
        m.append(call("line", list(range(len(values))), values, color="$ink", width=2))
        o.update(fill=False, navigation=False)
    elif name == "wind-rose":
        direction, speed = columns({"direction": [i*15 for i in range(24)], "speed": [1+(i%5) for i in range(24)]})
        result["factory"], result["args"] = "wind_rose", [direction, speed]
        o.update(sectors=12, speed_bins=[0, 2, 4, 6], navigation=False)
    elif name == "facets":
        x, y, group = columns({"x": [1, 2, 3, 1, 2, 3], "y": [3, 5, 4, 4, 6, 7], "group": ["Lab"]*3+["Field"]*3})
        result["factory"], result["data"] = "facet_chart", {"x": x, "y": y, "group": group}
        o.update(by="group", cols=2, share_x=True, share_y=True)
        m.append(call("scatter", "x", "y", color="$ink", size=7, opacity=1, density=False))
    if supplied is not None and set(d) - used:
        raise ValueError(f"Unknown data columns for {name}: {', '.join(sorted(set(d)-used))}")
    return result
