#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Synthetic MCP state, media, progress and form fixtures; no external actions."""

import argparse
import base64
import io
import json
import os
import sys
import wave
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--log", type=Path, required=True)
args = parser.parse_args()
args.log.parent.mkdir(parents=True, exist_ok=True)
pending = {}
state = {"value": 0, "version": 0}
HTML_URI = "ui://codex-feature-study/panel.html"
CSV_URI = "resource://codex-feature-study/sample.csv"
SVG_URI = "resource://codex-feature-study/chart.svg"
HTML = '<!doctype html><html lang="en"><title>Feature study</title><body style="color:#333e48;background:#ffffff"><button id="feature-study">Synthetic action</button><script>window.FEATURE_PANEL_READY=true;</script></body></html>'
SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="40"><title>Synthetic chart</title><rect width="100" height="40" fill="#ffffff"/><rect x="10" y="10" width="60" height="20" fill="#9e1b32"/></svg>'
wav_buffer = io.BytesIO()
with wave.open(wav_buffer, "wb") as audio:
    audio.setnchannels(1)
    audio.setsampwidth(2)
    audio.setframerate(8000)
    audio.writeframes(b"\0\0" * 80)
WAV = base64.b64encode(wav_buffer.getvalue()).decode("ascii")
TOOLS = ("panel", "state_get", "state_set", "audio", "resource_link", "embedded_resource", "progress",
         "form_types", "form_decline", "form_cancel", "openai_flat", "openai_alias", "nested_invalid", "bad_content")


def emit(message):
    print(json.dumps(message, separators=(",", ":")), flush=True)


def reply(identifier, result):
    emit({"jsonrpc": "2.0", "id": identifier, "result": result})


def result(identifier, text, data=None, error=False):
    payload = {"content": [{"type": "text", "text": text}], "isError": error}
    if data is not None:
        payload["structuredContent"] = data
    reply(identifier, payload)


for line in sys.stdin:
    try:
        message = json.loads(line)
    except json.JSONDecodeError:
        continue
    with args.log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"pid": os.getpid(), "message": message}) + "\n")
    identifier = message.get("id")
    method = message.get("method")
    params = message.get("params", {})
    if method == "initialize":
        reply(identifier, {"protocolVersion": params["protocolVersion"], "capabilities": {"tools": {}, "resources": {}},
                           "serverInfo": {"name": "codex-feature-study", "version": "1.0.0"}})
    elif method == "tools/list":
        tools = [{"name": name, "description": "Synthetic feature study: " + name,
                  "inputSchema": {"type": "object", "properties": {}, "additionalProperties": True},
                  "annotations": {"readOnlyHint": name != "state_set", "destructiveHint": False, "openWorldHint": False}}
                 for name in TOOLS]
        tools[0]["_meta"] = {"ui": {"resourceUri": HTML_URI}}
        reply(identifier, {"tools": tools})
    elif method == "resources/list":
        reply(identifier, {"resources": [{"uri": uri, "name": name, "mimeType": mime} for uri, name, mime in (
            (HTML_URI, "Synthetic panel", "text/html;profile=mcp-app"),
            (CSV_URI, "Synthetic CSV", "text/csv"), (SVG_URI, "Synthetic chart", "image/svg+xml"))]})
    elif method in ("resources/templates/list", "prompts/list"):
        reply(identifier, {"resourceTemplates": []} if method.startswith("resources") else {"prompts": []})
    elif method == "resources/read":
        uri = params.get("uri")
        mime, text = {HTML_URI: ("text/html;profile=mcp-app", HTML), CSV_URI: ("text/csv", "id,title,value\nsample-1,Synthetic record,1\n"), SVG_URI: ("image/svg+xml", SVG)}.get(uri, ("text/plain", "Unknown synthetic resource"))
        reply(identifier, {"contents": [{"uri": uri, "mimeType": mime, "text": text}]})
    elif method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        if name == "panel":
            reply(identifier, {"content": [{"type": "text", "text": "Synthetic panel fallback"}],
                               "structuredContent": state, "_meta": {"ui": {"resourceUri": HTML_URI}, "fixture": "metadata-only"}})
        elif name == "state_get":
            result(identifier, "Synthetic authoritative state", state)
        elif name == "state_set":
            if arguments.get("expectedVersion") != state["version"]:
                result(identifier, "Stale version; the synthetic value is unchanged.", state, error=True)
            else:
                state = {"value": state["value"] + 1, "version": state["version"] + 1}
                result(identifier, "Synthetic value updated.", state)
        elif name == "audio":
            reply(identifier, {"content": [{"type": "audio", "mimeType": "audio/wav", "data": WAV}, {"type": "text", "text": "Ten milliseconds of synthetic silence."}]})
        elif name == "resource_link":
            reply(identifier, {"content": [{"type": "resource_link", "uri": CSV_URI, "name": "Synthetic CSV", "mimeType": "text/csv", "description": "Synthetic export data; no OS download is asserted."}]})
        elif name == "embedded_resource":
            reply(identifier, {"content": [{"type": "resource", "resource": {"uri": SVG_URI, "mimeType": "image/svg+xml", "text": SVG}}]})
        elif name == "progress":
            token = params.get("_meta", {}).get("progressToken", "synthetic-progress")
            for progress in (0, 1):
                emit({"jsonrpc": "2.0", "method": "notifications/progress", "params": {"progressToken": token, "progress": progress, "total": 1, "message": "Synthetic progress"}})
            result(identifier, "Synthetic progress complete.", {"complete": True})
        elif name in ("form_types", "form_decline", "form_cancel", "openai_flat", "openai_alias", "nested_invalid"):
            schema = {"type": "object", "properties": {"choice": {"type": "string", "enum": ["alpha", "beta"]}}, "required": ["choice"]}
            if name == "form_types":
                schema["properties"].update({"title": {"type": "string", "minLength": 1}, "count": {"type": "integer", "minimum": 0, "maximum": 3}, "enabled": {"type": "boolean"}, "tags": {"type": "array", "items": {"type": "string", "enum": ["one", "two"]}, "minItems": 1}})
            if name == "nested_invalid":
                schema["properties"]["nested"] = {"type": "object", "properties": {"name": {"type": "string"}}}
            mode = "openaiForm" if name == "openai_alias" else "openai/form" if name in ("openai_flat", "nested_invalid") else "form"
            request_id = "synthetic-" + name
            pending[request_id] = identifier
            emit({"jsonrpc": "2.0", "id": request_id, "method": "elicitation/create", "params": {"mode": mode, "message": name + ": Synthetic input only.", "requestedSchema": schema}})
        elif name == "bad_content":
            reply(identifier, {"content": [{"type": "synthetic_unknown_content", "text": "Deliberately invalid MCP content variant."}]})
        else:
            result(identifier, "Unknown synthetic tool.", error=True)
    elif identifier in pending and method is None:
        result(pending.pop(identifier), json.dumps({"elicitationReply": message.get("result"), "elicitationError": message.get("error")}))
    elif method == "ping":
        reply(identifier, {})
    elif identifier is not None:
        emit({"jsonrpc": "2.0", "id": identifier, "error": {"code": -32601, "message": "Unknown synthetic method"}})
