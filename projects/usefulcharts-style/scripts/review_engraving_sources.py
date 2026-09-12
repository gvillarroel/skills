#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Render untouched source illustrations on the poster field for visual inspection."""

from pathlib import Path
from playwright.sync_api import sync_playwright


folder=Path(__file__).resolve().parent.parent/'artifacts/images/engraving-sources'
files=sorted(p for p in folder.iterdir() if p.suffix in ('.svg','.png') and p.name!='review.png')
document='<html><style>body{background:#EDEAD8;font:16px Arial;display:flex;flex-wrap:wrap;gap:25px}figure{margin:20px;width:350px}img{width:350px;height:360px;object-fit:contain}</style>'
document+=''.join(f'<figure><img src="{p.as_uri()}"><figcaption>{p.name}</figcaption></figure>' for p in files)
page_path=folder/'review.html';page_path.write_text(document,encoding='utf-8')
with sync_playwright() as p:
    browser=p.chromium.launch();page=browser.new_page(viewport={'width':1250,'height':500})
    page.goto(page_path.as_uri());page.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
    page.screenshot(path=str(folder/'review.png'),full_page=True)
    browser.close()
print('Rendered source illustration review.')
