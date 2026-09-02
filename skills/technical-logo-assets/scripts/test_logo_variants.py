#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Contract tests for genuine vector content, safe variants, and exact exports."""

from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from build_logo_manifest import apply_vector_source_lock
from build_logo_variants import add_grayscale, native_single_paint
from export_logo_asset import export_one, prepare_export
from logo_svg import SVG_NS, digest, inspect_vector, monochrome_root, painted_variant, wrapped_variant
from sync_normalized_logos import asset_directory, safe_asset_path, wrapped_svg


SINGLE = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#1a2b3c" fill-rule="evenodd" d="M0 0h24v24H0z M4 4v16h16V4z"/></svg>'
MULTI = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" fill="black"/><circle cx="12" cy="12" r="5" fill="white"/></svg>'
ITEM = {"id": "test-brand", "title": "Test brand", "provider": "Fixture", "licenseId": "MIT", "sourceSha256": digest(SINGLE), "sourceFormat": "svg"}


class SvgContractTests(unittest.TestCase):
    def test_real_geometry_is_vector(self) -> None:
        self.assertTrue(inspect_vector(SINGLE)["vectorOnly"])

    def test_raster_data_uri_is_rejected(self) -> None:
        source = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><image href="data:image/png;base64,iVBORw0KGgo="/></svg>'
        with self.assertRaisesRegex(ValueError, "Raster"):
            inspect_vector(source)

    def test_raster_with_fake_svg_mime_is_rejected(self) -> None:
        source = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><image href="data:image/svg+xml;base64,iVBORw0KGgo="/></svg>'
        with self.assertRaises(ValueError):
            inspect_vector(source)

    def test_nested_vector_is_checked(self) -> None:
        payload = wrapped_variant(ITEM, SINGLE)
        self.assertEqual(inspect_vector(payload)["embeddedSvgCount"], 1)

    def test_symlink_text_is_not_svg(self) -> None:
        with self.assertRaises(ValueError):
            inspect_vector(b"../../ui/src/assets/favicon/favicon-v3.svg")

    def test_active_external_and_entity_resources_are_rejected(self) -> None:
        for body in ('<script>alert(1)</script><path d="M0 0h1"/>', '<image href="https://example.com/logo.svg"/>',
                     '<style>@import "https://example.com/logo.css";</style><path d="M0 0h1"/>', '<path onload="x()" d="M0 0h1"/>'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                inspect_vector(f'<svg xmlns="{SVG_NS}" viewBox="0 0 24 24">{body}</svg>'.encode())
        with self.assertRaises(ValueError):
            inspect_vector(b'<!DOCTYPE svg [<!ENTITY bad "content">]>' + SINGLE)

    def test_bitmap_disguised_as_font_is_rejected(self) -> None:
        source = f'<svg xmlns="{SVG_NS}" viewBox="0 0 24 24"><style>@font-face{{font-family:X;src:url(data:font/ttf;base64,iVBORw0KGgo=)}}</style><text font-family="X">x</text></svg>'
        with self.assertRaisesRegex(ValueError, "font"):
            inspect_vector(source.encode())

    def test_unembedded_text_is_not_portable(self) -> None:
        with self.assertRaisesRegex(ValueError, "font"):
            inspect_vector(f'<svg xmlns="{SVG_NS}" viewBox="0 0 24 24"><text>x</text></svg>'.encode())

    def test_multicolor_cutout_is_never_flattened(self) -> None:
        with self.assertRaisesRegex(ValueError, "silhouette"):
            monochrome_root(MULTI)

    def test_different_currentcolor_values_are_not_one_paint(self) -> None:
        payload = f'<svg xmlns="{SVG_NS}" viewBox="0 0 24 24"><rect width="24" height="24" fill="currentColor" color="black"/><circle cx="12" cy="12" r="5" fill="currentColor" color="white"/></svg>'.encode()
        with self.assertRaises(ValueError):
            monochrome_root(payload)

    def test_adaptive_preserves_geometry_and_cutouts(self) -> None:
        payload = painted_variant(ITEM, SINGLE, "adaptive", "currentColor")
        root = ET.fromstring(payload)
        self.assertEqual(root.get("data-logo-variant"), "adaptive")
        self.assertEqual(root.get("data-recolorable"), "true")
        self.assertEqual(root.find(f".//{{{SVG_NS}}}path").get("fill-rule"), "evenodd")
        self.assertEqual(root.find(f".//{{{SVG_NS}}}path").get("fill"), "currentColor")
        self.assertIsNone(root.find(f".//{{{SVG_NS}}}image"))

    def test_black_and_white_are_exact_literals(self) -> None:
        for kind, value in (("mono-black", "#000000"), ("mono-white", "#ffffff")):
            root = ET.fromstring(painted_variant(ITEM, SINGLE, kind, value))
            self.assertEqual(root.find(f".//{{{SVG_NS}}}path").get("fill"), value)

    def test_outline_variant_preserves_inherited_no_fill(self) -> None:
        source = f'<svg xmlns="{SVG_NS}" viewBox="0 0 24 24" fill="none"><path stroke="#123456" d="M2 2h20v20H2z"/></svg>'.encode()
        root = ET.fromstring(painted_variant(ITEM, source, "adaptive", "currentColor"))
        inner = root.find(f"{{{SVG_NS}}}svg")
        self.assertEqual(inner.get("fill"), "none")
        self.assertEqual(inner.find(f"{{{SVG_NS}}}path").get("stroke"), "currentColor")

    def test_simple_css_is_resolved_before_recoloring(self) -> None:
        source = f'<svg xmlns="{SVG_NS}" viewBox="0 0 24 24"><style>.brand{{fill:#123456;fill-rule:evenodd}}</style><path class="brand" d="M0 0h24v24H0z"/></svg>'.encode()
        root = ET.fromstring(painted_variant(ITEM, source, "adaptive", "currentColor"))
        self.assertEqual(root.find(f".//{{{SVG_NS}}}path").get("fill-rule"), "evenodd")
        self.assertIsNone(root.find(f".//{{{SVG_NS}}}style"))

    def test_grayscale_keeps_single_normalization(self) -> None:
        root = ET.fromstring(add_grayscale(wrapped_variant(ITEM, MULTI), ITEM["id"]))
        images = root.findall(f".//{{{SVG_NS}}}image")
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].get("width"), "224")
        self.assertEqual(root.get("data-logo-variant"), "grayscale")

    def test_native_white_detection_does_not_recolor(self) -> None:
        white = SINGLE.replace(b"#1a2b3c", b"#ffffff")
        self.assertEqual(native_single_paint(white), "#ffffff")
        self.assertNotEqual(native_single_paint(SINGLE), "#ffffff")

    def test_unsafe_paths_are_rejected(self) -> None:
        for relative in ("../escape.svg", "x/../../escape.svg", "C:/outside.svg", "x\\file.svg"):
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                safe_asset_path(asset_directory(), relative)

    def test_raster_source_wrapper_cannot_be_generated(self) -> None:
        with self.assertRaisesRegex(ValueError, "Raster-backed"):
            wrapped_svg({**ITEM, "sourceFormat": "png"}, b"pixels", {})

    def test_vector_lock_rejects_changed_upstream(self) -> None:
        original = {**ITEM, "assetPath": "test.svg", "sourcePath": "old.png", "sourceRepository": "https://example.com", "sourceCommit": "pin"}
        replacement = {**original, "previousSource": dict(original), "sourcePath": "new.svg"}
        lock = {"schemaVersion": 1, "replacements": {ITEM["id"]: replacement}}
        self.assertEqual(apply_vector_source_lock([original], lock)[0]["sourcePath"], "new.svg")
        changed = {**original, "sourceSha256": "changed"}
        with self.assertRaisesRegex(ValueError, "Stale"):
            apply_vector_source_lock([changed], lock)


class CatalogSelectionTests(unittest.TestCase):
    def test_custom_color_is_labeled_and_geometry_is_vector(self) -> None:
        payload, metadata, license_bytes = prepare_export(asset_directory(), "devicon-python", "adaptive", "#07a")
        self.assertTrue(inspect_vector(payload)["vectorOnly"])
        root = ET.fromstring(payload)
        self.assertEqual(root.get("data-logo-variant"), "custom-color")
        self.assertEqual(root.get("data-color-value"), "#0077aa")
        self.assertEqual(metadata["requestedVariant"], "adaptive")
        self.assertIn(b"MIT License", license_bytes)
        self.assertNotIn(b'fill="currentColor"', payload)

    def test_cloud_adaptive_is_explicitly_unavailable(self) -> None:
        with self.assertRaisesRegex(ValueError, "license-no-derivatives"):
            prepare_export(asset_directory(), "aws-compute-lambda", "adaptive", "#123456")

    def test_wrong_variant_cannot_be_forced_to_custom_color(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires.*adaptive"):
            prepare_export(asset_directory(), "devicon-python", "color", "#123456")

    def test_invalid_color_is_rejected(self) -> None:
        for color in ("red", "url(https://example.com)", "#12345", "#12345678"):
            with self.subTest(color=color), self.assertRaises(ValueError):
                prepare_export(asset_directory(), "devicon-python", "adaptive", color)

    def test_unknown_id_is_not_fuzzily_substituted(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown exact"):
            prepare_export(asset_directory(), "python-ish", "color")

    def test_export_has_sidecars_and_preserves_existing_files(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            target = Path(folder) / "python.svg"
            export_one(asset_directory(), "devicon-python", "mono-black", target)
            self.assertTrue(target.with_suffix(".provenance.json").is_file())
            self.assertTrue(target.with_suffix(".license.txt").is_file())
            before = target.read_bytes()
            export_one(asset_directory(), "devicon-python", "mono-black", target)
            with self.assertRaisesRegex(ValueError, "overwrite"):
                export_one(asset_directory(), "devicon-python", "mono-white", target)
            self.assertEqual(target.read_bytes(), before)

    def test_no_derivatives_have_no_transformed_variants(self) -> None:
        path = asset_directory() / "logo_variants.json"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        for row in catalog["logos"]:
            for kind, record in row["variants"].items():
                if record["licenseId"] == "CC-BY-ND-2.0":
                    self.assertIn(record["method"], {"unmodified-source", "unmodified-native-monochrome"}, (row["id"], kind))


if __name__ == "__main__":
    unittest.main()
