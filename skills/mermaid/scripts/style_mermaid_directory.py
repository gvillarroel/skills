#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DIAGRAM_TYPES_MANIFEST = SKILL_DIR / "references" / "diagram-types.json"


def load_diagram_types_manifest() -> dict[str, object]:
    data = json.loads(DIAGRAM_TYPES_MANIFEST.read_text(encoding="utf-8"))
    families = data.get("families")
    if not isinstance(families, list) or not families:
        raise RuntimeError("Mermaid diagram type manifest must contain a non-empty families list.")

    family_ids: list[str] = []
    current_declarations: list[str] = []
    accepted_declarations: list[str] = []
    for family in families:
        if not isinstance(family, dict):
            raise RuntimeError("Every Mermaid diagram family manifest entry must be an object.")
        family_id = family.get("id")
        current = family.get("currentDeclarations")
        accepted = family.get("acceptedDeclarations")
        if not isinstance(family_id, str) or not family_id:
            raise RuntimeError("Every Mermaid diagram family must have a non-empty id.")
        if not isinstance(current, list) or not current or not all(isinstance(value, str) and value for value in current):
            raise RuntimeError(f"Mermaid family {family_id} must declare currentDeclarations.")
        if not isinstance(accepted, list) or not accepted or not all(isinstance(value, str) and value for value in accepted):
            raise RuntimeError(f"Mermaid family {family_id} must declare acceptedDeclarations.")
        if not set(current).issubset(accepted):
            raise RuntimeError(f"Mermaid family {family_id} current declarations must be accepted declarations.")
        family_ids.append(family_id)
        current_declarations.extend(current)
        accepted_declarations.extend(accepted)

    for label, values in (
        ("family ids", family_ids),
        ("current declarations", current_declarations),
        ("accepted declarations", accepted_declarations),
    ):
        duplicates = sorted({value for value in values if values.count(value) > 1})
        if duplicates:
            raise RuntimeError(f"Duplicate Mermaid {label} in manifest: {', '.join(duplicates)}")
    return data


DIAGRAM_TYPE_CATALOG = load_diagram_types_manifest()
DIAGRAM_FAMILIES = DIAGRAM_TYPE_CATALOG["families"]
OFFICIAL_FAMILIES = [family["id"] for family in DIAGRAM_FAMILIES]
OFFICIAL_DECLARATIONS = [
    declaration
    for family in DIAGRAM_FAMILIES
    for declaration in family["currentDeclarations"]
]
SUPPORTED_DECLARATIONS = [
    declaration
    for family in DIAGRAM_FAMILIES
    for declaration in family["acceptedDeclarations"]
]
DECLARATION_TO_FAMILY = {
    declaration.lower(): family["id"]
    for family in DIAGRAM_FAMILIES
    for declaration in family["acceptedDeclarations"]
}
CLASSDEF_FAMILIES = {
    family["id"]
    for family in DIAGRAM_FAMILIES
    if family.get("classDef") is True
}
MERMAID_VERSION = DIAGRAM_TYPE_CATALOG["upstream"]["version"]


LEGACY_COLORSET_DIRECTIVE_RE = re.compile(
    r"^\s*%%\{init:\s*\{.*?\"(?:mermaid-colorset-styler|mermaid)\".*?\}\}%%\s*$"
)
FENCE_RE = re.compile(r"(?P<open>^[ \t]*```[ \t]*mermaid[^\n]*\n)(?P<body>.*?)(?P<close>^[ \t]*```[ \t]*$)", re.MULTILINE | re.DOTALL)
CLASS_DEF_RE = re.compile(r"^\s*classDef\s+(?P<classes>[A-Za-z0-9_, -]+)\s+.*$", re.MULTILINE)
TRIPLE_CLASS_RE = re.compile(r":::\s*(?P<classes>[A-Za-z0-9_ -]+)")
CLASS_LINE_RE = re.compile(r"^\s*class\s+[^;\n]+?\s+(?P<classes>[A-Za-z0-9_ -]+)\s*;?\s*$", re.MULTILINE)
CLASS_MULTI_ASSIGNMENT_RE = re.compile(
    r"^(?P<indent>\s*)class\s+"
    r"(?P<targets>[A-Za-z_][A-Za-z0-9_.-]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_.-]*)+)\s+"
    r"(?P<classes>[A-Za-z0-9_ -]+)\s*;?\s*$",
    re.MULTILINE,
)
CSS_CLASS_LINE_RE = re.compile(r"^\s*cssClass\s+\"[^\"]+\"\s+(?P<classes>[A-Za-z0-9_ -]+)\s*;?\s*$", re.MULTILINE)
QUADRANT_AXIS_RE = re.compile(
    r"^(?P<indent>\s*)(?P<axis>[xy]-axis)\s+(?P<left>.+?)\s*-->\s*(?P<right>.+?)\s*$"
)
XY_AXIS_LINE_RE = re.compile(r"^(?P<indent>\s*)x-axis\s*\[(?P<items>.*)\]\s*$", re.IGNORECASE | re.MULTILINE)
XY_SERIES_LINE_RE = re.compile(r"^\s*(?:bar|line)\s*\[(?P<values>[^\]]+)\]\s*$", re.IGNORECASE | re.MULTILINE)
XY_VALUE_SUFFIX_RES = (
    re.compile(r"^(?P<label>.+?)\s*(?:=|:)\s*(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(?:%|[A-Za-z][A-Za-z0-9_./-]*)?\s*$"),
    re.compile(r"^(?P<label>.+?)\s*\(\s*(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(?:%|[A-Za-z][A-Za-z0-9_./-]*)?\s*\)\s*$"),
)
TOP_LEVEL_YAML_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:")

CONFIG_BEGIN = "# mermaid: config begin"
CONFIG_END = "# mermaid: config end"
METADATA_BEGIN = "# mermaid: metadata begin"
METADATA_END = "# mermaid: metadata end"
LEGACY_CONFIG_BEGIN = "# mermaid-colorset-styler: config begin"
LEGACY_CONFIG_END = "# mermaid-colorset-styler: config end"
LEGACY_METADATA_BEGIN = "# mermaid-colorset-styler: metadata begin"
LEGACY_METADATA_END = "# mermaid-colorset-styler: metadata end"
GENERATED_BEGIN_MARKERS = {
    CONFIG_BEGIN,
    METADATA_BEGIN,
    LEGACY_CONFIG_BEGIN,
    LEGACY_METADATA_BEGIN,
}
GENERATED_END_MARKERS = {
    CONFIG_END,
    METADATA_END,
    LEGACY_CONFIG_END,
    LEGACY_METADATA_END,
}

COLOR_CLASS_ORDER = [
    "csPrimary",
    "csAccent",
    "csMuted",
    "csCritical",
    "csWarning",
    "csSuccess",
    "csInfo",
    "csSpecial",
    "csNeutral",
]
COLOR_CLASSES = set(COLOR_CLASS_ORDER)
SEMANTIC_CLASS_NAMES = "|".join(re.escape(class_name) for class_name in COLOR_CLASS_ORDER)
SEMANTIC_TRIPLE_CLASS_RE = re.compile(
    rf":::[ \t]*(?:{SEMANTIC_CLASS_NAMES})(?:[ \t,]+(?:{SEMANTIC_CLASS_NAMES}))*"
)
SANKEY_FUNCTIONAL_CONFIG_KEYS = {
    "height",
    "labelStyle",
    "nodeAlignment",
    "nodePadding",
    "nodeWidth",
    "prefix",
    "showValues",
    "suffix",
    "useMaxWidth",
    "width",
}
TREEMAP_FUNCTIONAL_CONFIG_KEYS = {
    "borderWidth",
    "labelFontSize",
    "showValues",
    "valueFontSize",
    "valueFormat",
}
FAMILY_FUNCTIONAL_CONFIG_KEYS = {
    "sankey": SANKEY_FUNCTIONAL_CONFIG_KEYS,
    "treemap": TREEMAP_FUNCTIONAL_CONFIG_KEYS,
}

SEMANTIC_CAPACITY_LAYOUTS: dict[str, tuple[str, dict[str, int]]] = {
    "erDiagram": (
        "er",
        {
            "minEntityWidth": 180,
            "rankSpacing": 20,
        },
    ),
    "swimlane": (
        "flowchart",
        {
            "nodeSpacing": 10,
            "rankSpacing": 20,
        },
    ),
}

CORE_THEME_KEYS = [
    "background",
    "primaryColor",
    "primaryTextColor",
    "primaryBorderColor",
    "secondaryColor",
    "secondaryTextColor",
    "secondaryBorderColor",
    "tertiaryColor",
    "tertiaryTextColor",
    "tertiaryBorderColor",
    "lineColor",
    "textColor",
    "mainBkg",
    "nodeBkg",
    "nodeBorder",
    "clusterBkg",
    "clusterBorder",
    "defaultLinkColor",
    "edgeLabelBackground",
    "labelColor",
    "titleColor",
]

THEME_COLOR_LIMIT = 12
GIT_COLOR_LIMIT = 8
FILL_TYPE_LIMIT = 8
VENN_COLOR_LIMIT = 8

SERIES_THEME_KEYS = [f"cScale{index}" for index in range(THEME_COLOR_LIMIT)]
SERIES_LABEL_THEME_KEYS = [
    f"cScaleLabel{index}" for index in range(THEME_COLOR_LIMIT)
]
SERIES_INVERSE_THEME_KEYS = [
    f"cScaleInv{index}" for index in range(THEME_COLOR_LIMIT)
]
SERIES_PEER_THEME_KEYS = [
    f"cScalePeer{index}" for index in range(THEME_COLOR_LIMIT)
]
GIT_THEME_KEYS = [f"git{index}" for index in range(GIT_COLOR_LIMIT)]
GIT_INVERSE_THEME_KEYS = [f"gitInv{index}" for index in range(GIT_COLOR_LIMIT)]
GIT_BRANCH_LABEL_THEME_KEYS = [
    f"gitBranchLabel{index}" for index in range(GIT_COLOR_LIMIT)
]
FILL_TYPE_THEME_KEYS = [f"fillType{index}" for index in range(FILL_TYPE_LIMIT)]
VENN_THEME_KEYS = [f"venn{index}" for index in range(1, VENN_COLOR_LIMIT + 1)]

FAMILY_THEME_KEYS = {
    "sequenceDiagram": [
        "noteBkgColor",
        "noteTextColor",
        "noteBorderColor",
        "actorBkg",
        "actorBorder",
        "actorTextColor",
        "actorLineColor",
        "signalColor",
        "signalTextColor",
        "activationBorderColor",
        "activationBkgColor",
    ],
    "classDiagram": ["classText"],
    "requirementDiagram": ["classText"],
    "stateDiagram": [
        "classText",
        "transitionColor",
        "stateLabelColor",
        "stateBkg",
        "labelBackgroundColor",
        "compositeBackground",
        "altBackground",
        "compositeTitleBackground",
        "compositeBorder",
    ],
    "flowchart": ["classText"],
    "swimlane": ["classText"],
    "treemap": [
        "classText",
        "THEME_COLOR_LIMIT",
        *SERIES_THEME_KEYS,
        *SERIES_LABEL_THEME_KEYS,
        *SERIES_INVERSE_THEME_KEYS,
        *SERIES_PEER_THEME_KEYS,
    ],
    "gitGraph": [
        "commitLabelColor",
        "commitLabelBackground",
        "tagLabelColor",
        "tagLabelBackground",
        *GIT_THEME_KEYS,
        *GIT_INVERSE_THEME_KEYS,
        *GIT_BRANCH_LABEL_THEME_KEYS,
    ],
    "journey": [*FILL_TYPE_THEME_KEYS],
    "gantt": [
        "sectionBkgColor",
        "altSectionBkgColor",
        "sectionBkgColor2",
        "taskBkgColor",
        "taskBorderColor",
        "taskTextColor",
        "taskTextDarkColor",
        "taskTextLightColor",
        "taskTextOutsideColor",
        "activeTaskBkgColor",
        "activeTaskBorderColor",
        "doneTaskBkgColor",
        "doneTaskBorderColor",
        "critBkgColor",
        "critBorderColor",
        "excludeBkgColor",
        "gridColor",
        "todayLineColor",
    ],
    "pie": [
        "pie1",
        "pie2",
        "pie3",
        "pie4",
        "pie5",
        "pie6",
        "pie7",
        "pie8",
        "pie9",
        "pie10",
        "pie11",
        "pie12",
        "pieTitleTextColor",
        "pieLegendTextColor",
        "pieSectionTextColor",
        "pieStrokeColor",
    ],
    "quadrantChart": [
        "quadrant1Fill",
        "quadrant2Fill",
        "quadrant3Fill",
        "quadrant4Fill",
        "quadrant1TextFill",
        "quadrant2TextFill",
        "quadrant3TextFill",
        "quadrant4TextFill",
        "quadrantPointFill",
        "quadrantPointTextFill",
        "quadrantXAxisTextFill",
        "quadrantYAxisTextFill",
        "quadrantInternalBorderStrokeFill",
        "quadrantExternalBorderStrokeFill",
        "quadrantTitleFill",
    ],
    "mindmap": [
        "THEME_COLOR_LIMIT",
        "git0",
        "gitBranchLabel0",
        *SERIES_THEME_KEYS,
        *SERIES_LABEL_THEME_KEYS,
        *SERIES_INVERSE_THEME_KEYS,
    ],
    "timeline": [
        "THEME_COLOR_LIMIT",
        *SERIES_THEME_KEYS,
        *SERIES_LABEL_THEME_KEYS,
        *SERIES_INVERSE_THEME_KEYS,
    ],
    "kanban": [
        "THEME_COLOR_LIMIT",
        *SERIES_THEME_KEYS,
        *SERIES_LABEL_THEME_KEYS,
        *SERIES_INVERSE_THEME_KEYS,
    ],
    "architecture": [
        "archEdgeColor",
        "archEdgeArrowColor",
        "archEdgeWidth",
        "archGroupBorderColor",
        "archGroupBorderWidth",
    ],
    "sankey": [],
    "xyChart": ["xyChart"],
    "radar": ["THEME_COLOR_LIMIT", *SERIES_THEME_KEYS, "radar"],
    "eventmodeling": [
        "emUiFill",
        "emUiStroke",
        "emProcessorFill",
        "emProcessorStroke",
        "emReadModelFill",
        "emReadModelStroke",
        "emCommandFill",
        "emCommandStroke",
        "emEventFill",
        "emEventStroke",
        "emArrowhead",
        "emRelationStroke",
    ],
    "venn": [*VENN_THEME_KEYS, "vennTitleTextColor", "vennSetTextColor"],
    "wardley": ["wardleyEvolutionColor", "wardley"],
    "cynefin": ["cynefin"],
}

PALETTES = {
    "colorset1": {
        "name": "basic-red-neutral-style",
        "background": "#ffffff",
        "page": "#f7f7f7",
        "surface": "#ffffff",
        "ink": "#333e48",
        "muted": "#696969",
        "primary": "#9e1b32",
        "primary_dark": "#6d1222",
        "primary_light": "#ffccd5",
        "critical": "#e8002a",
        "accent": "#4f4f4f",
        "accent_light": "#e7e7e7",
        "warning": "#828282",
        "warning_light": "#e7e7e7",
        "success": "#333e48",
        "success_light": "#cfcfcf",
        "info": "#9e1b32",
        "info_light": "#ffccd5",
        "special": "#696969",
        "special_light": "#e7e7e7",
        "neutral": "#333e48",
        "neutral_light": "#e7e7e7",
        "gray100": "#e7e7e7",
        "gray200": "#cfcfcf",
        "gray300": "#b5b5b5",
        "gray400": "#9c9c9c",
        "gray500": "#828282",
        "gray600": "#696969",
        "gray700": "#4f4f4f",
        "gray800": "#363636",
        "gray900": "#1c1c1c",
    },
    "colorset2": {
        "name": "full-color-style",
        "background": "#ffffff",
        "page": "#f7f7f7",
        "surface": "#ffffff",
        "ink": "#333e48",
        "muted": "#696969",
        "primary": "#9e1b32",
        "primary_dark": "#6d1222",
        "primary_light": "#ffccd5",
        "critical": "#e8002a",
        "accent": "#007298",
        "accent_light": "#cdf3ff",
        "warning": "#e77204",
        "warning_light": "#ffe5cc",
        "success": "#45842a",
        "success_light": "#dbffcc",
        "info": "#00ace6",
        "info_light": "#cdf3ff",
        "special": "#652f6c",
        "special_light": "#f9ccff",
        "neutral": "#333e48",
        "neutral_light": "#e7e7e7",
        "gray100": "#e7e7e7",
        "gray200": "#cfcfcf",
        "gray300": "#b5b5b5",
        "gray400": "#9c9c9c",
        "gray500": "#828282",
        "gray600": "#696969",
        "gray700": "#4f4f4f",
        "gray800": "#363636",
        "gray900": "#1c1c1c",
    },
}


@dataclass
class DiagramResult:
    file: str
    block_index: int
    diagram_type: str
    family: str
    changed: bool
    has_style: bool
    referenced_classes: list[str]
    inserted_class_defs: list[str]
    skipped_class_defs: list[str]


def relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    high, low = sorted(
        (relative_luminance(first), relative_luminance(second)), reverse=True
    )
    return (high + 0.05) / (low + 0.05)


def readable_text_color(fill: str, palette: dict[str, str]) -> str:
    candidates = (palette["surface"], palette["ink"], palette["gray900"])
    return max(candidates, key=lambda candidate: contrast_ratio(fill, candidate))


def series_colors(palette: dict[str, str], extended: bool) -> list[str]:
    roles = (
        (
            "primary",
            "accent",
            "warning",
            "success",
            "special",
            "info",
            "critical",
            "primary_dark",
            "gray700",
            "gray500",
            "gray900",
            "gray400",
        )
        if extended
        else (
            "primary",
            "gray700",
            "gray500",
            "ink",
            "gray600",
            "critical",
            "primary_dark",
            "gray800",
            "gray400",
            "gray900",
            "gray300",
            "primary_light",
        )
    )
    return [palette[role] for role in roles]


def theme_variables(colorset: str, family: str | None = None) -> dict[str, object]:
    p = PALETTES[colorset]
    extended = colorset == "colorset2"
    scale_colors = series_colors(p, extended)
    scale_labels = [readable_text_color(color, p) for color in scale_colors]
    fill_type_roles = (
        (
            "primary_light",
            "accent_light",
            "warning_light",
            "success_light",
            "special_light",
            "neutral_light",
            "gray200",
            "gray300",
        )
        if extended
        else (
            "primary_light",
            "gray100",
            "gray200",
            "gray300",
            "gray400",
            "gray500",
            "gray600",
            "gray700",
        )
    )
    fill_type_colors = [p[role] for role in fill_type_roles]
    variables = {
        "THEME_COLOR_LIMIT": THEME_COLOR_LIMIT,
        "background": p["background"],
        "primaryColor": p["primary_light"],
        "primaryTextColor": p["ink"],
        "primaryBorderColor": p["primary"],
        "secondaryColor": p["accent_light"],
        "secondaryTextColor": p["ink"],
        "secondaryBorderColor": p["accent"],
        "tertiaryColor": p["neutral_light"],
        "tertiaryTextColor": p["ink"],
        "tertiaryBorderColor": p["gray400"],
        "lineColor": p["muted"],
        "textColor": p["ink"],
        "mainBkg": p["accent_light"] if extended else p["primary_light"],
        "nodeBkg": p["accent_light"] if extended else p["primary_light"],
        "nodeBorder": p["primary"],
        "clusterBkg": p["gray100"],
        "clusterBorder": p["gray400"],
        "defaultLinkColor": p["muted"],
        "edgeLabelBackground": p["surface"],
        "noteBkgColor": p["success_light"] if extended else p["neutral_light"],
        "noteTextColor": p["ink"],
        "noteBorderColor": p["success"] if extended else p["gray400"],
        "actorBkg": p["accent_light"] if extended else p["primary_light"],
        "actorBorder": p["accent"] if extended else p["primary"],
        "actorTextColor": p["ink"],
        "actorLineColor": p["accent"] if extended else p["primary"],
        "signalColor": p["primary"] if extended else p["muted"],
        "signalTextColor": p["ink"],
        "activationBorderColor": p["warning"] if extended else p["primary"],
        "activationBkgColor": p["warning_light"] if extended else p["primary_light"],
        "classText": p["ink"],
        "transitionColor": p["muted"],
        "stateLabelColor": p["ink"],
        "stateBkg": p["accent_light"] if extended else p["primary_light"],
        "labelBackgroundColor": p["accent_light"] if extended else p["primary_light"],
        "compositeBackground": p["accent_light"] if extended else p["neutral_light"],
        "altBackground": p["warning_light"] if extended else p["gray200"],
        "compositeTitleBackground": p["accent_light"] if extended else p["primary_light"],
        "compositeBorder": p["accent"] if extended else p["primary"],
        "labelColor": p["ink"],
        "titleColor": p["ink"],
        "commitLabelColor": p["ink"],
        "commitLabelBackground": p["surface"],
        "tagLabelColor": p["ink"],
        "tagLabelBackground": p["neutral_light"],
        **{
            f"git{index}": color
            for index, color in enumerate(scale_colors[:GIT_COLOR_LIMIT])
        },
        **{
            f"gitInv{index}": scale_labels[index]
            for index in range(GIT_COLOR_LIMIT)
        },
        **{
            f"gitBranchLabel{index}": scale_labels[index]
            for index in range(GIT_COLOR_LIMIT)
        },
        "sectionBkgColor": p["accent_light"] if extended else p["gray100"],
        "altSectionBkgColor": p["warning_light"] if extended else p["gray200"],
        "sectionBkgColor2": p["success_light"] if extended else p["gray100"],
        "taskBkgColor": p["accent"] if extended else p["primary_light"],
        "taskBorderColor": p["accent"] if extended else p["primary"],
        "taskTextColor": p["surface"] if extended else p["ink"],
        "taskTextDarkColor": p["ink"],
        "taskTextLightColor": p["surface"],
        "taskTextOutsideColor": p["ink"],
        "activeTaskBkgColor": p["warning"] if extended else p["primary_light"],
        "activeTaskBorderColor": p["warning"] if extended else p["primary"],
        "doneTaskBkgColor": p["success"] if extended else p["gray300"],
        "doneTaskBorderColor": p["success"] if extended else p["gray600"],
        "critBkgColor": p["primary"],
        "critBorderColor": p["critical"],
        "excludeBkgColor": p["gray100"],
        "gridColor": p["gray400"],
        "todayLineColor": p["critical"],
        **{
            f"pie{index + 1}": color for index, color in enumerate(scale_colors)
        },
        "pieTitleTextColor": p["ink"],
        "pieLegendTextColor": p["ink"],
        "pieSectionTextColor": p["surface"],
        "pieStrokeColor": p["surface"],
        **{
            f"fillType{index}": color
            for index, color in enumerate(fill_type_colors)
        },
        **{
            f"cScale{index}": color for index, color in enumerate(scale_colors)
        },
        **{
            f"cScaleLabel{index}": color
            for index, color in enumerate(scale_labels)
        },
        **{
            f"cScaleInv{index}": color
            for index, color in enumerate(scale_labels)
        },
        **{
            f"cScalePeer{index}": color
            for index, color in enumerate(scale_colors)
        },
        "quadrant1Fill": p["success_light"] if extended else p["primary_light"],
        "quadrant2Fill": p["accent_light"] if extended else p["neutral_light"],
        "quadrant3Fill": p["special_light"] if extended else p["gray200"],
        "quadrant4Fill": p["warning_light"] if extended else p["gray100"],
        "quadrant1TextFill": p["ink"],
        "quadrant2TextFill": p["ink"],
        "quadrant3TextFill": p["ink"],
        "quadrant4TextFill": p["ink"],
        "quadrantPointFill": p["accent"] if extended else p["primary"],
        "quadrantPointTextFill": p["ink"],
        "quadrantXAxisTextFill": p["ink"],
        "quadrantYAxisTextFill": p["ink"],
        "quadrantInternalBorderStrokeFill": p["muted"],
        "quadrantExternalBorderStrokeFill": p["accent"] if extended else p["primary"],
        "quadrantTitleFill": p["ink"],
        **{
            f"venn{index + 1}": color
            for index, color in enumerate(scale_colors[:VENN_COLOR_LIMIT])
        },
        "vennTitleTextColor": p["ink"],
        "vennSetTextColor": p["ink"],
        "archEdgeColor": p["muted"],
        "archEdgeArrowColor": p["muted"],
        "archEdgeWidth": "3",
        "archGroupBorderColor": p["primary"],
        "archGroupBorderWidth": "2px",
        "emUiFill": p["surface"],
        "emUiStroke": p["gray400"],
        "emProcessorFill": p["special_light"],
        "emProcessorStroke": p["special"],
        "emReadModelFill": p["success_light"],
        "emReadModelStroke": p["success"],
        "emCommandFill": p["accent_light"],
        "emCommandStroke": p["accent"],
        "emEventFill": p["warning_light"],
        "emEventStroke": p["warning"],
        "emArrowhead": p["primary"],
        "emRelationStroke": p["muted"],
        "wardleyEvolutionColor": p["critical"],
        "wardley": {
            "backgroundColor": p["background"],
            "axisColor": p["muted"],
            "axisTextColor": p["ink"],
            "gridColor": p["gray400"],
            "componentFill": p["surface"],
            "componentStroke": p["primary"],
            "componentLabelColor": p["ink"],
            "linkStroke": p["muted"],
            "evolutionStroke": p["critical"],
            "annotationStroke": p["accent"] if extended else p["gray600"],
            "annotationTextColor": p["ink"],
            "annotationFill": p["neutral_light"],
        },
        "xyChart": {
            "backgroundColor": p["surface"],
            "titleColor": p["ink"],
            "xAxisLabelColor": p["ink"],
            "xAxisTitleColor": p["ink"],
            "xAxisTickColor": p["muted"],
            "xAxisLineColor": p["muted"],
            "yAxisLabelColor": p["ink"],
            "yAxisTitleColor": p["ink"],
            "yAxisTickColor": p["muted"],
            "yAxisLineColor": p["muted"],
            "plotColorPalette": ", ".join(
                [p[role] for role in ("accent", "warning", "success", "special", "info", "primary")]
                if extended
                else [p[role] for role in ("primary", "accent", "warning", "success", "special")]
            ),
        },
        "radar": {
            "axisColor": p["ink"],
            "axisLabelColor": p["ink"],
            "graticuleColor": p["gray500"],
            "legendBoxBorderColor": p["gray400"],
            "legendBoxBackgroundColor": p["surface"],
        },
        "cynefin": {
            "complexBg": p["accent_light"],
            "complicatedBg": p["neutral_light"],
            "clearBg": p["success_light"],
            "chaoticBg": p["primary_light"],
            "confusionBg": p["warning_light"],
            "boundaryColor": p["muted"],
            "cliffColor": p["critical"],
            "arrowColor": p["primary"],
            "labelColor": p["ink"],
            "textColor": p["ink"],
        },
    }
    keys = set(CORE_THEME_KEYS)
    keys.update(FAMILY_THEME_KEYS.get(family or "", []))
    return {key: variables[key] for key in variables if key in keys}


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return "null"
    return json.dumps(str(value))


def yaml_key(value: object) -> str:
    text = str(value)
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", text):
        return text
    return json.dumps(text)


def yaml_mapping_lines(mapping: dict[str, object], indent: int = 0) -> list[str]:
    lines: list[str] = []
    prefix = " " * indent
    for key, value in mapping.items():
        rendered_key = yaml_key(key)
        if isinstance(value, dict):
            lines.append(f"{prefix}{rendered_key}:")
            lines.extend(yaml_mapping_lines(value, indent + 2))
        else:
            lines.append(f"{prefix}{rendered_key}: {yaml_scalar(value)}")
    return lines


def class_style(colorset: str, class_name: str) -> str:
    p = PALETTES[colorset]
    styles = {
        "csPrimary": (p["primary_light"], p["primary"], p["ink"]),
        "csAccent": (p["accent_light"], p["accent"], p["ink"]),
        "csMuted": (p["gray100"], p["gray500"], p["ink"]),
        "csCritical": (p["primary_light"], p["critical"], p["ink"]),
        "csWarning": (p["warning_light"], p["warning"], p["ink"]),
        "csSuccess": (p["success_light"], p["success"], p["ink"]),
        "csInfo": (p["info_light"], p["info"], p["ink"]),
        "csSpecial": (p["special_light"], p["special"], p["ink"]),
        "csNeutral": (p["neutral_light"], p["neutral"], p["ink"]),
    }
    fill, stroke, text = styles[class_name]
    return f"classDef {class_name} fill:{fill},stroke:{stroke},color:{text},stroke-width:2px;"


def sankey_node_colors(source: str, colorset: str) -> dict[str, str]:
    nodes: list[str] = []
    declaration_seen = False
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%%"):
            continue
        if not declaration_seen:
            declaration_seen = line.split()[0].rstrip(":").lower() in {"sankey", "sankey-beta"}
            continue
        try:
            row = next(csv.reader([raw_line]))
        except (csv.Error, StopIteration):
            continue
        if len(row) != 3:
            continue
        for node in (row[0].strip(), row[1].strip()):
            if node and node not in nodes:
                nodes.append(node)

    p = PALETTES[colorset]
    if colorset == "colorset2":
        palette = [p["primary"], p["accent"], p["warning"], p["success"], p["special"], p["info"], p["gray500"], p["critical"]]
    else:
        palette = [p["primary"], p["gray700"], p["gray500"], p["gray300"], p["primary_dark"], p["gray600"], p["gray400"], p["gray800"]]
    return {node: palette[index % len(palette)] for index, node in enumerate(nodes)}


def colorset_config(
    colorset: str,
    family: str | None = None,
    source: str = "",
    functional_options: dict[str, object] | None = None,
    existing_config_keys: set[str] | None = None,
) -> dict[str, object]:
    config: dict[str, object] = {
        "theme": "base",
        "themeVariables": theme_variables(colorset, family),
    }
    layout = SEMANTIC_CAPACITY_LAYOUTS.get(family or "")
    if layout and set(referenced_color_classes(source)) == COLOR_CLASSES:
        config_key, defaults = layout
        if config_key not in (existing_config_keys or set()):
            config[config_key] = dict(defaults)
    if family == "sankey":
        config["sankey"] = {
            **(functional_options or {}),
            "linkColor": "gradient",
            "nodeColors": sankey_node_colors(source, colorset),
        }
    elif family == "treemap":
        config["themeCSS"] = (
            ".treemapLeaf { fill-opacity: 0.5 !important; stroke-width: 6px !important; }"
        )
        config["treemap"] = {
            **(functional_options or {}),
            "useMaxWidth": False,
            "padding": 4,
            "diagramPadding": 8,
            "nodeWidth": 200,
            "nodeHeight": 65,
        }
    return config


def colorset_metadata(colorset: str) -> dict[str, object]:
    return {
        "mermaid": {
            "colorset": colorset,
            "mode": "standard" if colorset == "colorset1" else "extended",
            "palette": PALETTES[colorset]["name"],
        }
    }


def generated_config_lines(
    colorset: str,
    family: str | None = None,
    indent: int = 0,
    source: str = "",
    functional_options: dict[str, object] | None = None,
    existing_config_keys: set[str] | None = None,
) -> list[str]:
    prefix = " " * indent
    return [f"{prefix}{CONFIG_BEGIN}"] + yaml_mapping_lines(
        colorset_config(
            colorset,
            family,
            source,
            functional_options,
            existing_config_keys,
        ),
        indent,
    ) + [f"{prefix}{CONFIG_END}"]


def generated_metadata_lines(colorset: str, indent: int = 0) -> list[str]:
    prefix = " " * indent
    return [f"{prefix}{METADATA_BEGIN}"] + yaml_mapping_lines(colorset_metadata(colorset), indent) + [f"{prefix}{METADATA_END}"]


def colorset_frontmatter(
    colorset: str,
    family: str | None = None,
    source: str = "",
    functional_options: dict[str, object] | None = None,
) -> str:
    lines = ["---"]
    lines.extend([CONFIG_BEGIN, "config:"])
    lines.extend(
        yaml_mapping_lines(
            colorset_config(colorset, family, source, functional_options), 2
        )
    )
    lines.append(CONFIG_END)
    lines.extend(generated_metadata_lines(colorset))
    lines.append("---")
    return "\n".join(lines) + "\n"


def colorset_directive(colorset: str, family: str | None = None) -> str:
    return colorset_frontmatter(colorset, family)


def split_frontmatter(source: str) -> tuple[str, str]:
    lines = source.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "", source
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "".join(lines[: index + 1]), "".join(lines[index + 1 :])
    return "", source


def strip_generated_frontmatter(frontmatter: str) -> str:
    if not frontmatter:
        return ""
    lines = frontmatter.splitlines()
    if len(lines) < 2 or lines[0].strip() != "---" or lines[-1].strip() != "---":
        return frontmatter
    body = lines[1:-1]
    kept: list[str] = []
    skipping = False
    for line in body:
        marker = line.strip()
        if marker in GENERATED_BEGIN_MARKERS:
            skipping = True
            continue
        if skipping:
            if marker in GENERATED_END_MARKERS:
                skipping = False
            continue
        kept.append(line)
    while kept and not kept[0].strip():
        kept.pop(0)
    while kept and not kept[-1].strip():
        kept.pop()
    if not kept:
        return ""
    return "---\n" + "\n".join(kept) + "\n---\n"


def remove_generated_directives(body: str) -> str:
    return "\n".join(
        line for line in body.splitlines() if not LEGACY_COLORSET_DIRECTIVE_RE.match(line)
    ) + ("\n" if body.endswith("\n") else "")


def remove_generated_styling(source: str) -> str:
    frontmatter, rest = split_frontmatter(source)
    return strip_generated_frontmatter(frontmatter) + remove_generated_directives(rest)


def leading_spaces(value: str) -> int:
    return len(value) - len(value.lstrip(" "))


def is_top_level_key(line: str) -> bool:
    return bool(line.strip()) and not line.startswith((" ", "\t")) and not line.lstrip().startswith("#") and bool(TOP_LEVEL_YAML_KEY_RE.match(line))


def find_top_level_key(lines: list[str], key: str) -> int | None:
    pattern = re.compile(rf"^{re.escape(key)}\s*:")
    for index, line in enumerate(lines):
        if is_top_level_key(line) and pattern.match(line):
            return index
    return None


def find_mapping_end(lines: list[str], start: int) -> int:
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if is_top_level_key(line):
            return index
    return len(lines)


def child_indent(lines: list[str], start: int, end: int) -> int:
    indents = [
        leading_spaces(line)
        for line in lines[start + 1 : end]
        if line.strip() and not line.lstrip().startswith("#") and leading_spaces(line) > leading_spaces(lines[start])
    ]
    return min(indents) if indents else leading_spaces(lines[start]) + 2


def existing_config_child_keys(frontmatter: str) -> set[str]:
    if not frontmatter:
        return set()
    lines = frontmatter.splitlines()[1:-1]
    config_index = find_top_level_key(lines, "config")
    if config_index is None:
        return set()
    end = find_mapping_end(lines, config_index)
    indent = child_indent(lines, config_index, end)
    keys: set[str] = set()
    for line in lines[config_index + 1 : end]:
        if leading_spaces(line) != indent or line.lstrip().startswith("#"):
            continue
        match = re.match(r"(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s*:", line.strip())
        if match:
            keys.add(match.group("key"))
    return keys


def parse_simple_yaml_scalar(value: str) -> object:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    lowered = value.casefold()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?", value):
        return float(value)
    return value


def extract_family_options(frontmatter: str, family: str | None) -> dict[str, object]:
    allowed_keys = FAMILY_FUNCTIONAL_CONFIG_KEYS.get(family or "")
    if not allowed_keys:
        return {}
    options: dict[str, object] = {}
    lines = frontmatter.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(rf"^(?P<indent>\s*){re.escape(family or '')}\s*:\s*(?:#.*)?$", line)
        if not match:
            index += 1
            continue
        parent_indent = len(match.group("indent"))
        index += 1
        child_indent: int | None = None
        while index < len(lines):
            candidate = lines[index]
            stripped = candidate.strip()
            candidate_indent = leading_spaces(candidate)
            if stripped and not candidate.lstrip().startswith("#") and candidate_indent <= parent_indent:
                break
            if not stripped or candidate.lstrip().startswith("#"):
                index += 1
                continue
            if child_indent is None:
                child_indent = candidate_indent
            if candidate_indent == child_indent:
                option_match = re.match(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(?P<value>.+?)\s*$", stripped)
                if option_match and option_match.group("key") in allowed_keys:
                    options[option_match.group("key")] = parse_simple_yaml_scalar(option_match.group("value"))
            index += 1
    return options


def remove_config_style_keys(
    lines: list[str], start: int, end: int, indent: int, family: str | None = None
) -> list[str]:
    cleaned: list[str] = []
    index = start + 1
    while index < end:
        line = lines[index]
        stripped = line.strip()
        if leading_spaces(line) == indent and re.match(r"theme\s*:", stripped):
            index += 1
            continue
        if leading_spaces(line) == indent and re.match(r"themeVariables\s*:", stripped):
            index += 1
            while index < end:
                candidate = lines[index]
                if candidate.strip() and not candidate.lstrip().startswith("#") and leading_spaces(candidate) <= indent:
                    break
                index += 1
            continue
        if family in FAMILY_FUNCTIONAL_CONFIG_KEYS and leading_spaces(line) == indent and re.match(
            rf"{re.escape(family)}\s*:", stripped
        ):
            index += 1
            while index < end:
                candidate = lines[index]
                if candidate.strip() and not candidate.lstrip().startswith("#") and leading_spaces(candidate) <= indent:
                    break
                index += 1
            continue
        cleaned.append(line)
        index += 1
    return cleaned


def inject_colorset_frontmatter(
    frontmatter: str,
    colorset: str,
    family: str | None = None,
    source: str = "",
    functional_options: dict[str, object] | None = None,
) -> str:
    clean_frontmatter = strip_generated_frontmatter(frontmatter)
    if not clean_frontmatter:
        return colorset_frontmatter(colorset, family, source, functional_options)

    existing_config_keys = existing_config_child_keys(clean_frontmatter)

    lines = clean_frontmatter.splitlines()
    body = lines[1:-1]
    config_index = find_top_level_key(body, "config")
    if config_index is None:
        if body and body[-1].strip():
            body.append("")
        body.extend([CONFIG_BEGIN, "config:"])
        body.extend(
            yaml_mapping_lines(
                colorset_config(
                    colorset,
                    family,
                    source,
                    functional_options,
                    existing_config_keys,
                ),
                2,
            )
        )
        body.append(CONFIG_END)
    else:
        end = find_mapping_end(body, config_index)
        indent = child_indent(body, config_index, end)
        cleaned_config = remove_config_style_keys(body, config_index, end, indent, family)
        body = body[: config_index + 1] + cleaned_config + generated_config_lines(
            colorset,
            family,
            indent,
            source,
            functional_options,
            existing_config_keys,
        ) + body[end:]

    if body and body[-1].strip():
        body.append("")
    body.extend(generated_metadata_lines(colorset))
    return "---\n" + "\n".join(body) + "\n---\n"


def first_declaration(body: str) -> str:
    _, rest = split_frontmatter(body)
    for raw_line in rest.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%%") or line.startswith("---"):
            continue
        return line.split()[0].rstrip(":")
    return "unknown"


def canonical_family(declaration: str) -> str:
    lowered = declaration.lower()
    return DECLARATION_TO_FAMILY.get(lowered, lowered)


def referenced_color_classes(source: str) -> list[str]:
    found: set[str] = set()
    for regex in (TRIPLE_CLASS_RE, CLASS_LINE_RE, CSS_CLASS_LINE_RE):
        for match in regex.finditer(source):
            for token in re.split(r"[\s,]+", match.group("classes").strip()):
                if token in COLOR_CLASSES:
                    found.add(token)
    return [class_name for class_name in COLOR_CLASS_ORDER if class_name in found]


def strip_generated_class_defs(source: str) -> str:
    kept_lines: list[str] = []
    for line in source.splitlines():
        match = CLASS_DEF_RE.match(line)
        if match:
            class_tokens = {token.strip() for token in re.split(r"[, ]+", match.group("classes")) if token.strip()}
            if class_tokens & COLOR_CLASSES:
                continue
        kept_lines.append(line)
    trailing = "\n" if source.endswith("\n") else ""
    return "\n".join(kept_lines) + trailing


def normalize_class_assignments(source: str) -> str:
    """Expand parser-incompatible comma-grouped Class style assignments."""
    def expand(match: re.Match[str]) -> str:
        targets = [target.strip() for target in match.group("targets").split(",")]
        return "\n".join(
            f'{match.group("indent")}class {target} {match.group("classes").strip()}'
            for target in targets
        )

    return CLASS_MULTI_ASSIGNMENT_RE.sub(expand, source)


def strip_unsupported_color_class_references(source: str) -> str:
    kept_lines: list[str] = []
    for line in source.splitlines():
        if any(
            regex.match(line)
            and referenced_color_classes(line)
            for regex in (CLASS_LINE_RE, CSS_CLASS_LINE_RE)
        ):
            continue
        kept_lines.append(SEMANTIC_TRIPLE_CLASS_RE.sub("", line).rstrip())
    trailing = "\n" if source.endswith("\n") else ""
    return "\n".join(kept_lines) + trailing


def quote_quadrant_axis_endpoints(source: str) -> str:
    """Keep punctuation-bearing quadrant labels parseable without changing visible text."""
    quoted_lines: list[str] = []
    for line in source.splitlines():
        match = QUADRANT_AXIS_RE.match(line)
        if not match:
            quoted_lines.append(line)
            continue
        endpoints: list[str] = []
        for name in ("left", "right"):
            endpoint = match.group(name).strip()
            if not (len(endpoint) >= 2 and endpoint.startswith('"') and endpoint.endswith('"')):
                endpoint = f'"{endpoint}"'
            endpoints.append(endpoint)
        quoted_lines.append(
            f'{match.group("indent")}{match.group("axis")} {endpoints[0]} --> {endpoints[1]}'
        )
    trailing = "\n" if source.endswith("\n") else ""
    return "\n".join(quoted_lines) + trailing


def normalize_xy_category_labels(source: str) -> str:
    """Remove redundant numeric observations from XY category labels."""
    axis_match = XY_AXIS_LINE_RE.search(source)
    series_match = XY_SERIES_LINE_RE.search(source)
    if not axis_match or not series_match:
        return source
    try:
        labels = next(csv.reader([axis_match.group("items")], skipinitialspace=True))
        series = [Decimal(value.strip()) for value in series_match.group("values").split(",")]
    except (csv.Error, InvalidOperation, StopIteration):
        return source
    if len(labels) != len(series):
        return source

    clean_labels: list[str] = []
    for raw_label, series_value in zip(labels, series, strict=True):
        label = raw_label.strip()
        suffix_match = next((regex.fullmatch(label) for regex in XY_VALUE_SUFFIX_RES if regex.fullmatch(label)), None)
        if not suffix_match:
            return source
        try:
            suffix_value = Decimal(suffix_match.group("value"))
        except InvalidOperation:
            return source
        clean_label = suffix_match.group("label").strip()
        if not clean_label or suffix_value != series_value:
            return source
        clean_labels.append(clean_label)

    replacement = (
        f'{axis_match.group("indent")}x-axis '
        f'[{", ".join(json.dumps(label, ensure_ascii=False) for label in clean_labels)}]'
    )
    return source[: axis_match.start()] + replacement + source[axis_match.end() :]


def style_mermaid_block(body: str, colorset: str) -> tuple[str, dict[str, object]]:
    original = body
    frontmatter, rest = split_frontmatter(body)
    declaration = first_declaration(frontmatter + rest)
    family = canonical_family(declaration)
    functional_options = extract_family_options(frontmatter, family)
    frontmatter = strip_generated_frontmatter(frontmatter)
    rest = remove_generated_directives(rest)
    if family == "classDiagram":
        rest = normalize_class_assignments(rest)
    referenced = referenced_color_classes(rest)
    can_define_classes = family in CLASSDEF_FAMILIES
    inserted_classes = referenced if can_define_classes else []
    skipped_classes = [] if can_define_classes else referenced

    rest = strip_generated_class_defs(rest)
    if not can_define_classes:
        rest = strip_unsupported_color_class_references(rest)
    if family == "quadrantChart":
        rest = quote_quadrant_axis_endpoints(rest)
    if family == "xyChart":
        rest = normalize_xy_category_labels(rest)
    styled_frontmatter = inject_colorset_frontmatter(
        frontmatter, colorset, family, rest, functional_options
    )
    styled = styled_frontmatter + rest.lstrip("\n")
    if inserted_classes:
        styled = styled.rstrip() + "\n  " + "\n  ".join(
            class_style(colorset, class_name) for class_name in inserted_classes
        ) + "\n"
    if original.endswith("\n") and not styled.endswith("\n"):
        styled += "\n"
    return styled, {
        "diagramType": declaration,
        "family": family,
        "changed": styled != original,
        "hasStyle": f'colorset: "{colorset}"' in styled and 'theme: "base"' in styled,
        "referencedClasses": referenced,
        "insertedClassDefs": inserted_classes,
        "skippedClassDefs": skipped_classes,
    }


def mermaid_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", "__pycache__"} for part in path.parts):
            continue
        if path.suffix.lower() in {".mmd", ".mermaid", ".md", ".markdown"}:
            yield path


def style_file(path: Path, root: Path, colorset: str) -> tuple[str, list[DiagramResult], bool]:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(root).as_posix()
    results: list[DiagramResult] = []
    changed = False

    if path.suffix.lower() in {".mmd", ".mermaid"}:
        styled, meta = style_mermaid_block(text, colorset)
        changed = styled != text
        results.append(
            DiagramResult(
                file=rel,
                block_index=1,
                diagram_type=str(meta["diagramType"]),
                family=str(meta["family"]),
                changed=bool(meta["changed"]),
                has_style=bool(meta["hasStyle"]),
                referenced_classes=list(meta["referencedClasses"]),
                inserted_class_defs=list(meta["insertedClassDefs"]),
                skipped_class_defs=list(meta["skippedClassDefs"]),
            )
        )
        return styled, results, changed

    block_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal block_index, changed
        block_index += 1
        styled, meta = style_mermaid_block(match.group("body"), colorset)
        if styled != match.group("body"):
            changed = True
        results.append(
            DiagramResult(
                file=rel,
                block_index=block_index,
                diagram_type=str(meta["diagramType"]),
                family=str(meta["family"]),
                changed=bool(meta["changed"]),
                has_style=bool(meta["hasStyle"]),
                referenced_classes=list(meta["referencedClasses"]),
                inserted_class_defs=list(meta["insertedClassDefs"]),
                skipped_class_defs=list(meta["skippedClassDefs"]),
            )
        )
        return match.group("open") + styled + match.group("close")

    styled_text = FENCE_RE.sub(replace, text)
    return styled_text, results, changed


def write_report(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_routing_metadata(
    root: Path, colorset: str, diagrams: list[DiagramResult]
) -> tuple[Path | None, str | None, dict[str, object]]:
    path = root / "decision.json"
    status: dict[str, object] = {
        "path": "decision.json",
        "present": path.is_file(),
        "recognized": False,
        "changed": False,
    }
    if not path.is_file() or len(diagrams) != 1:
        return None, None, status
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"decision.json could not be read as JSON: {exc}", status
    keys = {"selectedFamily", "declaration", "colorset", "reason"}
    if not isinstance(value, dict) or set(value) != keys or not all(
        isinstance(value[key], str) for key in keys
    ):
        return None, None, status

    diagram = diagrams[0]
    expected = {
        "selectedFamily": diagram.family,
        "declaration": diagram.diagram_type,
        "colorset": colorset,
        "reason": value["reason"],
    }
    changed = any(value[key] != expected[key] for key in keys - {"reason"})
    status.update(
        {
            "recognized": True,
            "changed": changed,
            "canonicalFamily": diagram.family,
            "declaration": diagram.diagram_type,
            "colorset": colorset,
        }
    )
    rendered = json.dumps(expected, indent=2, ensure_ascii=False) + "\n" if changed else None
    return path if changed else None, rendered, status


def build_report(root: Path, colorset: str, diagrams: list[DiagramResult], changed_files: list[str], check: bool) -> dict[str, object]:
    missing = [d for d in diagrams if not d.has_style]
    declarations_seen = sorted({d.diagram_type for d in diagrams})
    families_seen = sorted({d.family for d in diagrams})
    declaration_counts = {declaration: 0 for declaration in SUPPORTED_DECLARATIONS}
    for diagram in diagrams:
        if diagram.diagram_type in declaration_counts:
            declaration_counts[diagram.diagram_type] += 1
    missing_current = [declaration for declaration in OFFICIAL_DECLARATIONS if declaration_counts[declaration] == 0]
    missing_supported = [declaration for declaration in SUPPORTED_DECLARATIONS if declaration_counts[declaration] == 0]
    duplicate_supported = sorted(declaration for declaration, count in declaration_counts.items() if count > 1)
    unexpected = sorted({diagram.diagram_type for diagram in diagrams if diagram.diagram_type not in SUPPORTED_DECLARATIONS})
    missing_families = [family for family in OFFICIAL_FAMILIES if family not in families_seen]

    def percentage(numerator: int, denominator: int) -> float:
        return round((numerator / denominator) * 100, 2) if denominator else 0.0

    return {
        "root": str(root),
        "colorset": colorset,
        "paletteMode": "standard" if colorset == "colorset1" else "extended",
        "mermaidVersion": MERMAID_VERSION,
        "diagramTypeManifest": "references/diagram-types.json",
        "check": check,
        "diagramCount": len(diagrams),
        "changedFileCount": len(changed_files),
        "changedFiles": changed_files,
        "missingStyleCount": len(missing),
        "declarationsSeen": declarations_seen,
        "familiesSeen": families_seen,
        "officialFamilyCount": len(OFFICIAL_FAMILIES),
        "officialFamilies": OFFICIAL_FAMILIES,
        "missingFamilies": missing_families,
        "familyCoveragePercent": percentage(len(OFFICIAL_FAMILIES) - len(missing_families), len(OFFICIAL_FAMILIES)),
        "officialDeclarationCount": len(OFFICIAL_DECLARATIONS),
        "officialDeclarations": OFFICIAL_DECLARATIONS,
        "missingOfficialDeclarations": missing_current,
        "officialDeclarationCoveragePercent": percentage(
            len(OFFICIAL_DECLARATIONS) - len(missing_current), len(OFFICIAL_DECLARATIONS)
        ),
        "supportedDeclarationCount": len(SUPPORTED_DECLARATIONS),
        "supportedDeclarations": SUPPORTED_DECLARATIONS,
        "missingSupportedDeclarations": missing_supported,
        "duplicateSupportedDeclarations": duplicate_supported,
        "unexpectedDeclarations": unexpected,
        "supportedDeclarationCoveragePercent": percentage(
            len(SUPPORTED_DECLARATIONS) - len(missing_supported), len(SUPPORTED_DECLARATIONS)
        ),
        "diagrams": [d.__dict__ for d in diagrams],
    }


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        print(f"Directory not found: {root}", file=sys.stderr)
        return 2
    if args.check and args.write:
        print("Use either --check or --write, not both.", file=sys.stderr)
        return 2

    diagrams: list[DiagramResult] = []
    changed_files: list[str] = []
    pending_writes: list[tuple[Path, str]] = []

    for path in mermaid_files(root):
        styled_text, file_results, changed = style_file(path, root, args.colorset)
        diagrams.extend(file_results)
        if changed:
            changed_files.append(path.relative_to(root).as_posix())
            pending_writes.append((path, styled_text))

    routing_path, routing_text, routing_metadata = normalize_routing_metadata(
        root, args.colorset, diagrams
    )
    if routing_path is not None and routing_text is not None:
        changed_files.append(routing_path.relative_to(root).as_posix())
        pending_writes.append((routing_path, routing_text))

    if args.write:
        for path, styled_text in pending_writes:
            path.write_text(styled_text, encoding="utf-8")

    report = build_report(root, args.colorset, diagrams, changed_files, args.check)
    report["routingMetadata"] = routing_metadata
    if args.report:
        write_report(args.report, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))

    if args.check and changed_files:
        print(f"{len(changed_files)} file(s) need colorset updates.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply the standard colorset1 or extended colorset2 palette to Mermaid files in a directory."
    )
    parser.add_argument("root", type=Path, help="Directory containing .mmd, .mermaid, .md, or .markdown files.")
    parser.add_argument(
        "--colorset",
        choices=sorted(PALETTES),
        default="colorset1",
        help="Palette to apply. Defaults to standard colorset1; use colorset2 for explicit extended-color requests.",
    )
    parser.add_argument("--write", action="store_true", help="Write styled diagrams in place.")
    parser.add_argument("--check", action="store_true", help="Fail if any file would change.")
    parser.add_argument("--report", type=Path, help="Write a JSON report.")
    return run(parser.parse_args())


if __name__ == "__main__":
    sys.exit(main())
