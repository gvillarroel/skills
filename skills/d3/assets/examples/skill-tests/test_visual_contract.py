#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the rendered D3 literal-contract checker."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import check_visual_contract


SVG = """<svg id="service-network" class="chart" data-layout="force" viewBox="0 0 400 240">
<title>Service network</title><desc>Directed service topology</desc>
<g class="node"><circle/><text>Gateway</text></g>
<g class="node"><circle/><text>Queue</text></g>
<g class="link"><line/></g><g class="link"><line/></g>
<text>Store</text></svg>"""

ARTIFACTS: Path


def arguments(path: Path, **overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "artifact": path,
        "require_id": [],
        "require_class": [],
        "require_tag": [],
        "require_attribute": [],
        "require_text": [],
        "ordered_text": [],
        "no_require_svg_contract": False,
        "json_report": None,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class VisualContractTests(unittest.TestCase):
    def write_svg(self, root: Path, source: str = SVG) -> Path:
        path = root / "visual.svg"
        path.write_text(source, encoding="utf-8")
        return path

    def test_exact_structure_and_order_pass(self) -> None:
        with tempfile.TemporaryDirectory(dir=ARTIFACTS) as temporary:
            path = self.write_svg(Path(temporary))
            result = check_visual_contract.check(
                arguments(
                    path,
                    require_id=["service-network"],
                    require_class=[("node", 2), ("link", 2)],
                    require_tag=[("circle", 2), ("line", 2)],
                    require_attribute=[("data-layout", "force")],
                    require_text=["Gateway", "Store"],
                    ordered_text=["Gateway", "Queue", "Store"],
                )
            )
            self.assertTrue(result["ok"], result)

    def test_near_equivalent_id_and_class_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir=ARTIFACTS) as temporary:
            path = self.write_svg(Path(temporary))
            result = check_visual_contract.check(
                arguments(path, require_id=["service-dependency-svg"], require_class=[("nodes", 2)])
            )
            self.assertFalse(result["ok"])
            self.assertIn("missing ID: service-dependency-svg", result["findings"])

    def test_order_uses_later_occurrence_when_title_repeats_a_data_label(self) -> None:
        source = """<svg id="release" viewBox="0 0 400 240">
<title>Release readiness</title><desc>Checks by stage</desc>
<text>Build</text><text>12</text><text>Verify</text><text>9</text><text>Release</text><text>6</text>
</svg>"""
        with tempfile.TemporaryDirectory(dir=ARTIFACTS) as temporary:
            path = self.write_svg(Path(temporary), source)
            result = check_visual_contract.check(
                arguments(path, ordered_text=["Build", "12", "Verify", "9", "Release", "6"])
            )
            self.assertTrue(result["ok"], result)

    def test_accessibility_contract_is_default(self) -> None:
        with tempfile.TemporaryDirectory(dir=ARTIFACTS) as temporary:
            path = self.write_svg(Path(temporary), "<svg><circle/></svg>")
            result = check_visual_contract.check(arguments(path))
            self.assertFalse(result["ok"])
            self.assertIn("missing rendered title", result["findings"])
            self.assertIn("missing rendered desc", result["findings"])
            self.assertIn("missing stable SVG viewBox", result["findings"])

    def test_cli_alias_repeated_and_pipe_sequence_are_equivalent(self) -> None:
        with tempfile.TemporaryDirectory(dir=ARTIFACTS) as temporary:
            path=self.write_svg(Path(temporary))
            flags=[['--ordered-text','Gateway','--ordered-text','Queue','--ordered-text','Store'],
                   ['--require-ordered-text','Gateway','--require-ordered-text','Queue','--require-ordered-text','Store'],
                   ['--require-ordered-text','Gateway|Queue|Store'],
                   ['--ordered-text','Gateway','--require-ordered-text','Queue|Store']]
            reports=[]
            for sequence in flags:
                args=check_visual_contract.parse_args([str(path),*sequence])
                self.assertEqual(args.ordered_text,['Gateway','Queue','Store'])
                reports.append(check_visual_contract.check(args))
            self.assertTrue(reports[0]['ok'],reports)
            self.assertTrue(all(report==reports[0] for report in reports))

    def test_cli_alias_wrong_order_and_missing_tokens_still_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir=ARTIFACTS) as temporary:
            path=self.write_svg(Path(temporary))
            for sequence in [
                ['--require-ordered-text','Store|Gateway|Queue'],
                ['--require-ordered-text','Store','--require-ordered-text','Gateway','--require-ordered-text','Queue'],
                ['--require-ordered-text','Gateway|Missing|Store']]:
                result=check_visual_contract.check(check_visual_contract.parse_args([str(path),*sequence]))
                self.assertFalse(result['ok'])
                self.assertIn('ordered visible text is missing or out of order',result['findings'])

    def test_legacy_pipe_label_stays_one_literal_token(self) -> None:
        with tempfile.TemporaryDirectory(dir=ARTIFACTS) as temporary:
            path=self.write_svg(Path(temporary),SVG.replace('Gateway','Gateway|Queue'))
            legacy=check_visual_contract.parse_args([str(path),'--ordered-text','Gateway|Queue','--ordered-text','Store'])
            self.assertEqual(legacy.ordered_text,['Gateway|Queue','Store'])
            self.assertTrue(check_visual_contract.check(legacy)['ok'])
            separate=self.write_svg(Path(temporary))
            result=check_visual_contract.check(check_visual_contract.parse_args([str(separate),'--ordered-text','Gateway|Queue']))
            self.assertFalse(result['ok'])

    def test_alias_rejects_empty_sequence_members(self) -> None:
        for value in ['', 'Gateway||Queue', '|Gateway', 'Gateway|']:
            with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as error:
                check_visual_contract.parse_args(['unused.svg','--require-ordered-text',value])
            self.assertEqual(error.exception.code,2)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts',type=Path,required=True)
    args=parser.parse_args()
    ARTIFACTS=args.artifacts.resolve()
    if ARTIFACTS.is_relative_to(Path(__file__).resolve().parents[3]):
        parser.error('Artifacts must be outside the skill resource')
    ARTIFACTS.mkdir(parents=True,exist_ok=True)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(VisualContractTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
