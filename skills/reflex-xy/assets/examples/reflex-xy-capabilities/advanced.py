"""Runnable XY 0.0.8 axes, layout, navigation, and data capability cases.

The gallery builder imports cases(); keep xy_colorsets.py and colorsets.json
beside this module in a portable source download. No live Python backend is
required for these chart snapshots. Kernel-backed APIs have a separate demo.
"""
from __future__ import annotations

import numpy as np
import xy

from xy_colorsets import categorical_colors, legend_style, theme


def cases(palette: str) -> list[dict]:
    """Return twelve independent chart compositions and exercised API metadata."""
    colors = categorical_colors(palette, 3)
    common = {"width": "100%", "height": 460, "padding": (70, 38, 74, 68)}
    output: list[dict] = []

    def add(identifier, title, category, summary, detail, chart, parameters,
            *, interaction="cartesian", paint_scope="exact", labels=()):
        parameters = {name.removeprefix("xy."): values for name, values in parameters.items()}
        output.append({
            "id": identifier, "title": title, "category": category,
            "summary": summary, "detail": detail, "chart": chart,
            "apis": list(parameters), "parameters": parameters,
            "paint_scope": paint_scope, "interaction": interaction,
            "expect_labels": [title, *labels],
        })

    x = np.arange(12.0)
    chart = xy.chart(
        xy.line(x, 18 + 5 * np.sin(x / 3), color=colors[0], width=3,
                name="Temperature", x_axis="x", y_axis="y"),
        xy.line(x * 60, 150 + 45 * np.cos(x / 3), color=colors[1], width=3,
                dash="dashed", name="Power", x_axis="x2", y_axis="y2"),
        xy.x_axis(id="x", label="Hours", domain=(-0.5, 11.5)),
        xy.x_axis(id="x2", label="Minutes", side="top", domain=(-30, 690)),
        xy.y_axis(id="y", label="Temperature (C)", domain=(10, 30)),
        xy.y_axis(id="y2", label="Power (kW)", side="right", domain=(80, 220)),
        xy.legend(loc="lower left", ncols=2, style=legend_style(palette)),
        theme(palette), title="Independent secondary axes", **common,
    )
    add("axes-secondary", "Independent secondary axes", "Axes and layout",
        "Two signals bind to independent x/x2 and y/y2 axes.",
        "The upper axis uses minutes and the right axis uses kilowatts. The same screen position can have different coordinates on each named axis; zoom policies can address each ID independently.",
        chart, {"xy.chart": ["width", "height", "padding", "title"],
                "xy.line": ["x_axis", "y_axis", "dash"],
                "xy.x_axis": ["id", "label", "side", "domain"],
                "xy.y_axis": ["id", "label", "side", "domain"]},
        labels=("Hours", "Minutes", "Temperature (C)", "Power (kW)"))

    positive = np.geomspace(0.1, 1000, 25)
    chart = xy.chart(
        xy.scatter(np.r_[-1.0, 0.0, positive], np.r_[1.0, 2.0, np.log10(positive) + 2],
                   color=colors[0], size=8, opacity=1, density=False),
        xy.x_axis(type_="log", nonpositive="mask", domain=(0.08, 1500),
                  label="Logarithmic input"),
        xy.y_axis(label="Response", domain=(0, 5.5)), xy.legend(show=False),
        theme(palette), title="Log scale and non-positive masking", **common,
    )
    add("scales-log", "Log scale and non-positive masking", "Axes and layout",
        "Equal ratios occupy equal horizontal distances; zero and negative inputs are masked.",
        "The source retains two non-positive inputs. The explicit log-axis policy masks them rather than pretending they have valid logarithmic positions.",
        chart, {"xy.x_axis": ["type_", "nonpositive", "domain", "label"]},
        labels=("Logarithmic input", "Response"))

    signed = np.linspace(-8, 8, 81)
    chart = xy.chart(
        xy.line(signed, signed ** 3 / 5, color=colors[0], width=3),
        xy.hline(0, color=colors[1]),
        xy.x_axis(label="Signed input", domain=(-9, 9)),
        xy.y_axis(type_="symlog", constant=5, domain=(-120, 120), label="Symmetric log response"),
        xy.legend(show=False), theme(palette), title="Symlog across negative and positive values", **common,
    )
    add("scales-symlog", "Symlog across negative and positive values", "Axes and layout",
        "A linear neighborhood around zero connects logarithmic positive and negative tails.",
        "The constant of 5 defines the linear central region. Signed observations remain on their original side of zero.",
        chart, {"xy.y_axis": ["type_", "constant", "domain", "label"],
                "xy.hline": ["color"]}, labels=("Signed input", "Symmetric log response"))

    dates = np.datetime64("2026-10-01", "D") + np.arange(10).astype("timedelta64[D]")
    readings = np.array([14, 17, 16, 20, 22, 19, 25, 23, 27, 29], dtype=float)
    chart = xy.chart(
        xy.line(dates, readings, color=colors[0], width=3),
        xy.scatter(dates, readings, color=colors[1], size=7, opacity=1, density=False),
        xy.x_axis(type_="time", format="%b %d", tick_count=4, label="Observation date"),
        xy.y_axis(label="Reading", domain=(10, 32)), xy.legend(show=False),
        theme(palette), title="Datetime axis and formatted ticks", **common,
    )
    add("axes-time", "Datetime axis and formatted ticks", "Axes and layout",
        "Real datetime64 observations use a time axis rather than a categorical string axis.",
        "XY canonical time is milliseconds. This daily example does not claim preservation of sub-millisecond distinctions or a live calendar connection.",
        chart, {"xy.x_axis": ["type_", "format", "tick_count", "label"]},
        labels=("Observation date", "Reading"))

    labels = ["Control", "Treatment A", "Treatment B", "Follow-up"]
    chart = xy.chart(
        xy.bar(labels, [27, 44, 38, 51], color=colors[0], opacity=1),
        xy.x_axis(label="Study group", label_offset=28, reverse=True, tick_label_angle=-24,
                  tick_label_anchor="end", tick_label_strategy="preserve"),
        xy.y_axis(label="Completed cases", domain=(0, 60)), xy.legend(show=False),
        theme(palette), title="Categorical order and rotated labels", **common,
    )
    add("axes-category-labels", "Categorical order and rotated labels", "Axes and layout",
        "String categories retain identity while the explicit axis reverses display order.",
        "Rotation and end anchoring help long labels fit. Reversal changes the axis orientation rather than sorting or modifying the underlying categories.",
        chart, {"xy.x_axis": ["label", "label_offset", "reverse", "tick_label_angle", "tick_label_anchor", "tick_label_strategy"]},
        labels=("Study group", "Completed cases"))

    ticks = np.arange(7.0)
    chart = xy.chart(
        xy.line(ticks, [3, 6, 4, 9, 7, 10, 8], color=colors[0], width=3),
        xy.x_axis(label="Measurement stage", domain=(-0.3, 6.3),
                  tick_values=[0, 2, 4, 6], minor_tick_values=[1, 3, 5],
                  tick_labels=["Start", "Stage 2", "Stage 4", "Finish"],
                  tick_sides=["bottom", "top"], tick_label_sides=["bottom"],
                  show=True, line=True, ticks=True, grid=True, text=True),
        xy.y_axis(label="Value", domain=(0, 12), tick_count=4, format=".0f"),
        xy.legend(show=False), theme(palette), title="Major and minor tick controls", **common,
    )
    add("axes-custom-ticks", "Major and minor tick controls", "Axes and layout",
        "Named major ticks coexist with unlabeled minor ticks and mirrored tick marks.",
        "The top edge repeats tick marks without repeating labels. Axis visibility switches independently control baselines, ticks, grids, and text.",
        chart, {"xy.x_axis": ["tick_values", "minor_tick_values", "tick_labels", "tick_sides", "tick_label_sides", "show", "line", "ticks", "grid", "text"],
                "xy.y_axis": ["tick_count", "format"]}, labels=("Measurement stage", "Value"))

    facet_data = {"x": np.tile(np.arange(10.0), 3),
                  "y": np.concatenate([10 + np.arange(10.0) * slope for slope in (0.8, 1.3, 1.8)]),
                  "cohort": np.repeat(["Lab", "Field", "Remote"], 10)}
    chart = xy.facet_chart(
        xy.scatter("x", "y", color="cohort", size=7, opacity=1, density=False),
        xy.x_axis(label="Stage", domain=(-0.5, 9.5)),
        xy.y_axis(label="Reading", domain=(5, 30)), xy.legend(show=False),
        xy.interaction_config(select=True, brush=True, crosshair=True), theme(palette),
        data=facet_data, by="cohort", cols=2, share_x=True, share_y=True,
        link="x", link_select=True, gap=18, width=820, height=300,
        title="Linked facet panels",
    )
    add("layout-facets-linked", "Linked facet panels", "Axes and layout",
        "Three group panels share domains and synchronize their x views within one document.",
        "Zoom a panel to verify linked x ranges. Linked selections echo data-space geometry rather than cross-filtering source rows. XY 0.0.8 facets require integer dimensions and fixed panel widths; narrow screens can scroll within the fixed grid. Separate HTML documents do not share the link.",
        chart, {"xy.facet_chart": ["data", "by", "cols", "share_x", "share_y", "link", "link_select", "gap", "width", "height"],
                "xy.interaction_config": ["select", "brush", "crosshair"]},
        interaction="facet", labels=("Stage", "Reading"))

    wave_x = np.linspace(0, 12, 121)
    wave_y = 10 + 3 * np.sin(wave_x)
    chart = xy.chart(
        xy.line(wave_x, wave_y, color=colors[0], width=3),
        xy.x_axis(label="Bounded x window", bounds="data"),
        xy.y_axis(label="Fixed y window", domain=(5, 15)), xy.legend(show=False),
        xy.interaction_config(pan=True, pan_axes=("x",), zoom=True, zoom_axes=("x",),
                              zoom_limits={"x": (1, 8)}, wheel_zoom=True, box_zoom=True,
                              zoom_buttons=True, double_click_reset=True, reset_axes=("x",),
                              default_drag_action="pan", history=True),
        theme(palette), title="X-only navigation with view history", **common,
    )
    add("navigation-x-only", "X-only navigation with view history", "Interaction and data",
        "Pan and zoom x while y remains fixed; use history and reset controls.",
        "The data bounds clamp x navigation and the magnification is limited to 1–8 times the home range. Back/forward and reset are browser-local view actions.",
        chart, {"xy.interaction_config": ["pan", "pan_axes", "zoom", "zoom_axes", "zoom_limits", "wheel_zoom", "box_zoom", "zoom_buttons", "double_click_reset", "reset_axes", "default_drag_action", "history"],
                "xy.x_axis": ["bounds"]}, labels=("Bounded x window", "Fixed y window"))

    grid_x, grid_y = np.meshgrid(np.arange(7.0), np.arange(5.0))
    chart = xy.chart(
        xy.scatter(grid_x.ravel(), grid_y.ravel(), color=colors[0], size=10, opacity=1, density=False),
        xy.x_axis(label="Selectable x", domain=(-0.5, 6.5)),
        xy.y_axis(label="Selectable y", domain=(-0.5, 4.5)), xy.legend(show=False),
        xy.interaction_config(hover=True, click=True, select=True, brush=True,
                              crosshair=True, default_drag_action="select-lasso"),
        xy.tooltip(fields=["x", "y"], labels={"x": "Column", "y": "Row"},
                   format={"x": ".0f", "y": ".0f"}, title="Grid observation"),
        theme(palette), title="Box and lasso selection controls", **common,
    )
    add("selection-box-lasso", "Box and lasso selection controls", "Interaction and data",
        "Start with lasso selection; switch drag mode to box, x range, or y range.",
        "Selection and hover are client-local in this HTML snapshot. Python callbacks and complete canonical row resolution require the notebook or Reflex host source.",
        chart, {"xy.interaction_config": ["hover", "click", "select", "brush", "crosshair", "default_drag_action"],
                "xy.tooltip": ["fields", "labels", "format", "title"]},
        labels=("Selectable x", "Selectable y"))

    chart = xy.chart(
        xy.line(wave_x, wave_y, color=colors[0], width=3),
        xy.x_axis(label="Input"), xy.y_axis(label="Reading"), xy.legend(show=False),
        xy.modebar(show=False), xy.tooltip(show=False),
        xy.interaction_config(hover=False, click=False, select=False, brush=False,
                              crosshair=False, navigation=False, history=False),
        theme(palette), title="Minimal chart without navigation chrome", **common,
    )
    add("controls-minimal", "Minimal chart without navigation chrome", "Interaction and data",
        "A compact reporting view deliberately disables toolbar, hover, selection, and navigation.",
        "The export remains a browser-rendered XY chart, with all interaction switches explicitly disabled. The absence of controls is the feature being demonstrated.",
        chart, {"xy.modebar": ["show"], "xy.tooltip": ["show"],
                "xy.interaction_config": ["hover", "click", "select", "brush", "crosshair", "navigation", "history"]},
        interaction="none", labels=("Input", "Reading"))

    anim_x = np.arange(9.0)
    chart = xy.chart(
        xy.scatter(anim_x, 2 + anim_x ** 1.4, key=np.arange(9), color=colors[0],
                   size=10, opacity=1, density=False),
        xy.line(anim_x, 2 + anim_x ** 1.4, key=np.arange(9), color=colors[1], width=3,
                animation=xy.animation(duration=700, enter="reveal")),
        xy.animation(enabled=True, duration=1000,
                     easing=xy.spring(stiffness=130, damping=18, mass=0.8),
                     match="key", enter="scale", update="interpolate",
                     interpolate=("position", "size", "color", "domain")),
        xy.x_axis(label="Stable row identity"), xy.y_axis(label="Animated reading"),
        xy.legend(show=False), theme(palette), title="Entrance animation and stable keys", **common,
    )
    add("animation-reveal", "Entrance animation and stable keys", "Interaction and data",
        "A spring-based point entrance and a mark-level line reveal share stable row identities.",
        "Reload the interactive export to replay entrance motion. Native images show the deterministic final scene. Subsequent data-update animation needs a live host; intermediate pixels can be renderer-derived blends.",
        chart, {"xy.animation": ["enabled", "duration", "easing", "match", "enter", "update", "interpolate"],
                "xy.spring": ["stiffness", "damping", "mass"], "xy.scatter": ["key"],
                "xy.line": ["key", "animation"]}, paint_scope="derived",
        labels=("Stable row identity", "Animated reading"))

    primary = {"x": np.arange(6.0), "y": np.array([3, 5, 4, 8, 7, 10], dtype=float)}
    override = {"x": np.arange(6.0) + 0.15, "y": np.array([6, 7, 6, 11, 10, 13], dtype=float)}
    chart = xy.chart(
        xy.scatter("x", "y", name="Chart table", color=colors[0], size=10, opacity=1, density=False),
        xy.scatter("x", "y", data=override, name="Mark override", color=colors[1],
                   size=10, symbol="diamond", opacity=1, density=False),
        xy.x_axis(label="Named x column", domain=(-0.5, 5.8)),
        xy.y_axis(label="Named y column", domain=(0, 16)),
        xy.legend(loc="upper left", ncols=2, style=legend_style(palette)),
        xy.tooltip(fields=["x", "y"], labels={"x": "Index", "y": "Reading"}),
        theme(palette), data=primary, title="Chart data and per-mark override", **common,
    )
    add("data-column-override", "Chart data and per-mark override", "Interaction and data",
        "One mark resolves named columns from chart data; a second explicitly overrides its table.",
        "Both marks use the same column names but preserve different arrays. The override applies to that mark only; it does not mutate the chart-level table.",
        chart, {"xy.chart": ["data"], "xy.scatter": ["x", "y", "data", "symbol"],
                "xy.tooltip": ["fields", "labels"]}, labels=("Named x column", "Named y column"))
    return output
