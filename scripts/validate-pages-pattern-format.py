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
DOCS = ROOT / "docs"


class AttributeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.body: dict[str, str] | None = None
        self.cards: list[dict[str, str]] = []
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        if tag == "body" and self.body is None:
            self.body = attributes
        if tag == "a" and "data-example-id" in attributes:
            self.cards.append(attributes)
        if tag == "meta" and "name" in attributes and "content" in attributes:
            self.meta[attributes["name"]] = attributes["content"]


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


def main() -> int:
    catalog_path = DOCS / "example-catalog.json"
    index_path = DOCS / "index.html"
    if not catalog_path.exists() or not index_path.exists():
        fail("run uv run --script scripts/build-pages.py before validating Pages output")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(catalog, list) or not catalog:
        fail("example-catalog.json must contain a non-empty list")

    ids = [entry.get("id") for entry in catalog]
    if len(ids) != len(set(ids)):
        fail("example-catalog.json contains duplicate ids")

    root = parse_html(index_path)
    require_attr(root.body, "data-example-id", "codex-skills-examples", "docs/index.html")
    require_attr(root.body, "data-pattern-id", "codex-skills-examples", "docs/index.html")
    require_attr(root.body, "data-pattern-page", "catalog", "docs/index.html")

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
            fail(f"docs/index.html is missing a card for {example_id}")
        if card.get("data-pattern-id") != example_id:
            fail(f"docs/index.html card {example_id} is missing matching data-pattern-id")

        href = entry.get("href")
        if not isinstance(href, str) or not href.startswith("examples/"):
            fail(f"catalog entry {example_id} has invalid href {href!r}")
        page_path = DOCS / href / "index.html"
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

    print(f"Validated {len(catalog)} published Pages entries with stable pattern-page metadata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
