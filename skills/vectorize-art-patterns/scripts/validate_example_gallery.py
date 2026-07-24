#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the published vectorize-art-patterns colorset gallery."""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any
import xml.etree.ElementTree as ET


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_EXAMPLE_ROOT = (
    SKILL_ROOT / "assets" / "examples" / "vectorize-art-patterns"
)
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")
sys.dont_write_bytecode = True


class GalleryValidationError(RuntimeError):
    """Raised when the published acceptance gallery violates its contract."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise GalleryValidationError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_module("validate_art_svg", SCRIPT_DIR / "validate_art_svg.py")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def geometry_sha256(svg: Path) -> str:
    root = ET.fromstring(svg.read_text(encoding="utf-8"))
    paths = [
        element.get("d", "")
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "path"
    ]
    payload = {"viewBox": root.get("viewBox", ""), "paths": paths}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GalleryValidationError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise GalleryValidationError(f"Expected a JSON object: {path}")
    return payload


def resolve_inside(root: Path, relative: Any, field: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise GalleryValidationError(f"Manifest field {field} must be a path")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise GalleryValidationError(
            f"Manifest field {field} escapes the gallery root: {relative}"
        ) from exc
    if not candidate.is_file():
        raise GalleryValidationError(f"Manifest file is missing: {relative}")
    return candidate


class GalleryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.body: dict[str, str | None] = {}
        self.articles: dict[str, dict[str, Any]] = {}
        self.id_counts: dict[str, int] = {}
        self.colorset_buttons: set[str] = set()
        self.local_assets: set[str] = set()
        self.current_article: str | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.id_counts[element_id] = self.id_counts.get(element_id, 0) + 1
        if tag == "meta" and values.get("name") and values.get("content"):
            self.meta[str(values["name"])] = str(values["content"])
        if tag == "body":
            self.body = values
        if tag == "article":
            article_id = values.get("id")
            if not article_id:
                raise GalleryValidationError("Every gallery article needs an id")
            self.current_article = article_id
            self.articles[article_id] = {
                "attrs": values,
                "images": [],
                "links": [],
            }
        if tag == "img" and self.current_article:
            self.articles[self.current_article]["images"].append(values)
        if tag == "a" and self.current_article and values.get("href"):
            self.articles[self.current_article]["links"].append(values)
        if tag == "button" and values.get("data-colorset-choice"):
            self.colorset_buttons.add(str(values["data-colorset-choice"]))
        if tag == "link" and values.get("rel") == "stylesheet" and values.get("href"):
            self.local_assets.add(str(values["href"]))
        if tag == "script" and values.get("src"):
            self.local_assets.add(str(values["src"]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "article":
            self.current_article = None


def validate_gallery(example_root: Path) -> dict[str, Any]:
    manifest_path = example_root / "manifest.json"
    index_path = example_root / "index.html"
    manifest = load_json(manifest_path)
    if manifest.get("schemaVersion") != 1:
        raise GalleryValidationError("Manifest schemaVersion must be 1")
    if manifest.get("pageId") != "vectorize-art-patterns":
        raise GalleryValidationError("Manifest pageId is incorrect")
    if manifest.get("namespace") != "vectorize":
        raise GalleryValidationError("Manifest namespace must be vectorize")
    patterns = manifest.get("patterns")
    if not isinstance(patterns, list) or len(patterns) != 8:
        raise GalleryValidationError("Manifest must contain exactly eight patterns")
    if (
        manifest.get("patternCount") != 8
        or manifest.get("basePatternCount") != 4
    ):
        raise GalleryValidationError("Manifest pattern counts are incorrect")
    expected_contract_sha = sha256_path(
        SKILL_ROOT / "assets" / "palettes" / "colorsets.json"
    )
    if manifest.get("colorsetContractSha256") != expected_contract_sha:
        raise GalleryValidationError("Manifest colorset contract hash is stale")

    parser = GalleryParser()
    parser.feed(index_path.read_text(encoding="utf-8"))
    if parser.meta.get("example-id") != "vectorize-art-patterns":
        raise GalleryValidationError("Page example-id metadata is incorrect")
    if parser.meta.get("pattern-id") != "vectorize-art-patterns":
        raise GalleryValidationError("Page pattern-id metadata is incorrect")
    if parser.meta.get("pattern-page") != "true":
        raise GalleryValidationError("Page pattern-page metadata is missing")
    if parser.body.get("data-colorset") != "colorset2":
        raise GalleryValidationError("Page default colorset must be colorset2")
    if parser.colorset_buttons != {"colorset1", "colorset2"}:
        raise GalleryValidationError("Page colorset controls are incomplete")
    if parser.local_assets != {"gallery.css", "gallery.js"}:
        raise GalleryValidationError("Page local CSS/JS asset contract is incorrect")
    duplicates = sorted(
        element_id for element_id, count in parser.id_counts.items() if count != 1
    )
    if duplicates:
        raise GalleryValidationError(f"Duplicate page element IDs: {duplicates}")

    union_allowed = set()
    for name in ("colorset1", "colorset2"):
        colorset = manifest.get("colorsets", {}).get(name)
        if not isinstance(colorset, dict) or not isinstance(
            colorset.get("allowed"), list
        ):
            raise GalleryValidationError(f"Manifest is missing {name}")
        union_allowed.update(str(value).lower() for value in colorset["allowed"])
    source_text = "\n".join(
        (example_root / filename).read_text(encoding="utf-8")
        for filename in ("index.html", "gallery.css", "gallery.js")
    )
    unexpected_page_colors = sorted(
        {token.lower() for token in HEX_RE.findall(source_text)} - union_allowed
    )
    if unexpected_page_colors:
        raise GalleryValidationError(
            f"Gallery page uses colors outside both contracts: {unexpected_page_colors}"
        )

    ids: set[str] = set()
    example_variants: dict[str, dict[str, str]] = {}
    expected_svgs: set[str] = set()
    expected_reports: set[str] = set()
    colorset_counts = {"colorset1": 0, "colorset2": 0}
    loaded_tokens: set[str] = set()
    for item in patterns:
        if not isinstance(item, dict):
            raise GalleryValidationError("Every manifest pattern must be an object")
        pattern_id = item.get("id")
        if (
            not isinstance(pattern_id, str)
            or not ID_RE.fullmatch(pattern_id)
            or not pattern_id.startswith("vectorize-")
        ):
            raise GalleryValidationError(f"Invalid pattern ID: {pattern_id!r}")
        if pattern_id in ids:
            raise GalleryValidationError(f"Duplicate manifest ID: {pattern_id}")
        ids.add(pattern_id)
        colorset = item.get("colorset")
        variant = item.get("variant")
        expected_variant = {
            "colorset1": "cs1",
            "colorset2": "cs2",
        }.get(colorset)
        if expected_variant is None or variant != expected_variant:
            raise GalleryValidationError(
                f"Colorset/variant mismatch for {pattern_id}"
            )
        if not pattern_id.endswith(f"-{variant}"):
            raise GalleryValidationError(
                f"Pattern ID variant suffix mismatch: {pattern_id}"
            )
        colorset_counts[colorset] += 1

        svg = resolve_inside(example_root, item.get("svg"), "svg")
        report_path = resolve_inside(example_root, item.get("report"), "report")
        expected_svgs.add(svg.name)
        expected_reports.add(report_path.name)
        if item.get("sha256") != sha256_path(svg):
            raise GalleryValidationError(f"SVG hash mismatch: {pattern_id}")
        if item.get("bytes") != svg.stat().st_size:
            raise GalleryValidationError(f"SVG byte count mismatch: {pattern_id}")
        if item.get("geometrySha256") != geometry_sha256(svg):
            raise GalleryValidationError(f"Geometry hash mismatch: {pattern_id}")
        report = load_json(report_path)
        inspection = validator.inspect_svg(svg)
        if (
            inspection["pattern_id"] != pattern_id
            or inspection["colorset"] != colorset
            or inspection["unexpected_color_tokens"]
        ):
            raise GalleryValidationError(
                f"SVG structural/colorset validation failed: {pattern_id}"
            )
        comparisons = {
            "output_sha256": item["sha256"],
            "pattern_id": pattern_id,
            "mode": item["mode"],
            "tile": item["tile"],
            "colorset": colorset,
            "path_count": item["pathCount"],
            "contour_count": item["contourCount"],
            "point_count": item["pointCount"],
            "palette": item["palette"],
        }
        for key, expected in comparisons.items():
            if report.get(key) != expected:
                raise GalleryValidationError(
                    f"Report field {key} mismatch for {pattern_id}"
                )
        loaded_tokens.update(inspection["visible_color_tokens"])

        article = parser.articles.get(pattern_id)
        if article is None:
            raise GalleryValidationError(f"Page article missing: {pattern_id}")
        attrs = article["attrs"]
        if (
            attrs.get("data-pattern-id") != pattern_id
            or attrs.get("data-example-id") != item.get("exampleId")
            or attrs.get("data-colorset") != colorset
        ):
            raise GalleryValidationError(f"Page article metadata mismatch: {pattern_id}")
        hidden = "hidden" in attrs
        if hidden != (colorset == "colorset1"):
            raise GalleryValidationError(
                f"Default page visibility mismatch: {pattern_id}"
            )
        image_sources = {
            str(image.get("src")) for image in article["images"] if image.get("src")
        }
        if image_sources != {item["svg"]}:
            raise GalleryValidationError(f"Page SVG image mismatch: {pattern_id}")
        download_links = {
            str(link.get("href"))
            for link in article["links"]
            if "download" in link
        }
        if download_links != {item["svg"]}:
            raise GalleryValidationError(f"Page download link mismatch: {pattern_id}")
        example_variants.setdefault(str(item["exampleId"]), {})[colorset] = str(
            item["geometrySha256"]
        )

    if set(parser.articles) != ids:
        raise GalleryValidationError("Page and manifest pattern IDs are not in parity")
    if colorset_counts != {"colorset1": 4, "colorset2": 4}:
        raise GalleryValidationError(f"Colorset counts are wrong: {colorset_counts}")
    for example_id, variants in example_variants.items():
        if set(variants) != {"colorset1", "colorset2"}:
            raise GalleryValidationError(
                f"Missing paired colorset variant: {example_id}"
            )
        if variants["colorset1"] != variants["colorset2"]:
            raise GalleryValidationError(
                f"Colorset geometry differs for {example_id}"
            )

    actual_svgs = {
        path.name for path in (example_root / "svgs").glob("*.svg")
    }
    actual_reports = {
        path.name for path in (example_root / "reports").glob("*.json")
    }
    if actual_svgs != expected_svgs or actual_reports != expected_reports:
        raise GalleryValidationError("Published SVG/report inventory has stale files")

    return {
        "schema_version": 1,
        "ok": True,
        "page_id": "vectorize-art-patterns",
        "base_pattern_count": len(example_variants),
        "pattern_count": len(ids),
        "colorset_counts": colorset_counts,
        "unique_geometry_count": len(
            {item["geometrySha256"] for item in patterns}
        ),
        "visible_color_token_count": len(loaded_tokens),
        "page_article_count": len(parser.articles),
        "manifest_sha256": sha256_path(manifest_path),
        "colorset_contract_sha256": expected_contract_sha,
    }


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the vectorize-art-patterns Pages gallery."
    )
    parser.add_argument(
        "--example-root",
        type=Path,
        default=DEFAULT_EXAMPLE_ROOT,
    )
    parser.add_argument("--output-report", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_gallery(args.example_root.resolve())
    if args.output_report:
        write_json_atomic(args.output_report.resolve(), result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GalleryValidationError as exc:
        print(f"[vectorize-art-patterns] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
