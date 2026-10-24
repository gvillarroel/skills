#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Check portable gallery fingerprints against precision and identity controls."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "skills/reflex-xy/assets/examples/reflex-xy-colorsets/build.py"
SPEC = importlib.util.spec_from_file_location("xy_gallery", SOURCE)
GALLERY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GALLERY)


def map_arrays(value, transform):
    if isinstance(value, np.ndarray):
        return transform(value)
    if isinstance(value, dict):
        return {key: map_arrays(item, transform) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(map_arrays(item, transform) for item in value)
    return value


class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.data = GALLERY.synthetic_data()
        self.expected = GALLERY.fingerprint(self.data)

    def test_float64_last_bits_do_not_change_wire_identity(self):
        nearby = map_arrays(self.data, lambda a: np.nextafter(a, np.inf))
        self.assertEqual(GALLERY.fingerprint(nearby), self.expected)

    def test_byte_order_and_layout_are_canonical(self):
        big_endian = map_arrays(self.data, lambda a: np.asfortranarray(a.astype(">f8")))
        self.assertEqual(GALLERY.fingerprint(big_endian), self.expected)

    def test_nan_payload_is_canonical(self):
        altered = copy.deepcopy(self.data)
        values = altered["trends"][1][1]
        values.view(np.uint64)[6] = 0x7FF8000000000123
        self.assertTrue(np.isnan(values[6]))
        self.assertEqual(GALLERY.fingerprint(altered), self.expected)

    def test_visible_value_change_is_detected(self):
        altered = copy.deepcopy(self.data)
        altered["latencies"][0] += 1
        self.assertNotEqual(GALLERY.fingerprint(altered), self.expected)

    def test_shape_change_is_detected(self):
        altered = copy.deepcopy(self.data)
        altered["workload"] = altered["workload"].reshape(1, -1)
        self.assertNotEqual(GALLERY.fingerprint(altered), self.expected)

    def test_label_and_week_changes_are_detected(self):
        altered = copy.deepcopy(self.data)
        _, x, y = altered["cohorts"][0]
        altered["cohorts"][0] = ("Different cohort", x, y)
        self.assertNotEqual(GALLERY.fingerprint(altered), self.expected)
        altered = copy.deepcopy(self.data)
        altered["weeks"][0] += 1
        self.assertNotEqual(GALLERY.fingerprint(altered), self.expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
