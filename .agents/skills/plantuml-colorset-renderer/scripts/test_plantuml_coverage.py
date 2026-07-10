#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from plantuml_coverage import (  # noqa: E402
    build_gallery_metadata,
    flatten_fixtures,
    load_manifest,
    validate_fixture_directory,
    validate_gallery_metadata,
    validate_manifest,
    validate_report_coverage,
)
from render_plantuml_directory import (  # noqa: E402
    inject_theme,
    kroki_diagram_type_for,
    render_source,
    source_for_kroki,
)


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest()

    def test_frozen_counts_and_fixtures_are_exact(self) -> None:
        self.assertEqual(self.manifest["counts"]["canonicalFamilies"], 27)
        self.assertEqual(self.manifest["counts"]["releaseExtraFamilies"], 1)
        self.assertEqual(self.manifest["counts"]["totalFamilies"], 28)
        self.assertEqual(self.manifest["counts"]["fixtures"], 29)
        findings = validate_fixture_directory(self.manifest, SKILL_DIR / "assets" / "examples" / "base")
        self.assertEqual(findings, [])

    def test_duplicate_family_id_is_rejected(self) -> None:
        broken = copy.deepcopy(self.manifest)
        broken["families"].append(copy.deepcopy(broken["families"][0]))
        findings = validate_manifest(broken)
        self.assertTrue(any("duplicate family id: sequence" in finding for finding in findings))
        self.assertTrue(any("counts.totalFamilies" in finding for finding in findings))

    def test_duplicate_fixture_id_is_rejected(self) -> None:
        broken = copy.deepcopy(self.manifest)
        broken["families"][1]["fixtures"][0]["id"] = "sequence"
        findings = validate_manifest(broken)
        self.assertTrue(any("duplicate fixture id: sequence" in finding for finding in findings))

    def test_missing_fixture_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_dir = Path(temporary)
            (fixture_dir / "sequence.puml").write_text("@startuml\nA -> B\n@enduml\n", encoding="utf-8")
            findings = validate_fixture_directory(self.manifest, fixture_dir)
        self.assertTrue(any("missing fixture sources" in finding for finding in findings))


class RendererPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.theme = "' plantuml-colorset-renderer: test\nskinparam backgroundColor #ffffff\n"

    def test_theme_is_never_injected_into_ditaa_math_or_latex(self) -> None:
        sources = [
            "@startditaa\n+---+\n| A |\n+---+\n@endditaa\n",
            "@startmath\nx^2\n@endmath\n",
            "@startlatex\nx^2\n@endlatex\n",
        ]
        for source in sources:
            with self.subTest(source=source.splitlines()[0]):
                self.assertEqual(inject_theme(source, self.theme), source)

    def test_theme_is_injected_into_normal_plantuml(self) -> None:
        source = "@startuml\nA -> B\n@enduml\n"
        themed = inject_theme(source, self.theme)
        self.assertIn("skinparam backgroundColor", themed)
        self.assertNotEqual(themed, source)

    def test_kroki_ditaa_route_and_payload_are_specialized(self) -> None:
        source = "@startditaa\n+---+\n| A |\n+---+\n@endditaa\n"
        self.assertEqual(kroki_diagram_type_for("@startditaa"), "ditaa")
        payload = source_for_kroki(source, "ditaa")
        self.assertNotIn("@startditaa", payload)
        self.assertNotIn("@endditaa", payload)
        self.assertIn("| A |", payload)

    def test_expected_unavailable_coverage_fixture_never_calls_renderer(self) -> None:
        manifest = load_manifest()
        fixture = next(item for item in flatten_fixtures(manifest) if item["fixtureId"] == "chronology")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / "chronology.puml"
            source_path.write_text(
                "@startchronology\n[A] happens on 2026-01-01 00:00:00\n@endchronology\n",
                encoding="utf-8",
            )
            result = render_source(
                source_path=source_path,
                input_dir=root,
                output_dir=root / "output",
                formats=["svg", "png"],
                theme=self.theme,
                engine="kroki",
                server_url="https://invalid.example",
                kroki_url="https://invalid.example",
                plantuml_command="invalid",
                timeout=1,
                write_themed=False,
                coverage_fixture=fixture,
            )
        self.assertTrue(result.ok)
        self.assertEqual(result.status, "expected-unavailable")
        self.assertEqual(result.outputs, [])


class ExactReportGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest()

    def make_report(self) -> dict[str, object]:
        results = []
        for fixture in flatten_fixtures(self.manifest):
            available = fixture["availability"] == "available"
            publication = fixture["publication"]
            formats = [publication["assetFormat"]] if publication.get("enabled") else []
            results.append(
                {
                    "source": fixture["source"],
                    "diagramId": fixture["fixtureId"],
                    "familyId": fixture["familyId"],
                    "fixtureId": fixture["fixtureId"],
                    "themeMode": fixture["themeMode"],
                    "availability": fixture["availability"],
                    "status": "rendered" if available else "expected-unavailable",
                    "outputs": [
                        {"format": fmt, "path": f"{fmt}/{fixture['fixtureId']}.{fmt}"}
                        for fmt in formats
                    ],
                }
            )
        return {
            "formats": ["svg", "png"],
            "publicationOnly": True,
            "coverageBaseline": copy.deepcopy(self.manifest["baseline"]),
            "coverageCounts": copy.deepcopy(self.manifest["counts"]),
            "sourceDiagramCount": len(results),
            "results": results,
        }

    def test_complete_report_passes(self) -> None:
        self.assertEqual(validate_report_coverage(self.make_report(), self.manifest), [])

    def test_missing_family_and_fixture_are_rejected(self) -> None:
        report = self.make_report()
        report["results"] = [result for result in report["results"] if result["familyId"] != "chart"]
        report["sourceDiagramCount"] = len(report["results"])
        findings = validate_report_coverage(report, self.manifest)
        self.assertTrue(any("missing report family ids: ['chart']" in finding for finding in findings))
        self.assertTrue(any("missing report fixture ids: ['chart']" in finding for finding in findings))

    def test_duplicate_fixture_and_count_are_rejected(self) -> None:
        report = self.make_report()
        report["results"].append(copy.deepcopy(report["results"][0]))
        report["sourceDiagramCount"] = len(report["results"])
        findings = validate_report_coverage(report, self.manifest)
        self.assertTrue(any("duplicate report fixture ids" in finding for finding in findings))
        self.assertTrue(any("report result count must be 29" in finding for finding in findings))

    def test_wrong_per_fixture_format_is_rejected(self) -> None:
        report = self.make_report()
        ditaa = next(result for result in report["results"] if result["fixtureId"] == "ditaa")
        ditaa["outputs"] = [{"format": "svg", "path": "svg/ditaa.svg"}]
        findings = validate_report_coverage(report, self.manifest)
        self.assertTrue(any("ditaa: output formats ['svg'] must equal ['png']" in finding for finding in findings))


class RenderArtifactValidationTests(unittest.TestCase):
    def test_default_black_and_white_do_not_prove_colorset_application(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output_dir = root / "output"
            svg_path = output_dir / "svg" / "default.svg"
            svg_path.parent.mkdir(parents=True)
            svg_path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#FFFFFF" stroke="#000000"/></svg>', encoding="utf-8")
            report_path = root / "report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "ok": True,
                        "colorset": "colorset1",
                        "formats": ["svg"],
                        "failedDiagramCount": 0,
                        "renderedDiagramCount": 1,
                        "results": [
                            {
                                "source": "default.puml",
                                "themeMode": "inject",
                                "themeApplied": True,
                                "expectedFormats": ["svg"],
                                "outputs": [{"format": "svg", "path": "svg/default.svg"}],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "validate_plantuml_render_report.py"),
                    "--report",
                    str(report_path),
                    "--output",
                    str(output_dir),
                    "--colorset",
                    "colorset1",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        validation = json.loads(completed.stdout)
        self.assertFalse(validation["ok"])
        self.assertTrue(any("distinctive colorset1" in finding for finding in validation["findings"]))

    def test_unthemed_png_only_report_does_not_require_svg_palette_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output_dir = root / "output"
            png_path = output_dir / "png" / "ditaa.png"
            png_path.parent.mkdir(parents=True)
            png_path.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
            report_path = root / "report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "ok": True,
                        "colorset": "colorset2",
                        "formats": ["png"],
                        "failedDiagramCount": 0,
                        "renderedDiagramCount": 1,
                        "results": [
                            {
                                "source": "ditaa.puml",
                                "themeApplied": False,
                                "expectedFormats": ["png"],
                                "outputs": [{"format": "png", "path": "png/ditaa.png"}],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "validate_plantuml_render_report.py"),
                    "--report",
                    str(report_path),
                    "--output",
                    str(output_dir),
                    "--colorset",
                    "colorset2",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["ok"])


class GalleryGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest()

    def test_complete_gallery_metadata_passes(self) -> None:
        metadata = build_gallery_metadata(self.manifest, "colorset2")
        self.assertEqual(validate_gallery_metadata(metadata, self.manifest), [])

    def test_duplicate_and_missing_gallery_items_are_rejected(self) -> None:
        metadata = build_gallery_metadata(self.manifest, "colorset2")
        metadata["items"] = metadata["items"][:-1] + [copy.deepcopy(metadata["items"][0])]
        findings = validate_gallery_metadata(metadata, self.manifest)
        self.assertTrue(any("duplicate gallery item ids" in finding for finding in findings))
        self.assertTrue(any("missing gallery item ids" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
