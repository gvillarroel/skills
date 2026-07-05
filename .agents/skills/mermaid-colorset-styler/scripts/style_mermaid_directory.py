#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


LEGACY_COLORSET_DIRECTIVE_RE = re.compile(r"^\s*%%\{init:\s*\{.*?\"mermaid-colorset-styler\".*?\}\}%%\s*$")
FENCE_RE = re.compile(r"(?P<open>^[ \t]*```[ \t]*mermaid[^\n]*\n)(?P<body>.*?)(?P<close>^[ \t]*```[ \t]*$)", re.MULTILINE | re.DOTALL)
CLASS_DEF_RE = re.compile(r"^\s*classDef\s+(?P<classes>[A-Za-z0-9_, -]+)\s+.*$", re.MULTILINE)
TRIPLE_CLASS_RE = re.compile(r":::\s*(?P<classes>[A-Za-z0-9_ -]+)")
CLASS_LINE_RE = re.compile(r"^\s*class\s+[^;\n]+?\s+(?P<classes>[A-Za-z0-9_ -]+)\s*;?\s*$", re.MULTILINE)
CSS_CLASS_LINE_RE = re.compile(r"^\s*cssClass\s+\"[^\"]+\"\s+(?P<classes>[A-Za-z0-9_ -]+)\s*;?\s*$", re.MULTILINE)
TOP_LEVEL_YAML_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:")

CONFIG_BEGIN = "# mermaid-colorset-styler: config begin"
CONFIG_END = "# mermaid-colorset-styler: config end"
METADATA_BEGIN = "# mermaid-colorset-styler: metadata begin"
METADATA_END = "# mermaid-colorset-styler: metadata end"
GENERATED_BEGIN_MARKERS = {CONFIG_BEGIN, METADATA_BEGIN}
GENERATED_END_MARKERS = {CONFIG_END, METADATA_END}

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
    "nodeBorder",
    "clusterBkg",
    "clusterBorder",
    "defaultLinkColor",
    "edgeLabelBackground",
    "labelColor",
    "titleColor",
]

SERIES_THEME_KEYS = [
    "cScale0",
    "cScale1",
    "cScale2",
    "cScale3",
    "cScale4",
    "cScale5",
    "cScale6",
    "cScale7",
]

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
    "stateDiagram": ["classText"],
    "flowchart": ["classText"],
    "swimlane": ["classText"],
    "treemap": ["classText"],
    "gitGraph": [
        "commitLabelColor",
        "commitLabelBackground",
        "tagLabelColor",
        "tagLabelBackground",
        "git0",
        "git1",
        "git2",
        "git3",
        "git4",
        "git5",
        "git6",
        "git7",
        "gitBranchLabel0",
        "gitBranchLabel1",
        "gitBranchLabel2",
        "gitBranchLabel3",
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
    "quadrantChart": SERIES_THEME_KEYS,
    "sankey": SERIES_THEME_KEYS,
    "xyChart": ["xyChart"],
    "radar": ["radar"],
    "cynefin": ["cynefin"],
}

CLASSDEF_FAMILIES = {
    "flowchart",
    "swimlane",
    "classDiagram",
    "stateDiagram",
    "requirementDiagram",
    "treemap",
}

OFFICIAL_DECLARATIONS = [
    "flowchart",
    "graph",
    "swimlane-beta",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "journey",
    "gantt",
    "pie",
    "quadrantChart",
    "requirementDiagram",
    "gitGraph",
    "C4Context",
    "C4Container",
    "C4Component",
    "C4Dynamic",
    "C4Deployment",
    "mindmap",
    "timeline",
    "zenuml",
    "sankey-beta",
    "xychart-beta",
    "block-beta",
    "packet",
    "kanban",
    "architecture-beta",
    "radar-beta",
    "eventmodeling",
    "treemap-beta",
    "venn-beta",
    "ishikawa-beta",
    "wardley-beta",
    "cynefin-beta",
    "treeView-beta",
    "railroad-beta",
    "railroad-ebnf-beta",
    "railroad-abnf-beta",
    "railroad-peg-beta",
]


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


def theme_variables(colorset: str, family: str | None = None) -> dict[str, object]:
    p = PALETTES[colorset]
    variables = {
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
        "mainBkg": p["surface"],
        "nodeBorder": p["primary"],
        "clusterBkg": p["gray100"],
        "clusterBorder": p["gray400"],
        "defaultLinkColor": p["muted"],
        "edgeLabelBackground": p["surface"],
        "noteBkgColor": p["neutral_light"],
        "noteTextColor": p["ink"],
        "noteBorderColor": p["gray400"],
        "actorBkg": p["primary_light"],
        "actorBorder": p["primary"],
        "actorTextColor": p["ink"],
        "actorLineColor": p["primary"],
        "signalColor": p["muted"],
        "signalTextColor": p["ink"],
        "activationBorderColor": p["primary"],
        "activationBkgColor": p["primary_light"],
        "classText": p["ink"],
        "labelColor": p["ink"],
        "titleColor": p["ink"],
        "commitLabelColor": p["ink"],
        "commitLabelBackground": p["surface"],
        "tagLabelColor": p["ink"],
        "tagLabelBackground": p["neutral_light"],
        "git0": p["primary"],
        "git1": p["accent"],
        "git2": p["warning"],
        "git3": p["success"],
        "git4": p["special"],
        "git5": p["gray500"],
        "git6": p["gray700"],
        "git7": p["critical"],
        "gitBranchLabel0": p["surface"],
        "gitBranchLabel1": p["surface"],
        "gitBranchLabel2": p["ink"],
        "gitBranchLabel3": p["surface"],
        "pie1": p["primary"],
        "pie2": p["accent"],
        "pie3": p["warning"],
        "pie4": p["success"],
        "pie5": p["special"],
        "pie6": p["gray500"],
        "pie7": p["gray700"],
        "pie8": p["critical"],
        "pie9": p["primary_light"],
        "pie10": p["accent_light"],
        "pie11": p["warning_light"],
        "pie12": p["success_light"],
        "pieTitleTextColor": p["ink"],
        "pieLegendTextColor": p["ink"],
        "pieSectionTextColor": p["surface"],
        "pieStrokeColor": p["surface"],
        "fillType0": p["primary_light"],
        "fillType1": p["accent_light"],
        "fillType2": p["warning_light"],
        "fillType3": p["success_light"],
        "fillType4": p["special_light"],
        "fillType5": p["neutral_light"],
        "fillType6": p["gray200"],
        "fillType7": p["gray300"],
        "cScale0": p["primary"],
        "cScale1": p["accent"],
        "cScale2": p["warning"],
        "cScale3": p["success"],
        "cScale4": p["special"],
        "cScale5": p["gray500"],
        "cScale6": p["gray700"],
        "cScale7": p["critical"],
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
            "plotColorPalette": f"{p['primary']}, {p['accent']}, {p['warning']}, {p['success']}, {p['special']}",
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


def yaml_mapping_lines(mapping: dict[str, object], indent: int = 0) -> list[str]:
    lines: list[str] = []
    prefix = " " * indent
    for key, value in mapping.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.extend(yaml_mapping_lines(value, indent + 2))
        else:
            lines.append(f"{prefix}{key}: {yaml_scalar(value)}")
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


def colorset_config(colorset: str, family: str | None = None) -> dict[str, object]:
    return {
        "theme": "base",
        "themeVariables": theme_variables(colorset, family),
    }


def colorset_metadata(colorset: str) -> dict[str, object]:
    return {
        "mermaid-colorset-styler": {
            "colorset": colorset,
            "palette": PALETTES[colorset]["name"],
        }
    }


def generated_config_lines(colorset: str, family: str | None = None, indent: int = 0) -> list[str]:
    prefix = " " * indent
    return [f"{prefix}{CONFIG_BEGIN}"] + yaml_mapping_lines(colorset_config(colorset, family), indent) + [f"{prefix}{CONFIG_END}"]


def generated_metadata_lines(colorset: str, indent: int = 0) -> list[str]:
    prefix = " " * indent
    return [f"{prefix}{METADATA_BEGIN}"] + yaml_mapping_lines(colorset_metadata(colorset), indent) + [f"{prefix}{METADATA_END}"]


def colorset_frontmatter(colorset: str, family: str | None = None) -> str:
    lines = ["---"]
    lines.extend([CONFIG_BEGIN, "config:"])
    lines.extend(yaml_mapping_lines(colorset_config(colorset, family), 2))
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


def remove_config_style_keys(lines: list[str], start: int, end: int, indent: int) -> list[str]:
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
        cleaned.append(line)
        index += 1
    return cleaned


def inject_colorset_frontmatter(frontmatter: str, colorset: str, family: str | None = None) -> str:
    clean_frontmatter = strip_generated_frontmatter(frontmatter)
    if not clean_frontmatter:
        return colorset_frontmatter(colorset, family)

    lines = clean_frontmatter.splitlines()
    body = lines[1:-1]
    config_index = find_top_level_key(body, "config")
    if config_index is None:
        if body and body[-1].strip():
            body.append("")
        body.extend([CONFIG_BEGIN, "config:"])
        body.extend(yaml_mapping_lines(colorset_config(colorset, family), 2))
        body.append(CONFIG_END)
    else:
        end = find_mapping_end(body, config_index)
        indent = child_indent(body, config_index, end)
        cleaned_config = remove_config_style_keys(body, config_index, end, indent)
        body = body[: config_index + 1] + cleaned_config + generated_config_lines(colorset, family, indent) + body[end:]

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
    if lowered in {"flowchart", "graph"}:
        return "flowchart"
    if lowered == "swimlane-beta":
        return "swimlane"
    if lowered.startswith("c4"):
        return "c4"
    if lowered in {"statediagram", "statediagram-v2"}:
        return "stateDiagram"
    if lowered == "classdiagram":
        return "classDiagram"
    if lowered == "requirementdiagram":
        return "requirementDiagram"
    if lowered == "treemap-beta":
        return "treemap"
    if lowered.startswith("railroad-"):
        return "railroad"
    replacements = {
        "sequencediagram": "sequenceDiagram",
        "erdiagram": "erDiagram",
        "quadrantchart": "quadrantChart",
        "gitgraph": "gitGraph",
        "xychart-beta": "xyChart",
        "block-beta": "block",
        "architecture-beta": "architecture",
        "radar-beta": "radar",
        "ishikawa-beta": "ishikawa",
        "wardley-beta": "wardley",
        "venn-beta": "venn",
        "cynefin-beta": "cynefin",
        "treeview-beta": "treeView",
        "sankey-beta": "sankey",
    }
    return replacements.get(lowered, lowered)


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


def style_mermaid_block(body: str, colorset: str) -> tuple[str, dict[str, object]]:
    original = body
    frontmatter, rest = split_frontmatter(body)
    frontmatter = strip_generated_frontmatter(frontmatter)
    rest = remove_generated_directives(rest)
    declaration = first_declaration(frontmatter + rest)
    family = canonical_family(declaration)
    referenced = referenced_color_classes(rest)
    can_define_classes = family in CLASSDEF_FAMILIES
    inserted_classes = referenced if can_define_classes else []
    skipped_classes = [] if can_define_classes else referenced

    rest = strip_generated_class_defs(rest)
    styled_frontmatter = inject_colorset_frontmatter(frontmatter, colorset, family)
    styled = styled_frontmatter + rest.lstrip("\n")
    if inserted_classes:
        styled = styled.rstrip() + "\n  " + "\n  ".join(class_style(colorset, class_name) for class_name in inserted_classes) + "\n"
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


def build_report(root: Path, colorset: str, diagrams: list[DiagramResult], changed_files: list[str], check: bool) -> dict[str, object]:
    missing = [d for d in diagrams if not d.has_style]
    declarations_seen = sorted({d.diagram_type for d in diagrams})
    families_seen = sorted({d.family for d in diagrams})
    return {
        "root": str(root),
        "colorset": colorset,
        "check": check,
        "diagramCount": len(diagrams),
        "changedFileCount": len(changed_files),
        "changedFiles": changed_files,
        "missingStyleCount": len(missing),
        "declarationsSeen": declarations_seen,
        "familiesSeen": families_seen,
        "officialDeclarationCount": len(OFFICIAL_DECLARATIONS),
        "officialDeclarations": OFFICIAL_DECLARATIONS,
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

    if args.write:
        for path, styled_text in pending_writes:
            path.write_text(styled_text, encoding="utf-8")

    report = build_report(root, args.colorset, diagrams, changed_files, args.check)
    if args.report:
        write_report(args.report, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))

    if args.check and changed_files:
        print(f"{len(changed_files)} file(s) need colorset updates.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply colorset1 or colorset2 styling to Mermaid files in a directory.")
    parser.add_argument("root", type=Path, help="Directory containing .mmd, .mermaid, .md, or .markdown files.")
    parser.add_argument("--colorset", choices=sorted(PALETTES), required=True, help="Colorset to apply.")
    parser.add_argument("--write", action="store_true", help="Write styled diagrams in place.")
    parser.add_argument("--check", action="store_true", help="Fail if any file would change.")
    parser.add_argument("--report", type=Path, help="Write a JSON report.")
    return run(parser.parse_args())


if __name__ == "__main__":
    sys.exit(main())
