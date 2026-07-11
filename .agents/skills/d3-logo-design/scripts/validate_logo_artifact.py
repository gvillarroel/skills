#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Validate the static contract embedded in a generated D3 logo studio."""

from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
GENERIC_SEGMENTS = {"pattern", "item", "example", "feature"}
MAX_INTENTIONAL_OCCLUSION_RATIO = 0.30
EXPECTED_PALETTES = {
    "colorset1": {
        "#000000", "#1c1c1c", "#333e48", "#363636", "#4f4f4f", "#696969",
        "#6d1222", "#828282", "#9c9c9c", "#9e1b32", "#b5b5b5", "#cfcfcf",
        "#e7e7e7", "#e8002a", "#f7f7f7", "#ffccd5", "#ffffff",
    },
    "colorset2": {
        "#000000", "#004d66", "#007298", "#00ace6", "#1c1c1c", "#294d19",
        "#333e48", "#363636", "#36b300", "#431f47", "#45842a", "#4f4f4f",
        "#652f6c", "#696969", "#6d1222", "#828282", "#98700c", "#994a00",
        "#9c9c9c", "#9e00b3", "#9e1b32", "#b5b5b5", "#cdf3ff", "#cfcfcf",
        "#dbffcc", "#e77204", "#e7e7e7", "#e8002a", "#f1c319", "#f7f7f7",
        "#f9ccff", "#ff9633", "#ffccd5", "#ffd332", "#ffe5cc", "#fff4cc",
        "#ffffff",
    },
}


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.current_id: str | None = None
        self.scripts: dict[str, list[str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "script":
            return
        attr_map = dict(attrs)
        script_id = attr_map.get("id")
        if script_id:
            self.current_id = script_id
            self.scripts.setdefault(script_id, [])

    def handle_data(self, data: str) -> None:
        if self.current_id:
            self.scripts[self.current_id].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script":
            self.current_id = None


def load_script_json(parser: ScriptCollector, script_id: str, findings: list[str]) -> dict[str, Any]:
    chunks = parser.scripts.get(script_id)
    if not chunks:
        findings.append(f"Missing JSON script #{script_id}.")
        return {}
    raw = "".join(chunks).replace("<\\/", "</")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        findings.append(f"Invalid JSON in #{script_id}: {error}")
        return {}
    if not isinstance(value, dict):
        findings.append(f"#{script_id} must contain a JSON object.")
        return {}
    return value


def validate_ids(records: Any, label: str, findings: list[str]) -> tuple[list[str], list[str]]:
    if not isinstance(records, list):
        findings.append(f"Manifest {label} must be an array.")
        return [], []
    record_ids: list[str] = []
    signatures: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            findings.append(f"{label}[{index}] must be an object.")
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or not ID_RE.fullmatch(record_id):
            findings.append(f"{label}[{index}] has an invalid lowercase hyphen-case id: {record_id!r}")
            continue
        if len(record_id) > 64:
            findings.append(f"{label} id exceeds 64 characters: {record_id}")
        generic = sorted(GENERIC_SEGMENTS.intersection(record_id.split("-")))
        if generic:
            findings.append(f"{label} id contains generic segment(s) {', '.join(generic)}: {record_id}")
        record_ids.append(record_id)
        signature = record.get("geometrySignature")
        if label in {"patterns", "textures"}:
            if not isinstance(signature, str) or not ID_RE.fullmatch(signature):
                findings.append(f"{label} {record_id} has an invalid geometrySignature: {signature!r}")
            else:
                signatures.append(signature)
    duplicates = sorted(key for key, count in Counter(record_ids).items() if count > 1)
    if duplicates:
        findings.append(f"Duplicate {label} ids: {', '.join(duplicates)}")
    duplicate_signatures = sorted(key for key, count in Counter(signatures).items() if count > 1)
    if duplicate_signatures:
        findings.append(f"Duplicate {label} geometry signatures: {', '.join(duplicate_signatures)}")
    return record_ids, signatures


def validate_palette_data(palette_data: dict[str, Any], findings: list[str]) -> dict[str, set[str]]:
    colorsets = palette_data.get("colorsets")
    if not isinstance(colorsets, dict):
        findings.append("Palette data must expose a colorsets object.")
        return {}
    observed: dict[str, set[str]] = {}
    for colorset_id, expected in EXPECTED_PALETTES.items():
        colorset = colorsets.get(colorset_id)
        if not isinstance(colorset, dict):
            findings.append(f"Missing palette {colorset_id}.")
            continue
        allowed = colorset.get("allowed")
        if not isinstance(allowed, list):
            findings.append(f"Palette {colorset_id}.allowed must be an array.")
            continue
        normalized = {str(value).lower() for value in allowed}
        observed[colorset_id] = normalized
        if normalized != expected:
            missing = sorted(expected - normalized)
            extra = sorted(normalized - expected)
            findings.append(f"Palette {colorset_id} differs from the frozen contract; missing={missing}, extra={extra}.")
        role_values = set(str(value).lower() for value in colorset.get("roles", {}).values())
        sequence_values = set(str(value).lower() for value in colorset.get("sequence", []))
        leakage = sorted((role_values | sequence_values) - normalized)
        if leakage:
            findings.append(f"Palette {colorset_id} roles/sequence contain undeclared colors: {leakage}")
    return observed


def validate_text_clearance_contracts(records: Any, findings: list[str]) -> dict[str, Any]:
    """Validate opt-in exceptions to the default no-occlusion/no-omission rule."""
    stats: dict[str, Any] = {
        "intentionalOcclusionCount": 0,
        "intentionalOmissionCount": 0,
        "maxDeclaredOcclusionRatio": 0.0,
    }
    if not isinstance(records, list):
        return stats

    def validate_token(value: Any, field: str, location: str) -> bool:
        if not isinstance(value, str) or not ID_RE.fullmatch(value) or len(value) > 64:
            findings.append(
                f"{location} {field} must be a lowercase hyphen-case semantic role of at most 64 characters; "
                f"found {value!r}."
            )
            return False
        return True

    def validate_reason(value: Any, location: str) -> None:
        if not isinstance(value, str) or not value.strip():
            findings.append(f"{location} reason must be a non-empty explanation.")

    for pattern_index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        pattern_id = record.get("id") if isinstance(record.get("id"), str) else f"patterns[{pattern_index}]"

        occlusions = record.get("intentionalOcclusions", [])
        if not isinstance(occlusions, list):
            findings.append(f"Pattern {pattern_id} intentionalOcclusions must be an array when declared.")
        else:
            stats["intentionalOcclusionCount"] += len(occlusions)
            seen_occlusions: set[tuple[str, str]] = set()
            for exception_index, exception in enumerate(occlusions):
                location = f"Pattern {pattern_id} intentionalOcclusions[{exception_index}]"
                if not isinstance(exception, dict):
                    findings.append(f"{location} must be an object.")
                    continue
                text_role = exception.get("textRole")
                occluder_role = exception.get("occluderRole")
                text_role_valid = validate_token(text_role, "textRole", location)
                occluder_role_valid = validate_token(occluder_role, "occluderRole", location)
                validate_reason(exception.get("reason"), location)

                ratio = exception.get("maxOcclusionRatio")
                ratio_valid = (
                    isinstance(ratio, (int, float))
                    and not isinstance(ratio, bool)
                    and math.isfinite(ratio)
                    and 0 < ratio <= MAX_INTENTIONAL_OCCLUSION_RATIO
                )
                if not ratio_valid:
                    findings.append(
                        f"{location} maxOcclusionRatio must be a finite number greater than 0 and at most "
                        f"{MAX_INTENTIONAL_OCCLUSION_RATIO:.2f}; found {ratio!r}."
                    )
                else:
                    stats["maxDeclaredOcclusionRatio"] = max(stats["maxDeclaredOcclusionRatio"], float(ratio))

                if text_role_valid and occluder_role_valid:
                    key = (text_role, occluder_role)
                    if key in seen_occlusions:
                        findings.append(
                            f"Pattern {pattern_id} repeats the intentional occlusion for "
                            f"textRole={text_role!r}, occluderRole={occluder_role!r}."
                        )
                    seen_occlusions.add(key)

        omissions = record.get("intentionalOmissions", [])
        if not isinstance(omissions, list):
            findings.append(f"Pattern {pattern_id} intentionalOmissions must be an array when declared.")
        else:
            stats["intentionalOmissionCount"] += len(omissions)
            seen_omissions: set[tuple[str, str]] = set()
            for exception_index, exception in enumerate(omissions):
                location = f"Pattern {pattern_id} intentionalOmissions[{exception_index}]"
                if not isinstance(exception, dict):
                    findings.append(f"{location} must be an object.")
                    continue
                text_role = exception.get("textRole")
                when = exception.get("when")
                text_role_valid = validate_token(text_role, "textRole", location)
                when_valid = validate_token(when, "when", location)
                validate_reason(exception.get("reason"), location)

                if text_role_valid and when_valid:
                    key = (text_role, when)
                    if key in seen_omissions:
                        findings.append(
                            f"Pattern {pattern_id} repeats the intentional omission for "
                            f"textRole={text_role!r}, when={when!r}."
                        )
                    seen_omissions.add(key)

    return stats


def extract_engine(text: str, findings: list[str]) -> str:
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", text, re.IGNORECASE | re.DOTALL)
    candidates = [script for script in scripts if "attachD3LogoDesign" in script and "PATTERN_RENDERERS" in script]
    if len(candidates) != 1:
        findings.append(f"Expected exactly one embedded D3LogoDesign engine, found {len(candidates)}.")
        return ""
    return candidates[0].replace("<\\/script", "</script")


def registry_ids(engine: str, start: str, end: str, label: str, findings: list[str]) -> list[str]:
    start_index = engine.find(start)
    end_index = engine.find(end, start_index + len(start)) if start_index >= 0 else -1
    if start_index < 0 or end_index < 0:
        findings.append(f"Could not locate {label} renderer registry markers.")
        return []
    block = engine[start_index:end_index]
    values = re.findall(r'"(d3-logo-[a-z0-9-]+)"\s*:', block)
    duplicates = sorted(key for key, count in Counter(values).items() if count > 1)
    if duplicates:
        findings.append(f"Duplicate {label} renderer keys: {duplicates}")
    return values


def main() -> int:
    arg_parser = argparse.ArgumentParser(description="Validate a generated D3 logo studio HTML artifact.")
    arg_parser.add_argument("input", type=Path)
    arg_parser.add_argument("--expect-patterns", type=int, default=30)
    arg_parser.add_argument("--expect-textures", type=int, default=10)
    arg_parser.add_argument("--expect-compositions", type=int, default=30)
    arg_parser.add_argument("--require-colorset", choices=("colorset1", "colorset2"))
    arg_parser.add_argument("--json-report", type=Path)
    args = arg_parser.parse_args()

    path = args.input.expanduser().resolve()
    findings: list[str] = []
    if not path.exists() or not path.is_file():
        findings.append(f"Input HTML does not exist: {path}")
        text = ""
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            findings.append("Input HTML is empty.")

    collector = ScriptCollector()
    if text:
        collector.feed(text)
    application_text = re.sub(
        r'<script\b[^>]*\bdata-runtime=["\']d3-7\.9\.0["\'][^>]*>.*?</script>',
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    manifest = load_script_json(collector, "d3-logo-manifest", findings)
    palette_data = load_script_json(collector, "d3-logo-palettes", findings)
    initial_config = load_script_json(collector, "d3-logo-initial-config", findings)
    engine = extract_engine(text, findings)

    pattern_ids, pattern_signatures = validate_ids(manifest.get("patterns"), "patterns", findings)
    texture_ids, texture_signatures = validate_ids(manifest.get("textures"), "textures", findings)
    composition_ids, _ = validate_ids(manifest.get("compositions"), "compositions", findings)
    clearance_findings_before = len(findings)
    clearance_stats = validate_text_clearance_contracts(manifest.get("patterns"), findings)
    clearance_contract_valid = isinstance(manifest.get("patterns"), list) and len(findings) == clearance_findings_before
    expected_counts = {
        "patterns": (len(pattern_ids), args.expect_patterns),
        "textures": (len(texture_ids), args.expect_textures),
        "compositions": (len(composition_ids), args.expect_compositions),
    }
    for label, (actual, expected) in expected_counts.items():
        if actual != expected:
            findings.append(f"Expected {expected} {label}, found {actual}.")

    patterns = set(pattern_ids)
    textures = set(texture_ids)
    pattern_renderer_ids = registry_ids(
        engine,
        "const PATTERN_RENDERERS = Object.freeze({",
        "function renderLogo(",
        "pattern",
        findings,
    ) if engine else []
    texture_renderer_ids = registry_ids(
        engine,
        "const TEXTURE_RENDERERS = {",
        "function createTexture(",
        "texture",
        findings,
    ) if engine else []
    if set(pattern_renderer_ids) != patterns or len(pattern_renderer_ids) != len(patterns):
        findings.append(
            "Pattern renderer registry does not match the manifest; "
            f"missing={sorted(patterns - set(pattern_renderer_ids))}, extra={sorted(set(pattern_renderer_ids) - patterns)}."
        )
    if set(texture_renderer_ids) != textures or len(texture_renderer_ids) != len(textures):
        findings.append(
            "Texture renderer registry does not match the manifest; "
            f"missing={sorted(textures - set(texture_renderer_ids))}, extra={sorted(set(texture_renderer_ids) - textures)}."
        )
    referenced_patterns: list[str] = []
    referenced_textures: list[str] = []
    example_ids: list[str] = []
    for record in manifest.get("compositions", []) if isinstance(manifest.get("compositions"), list) else []:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            continue
        pattern_id = record.get("patternId")
        texture_id = record.get("textureId")
        example_id = record.get("exampleId")
        referenced_patterns.append(str(pattern_id))
        referenced_textures.append(str(texture_id))
        example_ids.append(str(example_id))
        if pattern_id not in patterns:
            findings.append(f"Composition {record['id']} references unknown pattern {pattern_id!r}.")
        if texture_id not in textures:
            findings.append(f"Composition {record['id']} references unknown texture {texture_id!r}.")
        expected_example_id = str(pattern_id).removeprefix("d3-logo-")
        if example_id != expected_example_id or not ID_RE.fullmatch(str(example_id)):
            findings.append(
                f"Composition {record['id']} exampleId {example_id!r} must match its local technique slug {expected_example_id!r}."
            )
        if record.get("colorset") not in EXPECTED_PALETTES:
            findings.append(f"Composition {record['id']} has an invalid colorset {record.get('colorset')!r}.")
    if set(referenced_patterns) != patterns or len(referenced_patterns) != len(patterns):
        missing = sorted(patterns - set(referenced_patterns))
        repeated = sorted(key for key, count in Counter(referenced_patterns).items() if count > 1)
        findings.append(f"Compositions must cover every pattern exactly once; missing={missing}, repeated={repeated}.")
    missing_textures = sorted(textures - set(referenced_textures))
    if missing_textures:
        findings.append(f"Compositions do not cover all textures: {missing_textures}")
    if len(set(example_ids)) != len(patterns):
        findings.append(f"Expected {len(patterns)} unique local example IDs, found {len(set(example_ids))}.")

    observed_palettes = validate_palette_data(palette_data, findings)
    manifest_palettes = manifest.get("palettes")
    if manifest_palettes != palette_data.get("colorsets"):
        findings.append("Embedded manifest palettes do not match #d3-logo-palettes.")

    selected = initial_config.get("colorset")
    if selected not in EXPECTED_PALETTES:
        findings.append(f"Initial config has an invalid colorset: {selected!r}")
    if manifest.get("selectedColorset") != selected:
        findings.append("Manifest selectedColorset does not match the initial config.")
    if args.require_colorset and selected != args.require_colorset:
        findings.append(f"Expected initial colorset {args.require_colorset}, found {selected!r}.")

    union = set().union(*observed_palettes.values()) if observed_palettes else set()
    color_literals = set()
    for token in re.findall(r"#[0-9A-Fa-f]{3,8}\b", application_text):
        normalized = token.lower()
        if len(normalized) != 7:
            findings.append(f"Unsupported hex color format: {token}")
        else:
            color_literals.add(normalized)
    palette_leakage = sorted(color_literals - union)
    if palette_leakage:
        findings.append(f"HTML contains colors outside the colorset union: {palette_leakage}")

    forbidden_patterns = {
        "gradient": r"(?i)(?:linear|radial|conic)-gradient\s*\(|<\s*(?:linearGradient|radialGradient)\b",
        "functional color": r"(?i)\b(?:rgba?|hsla?|lch|oklch)\s*\(",
        "raster or canvas surface": r"(?i)<\s*(?:image|img|picture|video|canvas)\b",
        "external resource element": r"(?i)<\s*(?:script|link)\b[^>]*\b(?:src|href)\s*=",
        "non-fragment URL paint": r"(?i)(?<![\w$])url\(\s*(?!['\"]?#)",
        "TODO marker": r"(?i)\bTODO\b",
    }
    for label, pattern in forbidden_patterns.items():
        scan_text = text if label == "external resource element" else application_text
        if re.search(pattern, scan_text):
            findings.append(f"Artifact contains forbidden {label} syntax.")
    standalone = not re.search(forbidden_patterns["external resource element"], text)
    if engine and re.search(r"\b(?:Math\.random|Date\.now|crypto\.getRandomValues|d3\.(?:event|voronoi|nest|mouse))\b", engine):
        findings.append("Embedded engine contains a forbidden nondeterministic or deprecated API.")

    node = shutil.which("node")
    engine_syntax_checked = False
    engine_runtime_checked = False
    engine_registry_parity = False
    if engine and node:
        engine_syntax_checked = True
        checked = subprocess.run(
            [node, "--check", "-"],
            input=engine,
            text=True,
            capture_output=True,
            check=False,
        )
        if checked.returncode != 0:
            detail = (checked.stderr or checked.stdout).strip()
            findings.append(f"Embedded engine failed node --check: {detail}")
        else:
            probe_code = (
                "const fs=require('fs'),vm=require('vm');"
                "vm.runInThisContext(fs.readFileSync(0,'utf8'));"
                "const a=globalThis.D3LogoDesign;"
                "process.stdout.write(JSON.stringify({patterns:a.PATTERNS,textures:a.TEXTURES,"
                "compositions:a.COMPOSITIONS,palettes:a.COLORSETS}));"
            )
            probed = subprocess.run(
                [node, "-e", probe_code],
                input=engine,
                text=True,
                capture_output=True,
                check=False,
            )
            if probed.returncode != 0:
                findings.append(f"Embedded engine runtime registry probe failed: {(probed.stderr or probed.stdout).strip()}")
            else:
                try:
                    runtime = json.loads(probed.stdout)
                except json.JSONDecodeError as error:
                    findings.append(f"Embedded engine runtime registry probe returned invalid JSON: {error}")
                else:
                    engine_runtime_checked = True
                    expected_runtime = {
                        "patterns": manifest.get("patterns"),
                        "textures": manifest.get("textures"),
                        "compositions": manifest.get("compositions"),
                        "palettes": palette_data.get("colorsets"),
                    }
                    engine_registry_parity = runtime == expected_runtime
                    if not engine_registry_parity:
                        mismatches = [key for key in expected_runtime if runtime.get(key) != expected_runtime[key]]
                        findings.append(f"Embedded engine registries differ from the authoritative catalogs: {mismatches}")
    elif engine:
        findings.append("Node.js is required to syntax-check the embedded engine but was not found on PATH.")

    required_literals = [
        "https://d3js.org v7.9.0 Copyright", 'data-runtime="d3-7.9.0"', 't.version="7.9.0"', 'data-small-size-lockup', "D3LogoDesign", 'id="studio-logo"', 'id="brand"', 'id="tagline"',
        'id="colorset"', 'id="font"', 'id="pattern"', 'id="texture"', 'id="density"',
        'id="curvature"', 'id="scale"', 'id="rotation"', 'id="textureStrength"',
    ]
    for literal in required_literals:
        if literal not in text:
            findings.append(f"Artifact is missing required marker: {literal}")
    if manifest.get("schemaVersion") != 1:
        findings.append(f"Expected manifest schemaVersion 1, found {manifest.get('schemaVersion')!r}.")
    if manifest.get("d3Version") != "7.9.0":
        findings.append(f"Expected manifest d3Version 7.9.0, found {manifest.get('d3Version')!r}.")

    report = {
        "ok": not findings,
        "input": str(path),
        "patternCount": len(pattern_ids),
        "textureCount": len(texture_ids),
        "compositionCount": len(composition_ids),
        "exampleIdCount": len(set(example_ids)),
        "patternSignatureCount": len(set(pattern_signatures)),
        "textureSignatureCount": len(set(texture_signatures)),
        "patternRendererCount": len(pattern_renderer_ids),
        "textureRendererCount": len(texture_renderer_ids),
        "engineSyntaxChecked": engine_syntax_checked,
        "engineRuntimeChecked": engine_runtime_checked,
        "engineRegistryParity": engine_registry_parity,
        "textClearanceContractValid": clearance_contract_valid,
        "textOcclusionDefault": "prohibited",
        **clearance_stats,
        "standalone": standalone,
        "embeddedD3Version": manifest.get("d3Version"),
        "usedTextureCount": len(set(referenced_textures)),
        "selectedColorset": selected,
        "initialPattern": initial_config.get("patternId"),
        "initialExampleId": initial_config.get("exampleId"),
        "initialTexture": initial_config.get("textureId"),
        "initialBrand": initial_config.get("brand"),
        "initialTagline": initial_config.get("tagline"),
        "initialFont": initial_config.get("font"),
        "initialSeed": initial_config.get("seed"),
        "staticColorCount": len(color_literals),
        "findings": findings,
    }
    if args.json_report:
        report_path = args.json_report.expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
