#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import colorsys
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
EXAMPLE_DIR = SCRIPT_DIR.parent
SKILL_DIR = EXAMPLE_DIR.parents[2]
MANIFEST_PATH = EXAMPLE_DIR / "manifest.json"
STYLER_PATH = SKILL_DIR / "scripts" / "style_mermaid_directory.py"
DIAGRAM_TYPES_PATH = SKILL_DIR / "references" / "diagram-types.json"
MERMAID_CLI_PACKAGE = "@mermaid-js/mermaid-cli@11.16.0"
COLOR_RE = re.compile(r"#[0-9a-fA-F]{6}\b")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def load_styler():
    spec = importlib.util.spec_from_file_location("mermaid_max_element_styler", STYLER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load the Mermaid styler: {STYLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_for_case(manifest: dict[str, Any], case: dict[str, Any]) -> str:
    sources = manifest.get("sources", {})
    if not isinstance(sources, dict):
        return ""
    source = sources.get(str(case.get("source", "")), "")
    return source if isinstance(source, str) else ""


def probe_labels(case: dict[str, Any]) -> list[str]:
    labels = [str(value) for value in case.get("requiredLabels", [])]
    for probe in case.get("probes", []):
        prefix = str(probe["prefix"])
        suffix = str(probe.get("suffix", ""))
        padding = int(probe.get("pad", 0))
        for index in range(int(probe["start"]), int(probe["end"]) + 1):
            number = str(index).zfill(padding) if padding else str(index)
            labels.append(f"{prefix}{number}{suffix}")
    return labels


def rendered_probe_labels(case: dict[str, Any]) -> list[str]:
    render_case = dict(case)
    if "renderRequiredLabels" in case:
        render_case["requiredLabels"] = case["renderRequiredLabels"]
    if "renderProbes" in case:
        render_case["probes"] = case["renderProbes"]
    return probe_labels(render_case)


def normalized_svg_text(svg: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", html.unescape(svg))
    return " ".join(without_tags.split())


def expected_style_keys(case: dict[str, Any]) -> list[str]:
    style = case.get("style", {})
    keys = [str(value) for value in style.get("exact", [])]
    for item in style.get("ranges", []):
        prefix = str(item["prefix"])
        if prefix == "class:":
            continue
        suffix = str(item.get("suffix", ""))
        keys.extend(
            f"{prefix}{index}{suffix}"
            for index in range(int(item["start"]), int(item["end"]) + 1)
        )
    return keys


def contract_tokens(contract: dict[str, Any]) -> list[str]:
    tokens = [str(value) for value in contract.get("tokens", [])]
    for item in contract.get("ranges", []):
        prefix = str(item["prefix"])
        suffix = str(item.get("suffix", ""))
        tokens.extend(
            f"{prefix}{index}{suffix}"
            for index in range(int(item["start"]), int(item["end"]) + 1)
        )
    return tokens


def contract_style_keys(contract: dict[str, Any]) -> list[str]:
    return expected_style_keys(
        {
            "style": {
                "exact": contract.get("styleExact", []),
                "ranges": contract.get("styleRanges", []),
            }
        }
    )


def rendered_color_forms(color: str) -> tuple[str, str, str]:
    red, green, blue = (int(color[index : index + 2], 16) for index in (1, 3, 5))
    return (
        color.lower(),
        f"rgb({red}, {green}, {blue})",
        f"rgb({red},{green},{blue})",
    )


def css_color_to_rgb(value: str) -> tuple[int, int, int] | None:
    normalized = re.sub(r"\s*!important\s*$", "", value.strip().lower())
    hex_match = re.fullmatch(r"#([0-9a-f]{6})", normalized)
    if hex_match:
        payload = hex_match.group(1)
        return tuple(int(payload[index : index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]

    rgb_match = re.fullmatch(
        r"rgba?\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)(?:\s*,[^)]+)?\)",
        normalized,
    )
    if rgb_match:
        return tuple(round(float(rgb_match.group(index))) for index in (1, 2, 3))  # type: ignore[return-value]

    hsl_match = re.fullmatch(
        r"hsla?\(\s*([-0-9.]+)\s*,\s*([0-9.]+)%\s*,\s*([0-9.]+)%(?:\s*,[^)]+)?\)",
        normalized,
    )
    if hsl_match:
        hue = (float(hsl_match.group(1)) % 360.0) / 360.0
        saturation = float(hsl_match.group(2)) / 100.0
        lightness = float(hsl_match.group(3)) / 100.0
        red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
        return tuple(round(channel * 255) for channel in (red, green, blue))
    return None


def transformed_theme_rgb(
    color: str, transform: str | None = None, amount: float = 0.0
) -> tuple[int, int, int] | None:
    rgb = css_color_to_rgb(color)
    if rgb is None or transform is None:
        return rgb
    if transform not in {"lighten", "darken"}:
        raise ValueError(f"Unsupported render-contract color transform: {transform}")
    red, green, blue = (channel / 255.0 for channel in rgb)
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    adjustment = amount / 100.0
    if transform == "darken":
        adjustment *= -1
    lightness = min(1.0, max(0.0, lightness + adjustment))
    adjusted = colorsys.hls_to_rgb(hue, lightness, saturation)
    return tuple(round(channel * 255) for channel in adjusted)


def css_property_for_selector(svg: str, selector: str, property_name: str) -> str | None:
    selector_pattern = re.compile(
        re.escape(selector) + r"(?![A-Za-z0-9_-])[^{}]*\{([^{}]*)\}",
        re.IGNORECASE,
    )
    property_pattern = re.compile(
        rf"(?:^|;)\s*{re.escape(property_name)}\s*:\s*([^;}}]+)",
        re.IGNORECASE,
    )
    for selector_match in selector_pattern.finditer(svg):
        property_match = property_pattern.search(selector_match.group(1))
        if property_match:
            return property_match.group(1).strip()
    return None


def validate_css_bindings(
    family: str,
    colorset: str,
    theme: dict[str, Any],
    contract: dict[str, Any],
    svg: str,
    findings: list[str],
) -> None:
    for binding in contract.get("cssBindings", []):
        selector_start = int(binding["selectorStart"])
        selector_end = int(binding["selectorEnd"])
        theme_start = int(binding["themeStart"])
        property_name = str(binding.get("property", "fill"))
        observed_colors: list[tuple[int, int, int]] = []
        for offset, selector_index in enumerate(range(selector_start, selector_end + 1)):
            selector = str(binding["selectorTemplate"]).format(index=selector_index)
            theme_key = f"{binding['themePrefix']}{theme_start + offset}"
            actual_value = css_property_for_selector(svg, selector, property_name)
            if actual_value is None:
                findings.append(
                    f"{family}/{colorset}: rendered CSS selector {selector!r} has no "
                    f"{property_name} declaration"
                )
                continue
            actual_rgb = css_color_to_rgb(actual_value)
            expected_rgb = transformed_theme_rgb(
                str(theme.get(theme_key, "")),
                str(binding["transform"]) if "transform" in binding else None,
                float(binding.get("amount", 0.0)),
            )
            if actual_rgb is None or expected_rgb is None:
                findings.append(
                    f"{family}/{colorset}: could not parse CSS binding {selector!r} "
                    f"({actual_value!r}) or theme key {theme_key!r}"
                )
                continue
            observed_colors.append(actual_rgb)
            if max(abs(actual - expected) for actual, expected in zip(actual_rgb, expected_rgb)) > 1:
                findings.append(
                    f"{family}/{colorset}: {selector} {property_name}={actual_value} "
                    f"does not match {theme_key} after its declared transform"
                )
        expected_count = selector_end - selector_start + 1
        if len(observed_colors) == expected_count and len(set(observed_colors)) != expected_count:
            findings.append(
                f"{family}/{colorset}: indexed CSS bindings contain only "
                f"{len(set(observed_colors))} distinct colors; expected {expected_count}"
            )


def _class_tokens(element: ET.Element) -> set[str]:
    return set(element.attrib.get("class", "").split())


def _local_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _paint_value(element: ET.Element, property_name: str) -> str | None:
    style = element.attrib.get("style", "")
    match = re.search(
        rf"(?:^|;)\s*{re.escape(property_name)}\s*:\s*([^;]+)",
        style,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    return element.attrib.get(property_name)


def _first_descendant(
    element: ET.Element, tag_name: str, class_tokens: set[str] | None = None
) -> ET.Element | None:
    for descendant in element.iter():
        if _local_name(descendant) != tag_name:
            continue
        if class_tokens and not class_tokens.issubset(_class_tokens(descendant)):
            continue
        return descendant
    return None


def _assert_geometry_color(
    family: str,
    colorset: str,
    label: str,
    actual_value: str | None,
    expected_value: str,
    findings: list[str],
) -> None:
    actual_rgb = css_color_to_rgb(actual_value or "")
    expected_rgb = css_color_to_rgb(expected_value)
    if actual_rgb is None or expected_rgb is None or actual_rgb != expected_rgb:
        findings.append(
            f"{family}/{colorset}: geometry {label} uses {actual_value!r}; "
            f"expected {expected_value}"
        )


def validate_inline_geometry_colors(
    styler,
    family: str,
    colorset: str,
    theme: dict[str, Any],
    source: str,
    svg: str,
    findings: list[str],
) -> None:
    if family not in {"pie", "sankey", "xyChart", "treemap", "venn"}:
        return
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        findings.append(f"{family}/{colorset}: could not parse rendered SVG XML: {error}")
        return

    elements = list(root.iter())
    if family == "pie":
        slices = [
            element
            for element in elements
            if _local_name(element) == "path" and "pieCircle" in _class_tokens(element)
        ]
        if len(slices) != 12:
            findings.append(f"{family}/{colorset}: found {len(slices)} slice paths; expected 12")
        for index, element in enumerate(slices[:12], start=1):
            _assert_geometry_color(
                family,
                colorset,
                f"slice {index}",
                _paint_value(element, "fill"),
                str(theme[f"pie{index}"]),
                findings,
            )
    elif family == "sankey":
        nodes = [element for element in elements if "node" in _class_tokens(element)]
        expected = list(styler.sankey_node_colors(source, colorset).values())
        if len(nodes) != len(expected):
            findings.append(
                f"{family}/{colorset}: found {len(nodes)} node groups; expected {len(expected)}"
            )
        for index, (node, color) in enumerate(zip(nodes, expected), start=1):
            rect = _first_descendant(node, "rect")
            _assert_geometry_color(
                family,
                colorset,
                f"node {index}",
                _paint_value(rect, "fill") if rect is not None else None,
                color,
                findings,
            )
    elif family == "xyChart":
        palette = [
            value.strip()
            for value in str(theme.get("xyChart", {}).get("plotColorPalette", "")).split(",")
            if value.strip()
        ]
        plots: dict[int, ET.Element] = {}
        for element in elements:
            for token in _class_tokens(element):
                match = re.fullmatch(r"(?:bar|line)-plot-(\d+)", token)
                if match:
                    plots[int(match.group(1))] = element
        if sorted(plots) != list(range(6)):
            findings.append(
                f"{family}/{colorset}: rendered plot indices are {sorted(plots)}; expected 0 through 5"
            )
        for index in range(6):
            plot = plots.get(index)
            geometry = None if plot is None else next(
                (
                    item
                    for item in plot.iter()
                    if _local_name(item) in {"rect", "path"}
                ),
                None,
            )
            property_name = "fill" if geometry is not None and _local_name(geometry) == "rect" else "stroke"
            _assert_geometry_color(
                family,
                colorset,
                f"plot {index}",
                _paint_value(geometry, property_name) if geometry is not None else None,
                palette[index % len(palette)],
                findings,
            )
    elif family == "treemap":
        for index in range(12):
            class_tokens = {"treemapSection", f"section{index + 1}"}
            rect = next(
                (
                    element
                    for element in elements
                    if _local_name(element) == "rect"
                    and class_tokens.issubset(_class_tokens(element))
                ),
                None,
            )
            _assert_geometry_color(
                family,
                colorset,
                f"named hierarchy slot {index + 1}",
                _paint_value(rect, "fill") if rect is not None else None,
                str(theme[f"cScale{index}"]),
                findings,
            )
    elif family == "venn":
        for index in range(8):
            group = next(
                (
                    element
                    for element in elements
                    if f"venn-set-{index}" in _class_tokens(element)
                ),
                None,
            )
            path = _first_descendant(group, "path") if group is not None else None
            _assert_geometry_color(
                family,
                colorset,
                f"set {index + 1}",
                _paint_value(path, "fill") if path is not None else None,
                str(theme[f"venn{index + 1}"]),
                findings,
            )


def validate_semantic_class_bindings(
    styler,
    family: str,
    colorset: str,
    semantic_classes: list[str],
    svg: str,
    findings: list[str],
) -> None:
    """Prove every semantic role is bound to distinct rendered geometry."""

    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        findings.append(f"{family}/{colorset}: could not parse rendered SVG XML: {error}")
        return

    geometry_tags = {"circle", "ellipse", "path", "polygon", "rect"}
    css_svg = html.unescape(svg)
    carriers: dict[str, ET.Element] = {}
    for class_name in semantic_classes:
        carrier = next(
            (
                element
                for element in root.iter()
                if class_name in _class_tokens(element)
                and any(_local_name(child) in geometry_tags for child in element.iter())
            ),
            None,
        )
        if carrier is None:
            findings.append(
                f"{family}/{colorset}: semantic role {class_name} is not bound "
                "to rendered geometry"
            )
            continue
        carriers[class_name] = carrier
        expected_declaration = styler.class_style(colorset, class_name)
        for property_name in ("fill", "stroke"):
            expected_match = re.search(
                rf"\b{property_name}:([^,;]+)", expected_declaration
            )
            actual_value = next(
                (
                    value
                    for child in carrier.iter()
                    if _local_name(child) in geometry_tags
                    for value in [_paint_value(child, property_name)]
                    if value
                    and value.casefold() not in {"none", "transparent"}
                ),
                None,
            )
            if not actual_value or actual_value.casefold() in {"none", "transparent"}:
                actual_value = css_property_for_selector(
                    css_svg, f".{class_name}>*", property_name
                )
            expected_value = expected_match.group(1).strip() if expected_match else ""
            _assert_geometry_color(
                family,
                colorset,
                f"semantic role {class_name} {property_name}",
                actual_value,
                expected_value,
                findings,
            )

    if len(carriers) == len(semantic_classes) and len(
        {id(element) for element in carriers.values()}
    ) != len(semantic_classes):
        findings.append(
            f"{family}/{colorset}: semantic roles are not bound to "
            f"{len(semantic_classes)} distinct rendered elements"
        )


def iter_hex_colors(value: object) -> Iterable[str]:
    if isinstance(value, dict):
        for nested in value.values():
            yield from iter_hex_colors(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_hex_colors(nested)
    elif isinstance(value, str):
        yield from (match.group(0).lower() for match in COLOR_RE.finditer(value))


def validate_manifest(
    manifest: dict[str, Any], diagram_types: dict[str, Any], findings: list[str]
) -> list[dict[str, Any]]:
    cases = manifest.get("families")
    if not isinstance(cases, list) or not all(isinstance(case, dict) for case in cases):
        findings.append("manifest families must be a list of objects")
        return []

    expected_ids = [str(family["id"]) for family in diagram_types.get("families", [])]
    actual_ids = [str(case.get("id")) for case in cases]
    if len(actual_ids) != 31:
        findings.append(f"manifest has {len(actual_ids)} families; expected 31")
    if len(set(actual_ids)) != len(actual_ids):
        findings.append("manifest family IDs are not unique")
    if set(actual_ids) != set(expected_ids):
        findings.append(
            "manifest family identities differ from diagram-types.json: "
            f"missing={sorted(set(expected_ids) - set(actual_ids))}, "
            f"unexpected={sorted(set(actual_ids) - set(expected_ids))}"
        )

    if manifest.get("mermaidVersion") != diagram_types.get("upstream", {}).get("version"):
        findings.append("manifest Mermaid version does not match diagram-types.json")

    valid_capacity_kinds = {
        "configured-cycle",
        "fixed-cycle",
        "reachable-cycle",
        "semantic-classes",
        "semantic-roles",
        "unbounded-uniform",
    }
    render_contracts = manifest.get("renderContracts")
    if not isinstance(render_contracts, dict) or not all(
        isinstance(key, str) and isinstance(value, dict)
        for key, value in render_contracts.items()
    ):
        findings.append("manifest renderContracts must be an object of objects")
        render_contracts = {}

    sources = manifest.get("sources")
    if not isinstance(sources, dict) or not all(
        isinstance(key, str) and isinstance(value, str) and value.strip()
        for key, value in sources.items()
    ):
        findings.append("manifest sources must map source names to non-empty Mermaid text")
        sources = {}

    referenced_sources = {str(case.get("source", "")) for case in cases}
    if set(sources) != referenced_sources:
        findings.append(
            "manifest embedded sources differ from family source references: "
            f"missing={sorted(referenced_sources - set(sources))}, "
            f"unexpected={sorted(set(sources) - referenced_sources)}"
        )

    for case in cases:
        family = str(case.get("id"))
        source_name = str(case.get("source", ""))
        source_path = Path(source_name)
        if (
            source_path.is_absolute()
            or ".." in source_path.parts
            or source_path.suffix.casefold() != ".mmd"
        ):
            findings.append(f"{family}: source must be a portable relative .mmd name")
        if not source_for_case(manifest, case).strip():
            findings.append(f"{family}: embedded source is missing or empty")
        if case.get("capacityKind") not in valid_capacity_kinds:
            findings.append(f"{family}: unknown capacityKind {case.get('capacityKind')!r}")
        max_slots = case.get("maxSlots")
        fixture_count = case.get("fixtureElementCount")
        if not isinstance(fixture_count, int) or fixture_count < 2:
            findings.append(f"{family}: fixtureElementCount must be at least 2")
        if max_slots is not None and (
            not isinstance(max_slots, int) or max_slots < 1 or fixture_count < max_slots
        ):
            findings.append(
                f"{family}: finite maxSlots must be positive and reached by fixtureElementCount"
            )
        if case.get("capacityKind") == "unbounded-uniform" and max_slots is not None:
            findings.append(f"{family}: unbounded capacity must not claim a finite maximum")

    cyclic_ids = {
        str(case["id"])
        for case in cases
        if case.get("capacityKind")
        in {"configured-cycle", "fixed-cycle", "reachable-cycle"}
    }
    if set(render_contracts) != cyclic_ids:
        findings.append(
            "render contracts must cover every cyclic palette family exactly: "
            f"missing={sorted(cyclic_ids - set(render_contracts))}, "
            f"unexpected={sorted(set(render_contracts) - cyclic_ids)}"
        )
    return cases


def validate_sources_and_style(
    styler,
    manifest: dict[str, Any],
    cases: list[dict[str, Any]],
    work_dir: Path,
    findings: list[str],
) -> dict[str, dict[str, Path]]:
    semantic_classes = [str(value) for value in manifest.get("semanticClasses", [])]
    styled_paths: dict[str, dict[str, Path]] = {"colorset1": {}, "colorset2": {}}

    for case in cases:
        family = str(case["id"])
        source_name = Path(str(case["source"])).name
        source = source_for_case(manifest, case)
        declaration = styler.first_declaration(source)
        detected_family = styler.canonical_family(declaration)
        if detected_family != family:
            findings.append(
                f"{family}: declaration {declaration!r} resolves to {detected_family!r}"
            )
        for label in probe_labels(case):
            if label not in source:
                findings.append(f"{family}: source is missing probe label {label!r}")

        plot_directive_count = case.get("style", {}).get("plotDirectiveCount")
        if plot_directive_count is not None:
            actual_plot_directives = len(
                re.findall(r"(?m)^\s*(?:bar|line)\s+\[", source)
            )
            if actual_plot_directives != int(plot_directive_count):
                findings.append(
                    f"{family}: source has {actual_plot_directives} plot directives; "
                    f"expected {plot_directive_count}"
                )

        if case.get("capacityKind") == "semantic-classes":
            missing_classes = [name for name in semantic_classes if name not in source]
            if missing_classes:
                findings.append(
                    f"{family}: semantic class fixture is missing {missing_classes}"
                )

        for colorset in ("colorset1", "colorset2"):
            theme = styler.theme_variables(colorset, family)
            for key in expected_style_keys(case):
                if key not in theme:
                    findings.append(f"{family}/{colorset}: missing theme variable {key}")

            allowed_colors = {
                str(value).lower()
                for key, value in styler.PALETTES[colorset].items()
                if key != "name" and isinstance(value, str) and COLOR_RE.fullmatch(value)
            }
            unexpected_colors = sorted(set(iter_hex_colors(theme)) - allowed_colors)
            if unexpected_colors:
                findings.append(
                    f"{family}/{colorset}: generated theme uses colors outside the palette: "
                    f"{unexpected_colors}"
                )

            style = case.get("style", {})
            if "sankeyNodeCount" in style:
                node_colors = styler.sankey_node_colors(source, colorset)
                if len(node_colors) != int(style["sankeyNodeCount"]):
                    findings.append(
                        f"{family}/{colorset}: Sankey nodeColors has {len(node_colors)} entries; "
                        f"expected {style['sankeyNodeCount']}"
                    )
            if "xyPalette" in style:
                palette = theme.get("xyChart", {}).get("plotColorPalette", "")
                count = len([item for item in str(palette).split(",") if item.strip()])
                expected = int(style["xyPalette"][colorset])
                if count != expected:
                    findings.append(
                        f"{family}/{colorset}: XY palette has {count} entries; expected {expected}"
                    )

            styled, metadata = styler.style_mermaid_block(source, colorset)
            if metadata.get("family") != family:
                findings.append(
                    f"{family}/{colorset}: styled metadata resolves to "
                    f"{metadata.get('family')!r}"
                )
            if case.get("capacityKind") == "semantic-classes":
                for class_name in semantic_classes:
                    if f"classDef {class_name} " not in styled:
                        findings.append(
                            f"{family}/{colorset}: styled source is missing classDef {class_name}"
                        )
            restyled, _ = styler.style_mermaid_block(styled, colorset)
            if restyled != styled:
                findings.append(f"{family}/{colorset}: styling is not idempotent")

            output_path = work_dir / "styled" / colorset / source_name
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(styled, encoding="utf-8")
            styled_paths[colorset][family] = output_path

    return styled_paths


def render_command() -> list[str]:
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required to render the pinned Mermaid CLI acceptance fixture")
    return [npx, "-y", MERMAID_CLI_PACKAGE]


def approve_svg(path: Path) -> list[str]:
    findings: list[str] = []
    if not path.is_file() or path.stat().st_size < 500:
        return [f"rendered SVG is missing or too small: {path}"]
    text = path.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()
    if "<svg" not in lowered:
        findings.append(f"rendered artifact is not SVG: {path}")
    for marker in ("syntax error", "aria-roledescription=\"error\""):
        if marker in lowered:
            findings.append(f"rendered SVG contains Mermaid error marker {marker!r}: {path}")
    return findings


def validate_render_contract(
    styler,
    case: dict[str, Any],
    contract: dict[str, Any],
    colorset: str,
    source: str,
    svg: str,
    findings: list[str],
) -> None:
    family = str(case["id"])
    for token in contract_tokens(contract):
        if token not in svg:
            findings.append(
                f"{family}/{colorset}: rendered SVG is missing capacity token {token!r}"
            )

    for count_contract in contract.get("counts", []):
        token = str(count_contract["token"])
        expected = int(count_contract["count"])
        actual = svg.count(token)
        if actual != expected:
            findings.append(
                f"{family}/{colorset}: rendered SVG contains {actual} instances of "
                f"{token!r}; expected {expected}"
            )

    theme = styler.theme_variables(colorset, family)
    validate_css_bindings(family, colorset, theme, contract, svg, findings)
    expected_colors: list[str] = []
    for key in contract_style_keys(contract):
        if key not in theme:
            findings.append(
                f"{family}/{colorset}: render contract theme key is missing: {key}"
            )
            continue
        expected_colors.extend(iter_hex_colors(theme[key]))

    if contract.get("sankeyNodeColors") is True:
        expected_colors.extend(styler.sankey_node_colors(source, colorset).values())
    if contract.get("xyPaletteColors") is True:
        palette = str(theme.get("xyChart", {}).get("plotColorPalette", ""))
        expected_colors.extend(
            color.strip() for color in palette.split(",") if color.strip()
        )

    validate_inline_geometry_colors(
        styler, family, colorset, theme, source, svg, findings
    )

    lowered_svg = svg.lower()
    for color in sorted(set(color.lower() for color in expected_colors)):
        if not any(form in lowered_svg for form in rendered_color_forms(color)):
            findings.append(
                f"{family}/{colorset}: configured capacity color {color} is absent "
                "from the rendered SVG"
            )


def locate_batch_svgs(output: Path, expected_count: int) -> list[Path]:
    if expected_count == 1 and output.is_file():
        return [output]
    candidates = [
        output.with_name(f"{output.stem}-{index}.svg")
        for index in range(1, expected_count + 1)
    ]
    if all(path.is_file() for path in candidates):
        return candidates
    sibling_candidates = sorted(output.parent.glob(f"{output.stem}-*.svg"))
    return sibling_candidates


def render_cases(
    styler,
    manifest: dict[str, Any],
    cases: list[dict[str, Any]],
    styled_paths: dict[str, dict[str, Path]],
    work_dir: Path,
    findings: list[str],
    chunk_size: int,
    npm_cache: Path | None,
    render_attempts: int,
) -> dict[str, dict[str, Path]]:
    rendered: dict[str, dict[str, Path]] = {"colorset1": {}, "colorset2": {}}
    command_prefix = render_command()
    environment = os.environ.copy()
    cache_dir = npm_cache or (work_dir / "npm-cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    environment["npm_config_cache"] = str(cache_dir)
    render_contracts = manifest.get("renderContracts", {})

    for colorset in ("colorset1", "colorset2"):
        for chunk_index, start in enumerate(range(0, len(cases), chunk_size), start=1):
            chunk = cases[start : start + chunk_size]
            batch_path = work_dir / "batches" / colorset / f"batch-{chunk_index:02d}.md"
            output_path = work_dir / "rendered" / colorset / f"batch-{chunk_index:02d}.svg"
            batch_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            parts: list[str] = []
            for case in chunk:
                family = str(case["id"])
                source = styled_paths[colorset][family].read_text(encoding="utf-8")
                parts.extend([f"## {family}", "", "```mermaid", source.rstrip(), "```", ""])
            batch_path.write_text("\n".join(parts), encoding="utf-8")
            command = [
                *command_prefix,
                "-i",
                str(batch_path),
                "-o",
                str(output_path),
                "-j",
                "1",
                "-b",
                "white",
            ]
            result: subprocess.CompletedProcess[str] | None = None
            for attempt in range(1, render_attempts + 1):
                if attempt > 1:
                    for stale_output in output_path.parent.glob(
                        f"{output_path.stem}*.svg"
                    ):
                        stale_output.unlink()
                result = subprocess.run(
                    command,
                    cwd=work_dir,
                    env=environment,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    check=False,
                    timeout=300,
                )
                if result.returncode == 0:
                    break
            if result is None:
                raise RuntimeError("render subprocess did not run")
            if result.returncode != 0:
                detail = (result.stderr.strip() or result.stdout.strip())[-3000:]
                findings.append(
                    f"{colorset} batch {chunk_index} failed after {render_attempts} "
                    f"attempts with exit {result.returncode}: {detail}"
                )
            svg_paths = locate_batch_svgs(output_path, len(chunk))
            if len(svg_paths) != len(chunk):
                findings.append(
                    f"{colorset} batch {chunk_index} produced {len(svg_paths)} SVGs; "
                    f"expected {len(chunk)}"
                )
                continue
            for case, svg_path in zip(chunk, svg_paths, strict=True):
                family = str(case["id"])
                findings.extend(f"{family}/{colorset}: {item}" for item in approve_svg(svg_path))
                if svg_path.is_file():
                    raw_svg = svg_path.read_text(encoding="utf-8", errors="replace")
                    svg = html.unescape(raw_svg)
                    normalized_text = normalized_svg_text(svg)
                    for label in rendered_probe_labels(case):
                        normalized_label = " ".join(label.split())
                        if label not in svg and normalized_label not in normalized_text:
                            findings.append(
                                f"{family}/{colorset}: rendered SVG is missing probe label {label!r}"
                            )
                    contract = render_contracts.get(family)
                    if isinstance(contract, dict):
                        validate_render_contract(
                            styler,
                            case,
                            contract,
                            colorset,
                            source_for_case(manifest, case),
                            svg,
                            findings,
                        )
                    if case.get("capacityKind") == "semantic-classes":
                        validate_semantic_class_bindings(
                            styler,
                            family,
                            colorset,
                            [
                                str(value)
                                for value in manifest.get("semanticClasses", [])
                            ],
                            raw_svg,
                            findings,
                        )
                    rendered[colorset][family] = svg_path
    return rendered


def write_report(path: Path | None, report: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate maximum Mermaid palette-element coverage for all public families."
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        required=True,
        help="Fresh output directory for styled copies, batches, rendered SVGs, and npm cache.",
    )
    parser.add_argument("--report", type=Path, help="Write a JSON validation report.")
    parser.add_argument(
        "--npm-cache",
        type=Path,
        help="Reuse an npm cache outside the fresh work directory.",
    )
    parser.add_argument("--skip-render", action="store_true", help="Run static and styling gates only.")
    parser.add_argument("--chunk-size", type=int, default=6, help="Markdown diagrams per CLI render batch.")
    parser.add_argument(
        "--render-attempts",
        type=int,
        default=2,
        help="Attempts per Mermaid CLI batch to absorb transient browser failures.",
    )
    args = parser.parse_args()

    work_dir = args.work_dir.resolve()
    report_path = args.report.resolve() if args.report else None
    if work_dir.exists() and any(work_dir.iterdir()):
        print(f"Work directory must be fresh or empty: {work_dir}", file=sys.stderr)
        return 2
    work_dir.mkdir(parents=True, exist_ok=True)

    findings: list[str] = []
    manifest = load_json(MANIFEST_PATH)
    diagram_types = load_json(DIAGRAM_TYPES_PATH)
    cases = validate_manifest(manifest, diagram_types, findings)
    styler = load_styler()
    styled_paths = validate_sources_and_style(styler, manifest, cases, work_dir, findings)
    rendered: dict[str, dict[str, Path]] = {"colorset1": {}, "colorset2": {}}
    if not args.skip_render:
        try:
            rendered = render_cases(
                styler,
                manifest,
                cases,
                styled_paths,
                work_dir,
                findings,
                max(1, args.chunk_size),
                args.npm_cache.resolve() if args.npm_cache else None,
                max(1, args.render_attempts),
            )
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            findings.append(f"rendering failed: {error}")

    finite_cases = [case for case in cases if case.get("maxSlots") is not None]
    report = {
        "ok": not findings,
        "mermaidVersion": manifest.get("mermaidVersion"),
        "familyCount": len(cases),
        "finiteCapacityCaseCount": len(finite_cases),
        "finiteCapacitySlots": sum(int(case["maxSlots"]) for case in finite_cases),
        "renderContractCount": len(manifest.get("renderContracts", {})),
        "styledDiagramCount": sum(len(paths) for paths in styled_paths.values()),
        "renderedDiagramCount": sum(len(paths) for paths in rendered.values()),
        "renderSkipped": bool(args.skip_render),
        "findings": findings,
    }
    write_report(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
