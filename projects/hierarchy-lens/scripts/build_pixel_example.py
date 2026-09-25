#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the compact example and preserve all previously published view links."""

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
build(source, folder / "radial.html", view="pixel")
report = build(source, folder / "index.html", view="organic")
page = folder / "index.html"
redirect = "<script>const legacyViews={'#hierarchy-radial-lenses':'analytical.html','#hierarchy-radial-pixels':'radial.html'};function openLegacyView(){if(legacyViews[location.hash])location.replace(legacyViews[location.hash]+location.hash);}addEventListener('hashchange',openLegacyView);openLegacyView();</script>"
legacy_link = '<p><a style="color:#acd9d3" href="radial.html#hierarchy-radial-pixels">Compare the radial pixel view</a></p><p><a style="color:#acd9d3" href="analytical.html#hierarchy-radial-lenses">Open the labeled hierarchy example</a></p>'
page.write_text(page.read_text(encoding="utf-8").replace("</head>", redirect+"\n</head>").replace("</aside>", legacy_link+"</aside>"), encoding="utf-8")
radial = folder / "radial.html"
backlink = '<p><a style="color:#acd9d3" href="index.html#hierarchy-organic-pixels">Compare the compact organic view</a></p>'
radial.write_text(radial.read_text(encoding="utf-8").replace("</aside>",backlink+"</aside>"),encoding="utf-8")
report["bytes"] = page.stat().st_size
print(json.dumps(report))
