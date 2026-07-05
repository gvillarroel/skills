#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.45.0"]
# ///

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
HELPER_PATH = SCRIPT_DIR / "build_standalone_explainer.py"

PATTERNS = [
    "skill-tree",
    "skill-tree-route",
    "systems-flow",
    "state-machine",
    "comparison-matrix",
    "causal-loop",
    "phase-timeline",
    "metric-dashboard",
    "dependency-map",
    "sequence-trace",
    "sankey-flow",
    "swimlane-handoff",
    "risk-bowtie",
    "scenario-tree",
    "evidence-ladder",
    "layered-architecture",
    "data-lineage",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate every standalone Metro scaffold pattern without encoding video, then run Metro audits."
    )
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    parser.add_argument("--workdir", type=Path, help="Optional directory to keep generated pattern fixtures.")
    parser.add_argument("--patterns", help="Comma-separated subset of patterns to validate.")
    parser.add_argument("--install-browser", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--masonry-layout", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    return parser.parse_args()


def load_helper() -> Any:
    spec = importlib.util.spec_from_file_location("build_standalone_explainer", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selected_patterns(raw: str | None) -> list[str]:
    if not raw:
        return PATTERNS[:]
    requested = [item.strip() for item in raw.split(",") if item.strip()]
    unknown = sorted(set(requested) - set(PATTERNS))
    if unknown:
        raise ValueError(f"Unknown patterns: {', '.join(unknown)}")
    return requested


def helper_args(pattern: str, project_root: Path, *, masonry_layout: bool = False) -> argparse.Namespace:
    blank_labels = {
        "node_label": [],
        "option_label": [],
        "criterion_label": [],
        "state_label": [],
        "guard_label": [],
        "system_label": [],
        "tree_label": [],
        "meter_label": [],
        "route_label": [],
        "checkpoint_label": [],
        "phase_label": [],
        "metric_label": [],
        "threshold_label": [],
        "dependency_label": [],
        "cluster_label": [],
        "trace_label": [],
        "flow_label": [],
        "lane_label": [],
        "handoff_label": [],
        "threat_label": [],
        "barrier_label": [],
        "consequence_label": [],
        "scenario_label": [],
        "probability_label": [],
        "claim_label": [],
        "evidence_label": [],
        "layer_label": [],
        "concern_label": [],
        "lineage_label": [],
        "quality_label": [],
    }
    return argparse.Namespace(
        project_root=project_root,
        title=f"Metro {pattern} Smoke",
        topic=f"Metro strict-grid no-padding smoke for {pattern}",
        output_id=f"{pattern}-metro-smoke",
        pattern=pattern,
        checked_date="July 4, 2026",
        audience="validator",
        duration=4.0,
        fps=6,
        width=1280,
        height=720,
        edge_style="square",
        masonry_layout=masonry_layout,
        fact=[
            "Boxes must have zero internal padding.",
            "Hierarchy must use distinct grayscale levels.",
            "All rendered rectangles must stay on the grid with square edges.",
        ],
        anchor=["zero internal padding", "grayscale hierarchy levels", "0-radius rectangular panels"],
        source_url=["local pattern smoke"],
        **blank_labels,
    )


def write_scaffold(helper: Any, pattern: str, project_root: Path, *, masonry_layout: bool = False) -> dict[str, Any]:
    args = helper_args(pattern, project_root, masonry_layout=masonry_layout)
    paths = helper.build_paths(args.project_root, args.output_id)
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    package = helper.source_package(args, paths)
    helper.write_json(paths["source_package"], package)
    helper.write_notes(args, paths, package)
    helper.write_html(args, paths, package)
    helper.write_render_js(args, paths, package)
    return {"args": args, "paths": paths, "package": package}


def run_suite(
    *,
    html: Path,
    source_package: Path,
    output: Path,
    install_browser: bool,
    timeout_seconds: int,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "run_metro_audit_suite.py"),
        "--html",
        html.as_posix(),
        "--source-package",
        source_package.as_posix(),
        "--output",
        output.as_posix(),
        "--audit-timeout-seconds",
        str(timeout_seconds),
    ]
    if not install_browser:
        command.append("--no-install-browser")
    result = subprocess.run(command, text=True, capture_output=True, check=False, timeout=timeout_seconds * 4)
    try:
        manifest = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        manifest = {"manifestReadError": str(exc)}
    return {
        "command": command,
        "returnCode": result.returncode,
        "stdoutTail": result.stdout[-1000:],
        "stderrTail": result.stderr[-1000:],
        "manifest": output.as_posix(),
        "manifestPassed": manifest.get("passed"),
        "findings": manifest.get("findings"),
        "stylePassed": (manifest.get("styleAudit") or {}).get("passed") if isinstance(manifest, dict) else None,
        "compositionPassed": (manifest.get("compositionAudit") or {}).get("passed") if isinstance(manifest, dict) else None,
        "renderedFramePassed": (manifest.get("renderedFrameAudit") or {}).get("passed")
        if isinstance(manifest, dict)
        else None,
    }


def compact_rendered_metrics(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"readError": str(exc)}
    keys = [
        "passed",
        "zeroPaddingGeometryCheckCount",
        "zeroPaddingGeometryViolationCount",
        "untaggedInsetRectCheckCount",
        "untaggedInsetRectViolationCount",
        "maxRenderedInternalPaddingPx",
        "maxGrayLevelCount",
        "medianGrayLevelCount",
        "graySamplePassRatio",
        "finalGrayLevelCount",
        "masonryRequired",
        "maxMasonryModuleCount",
        "minMasonryModuleCount",
        "masonryModuleCountRange",
        "masonryModuleCountDistinct",
        "masonryModuleCountNondecreasing",
        "maxMasonrySizeCount",
        "maxMasonryAreaRatio",
        "maxSemanticGlyphCount",
        "minSemanticGlyphCount",
        "semanticGlyphCountDistinct",
        "maxTextElementCount",
        "maxTextCharacterCount",
    ]
    return {key: data.get(key) for key in keys}


def numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def aggregate_metrics(cases: list[dict[str, Any]]) -> dict[str, Any]:
    max_padding = 0.0
    total_zero_padding_violations = 0
    total_untagged_inset_violations = 0
    median_gray_levels: list[float] = []
    final_gray_levels: list[float] = []
    gray_pass_ratios: list[float] = []
    max_masonry_modules: list[float] = []
    masonry_size_counts: list[float] = []
    masonry_area_ratios: list[float] = []
    masonry_count_distincts: list[float] = []
    masonry_text_element_counts: list[float] = []
    masonry_text_character_counts: list[float] = []
    semantic_glyph_counts: list[float] = []
    patterns_with_padding_or_inset: list[str] = []
    patterns_with_weak_gray: list[str] = []
    patterns_with_weak_masonry: list[str] = []

    for case in cases:
        pattern = str(case.get("pattern"))
        rendered = case.get("renderedMetrics")
        if not isinstance(rendered, dict):
            continue
        padding = numeric(rendered.get("maxRenderedInternalPaddingPx"))
        if padding is not None:
            max_padding = max(max_padding, padding)
        zero_padding_violations = int(numeric(rendered.get("zeroPaddingGeometryViolationCount")) or 0)
        untagged_inset_violations = int(numeric(rendered.get("untaggedInsetRectViolationCount")) or 0)
        total_zero_padding_violations += zero_padding_violations
        total_untagged_inset_violations += untagged_inset_violations
        if (padding is not None and padding > 0) or zero_padding_violations or untagged_inset_violations:
            patterns_with_padding_or_inset.append(pattern)

        median_gray = numeric(rendered.get("medianGrayLevelCount"))
        if median_gray is not None:
            median_gray_levels.append(median_gray)
        final_gray = numeric(rendered.get("finalGrayLevelCount"))
        if final_gray is not None:
            final_gray_levels.append(final_gray)
        pass_ratio = numeric(rendered.get("graySamplePassRatio"))
        if pass_ratio is not None:
            gray_pass_ratios.append(pass_ratio)
        if (median_gray is not None and median_gray < 4) or (final_gray is not None and final_gray < 4):
            patterns_with_weak_gray.append(pattern)

        if rendered.get("masonryRequired") is True:
            max_modules = numeric(rendered.get("maxMasonryModuleCount"))
            size_count = numeric(rendered.get("maxMasonrySizeCount"))
            area_ratio = numeric(rendered.get("maxMasonryAreaRatio"))
            count_distinct = numeric(rendered.get("masonryModuleCountDistinct"))
            text_elements = numeric(rendered.get("maxTextElementCount"))
            text_characters = numeric(rendered.get("maxTextCharacterCount"))
            glyph_count = numeric(rendered.get("maxSemanticGlyphCount"))
            if max_modules is not None:
                max_masonry_modules.append(max_modules)
            if size_count is not None:
                masonry_size_counts.append(size_count)
            if area_ratio is not None:
                masonry_area_ratios.append(area_ratio)
            if count_distinct is not None:
                masonry_count_distincts.append(count_distinct)
            if text_elements is not None:
                masonry_text_element_counts.append(text_elements)
            if text_characters is not None:
                masonry_text_character_counts.append(text_characters)
            if glyph_count is not None:
                semantic_glyph_counts.append(glyph_count)
            if (
                (max_modules is not None and max_modules < 6)
                or (size_count is not None and size_count < 4)
                or (area_ratio is not None and area_ratio < 0.25)
                or (count_distinct is not None and count_distinct < 3)
                or rendered.get("masonryModuleCountNondecreasing") is not True
                or (text_elements is not None and text_elements > 0)
                or (text_characters is not None and text_characters > 0)
            ):
                patterns_with_weak_masonry.append(pattern)

    return {
        "passedPatternCount": sum(1 for case in cases if case.get("passed") is True),
        "failedPatternCount": sum(1 for case in cases if case.get("passed") is not True),
        "maxRenderedInternalPaddingPx": max_padding,
        "totalZeroPaddingGeometryViolationCount": total_zero_padding_violations,
        "totalUntaggedInsetRectViolationCount": total_untagged_inset_violations,
        "minMedianGrayLevelCount": min(median_gray_levels) if median_gray_levels else None,
        "minFinalGrayLevelCount": min(final_gray_levels) if final_gray_levels else None,
        "minGraySamplePassRatio": min(gray_pass_ratios) if gray_pass_ratios else None,
        "minMaxMasonryModuleCount": min(max_masonry_modules) if max_masonry_modules else None,
        "minMaxMasonrySizeCount": min(masonry_size_counts) if masonry_size_counts else None,
        "minMaxMasonryAreaRatio": min(masonry_area_ratios) if masonry_area_ratios else None,
        "minMasonryModuleCountDistinct": min(masonry_count_distincts) if masonry_count_distincts else None,
        "minMaxSemanticGlyphCount": min(semantic_glyph_counts) if semantic_glyph_counts else None,
        "maxMasonryTextElementCount": max(masonry_text_element_counts) if masonry_text_element_counts else None,
        "maxMasonryTextCharacterCount": max(masonry_text_character_counts) if masonry_text_character_counts else None,
        "patternsWithPaddingOrInsetViolations": patterns_with_padding_or_inset,
        "patternsWithWeakGrayHierarchy": patterns_with_weak_gray,
        "patternsWithWeakMasonry": patterns_with_weak_masonry,
    }


def validate_patterns(
    *,
    workdir: Path,
    patterns: list[str],
    install_browser: bool,
    masonry_layout: bool,
    timeout_seconds: int,
) -> dict[str, Any]:
    helper = load_helper()
    cases: list[dict[str, Any]] = []
    for pattern in patterns:
        project_root = workdir / pattern
        scaffold = write_scaffold(helper, pattern, project_root, masonry_layout=masonry_layout)
        paths = scaffold["paths"]
        report_dir = project_root / "artifacts" / "reviews"
        suite_output = report_dir / "metro-audit-suite.json"
        suite = run_suite(
            html=paths["html"],
            source_package=paths["source_package"],
            output=suite_output,
            install_browser=install_browser,
            timeout_seconds=timeout_seconds,
        )
        rendered_metrics = compact_rendered_metrics(report_dir / "metro-rendered-frame-audit.json")
        passed = (
            suite.get("returnCode") == 0
            and suite.get("manifestPassed") is True
            and rendered_metrics.get("passed") is True
        )
        cases.append(
            {
                "pattern": pattern,
                "passed": passed,
                "html": paths["html"].as_posix(),
                "sourcePackage": paths["source_package"].as_posix(),
                "suite": suite,
                "renderedMetrics": rendered_metrics,
            }
        )
    failed = [case for case in cases if not case.get("passed")]
    return {
        "passed": not failed,
        "patternCount": len(cases),
        "masonryLayout": masonry_layout,
        "failedPatterns": [case["pattern"] for case in failed],
        "workdir": workdir.as_posix(),
        "aggregateMetrics": aggregate_metrics(cases),
        "cases": cases,
    }


def main() -> int:
    args = parse_args()
    patterns = selected_patterns(args.patterns)
    if args.workdir:
        workdir = args.workdir
        workdir.mkdir(parents=True, exist_ok=True)
        report = validate_patterns(
            workdir=workdir,
            patterns=patterns,
            install_browser=args.install_browser,
            masonry_layout=args.masonry_layout,
            timeout_seconds=args.timeout_seconds,
        )
    else:
        with tempfile.TemporaryDirectory(prefix="metro-pattern-smoke-") as temp:
            report = validate_patterns(
                workdir=Path(temp),
                patterns=patterns,
                install_browser=args.install_browser,
                masonry_layout=args.masonry_layout,
                timeout_seconds=args.timeout_seconds,
            )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
