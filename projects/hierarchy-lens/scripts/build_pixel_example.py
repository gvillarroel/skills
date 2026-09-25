#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the pixel acceptance page and preserve the original analytical link."""

import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[3]
skill = root / "skills/hierarchy-lens"
sys.path.insert(0, str(skill / "scripts"))
from build_explorer import build

folder = skill / "assets/examples/hierarchy-lens"
source = json.loads((folder / "organization.json").read_text(encoding="utf-8"))
build(source, folder / "analytical.html")
report = build(source, folder / "index.html", view="pixel")
page = folder / "index.html"
redirect = "<script>if(location.hash==='#hierarchy-radial-lenses')location.replace('analytical.html'+location.hash);</script>"
legacy_link = '<p><a style="color:#acd9d3" href="analytical.html#hierarchy-radial-lenses">Open the labeled hierarchy example</a></p>'
page.write_text(page.read_text(encoding="utf-8").replace("</head>", redirect+"\n</head>").replace("</aside>", legacy_link+"</aside>"), encoding="utf-8")
print(json.dumps(report))
