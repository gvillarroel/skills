#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Inspect a local composition without attaching to an account browser."""
import argparse
import functools
import http.server
import json
import sys
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'skills/line-world-video/scripts'))
from inspect_focus import browser_path


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass


def main():
    parser=argparse.ArgumentParser();parser.add_argument('html',type=Path);parser.add_argument('--expression');args=parser.parse_args()
    document=args.html.resolve()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(document.parent)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=browser_path(),headless=True)
            page=browser.new_page(viewport={'width':1920,'height':1080});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/{document.name}')
            try: page.evaluate('async()=>{await document.fonts.ready;await window.ready}')
            except Exception as error: errors.append(str(error))
            data=page.evaluate(args.expression) if args.expression else page.evaluate('''()=>({motion:window.FOCUS_PLAN?.windows,photos:window.PHOTO_FOCUS_PLAN?.bindings?.length,sceneIds:(window.PRODUCTION?.scenes||window.STORY?.beats||[]).map(s=>s.id)})''')
            print(json.dumps({'errors':errors,'data':data}));browser.close()
    finally: server.shutdown();server.server_close()


if __name__=='__main__': main()
