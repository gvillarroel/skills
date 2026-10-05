#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check independent category order, canvas exclusion, contrast and overflow."""
import unittest
from palette_contract import solid_colors, category_style

CS1 = ['#9e1b32', '#000000', '#828282', '#1c1c1c', '#9c9c9c',
       '#363636', '#b5b5b5', '#333e48', '#cfcfcf', '#4f4f4f',
       '#e7e7e7', '#696969', '#f7f7f7', '#ffffff', '#6d1222',
       '#e8002a', '#ffccd5']
CS2 = ['#9e1b32', '#007298', '#e77204', '#45842a', '#652f6c', '#f1c319',
       '#6d1222', '#004d66', '#994a00', '#294d19', '#431f47', '#98700c',
       '#e8002a', '#00ace6', '#ff9633', '#36b300', '#9e00b3', '#ffd332',
       '#333e48', '#4f4f4f', '#696969', '#828282', '#9c9c9c', '#b5b5b5',
       '#1c1c1c', '#363636', '#000000', '#cfcfcf', '#e7e7e7', '#ffccd5',
       '#cdf3ff', '#dbffcc', '#f9ccff', '#ffe5cc', '#fff4cc', '#ffffff', '#f7f7f7']


def luminance(paint):
    channels = [int(paint[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4
              for value in channels]
    return sum(value * weight for value, weight in zip(linear, (.2126, .7152, .0722)))


def contrast(first, second):
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + .05) / (dark + .05)


class CategoryContractTests(unittest.TestCase):
    def test_exact_sequences_canvas_filter_and_solid_capacity(self):
        for colorset, literal in [('colorset1', CS1), ('colorset2', CS2)]:
            for canvas in ['#ffffff', '#f7f7f7', '#000000', '#9e1b32']:
                expected = [fill for fill in literal if fill != canvas]
                self.assertEqual(solid_colors(colorset, canvas), expected)
                for index, fill in enumerate(expected):
                    style = category_style(index, colorset, canvas)
                    self.assertEqual(style['fill'], fill)
                    self.assertEqual(style['stroke'], 'none')
                    self.assertEqual(style['strokeWidth'], 0)
                    self.assertFalse(style['overflow'])
                    self.assertFalse(style['overflowExhausted'])
                    self.assertEqual(style['text'], max(('#000000', '#ffffff'),
                                                       key=lambda ink: contrast(ink, fill)))
                overflow = category_style(len(expected), colorset, canvas)
                self.assertTrue(overflow['overflow'])
                self.assertEqual(overflow['fill'], expected[0])
                self.assertGreaterEqual(contrast(overflow['stroke'], overflow['fill']), 3)
                self.assertGreater(overflow['strokeWidth'], 0)
                self.assertLessEqual(overflow['strokeWidth'], 3)


if __name__ == '__main__':
    unittest.main()
