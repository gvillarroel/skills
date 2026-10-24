#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Build paired Color Set 1 / Color Set 2 XY charts and a portable gallery.

Run: uv run --script build.py --output-dir <gallery-directory>
The downloadable source directory includes this file, gallery.html,
xy_colorsets.py, colorsets.json, and patterns.json; keep them together to rebuild.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.metadata
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import xy

HERE = Path(__file__).resolve().parent
HELPER_DIR = HERE if (HERE / "xy_colorsets.py").is_file() else HERE.parents[2] / "scripts"
sys.path.insert(0, str(HELPER_DIR))
from xy_colorsets import binned_colors, categorical_colors, css, legend_style, load_palette, sequential_colors, text_on, theme

SET_ID = "reflex-xy-colorsets"
SEED = 20261024
WIDTH, HEIGHT = 820, 480
PALETTES = ("colorset1", "colorset2")
MECHANISMS = (
    ("category-scatter", "Category scatter", "Compare three cohorts", "195 observations; shape and color identify the same three cohorts.", "Each cohort keeps a separate mark, a direct color, and a matching legend entry. Circle, square, and triangle symbols provide a second cue."),
    ("trend-lines", "Trend lines", "Follow a change over time", "Three weekly series; one missing observation stays visibly missing.", "Line dashes repeat the series distinction. A missing week in the Field series remains a gap in both palette variants."),
    ("grouped-bars", "Grouped bars", "Compare within each category", "Three delivery channels across four regions, with a shared zero baseline.", "The same series matrix produces each group. Colors follow the channel order, so comparisons stay consistent across regions."),
    ("histogram", "Histogram", "Reveal the shape of a distribution", "900 synthetic service times; the dashed line marks the sample median.", "One solid palette color carries the distribution. The reference line adds a summary without replacing the individual bin counts."),
    ("heatmap", "Binned heatmap", "Find patterns across two dimensions", "A 7-by-12 synthetic workload matrix, divided into four fixed numeric bins.", "Data-unit rectangles use exact sequential colors with no gradient and resize with the canvas. Each cell displays its original workload; bin thresholds stay fixed at 0, 20, 40, 60, and 80."),
    ("dense-scatter", "Dense scatter", "Reveal structure in a dense sample", "8,000 synthetic observations drawn as opaque point marks.", "Small opaque markers retain exact palette fills. The footprint reveals concentration while every mark remains an individual point; automatic density aggregation is disabled."),
)


def synthetic_data() -> dict:
    """Generate once, then reuse byte-identical arrays for both palettes."""
    rng = np.random.default_rng(SEED)
    cohorts = []
    for i, name in enumerate(("Lab", "Field", "Remote")):
        x = rng.normal(3.2 + i * 2.0, 1.0, 65)
        y = 6.0 + x * 2.2 + i * 1.8 + rng.normal(0, 2.3, len(x))
        cohorts.append((name, x, y))
    weeks = np.arange(1.0, 13.0)
    trends = [
        ("Lab", 57 + weeks * 2.5 + np.sin(weeks / 1.3) * 4.0),
        ("Field", 48 + weeks * 2.9 + np.cos(weeks / 1.8) * 4.5),
        ("Remote", 40 + weeks * 2.4 + np.sin(weeks / 1.8) * 3.0),
    ]
    trends[1][1][6] = np.nan
    latencies = rng.lognormal(mean=np.log(145.0), sigma=0.42, size=900)
    hour = np.arange(12.0)
    day = np.arange(7.0)[:, None]
    workload = 18 + 45 * np.exp(-((hour[None, :] - 6.0) / 2.3) ** 2)
    workload = np.rint(np.clip(workload * (0.65 + (6 - day) * 0.06) + rng.normal(0, 3.2, (7, 12)), 0, 80))
    dense_x = rng.normal(0, 1, 8_000)
    dense_y = 0.65 * dense_x + rng.normal(0, 0.55, dense_x.size)
    return {"cohorts": cohorts, "weeks": weeks, "trends": trends, "latencies": latencies, "workload": workload, "dense_x": dense_x, "dense_y": dense_y}


def fingerprint(data: dict) -> str:
    """Hash labelled arrays at XY's float32 wire precision, independent of libm.

    Windows and Linux can differ in float64 transcendental last bits even when
    XY exports identical transport buffers and SVGs. Record shape and names,
    use explicit little endian bytes, and normalize NaNs before hashing.
    """
    digest = hashlib.sha256(b"labelled-float32-le-v1\0")

    def add_array(label: str, values) -> None:
        array = np.array(values, dtype="<f4", order="C", copy=True)
        array[np.isnan(array)] = np.float32("nan")
        digest.update(json.dumps([label, list(array.shape), "<f4"], separators=(",", ":")).encode())
        digest.update(b"\0")
        digest.update(array.tobytes(order="C"))

    for label, x, y in data["cohorts"]:
        add_array(f"cohorts/{label}/x", x)
        add_array(f"cohorts/{label}/y", y)
    add_array("weeks", data["weeks"])
    for key in ("latencies", "workload", "dense_x", "dense_y"):
        add_array(key, data[key])
    for label, values in data["trends"]:
        add_array(f"trends/{label}", values)
    return digest.hexdigest()


def make_chart(mechanism: str, name: str, data: dict) -> xy.Chart:
    """Use public XY marks, including exact-color rectangles for the matrix."""
    colors = categorical_colors(name, 3)
    shared = dict(width="100%", height=HEIGHT, padding=(44, 26, 56, 64))
    styling = theme(name)
    if mechanism == "category-scatter":
        marks = [xy.scatter(x, y, name=label, color=color, size=7, opacity=1, symbol=symbol, density=False)
                 for (label, x, y), color, symbol in zip(data["cohorts"], colors, ("circle", "square", "triangle"), strict=True)]
        return xy.chart(*marks, xy.x_axis(label="Input (units)", domain=(-0.5, 10.5)), xy.y_axis(label="Response (units)", domain=(0, 35)), xy.legend(loc="lower right", ncols=1, style=legend_style(name)), xy.tooltip(), styling, title="Cohort comparison", **shared)
    if mechanism == "trend-lines":
        marks = [xy.line(data["weeks"], values, name=label, color=color, width=2.8, dash=dash)
                 for (label, values), color, dash in zip(data["trends"], colors, ("solid", "dashed", "dotted"), strict=True)]
        return xy.chart(*marks, xy.x_axis(label="Week", domain=(0.5, 12.5), tick_count=6), xy.y_axis(label="Completion (%)", domain=(30, 95)), xy.legend(ncols=3, style=legend_style(name)), xy.tooltip(), styling, title="Weekly completion", **shared)
    if mechanism == "grouped-bars":
        return xy.chart(xy.bar(["North", "South", "East", "West"], [[44, 61, 53, 70], [35, 49, 59, 57], [28, 40, 37, 48]], series=["Direct", "Partner", "Online"], colors=colors, opacity=1, corner_radius=2), xy.x_axis(label="Region", grid=False), xy.y_axis(label="Deliveries (count)", domain=(0, 80)), xy.legend(ncols=3, style=legend_style(name)), xy.tooltip(), styling, title="Channels by region", **shared)
    if mechanism == "histogram":
        values = data["latencies"]
        bins = np.linspace(0, 600, 25)
        peak = int(np.histogram(values, bins=bins)[0].max())
        median = float(np.median(values))
        return xy.chart(xy.hist(values, bins=bins, color=colors[0], opacity=1, name="Observations"), xy.line([median, median], [0, peak + 8], color=colors[1], width=2.5, dash="dashed", name=f"Median {median:.0f} ms"), xy.x_axis(label="Service time (ms)", domain=(-20, 620)), xy.y_axis(label="Observations (count)", domain=(0, peak + 12)), xy.legend(ncols=2, style=legend_style(name)), xy.tooltip(), styling, title="Service time distribution", **shared)
    if mechanism == "heatmap":
        values = data["workload"].flatten()
        x, y = np.tile(np.arange(12.0), 7), np.repeat(np.arange(7.0), 12)
        paint = np.array(binned_colors(values, name, bins=4, domain=(0, 80)))
        marks = [xy.bar(x[paint == color], np.full(np.count_nonzero(paint == color), 0.88), base=y[paint == color] - 0.44, width=0.88, color=color, opacity=1, name=label)
                 for color, label in zip(sequential_colors(name), ("0–19", "20–39", "40–59", "60–80"), strict=True)]
        annotations = [xy.text(float(cx), float(cy), str(round(float(value))), dx=0, dy=0, anchor="middle", color=text_on(color))
                       for cx, cy, value, color in zip(x, y, values, paint, strict=True)]
        return xy.chart(*marks, *annotations, xy.x_axis(label="Hour of observation", domain=(-0.65, 11.65), tick_values=[0, 2, 4, 6, 8, 10], tick_labels=["08", "10", "12", "14", "16", "18"], grid=False), xy.y_axis(label="Day", domain=(-1.65, 6.65), tick_values=list(range(7)), tick_labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], reverse=True, grid=False), xy.legend(ncols=2, style=legend_style(name)), xy.tooltip(), styling, title="Workload by day and hour", **shared)
    if mechanism == "dense-scatter":
        # There is one unnamed measurement: use red for CS1 and blue for CS2.
        ink = colors[0] if name == "colorset1" else colors[1]
        return xy.chart(xy.scatter(data["dense_x"], data["dense_y"], color=ink, density=False, size=2, opacity=1, name="Individual observations"), xy.x_axis(label="Input deviation (units)", domain=(-4.5, 4.5)), xy.y_axis(label="Response deviation (units)", domain=(-4.5, 4.5)), xy.legend(show=False), xy.tooltip(), styling, title="8,000 observations", **shared)
    raise ValueError(f"Unknown mechanism: {mechanism}")


def render_card(item: dict) -> str:
    esc = html.escape
    label = "Color Set 1" if item["colorset"] == "colorset1" else "Color Set 2"
    return f'''<article class="chart-card" id="{item['id']}" data-example-id="{item['id']}" data-pattern-id="{item['id']}" data-colorset="{item['colorset']}" data-html="{item['html']}">
      <header class="card-top"><span class="palette-badge">{label}</span><a class="permalink" href="#{item['id']}" aria-label="Link to {esc(item['title'])} in {label}">#</a></header>
      <div class="chart-stage"><img class="chart-preview" src="{item['svg']}" width="{WIDTH}" height="{HEIGHT}" loading="lazy" alt="{esc(item['title'])}, {label}. {esc(item['summary'])}"></div>
      <footer class="card-actions"><button type="button" data-action="explore" aria-label="Explore {esc(item['title'])} in {label}">Explore chart <span aria-hidden="true">↗</span></button><a href="{item['svg']}" download>SVG</a><a href="{item['html']}" target="_blank" rel="noopener">Open HTML</a><a href="source/build.py" download>Python</a></footer>
    </article>'''


def render_gallery(items: list[dict], palettes: dict, output: Path) -> None:
    sections = []
    for index, (slug, title, heading, summary, detail) in enumerate(MECHANISMS, 1):
        cards = "\n".join(render_card(item) for item in items if item["mechanism"] == slug)
        sections.append(f'''<section class="example-section" id="{slug}" data-mechanism="{slug}"><div class="section-heading"><span class="section-number">{index:02d}</span><div><p class="eyebrow">{html.escape(title)}</p><h2>{html.escape(heading)}</h2><p class="section-summary">{html.escape(summary)}</p></div></div><div class="chart-pair">{cards}</div><p class="pattern-note">{html.escape(detail)}</p></section>''')
    swatches = []
    for name in PALETTES:
        palette = palettes[name]
        solids = list(dict.fromkeys(categorical_colors(name)))
        swatches.append(f'<div class="palette-strip" data-palette="{name}"><span>{"Color Set 1" if name == "colorset1" else "Color Set 2"}</span><div>' + "".join(f'<i style="background:{color}" title="{color}"><span>{color}</span></i>' for color in solids) + '</div></div>')
    template = (HERE / "gallery.html").read_text(encoding="utf-8")
    text = template.replace("{{SECTIONS}}", "\n".join(sections)).replace("{{SWATCHES}}", "\n".join(swatches))
    (output / "index.html").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    charts = output / "charts"
    source = output / "source"
    charts.mkdir(parents=True, exist_ok=True)
    source.mkdir(parents=True, exist_ok=True)
    data = synthetic_data()
    registered = {item["id"] for item in json.loads((HERE / "patterns.json").read_text(encoding="utf-8"))["patterns"]}
    expected = {f"reflex-xy-{slug}-{suffix}" for slug, *_ in MECHANISMS for suffix in ("cs1", "cs2")}
    if registered != expected:
        raise ValueError(f"Pattern registry drift: missing={sorted(expected - registered)}, extra={sorted(registered - expected)}")
    items = []
    for mechanism, title, heading, summary, detail in MECHANISMS:
        for name in PALETTES:
            suffix = "cs1" if name == "colorset1" else "cs2"
            item_id = f"reflex-xy-{mechanism}-{suffix}"
            chart = make_chart(mechanism, name, data)
            chart.to_html(charts / f"{item_id}.html", custom_css=css(name) + "\nhtml,body{margin:0;max-width:100%}.xy{box-sizing:border-box;max-width:100%}\n")
            svg = chart.to_svg(width=WIDTH, height=HEIGHT)
            svg = svg.replace("<svg ", f'<svg data-colorset="{name}" data-pattern-id="{item_id}" ', 1)
            (charts / f"{item_id}.svg").write_text(svg, encoding="utf-8")
            items.append({"id": item_id, "colorset": name, "mechanism": mechanism, "title": title, "summary": summary, "svg": f"charts/{item_id}.svg", "html": f"charts/{item_id}.html", "source": "source/build.py", "data_sha256": fingerprint(data), "width": WIDTH, "height": HEIGHT, "engine": "native"})
            print(f"Created {item_id}")
    palette_file = HELPER_DIR / "colorsets.json"
    if not palette_file.is_file():
        palette_file = HELPER_DIR.parent / "assets" / "palettes" / "colorsets.json"
    for origin in (Path(__file__).resolve(), HERE / "gallery.html", HELPER_DIR / "xy_colorsets.py", palette_file, HERE / "patterns.json"):
        target = source / origin.name
        if origin.resolve() != target.resolve():
            shutil.copyfile(origin, target)
    palettes = {name: load_palette(name) for name in PALETTES}
    render_gallery(items, palettes, output)
    (output / "manifest.json").write_text(json.dumps({"set_id": SET_ID, "package": "xy", "version": importlib.metadata.version("xy"), "seed": SEED, "data_fingerprint_format": "labelled-float32-le-v1", "data_sha256": fingerprint(data), "items": items, "palettes": palettes, "quantitative_color_note": "The binned matrix uses four exact-color data-unit rectangle marks with raw-value text labels. All categorical and numeric fills are opaque canonical solids; raster edge antialiasing may blend pixels."}, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(items)} charts and gallery in {output}")


if __name__ == "__main__":
    main()
