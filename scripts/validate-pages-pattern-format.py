#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES_ROOT = ROOT / "dist" / "pages"


class AttributeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.body: dict[str, str] | None = None
        self.cards: list[dict[str, str]] = []
        self.icons: list[dict[str, str]] = []
        self.theme_controls: list[dict[str, str]] = []
        self.capability_controls: list[dict[str, str]] = []
        self.d3_capabilities: list[dict[str, str]] = []
        self.d3_gallery_links: list[dict[str, str]] = []
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        if tag == "body" and self.body is None:
            self.body = attributes
        if tag == "a" and "data-example-id" in attributes:
            self.cards.append(attributes)
        if "data-theme" in attributes:
            self.theme_controls.append(attributes)
        if "data-capability-filter" in attributes:
            self.capability_controls.append(attributes)
        if "data-capability-id" in attributes:
            self.d3_capabilities.append(attributes)
        if tag == "a" and "data-gallery-id" in attributes:
            self.d3_gallery_links.append(attributes)
        if tag == "meta" and "name" in attributes and "content" in attributes:
            self.meta[attributes["name"]] = attributes["content"]
        if tag == "link" and "icon" in attributes.get("rel", "").lower().split():
            self.icons.append(attributes)


def parse_html(path: Path) -> AttributeParser:
    parser = AttributeParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def fail(message: str) -> None:
    print(f"Pages pattern format validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_attr(attrs: dict[str, str] | None, name: str, value: str, context: str) -> None:
    if attrs is None:
        fail(f"{context} is missing a <body> tag")
    actual = attrs.get(name)
    if actual != value:
        fail(f"{context} expected {name}={value!r}, found {actual!r}")


def require_nonempty_attr(attrs: dict[str, str] | None, name: str, context: str) -> None:
    if attrs is None:
        fail(f"{context} is missing a <body> tag")
    actual = attrs.get(name)
    if not actual:
        fail(f"{context} is missing non-empty {name}")


def validate_unified_plantuml(catalog: list[dict[str, object]]) -> None:
    canonical_id = "plantuml-colorset-renderer"
    legacy_id = "plantuml-colorset-renderer-cs1"
    plantuml_entries = [
        entry.get("id") for entry in catalog if str(entry.get("id", "")).startswith("plantuml-")
    ]
    if plantuml_entries != [canonical_id]:
        fail(f"PlantUML must have exactly one catalog entry ({canonical_id}), found {plantuml_entries}")

    canonical_path = PAGES_ROOT / "examples" / canonical_id / "index.html"
    public_plantuml_pages: list[Path] = []
    for index_path in (PAGES_ROOT / "examples").rglob("index.html"):
        page = parse_html(index_path)
        if (
            page.body
            and page.body.get("data-pattern-page") == "true"
            and "plantuml" in index_path.as_posix().lower()
        ):
            public_plantuml_pages.append(index_path)
    if public_plantuml_pages != [canonical_path]:
        rendered = [path.relative_to(PAGES_ROOT).as_posix() for path in public_plantuml_pages]
        fail(f"PlantUML must expose exactly one pattern page, found {rendered}")

    canonical_page = parse_html(canonical_path)
    theme_ids = {control.get("data-theme") for control in canonical_page.theme_controls}
    if theme_ids != {"colorset1", "colorset2"}:
        fail(f"unified PlantUML page must expose Colorset 1 and Colorset 2 controls, found {sorted(theme_ids)}")
    expected_capabilities = {
        "all",
        "uml-behavior",
        "architecture-network",
        "data-notation",
        "planning-structure",
        "visual-specialist",
    }
    capability_ids = {control.get("data-capability-filter") for control in canonical_page.capability_controls}
    if capability_ids != expected_capabilities:
        fail(f"unified PlantUML page has incomplete capability controls: {sorted(capability_ids)}")

    legacy_root = PAGES_ROOT / "examples" / legacy_id
    for theme_root, expected_colorset in (
        (canonical_path.parent, "colorset2"),
        (legacy_root, "colorset1"),
    ):
        coverage_path = theme_root / "coverage.json"
        report_path = theme_root / "render-report.json"
        if not coverage_path.exists() or not report_path.exists():
            fail(f"PlantUML {expected_colorset} assets are missing coverage.json or render-report.json")
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if coverage.get("colorset") != expected_colorset or coverage.get("itemCount") != 28:
            fail(f"PlantUML {expected_colorset} coverage must contain exactly 28 items")
        if report.get("colorset") != expected_colorset or report.get("ok") is not True:
            fail(f"PlantUML {expected_colorset} render report must be successful")

    legacy_path = legacy_root / "index.html"
    legacy_page = parse_html(legacy_path)
    require_attr(legacy_page.body, "data-legacy-redirect", legacy_id, legacy_path.relative_to(ROOT).as_posix())
    if legacy_page.body and legacy_page.body.get("data-pattern-page"):
        fail("legacy PlantUML CS1 route must redirect rather than expose a second pattern page")
    legacy_text = legacy_path.read_text(encoding="utf-8")
    if "../plantuml-colorset-renderer/" not in legacy_text or "theme\", \"colorset1" not in legacy_text:
        fail("legacy PlantUML CS1 route must preserve links by redirecting to the unified Colorset 1 view")


def validate_unified_d3(catalog: list[dict[str, object]]) -> None:
    canonical_id = "d3"
    legacy_ids = {
        "d3-animated-svg",
        "d3-animated-svg-cs1",
        "d3-animated-svg-colorset2",
        "d3-logo-design",
        "d3-logo-textures",
    }
    d3_entries = [
        entry.get("id")
        for entry in catalog
        if entry.get("id") == canonical_id or str(entry.get("id", "")).startswith("d3-")
    ]
    if d3_entries != [canonical_id]:
        fail(f"D3 must have exactly one catalog entry ({canonical_id}), found {d3_entries}")

    canonical_path = PAGES_ROOT / "examples" / canonical_id / "index.html"
    page = parse_html(canonical_path)
    context = canonical_path.relative_to(ROOT).as_posix()
    require_attr(page.body, "data-page-kind", "skill-hub", context)
    require_attr(page.body, "data-capability-count", "8", context)
    require_attr(page.body, "data-gallery-link-count", "6", context)

    expected_capabilities = {
        "quantitative-charts",
        "networks-flows",
        "maps-spatial",
        "motion-interaction",
        "ai-system-explainers",
        "composition-audit",
        "logos-textures",
        "portable-output",
    }
    capability_ids = {item.get("data-capability-id") for item in page.d3_capabilities}
    if capability_ids != expected_capabilities or len(page.d3_capabilities) != len(expected_capabilities):
        fail(f"unified D3 hub has incomplete or duplicate capabilities: {sorted(capability_ids)}")

    expected_galleries = {
        "patterns": "../d3-animated-svg/",
        "colorset1": "../d3-animated-svg-cs1/",
        "colorset2": "../d3-animated-svg-colorset2/",
        "compositions": "../d3-animated-svg/composition-sheets.html",
        "logos": "../d3-logo-design/",
        "textures": "../d3-logo-textures/",
    }
    gallery_links = {
        item.get("data-gallery-id"): item.get("href") for item in page.d3_gallery_links
    }
    if gallery_links != expected_galleries or len(page.d3_gallery_links) != len(expected_galleries):
        fail(f"unified D3 hub has incomplete or duplicate focused gallery links: {gallery_links}")
    for gallery_id, href in gallery_links.items():
        target = (canonical_path.parent / str(href)).resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            fail(f"unified D3 hub link {gallery_id} has no generated target: {href}")

    for legacy_id in legacy_ids:
        legacy_path = PAGES_ROOT / "examples" / legacy_id / "index.html"
        if not legacy_path.is_file():
            fail(f"legacy D3 route was not preserved: {legacy_path.relative_to(ROOT).as_posix()}")


def main() -> int:
    catalog_path = PAGES_ROOT / "example-catalog.json"
    index_path = PAGES_ROOT / "index.html"
    if not catalog_path.exists() or not index_path.exists():
        fail("run uv run --script scripts/build-pages.py before validating Pages output")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(catalog, list) or not catalog:
        fail("example-catalog.json must contain a non-empty list")

    ids = [entry.get("id") for entry in catalog]
    if len(ids) != len(set(ids)):
        fail("example-catalog.json contains duplicate ids")

    root = parse_html(index_path)
    require_attr(root.body, "data-example-id", "codex-skills-examples", "dist/pages/index.html")
    require_attr(root.body, "data-pattern-id", "codex-skills-examples", "dist/pages/index.html")
    require_attr(root.body, "data-pattern-page", "catalog", "dist/pages/index.html")
    if not root.icons or not root.icons[0].get("href"):
        fail("dist/pages/index.html is missing a non-empty favicon link")

    root_cards = {card.get("data-example-id"): card for card in root.cards}
    for entry in catalog:
        example_id = entry.get("id")
        if not isinstance(example_id, str) or not example_id:
            fail("catalog entries must have an id")
        if entry.get("patternId") != example_id:
            fail(f"catalog entry {example_id} must expose patternId equal to its id")
        if entry.get("pageFormat") != "pattern-gallery":
            fail(f"catalog entry {example_id} must expose pageFormat='pattern-gallery'")
        card = root_cards.get(example_id)
        if card is None:
            fail(f"dist/pages/index.html is missing a card for {example_id}")
        if card.get("data-pattern-id") != example_id:
            fail(f"dist/pages/index.html card {example_id} is missing matching data-pattern-id")

        href = entry.get("href")
        if not isinstance(href, str) or not href.startswith("examples/"):
            fail(f"catalog entry {example_id} has invalid href {href!r}")
        page_path = PAGES_ROOT / href / "index.html"
        if not page_path.exists():
            fail(f"published page is missing: {page_path.relative_to(ROOT).as_posix()}")
        page = parse_html(page_path)
        context = page_path.relative_to(ROOT).as_posix()
        require_attr(page.body, "data-example-id", example_id, context)
        require_nonempty_attr(page.body, "data-pattern-id", context)
        require_attr(page.body, "data-pattern-page", "true", context)
        if page.meta.get("example-id") != example_id:
            fail(f"{context} is missing meta example-id={example_id!r}")
        if page.meta.get("pattern-id") != example_id:
            fail(f"{context} is missing meta pattern-id={example_id!r}")
        if page.meta.get("pattern-page") != "true":
            fail(f"{context} is missing meta pattern-page='true'")
        if not page.icons or not page.icons[0].get("href"):
            fail(f"{context} is missing a non-empty favicon link")

    validate_unified_d3(catalog)
    validate_unified_plantuml(catalog)

    print(f"Validated {len(catalog)} published Pages entries with stable pattern-page metadata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
