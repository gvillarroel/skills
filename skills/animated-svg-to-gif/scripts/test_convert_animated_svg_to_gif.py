from __future__ import annotations

import argparse
import runpy
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("convert_animated_svg_to_gif.py")
RESOLVE_OUTPUT_DIRECTORY = runpy.run_path(str(SCRIPT))["resolve_output_directory"]


class OutputDirectoryTests(unittest.TestCase):
    def test_named_output_keeps_run_manifest_beside_gif(self) -> None:
        args = argparse.Namespace(
            output=Path("projects/demo/artifacts/gifs/pulse.gif"),
            output_dir=Path("unused-default"),
        )

        self.assertEqual(
            RESOLVE_OUTPUT_DIRECTORY(args),
            Path("projects/demo/artifacts/gifs").resolve(),
        )

    def test_batch_output_uses_output_directory(self) -> None:
        args = argparse.Namespace(
            output=None,
            output_dir=Path("projects/demo/artifacts/gifs/batch"),
        )

        self.assertEqual(
            RESOLVE_OUTPUT_DIRECTORY(args),
            Path("projects/demo/artifacts/gifs/batch").resolve(),
        )


if __name__ == "__main__":
    unittest.main()
