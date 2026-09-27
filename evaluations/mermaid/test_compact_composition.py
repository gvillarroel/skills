#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Behavioral checks for compact geometry, red/neutral roles, and authored overrides."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "skills/mermaid/scripts/style_mermaid_directory.py"
spec = importlib.util.spec_from_file_location("compact_mermaid_styler", PATH)
styler = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = styler
spec.loader.exec_module(styler)


def styled_config(source: str, colorset: str = "colorset1"):
    styled, _ = styler.style_mermaid_block(source, colorset)
    frontmatter, _ = styler.split_frontmatter(styled)
    return styled, yaml.safe_load(frontmatter.strip().removeprefix("---").removesuffix("---"))["config"]


class CompactCompositionTests(unittest.TestCase):
    def test_no_automatic_pink_in_any_standard_family(self):
        for family in styler.OFFICIAL_FAMILIES:
            with self.subTest(family=family):
                serialized = json.dumps(styler.theme_variables("colorset1", family))
                self.assertNotIn("#ffccd5", serialized)

    def test_semantic_roles_use_only_red_and_neutral_with_readable_text(self):
        allowed = {"#ffffff", "#000000", "#333e48", "#9e1b32", "#6d1222", "#e8002a"}
        allowed.update(styler.PALETTES["colorset1"][f"gray{i}00"] for i in range(1, 10))
        for role in styler.COLOR_CLASS_ORDER:
            with self.subTest(role=role):
                style = styler.class_style("colorset1", role)
                fill, stroke, text = re.findall(r"#[0-9a-f]{6}", style)
                self.assertLessEqual({fill, stroke, text}, allowed)
                self.assertGreaterEqual(styler.contrast_ratio(fill, text), 4.5)
        self.assertIn("fill:#9e1b32", styler.class_style("colorset1", "csPrimary"))
        self.assertIn("fill:#ffffff", styler.class_style("colorset1", "csInfo"))

    def test_extended_semantic_palette_stays_extended(self):
        self.assertIn("#cdf3ff", styler.class_style("colorset2", "csAccent"))
        self.assertIn("#ffccd5", styler.class_style("colorset2", "csPrimary"))

    def test_twelve_unique_indexed_slots_do_not_need_pink(self):
        colors = styler.series_colors(styler.PALETTES["colorset1"], False)
        self.assertEqual(len(set(colors)), 12)
        self.assertNotIn("#ffccd5", colors)
        for color in colors:
            self.assertGreaterEqual(styler.contrast_ratio(color, styler.readable_text_color(color, styler.PALETTES["colorset1"])), 4.5)

    def test_small_flowchart_is_compact_without_semantic_classes(self):
        styled, config = styled_config("flowchart TB\n A[First] --> B[Second]\n")
        self.assertLess(config["flowchart"]["padding"], 15)
        self.assertEqual(config["flowchart"]["padding"], 6)
        self.assertLess(config["flowchart"]["rankSpacing"], 50)
        self.assertNotIn("fontSize", config)
        self.assertEqual(styler.style_mermaid_block(styled, "colorset1")[0], styled)

    def test_all_compact_families_receive_native_config(self):
        sources = {
            "state": "stateDiagram-v2\n A --> B",
            "class": "classDiagram\n A --> B",
            "er": "erDiagram\n A ||--o{ B : has",
            "sequence": "sequenceDiagram\n A->>B: Send",
            "block": "block\n A B",
            "mindmap": "mindmap\n root\n  child",
            "requirement": "requirementDiagram\n requirement a {\n id: A\n text: Test\n risk: low\n verifymethod: test\n }",
        }
        for key, source in sources.items():
            with self.subTest(family=key):
                styled, config = styled_config(source)
                self.assertIn(key, config)
                self.assertEqual(styler.style_mermaid_block(styled, "colorset1")[0], styled)

    def test_partial_authored_map_keeps_comments_nested_values_and_zero(self):
        source = '''---
title: Author title
config:
  flowchart:
    padding: 0 # deliberate
    curve: linear
    subGraphTitleMargin:
      top: 9
  securityLevel: strict
---
flowchart TB
 A --> B
'''
        styled, config = styled_config(source)
        self.assertEqual(config["flowchart"]["padding"], 0)
        self.assertEqual(config["flowchart"]["curve"], "linear")
        self.assertEqual(config["flowchart"]["subGraphTitleMargin"], {"top": 9})
        self.assertEqual(config["flowchart"]["rankSpacing"], 32)
        self.assertEqual(config["securityLevel"], "strict")
        self.assertIn("# deliberate", styled)
        self.assertEqual(styler.style_mermaid_block(styled, "colorset1")[0], styled)

    def test_complete_authored_spacing_is_never_overwritten(self):
        for mapping in ('flowchart: {padding: 21, rankSpacing: 88, nodeSpacing: 70}', '"flowchart":\n    padding: 21\n    rankSpacing: 88\n    nodeSpacing: 70'):
            styled, config = styled_config(f"---\nconfig:\n  {mapping}\n---\nflowchart TB\n A --> B\n")
            self.assertEqual({key: config["flowchart"][key] for key in ("padding", "rankSpacing", "nodeSpacing")}, {"padding": 21, "rankSpacing": 88, "nodeSpacing": 70})
            self.assertEqual(styler.style_mermaid_block(styled, "colorset1")[0], styled)

    def test_yaml_alias_and_merge_overrides_remain_effective(self):
        for mapping in ('*spacing', '\n    <<: *spacing\n    curve: linear'):
            source = f"---\nspacing: &spacing {{padding: 19, rankSpacing: 73}}\nconfig:\n  flowchart: {mapping}\n---\nflowchart TB\n A --> B\n"
            styled, config = styled_config(source)
            self.assertEqual(config["flowchart"]["padding"], 19)
            self.assertEqual(config["flowchart"]["rankSpacing"], 73)
            self.assertNotIn("nodeSpacing", config["flowchart"])
            self.assertEqual(styler.style_mermaid_block(styled, "colorset1")[0], styled)

    def test_standard_and_extended_round_trip_is_stable(self):
        source = "flowchart LR\n A[Primary]:::csPrimary --> B[Info]:::csInfo\n"
        standard, _ = styled_config(source)
        extended, _ = styled_config(standard, "colorset2")
        again, _ = styled_config(extended)
        self.assertEqual(again, standard)
        self.assertNotIn("#ffccd5", standard)


if __name__ == "__main__":
    unittest.main(verbosity=2)
