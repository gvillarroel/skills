#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Cartesian XY 0.0.8 acceptance cases; imported by the gallery builder."""

import numpy as np
import xy
from xy_colorsets import categorical_colors, legend_style, load_palette, sequential_colors, text_on, theme


def cases(palette: str) -> list[dict]:
    """Return reproducible charts; export artifacts outside this source folder."""
    colors = categorical_colors(palette, 6)
    roles = load_palette(palette)["roles"]
    ramp = sequential_colors(palette)
    ink = colors[0] if palette == "colorset1" else colors[1]
    rng = np.random.default_rng(17)
    x = np.arange(8, dtype=float)
    y = np.array([3, 4, 3, 6, 5, 7, 6, 8], dtype=float)
    groups = ["Lab", "Field", "Remote"]
    samples = np.stack([rng.normal(5 + i, 0.6 + i * 0.2, 80) for i in range(3)], axis=1)
    grid_x, grid_y = np.linspace(-2, 2, 32), np.linspace(-2, 2, 24)
    gx, gy = np.meshgrid(grid_x, grid_y)
    field = np.exp(-(gx**2 + gy**2)) * 8 - np.exp(-((gx - 1)**2 + (gy - 1)**2)) * 4
    dense_x, noise = rng.normal(size=(2, 12_000))
    dense_y = dense_x * 0.65 + noise * 0.55
    result = []

    def add(slug, title, category, summary, detail, chart, apis, parameters,
            paint_scope="exact", interaction="cartesian", expect_labels=None):
        result.append(dict(id=slug, title=title, category=category, summary=summary,
                           detail=detail, chart=chart, apis=apis, parameters=parameters,
                           paint_scope=paint_scope, interaction=interaction,
                           expect_labels=expect_labels or [title]))

    def make(factory, title, *marks, xlabel="Input", ylabel="Response", axes=None,
             legend=True):
        axis_children = axes or [xy.x_axis(label=xlabel), xy.y_axis(label=ylabel)]
        return factory(*marks, *axis_children,
                       xy.legend(loc="upper left", anchor=(0, -.18), ncols=3,
                                 style=legend_style(palette)) if legend else xy.legend(show=False),
                       theme(palette), title=title, width="100%", height=480,
                       padding=(44, 28, 112 if legend else 56, 64))

    # Data channels and large-data representations.
    cohort = np.repeat(groups, 40)
    channel_x = np.concatenate([rng.normal(3 + i * 2, .7, 40) for i in range(3)])
    channel_y = channel_x * 1.3 + rng.normal(0, .8, 120)
    sizes = np.linspace(1, 10, 120)
    columns = {"input": channel_x, "response": channel_y, "cohort": cohort, "weight": sizes}
    add("scatter-encoding", "Categorical scatter channels", "Core marks",
        "Named columns bind category color and a numeric size channel.",
        "The theme cycle colors sorted cohort labels. Symbols repeat the same distinction; opaque fills retain exact palette paints.",
        make(xy.scatter_chart, "Categorical scatter channels",
             xy.scatter("input", "response", data=columns, color="cohort", size="weight",
                        size_range=(5, 13), symbol=np.repeat(["circle", "square", "triangle"], 40),
                        opacity=1, density=False), xlabel="Input (units)", ylabel="Response (units)"),
        ["scatter", "scatter_chart"], {"scatter": ["data", "color", "size", "size_range", "symbol", "opacity", "density"]})
    add("scatter-continuous", "Continuous scatter color", "Core marks",
        "A numeric color channel uses an explicit palette-derived scale.",
        "Magnitude maps through canonical ramp stops. XY interpolates intermediate quantitative shades; these derived paints are intentional.",
        make(xy.scatter_chart, "Continuous scatter color",
             xy.scatter(channel_x, channel_y, color=sizes, colormap=ramp, color_domain=(1, 10),
                        size=6, opacity=1, density=False), xy.colorbar(title="Weight"), legend=False),
        ["scatter", "scatter_chart", "colorbar"], {"scatter": ["color", "colormap", "color_domain", "size", "opacity", "density"], "colorbar": ["title"]}, "derived")
    add("scatter-density", "Aggregated scatter density", "Core marks",
        "12,000 observations use XY's native density representation.",
        "density=True aggregates observations. Concentration derives tones from one canonical tint; each density pixel summarizes a bin.",
        make(xy.scatter_chart, "Aggregated scatter density",
             xy.scatter(dense_x, dense_y, color=ink, density=True, opacity=1), legend=False),
        ["scatter", "scatter_chart"], {"scatter": ["color", "density", "opacity"]}, "derived")
    missing = y.copy(); missing[3] = np.nan
    add("line-gaps", "Lines with a missing value", "Core marks",
        "Smooth and dashed series retain an explicit missing observation.",
        "NaN breaks a run. Each line owns a constant color, width, and interpolation rule.",
        make(xy.line_chart, "Lines with a missing value",
             xy.line(x, missing, color=colors[0], curve="smooth", width=2.5, name="Measured"),
             xy.line(x, y + 1, color=colors[1], dash="dashed", width=2, name="Reference")),
        ["line", "line_chart"], {"line": ["color", "curve", "width", "name", "dash"]})
    add("area-baseline", "Area above a baseline", "Core marks",
        "An opaque area fills the interval between a series and its baseline.",
        "base is a data value, not an opacity setting. The outline is disabled explicitly so the solid fill carries the region.",
        make(xy.area_chart, "Area above a baseline", xy.area(x, y, base=1, color=ink, opacity=1, line_width=0), legend=False),
        ["area", "area_chart"], {"area": ["base", "color", "opacity", "line_width"]})
    lower = np.array([2, 3, 2, 4, 3, 4, 4, 5], dtype=float)
    upper = np.array([2, 1, 3, 2, 3, 2, 3, 2], dtype=float)
    add("stacked-area", "Explicit stacked areas", "Core marks",
        "Two areas share a cumulative boundary computed from aligned arrays.",
        "The upper layer uses base=lower and y=lower+upper. Area y is an endpoint; bar y uses a height. These contracts differ.",
        make(xy.area_chart, "Explicit stacked areas",
             xy.area(x, lower, base=0, color=colors[0], opacity=1, line_width=0, name="Lab"),
             xy.area(x, lower + upper, base=lower, color=colors[1], opacity=1, line_width=0, name="Field"),
             axes=[xy.x_axis(label="Input"), xy.y_axis(label="Response", domain=(0, 10))]),
        ["area", "area_chart"], {"area": ["base", "color", "opacity", "line_width", "name"]})
    regions = ["North", "South", "West"]
    values = [[4, 5, 6], [2, 3, 2], [3, 2, 4]]
    for slug, title, mode, summary in (
        ("grouped-bars", "Grouped bar series", "grouped", "Series sit beside one another within each category."),
        ("stacked-bars", "Stacked bar series", "stacked", "Series stack their heights from a shared zero baseline."),
        ("normalized-bars", "Normalized bar shares", "normalized", "Each category's total becomes one whole for share comparisons."),
    ):
        add(slug, title, "Core marks", summary,
            "A series-by-category matrix and explicit names keep color alignment stable. mode controls the layout.",
            make(xy.bar_chart, title, xy.bar(regions, values, series=groups, colors=colors[:3], mode=mode, opacity=1)),
            ["bar", "bar_chart"], {"bar": ["series", "colors", "mode", "opacity"]})
    add("horizontal-bars", "Horizontal bar categories", "Core marks",
        "The same bar API places categories on the vertical axis.",
        "orientation='horizontal' changes the geometry without exchanging source arrays. A named category remains paired with its own value.",
        make(xy.bar_chart, "Horizontal bar categories", xy.bar(regions, [4, 7, 6], orientation="horizontal", color=ink, opacity=1, corner_radius=3), xlabel="Value", ylabel="Region", legend=False),
        ["bar", "bar_chart"], {"bar": ["orientation", "color", "opacity", "corner_radius"]})
    add("columns", "Columns with explicit bases", "Core marks",
        "The column alias uses the shared bar renderer and varying baselines.",
        "y is a height above its matching base; width is in category units, independent of canvas pixels.",
        make(xy.column_chart, "Columns with explicit bases", xy.column(x[:5], [2, 3, 4, 2, 3], base=[1, 2, 1, 3, 2], width=.65, color=ink, opacity=1), legend=False),
        ["column", "column_chart"], {"column": ["base", "width", "color", "opacity"]})
    # Distribution and uncertainty marks.
    for slug, title, fn, density, cumulative in (
        ("histogram-counts", "Histogram counts", xy.hist, False, False),
        ("histogram-cumulative", "Cumulative histogram", xy.histogram, True, True),
    ):
        add(slug, title, "Distributions", "Fixed bin edges preserve the same input sample across representations.",
            "Count mode shows observations per bin. density=True with cumulative=True shows normalized accumulated mass ending at one when bins cover the sample.",
            make(xy.histogram_chart, title, fn(samples[:, 0], bins=np.linspace(2, 8, 17), density=density, cumulative=cumulative, color=ink, opacity=1), xlabel="Value", ylabel="Cumulative mass" if cumulative else "Count", legend=False),
            ["histogram" if cumulative else "hist", "histogram_chart"], {"histogram" if cumulative else "hist": ["bins", "density", "cumulative", "color", "opacity"]})
    add("step-transitions", "Pre, mid, and post steps", "Core marks",
        "Transition convention controls when a sample takes effect.",
        "pre, mid, and post all use the same ordered samples. Lines are vertically offset only to make the conventions readable in one panel.",
        make(xy.step_chart, "Pre, mid, and post steps", *[
            xy.step(x, y + 5 * i, where=where, color=colors[i], width=2, name=where)
            for i, where in enumerate(("pre", "mid", "post"))]),
        ["step", "step_chart"], {"step": ["where", "color", "width", "name"]})
    add("prebinned-stairs", "Stairs from explicit edges", "Core marks",
        "Four heights describe four unequal-width intervals with five edges.",
        "Stairs accepts N heights and N+1 edges, preserving precomputed bin boundaries.",
        make(xy.stairs_chart, "Stairs from explicit edges", xy.stairs([3, 7, 4, 8], [0, 1, 2, 4, 6], where="post", color=ink, width=2), legend=False),
        ["stairs", "stairs_chart"], {"stairs": ["where", "color", "width"]})
    add("stems", "Discrete stem impulses", "Core marks",
        "Each sample receives a stem from a baseline and an endpoint marker.",
        "Marker shape, size, baseline, and stem width vary independently. Input positions stay discrete.",
        make(xy.stem_chart, "Discrete stem impulses", xy.stem(x, y, base=1, color=ink, width=2, marker=True, marker_size=8, symbol="diamond"), legend=False),
        ["stem", "stem_chart"], {"stem": ["base", "color", "width", "marker", "marker_size", "symbol"]})
    add("empirical-cdf", "Empirical distributions", "Distributions",
        "Two sample distributions become monotone empirical cumulative curves.",
        "ECDF sorts sample values internally. bins bounds the evaluation resolution.",
        make(xy.ecdf_chart, "Empirical distributions", xy.ecdf(samples[:, 0], color=colors[0], width=2, name="Lab"), xy.ecdf(samples[:, 1], bins=32, color=colors[1], width=2, dash="dashed", name="Field"), xlabel="Value", ylabel="Cumulative fraction"),
        ["ecdf", "ecdf_chart"], {"ecdf": ["bins", "color", "width", "name", "dash"]})
    add("box-distributions", "Tukey box distributions", "Distributions",
        "Three samples expose quartiles, medians, whiskers, and outliers.",
        "x aligns with sample rows. Whiskers and medians use separate styles; a contrasting median remains visible over an opaque body.",
        make(xy.box_chart, "Tukey box distributions", *[
            xy.box(samples[:, i], x=np.full(80, i), color=colors[i], opacity=1, name=groups[i], show_outliers=True, outlier_size=5, style={"stroke-width": 0}, median_style={"stroke": text_on(colors[i]), "stroke-width": 2}, whisker_style={"stroke": colors[i], "stroke-width": 1.5})
            for i in range(3)], xlabel="Group", ylabel="Value"),
        ["box", "box_chart"], {"box": ["x", "color", "opacity", "name", "show_outliers", "outlier_size", "style", "median_style", "whisker_style"]})
    add("violin-distributions", "Horizontal violin shapes", "Distributions",
        "Bounded-resolution density estimates expose sample distribution shapes.",
        "bins sets density resolution. In horizontal orientation, x still holds group positions aligned with sample rows.",
        make(xy.violin_chart, "Horizontal violin shapes", *[
            xy.violin(samples[:, i], x=np.full(80, i), color=colors[i], opacity=1, name=groups[i], bins=48, orientation="horizontal")
            for i in range(3)], xlabel="Value", ylabel="Group"),
        ["violin", "violin_chart"], {"violin": ["x", "color", "opacity", "name", "bins", "orientation"]})
    add("error-bars", "Asymmetric error bars", "Distributions",
        "Horizontal and asymmetric vertical uncertainties share the same observations.",
        "yerr is a lower/upper pair of nonnegative magnitudes. xerr is symmetric. cap_size=.18 uses perpendicular data-axis units, while width is a pixel stroke.",
        make(xy.errorbar_chart, "Asymmetric error bars", xy.errorbar(x, y, yerr=[np.full(8, .6), np.full(8, 1.1)], xerr=.15, color=ink, width=2, cap_size=.18), xy.scatter(x, y, color=roles["inkDark"], size=6, opacity=1, density=False), legend=False),
        ["errorbar", "errorbar_chart", "scatter"], {"errorbar": ["yerr", "xerr", "color", "width", "cap_size"], "scatter": ["color", "size", "opacity", "density"]})
    add("error-band", "Uncertainty range band", "Distributions",
        "Lower and upper arrays bound a central estimate without altering it.",
        "A pale canonical fill distinguishes the interval from its central line. The band does not calculate confidence.",
        make(xy.error_band_chart, "Uncertainty range band", xy.error_band(x, y - .8, y + 1.2, color=ramp[0], opacity=1, line_width=0), xy.line(x, y, color=ink, width=2), legend=False),
        ["error_band", "error_band_chart", "line"], {"error_band": ["color", "opacity", "line_width"], "line": ["color", "width"]})
    # Numeric fields and flow primitives.
    add("native-heatmap", "Native continuous heatmap", "Fields and flows",
        "A rectangular numeric grid uses the actual native heatmap mark.",
        "x/y centers align with the matrix dimensions. The native ramp interpolates canonical stops into derived shades; the original gallery separately demonstrates exact bins.",
        make(xy.heatmap_chart, "Native continuous heatmap", xy.heatmap(field, x=grid_x, y=grid_y, colormap=ramp, domain=(-2, 8), opacity=1), xy.colorbar(title="Magnitude"), legend=False),
        ["heatmap", "heatmap_chart", "colorbar"], {"heatmap": ["x", "y", "colormap", "domain", "opacity"], "colorbar": ["title"]}, "derived")
    add("hexbin-density", "Hexagonal density bins", "Fields and flows",
        "Native hexagonal bins summarize 12,000 points by count.",
        "gridsize controls resolution; mincnt omits empty bins. The count ramp interpolates canonical stops. Each hexagon represents an aggregate.",
        make(xy.hexbin_chart, "Hexagonal density bins", xy.hexbin(dense_x, dense_y, gridsize=22, bins="count", mincnt=1, colormap=ramp, opacity=1), xy.colorbar(title="Count"), legend=False),
        ["hexbin", "hexbin_chart", "colorbar"], {"hexbin": ["gridsize", "bins", "mincnt", "colormap", "opacity"], "colorbar": ["title"]}, "derived")
    add("contour-lines", "Exact-color contour lines", "Fields and flows",
        "Six isolines trace explicit values of the same regular numeric grid.",
        "An explicit color list cycles across levels. Negative isolines are dashed for monochrome readability.",
        make(xy.contour_chart, "Exact-color contour lines", xy.contour(field, x=grid_x, y=grid_y, levels=[-1, 0, 1, 2, 4, 6], color=colors, width=2, opacity=1, dash_negative=True), legend=False),
        ["contour", "contour_chart"], {"contour": ["x", "y", "levels", "color", "width", "opacity", "dash_negative"]})
    add("filled-contours", "Filled contour intervals", "Fields and flows",
        "Filled intervals reveal the same scalar field between chosen thresholds.",
        "filled=True adds interval surfaces with derived ramp shades. corner_mask preserves valid triangles near missing grid corners when a mask is present.",
        make(xy.contour_chart, "Filled contour intervals", xy.contour(field, x=grid_x, y=grid_y, levels=[-2, 0, 1, 2, 4, 6, 8], filled=True, colormap=ramp, opacity=1, extend="neither", corner_mask=True), legend=False),
        ["contour", "contour_chart"], {"contour": ["x", "y", "levels", "filled", "colormap", "opacity", "extend", "corner_mask"]}, "derived")
    add("independent-segments", "Independent line segments", "Fields and flows",
        "Each row supplies two endpoints and an independent stroke width.",
        "Segments keep rows independent, useful for intervals, vector fields, whiskers, and structural overlays.",
        make(xy.segments_chart, "Independent line segments", xy.segments(x, np.zeros(8), x + .6, y, color=ink, width=np.linspace(1, 4, 8), opacity=1), legend=False),
        ["segments", "segments_chart"], {"segments": ["color", "width", "opacity"]})
    add("triangle-mesh", "Explicit triangle mesh", "Fields and flows",
        "Three independent triangles carry direct per-triangle palette colors.",
        "Each row specifies three vertices. CSS color arrays retain exact paints; numeric colors require a colormap.",
        make(xy.triangle_mesh_chart, "Explicit triangle mesh", xy.triangle_mesh([0, 1, 1], [0, 0, 1], [1, 2, 2], [0, 0, 1], [1, 2, 1], [1, 1, 2], color=colors[:3], opacity=1), legend=False),
        ["triangle_mesh", "triangle_mesh_chart"], {"triangle_mesh": ["color", "opacity"]})
    add("flat-ribbons", "Flat flow ribbon spans", "Fields and flows",
        "Two spans at a source face connect smoothly to two target spans.",
        "Omitting color_target keeps exact flat fills. A different target color produces a gradient along the flow.",
        make(xy.chart, "Flat flow ribbon spans", xy.ribbon([0, 0], [2, 2], [0, 2], [1, 3], [1, 0], [2, 1], color=colors[:2], opacity=1), legend=False),
        ["ribbon", "chart"], {"ribbon": ["color", "opacity"]})
    links = [("Input", "Lab", 12), ("Input", "Field", 8), ("Lab", "Output", 10), ("Field", "Output", 8), ("Lab", "Loss", 2)]
    add("sankey-flow", "Sankey flow conservation", "Fields and flows",
        "Five weighted links become aligned nodes and proportionate ribbons.",
        "Sankey lays out links in Python. Its ribbons interpolate canonical dark node colors into derived gradients. White annotation_text keeps the native labels readable over those dark fills.",
        xy.sankey_chart(links, theme(palette, annotation_text="#ffffff"), xy.legend(show=False), colors=[colors[i % 2] for i in range(5)], nodes=["Input", "Lab", "Field", "Output", "Loss"], align="justify", iterations=6, node_width=.025, node_padding=.06, link_opacity=1, labels=True, navigation=False, title="Sankey flow conservation", width="100%", height=480),
        ["sankey", "sankey_chart", "theme"], {"sankey_chart": ["colors", "nodes", "align", "iterations", "node_width", "node_padding", "link_opacity", "labels", "navigation"], "theme": ["annotation_text"]}, "derived", "none")
    for slug, title, geometry, orientation in (
        ("funnel-area", "Tapered conversion funnel", "area", "vertical"),
        ("funnel-bars", "Horizontal funnel bars", "bar", "horizontal"),
    ):
        add(slug, title, "Fields and flows", "Four ordered stages retain their original counts and conversion labels.",
            "Area geometry makes a taper whose painted area is not proportional to value; bar geometry uses proportional centered widths. XY 0.0.8 generates native contrast-label paints #f7f8fa/#1f2430 outside the theme; stage fills remain canonical.",
            xy.funnel_chart(xy.funnel(["Visits", "Leads", "Trials", "Paid"], [1200, 780, 420, 210], colors=colors[:4], geometry=geometry, orientation=orientation, opacity=1, show_values=True, show_conversion=True, show_dropoff=True), theme(palette), xy.legend(show=False), navigation=False, title=title, width="100%", height=480),
            ["funnel", "funnel_chart"], {"funnel": ["colors", "geometry", "orientation", "opacity", "show_values", "show_conversion", "show_dropoff"], "funnel_chart": ["navigation"]}, paint_scope="derived", interaction="none")
        result[-1]["native_paint_exceptions"] = ["#f7f8fa", "#1f2430"]
    return result
