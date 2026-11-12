#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify saved synthetic Claude Desktop observations without a model call."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "projects/desktop-plugin-ui/artifacts/cross-assistant"
CAPTURES = ARTIFACTS / "claude-desktop-live"


def read(name: str) -> str:
    return (CAPTURES / name).read_text(encoding="utf-8")


def main() -> int:
    events = [json.loads(line)["event"] for line in read("events.jsonl").splitlines() if line]
    initial, increment, invalid = [read(name) for name in ("initial-ui.txt", "increment-ui.txt", "invalid-ui.txt")]
    fullscreen, context = [read(name) for name in ("fullscreen-ui.txt", "context-and-caps-ui.txt")]
    sandbox = read("sandbox-ui.txt")
    returned = read("return-inline-ui.txt")
    restoration = json.loads((ARTIFACTS / "desktop-config/restoration.json").read_text(encoding="utf-8-sig"))
    checks = {
        "actual_ui_extension_negotiated": any("io.modelcontextprotocol/ui" in e.get("capabilities", {}).get("extensions", {}) for e in events),
        "resource_read_and_open_called_once": sum(e.get("kind") == "resource-read" for e in events) == 1 and sum(e.get("name") == "ui_limits_open" for e in events) == 1,
        "initial_paint_connected_value7": "Connected to actual host" in initial and bool(re.search(r"\d+ text 7\n", initial)),
        "direct_increment_value8": '"action": "increment"' in increment and '"value": 8' in increment and sum(e.get("name") == "ui_probe_increment" for e in events) == 1,
        "schema_error_preserves_value8": "-32602" in invalid and '"isError": true' in invalid and bool(re.search(r"\d+ text 8\n", invalid)),
        "actual_fullscreen_and_preserved8": "Close fullscreen" in fullscreen and '"mode": "fullscreen"' in fullscreen and bool(re.search(r"\d+ text 8\n", fullscreen)),
        "context_ack_no_additional_chat_article": '"action": "context", "result": {}' in context and "Message 2 of 2" in context and "Message 3 of" not in context,
        "immediate_proxy_and_no_openai_bridge": '"parentDom": "MCP-UI Proxy"' in sandbox and '"openaiBridge": "undefined"' in sandbox,
        "modes_inline_fullscreen_not_pip": '"availableDisplayModes": [ "inline", "fullscreen" ]' in context and "button (disabled) Picture in picture" in context,
        "download_consent_and_cancel": "alert dialog Download file" in read("download-request-ui.txt") and '"action": "download", "result": { "isError": true }' in read("download-cancel-ui.txt"),
        "link_consent_and_cancel": "alert dialog Open external link" in read("link-request-ui.txt") and '"action": "link", "result": { "isError": true }' in read("link-cancel-ui.txt"),
        "return_inline_preserves8": "Close fullscreen" not in returned and '"displayMode": "inline"' in returned and bool(re.search(r"\d+ text 8\n", returned)),
        "configuration_exactly_restored": restoration.get("originalBytesRestored") is True and restoration.get("temporaryServerPresent") is False,
    }
    screenshots = {}
    for name in ("initial-ui.jpg", "fullscreen-ui.jpg"):
        raw = (CAPTURES / name).read_bytes()
        screenshots[name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    checks["actual_screenshots_retained"] = all(row["bytes"] > 1000 for row in screenshots.values())
    result = {"passed": all(checks.values()), "checks": checks, "assertions": len(checks), "screenshots": screenshots, "scope": "Saved actual Desktop Chat captures; no re-execution or model request"}
    (CAPTURES / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
