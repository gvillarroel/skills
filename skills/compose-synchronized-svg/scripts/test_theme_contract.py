#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Focused tests for theme_contract; run directly with uv."""

from __future__ import annotations

import unittest

from theme_contract import contrast_ratio, resolve_theme, derived_theme_colors, mix_color, readable_text
from palette_contract import COLORSETS, solid_colors, category_style, text_on_fill


class ThemeContractTests(unittest.TestCase):
    def test_automatic_foreground_handles_light_dark_and_saturated_surfaces(self) -> None:
        for red in range(0, 256, 17):
            for green in range(0, 256, 17):
                for blue in range(0, 256, 17):
                    background = f"#{red:02x}{green:02x}{blue:02x}"
                    color = readable_text([background], ["#203332", "#ffffff"])
                    self.assertGreaterEqual(contrast_ratio(color, background), 4.5)
        self.assertEqual(readable_text(["#fff0a8"], ["#ffffff", "#203332"]), "#203332")
        self.assertEqual(readable_text(["#203332"], ["#ffffff"]), "#ffffff")
        with self.assertRaisesRegex(ValueError, "opaque label surface"):
            readable_text(["#000000", "#ffffff"])

    def test_safe_tints_preserve_a_near_threshold_foreground(self) -> None:
        theme = resolve_theme({"colors": {"canvas": "#ffffff", "muted": "#696969"}}, ["a"])
        original = dict(theme["colors"])
        pairs = derived_theme_colors(theme)
        for key in ("surface-subtle", "accent-soft", "warning-soft", "danger-soft"):
            for role in ("ink", "muted", "accent", "warning", "danger"):
                self.assertGreaterEqual(contrast_ratio(theme["colors"][role], pairs[key]), 4.5)
        self.assertEqual(theme["colors"], original)
        self.assertTrue(set(pairs.values()) <= set(COLORSETS['colorset1']['allowed']))
        self.assertEqual(pairs["surface-value-a"], theme["conceptColors"]["a"])
        self.assertEqual(pairs["on-value-a"], text_on_fill(pairs["surface-value-a"], "colorset1"))

    def test_mark_color_stays_exact_while_small_text_gets_a_readable_pair(self) -> None:
        theme = resolve_theme({"conceptColors": {"a": "#828282"}}, ["a"])
        self.assertLess(contrast_ratio(theme["conceptColors"]["a"], theme["colors"]["surface"]), 4.5)
        pairs = derived_theme_colors(theme)
        self.assertEqual(theme["conceptColors"]["a"], "#828282")
        self.assertGreaterEqual(contrast_ratio(pairs["text-value-a"], theme["colors"]["surface"]), 4.5)

    def test_inverse_text_pairs_work_in_complete_light_and_dark_themes(self) -> None:
        dark = {"canvas": "#1c1c1c", "surface": "#333e48", "ink": "#f7f7f7",
                "muted": "#cfcfcf", "line": "#696969", "accent": "#ffccd5",
                "focus": "#ffffff", "warning": "#e7e7e7", "danger": "#ffccd5"}
        for raw in ({}, {"colors": dark, "conceptColors": {"a": "#ffffff"}}):
            theme = resolve_theme(raw, ["a"])
            pairs = derived_theme_colors(theme)
            for role in ("on-ink", "on-ink-muted"):
                self.assertGreaterEqual(contrast_ratio(pairs[role], theme["colors"]["ink"]), 4.5)

    def test_threshold_is_not_rounded_up(self) -> None:
        self.assertLess(contrast_ratio("#777777", "#ffffff"), 4.5)
        with self.assertRaisesRegex(ValueError, "insufficient contrast"):
            resolve_theme({"colors": {"canvas": "#ffffff", "muted": "#828282"}}, [])

    def test_inverse_navigation_tokens_maximize_exact_black_white_contrast(self) -> None:
        dark = {"canvas": "#1c1c1c", "surface": "#333e48", "ink": "#f7f7f7",
                "muted": "#cfcfcf", "line": "#696969", "accent": "#ffccd5",
                "focus": "#ffffff", "warning": "#e7e7e7", "danger": "#ffccd5"}
        for colorset in ("colorset1", "colorset2"):
            for overrides in ({}, {"colors": dark}):
                theme = resolve_theme({"preset": colorset, **overrides}, ["a"])
                pairs = derived_theme_colors(theme)
                expected = text_on_fill(theme["colors"]["ink"], colorset)
                for token in ("on-ink", "on-ink-muted"):
                    self.assertIn(pairs[token], ("#000000", "#ffffff"))
                    self.assertEqual(pairs[token], expected)
                    self.assertEqual(contrast_ratio(pairs[token], theme["colors"]["ink"]),
                                     max(contrast_ratio(candidate, theme["colors"]["ink"])
                                         for candidate in ("#000000", "#ffffff")))

    def test_long_overflow_cycles_keep_contrast_and_bounded_width(self) -> None:
        for colorset in COLORSETS:
            for canvas in ("#ffffff", "#000000", "#9e1b32"):
                capacity = len(solid_colors(colorset, canvas))
                for index in range(capacity, capacity * 220):
                    style = category_style(index, colorset, canvas)
                    self.assertNotEqual(style["stroke"], style["fill"])
                    self.assertGreaterEqual(contrast_ratio(style["stroke"], style["fill"]), 3)
                    self.assertIn(style["strokeWidth"], (1, 2, 3))
                    self.assertIn(style["dash"], ("", "6 3", "2 3"))
                self.assertTrue(category_style(capacity * 220, colorset, canvas)["overflowExhausted"])

    def test_default_and_presets(self) -> None:
        self.assertEqual(resolve_theme(None, [])['preset'], 'editorial')
        classic = resolve_theme({'preset': 'classic'}, ['a', 'b'])
        self.assertEqual(classic['conceptColors'], {'a': '#9e1b32', 'b': '#007298'})

    def test_classic_color_function_stays_inside_finite_palette(self) -> None:
        colors = resolve_theme({'preset': 'classic'}, [f't{i}' for i in range(24)])['conceptColors']
        self.assertEqual(colors['t0'], '#9e1b32')
        self.assertEqual(len(set(colors.values())), 24)
        self.assertTrue(set(colors.values()) <= set(COLORSETS['colorset2']['allowed']))
        self.assertNotEqual(colors['t19'], colors['t0'])

    def test_custom_brand_colors_are_normalized_and_preserved(self) -> None:
        theme = resolve_theme({'colors': {
            'canvas': '#F7F7F7', 'surface': '#FFFFFF', 'ink': '#333E48',
            'muted': '#696969', 'line': '#CFCFCF', 'accent': '#9E1B32',
            'focus': '#6D1222', 'warning': '#4F4F4F', 'danger': '#9E1B32',
        }, 'conceptColors': {'brand': '#363636'}}, ['brand'])
        self.assertEqual(theme['colors']['accent'], '#9e1b32')
        self.assertEqual(theme['conceptColors']['brand'], '#363636')
        with self.assertRaisesRegex(ValueError, 'exact colorset1 token'):
            resolve_theme({'conceptColors': {'brand': '#123456'}}, ['brand'])

    def test_alias_unknown_key_names_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "alias.*root 'source'"):
            resolve_theme({'conceptColors': {'derived': '#123456'}}, ['source', 'derived'], {'source': 'source', 'derived': 'source'})

    def test_rejects_unknown_fields_types_and_injection(self) -> None:
        cases = [
            ({'nope': 1}, []),
            ({'colors': {'accent': 3}}, []),
            ({'colors': {'accent': 'red'}}, []),
            ({'conceptColors': []}, ['x']),
            ({'preset': 'neon'}, []),
        ]
        for raw, ids in cases:
            with self.subTest(raw=raw):
                with self.assertRaisesRegex(ValueError, 'theme validation failure'):
                    resolve_theme(raw, ids)

    def test_rejects_low_contrast_and_collisions(self) -> None:
        with self.assertRaisesRegex(ValueError, 'insufficient contrast'):
            resolve_theme({'colors': {'accent': '#e7e7e7'}}, [])
        repeated = resolve_theme({'conceptColors': {'a': '#9e1b32', 'b': '#9e1b32'}}, ['a', 'b'])
        self.assertEqual(set(repeated['conceptColors']), {'a', 'b'})

    def test_deterministic_editorial_expansion_for_24_tokens(self) -> None:
        ids = [f'value-{i}' for i in range(24)]
        first = resolve_theme(None, ids)
        second = resolve_theme(None, ids)
        self.assertEqual(first, second)
        self.assertEqual(len(first['conceptColors']), 24)
        self.assertEqual(len(set(first['conceptColors'].values())), 16)
        self.assertTrue(set(first['conceptColors'].values()) <= set(COLORSETS['colorset1']['allowed']))

    def test_role_and_token_contrast(self) -> None:
        theme = resolve_theme(None, ['a', 'b', 'c'])
        for role in ('ink', 'muted', 'accent', 'warning', 'danger'):
            self.assertGreaterEqual(min(contrast_ratio(theme['colors'][role], theme['colors'][base]) for base in ('canvas', 'surface')), 4.5)
        self.assertGreaterEqual(min(contrast_ratio(theme['colors']['focus'], theme['colors'][base]) for base in ('canvas', 'surface')), 3)
        for color in theme['conceptColors'].values():
            self.assertGreaterEqual(min(contrast_ratio(color, theme['colors'][base]) for base in ('canvas', 'surface')), 3)

    def test_exhaust_every_solid_before_explicit_border_overflow(self):
        for colorset in COLORSETS:
            for canvas in ("#f7f7f7", "#ffffff", "#000000"):
                solids = solid_colors(colorset, canvas)
                self.assertEqual(set(solids), set(COLORSETS[colorset]["allowed"]) - {canvas})
                styles = [category_style(i, colorset, canvas) for i in range(len(solids))]
                self.assertEqual(len({s["fill"] for s in styles}), len(solids))
                for style in styles:
                    self.assertEqual(style["stroke"], "none")
                    self.assertEqual(style["strokeWidth"], 0)
                    self.assertFalse(style["overflow"])
                    self.assertIn(style["text"], ("#000000", "#ffffff"))
                    self.assertEqual(style["text"], max(("#000000", "#ffffff"), key=lambda c: contrast_ratio(c, style["fill"])))
                overflow = category_style(len(solids), colorset, canvas)
                self.assertTrue(overflow["overflow"])
                self.assertGreater(overflow["strokeWidth"], 0)
                self.assertNotEqual(overflow["stroke"], overflow["fill"])


if __name__ == '__main__':
    unittest.main()
