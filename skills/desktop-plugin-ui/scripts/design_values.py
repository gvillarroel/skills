#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve exact bundled palette tokens and calculate opaque sRGB contrast."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


BUNDLE = Path(__file__).resolve().parents[1]
PALETTES = {"colorset1": "colorset1.yml", "colorset2": "colorset2.yaml"}
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
TOKEN_PATH = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")
KEY = re.compile(r'^("(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z0-9_-]*):(?: (.*))?$')


class DesignFinding(ValueError):
    def __init__(self, code: str, message: str, **details: Any):
        super().__init__(message)
        self.finding = {"code": code, "message": message, **details}


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise DesignFinding("invalid_arguments", message)


def read_mapping(text: str) -> dict[str, Any]:
    """Parse only this bundle's two-space, quoted-string YAML mapping format.

    Fail closed on aliases, sequences, implicit types, duplicate keys, tabs,
    multiline scalars and inconsistent indentation. This is not a general YAML
    parser and intentionally does not guess unsupported future source syntax.
    """
    root: dict[str, Any] = {}
    stack: list[dict[str, Any]] = [root]
    previous_indent = -2
    previous_was_mapping = True
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" in line:
            raise DesignFinding("invalid_palette_source", "Tabs are not supported in the bundled palette mapping.", line=number)
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2 or indent > previous_indent + (2 if previous_was_mapping else 0):
            raise DesignFinding("invalid_palette_source", "Expected consistent two-space mapping indentation.", line=number)
        level = indent // 2
        if level >= len(stack):
            raise DesignFinding("invalid_palette_source", "A palette entry has no containing mapping.", line=number)
        match = KEY.fullmatch(line[indent:])
        if match is None:
            raise DesignFinding("invalid_palette_source", "Expected a mapping key and an optional double-quoted string.", line=number)
        raw_key, raw_value = match.groups()
        try:
            key = json.loads(raw_key) if raw_key.startswith('"') else raw_key
        except json.JSONDecodeError as error:
            raise DesignFinding("invalid_palette_source", "A quoted palette key is invalid.", line=number) from error
        if not isinstance(key, str) or not TOKEN_PATH.fullmatch(key) or "." in key:
            raise DesignFinding("invalid_palette_source", "Palette keys must be nonempty source-path segments.", line=number)
        parent = stack[level]
        if key in parent:
            raise DesignFinding("invalid_palette_source", "Duplicate palette keys are not allowed.", line=number, key=key)
        del stack[level + 1:]
        if raw_value is None:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append(child)
            previous_was_mapping = True
        else:
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError as error:
                raise DesignFinding("invalid_palette_source", "Palette scalar values must be double-quoted strings.", line=number) from error
            if not isinstance(value, str) or not raw_value.startswith('"'):
                raise DesignFinding("invalid_palette_source", "Palette scalar values must be strings, without implicit YAML types.", line=number)
            parent[key] = value
            previous_was_mapping = False
        previous_indent = indent
    if not root:
        raise DesignFinding("invalid_palette_source", "The bundled palette mapping is empty.")
    return root


def token_catalog(mapping: dict[str, Any]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}

    def visit(node: dict[str, Any], segments: tuple[str, ...]) -> None:
        if "value" in node:
            value = node["value"]
            if not isinstance(value, str) or not segments:
                raise DesignFinding("invalid_palette_source", "A design token must have a string value at a named source path.")
            token_path = ".".join(segments)
            is_color = segments[0] in {"colors", "interface"}
            if is_color and not HEX.fullmatch(value):
                raise DesignFinding("invalid_palette_source", "Color token values must use exact six-digit hexadecimal notation.", token_path=token_path)
            if "use" in node and not isinstance(node["use"], str):
                raise DesignFinding("invalid_palette_source", "A token use description must be a string.", token_path=token_path)
            result[token_path] = {"token_path": token_path, "value_path": token_path + ".value",
                                  "value": value, "value_type": "color" if is_color else "string"}
            if "use" in node:
                result[token_path]["use"] = node["use"]
        for key, value in node.items():
            if isinstance(value, dict):
                visit(value, (*segments, key))

    visit(mapping, ())
    if not result or not any(item["value_type"] == "color" for item in result.values()):
        raise DesignFinding("invalid_palette_source", "The palette contains no usable color tokens.")
    return dict(sorted(result.items()))


def resolve_token(requested_path: str, catalog: dict[str, dict[str, str]]) -> dict[str, str]:
    if not TOKEN_PATH.fullmatch(requested_path):
        raise DesignFinding("unknown_token_path", "Use an exact dot-separated source token path, optionally ending in .value.", requested_path=requested_path)
    canonical = requested_path[:-6] if requested_path.endswith(".value") else requested_path
    if canonical not in catalog:
        raise DesignFinding("unknown_token_path", "The source token path does not exist. No prefix was inserted; use --list-tokens for exact paths.", requested_path=requested_path)
    return {"requested_path": requested_path, **catalog[canonical]}


def exact_color(value: str, allowed: set[str]) -> str:
    if not HEX.fullmatch(value):
        raise DesignFinding("invalid_hex", "Contrast inputs must use #RRGGBB notation, without alpha, shorthand, names or surrounding whitespace.", input=value)
    canonical = value.lower()
    if canonical not in allowed:
        raise DesignFinding("unlisted_color", "The hexadecimal color is absent from the selected palette. Choose an exact listed token; no color was substituted.", input=value)
    return canonical


def relative_luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def calculate_contrast(foreground: str, background: str, allowed: set[str]) -> dict[str, Any]:
    front, back = exact_color(foreground, allowed), exact_color(background, allowed)
    front_luminance, back_luminance = relative_luminance(front), relative_luminance(back)
    light, dark = sorted((front_luminance, back_luminance), reverse=True)
    ratio = (light + 0.05) / (dark + 0.05)
    return {"input_foreground": foreground, "input_background": background,
            "foreground": front, "background": back,
            "foreground_luminance": front_luminance, "background_luminance": back_luminance,
            "ratio_unrounded": ratio,
            "requirements": {name: {"minimum": minimum, "passes": ratio >= minimum}
                             for name, minimum in (("ordinary_text", 4.5), ("large_text", 3.0), ("essential_non_text", 3.0))}}


def print_json(value: dict[str, Any]) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False))


def main(argv: list[str] | None = None) -> int:
    parser = Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--palette", default="colorset1", help="Exact bundled palette name: colorset1 (default) or colorset2.")
    parser.add_argument("--resolve", action="append", default=[], metavar="PATH", help="Resolve an exact token path, with or without .value. Repeat as needed.")
    parser.add_argument("--contrast", action="append", default=[], nargs=2, metavar=("FOREGROUND", "BACKGROUND"), help="Calculate unrounded contrast for two exact listed #RRGGBB values. Repeat as needed.")
    parser.add_argument("--list-tokens", action="store_true", help="List every exact token/value path, value and type, including typography and iconography.")
    parser.add_argument("--fail-on-findings", action="store_true", help="Exit 1 on findings for CI; default returns diagnostic passed:false JSON with exit 0.")
    args: argparse.Namespace | None = None
    try:
        args = parser.parse_args(argv)
        if not (args.resolve or args.contrast or args.list_tokens):
            parser.error("Choose at least one operation: --resolve, --contrast or --list-tokens.")
        if args.palette not in PALETTES:
            raise DesignFinding("unknown_palette", "Choose the exact palette name colorset1 or colorset2.", input=args.palette, available_palettes=sorted(PALETTES))
        relative = Path("assets") / "palettes" / PALETTES[args.palette]
        source_path = (BUNDLE / relative).resolve()
        if not source_path.is_relative_to(BUNDLE):
            raise DesignFinding("invalid_palette_source", "The selected palette must remain inside its own skill bundle.")
        payload = source_path.read_bytes()
        catalog = token_catalog(read_mapping(payload.decode("utf-8-sig")))
        allowed = {item["value"].lower() for item in catalog.values() if item["value_type"] == "color"}
        result: dict[str, Any] = {"passed": True, "palette": args.palette, "source": relative.as_posix(),
                                  "source_sha256": hashlib.sha256(payload).hexdigest(),
                                  "resolved": [resolve_token(value, catalog) for value in args.resolve],
                                  "contrast": [calculate_contrast(front, back, allowed) for front, back in args.contrast],
                                  "findings": []}
        if args.list_tokens:
            result["tokens"] = list(catalog.values())
            result["token_count"] = len(catalog)
            result["unique_color_count"] = len(allowed)
        if args.contrast:
            result["contrast_scope"] = "Opaque sRGB token arithmetic; no compositing, host-paint measurement or full accessibility certification. Requirement decisions use the unrounded ratio."
        print_json(result)
        return 0
    except DesignFinding as error:
        print_json({"passed": False, "findings": [error.finding]})
        if error.finding["code"] == "invalid_arguments":
            return 2
        return 1 if args is not None and args.fail_on_findings else 0
    except (OSError, UnicodeError) as error:
        print_json({"passed": False, "findings": [{"code": "palette_read_failed", "message": "The selected bundled palette could not be read as UTF-8.", "detail": str(error)}]})
        return 1 if args is not None and args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
