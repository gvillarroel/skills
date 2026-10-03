#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise paint remapping without executing any recorded command."""
import json
import tempfile
import unittest
from pathlib import Path
from colorset_contract import tokens
from terminal_colorsets import agg_theme, recolor_sgr, write_presentation_cast


class TerminalColorsetTests(unittest.TestCase):
    def test_theme_slots_fit_each_contract(self):
        for mode in ("colorset1", "colorset2"):
            entries = agg_theme(mode).split(",")
            self.assertEqual(len(entries), 18)
            self.assertTrue({"#" + token for token in entries} <= set(tokens(mode)))

    def test_truecolor_indexed_and_colon_keep_text_and_other_attributes(self):
        for sequence in ("38;2;13;27;49", "48;5;27", "38:2::13:27:49", "38:2:0:13:27:49"):
            output = recolor_sgr("\x1b[1;" + sequence + "mLabel\x1b[0m", "colorset1")
            self.assertIn("Label\x1b[0m", output)
            self.assertTrue(output.startswith("\x1b[1;"))
            self.assertNotIn("13;27;49", output)

    def test_dynamic_palette_changes_do_not_escape_theme(self):
        self.assertEqual(recolor_sgr("before\x1b]4;1;#123456\x07after", "colorset1"), "beforeafter")

    def test_split_sgr_preserves_original_and_event_timing(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.cast"
            target = Path(directory) / "render.cast"
            records = [{"version": 2, "width": 80, "height": 24}, [0.1, "o", "A\x1b[38;2;13;"], [0.2, "o", "27;49mB\x1b[0m"], [0.3, "i", "input"]]
            original = "\n".join(json.dumps(record) for record in records) + "\n"
            source.write_text(original, encoding="utf-8")
            write_presentation_cast(source, target, "colorset1")
            observed = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertEqual([record[:2] for record in observed[1:]], [record[:2] for record in records[1:]])
            text = "".join(record[2] for record in observed[1:] if record[1] == "o")
            self.assertTrue(text.startswith("A\x1b[38;2;"))
            self.assertTrue(text.endswith("mB\x1b[0m"))
            self.assertNotIn("13;27;49", text)
            self.assertEqual(observed[-1], records[-1])


if __name__ == "__main__":
    unittest.main()
