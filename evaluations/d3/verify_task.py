#!/usr/bin/env python3
"""Independent Harbor verifier for the unified D3 skill evaluation."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from visual_palette import evaluate_visual_palette, make_counterfactual_source


COLORSET1 = {
    "#000000", "#1c1c1c", "#333e48", "#363636", "#4f4f4f", "#696969",
    "#6d1222", "#828282", "#9c9c9c", "#9e1b32", "#b5b5b5", "#cfcfcf",
    "#e7e7e7", "#e8002a", "#f7f7f7", "#ffccd5", "#ffffff",
}
COLORSET2 = COLORSET1 | {
    "#004d66", "#007298", "#00ace6", "#294d19", "#36b300", "#431f47",
    "#45842a", "#652f6c", "#98700c", "#994a00", "#9e00b3", "#cdf3ff",
    "#dbffcc", "#e77204", "#f1c319", "#f9ccff", "#ff9633", "#ffd332",
    "#ffe5cc", "#fff4cc",
}
EXTENDED = COLORSET2 - COLORSET1
HEX_RE = re.compile(r"(?<![A-Za-z0-9_-])#[0-9A-Fa-f]{3,8}\b")
FUNCTIONAL_COLOR_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_-])(?:rgb|rgba|hsl|hsla|lab|lch|oklab|oklch|color)\s*\("
)
EXTERNAL_DEPENDENCY_RE = re.compile(
    r"(?is)<script\b[^>]*\bsrc\s*=\s*[\"'](?:https?:)?//|"
    r"<link\b[^>]*\bhref\s*=\s*[\"'](?:https?:)?//|"
    r"<(?:img|image)\b[^>]*(?:src|href|xlink:href)\s*=\s*[\"'](?:https?:)?//|"
    r"\b(?:fetch|d3\.(?:csv|json|text|xml|image))\s*\(\s*[\"']https?://"
)
D3_EVIDENCE_RE = re.compile(
    r"\bd3\.(?:select|selectAll|scale\w*|force\w*|line|area|arc|pie|stack|hierarchy|"
    r"tree|cluster|pack|geo\w*|axis\w*|drag|zoom|transition|pointer|quadtree|Delaunay)\b"
)
ANIMATION_RE = re.compile(r"(?i)\.transition\s*\(|requestAnimationFrame\s*\(|@keyframes\b|<animate(?:Transform|Motion)?\b")
INTERACTION_RE = re.compile(r"(?i)\.on\s*\(\s*[\"'](?:click|pointer|mouse|focus|key|drag)|addEventListener\s*\(|\btabindex\s*=")


class RenderedSurface(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: Counter[str] = Counter()
        self.classes: Counter[str] = Counter()
        self.ids: set[str] = set()
        self.attributes: list[dict[str, str]] = []
        self.text_parts: list[str] = []
        self.surface_parts: list[str] = []
        self._ignored_depth = 0
        self._style_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.casefold()
        values = {name.casefold(): value or "" for name, value in attrs}
        if lowered in {"script", "template"}:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if lowered == "style":
            self._style_depth += 1
        self.tags[lowered] += 1
        for class_name in values.get("class", "").split():
            self.classes[class_name] += 1
        if values.get("id"):
            self.ids.add(values["id"])
        self.attributes.append(values)
        rendered_attrs = " ".join(f'{name}="{value}"' for name, value in values.items())
        self.surface_parts.append(f"<{lowered} {rendered_attrs}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered in {"script", "template"} and self._ignored_depth:
            self._ignored_depth -= 1
            return
        if self._ignored_depth:
            return
        self.surface_parts.append(f"</{lowered}>")
        if lowered == "style" and self._style_depth:
            self._style_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        self.surface_parts.append(data)
        if not self._style_depth and data.strip():
            self.text_parts.append(data.strip())

    @property
    def text(self) -> str:
        return " ".join(self.text_parts)

    @property
    def surface(self) -> str:
        return "\n".join(self.surface_parts)


def read_json(path: Path, findings: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        findings.append(f"{label} missing or invalid: {error}")
        return {}
    if not isinstance(value, dict):
        findings.append(f"{label} must contain one JSON object")
        return {}
    return value


def render_html(source: Path, screenshot: Path, dom_log: Path, browser_log: Path, label: str) -> str:
    renderer = Path(__file__).with_name("render_browser.js")
    if not renderer.is_file():
        browser_log.write_text("Evaluator browser helper is missing.\n", encoding="utf-8")
        return ""
    command = [
        "node",
        str(renderer),
        str(source.resolve()),
        str(screenshot.resolve()),
        str(dom_log.resolve()),
    ]
    try:
        completed = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        browser_log.write_text(f"Chromium timed out: {error}\n", encoding="utf-8")
        return ""
    browser_log.write_text(
        f"returncode={completed.returncode}\n=== stderr ===\n{completed.stderr}\n",
        encoding="utf-8",
    )
    if completed.returncode != 0 or not dom_log.is_file() or not screenshot.is_file():
        return ""
    if screenshot.stat().st_size == 0 or dom_log.stat().st_size == 0:
        return ""
    return dom_log.read_text(encoding="utf-8")


def active_metadata(surface: RenderedSurface, colorset: str) -> bool:
    return any(
        attributes.get("data-colorset", "").casefold() == colorset
        or attributes.get("data-color-set", "").casefold() == colorset
        for attributes in surface.attributes
    )


def paint_contract(surface: RenderedSurface, colorset: str, require_extended: bool) -> tuple[bool, dict[str, Any], list[str]]:
    allowed = COLORSET1 if colorset == "colorset1" else COLORSET2
    raw = sorted(set(HEX_RE.findall(surface.surface)))
    malformed = sorted(value for value in raw if len(value) != 7 or value != value.casefold())
    canonical = sorted({value.casefold() for value in raw if len(value) == 7})
    forbidden = sorted(value for value in canonical if value not in allowed)
    functional = sorted(set(match.group(0) for match in FUNCTIONAL_COLOR_RE.finditer(surface.surface)))
    extended = sorted(set(canonical) & EXTENDED)
    findings = []
    if malformed:
        findings.append("non-canonical hex syntax")
    if forbidden:
        findings.append(f"colors outside {colorset}: {', '.join(forbidden)}")
    if functional:
        findings.append("functional color syntax")
    if require_extended and not extended:
        findings.append("no colorset2-only token on rendered surface")
    details = {
        "colors": canonical,
        "extendedColors": extended,
        "forbiddenColors": forbidden,
        "malformedColors": malformed,
        "functionalSyntax": functional,
    }
    return not findings, details, findings


def metadata_contract(decision: dict[str, Any], contract: dict[str, Any]) -> tuple[bool, list[str]]:
    findings = []
    if decision.get("route") != contract["route"]:
        findings.append(f"decision route must be {contract['route']}")
    if decision.get("colorset") != contract["colorset"]:
        findings.append(f"decision colorset must be {contract['colorset']}")
    pattern_id = decision.get("patternId")
    expected_pattern = contract.get("expectedPatternId")
    if expected_pattern and pattern_id != expected_pattern:
        findings.append(f"decision patternId must be {expected_pattern}")
    if not expected_pattern and (not isinstance(pattern_id, str) or not pattern_id.startswith("d3-")):
        findings.append("decision patternId must be a stable d3-* ID")
    if not isinstance(decision.get("reason"), str) or not decision.get("reason", "").strip():
        findings.append("decision reason is missing")
    return not findings, findings


def verify_evaluation(workspace: Path, log_dir: Path, contract: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    report_path = workspace / "deliverables" / "evaluation.md"
    decision = read_json(workspace / "deliverables" / "decision.json", findings, "decision.json")
    try:
        report = report_path.read_text(encoding="utf-8")
    except OSError as error:
        findings.append(f"evaluation.md missing: {error}")
        report = ""
    lowered = report.casefold()
    for term in contract.get("requiredTerms", []):
        if str(term).casefold() not in lowered:
            findings.append(f"evaluation missing term: {term}")
    for pattern in contract.get("patterns", []):
        if not re.search(pattern, report, re.IGNORECASE | re.MULTILINE):
            findings.append(f"evaluation missing structured evidence: {pattern}")
    metadata_ok, metadata_findings = metadata_contract(decision, contract)
    findings.extend(metadata_findings)
    fidelity_ok = not [finding for finding in findings if finding.startswith("evaluation ")]
    passed = bool(report and fidelity_ok and metadata_ok)
    rewards = {
        "reward": 1.0 if passed else 0.0,
        "routing": 1.0 if decision.get("route") == contract["route"] else 0.0,
        "palette": 1.0 if decision.get("colorset") == contract["colorset"] else 0.0,
        "render": 1.0,
        "fidelity": 1.0 if fidelity_ok else 0.0,
        "metadata": 1.0 if metadata_ok else 0.0,
        "d3_contract": 1.0 if fidelity_ok else 0.0,
    }
    return {"ok": passed, "rewards": rewards, "findings": findings}


def verify_visual(workspace: Path, log_dir: Path, contract: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    source_path = workspace / "deliverables" / "visual.html"
    decision = read_json(workspace / "deliverables" / "decision.json", findings, "decision.json")
    try:
        source = source_path.read_text(encoding="utf-8")
    except OSError as error:
        findings.append(f"visual.html missing: {error}")
        source = ""

    self_contained_ok = bool(source and not EXTERNAL_DEPENDENCY_RE.search(source))
    if not self_contained_ok:
        findings.append("visual.html is missing or has an external dependency")
    d3_ok = bool(D3_EVIDENCE_RE.search(source) and re.search(r'data-renderer\s*=\s*[\"\']d3[\"\']', source, re.IGNORECASE))
    if not d3_ok:
        findings.append("D3 execution evidence or data-renderer=\"d3\" is missing")
    if contract.get("requiresAnimation") and not ANIMATION_RE.search(source):
        findings.append("requested animation evidence is missing")
    if contract.get("requiresInteraction") and not INTERACTION_RE.search(source):
        findings.append("requested interaction evidence is missing")

    actual_png = log_dir / "rendered.png"
    actual_dom_path = log_dir / "rendered-dom.html"
    actual_log = log_dir / "chromium-render.log"
    dom = render_html(source_path, actual_png, actual_dom_path, actual_log, "actual") if source else ""
    render_ok = bool(dom and actual_png.is_file() and actual_png.stat().st_size > 0)
    if not render_ok:
        findings.append("independent Chromium render failed")

    surface = RenderedSurface()
    if dom:
        surface.feed(dom)
        surface.close()
    if surface.tags["svg"] < 1 or surface.tags["title"] < 1 or surface.tags["desc"] < 1:
        findings.append("rendered SVG must contain svg, title, and desc")
    if not any(attributes.get("viewbox", "").strip() for attributes in surface.attributes):
        findings.append("rendered SVG viewBox is missing")
    if not active_metadata(surface, contract["colorset"]):
        findings.append(f"rendered active-colorset metadata is not {contract['colorset']}")

    visible_text = surface.text.casefold()
    for term in contract.get("requiredTerms", []):
        if str(term).casefold() not in visible_text:
            findings.append(f"rendered visual missing term: {term}")
    positions = [visible_text.find(str(term).casefold()) for term in contract.get("orderedTerms", [])]
    if positions and (any(position < 0 for position in positions) or positions != sorted(positions)):
        findings.append("rendered visible order is incorrect")
    for tag, minimum in contract.get("tagMinimums", {}).items():
        if surface.tags[str(tag).casefold()] < int(minimum):
            findings.append(f"rendered tag {tag} count below {minimum}")
    for class_name, minimum in contract.get("classMinimums", {}).items():
        if surface.classes[str(class_name)] < int(minimum):
            findings.append(f"rendered class {class_name} count below {minimum}")
    for required_id in contract.get("requiredIds", []):
        if str(required_id) not in surface.ids:
            findings.append(f"rendered ID missing: {required_id}")
    for attribute, expected in contract.get("requiredAttributes", {}).items():
        expected_values = [str(value) for value in expected] if isinstance(expected, list) else [str(expected)]
        if not any(values.get(attribute.casefold()) in expected_values for values in surface.attributes):
            findings.append(f"rendered attribute missing: {attribute}={expected_values}")

    static_palette_ok, static_palette, palette_findings = paint_contract(
        surface,
        contract["colorset"],
        bool(contract.get("requireExtended")),
    )
    findings.extend(f"palette: {finding}" for finding in palette_findings)

    visual_palette: dict[str, Any] = {}
    visual_palette_ok = False
    palette_influence_ok = False
    counterfactual_replacements = 0
    if render_ok and source:
        counterfactual, counterfactual_replacements = make_counterfactual_source(source, contract["colorset"])
        counterfactual_path = log_dir / "counterfactual.html"
        counterfactual_png = log_dir / "counterfactual.png"
        counterfactual_path.write_text(counterfactual, encoding="utf-8")
        counterfactual_dom = render_html(
            counterfactual_path,
            counterfactual_png,
            log_dir / "counterfactual-dom.html",
            log_dir / "chromium-counterfactual.log",
            "counterfactual",
        )
        if counterfactual_replacements and counterfactual_dom:
            try:
                visual_palette = evaluate_visual_palette(
                    actual_png,
                    counterfactual_png,
                    contract["colorset"],
                    contract["visualPalette"],
                )
                visual_palette_ok = bool(visual_palette.get("palette", {}).get("ok"))
                palette_influence_ok = bool(visual_palette.get("influence", {}).get("ok"))
            except (OSError, ValueError) as error:
                findings.append(f"visible palette analysis failed: {error}")
    if not visual_palette_ok:
        findings.append("rendered palette coverage failed")
    if not palette_influence_ok:
        findings.append("counterfactual palette influence failed")

    metadata_ok, metadata_findings = metadata_contract(decision, contract)
    findings.extend(metadata_findings)
    structural_prefixes = (
        "rendered visual missing", "rendered visible order", "rendered tag", "rendered class",
        "rendered ID", "rendered attribute", "rendered SVG", "rendered active",
    )
    fidelity_ok = not any(finding.startswith(structural_prefixes) for finding in findings)
    routing_ok = decision.get("route") == contract["route"]
    palette_ok = bool(static_palette_ok and visual_palette_ok and palette_influence_ok)
    passed = bool(
        source
        and self_contained_ok
        and d3_ok
        and render_ok
        and fidelity_ok
        and palette_ok
        and metadata_ok
        and not (contract.get("requiresAnimation") and not ANIMATION_RE.search(source))
        and not (contract.get("requiresInteraction") and not INTERACTION_RE.search(source))
    )
    rewards = {
        "reward": 1.0 if passed else 0.0,
        "routing": 1.0 if routing_ok else 0.0,
        "palette": 1.0 if palette_ok else 0.0,
        "visual_palette": 1.0 if visual_palette_ok else 0.0,
        "palette_influence": 1.0 if palette_influence_ok else 0.0,
        "render": 1.0 if render_ok else 0.0,
        "fidelity": 1.0 if fidelity_ok else 0.0,
        "metadata": 1.0 if metadata_ok else 0.0,
        "d3_contract": 1.0 if d3_ok and self_contained_ok else 0.0,
    }
    return {
        "ok": passed,
        "rewards": rewards,
        "findings": findings,
        "staticPalette": static_palette,
        "counterfactualReplacements": counterfactual_replacements,
        "visualPalette": visual_palette,
        "renderedInventory": {
            "tags": dict(surface.tags),
            "classes": dict(surface.classes),
            "ids": sorted(surface.ids),
        },
    }


def main() -> int:
    workspace = Path(os.environ.get("HARBOR_APP_DIR", Path.cwd())).resolve()
    log_dir = Path(os.environ.get("HARBOR_VERIFIER_LOG_DIR", workspace / ".harbor-verifier")).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    contract = json.loads((Path(__file__).with_name("contract.json")).read_text(encoding="utf-8"))
    if contract["route"] == "evaluation":
        result = verify_evaluation(workspace, log_dir, contract)
    else:
        result = verify_visual(workspace, log_dir, contract)
    result = {
        "taskId": contract["taskId"],
        "route": contract["route"],
        "expectedColorset": contract["colorset"],
        **result,
    }
    (log_dir / "verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (log_dir / "reward.json").write_text(
        json.dumps(result["rewards"], sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
