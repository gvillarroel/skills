#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for the D3 recipe consolidation helper."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import consolidate_iteration3_patterns as consolidation


class ConsolidationStateTests(unittest.TestCase):
    def test_recognizes_complete_applied_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pattern_root = Path(temporary)
            routes: list[str] = []
            for collection in consolidation.COLLECTIONS:
                sections: list[str] = []
                for filename in collection.sources:
                    pattern_id = f"d3-{Path(filename).stem}"
                    sections.append(f"## {pattern_id}\n")
                    routes.append(
                        f"references/patterns/{collection.filename}#{pattern_id}"
                    )
                (pattern_root / collection.filename).write_text(
                    "\n".join(sections), encoding="utf-8"
                )

            report = consolidation.applied_state_report(
                pattern_root, "\n".join(routes)
            )

            self.assertIsNotNone(report)
            assert report is not None
            self.assertEqual(report["state"], "already-applied")
            self.assertEqual(report["runtimeFileDelta"], -30)
            self.assertEqual(report["patternRoutesPreserved"], 33)


if __name__ == "__main__":
    unittest.main()
