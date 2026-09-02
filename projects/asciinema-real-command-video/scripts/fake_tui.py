#!/usr/bin/env python3
"""Small deterministic TUI target for exercising timed PTY input."""

from __future__ import annotations

import sys
import time


def main() -> int:
    print("REAL FAKE TUI PROCESS", flush=True)
    while True:
        try:
            prompt = input("READY> ")
        except EOFError:
            return 1
        if prompt == "/exit":
            print("TUI closed normally.", flush=True)
            return 0
        print("Processing real PTY input...", flush=True)
        time.sleep(0.4)
        print(f"REAL RESPONSE: {prompt[::-1]}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
