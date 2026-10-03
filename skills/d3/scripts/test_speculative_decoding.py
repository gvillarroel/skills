#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise literal-data, palette, boundary, portability and exact-output contracts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from build_speculative_decoding import build_html, build_svg


HERE = Path(__file__).resolve().parent
NS = {"s": "http://www.w3.org/2000/svg"}


class SpeculativeDecodingTests(unittest.TestCase):
    def fixture(self, accepted=3, **kwargs):
        return build_svg(["the", "answer", "is", "42"], accepted, "next", **kwargs)

    def test_literal_token_order_and_status(self):
        root = ET.fromstring(self.fixture())
        tokens = root.findall('.//s:g[@data-token-index]', NS)
        self.assertEqual([node.find("s:text", NS).text for node in tokens], ["prompt", "the", "answer", "is", "42", "next"])
        self.assertEqual([node.attrib["class"] for node in tokens], ["token context", "token accepted", "token accepted", "token accepted", "token rejected", "token target"])

    def test_zero_accepted_and_all_accepted(self):
        for accepted, counts in ((0, (0, 4)), (4, (4, 0))):
            root = ET.fromstring(self.fixture(accepted))
            self.assertEqual((len(root.findall('.//s:g[@class="token accepted"]', NS)),
                              len(root.findall('.//s:g[@class="token rejected"]', NS))), counts)
            path = root.find('.//s:path[@class="target-resume"]', NS)
            self.assertIsNotNone(path)
            self.assertEqual(len(root.findall('.//s:g[@class="token target"]', NS)), 1)

    def test_xml_escaping_and_repeated_literals(self):
        root = ET.fromstring(build_svg(["a<&", "a<&", "β"], 2, '"done"', title="A & B", alternates=[(2, "x<y")]))
        self.assertEqual(root.find("s:title", NS).text, "A & B")
        self.assertEqual([t.text for t in root.findall('.//s:text[@class="token-label"]', NS)], ["prompt", "a<&", "a<&", "β", '"done"'])
        self.assertEqual(root.find('.//s:text[@class="alternate-label"]', NS).text, "x<y")

    def test_palette_and_self_contained_validators(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as scratch:
            for colorset in ("colorset1", "colorset2"):
                for extension, content in (("svg", self.fixture(colorset=colorset)),
                                            ("html", build_html(self.fixture(colorset=colorset), colorset, "Speculative decoding"))):
                    artifact = Path(scratch) / f"explanation.{extension}"
                    artifact.write_text(content, encoding="utf-8")
                    command = [sys.executable, str(HERE / "check_palette_contract.py"), str(artifact), "--colorset", colorset]
                    if colorset == "colorset2":
                        command.append("--require-extended")
                    result = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    if extension == "html":
                        result = subprocess.run([sys.executable, str(HERE / "check_self_contained_html.py"), str(artifact)], capture_output=True, text=True)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_paths_and_deterministic_rerun(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as scratch:
            html = Path(scratch) / "nested/lesson.html"
            svg = Path(scratch) / "different/lesson.svg"
            command = [sys.executable, str(HERE / "build_speculative_decoding.py"), "--output-html", str(html),
                       "--output-svg", str(svg), "--draft-token", "the", "--draft-token", "answer", "--accepted-count", "1", "--resume-token", "next"]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = (html.read_bytes(), svg.read_bytes())
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(before, (html.read_bytes(), svg.read_bytes()))
            self.assertEqual(json.loads(first.stdout)["draftTokens"], 2)

    def test_invalid_contract_does_not_write_outputs(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as scratch:
            html, svg = Path(scratch) / "keep.html", Path(scratch) / "missing.svg"
            html.write_text("existing", encoding="utf-8")
            result = subprocess.run([sys.executable, str(HERE / "build_speculative_decoding.py"), "--output-html", str(html),
                                     "--output-svg", str(svg), "--draft-token", "word", "--accepted-count", "2", "--resume-token", "next"], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(html.read_text(encoding="utf-8"), "existing")
            self.assertFalse(svg.exists())

    def test_rejects_invalid_data_and_density(self):
        cases = [([], 0, "next", {}), (["x"], -1, "next", {}), (["x"], 2, "next", {}),
                 ([" x"], 0, "next", {}), (["x\x00"], 0, "next", {}), (["x"], 0, "", {}),
                 (["x"], 0, "next", {"alternates": [(2, "else")]}),
                 (["x"], 0, "next", {"alternates": [(1, "a"), (1, "b")]}),
                 (["x"], 0, "next", {"width": 300}), (["x"], 0, "next", {"height": 200}),
                 (["x"], 0, "next", {"colorset": "rainbow"}),
                 (["label" * 30], 0, "next", {}), (["x"] * 12, 6, "next", {"width": 480})]
        for tokens, accepted, resume, kwargs in cases:
            with self.subTest(tokens=tokens, kwargs=kwargs), self.assertRaises(ValueError):
                build_svg(tokens, accepted, resume, **kwargs)

    def test_larger_changed_input_and_optional_branches(self):
        root = ET.fromstring(build_svg(["We", "can", "ship", "the", "small", "change"], 4, "today", width=960, height=520, colorset="colorset2", alternates=[(2, "may"), (5, "large")]))
        self.assertEqual(root.attrib["viewBox"], "0 0 960 520")
        self.assertEqual(len(root.findall('.//s:g[@data-token-index]', NS)), 8)
        self.assertEqual(len(root.findall('.//s:text[@class="alternate-label"]', NS)), 2)

    def test_portable_svg_and_finite_marker(self):
        root = ET.fromstring(self.fixture())
        for tag in ("script", "foreignObject", "image"):
            self.assertFalse(root.findall(f".//s:{tag}", NS))
        self.assertIsNotNone(root.find("s:title", NS))
        self.assertIsNotNone(root.find("s:desc", NS))
        marker = root.find('.//s:circle[@class="motion-marker"]', NS)
        self.assertEqual(marker.attrib["opacity"], "0")
        animations = root.findall('.//s:animate', NS)
        self.assertTrue(animations)
        self.assertTrue(all(a.attrib.get("repeatCount") != "indefinite" for a in animations))
        self.assertIn('prefers-reduced-motion', root.find("s:style", NS).text)

    def test_browser_verifier_positive_and_missing_replay(self):
        runner = shutil.which("uv")
        self.assertIsNotNone(runner, "The browser verifier is a uv script with declared Playwright dependencies")
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as scratch:
            root = Path(scratch)
            svg, html = root / "lesson.svg", root / "lesson.html"
            source = self.fixture()
            svg.write_text(source, encoding="utf-8")
            for with_replay in (True, False):
                content = build_html(source, "colorset1", "Speculative decoding")
                if not with_replay:
                    content = content.replace('>Replay</button>', '>Start</button>')
                html.write_text(content, encoding="utf-8")
                report = root / "check.json"
                result = subprocess.run([runner, "run", "--script", str(HERE / "verify_speculative_decoding.py"), str(html), "--svg", str(svg),
                                         "--screenshot", str(root / "preview.png"), "--json-report", str(report)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0 if with_replay else 1, result.stdout + result.stderr)
                parsed = json.loads(report.read_text(encoding="utf-8"))
                self.assertEqual(parsed["passed"], with_replay)
                if with_replay:
                    self.assertTrue((root / "preview.png").is_file())
                    self.assertTrue(parsed["checks"]["replay2Visibility"])
                else:
                    self.assertIn("replayControl", parsed["failedChecks"])

    def test_browser_verifier_rejects_viewport_mismatch(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as scratch:
            root = Path(scratch)
            source = self.fixture()
            html, svg = root / "lesson.html", root / "lesson.svg"
            html.write_text(build_html(source, "colorset1", "Speculative decoding"), encoding="utf-8")
            svg.write_text(source.replace('viewBox="0 0 720 440"', 'viewBox="0 0 800 480"'), encoding="utf-8")
            report = root / "check.json"
            result = subprocess.run([shutil.which("uv"), "run", "--script", str(HERE / "verify_speculative_decoding.py"), str(html), "--svg", str(svg),
                                     "--screenshot", str(root / "preview.png"), "--json-report", str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("htmlFinalViewBox", json.loads(report.read_text(encoding="utf-8"))["failedChecks"])

    def test_browser_verifier_cannot_overwrite_input(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as scratch:
            root = Path(scratch)
            source = self.fixture()
            html, svg = root / "lesson.html", root / "lesson.svg"
            html.write_text(build_html(source, "colorset1", "Speculative decoding"), encoding="utf-8")
            svg.write_text(source, encoding="utf-8")
            before = html.read_bytes()
            result = subprocess.run([shutil.which("uv"), "run", "--script", str(HERE / "verify_speculative_decoding.py"), str(html), "--svg", str(svg),
                                     "--screenshot", str(html)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(html.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
