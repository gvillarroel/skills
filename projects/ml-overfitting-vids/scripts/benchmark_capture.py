#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "resvg-py==0.5.0"]
# ///
"""Measure local authored composition capture costs."""
from pathlib import Path
import os,time,json
from playwright.sync_api import sync_playwright
import resvg_py
root=Path(__file__).resolve().parent.parent/'artifacts/composition'
cache=Path(os.environ['LOCALAPPDATA'])/'ms-playwright';path=next(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=str(path),headless=True);page=b.new_page(viewport={'width':1920,'height':1080});page.goto((root/'index.html').as_uri());page.evaluate('document.fonts.ready')
    for method in ['browser','resvg']:
        start=time.perf_counter()
        for i in range(5):
            page.evaluate('t=>renderAt(0,t)',i*.1)
            if method=='browser':page.screenshot(type='png')
            else:resvg_py.svg_to_bytes(svg_string=page.locator('#stage').evaluate('e=>e.outerHTML'),font_files=[str(root/'space-grotesk.ttf')],skip_system_fonts=True)
        print(json.dumps({'method':method,'secondsPerFrame':(time.perf_counter()-start)/5}),flush=True)
    b.close()
