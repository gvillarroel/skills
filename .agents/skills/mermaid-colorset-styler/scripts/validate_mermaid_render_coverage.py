#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
STYLE_SCRIPT = SCRIPT_DIR / "style_mermaid_directory.py"
FIXTURE = SKILL_DIR / "assets" / "examples" / "base" / "all-types.md"
DEFAULT_MERMAID_PACKAGE = "@mermaid-js/mermaid-cli@11.16.0"
ERROR_CLASSES = {"error-icon", "error-text"}


def load_styler():
    spec = importlib.util.spec_from_file_location("style_mermaid_directory", STYLE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load style_mermaid_directory.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def find_npx() -> str:
    for name in ("npx.cmd", "npx", "npx.ps1"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("Could not find npx. Install Node.js to render Mermaid examples.")


def class_tokens(element: ET.Element) -> set[str]:
    return {token for token in element.get("class", "").split() if token}


def inspect_svg(path: Path) -> list[str]:
    if not path.is_file() or path.stat().st_size < 100:
        return ["render output is missing or too small"]
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        return [f"render output is invalid XML: {error}"]
    findings: list[str] = []
    if not root.tag.endswith("svg"):
        findings.append("render output root is not svg")
    if root.get("aria-roledescription", "").lower() == "error":
        findings.append("render output is a Mermaid error SVG")
    if any(class_tokens(element) & ERROR_CLASSES for element in root.iter()):
        findings.append("render output contains Mermaid error classes")
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    if "syntaxerrorintext" in text:
        findings.append("render output contains Mermaid syntax-error text")
    return findings


def style_fixture(styler, source: str, colorset: str) -> tuple[str, list[dict[str, str]]]:
    examples: list[dict[str, str]] = []

    def replace(match: re.Match[str]) -> str:
        body = match.group("body")
        declaration = styler.first_declaration(body)
        family = styler.canonical_family(declaration)
        styled, _metadata = styler.style_mermaid_block(body, colorset)
        examples.append({"declaration": declaration, "family": family})
        return match.group("open") + styled + match.group("close")

    return styler.FENCE_RE.sub(replace, source), examples


def validate_fixture_examples(styler, examples: list[dict[str, str]]) -> list[str]:
    findings: list[str] = []
    declarations = [example["declaration"] for example in examples]
    if len(declarations) != len(styler.SUPPORTED_DECLARATIONS):
        findings.append(
            f"fixture has {len(declarations)} diagrams; expected {len(styler.SUPPORTED_DECLARATIONS)}"
        )
    if set(declarations) != set(styler.SUPPORTED_DECLARATIONS):
        findings.append(
            "fixture declaration set differs from the renderable manifest: "
            f"missing={sorted(set(styler.SUPPORTED_DECLARATIONS) - set(declarations))}, "
            f"unexpected={sorted(set(declarations) - set(styler.SUPPORTED_DECLARATIONS))}"
        )
    duplicate_declarations = sorted(
        declaration for declaration in set(declarations) if declarations.count(declaration) > 1
    )
    if duplicate_declarations:
        findings.append(f"fixture has duplicate declarations: {duplicate_declarations}")
    return findings


def rendered_counts_by_colorset(
    actual_names: set[str], colorset_inputs: list[dict[str, object]]
) -> dict[str, int]:
    return {
        str(item["colorset"]): sum(
            f"rendered-{index}.svg" in actual_names
            for index in range(int(item["startIndex"]), int(item["endIndex"]) + 1)
        )
        for item in colorset_inputs
    }


def attempts_for_colorset(
    attempts: list[dict[str, object]], colorset: str
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for attempt in attempts:
        result = dict(attempt)
        counts = result.pop("colorsetRenderedSvgCounts", {})
        if isinstance(counts, dict):
            result["renderedSvgCount"] = int(counts.get(colorset, 0))
        results.append(result)
    return results


def render_colorsets(
    styler,
    npx: str,
    package: str,
    source: str,
    workspace: Path,
    timeout: int,
    retries: int,
    jobs: int,
) -> tuple[list[dict[str, object]], list[str], dict[str, object]]:
    colorset_inputs: list[dict[str, object]] = []
    combined_parts: list[str] = []
    next_global_index = 1
    for colorset in ("colorset1", "colorset2"):
        styled, examples = style_fixture(styler, source, colorset)
        start_index = next_global_index
        end_index = start_index + len(examples) - 1
        next_global_index = end_index + 1
        colorset_inputs.append(
            {
                "colorset": colorset,
                "examples": examples,
                "startIndex": start_index,
                "endIndex": end_index,
                "findings": validate_fixture_examples(styler, examples),
            }
        )
        combined_parts.append(f"# {colorset}\n\n{styled.strip()}\n")

    input_path = workspace / "all-colorsets.md"
    output_path = workspace / "rendered.md"
    input_path.write_text("\n\n".join(combined_parts), encoding="utf-8", newline="\n")
    # Mermaid CLI shares one Chromium browser across every Markdown render promise.
    # One serialized 96-diagram invocation avoids a flaky second browser launch on
    # constrained Linux runners while keeping both colorsets freshly rendered.
    command = [
        npx,
        "-y",
        package,
        "-i",
        str(input_path),
        "-o",
        str(output_path),
        "--quiet",
        "--jobs",
        str(jobs),
    ]
    render_count = next_global_index - 1
    expected_names = {f"rendered-{index}.svg" for index in range(1, render_count + 1)}
    attempts: list[dict[str, object]] = []
    completed: subprocess.CompletedProcess[str] | None = None
    for attempt in range(1, retries + 1):
        for stale_path in workspace.glob("rendered-*.svg"):
            stale_path.unlink()
        output_path.unlink(missing_ok=True)
        try:
            completed = subprocess.run(
                command,
                cwd=workspace,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
                timeout=timeout,
            )
            actual_names = {path.name for path in workspace.glob("rendered-*.svg")}
            attempts.append(
                {
                    "attempt": attempt,
                    "exitCode": completed.returncode,
                    "jobs": jobs,
                    "renderedSvgCount": len(actual_names),
                    "colorsetRenderedSvgCounts": rendered_counts_by_colorset(
                        actual_names, colorset_inputs
                    ),
                    "stdout": completed.stdout.strip()[-1000:],
                    "stderr": completed.stderr.strip()[-1000:],
                }
            )
            if completed.returncode == 0 and actual_names == expected_names:
                break
        except subprocess.TimeoutExpired:
            completed = None
            timeout_names = {path.name for path in workspace.glob("rendered-*.svg")}
            attempts.append(
                {
                    "attempt": attempt,
                    "exitCode": None,
                    "jobs": jobs,
                    "renderedSvgCount": len(timeout_names),
                    "colorsetRenderedSvgCounts": rendered_counts_by_colorset(
                        timeout_names, colorset_inputs
                    ),
                    "stdout": "",
                    "stderr": f"timed out after {timeout} seconds",
                }
            )

    actual_names = {path.name for path in workspace.glob("rendered-*.svg")}
    final_exit_code = completed.returncode if completed is not None else None
    batch_findings: list[str] = []
    if completed is None:
        batch_findings.append(f"Mermaid CLI did not complete within {retries} attempts")
    elif completed.returncode != 0:
        detail = (completed.stderr.strip() or completed.stdout.strip())[-2000:]
        batch_findings.append(
            f"Mermaid CLI exited {completed.returncode} after {len(attempts)} attempts: {detail}"
        )

    if actual_names != expected_names:
        batch_findings.append(
            f"rendered SVG set differs: missing={sorted(expected_names - actual_names)}, "
            f"unexpected={sorted(actual_names - expected_names)}"
        )

    colorset_results: list[dict[str, object]] = []
    prefixed_findings: list[str] = list(batch_findings)
    for colorset_input in colorset_inputs:
        colorset = str(colorset_input["colorset"])
        examples = colorset_input["examples"]
        assert isinstance(examples, list)
        start_index = int(colorset_input["startIndex"])
        colorset_findings = list(colorset_input["findings"])
        render_results: list[dict[str, object]] = []
        for index, example in enumerate(examples, start=1):
            assert isinstance(example, dict)
            global_index = start_index + index - 1
            svg_findings = inspect_svg(workspace / f"rendered-{global_index}.svg")
            render_results.append(
                {
                    "index": index,
                    "globalIndex": global_index,
                    "declaration": example["declaration"],
                    "family": example["family"],
                    "approved": not svg_findings,
                    "findings": svg_findings,
                }
            )
            colorset_findings.extend(
                f"{example['declaration']}: {finding}" for finding in svg_findings
            )
        findings = [*batch_findings, *colorset_findings]
        colorset_results.append(
            {
                "colorset": colorset,
                "ok": not findings and not batch_findings,
                "exitCode": final_exit_code,
                "jobs": jobs,
                "attemptCount": len(attempts),
                "attempts": attempts_for_colorset(attempts, colorset),
                "startIndex": start_index,
                "endIndex": int(colorset_input["endIndex"]),
                "diagramCount": len(examples),
                "approvedRenderCount": sum(1 for result in render_results if result["approved"]),
                "renders": render_results,
                "findings": findings,
            }
        )
        prefixed_findings.extend(
            f"{colorset}: {finding}" for finding in colorset_findings
        )

    batch = {
        "ok": not batch_findings,
        "exitCode": final_exit_code,
        "jobs": jobs,
        "attemptCount": len(attempts),
        "attempts": attempts,
        "renderCount": render_count,
        "renderedSvgCount": len(actual_names),
        "findings": batch_findings,
    }
    return colorset_results, prefixed_findings, batch


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fresh batch-render every Mermaid colorset declaration and reject error SVGs."
    )
    parser.add_argument("--fixture", type=Path, default=FIXTURE, help="Markdown coverage fixture.")
    parser.add_argument("--mermaid-cli-package", default=DEFAULT_MERMAID_PACKAGE, help="Exact npx Mermaid CLI package spec.")
    parser.add_argument("--timeout", type=int, default=180, help="Seconds allowed for the combined colorset batch render.")
    parser.add_argument("--render-retries", type=int, default=3, help="Fresh combined-batch attempts for transient browser failures.")
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Parallel Mermaid renders per batch. Keep 1 for deterministic CI coverage.",
    )
    parser.add_argument("--report", type=Path, help="Write the validation report as JSON.")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")

    styler = load_styler()
    npx = find_npx()
    findings: list[str] = []
    version = subprocess.run(
        [npx, "-y", args.mermaid_cli_package, "--version"],
        cwd=SKILL_DIR,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=args.timeout,
    )
    observed_version = version.stdout.strip()
    if version.returncode != 0 or observed_version != styler.MERMAID_VERSION:
        findings.append(
            f"Mermaid CLI version is {observed_version!r} with exit {version.returncode}; expected {styler.MERMAID_VERSION!r}"
        )

    source = args.fixture.resolve().read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="mermaid-render-coverage-") as temporary:
        workspace = Path(temporary)
        colorset_results, render_findings, batch = render_colorsets(
            styler,
            npx,
            args.mermaid_cli_package,
            source,
            workspace,
            args.timeout,
            args.render_retries,
            args.jobs,
        )
        findings.extend(render_findings)

    report = {
        "ok": not findings,
        "mermaidVersion": styler.MERMAID_VERSION,
        "observedMermaidCliVersion": observed_version,
        "familyCount": len(styler.OFFICIAL_FAMILIES),
        "currentDeclarationCount": len(styler.OFFICIAL_DECLARATIONS),
        "renderableDeclarationCount": len(styler.SUPPORTED_DECLARATIONS),
        "colorsetCount": len(colorset_results),
        "jobs": args.jobs,
        "batch": batch,
        "renderCount": sum(int(result["diagramCount"]) for result in colorset_results),
        "approvedRenderCount": sum(int(result["approvedRenderCount"]) for result in colorset_results),
        "colorsets": colorset_results,
        "findings": findings,
    }
    if args.report:
        report_path = args.report.resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
