#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Build the XY 0.0.8 capability atlas with paired palettes and an API catalogue.

Run: uv run --script build.py --output-dir <directory>
Keep all downloaded source files together. No repository files are needed when
xy_colorsets.py and colorsets.json are beside this builder.
"""

from __future__ import annotations

import argparse
import dataclasses
from enum import Enum
import hashlib
import html
import importlib.metadata
import inspect
import json
from pathlib import Path
import re
import shutil
import struct
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

import xy

HERE = Path(__file__).resolve().parent
HELPER = HERE if (HERE / "xy_colorsets.py").is_file() else HERE.parents[2] / "scripts"
sys.path.insert(0, str(HELPER))
from xy_colorsets import css, load_palette
from xy_svg_compat import repair_duplicate_line_symbol_fill

SET_ID = "reflex-xy-capabilities"
VERSION = "0.0.8"
PALETTES = ("colorset1", "colorset2")
MODULES = ("core_marks", "polar_annotations", "advanced", "utilities")
UPSTREAM = "https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/"


def clean(value) -> str:
    return re.sub(r"<object object at 0x[0-9a-fA-F]+>", "<default sentinel>", str(value))


def serializable(value):
    if dataclasses.is_dataclass(value):
        return serializable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(k): serializable(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return [serializable(v) for v in sorted(value, key=repr)]
    if isinstance(value, (list, tuple)):
        return [serializable(v) for v in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return clean(value)


def callable_info(value) -> dict:
    result = {"kind": "class" if inspect.isclass(value) else "function" if callable(value) else "constant"}
    if inspect.isclass(value) and issubclass(value, Enum):
        result["values"] = [{"name": member.name, "value": member.value} for member in value]
    try:
        signature = inspect.signature(value)
    except (ValueError, TypeError):
        return result
    public = [p for p in signature.parameters.values() if not p.name.startswith("_") and p.name not in ("self", "cls")]
    result["signature"] = clean(signature.replace(parameters=public))
    result["parameters"] = [
        {"name": p.name, "annotation": "" if p.annotation is inspect.Parameter.empty else clean(p.annotation),
         "kind": p.kind.name, "default": None if p.default is inspect.Parameter.empty else clean(repr(p.default)),
         "required": p.default is inspect.Parameter.empty and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)}
        for p in signature.parameters.values() if not p.name.startswith("_") and p.name not in ("self", "cls")
    ]
    return result


def capture_api() -> dict:
    import xy.channels
    import xy.components
    import xy._validate
    import xy.pyplot as plt
    from xy.styling import capabilities

    exports = {name: callable_info(getattr(xy, name)) for name in xy.__all__}
    methods = {}
    for cls in (xy.Chart, xy.FacetChart, xy.Column, xy.ColumnStore, xy.Selection):
        methods[cls.__name__] = {
            name: callable_info(getattr(cls, name)) for name in dir(cls)
            if not name.startswith("_") and callable(getattr(cls, name))
        }
    finite = {}
    choices = {
        "Point symbols": "_POINT_SYMBOLS", "Line dash presets": "_DASH_PRESETS",
        "Line curves": "_CURVES", "Axis label positions": "_LABEL_POSITIONS",
        "Tick label strategies": "_TICK_LABEL_STRATEGIES", "Legend locations": "LEGEND_LOCATIONS",
        "Theta units": "_THETA_UNITS", "Theta directions": "_THETA_DIRECTIONS",
        "Polar grids": "_POLAR_GRID_SHAPES", "Theta compass zero": "_THETA_ZEROS",
        "Gradient spaces": "_FILL_SPACES", "Gradient directions": "_GRADIENT_DIRS",
    }
    for label, key in choices.items():
        finite[label] = serializable(getattr(xy._validate, key))
    finite["Built-in colormap names"] = list(xy.channels.COLORMAPS)
    finite["Theme token names"] = serializable(xy.components._THEME_TOKEN_NAMES)
    finite["Browser export formats"] = serializable(xy.components._EXPORT_CONFIG_FORMATS)
    pyplot_names = getattr(plt, "__all__", [n for n in dir(plt) if not n.startswith("_")])
    return {
        "package": "xy", "version": VERSION,
        "upstream_commit": "6483032a7947e1f44ced1a560ac08f1025637529",
        "scope": "Every top-level public export is catalogued. Examples demonstrate finite mechanisms and representative settings, not every combination or every optional argument.",
        "exports": exports, "methods": methods,
        "pyplot": {name: callable_info(getattr(plt, name)) for name in pyplot_names if hasattr(plt, name)},
        "finite_options": finite,
        "styling": {"summary": capabilities.summary(),
                    "mark_properties": serializable(capabilities.MARK_STYLE_PROPERTIES),
                    "axis_keys": capabilities.axis_style_keys(),
                    "dom_slots": serializable(capabilities.CHART_SLOTS),
                    "renderer_divergences": serializable(capabilities.KNOWN_RENDERER_DIVERGENCES)},
    }


def collect_cases(palette: str) -> list[dict]:
    import importlib
    return [item for name in MODULES for item in importlib.import_module(name).cases(palette)]


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def badges(item: dict) -> str:
    scope = "Exact palette paints" if item["paint_scope"] == "exact" else "Renderer-derived tones"
    repair = '<span class="badge">SVG compatibility repair</span>' if item.get("svg_compat_repairs") else ""
    return f'<span class="badge">{scope}</span><span class="badge">{esc(item["interaction"])}</span>{repair}'


def render_index(items: list[dict], api: dict, output: Path) -> None:
    sections = []
    categories = list(dict.fromkeys(item["category"] for item in items))
    order = {slug: i for i, slug in enumerate(dict.fromkeys(item["slug"] for item in items))}
    for category in categories:
        cards = []
        for item in sorted(items, key=lambda value: (order[value["slug"]], value["colorset"])):
            if item["category"] != category:
                continue
            search = " ".join([item["title"], item["summary"], *item["apis"], *[p for v in item["parameters"].values() for p in v]])
            cards.append(f'''<article id="{item['id']}" data-pattern-id="{item['id']}" data-case="{item['slug']}" data-colorset="{item['colorset']}" data-height="{item['height']}" data-search="{esc(search.lower())}" data-html="{item['html']}">
<header class="card-head"><div><small>{esc(item['category'])} · {'CS1' if item['colorset']=='colorset1' else 'CS2'}</small><h3>{esc(item['title'])}</h3></div><a href="#{item['id']}" aria-label="Link to {esc(item['title'])}">#</a></header>
<p class="summary">{esc(item['summary'])}</p><div class="stage" style="--ratio:{item['width']}/{item['height']}"><img class="preview" src="{item['svg']}" loading="lazy" width="{item['width']}" height="{item['height']}" alt="{esc(item['title'])}, {esc(item['colorset'])}"></div>
<div class="card-tools"><button type="button" data-explore aria-expanded="false">Explore chart ↗</button><a href="{item['html']}" target="_blank" rel="noopener">HTML ↗</a><a href="{item['svg']}" download>SVG ↓</a><a href="{item['png']}" download>PNG ↓</a><a href="source/{item['source']}">Python</a></div>
<div class="badges">{badges(item)}</div><details><summary>Options and implementation</summary><p>{esc(item['detail'])}</p><p class="api-tags">{''.join(f'<a href="api.html#{esc(name)}">xy.{esc(name)}</a>' for name in item['apis'])}</p><pre>{esc(json.dumps(item['parameters'],indent=2))}</pre></details></article>''')
        sections.append(f'<section class="family" data-category="{esc(category)}"><h2>{esc(category)}</h2><div class="cards">{"".join(cards)}</div></section>')
    options = ''.join(f'<option value="{esc(category)}">{esc(category)}</option>' for category in categories)
    template = (HERE / "gallery.html").read_text(encoding="utf-8")
    replacements = {"{{SECTIONS}}": "\n".join(sections), "{{CATEGORIES}}": options,
                    "{{COUNT}}": str(len(items)), "{{MECHANISMS}}": str(len(items)//2),
                    "{{API_COUNT}}": str(len(api["exports"]))}
    for token, value in replacements.items():
        template = template.replace(token, value)
    (output / "index.html").write_text(template, encoding="utf-8")


TYPE_FACTORIES = {
    "Chart": ["chart"], "FacetChart": ["facet_chart"], "Mark": ["scatter", "line", "area", "bar"],
    "Axis": ["x_axis", "y_axis", "theta_axis", "r_axis"], "Annotation": ["text", "arrow", "threshold"],
    "Animation": ["animation"], "Spring": ["spring"], "Theme": ["theme"],
    "Legend": ["legend"], "Tooltip": ["tooltip"], "Colorbar": ["colorbar"],
    "Modebar": ["modebar"], "Interaction": ["interaction_config"], "ExportConfig": ["export_config"],
    "Component": ["chart"], "MarkPlugin": ["register_mark"], "MarkContext": ["mark"],
}
HOST_APIS = {"Column", "ColumnStore", "ZoneMaps", "Selection", "Engine", "write_images", "structural_probe", "unregister_mark", "export_config"}


def render_api(items: list[dict], api: dict, output: Path) -> None:
    coverage = {}
    rows = []
    for name, record in api["exports"].items():
        direct = [item for item in items if name in item["apis"]]
        typed = [item for item in items if any(factory in item["apis"] for factory in TYPE_FACTORIES.get(name, []))]
        examples = list({item["slug"]: item for item in [*direct, *typed] if item["colorset"] == "colorset1"}.values())
        kind = ("Catalogued constant" if record["kind"] == "constant" else
                "Returned low-level type" if name == "ZoneMaps" else
                "Export engine enum" if name == "Engine" else
                "Visual example" if direct else "Returned type" if typed else
                "Live/technical recipe" if name in HOST_APIS else "API reference")
        exercised = sorted({p for item in direct for p in item["parameters"].get(name, [])})
        coverage[name] = {"coverage": kind, "examples": [i["id"] for i in examples], "explicit_parameters": exercised}
        links = ''.join(f'<a href="index.html#{i["id"]}">{esc(i["title"])}</a>' for i in examples[:5])
        if name in HOST_APIS:
            links += '<a href="hosts.html">Executable host and data recipes</a>'
        parameters = []
        for p in record.get("parameters", []):
            label = "explicit in example" if p["name"] in exercised else "available option"
            parameters.append(f'<li><code>{esc(p["name"])}</code> <span>{esc(p["annotation"])}</span><small>{label}; {"required" if p["required"] else "default: " + esc(p["default"])}</small></li>')
        enum_values = f'<pre>{esc(json.dumps(record["values"],indent=2))}</pre>' if "values" in record else ""
        rows.append(f'<article class="api-entry" id="{esc(name)}" data-api="{esc(name.lower())}"><h2><code>xy.{esc(name)}</code><span class="badge">{kind}</span></h2><pre>{esc(record.get("signature", record["kind"]))}</pre>{enum_values}<div class="api-links">{links}</div><details><summary>Parameters ({len(parameters)})</summary><ul class="parameter-list">{"".join(parameters)}</ul></details></article>')
    api["coverage"] = coverage
    method_rows = []
    for cls, methods in api["methods"].items():
        method_rows.append(f'<details><summary>{esc(cls)} · {len(methods)} public methods</summary>' + ''.join(f'<h3><code>{esc(name)}</code></h3><pre>{esc(record.get("signature", ""))}</pre>' for name, record in methods.items()) + '</details>')
    option_rows = ''.join(f'<details><summary>{esc(label)}</summary><pre>{esc(json.dumps(values,indent=2))}</pre></details>' for label, values in api["finite_options"].items())
    style_rows = ''.join(f'<details><summary>{esc(key.replace("_", " "))}</summary><pre>{esc(json.dumps(value,indent=2))}</pre></details>' for key, value in api["styling"].items())
    pyplot_rows = ''.join(f'<details><summary><code>xy.pyplot.{esc(name)}</code></summary><pre>{esc(record.get("signature",record["kind"]))}</pre></details>' for name, record in api["pyplot"].items())
    body = f'''<p class="eyebrow">XY {VERSION} · public surface</p><h1>{len(api['exports'])} public exports.<br><em>Every option, indexed.</em></h1><p class="lead">Inspect actual installed signatures, find examples and distinguish explicit demonstrations from available parameters. No claim is made that every parameter combination is visualized.</p>
<div class="notice">Factory aliases and returned types are included. Underscore-prefixed adapter arguments are excluded. Browser CSS, native output and live Python have different capabilities; consult the recorded support entries.</div>
<nav class="jump"><a href="#exports">Core API</a><a href="#methods">Methods</a><a href="#options">Finite choices</a><a href="#styling">Styling registry</a><a href="#pyplot">xy.pyplot ({len(api['pyplot'])})</a><a href="api.json" download>Download JSON ↓</a></nav>
<label class="search-label">Find a public export<input id="api-search" type="search" placeholder="scatter, animation, ColumnStore…"></label><section id="exports">{''.join(rows)}</section><section id="methods"><h2>Public object methods</h2>{''.join(method_rows)}</section><section id="options"><h2>Finite option vocabularies</h2><p>Values are extracted from the matching release's validators. Built-in colormap names are listed; chart examples use the selected colorset, with interpolation disclosed where a native continuous renderer requires it.</p>{option_rows}</section><section id="styling"><h2>Renderer styling support</h2>{style_rows}</section><section id="pyplot"><h2>Matplotlib-style adapter</h2><p>The executable host recipe demonstrates pyplot construction and export. This index records the adapter surface; it does not promise complete Matplotlib compatibility.</p>{pyplot_rows}</section>'''
    page(output / "api.html", "XY API and option catalogue", body, '<script>document.querySelector("#api-search").addEventListener("input",e=>{const q=e.target.value.toLowerCase();document.querySelectorAll("[data-api]").forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(q))})</script>')


def page(path: Path, title: str, body: str, script: str = "") -> None:
    path.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><link rel="stylesheet" href="atlas.css"></head><body data-colorset="colorset2"><header class="site-head"><a href="index.html">XY capability atlas</a><nav><a href="api.html">API & options</a><a href="hosts.html">Hosts & exports</a><a href="source.zip" download>All Python source ↓</a></nav></header><main class="document">{body}</main>{script}</body></html>', encoding="utf-8")


def render_hosts(output: Path, exports: list[str]) -> None:
    downloads = ''.join(f'<a href="{path}" download>{esc(Path(path).name)}</a>' for path in exports)
    resources = ''.join(f'<a href="{path.relative_to(output).as_posix()}" download>{esc(path.relative_to(output / "host-artifacts"))}</a>' for path in sorted((output / "host-artifacts").rglob("*")) if path.is_file() and path.suffix in (".html", ".py", ".json", ".toml"))
    body = f'''<p class="eyebrow">Delivery modes · data · live Python</p><h1>Choose the host.<br><em>Keep the contract.</em></h1><p class="lead">All gallery charts are actual XY exports. Standalone HTML can hover, pan, zoom and use client controls; future Python updates and callbacks need a running host.</p>
<div class="host-grid"><article><h2>Standalone HTML</h2><p>Self-contained client and data, with no CDN. Explore/download any chart. Each file is a snapshot; re-export after Python mutation.</p></article><article><h2>Native export</h2><p>SVG, PNG, PDF, JPEG and WebP use the native engine. Raster layers can appear in density/grid SVGs. Native output does not reproduce every browser CSS slot.</p><div class="api-links">{downloads}</div></article><article><h2>Notebook widget</h2><p>Use chart.widget() with a live kernel for callbacks, programmatic selection and streamed append batches. A static screenshot does not establish callback delivery.</p><a href="source/host_examples.py">Host and data Python recipe</a></article><article><h2>Reflex application</h2><p>The source demonstrates four tiers: a concrete chart for static Reflex export, shared inline live events, @data column updates and @figure structural updates. The last three need a running Python backend. GitHub Pages serves their source and chart snapshots.</p><a href="source/host_examples.py">Executable integration recipe</a></article></div>
<h2>Run locally</h2><pre>uv run --script build.py --output-dir gallery\nuv run --script host_examples.py --output-dir results
uv run --with "xy[reflex]==0.0.8" --with "reflex==0.10.0" --script host_examples.py --output-dir live-results --with-reflex</pre><p>Download and extract <a href="source.zip">all source files</a> together. The JSON reports record which native/programmatic paths actually ran. Optional integrations declare their dependencies in the source.</p><div class="api-links"><a href="host-report.json">Host validation report</a><a href="data-report.json">Column store and registry report</a><a href="source/data_tools.py">Low-level data Python recipe</a><a href="api.json">API / finite option JSON</a><a href="manifest.json">Gallery manifest</a></div>
<h2>Generated host artifacts</h2><p>Core snapshots, source and reports are generated during this build. Optional Reflex compilation is requested with the explicit extras above; callback delivery still needs an actual running frontend.</p><div class="api-links">{resources}</div><h2>Coverage boundaries</h2><p>The atlas covers all installed top-level public exports in its catalogue and demonstrates each implemented visual family in two palettes. Numeric arguments, arbitrary data, CSS strings and callback code have unbounded combinations. Parameters marked “available option” are indexed from signatures rather than falsely counted as independently tested examples.</p><p>XY 0.0.8 is the pinned baseline. All data are fictional. Derived-tone cards intentionally demonstrate native interpolation, opacity, gradients or density; exact-paint cards use canonical base colors. This distinction also applies to antialiased raster edges.</p><p>Official source: <a href="{UPSTREAM}python/xy/__init__.py">public API</a>, <a href="{UPSTREAM}python/xy/styling/capabilities.py">styling registry</a>, <a href="https://reflex.dev/docs/xy/">documentation</a>.</p>'''
    page(output / "hosts.html", "XY hosts, data and export recipes", body)


def build(output: Path, only: list[str]) -> None:
    if importlib.metadata.version("xy") != VERSION:
        raise RuntimeError(f"This atlas targets xy=={VERSION}; use its declared environment")
    output.mkdir(parents=True, exist_ok=True)
    (output / "charts").mkdir(exist_ok=True)
    source = output / "source"
    source.mkdir(exist_ok=True)
    registry = json.loads((HERE / "patterns.json").read_text(encoding="utf-8"))
    expected = {p["id"] for p in registry["patterns"]}
    items = []
    for palette in PALETTES:
        for case in collect_cases(palette):
            if only and case["id"] not in only:
                continue
            chart = case.pop("chart")
            slug = case.pop("id")
            item_id = f'xy-{slug}-cs{palette[-1]}'
            stem = output / "charts" / item_id
            export_css = css(palette)
            if isinstance(chart, xy.FacetChart):
                roles = load_palette(palette)["roles"]
                grid_width = int(chart.props["width"])
                export_css += f'\n.xy-facet-document .xy-facet-title{{color:{roles["inkDark"]}}}.xy-facet-document{{background:{roles["background"]};overflow-x:auto}}.xy-facet-document .xy-facet-grid{{width:{grid_width}px}}\n'
                case["detail"] += " XY 0.0.8 facets use integer grid dimensions; the standalone grid scrolls horizontally on narrow screens instead of shrinking fixed-width child panels. Native SVG and PNG compose the facet heading differently; the manifest records each format's actual dimensions."
            chart.to_html(str(stem.with_suffix(".html")), custom_css=export_css)
            if isinstance(chart, xy.FacetChart):
                svg = chart.to_svg()
                chart.to_png(str(stem.with_suffix(".png")), scale=1)
            else:
                svg = chart.to_svg(width=840)
                chart.to_png(str(stem.with_suffix(".png")), width=840, scale=1)
            original_svg = svg
            svg, repairs = repair_duplicate_line_symbol_fill(svg)
            original_path = None
            if repairs:
                (output / "compat-originals").mkdir(exist_ok=True)
                original_path = f"compat-originals/{item_id}.svg.txt"
                (output / original_path).write_text(original_svg, encoding="utf-8")
                case["detail"] += " The native line-only glyph SVG has a known duplicate-fill defect in 0.0.8. The builder preserves its original text and applies the bundled narrow XML compatibility repair without changing stroke or geometry."
            root = ET.fromstring(svg)
            width, height = [int(float(root.attrib[key].removesuffix("px"))) for key in ("width", "height")]
            png = stem.with_suffix(".png").read_bytes()
            if png[:8] != b"\x89PNG\r\n\x1a\n":
                raise RuntimeError(f"Invalid native PNG for {item_id}")
            png_width, png_height = struct.unpack(">II", png[16:24])
            svg = svg.replace("<svg ", f'<svg data-colorset="{palette}" data-pattern-id="{item_id}" data-paint-scope="{case["paint_scope"]}" data-svg-compat-repairs="{repairs}" ', 1)
            stem.with_suffix(".svg").write_text(svg, encoding="utf-8")
            module = next(name for name in MODULES if slug in Path(HERE / f"{name}.py").read_text(encoding="utf-8"))
            items.append({**case, "id": item_id, "slug": slug, "colorset": palette,
                          "width": width, "height": height, "svg": f"charts/{item_id}.svg",
                          "png_width": png_width, "png_height": png_height,
                          "html": f"charts/{item_id}.html", "png": f"charts/{item_id}.png",
                          "source": f"{module}.py", "svg_compat_repairs": repairs,
                          "original_svg_text": original_path})
            print(f"Created {item_id}")
    actual = {item["id"] for item in items}
    if not only and actual != expected:
        raise RuntimeError(f"Registry drift: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    api = capture_api()
    render_index(items, api, output)
    render_api(items, api, output)
    samples = []
    for palette in PALETTES:
        sample = next(c["chart"] for c in collect_cases(palette) if c["id"] == "line-dash-curves")
        for extension in ("pdf", "jpg", "webp"):
            path = f'charts/xy-export-sample-cs{palette[-1]}.{extension}'
            sample.write_image(str(output / path), width=840, height=480, scale=1,
                               background=load_palette(palette)["roles"]["background"])
            samples.append(path)
    import host_examples
    host_report = host_examples.run(output / "host-artifacts", include_reflex=False)
    (output / "host-report.json").write_text(json.dumps(host_report, indent=2) + "\n", encoding="utf-8")
    import data_tools
    data_report = data_tools.run(output / "data-artifacts")
    (output / "data-report.json").write_text(json.dumps(data_report, indent=2) + "\n", encoding="utf-8")
    render_hosts(output, samples)
    for path in HERE.iterdir():
        if path.suffix in (".py", ".html", ".css", ".json"):
            shutil.copyfile(path, source / path.name)
    palette_path = HELPER / "colorsets.json"
    if not palette_path.is_file():
        palette_path = HELPER.parent / "assets/palettes/colorsets.json"
    shutil.copyfile(HELPER / "xy_colorsets.py", source / "xy_colorsets.py")
    shutil.copyfile(HELPER / "xy_svg_compat.py", source / "xy_svg_compat.py")
    shutil.copyfile(palette_path, source / "colorsets.json")
    shutil.copyfile(HERE / "atlas.css", output / "atlas.css")
    shutil.make_archive(str(output / "source"), "zip", source)
    (output / "api.json").write_text(json.dumps(api, indent=2) + "\n", encoding="utf-8")
    manifest = {"set_id": SET_ID, "version": VERSION, "upstream_commit": api["upstream_commit"],
                "public_export_count": len(api["exports"]), "mechanism_count": len(items)//2,
                "items": items, "palettes": {name: load_palette(name) for name in PALETTES},
                "source_files": sorted(p.name for p in source.iterdir()), "export_samples": samples,
                "scope": api["scope"]}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if "gallery_normalized_path" in xy.registered_marks():
        xy.unregister_mark("gallery_normalized_path")
    print(f"Built {len(items)} charts and {len(api['exports'])} public API entries in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--only", action="append", default=[], help="Maintenance subset by semantic case ID")
    args = parser.parse_args()
    build(args.output_dir.resolve(), args.only)
