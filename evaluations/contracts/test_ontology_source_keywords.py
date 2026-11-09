"""Verify source-local witness boundaries and exact replay."""

from hashlib import sha256
import importlib.util
from pathlib import Path
import unittest


MODULE = (Path(__file__).resolve().parents[2] / "skills" / "extract-with-ontology"
          / "scripts" / "index_source_keywords.py")
SPEC = importlib.util.spec_from_file_location("index_source_keywords", MODULE)
KEYWORDS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(KEYWORDS)


def plan(text, units=None):
    return {
        "source_sha256": sha256(text.encode()).hexdigest(),
        "keywords": ["MUST", "MUST NOT", "MAY"],
        "units": units or [{"id": "one", "start": 0, "end": len(text)}],
    }


class SourceKeywordTests(unittest.TestCase):
    def test_compound_phrase_keeps_raw_offsets(self):
        text = "café MUST\r\n  NOT be sent. The reader MAY stop."
        found = KEYWORDS.index(text.encode(), plan(text))["witnesses"]
        self.assertEqual([item["keyword"] for item in found], ["MUST NOT", "MAY"])
        self.assertEqual(found[0]["quote"], "MUST\r\n  NOT")
        for item in found:
            self.assertEqual(text[item["start"]:item["end"]], item["quote"])
            context = item["context"]
            self.assertEqual(text[context["start"]:context["end"]], context["quote"])
        self.assertLessEqual(found[0]["context"]["end"], found[1]["start"])

    def test_unit_edges_do_not_accept_partial_matches(self):
        for text, stop in (("MUSTARD", 4), ("MUST NOT continue", 4)):
            with self.subTest(text=text):
                units = [{"id": "prefix", "start": 0, "end": stop}]
                result = KEYWORDS.index(text.encode(), plan(text, units))
                self.assertEqual(result["witnesses"], [])

    def test_unit_order_has_no_effect(self):
        text = "MAY. MUST."
        ranges = [{"id": "first", "start": 0, "end": 4}, {"id": "last", "start": 5, "end": len(text)}]
        first = KEYWORDS.index(text.encode(), plan(text, ranges))
        second = KEYWORDS.index(text.encode(), plan(text, ranges[::-1]))
        self.assertEqual(first, second)
        self.assertEqual([item["unit"] for item in first["witnesses"]], ["first", "last"])

    def test_wrong_digest_and_overlap_are_rejected(self):
        text = "MAY remain."
        with self.assertRaisesRegex(ValueError, "digest"):
            KEYWORDS.index(b"MAY change.", plan(text))
        ranges = [{"id": "a", "start": 0, "end": 5}, {"id": "b", "start": 4, "end": len(text)}]
        with self.assertRaisesRegex(ValueError, "overlap"):
            KEYWORDS.index(text.encode(), plan(text, ranges))

    def test_material_outside_units_is_excluded(self):
        text = "Example MUST.\nThe record MAY."
        units = [{"id": "body", "start": text.index("The"), "end": len(text)}]
        result = KEYWORDS.index(text.encode(), plan(text, units))
        self.assertEqual([item["keyword"] for item in result["witnesses"]], ["MAY"])

    def test_duplicate_ids_are_rejected(self):
        text = "MAY. MUST."
        units = [{"id": "same", "start": 0, "end": 4}, {"id": "same", "start": 5, "end": len(text)}]
        with self.assertRaisesRegex(ValueError, "duplicate ID"):
            KEYWORDS.index(text.encode(), plan(text, units))


if __name__ == "__main__":
    unittest.main()
