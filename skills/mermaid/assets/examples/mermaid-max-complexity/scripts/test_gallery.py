#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Regression tests for the Mermaid maximum-complexity gallery."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
GALLERY_DIR = SCRIPT_DIR.parent
SKILL_DIR = Path(__file__).resolve().parents[4]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("mermaid_gallery_builder", SCRIPT_DIR / "build_gallery.py")
validator = load_module("mermaid_gallery_validator", SCRIPT_DIR / "validate_gallery.py")


class GalleryContractTests(unittest.TestCase):
    def test_catalog_matches_taxonomy_order(self) -> None:
        catalog = json.loads((GALLERY_DIR / "catalog.json").read_text(encoding="utf-8"))
        taxonomy = json.loads((SKILL_DIR / "references" / "diagram-types.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [entry["familyId"] for entry in catalog["families"]],
            [entry["id"] for entry in taxonomy["families"]],
        )
        self.assertEqual(len(catalog["families"]), 31)

    def test_capacity_fixture_totals_remain_terminal(self) -> None:
        capacity = json.loads(
            (GALLERY_DIR.parent / "mermaid-max-elements" / "manifest.json").read_text(encoding="utf-8")
        )
        finite = [entry for entry in capacity["families"] if entry["maxSlots"] is not None]
        self.assertEqual(len(finite), 25)
        self.assertEqual(sum(entry["maxSlots"] for entry in finite), 200)

    def test_accessibility_is_inserted_after_declaration(self) -> None:
        source = "flowchart LR\n  A --> B\n"
        actual = builder.inject_accessibility(source, "Title", "Description")
        self.assertEqual(
            actual.splitlines()[:3],
            ["flowchart LR", "  accTitle: Title", "  accDescr: Description"],
        )

    def test_existing_accessibility_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not contain"):
            builder.inject_accessibility("flowchart LR\n  accTitle: Existing\n", "Title", "Description")

    def test_renderer_fallback_metadata_is_accessible(self) -> None:
        import tempfile
        import xml.etree.ElementTree as ET

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.svg"
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>', encoding="utf-8")
            builder.inject_svg_accessibility(path, "A & B", "Dense <diagram>", "mermaid-block-cs1")
            root = ET.parse(path).getroot()
            self.assertEqual(root.get("role"), "img")
            self.assertEqual(root.get("aria-labelledby"), "mermaid-block-cs1-title")
            self.assertEqual(root.get("aria-describedby"), "mermaid-block-cs1-desc")
            self.assertEqual(next(iter(root)).text, "A & B")

    def test_duplicate_svg_ids_are_renamed_after_first_occurrence(self) -> None:
        import tempfile
        import xml.etree.ElementTree as ET

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.svg"
            path.write_text('<svg><g id="node"/><path id="node"/><use href="#node"/></svg>', encoding="utf-8")
            builder.normalize_duplicate_svg_ids(path)
            root = ET.parse(path).getroot()
            self.assertEqual([element.get("id") for element in root if element.get("id")], ["node", "node-duplicate-2"])
            self.assertEqual(root[-1].get("href"), "#node")

    def test_legacy_hashes_are_unique(self) -> None:
        catalog = json.loads((GALLERY_DIR / "catalog.json").read_text(encoding="utf-8"))
        aliases = [alias for family in catalog["families"] for alias in family.get("legacyIds", [])]
        self.assertEqual(len(aliases), len(set(aliases)))

    def test_generated_gallery_passes_static_validation(self) -> None:
        self.assertTrue((GALLERY_DIR / "gallery.json").is_file(), "Run build_gallery.py first")
        findings, stats = validator.validate(GALLERY_DIR)
        self.assertEqual(findings, [], json.dumps(stats, indent=2))


if __name__ == "__main__":
    unittest.main()
