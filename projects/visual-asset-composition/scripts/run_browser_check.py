#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Run an existing browser check with installed Edge, without changing its checks."""
import functools
from pathlib import Path
import runpy
import sys
from playwright.sync_api import BrowserType

original_launch = BrowserType.launch
BrowserType.launch = functools.partialmethod(original_launch, channel="msedge")
target = Path(sys.argv[1]).resolve()
sys.argv = [str(target), *sys.argv[2:]]
runpy.run_path(str(target), run_name="__main__")
