#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Serve the local artifact gallery on loopback only."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
root=Path(__file__).resolve().parents[1]/'artifacts'
print('Gallery: http://127.0.0.1:8768/index.html',flush=True)
ThreadingHTTPServer(('127.0.0.1',8768),partial(SimpleHTTPRequestHandler,directory=str(root))).serve_forever()
