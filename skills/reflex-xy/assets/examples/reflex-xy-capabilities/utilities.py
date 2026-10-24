"""Finite style vocabularies and a compositional custom mark for XY 0.0.8."""

from __future__ import annotations

import numpy as np
import xy

from xy_colorsets import categorical_colors, legend_style, load_palette, theme

SYMBOLS = (
    "circle", "cross", "diamond", "hexagon", "horizontal_line", "pentagon",
    "pixel", "plus_line", "point", "square", "star", "thin_diamond",
    "triangle", "triangle_down", "triangle_left", "triangle_right",
    "vertical_line", "x", "x_line",
)


def cases(palette: str) -> list[dict]:
    colors = categorical_colors(palette, 4)
    ink = load_palette(palette)["roles"]["inkDark"]
    result = []
    symbols = []
    for index, symbol in enumerate(SYMBOLS):
        x, y = index % 3, 6 - index // 3
        line_only = symbol in {"horizontal_line", "vertical_line", "plus_line", "x_line"}
        paint = colors[index % 4]
        symbols.append(xy.scatter([x], [y], symbol=symbol, size=16,
                                  color=paint, opacity=1, density=False,
                                  stroke=paint if line_only else None,
                                  stroke_width=2 if line_only else 0))
        symbols.append(xy.text(x, y - 0.42, symbol, anchor="middle", color=ink,
                               style={"font-size": "10px"}))
    result.append(dict(
        id="point-symbols", title="Every point symbol", category="Styling and extensions",
        summary="All 19 shipped point symbols, at a common marker size.",
        detail="Names match the installed validator and use the same requested marker size. Some names are aliases. The four line-only glyphs use an explicit two-pixel stroke so they remain visible; filled glyphs have no decorative outline. Shape can carry category identity alongside either palette.",
        chart=xy.scatter_chart(*symbols, xy.x_axis(domain=(-0.6, 2.6), show=False),
                               xy.y_axis(domain=(-0.8, 6.6), show=False), theme(palette),
                               title="Point symbol vocabulary", width="100%", height=650,
                               padding=(45, 24, 24, 24)),
        apis=["scatter", "scatter_chart", "text", "x_axis", "y_axis", "theme"],
        parameters={"scatter": ["symbol", "size", "color", "opacity", "density", "stroke", "stroke_width"],
                    "text": ["anchor", "color", "style"]},
        paint_scope="exact", interaction="cartesian", expect_labels=["Point symbol vocabulary"],
    ))
    lines = []
    for i, dash in enumerate(("solid", "dashed", "dotted", "dashdot")):
        lines.append(xy.line([0, 1, 2, 3, 4], np.array([1, 1.5, 1.1, 1.7, 1.4]) + i * 1.8,
                             color=colors[i], width=3, dash=dash, name=dash))
    lines.append(xy.line([0, 1, 2, 3, 4], [9, 9.5, 9.1, 9.7, 9.4], color=colors[0],
                         width=3, dash=[10, 3, 2, 3], name="custom array", curve="smooth"))
    result.append(dict(
        id="line-dash-curves", title="Dash patterns and curve interpolation", category="Styling and extensions",
        summary="Four named dash presets, one custom dash array, and a smooth curve.",
        detail="Dash length is a visual encoding independent of color. The upper series uses a documented smooth curve; the others preserve linear segments. The guide does not imply identical wide-line joins across every renderer.",
        chart=xy.line_chart(*lines, xy.x_axis(label="Position"),
                            xy.y_axis(label="Separated series", domain=(0, 13)),
                            xy.legend(loc="upper left", ncols=2, style=legend_style(palette)),
                            theme(palette), title="Line style vocabulary", width="100%", height=480,
                            padding=(50, 30, 54, 68)),
        apis=["line", "line_chart", "legend", "theme"],
        parameters={"line": ["dash", "curve", "width", "color", "name"], "legend": ["ncols", "loc", "style"]},
        paint_scope="exact", interaction="cartesian", expect_labels=["Line style vocabulary"],
    ))
    style_chart = xy.chart(
        xy.bar([0, 1, 2, 3], [3, 5, 4, 6], width=0.55, color=colors[0], opacity=1,
               style={"fill": colors[0], "fill-opacity": 1, "border-radius": "7px"}),
        xy.line([0, 1, 2, 3], [4, 6, 5, 7], name="styled path", color=colors[1],
                style={"stroke": colors[1], "stroke-width": "3px", "stroke-opacity": 1,
                       "stroke-dasharray": "8 4", "stroke-linecap": "round"}),
        xy.scatter([0, 1, 2, 3], [4, 6, 5, 7], color=colors[2], size=12, opacity=1,
                   style={"marker-shape": "diamond", "opacity": 1}),
        xy.x_axis(label="Category", tick_values=[0, 1, 2, 3], tick_labels=["A", "B", "C", "D"],
                  style={"label_font_weight": "bold", "grid_dash": "dotted"}),
        xy.y_axis(label="Value", domain=(0, 9)),
        xy.legend(loc="upper left", style=legend_style(palette)), theme(palette),
        title="Mark styles and theme tokens", width="100%", height=480,
        padding=(50, 30, 54, 68),
    )
    result.append(dict(
        id="mark-style-properties", title="Mark styles and theme tokens", category="Styling and extensions",
        summary="Rounded bars, a styled path and diamond markers use supported mark properties.",
        detail="Style keys are validated against each mark kind. Browser DOM/CSS slots have a larger surface than native export; the API catalogue lists all 48 slots and their renderer support. Wedge gaps are demonstrated by the pie/donut example.",
        chart=style_chart, apis=["chart", "bar", "line", "scatter", "theme", "CHART_DOM_SLOTS"],
        parameters={"bar": ["style", "width"], "line": ["style"], "scatter": ["style"], "x_axis": ["style"]},
        paint_scope="exact", interaction="cartesian", expect_labels=["Mark styles and theme tokens"],
    ))

    def build_custom(context: xy.MarkContext):
        return [
            xy.line(context.columns["x"], context.columns["y"], color=context.options["color"], width=3),
            xy.scatter(context.columns["x"], context.columns["y"], color=context.options["color"],
                       symbol="diamond", size=10, opacity=1, density=False),
        ]

    plugin = xy.MarkPlugin(
        "gallery_normalized_path", build=build_custom, columns=("x", "y"),
        calc=lambda columns: {"x": np.asarray(columns["x"]), "y": np.asarray(columns["y"]) / 10},
        doc="Normalize source units and compose a line with diamond markers.",
    )
    xy.register_mark(plugin, replace=True)
    if plugin.name not in xy.registered_marks():
        raise RuntimeError("Custom mark registration failed")
    custom = xy.chart(
        xy.mark(plugin.name, x="time", y="value", color=colors[0], name="Normalized readings"),
        xy.x_axis(label="Time"), xy.y_axis(label="Value / 10", domain=(0, 8)),
        theme(palette), data={"time": [0, 1, 2, 3, 4], "value": [15, 35, 28, 57, 63]},
        title="Custom mark composition", width="100%", height=480, padding=(50, 30, 54, 68),
    )
    result.append(dict(
        id="custom-mark-composition", title="Extend XY by composing marks", category="Styling and extensions",
        summary="A registered plugin normalizes columns and emits built-in line/scatter marks.",
        detail="The shipped extension point runs a Python calculation over declared columns and composes built-in marks one level deep. It does not install a custom WebGL shader. The portable source demonstrates registration, discovery and cleanup.",
        chart=custom, apis=["MarkPlugin", "MarkContext", "register_mark", "registered_marks", "mark"],
        parameters={"MarkPlugin": ["name", "build", "columns", "calc", "doc"],
                    "register_mark": ["replace"], "mark": ["data", "name", "fields"]},
        paint_scope="exact", interaction="cartesian", expect_labels=["Custom mark composition"],
    ))
    return result
