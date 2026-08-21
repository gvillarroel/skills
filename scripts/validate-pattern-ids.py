#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Validate canonical public pattern IDs across skill sources."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_ID_LENGTH = 64
REVIEW_ID_LENGTH = 48
GENERIC_SEGMENTS = {"pattern", "item", "example", "feature"}
TEXT_SUFFIXES = {".html", ".js", ".json", ".md", ".mjs", ".py", ".ts", ".tsx", ".vue"}
SKIP_PARTS = {"dist", "node_modules"}
STATIC_ID_PATTERNS = (
    re.compile(r'(?<!:)(?<!legacy-)data-pattern-id\s*=\s*["\']([^"\'${}`]+)["\']', re.IGNORECASE),
    re.compile(r'(?<!legacy)(?<!Legacy)\bpatternId\s*:\s*["\']([^"\'${}`]+)["\']'),
    re.compile(r'\*\*Pattern ID:\*\*\s*`([^`*]+)`'),
)


@dataclass(frozen=True)
class Finding:
    path: Path
    message: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def add(findings: list[Finding], path: Path, message: str) -> None:
    findings.append(Finding(path=path, message=message))


def iter_active_sources(root: Path):
    source_roots = (root / "skills", root / "evaluations")
    for source_root in source_roots:
        if not source_root.exists():
            continue
        for path in source_root.rglob("*"):
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            if source_root.name == "evaluations" and "runs" in path.relative_to(source_root).parts:
                continue
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            yield path


def validate_id(pattern_id: str, path: Path, findings: list[Finding]) -> None:
    if not ID_RE.fullmatch(pattern_id):
        add(findings, path, f"pattern ID must be lowercase hyphen-case: {pattern_id}")
        return
    if len(pattern_id) > MAX_ID_LENGTH:
        add(findings, path, f"pattern ID exceeds {MAX_ID_LENGTH} characters: {pattern_id}")
    generic = sorted(GENERIC_SEGMENTS.intersection(pattern_id.split("-")))
    if generic:
        add(findings, path, f"canonical pattern ID contains generic segment(s) {', '.join(generic)}: {pattern_id}")


def collect_explicit_ids(root: Path, findings: list[Finding]) -> tuple[dict[str, set[Path]], int]:
    observed: dict[str, set[Path]] = {}
    occurrences = 0
    for path in iter_active_sources(root):
        content = path.read_text(encoding="utf-8", errors="replace")
        for pattern in STATIC_ID_PATTERNS:
            for match in pattern.finditer(content):
                pattern_id = match.group(1).strip()
                if not pattern_id or pattern_id.endswith("-*") or any(token in pattern_id for token in "{}"):
                    continue
                validate_id(pattern_id, path, findings)
                observed.setdefault(pattern_id, set()).add(path)
                occurrences += 1

        stale_patterns = (
            re.compile(r'data-pattern-id\s*=\s*["\'`]([a-z0-9-]*-pattern-[a-z0-9-${}]+)', re.IGNORECASE),
            re.compile(r'(?<!legacy)(?<!Legacy)\bpatternId\s*(?:=|:)\s*["\'`]([a-z0-9-]*-pattern-[a-z0-9-${}]+)'),
        )
        for stale_pattern in stale_patterns:
            for match in stale_pattern.finditer(content):
                line_number = content.count("\n", 0, match.start()) + 1
                add(
                    findings,
                    path,
                    f"line {line_number} exposes legacy-shaped canonical pattern ID: {match.group(1)}",
                )
        relative_parts = path.relative_to(root).parts
        is_active_evaluation_input = (
            len(relative_parts) > 1
            and relative_parts[0] == "evaluations"
            and (
                relative_parts[1] in {"contracts", "pi-prompts"}
                or path.name.endswith("prompt.md")
            )
        )
        if is_active_evaluation_input:
            active_eval_legacy = re.compile(
                r"\b(?:d3|echarts|mermaid|threejs|slidev-echarts|slidev-animejs|ai)[a-z0-9-]*-pattern-[a-z0-9-]+\b"
            )
            for match in active_eval_legacy.finditer(content):
                line_number = content.count("\n", 0, match.start()) + 1
                add(
                    findings,
                    path,
                    f"line {line_number} uses a legacy pattern ID in an active evaluation: {match.group(0)}",
                )
    return observed, occurrences


def validate_d3_registry(root: Path, findings: list[Finding]) -> set[str]:
    reference_root = root / "skills" / "d3" / "references"
    patterns_root = reference_root / "patterns"
    index_path = reference_root / "pattern-index.md"
    expected: dict[str, str] = {}

    def register(pattern_id: str, route: str, path: Path) -> None:
        if pattern_id in expected:
            add(findings, path, f"duplicate D3 registry pattern ID: {pattern_id}")
        expected[pattern_id] = route

    for path in sorted(patterns_root.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        collection_sections = list(re.finditer(r"^##\s+(d3-[a-z0-9-]+)\s*$", content, re.MULTILINE))
        if collection_sections:
            for index, heading in enumerate(collection_sections):
                pattern_id = heading.group(1)
                section_end = collection_sections[index + 1].start() if index + 1 < len(collection_sections) else len(content)
                section = content[heading.end():section_end]
                declared_match = re.search(r"(?:\*\*)?Pattern ID(?:\*\*)?:?[^\n]*", section)
                declared_ids = re.findall(r"`(d3-[a-z0-9-]+)`", declared_match.group(0)) if declared_match else []
                source_match = re.search(r"\*\*Gallery source ID:\*\*\s*`([^`]+)`", section)
                if declared_ids != [pattern_id]:
                    add(findings, path, f"collection section {pattern_id} must declare only its heading Pattern ID")
                if source_match and ID_RE.fullmatch(source_match.group(1)):
                    canonical = f"d3-{source_match.group(1)}"
                    if pattern_id != canonical:
                        add(findings, path, f"collection section {pattern_id} does not match Gallery source ID {source_match.group(1)}")
                register(pattern_id, f"{path.name}#{pattern_id}", path)
            continue

        header = "\n".join(content.splitlines()[:15])
        declaration_match = re.search(r"(?:\*\*)?Pattern IDs?(?:\*\*)?:?[^\n]*", header)
        source_match = re.search(r"\*\*Gallery source ID:\*\*\s*`([^`]+)`", content)
        declared_ids = re.findall(r"`(d3-[a-z0-9-]+)`", declaration_match.group(0)) if declaration_match else []
        if not declared_ids:
            add(findings, path, "D3 pattern reference must declare at least one Pattern ID near the top")
            continue
        if source_match and ID_RE.fullmatch(source_match.group(1)):
            source_id = source_match.group(1)
            canonical = f"d3-{source_id}"
            if declared_ids != [canonical]:
                add(findings, path, f"gallery-backed D3 reference must declare only {canonical}")
            if path.stem != source_id:
                add(findings, path, f"D3 reference filename must match Gallery source ID {source_id}")
        for pattern_id in declared_ids:
            register(pattern_id, path.name, path)

    index_content = index_path.read_text(encoding="utf-8")
    rows = re.findall(
        r"^\|\s*`(d3-[^`]+)`\s*\|.*?\|\s*`references/patterns/([^`]+\.md(?:#d3-[a-z0-9-]+)?)`\s*\|\s*$",
        index_content,
        re.MULTILINE,
    )
    indexed: dict[str, str] = {}
    for pattern_id, filename in rows:
        if pattern_id in indexed:
            add(findings, index_path, f"duplicate D3 pattern-index ID: {pattern_id}")
        indexed[pattern_id] = filename
        expected_route = expected.get(pattern_id)
        if expected_route is None:
            add(findings, index_path, f"D3 pattern-index ID has no reference: {pattern_id}")
        elif expected_route != filename:
            add(findings, index_path, f"D3 pattern-index path mismatch for {pattern_id}: {filename}")

    missing = sorted(set(expected) - set(indexed))
    if missing:
        add(findings, index_path, f"D3 pattern index is missing {len(missing)} ID(s): {', '.join(missing[:8])}")
    if len(expected) != 242:
        add(findings, index_path, f"expected 242 canonical D3 registry IDs, found {len(expected)}")
    return set(expected)


def extract_block(content: str, start_marker: str, end_marker: str, path: Path, findings: list[Finding]) -> str:
    start = content.find(start_marker)
    if start < 0:
        add(findings, path, f"could not find pattern inventory marker: {start_marker}")
        return ""
    start += len(start_marker)
    end = content.find(end_marker, start)
    if end < 0:
        add(findings, path, f"could not find pattern inventory terminator after: {start_marker}")
        return ""
    return content[start:end]


def string_map(content: str, marker: str, path: Path, findings: list[Finding]) -> dict[str, str]:
    block = extract_block(content, marker, "])", path, findings)
    return dict(re.findall(r"\[\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\]", block))


def attribute(tag: str, name: str) -> str:
    match = re.search(rf'\b{re.escape(name)}="([^"]*)"', tag)
    return match.group(1) if match else ""


def kebab(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-")
    return value.lower()


def manifest_pattern_ids(
    path: Path,
    expected_namespace: str,
    findings: list[Finding],
) -> list[str]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        add(findings, path, f"could not load pattern manifest: {error}")
        return []

    if not isinstance(manifest, dict):
        add(findings, path, "pattern manifest must be a JSON object")
        return []

    namespace = manifest.get("namespace")
    if namespace != expected_namespace:
        add(
            findings,
            path,
            f"pattern manifest namespace must be {expected_namespace!r}, found {namespace!r}",
        )

    patterns = manifest.get("patterns")
    if not isinstance(patterns, list):
        add(findings, path, "pattern manifest must contain a patterns list")
        return []

    pattern_ids: list[str] = []
    for index, pattern in enumerate(patterns, start=1):
        if not isinstance(pattern, dict):
            add(findings, path, f"pattern manifest entry {index} must be an object")
            continue
        pattern_id = pattern.get("id")
        if not isinstance(pattern_id, str) or not pattern_id:
            add(findings, path, f"pattern manifest entry {index} must contain a non-empty string id")
            continue
        pattern_ids.append(pattern_id)

    if len(pattern_ids) != len(patterns):
        add(
            findings,
            path,
            f"pattern manifest ID parity mismatch: {len(pattern_ids)} IDs for {len(patterns)} patterns",
        )

    namespace_prefix = f"{expected_namespace}-"
    wrong_namespace = sorted(
        pattern_id for pattern_id in pattern_ids if not pattern_id.startswith(namespace_prefix)
    )
    if wrong_namespace:
        add(
            findings,
            path,
            f"pattern manifest IDs must use the {namespace_prefix} namespace: {', '.join(wrong_namespace[:8])}",
        )

    return pattern_ids


def register_family(
    family: str,
    ids: list[str],
    expected_count: int,
    path: Path,
    findings: list[Finding],
    global_ids: dict[str, str],
    review_ids: set[str],
    family_counts: dict[str, int],
) -> None:
    if len(ids) != expected_count:
        add(findings, path, f"{family} expected {expected_count} canonical IDs, found {len(ids)}")
    if len(set(ids)) != len(ids):
        duplicates = sorted({pattern_id for pattern_id in ids if ids.count(pattern_id) > 1})
        add(findings, path, f"{family} contains duplicate canonical IDs: {', '.join(duplicates[:8])}")
    for pattern_id in ids:
        validate_id(pattern_id, path, findings)
        if len(pattern_id) > REVIEW_ID_LENGTH:
            review_ids.add(pattern_id)
        owner = global_ids.get(pattern_id)
        if owner is not None and owner != family:
            add(findings, path, f"canonical ID collision between {owner} and {family}: {pattern_id}")
        global_ids[pattern_id] = family
    family_counts[family] = len(ids)


def validate_family_inventories(
    root: Path,
    d3_registry: set[str],
    findings: list[Finding],
) -> tuple[dict[str, int], set[str], set[str]]:
    global_ids: dict[str, str] = {}
    review_ids: set[str] = set()
    family_counts: dict[str, int] = {}

    d3_gallery_path = root / "skills/d3/assets/examples/d3-animated-svg/gallery.js"
    d3_gallery = d3_gallery_path.read_text(encoding="utf-8")
    d3_examples_block = extract_block(d3_gallery, "const examples = [", "\n  ];\n\n  function assignPatternIds", d3_gallery_path, findings)
    d3_sources = re.findall(r'\{\s*id:\s*"([a-z0-9-]+)"', d3_examples_block)
    if len(d3_sources) != 225 or len(set(d3_sources)) != 225:
        add(findings, d3_gallery_path, f"D3 gallery must expose 225 unique source IDs, found {len(set(d3_sources))}")
    missing_d3_sources = sorted({f"d3-{source_id}" for source_id in d3_sources} - d3_registry)
    if missing_d3_sources:
        add(findings, d3_gallery_path, f"D3 gallery IDs missing from registry: {', '.join(missing_d3_sources[:8])}")
    register_family("d3-base", sorted(d3_registry), 242, d3_gallery_path, findings, global_ids, review_ids, family_counts)
    register_family("d3-cs1", [f"d3-{source_id}-cs1" for source_id in d3_sources], 225, d3_gallery_path, findings, global_ids, review_ids, family_counts)
    register_family("d3-cs2", [f"d3-{source_id}-cs2" for source_id in d3_sources], 225, d3_gallery_path, findings, global_ids, review_ids, family_counts)

    composition_path = d3_gallery_path.with_name("composition-sheets.js")
    composition_content = composition_path.read_text(encoding="utf-8")
    composition_block = extract_block(
        composition_content,
        "const curatedCompositionVariantIds = new Set([",
        "]);\n  const curatedVariantOrder",
        composition_path,
        findings,
    )
    composition_ids = re.findall(r'"(d3-composition-[a-z0-9-]+)"', composition_block)
    register_family("d3-composition", composition_ids, 78, composition_path, findings, global_ids, review_ids, family_counts)

    logo_manifest_path = root / "skills/d3/assets/catalog/logo-manifest.json"
    try:
        logo_manifest = json.loads(logo_manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        add(findings, logo_manifest_path, f"could not load D3 logo manifest: {error}")
        logo_manifest = {}
    logo_ids = [str(item.get("id", "")) for item in logo_manifest.get("patterns", []) if isinstance(item, dict)]
    logo_texture_ids = [str(item.get("id", "")) for item in logo_manifest.get("textures", []) if isinstance(item, dict)]
    register_family("d3-logo", logo_ids, 90, logo_manifest_path, findings, global_ids, review_ids, family_counts)
    register_family(
        "d3-logo-textures",
        logo_texture_ids,
        40,
        logo_manifest_path,
        findings,
        global_ids,
        review_ids,
        family_counts,
    )

    echarts_path = root / "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/index.html"
    echarts_content = echarts_path.read_text(encoding="utf-8")
    echarts_tags = re.findall(r'<article class="chart-card[^>]+>', echarts_content)
    echarts_ids: list[str] = []
    for tag in echarts_tags:
        pattern_id = attribute(tag, "data-pattern-id")
        echarts_ids.append(pattern_id)
        if attribute(tag, "id") != pattern_id:
            add(findings, echarts_path, f"ECharts card DOM id must equal data-pattern-id: {pattern_id}")
        if not attribute(tag, "data-example-id") or attribute(tag, "data-example-id") == "echarts-animated-svg":
            add(findings, echarts_path, f"ECharts card must expose a local data-example-id: {pattern_id}")
        legacy_id = attribute(tag, "data-legacy-pattern-id")
        if legacy_id and legacy_id == pattern_id:
            add(findings, echarts_path, f"ECharts legacy alias equals canonical ID: {pattern_id}")
    register_family("echarts", echarts_ids, 43, echarts_path, findings, global_ids, review_ids, family_counts)

    mermaid_manifest_path = (
        root / "skills/mermaid/assets/examples/mermaid-max-complexity/gallery.json"
    )
    mermaid_ids = manifest_pattern_ids(mermaid_manifest_path, "mermaid", findings)
    register_family(
        "mermaid",
        mermaid_ids,
        62,
        mermaid_manifest_path,
        findings,
        global_ids,
        review_ids,
        family_counts,
    )

    plant_root = root / "skills/plantuml-colorset-renderer/assets/examples"
    for directory, suffix, family in (
        ("plantuml-colorset-renderer", "cs2", "plantuml-cs2"),
        ("plantuml-colorset-renderer-cs1", "cs1", "plantuml-cs1"),
    ):
        gallery_path = plant_root / directory / "plantuml-gallery.js"
        gallery_content = gallery_path.read_text(encoding="utf-8")
        coverage_path = gallery_path.with_name("coverage.json")
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        slug_map = string_map(gallery_content, "const patternSlugs = new Map([", gallery_path, findings)
        plant_ids = [f"plantuml-{slug_map.get(item['id'], item['id'])}-{suffix}" for item in coverage["items"]]
        register_family(family, plant_ids, 28, gallery_path, findings, global_ids, review_ids, family_counts)
        if 'legacyPatternId === patternIdFor(example) ? "" : legacyPatternId' not in gallery_content:
            add(findings, gallery_path, "PlantUML must omit legacy aliases that equal the canonical ID")

    three_path = root / "skills/threejs-animated-3d/assets/examples/threejs-animated-3d/src/main.js"
    three_content = three_path.read_text(encoding="utf-8")
    three_slug_map = string_map(three_content, "const PATTERN_SLUGS = new Map([", three_path, findings)
    three_block = extract_block(three_content, "const examples = [", "\n]\n\nconst gallery", three_path, findings)
    three_sources = re.findall(r"\bid:\s*'([a-z0-9-]+)'", three_block)
    three_ids = [f"threejs-{three_slug_map.get(source_id, source_id)}" for source_id in three_sources]
    register_family("threejs", three_ids, 24, three_path, findings, global_ids, review_ids, family_counts)

    slidev_echarts_root = root / "skills/slidev-echarts/assets/examples/slidev-echarts"
    chart_lab_path = slidev_echarts_root / "lib" / "chart-lab.js"
    chart_lab = chart_lab_path.read_text(encoding="utf-8")
    chart_block = extract_block(chart_lab, "export const chartSpecs = {", "\n}\n\nexport const chartOrder", chart_lab_path, findings)
    chart_sources = re.findall(r"^\s{2}([A-Za-z][A-Za-z0-9]*):\s*\{", chart_block, re.MULTILINE)
    chart_component_path = slidev_echarts_root / "components" / "ChartTypeSlide.vue"
    chart_component = chart_component_path.read_text(encoding="utf-8")
    chart_slug_map = string_map(chart_component, "const publicChartSlugs = new Map([", chart_component_path, findings)
    if ':data-example-id="sourceSlug"' not in chart_component:
        add(findings, chart_component_path, "Slidev ECharts chart items must preserve the local source slug in data-example-id")
    chart_ids = [f"slidev-echarts-{chart_slug_map.get(kebab(source_id), kebab(source_id))}" for source_id in chart_sources]
    slidev_echarts_ids = [
        *chart_ids,
        "slidev-echarts-executive-dashboard",
        "slidev-echarts-market-mix",
        "slidev-echarts-revenue-story",
        "slidev-echarts-spotlight",
        "slidev-echarts-comparison",
        "slidev-echarts-svg-path",
        "slidev-echarts-svg-particles",
        "slidev-echarts-svg-bands",
        "slidev-echarts-svg-glyphs",
    ]
    register_family("slidev-echarts", slidev_echarts_ids, 32, chart_component_path, findings, global_ids, review_ids, family_counts)
    for filename in (
        "ChartTypeSlide.vue",
        "CompositionScene.vue",
        "GeneratedSvgMotion.vue",
        "ExecutiveDashboard.vue",
        "MarketMixChart.vue",
        "RevenueStory.vue",
    ):
        component_path = slidev_echarts_root / "components" / filename
        if 'data-example-id="slidev-echarts"' in component_path.read_text(encoding="utf-8"):
            add(findings, component_path, "item surfaces must use a local data-example-id, not the page-set ID")

    slidev_anime_root = root / "skills/slidev-animejs/assets/examples/slidev-animejs"
    anime_demo_path = slidev_anime_root / "lib" / "anime-demos.js"
    anime_demos = anime_demo_path.read_text(encoding="utf-8")
    feature_block = extract_block(anime_demos, "export const featureOrder = [", "]", anime_demo_path, findings)
    feature_ids = re.findall(r"'([a-z0-9-]+)'", feature_block)
    svg_asset_path = (
        root
        / "skills/slidev-animejs/assets/templates/slidev-svg-asset-pack/lib/svg-assets.js"
    )
    svg_assets = svg_asset_path.read_text(encoding="utf-8")
    asset_block = extract_block(svg_assets, "export const svgAssetOrder = [", "]", svg_asset_path, findings)
    asset_ids = re.findall(r"'([a-z0-9-]+)'", asset_block)
    slidev_anime_ids = [f"slidev-animejs-{source_id}" for source_id in [*feature_ids, *asset_ids]]
    register_family("slidev-animejs", slidev_anime_ids, 27, anime_demo_path, findings, global_ids, review_ids, family_counts)
    for filename in ("AnimeFeatureSlide.vue", "SvgAssetSlide.vue"):
        component_path = slidev_anime_root / "components" / filename
        if 'data-example-id="slidev-animejs"' in component_path.read_text(encoding="utf-8"):
            add(findings, component_path, "item surfaces must use a local data-example-id, not the page-set ID")

    ai_path = root / "skills/html-d3-anime-video-workflow/assets/examples/ai-concept-videos/concepts.js"
    ai_content = ai_path.read_text(encoding="utf-8")
    ai_ids = re.findall(r'^\s*patternId:\s*"(ai-[a-z0-9-]+)"', ai_content, re.MULTILINE)
    register_family("ai-concepts", ai_ids, 11, ai_path, findings, global_ids, review_ids, family_counts)
    ai_index_path = ai_path.with_name("index.html")
    ai_main_match = re.search(r'<main[^>]+data-example-id="([^"]+)"[^>]+data-pattern-id="([^"]+)"', ai_index_path.read_text(encoding="utf-8"))
    if not ai_main_match or ai_main_match.group(1) == "ai-concept-videos":
        add(findings, ai_index_path, "AI concept item surface must use the local concept ID")

    procedural_manifest_path = root / "skills/procedural-svg-animation/assets/pattern-specs.json"
    procedural_ids = manifest_pattern_ids(procedural_manifest_path, "procedural-svg", findings)
    register_family(
        "procedural-svg",
        procedural_ids,
        66,
        procedural_manifest_path,
        findings,
        global_ids,
        review_ids,
        family_counts,
    )

    return family_counts, review_ids, set(global_ids)


def require_contracts(root: Path, findings: list[Finding]) -> None:
    contracts = (
        (
            "skills/d3/assets/examples/d3-animated-svg/gallery.js",
            r"`d3-\$\{example\.id\}`",
            "D3 gallery must derive base IDs as d3-<source>",
        ),
        (
            "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/scripts/build-gallery.mjs",
            r"`echarts-\$\{patternSlug\}`",
            "ECharts gallery must derive IDs as echarts-<slug>",
        ),
        (
            "skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/plantuml-gallery.js",
            r"`plantuml-\$\{patternSlugs\.get\(example\.id\) \|\| example\.id\}\$\{patternSuffix\}`",
            "PlantUML gallery must append the style suffix to plantuml-<slug>",
        ),
        (
            "skills/threejs-animated-3d/assets/examples/threejs-animated-3d/src/main.js",
            r"`threejs-\$\{PATTERN_SLUGS\.get\(example\.id\) \|\| example\.id\}`",
            "Three.js gallery must derive IDs as threejs-<slug>",
        ),
        (
            "skills/slidev-echarts/assets/examples/slidev-echarts/components/CompositionScene.vue",
            r"`slidev-echarts-\$\{scene\}`",
            "Slidev ECharts compositions must omit the redundant composition segment",
        ),
        (
            "skills/slidev-animejs/assets/examples/slidev-animejs/components/AnimeFeatureSlide.vue",
            r"`slidev-animejs-\$\{spec\.type\}`",
            "Slidev Anime.js features must omit the redundant feature segment",
        ),
    )
    for relative_path, pattern, message in contracts:
        path = root / relative_path
        if not path.exists():
            add(findings, path, "pattern-ID contract source is missing")
            continue
        if not re.search(pattern, path.read_text(encoding="utf-8")):
            add(findings, path, message)


def validate_pattern_ids(root: Path) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    observed, explicit_occurrences = collect_explicit_ids(root, findings)
    d3_registry = validate_d3_registry(root, findings)
    family_counts, family_review_ids, canonical_item_ids = validate_family_inventories(root, d3_registry, findings)
    require_contracts(root, findings)
    explicit_review_ids = {pattern_id for pattern_id in observed if len(pattern_id) > REVIEW_ID_LENGTH}
    return findings, {
        "explicit_occurrences": explicit_occurrences,
        "unique_explicit_ids": len(observed),
        "canonical_item_ids": sum(family_counts.values()),
        "max_canonical_length": max((len(pattern_id) for pattern_id in canonical_item_ids), default=0),
        "review_threshold_ids": len(explicit_review_ids | family_review_ids),
    }


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate canonical public pattern IDs across skills.")
    parser.add_argument("--root", type=Path, default=repo_root(), help="Repository root to validate.")
    args = parser.parse_args()
    root = args.root.resolve()
    findings, stats = validate_pattern_ids(root)
    if findings:
        print(f"Pattern ID validation failed with {len(findings)} finding(s):")
        for finding in findings:
            print(f"- {relative(finding.path, root)}: {finding.message}")
        return 1
    print(
        "Pattern ID validation passed: "
        f"{stats['canonical_item_ids']} canonical item IDs across families, "
        f"maximum length {stats['max_canonical_length']}, "
        f"{stats['unique_explicit_ids']} explicit canonical IDs, "
        f"{stats['explicit_occurrences']} source declarations, "
        f"{stats['review_threshold_ids']} IDs above the {REVIEW_ID_LENGTH}-character review threshold."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
