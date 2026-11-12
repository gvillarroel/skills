#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Small deterministic MCP server for Codex protocol UI boundary probes."""
import argparse
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--log", type=Path, required=True)
args = parser.parse_args()
args.log.parent.mkdir(parents=True, exist_ok=True)
pending = {}
PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aV1cAAAAASUVORK5CYII="
HTML = '<!doctype html><html lang="en"><body><button id="ui-probe">UI_PROBE_BUTTON</button><script>window.__uiProbeExecuted = true;</script></body></html>'
URI = "ui://codex-ui-probe/card.html"


def emit(message):
    print(json.dumps(message, separators=(",", ":")), flush=True)


def reply(identifier, result):
    emit({"jsonrpc": "2.0", "id": identifier, "result": result})


for line in sys.stdin:
    try:
        message = json.loads(line)
    except json.JSONDecodeError:
        continue
    with args.log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(message) + "\n")
    identifier = message.get("id")
    method = message.get("method")
    params = message.get("params", {})
    if method == "initialize":
        reply(identifier, {"protocolVersion": params["protocolVersion"], "capabilities": {"tools": {}, "resources": {}}, "serverInfo": {"name": "codex-ui-probe", "version": "1.0.0"}})
    elif method == "tools/list":
        tools = []
        for name in ("ui_card", "image", "form", "url", "openai_form", "extended_form"):
            tool = {"name": name, "description": "Deterministic UI boundary probe: " + name, "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}, "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}}
            if name == "ui_card":
                tool["_meta"] = {"ui": {"resourceUri": URI}}
            tools.append(tool)
        reply(identifier, {"tools": tools})
    elif method == "resources/list":
        reply(identifier, {"resources": [{"uri": URI, "name": "UI boundary card", "mimeType": "text/html;profile=mcp-app"}]})
    elif method == "resources/templates/list":
        reply(identifier, {"resourceTemplates": []})
    elif method == "prompts/list":
        reply(identifier, {"prompts": []})
    elif method == "resources/read":
        reply(identifier, {"contents": [{"uri": URI, "mimeType": "text/html;profile=mcp-app", "text": HTML, "_meta": {"ui": {"csp": {"connectDomains": [], "resourceDomains": []}}}}]})
    elif method == "tools/call":
        name = params.get("name")
        if name == "ui_card":
            reply(identifier, {"content": [{"type": "text", "text": "UI_PROBE_FALLBACK: This is a text result, with a separate HTML resource."}], "structuredContent": {"label": "UI_PROBE_CARD", "button": "UI_PROBE_BUTTON"}, "_meta": {"ui": {"resourceUri": URI}, "hiddenProbe": "UI_PROBE_META_ONLY"}})
        elif name == "image":
            reply(identifier, {"content": [{"type": "image", "mimeType": "image/png", "data": PNG}, {"type": "text", "text": "UI_PROBE_PNG"}]})
        elif name in ("form", "url", "openai_form", "extended_form"):
            request_id = "elicitation-" + name
            pending[request_id] = identifier
            request = {"mode": name.replace("_", "/"), "message": "Synthetic UI probe; no account details required."}
            if name == "extended_form":
                request["mode"] = "openai/form"
            if name == "url":
                request.update({"url": "https://example.com/ui-probe", "elicitationId": "synthetic-ui-probe"})
            else:
                request["requestedSchema"] = {"type": "object", "properties": {"choice": {"type": "string", "enum": ["alpha", "beta"]}, "enabled": {"type": "boolean"}}, "required": ["choice"]}
                if name == "extended_form":
                    request["requestedSchema"]["properties"]["record"] = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
            emit({"jsonrpc": "2.0", "id": request_id, "method": "elicitation/create", "params": request})
        else:
            reply(identifier, {"content": [{"type": "text", "text": "Unknown probe tool"}], "isError": True})
    elif identifier in pending and method is None:
        call_id = pending.pop(identifier)
        reply(call_id, {"content": [{"type": "text", "text": json.dumps({"elicitationReply": message.get("result"), "elicitationError": message.get("error")})}]})
    elif method == "ping":
        reply(identifier, {})
    elif identifier is not None:
        emit({"jsonrpc": "2.0", "id": identifier, "error": {"code": -32601, "message": "Unknown fixture method"}})
