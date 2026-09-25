#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Check the published catalog route and all four hierarchy deep links."""

import argparse
import functools
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Live Pages root, or omit to serve local dist/pages.")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    server = None
    if args.url:
        base = args.url.rstrip("/") + "/"
    else:
        handler = functools.partial(QuietHandler, directory=str(root / "dist/pages"))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}/"
    checks, errors = [], []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(base)
            card = page.locator("#example-set-hierarchy-lens")
            checks.append({"check": "catalog-discovery", "ok": card.count() == 1 and "composition" in card.inner_text().lower()})
            card.click()
            page.wait_for_function("document.documentElement.dataset.ready === 'true'")
            checks.append({"check": "catalog-opens-decision", "ok": page.locator('[data-pattern-id="hierarchy-decision-growth"]').count() == 1})
            example = base + "examples/hierarchy-lens/"
            for pattern, target in [("hierarchy-radial-pixels", "radial.html"), ("hierarchy-radial-lenses", "analytical.html"), ("hierarchy-organic-pixels", "organic.html")]:
                page.goto(example + "#" + pattern)
                page.wait_for_url("**/" + target + "#" + pattern)
                page.wait_for_function("document.documentElement.dataset.ready === 'true'")
                checks.append({"check": pattern + "-legacy-redirect", "ok": page.locator('[data-pattern-id="' + pattern + '"]').count() == 1})
            page.goto(example + "#hierarchy-decision-growth")
            page.wait_for_function("document.documentElement.dataset.ready === 'true'")
            checks.append({"check": "decision-link", "ok": page.url == example + "#hierarchy-decision-growth"})
            checks.append({"check": "comparison-links", "ok": page.locator('a[href="radial.html#hierarchy-radial-pixels"]').count() == 1 and page.locator('a[href="analytical.html#hierarchy-radial-lenses"]').count() == 1})
            browser.close()
        checks.append({"check": "no-browser-errors", "ok": not errors})
    except Exception as error:
        errors.append(str(error))
    finally:
        if server:
            server.shutdown()
            server.server_close()
    report = {"ok": not errors and all(c["ok"] for c in checks), "url": base, "checks": checks, "errors": errors}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
