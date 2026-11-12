#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inspect completed evidence-report artifacts without modifying their content."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HEURISTICS = ["Visible status", "Familiar concepts", "Control and exits", "Consistent conventions",
              "Prevent mistakes", "Recognition cues", "Efficient paths", "Minimal content",
              "Useful errors", "Contextual help"]
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
TOKEN = re.compile(r"\b(?:colors|interface|typography|iconography)\.[A-Za-z0-9_.]+")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten_tokens(path: Path) -> dict[str, object]:
    """Read simple bundled YAML leaves independently, including font values."""
    stack = []
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^( *)([^:#][^:]*):\s*(.*)$", line)
        if not match:
            continue
        indent, key, scalar = match.groups()
        depth = len(indent)
        key = key.strip().strip('"\'')
        while stack and stack[-1][0] >= depth:
            stack.pop()
        names = [item[1] for item in stack] + [key]
        if not scalar:
            stack.append((depth, key))
        else:
            scalar = scalar.strip()
            if scalar.startswith('"'):
                parsed = json.loads(scalar)
            elif scalar.startswith("'") and scalar.endswith("'"):
                parsed = scalar[1:-1].replace("''", "'")
            else:
                parsed = scalar
            if isinstance(parsed, str) and HEX.fullmatch(parsed):
                parsed = parsed.lower()
            token = ".".join(names)
            values[token] = parsed
            if token.endswith(".value"):
                values[token[:-6]] = values[token]
    return values


def contrast(foreground: str, background: str) -> float:
    def luminance(color):
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
        return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
    values = sorted((luminance(foreground), luminance(background)))
    return (values[1] + 0.05) / (values[0] + 0.05)


def children(data):
    yield data
    if isinstance(data, dict):
        for value in data.values():
            yield from children(value)
    elif isinstance(data, list):
        for value in data:
            yield from children(value)


def inspect(run: Path) -> dict:
    workspace = run / "workspace"
    bundle = workspace / "skills/desktop-plugin-ui"
    output = workspace / "offerings/recommendation.json"
    markdown = workspace / "offerings/recommendation.md"
    data = json.loads(output.read_text(encoding="utf-8"))
    text = markdown.read_text(encoding="utf-8")
    tokens = flatten_tokens(bundle / "assets/palettes/colorset1.yml")
    path_checks = []
    for path in sorted({match.group(0).rstrip(".") for match in TOKEN.finditer(json.dumps(data) + "\n" + text)}):
        path_checks.append({"path": path, "exists": path in tokens, "value": tokens.get(path)})
    binding_checks = []
    for value in children(data.get("palette_bindings", {})):
        if isinstance(value, dict) and isinstance(value.get("value"), str) and HEX.fullmatch(value["value"]):
            path = value.get("path", value.get("token", value.get("token_path")))
            if isinstance(path, str):
                binding_checks.append({"path": path, "declared": value["value"].lower(), "actual": tokens.get(path),
                                       "passed": tokens.get(path) == value["value"].lower()})
        elif isinstance(value, str):
            for match in re.finditer(r"((?:colors|interface)\.[A-Za-z0-9_.]+)\s*\((#[0-9a-fA-F]{6})\)", value):
                path, declared = match.groups()
                binding_checks.append({"path": path, "declared": declared.lower(), "actual": tokens.get(path),
                                       "passed": tokens.get(path) == declared.lower()})
            for match in re.finditer(r"((?:colors|interface)\.[A-Za-z0-9_.]+)\s*(?:=|is)\s*(#[0-9a-fA-F]{6})", value):
                path, declared = match.groups()
                binding_checks.append({"path": path, "declared": declared.lower(), "actual": tokens.get(path),
                                       "passed": tokens.get(path) == declared.lower()})
    pairs = []
    palette = data.get("palette_bindings", {})
    for value in children(palette):
        if isinstance(value, dict) and all(key in value for key in ("foreground", "background", "ratio")):
            pairs.append((value["foreground"], value["background"], value["ratio"]))
        elif isinstance(value, dict) and all(key in value for key in ("foreground", "background", "ratio_unrounded")):
            pairs.append((value["foreground"], value["background"], value["ratio_unrounded"]))
        elif isinstance(value, dict) and isinstance(value.get("pair"), list) and len(value["pair"]) == 2 and isinstance(value.get("ratio"), (int, float)):
            pairs.append((*value["pair"], value["ratio"]))
        if isinstance(value, dict):
            for key, ratio in value.items():
                match = re.fullmatch(r"(#[0-9a-fA-F]{6}) on (#[0-9a-fA-F]{6})", key)
                if match and isinstance(ratio, (int, float)):
                    pairs.append((*match.groups(), ratio))
    named_pairs = {"primary_on_surface": ("#9e1b32", "#ffffff"), "inverse_on_primary": ("#ffffff", "#9e1b32"),
                   "hover_on_surface": ("#6d1222", "#ffffff"), "primary_text_on_surface": ("#333e48", "#ffffff"),
                   "secondary_text_on_surface": ("#696969", "#ffffff"),
                   "primary_text_on_selected_or_critical_background": ("#333e48", "#ffccd5"),
                   "critical_red_on_selected_or_critical_background": ("#e8002a", "#ffccd5"),
                   "primary_text_on_white": ("#333e48", "#ffffff"),
                   "secondary_text_on_white": ("#696969", "#ffffff"),
                   "primary_action_on_white": ("#9e1b32", "#ffffff"),
                   "pressed_action_on_white": ("#6d1222", "#ffffff"),
                   "primary_text_on_selected_or_error_background": ("#333e48", "#ffccd5"),
                   "error_red_on_error_background": ("#e8002a", "#ffccd5")}
    for name, ratio in palette.get("verified_contrast", {}).items():
        if name in named_pairs:
            pairs.append((*named_pairs[name], ratio))
    checks = palette.get("contrast_checks", {})
    if isinstance(checks, dict):
        for name, ratio in checks.items():
            if name in named_pairs and isinstance(ratio, str):
                number = re.match(r"^[0-9]+(?:\.[0-9]+)?", ratio)
                if number:
                    pairs.append((*named_pairs[name], float(number.group(0))))
    numeric_checks = [{"foreground": fg, "background": bg, "reported": value, "computed": contrast(fg, bg),
                       "passed": abs(value - contrast(fg, bg)) <= 1e-9} for fg, bg, value in pairs]
    heuristic_checks = [{"id": f"H{index}", "label": label,
                         "passed": sum(row.get("id") == f"H{index}" and row.get("label") == label
                                       for row in data.get("heuristics", [])) == 1} for index, label in enumerate(HEURISTICS, 1)]
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location("frozen_evidence_ledger", bundle / "scripts/evidence_ledger.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        rendered = module.render_markdown({"evidence_records": data["evidence_records"]})
    finally:
        sys.dont_write_bytecode = previous
    checker = [sys.executable, str(bundle / "scripts/check_reports.py"), str(markdown), str(output),
               "--require-evidence-records", "--fail-on-findings"]
    checked = subprocess.run(checker, capture_output=True, text=True, encoding="utf-8", timeout=30)
    checker_result = json.loads(checked.stdout)
    required = ["snapshot_date", "language", "offerings", "state_plan", "authored_ui_copy", "palette_bindings",
                "heuristics", "sources", "evidence_records", "host_acceptance_verified", "task_empirical_tests_performed"]
    literal_table = rendered.rstrip() in text
    underscore_equivalent_table = rendered.rstrip().replace("\\_", "_") in text.replace("\\_", "_")
    structural = {"required_fields": all(key in data for key in required),
                  "false_flags": data.get("host_acceptance_verified") is False and data.get("task_empirical_tests_performed") is False,
                  "default_palette": palette.get("palette") == "colorset1",
                  "offer_fields": all(all(key in offer for key in ("client", "feature", "evidence", "conditions", "fallback", "validation")) for offer in data.get("offerings", [])),
                  "helper_table_reused": literal_table or underscore_equivalent_table}
    result = {"structural_passed": all(structural.values()), "structural": structural,
              "checker_exit": checked.returncode, "checker": checker_result,
              "path_checks": path_checks, "bindings": binding_checks, "ratios": numeric_checks, "heuristics": heuristic_checks,
              "artifact_sha256": {"markdown": sha(markdown), "json": sha(output)},
              "helper_table_format": {"literal_match": literal_table, "underscore_escape_equivalent": underscore_equivalent_table},
              "limitations": "Numeric/token/format checks only; manually review fact scope, all prose, isolation and actual helper trace."}
    result["checked_subset_passed"] = (result["structural_passed"] and checked.returncode == 0 and checker_result["passed"]
                                         and all(row["exists"] for row in path_checks)
                                         and all(row["passed"] for row in binding_checks + numeric_checks + heuristic_checks))
    (run / "independent-content-check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return {"run": run.name, "checked_subset_passed": result["checked_subset_passed"], "structural": structural,
            "checker": {key: checker_result.get(key) for key in ("passed", "checked_official_urls", "checked_evidence_records")},
            "token_paths": len(path_checks), "bindings": len(binding_checks), "ratios": len(numeric_checks),
            "heuristics": len(heuristic_checks)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--count", type=int, default=3)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,150}", args.prefix) or args.count < 1:
        parser.error("Use a filesystem-safe prefix and a positive count")
    reports = [inspect(ROOT / "evaluations/runs" / f"{args.prefix}-{index}") for index in range(1, args.count + 1)]
    print(json.dumps(reports, indent=2))
    return 0 if all(row["checked_subset_passed"] for row in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
