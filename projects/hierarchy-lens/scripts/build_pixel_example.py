#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the decision composer and preserve every previously published view."""

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
build(source, folder / "organic.html", view="organic")
policy = json.loads((folder / "composition.json").read_text(encoding="utf-8"))
report = build(source, folder / "index.html", view="decision", initial_lens="role", composition=policy)
page = folder / "index.html"
redirect = "<script>const legacyViews={'#hierarchy-radial-lenses':'analytical.html','#hierarchy-radial-pixels':'radial.html','#hierarchy-organic-pixels':'organic.html'};function openLegacyView(){if(legacyViews[location.hash])location.replace(legacyViews[location.hash]+location.hash);}addEventListener('hashchange',openLegacyView);openLegacyView();</script>"
legacy_link = '<p><a style="color:#acd9d3" href="organic.html#hierarchy-organic-pixels">Compare the geometric organic view</a></p><p><a style="color:#acd9d3" href="radial.html#hierarchy-radial-pixels">Compare the radial pixel view</a></p><p><a style="color:#acd9d3" href="analytical.html#hierarchy-radial-lenses">Open the labeled hierarchy example</a></p>'
page.write_text(page.read_text(encoding="utf-8").replace("</head>", redirect+"\n</head>").replace("</aside>", legacy_link+"</aside>"), encoding="utf-8")
backlink = '<p><a style="color:#acd9d3" href="index.html#hierarchy-decision-growth">Open the decision composer</a></p>'
for name in ["radial.html", "organic.html"]:
    previous = folder / name
    previous.write_text(previous.read_text(encoding="utf-8").replace("</aside>",backlink+"</aside>"),encoding="utf-8")
report["bytes"] = page.stat().st_size
print(json.dumps(report))
