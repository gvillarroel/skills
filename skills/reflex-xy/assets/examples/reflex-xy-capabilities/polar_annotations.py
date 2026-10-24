"""Public XY 0.0.8 polar factories and annotation compositions.

The gallery builder supplies the adjacent xy_colorsets runtime helper. All data,
domains, sizes, and layouts are identical across the two selected palettes.
"""
from __future__ import annotations

import numpy as np
import xy

from xy_colorsets import categorical_colors, legend_style, load_palette, theme


def _record(slug, title, category, summary, detail, chart, parameters, labels,
            interaction="polar", paint_scope="exact"):
    return {"id": slug, "title": title, "category": category,
            "summary": summary, "detail": detail, "chart": chart,
            "apis": list(parameters), "parameters": parameters,
            "paint_scope": paint_scope, "interaction": interaction,
            "expect_labels": labels}


def _opaque_factory(chart):
    """Override generated public Mark props before the chart is compiled.

    pie_chart/wind_rose generate bar children with a translucent default and
    have no opacity keyword. Mark.props is a public dataclass field; changing
    these paint props preserves factory-computed slices, counts, and geometry.
    """
    for child in chart.children:
        if isinstance(child, xy.Mark) and child.kind in {"bar", "column"}:
            child.props.update(opacity=1.0, stroke_width=0.0)
    return chart


def cases(palette: str) -> list[dict]:
    colors = categorical_colors(palette, 6)
    roles = load_palette(palette)["roles"]
    frame = {"width": "100%", "height": 520, "padding": [48, 72, 48, 72]}
    def legend(**kwargs):
        # A footer leaves the rim, spoke labels, and filled sectors unobscured
        # at both full native width and a narrow responsive HTML width.
        return xy.legend(style=legend_style(palette), anchor=(0, 0), ncols=2, **kwargs)
    output = []

    angle = np.linspace(0, 360, 73)
    signal = 6 + 1.5 * np.cos(np.deg2rad(angle * 2))
    envelope = 4.2 + 0.7 * np.sin(np.deg2rad(angle * 3))
    title = "Polar marks: one angle, three encodings"
    chart = xy.polar_chart(
        xy.area(angle, envelope, color=colors[2], opacity=1, line_width=0,
                name="Inner area"),
        xy.line(angle, signal, color=colors[0], width=2.5, name="Response"),
        xy.scatter(angle[::6], signal[::6], color=colors[1], size=7,
                   opacity=1, stroke_width=0, name="Samples"),
        xy.theta_axis(unit="degrees", zero="N", direction="clockwise",
                      tick_values=[0, 90, 180, 270],
                      tick_labels=["North", "East", "South", "West"]),
        xy.r_axis(domain=(0, 10), tick_values=[2, 4, 6, 8, 10]),
        legend(loc="upper left"), theme(palette), title=title, **frame,
    )
    output.append(_record(
        "polar-composition", title, "Polar charts",
        "Area, line, and sampled points reuse ordinary marks in polar coordinates.",
        "Degrees start at North and increase clockwise. The opaque inner region, "
        "outer response, and sampled observations share one radial domain. Polar "
        "zoom is off by default because the fixed center and full rim are meaningful.",
        chart, {"polar_chart": ["title", "width", "height", "padding"],
                "area": ["x", "y", "color", "opacity", "line_width", "name"],
                "line": ["x", "y", "color", "width", "name"],
                "scatter": ["x", "y", "color", "size", "opacity", "stroke_width", "name"],
                "theta_axis": ["unit", "zero", "direction", "tick_values", "tick_labels"],
                "r_axis": ["domain", "tick_values"],
                "legend": ["style", "loc", "anchor", "ncols"], "theme": ["palette"]},
        ["Polar marks", "North", "Response", "Samples"],
    ))

    bearings = [0, 60, 120, 180, 240, 300]
    counts = [5, 7, 4, 6, 3, 5]
    bars = [xy.bar([direction], [count], base=1, width=46,
                   wedge_gap=3, corner_radius=2, color=color,
                   opacity=1, stroke_width=0, name=f"Sector {index + 1}")
            for index, (direction, count, color) in enumerate(zip(bearings, counts, colors))]
    title = "Polar bars: radial magnitude"
    chart = xy.polar_bar_chart(
        *bars,
        xy.theta_axis(unit="degrees", zero="E", direction="counterclockwise",
                      tick_values=bearings),
        xy.r_axis(domain=(0, 9), hole=0.12, tick_values=[2, 4, 6, 8]),
        legend(loc="upper left"), theme(palette), title=title, **frame,
    )
    output.append(_record(
        "polar-bars", title, "Polar charts",
        "Angular bar widths, annular bases, rounded corners, and pixel gaps.",
        "Each sector is a genuine bar with a one-unit radial base. Angular width "
        "is measured in degrees; wedge gaps and corner rounding are renderer "
        "geometry. East is zero and angles increase counterclockwise. The "
        "two-column legend is anchored below the polar rim so narrow displays "
        "keep every angular tick readable.",
        chart, {"polar_bar_chart": ["title", "width", "height", "padding"],
                "bar": ["x", "y", "base", "width", "wedge_gap", "corner_radius", "color", "opacity", "stroke_width", "name"],
                "theta_axis": ["unit", "zero", "direction", "tick_values"],
                "r_axis": ["domain", "hole", "tick_values"],
                "legend": ["style", "loc", "anchor", "ncols"], "theme": ["palette"]},
        ["Polar bars", "Sector 1", "Sector 6"],
    ))

    title = "Radar: categorical spokes"
    chart = xy.radar_chart(
        ["Speed", "Range", "Power", "Agility", "Comfort"],
        xy.area([5.5, 7.0, 4.0, 6.0, 5.0], color=colors[2], opacity=1,
                line_width=0, name="Baseline area"),
        xy.line([7.5, 5.0, 8.0, 6.5, 7.0], color=colors[0], width=2.5,
                name="Candidate outline"),
        xy.theta_axis(unit="degrees", zero="N", direction="clockwise", grid_shape="linear"),
        xy.r_axis(domain=(0, 10), tick_values=[2, 4, 6, 8, 10]),
        legend(loc="upper left"), theme(palette), fill=True, title=title, **frame,
    )
    output.append(_record(
        "radar", title, "Polar charts",
        "An opaque area and an outline close automatically across named spokes.",
        "The public radar factory derives evenly spaced angles and closes the "
        "last segment at a full turn. Polygonal grids use theta_axis(grid_shape='linear'); "
        "each mark provides exactly one value per category.",
        chart, {"radar_chart": ["categories", "fill", "title", "width", "height", "padding"],
                "area": ["x", "color", "opacity", "line_width", "name"],
                "line": ["x", "color", "width", "name"],
                "theta_axis": ["unit", "zero", "direction", "grid_shape"],
                "r_axis": ["domain", "tick_values"],
                "legend": ["style", "loc", "anchor", "ncols"], "theme": ["palette"]},
        ["Radar", "Speed", "Comfort", "Candidate outline"],
    ))

    for slug, hole, title in (("pie-solid", 0.0, "Pie: direct shares"),
                              ("pie-donut", 0.48, "Donut: shares around a hole")):
        chart = _opaque_factory(xy.pie_chart(
            ["North", "South", "East", "West"], [40, 30, 20, 10],
            legend(loc="upper left"), theme(palette),
            hole=hole, pad=3, colors=colors[:4], corner_radius=3,
            show_values=True, show_percent=True, title=title, **frame,
        ))
        output.append(_record(
            slug, title, "Polar charts",
            "The pie factory computes angular shares, values, and percentages.",
            f"hole={hole:g} selects this {'solid pie' if hole == 0 else 'donut'}. "
            "The four values total 100. Public generated Mark.props set opacity=1 "
            "before compilation, replacing the factory's translucent bar default; "
            "computed slice spans and tooltips are unchanged.",
            chart, {"pie_chart": ["labels", "values", "hole", "pad", "colors", "corner_radius", "show_values", "show_percent", "title", "width", "height", "padding"],
                    "Mark": ["props"], "legend": ["style", "loc", "anchor", "ncols"], "theme": ["palette"]},
            ["Pie" if hole == 0 else "Donut", "North", "South"],
        ))

    index = np.arange(160)
    directions = (index * 137.5 + 25 * np.sin(index * 0.17)) % 360
    speeds = (index % 8) + 1
    title = "Wind rose: frequency by direction and speed"
    chart = _opaque_factory(xy.wind_rose(
        directions, speeds,
        xy.theta_axis(unit="degrees", zero="N", direction="clockwise",
                      tick_values=[0, 90, 180, 270], tick_labels=["N", "E", "S", "W"]),
        xy.r_axis(domain=(0, 30), tick_values=[10, 20, 30], tick_labels=["", "", "30"]),
        legend(loc="upper left", title="Speed band"), theme(palette),
        sectors=8, speed_bins=[2, 4, 6, 8], title=title, **frame,
    ))
    output.append(_record(
        "wind-rose", title, "Polar charts",
        "160 observations aggregate into eight directions and four speed bands.",
        "The public factory bins observations and stacks their frequency counts. "
        "The highest authored speed edge covers every observation. Public Mark "
        "paint props make each generated band opaque. Inner ring labels are "
        "omitted so dark solid bands retain legible labels; the outer ring is 30. Wind-rose radial zoom is "
        "enabled by default because radius measures a frequency count.",
        chart, {"wind_rose": ["directions", "speeds", "sectors", "speed_bins", "title", "width", "height", "padding"],
                "Mark": ["props"], "theta_axis": ["unit", "zero", "direction", "tick_values", "tick_labels"],
                "r_axis": ["domain", "tick_values", "tick_labels"], "legend": ["style", "loc", "title", "anchor", "ncols"], "theme": ["palette"]},
        ["Wind rose", "Speed band"],
    ))

    angle = np.linspace(-60, 240, 61)
    radius = 4 + 2.5 * np.cos(np.deg2rad(angle * 1.4))
    title = "Polar axes: sector and shifted origin"
    chart = xy.polar_chart(
        xy.line(angle, radius, color=colors[0], width=2.5, name="Radial response"),
        xy.scatter(angle[::6], radius[::6], color=colors[1], size=7,
                   opacity=1, stroke_width=0),
        xy.theta_axis(unit="degrees", zero="N", direction="clockwise",
                      sector=(-60, 240), grid_shape="circular",
                      tick_values=[-60, 0, 60, 120, 180, 240]),
        xy.r_axis(type_="symlog", constant=1, domain=(-3, 10), origin=-3,
                  tick_values=[-3, 0, 3, 6, 9]),
        legend(loc="upper left"), theme(palette), title=title, **frame,
    )
    output.append(_record(
        "polar-sectors", title, "Polar charts",
        "A partial angular sector and a symmetric-log radius retain their geometry.",
        "The theta sector spans -60 to 240 degrees. A shifted radial origin of -3 "
        "is an explicit frame choice; symlog uses a one-unit "
        "linear region around zero. The same projection is exported natively.",
        chart, {"polar_chart": ["title", "width", "height", "padding"],
                "line": ["x", "y", "color", "width", "name"],
                "scatter": ["x", "y", "color", "size", "opacity", "stroke_width"],
                "theta_axis": ["unit", "zero", "direction", "sector", "grid_shape", "tick_values"],
                "r_axis": ["type_", "constant", "domain", "origin", "tick_values"],
                "legend": ["style", "loc", "anchor", "ncols"], "theme": ["palette"]},
        ["Polar axes", "Radial response"],
    ))

    x = np.arange(1, 12)
    y = np.array([4.0, 4.8, 5.2, 4.9, 6.2, 6.8, 6.1, 7.2, 6.5, 7.4, 7.0])

    def cartesian(*children, title):
        return xy.chart(
            *children, xy.x_axis(label="Input", domain=(0, 12), tick_count=7),
            xy.y_axis(label="Response", domain=(0, 10), tick_count=6),
            xy.legend(show=False), theme(palette), title=title, **frame,
        )

    title = "Annotation guides: rules and intervals"
    chart = cartesian(
        xy.x_band(3, 5, text="Input window", color=roles["muted"], opacity=0.18,
                  style={"label_color": "#000000", "label_opacity": 1}),
        xy.y_band(1, 2.5, text="Reference band", color=roles["muted"], opacity=0.18,
                  style={"label_color": "#000000", "label_opacity": 1}),
        xy.line(x, y, color=colors[0], width=2.5),
        xy.hline(8.5, text="Upper guide", color=colors[1], width=1.5, opacity=1),
        xy.vline(9, text="Review point", color=colors[1], width=1.5, opacity=1),
        title=title,
    )
    output.append(_record(
        "annotation-guides", title, "Annotations",
        "Horizontal and vertical rules complement intervals on both axes.",
        "x_band and y_band use canonical neutral paints at 18% alpha so the "
        "observed line remains visible. Their composite pixels are derived colors. Rules preserve "
        "their measurement meaning as thin semantic lines. The original observed "
        "response remains a separate red line.",
        chart, {"chart": ["title", "width", "height", "padding"],
                "x_band": ["x0", "x1", "text", "color", "opacity", "style"],
                "y_band": ["y0", "y1", "text", "color", "opacity", "style"],
                "hline": ["y", "text", "color", "width", "opacity"],
                "vline": ["x", "text", "color", "width", "opacity"],
                "line": ["x", "y", "color", "width"],
                "x_axis": ["label", "domain", "tick_count"],
                "y_axis": ["label", "domain", "tick_count"], "legend": ["show"], "theme": ["palette"]},
        ["Annotation guides", "Input", "Response", "Upper guide", "Review point"],
        interaction="cartesian", paint_scope="derived",
    ))

    title = "Annotation notes: data anchors and offsets"
    chart = cartesian(
        xy.scatter([2, 4, 6, 8, 10], [4, 6, 5, 7, 4], color=colors[0],
                   size=10, opacity=1, stroke_width=0),
        xy.text(1, 8.5, "Text anchor", dx=0, dy=0, color=colors[1], anchor="start"),
        xy.label(5, 8.5, "Label alias", dx=0, dy=0, color=colors[1], anchor="start"),
        xy.arrow(8.8, 8, 8, 7, text="Arrow", color=colors[1], width=1.5, opacity=1),
        xy.callout(4, 6, "Callout detail", dx=-32, dy=-58,
                   color=colors[1], width=1.5, opacity=1, anchor="middle"),
        xy.marker(10, 4, text="Flag", color=colors[2], size=13, symbol="diamond",
                  stroke_color=colors[2], stroke_width=0, opacity=1,
                  dx=14, dy=0, anchor="start"),
        title=title,
    )
    output.append(_record(
        "annotation-notes", title, "Annotations",
        "Text, labels, arrows, callouts, and a semantic marker stay anchored to data.",
        "Text and label are equivalent authoring entry points. Callout offsets "
        "are pixels while their anchor remains a data coordinate. The annotation "
        "marker has an explicit symbol, fill, and zero decorative outline.",
        chart, {"chart": ["title", "width", "height", "padding"],
                "scatter": ["x", "y", "color", "size", "opacity", "stroke_width"],
                "text": ["x", "y", "value", "dx", "dy", "color", "anchor"],
                "label": ["x", "y", "value", "dx", "dy", "color", "anchor"],
                "arrow": ["x0", "y0", "x1", "y1", "text", "color", "width", "opacity"],
                "callout": ["x", "y", "value", "dx", "dy", "color", "width", "opacity", "anchor"],
                "marker": ["x", "y", "text", "color", "size", "symbol", "stroke_color", "stroke_width", "opacity", "dx", "dy", "anchor"],
                "x_axis": ["label", "domain", "tick_count"],
                "y_axis": ["label", "domain", "tick_count"], "legend": ["show"], "theme": ["palette"]},
        ["Annotation notes", "Text anchor", "Label alias", "Callout detail", "Flag"],
        interaction="cartesian",
    ))

    title = "Thresholds: targets and acceptable regions"
    chart = cartesian(
        xy.threshold_zone(2, 4, axis="y", text="Preferred range",
                          color=roles["muted"], opacity=0.18,
                          style={"label_color": "#000000", "label_opacity": 1}),
        xy.line(x, y - 1.5, color=colors[0], width=2.5),
        xy.threshold(6, axis="y", text="Target", color=colors[1], width=1.5, opacity=1),
        xy.threshold(8, axis="x", text="Review time", color=colors[1], width=1.5, opacity=1),
        title=title,
    )
    output.append(_record(
        "annotation-thresholds", title, "Annotations",
        "Semantic threshold helpers select an axis without changing source observations.",
        "The preferred response region is 2 to 4, the target is 6, and review "
        "occurs at input 8. The region uses a canonical neutral at 18% alpha "
        "to keep observations visible, producing derived composite pixels. "
        "Threshold helpers compile to ordinary axis rules and bands.",
        chart, {"chart": ["title", "width", "height", "padding"],
                "threshold_zone": ["start", "end", "axis", "text", "color", "opacity", "style"],
                "threshold": ["value", "axis", "text", "color", "width", "opacity"],
                "line": ["x", "y", "color", "width"],
                "x_axis": ["label", "domain", "tick_count"],
                "y_axis": ["label", "domain", "tick_count"], "legend": ["show"], "theme": ["palette"]},
        ["Thresholds", "Target", "Review time", "Preferred range"],
        interaction="cartesian", paint_scope="derived",
    ))
    return output
