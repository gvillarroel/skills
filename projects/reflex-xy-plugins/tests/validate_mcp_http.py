#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0"]
# ///
"""Independent Streamable HTTP MCP client checks for the XY app adapter."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from artifact_contract import inspect_html, inspect_png, inspect_svg


def require(value: object, message: str) -> None:
    if not value:
        raise AssertionError(message)


class MCP:
    def __init__(self, url: str, token: str | None) -> None:
        self.url, self.token, self.session, self.counter = url, token, None, 0
        self.transcript: list[dict] = []

    def send(self, method: str, params: dict | None = None, notification: bool = False) -> dict | None:
        self.counter += 1
        message = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        if not notification:
            message["id"] = self.counter
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                   "MCP-Protocol-Version": "2025-11-25"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        request = urllib.request.Request(self.url, json.dumps(message).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=180) as response:
            self.session = response.headers.get("Mcp-Session-Id", self.session)
            raw = response.read().decode("utf-8")
            status = response.status
            mime = response.headers.get("Content-Type", "")
        if notification and not raw:
            result = None
        elif "text/event-stream" in mime:
            payloads = []
            for line in raw.splitlines():
                if line.startswith("data:"):
                    payload = json.loads(line[5:].strip())
                    if payload.get("id") == message.get("id"):
                        payloads.append(payload)
            require(len(payloads) == 1, "No unambiguous JSON-RPC result in SSE response")
            result = payloads[0]
        else:
            result = json.loads(raw) if raw else None
        self.transcript.append({"method": method, "params": params, "status": status, "response": result})
        if result is not None:
            require(result.get("jsonrpc") == "2.0" and result.get("id") == message.get("id"), "MCP response envelope mismatch")
            require("error" not in result, "JSON-RPC error: " + str(result.get("error")))
            return result.get("result")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8787/mcp")
    parser.add_argument("--token-env", default="XY_MCP_BEARER_TOKEN")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--palettes", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    client = MCP(args.url, os.environ.get(args.token_env))
    palettes = json.loads(args.palettes.read_text(encoding="utf-8"))["colorsets"]
    summary = {"passed": False, "url": args.url, "checks": [], "live_chatgpt_installation": "not_tested"}
    try:
        initialization = client.send("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
            "clientInfo": {"name": "independent-xy-acceptance", "version": "0.1.0"}})
        require(initialization and initialization.get("serverInfo"), "Missing MCP server identity")
        client.send("notifications/initialized", notification=True)
        listed = client.send("tools/list")
        tools = {tool["name"]: tool for tool in listed["tools"]}
        require({"xy_render_chart", "xy_capabilities", "xy_get_reference"} <= set(tools), "Required public tools missing")
        for name, tool in tools.items():
            annotations = tool.get("annotations", {})
            for key in ["readOnlyHint", "destructiveHint", "openWorldHint"]:
                require(isinstance(annotations.get(key), bool), f"{name} lacks explicit {key}")
            require(annotations["readOnlyHint"] is True and annotations["destructiveHint"] is False
                    and annotations["openWorldHint"] is False, f"Unexpected mutation/network tool {name}")
            require(tool.get("inputSchema", {}).get("type") == "object", "Tool input schema missing")
        summary["tools"] = tools
        summary["checks"].append("initialization_and_truthful_tool_metadata")
        capabilities = client.send("tools/call", {"name": "xy_capabilities", "arguments": {}})
        require(not capabilities.get("isError"), "Capabilities tool failed")
        if "structuredContent" in capabilities:
            require(tools["xy_capabilities"].get("outputSchema"), "Capabilities structuredContent lacks outputSchema")
        (args.output_dir / "capabilities-result.json").write_text(json.dumps(capabilities, indent=2) + "\n", encoding="utf-8")
        for topic in ["workflow", "colorsets", "exports"]:
            reference = client.send("tools/call", {"name": "xy_get_reference", "arguments": {"topic": topic}})
            require(not reference.get("isError"), "Bundled skill reference is unavailable")
            require(reference.get("structuredContent", {}).get("topic") == topic, "Reference topic mismatch")
            text = reference.get("structuredContent", {}).get("text")
            require(isinstance(text, str) and 100 < len(text.encode()) <= 32768, "Invalid focused skill reference")
            require(tools["xy_get_reference"].get("outputSchema"), "Reference structuredContent lacks outputSchema")
        summary["checks"].append("canonical_focused_skill_references")
        resources = client.send("resources/list")
        uri = tools["xy_render_chart"].get("_meta", {}).get("ui", {}).get("resourceUri")
        require(uri and uri.startswith("ui://"), "Render tool lacks MCP Apps resource URI")
        require(any(resource["uri"] == uri for resource in resources.get("resources", [])), "UI resource not discoverable")
        resource = client.send("resources/read", {"uri": uri})
        contents = resource["contents"]
        require(len(contents) == 1, "Unexpected component resource shape")
        content = contents[0]
        require(content.get("mimeType") == "text/html;profile=mcp-app", "Incorrect MCP Apps MIME type")
        require(content.get("text") and len(content["text"]) < 3000000, "Missing or oversized component source")
        csp = content.get("_meta", {}).get("ui", {}).get("csp")
        require(isinstance(csp, dict) and "connectDomains" in csp and "resourceDomains" in csp, "Explicit standard resource CSP missing")
        for key, domains in csp.items():
            require(isinstance(domains, list) and all(isinstance(domain, str) and "*" not in domain for domain in domains), f"Broad or invalid CSP {key}")
        summary["resource_uri"] = uri
        summary["resource_meta"] = content.get("_meta")
        summary["checks"].append("discoverable_component_mime_and_csp")
        (args.output_dir / "widget.html").write_text(content["text"], encoding="utf-8")
        for colorset in ["colorset1", "colorset2"]:
            spec = {"preset": "scatter", "colorset": colorset, "title": f"Independent HTTP {colorset}"}
            rendered = client.send("tools/call", {"name": "xy_render_chart", "arguments": {"spec_json": json.dumps(spec)}})
            require(not rendered.get("isError"), "Chart tool reported failure")
            require(isinstance(rendered.get("structuredContent"), dict), "Chart tool lacks structured content")
            require(tools["xy_render_chart"].get("outputSchema"), "Render structuredContent lacks outputSchema")
            (args.output_dir / f"render-{colorset}.json").write_text(json.dumps(rendered, indent=2) + "\n", encoding="utf-8")
            artifact_dir = args.output_dir / colorset
            artifact_dir.mkdir(exist_ok=True)
            downloads = rendered["structuredContent"]["downloads"]
            origin = urllib.parse.urlsplit(args.url)
            for kind, url in downloads.items():
                parsed = urllib.parse.urlsplit(url)
                require((parsed.scheme, parsed.netloc) == (origin.scheme, origin.netloc), "Artifact URL escaped the configured origin")
                with urllib.request.urlopen(url, timeout=30) as artifact:
                    require(artifact.headers.get("Cache-Control") == "no-store", "Chart artifact is browser-cacheable")
                    require(artifact.headers.get("Referrer-Policy") == "no-referrer", "Chart capability may leak via referrer")
                    data = artifact.read()
                extension = {"source": "py", "spec": "json"}.get(kind, kind)
                (artifact_dir / f"chart.{extension}").write_bytes(data)
            palette = palettes[colorset]
            summary.setdefault("native_artifacts", {})[colorset] = {
                "svg": inspect_svg(artifact_dir / "chart.svg", set(palette["allowed"])),
                "png": inspect_png(artifact_dir / "chart.png", palette["roles"]["background"]),
                "html": inspect_html(artifact_dir / "chart.html"),
            }
            svg_url = urllib.parse.urlsplit(downloads["svg"])
            for name, query in [("missing_capability", ""), ("wrong_capability", "token=wrong")]:
                denied = urllib.parse.urlunsplit(svg_url._replace(query=query))
                try:
                    urllib.request.urlopen(denied, timeout=10).close()
                    raise AssertionError(f"Artifact {name} was accessible")
                except urllib.error.HTTPError as denied_response:
                    require(denied_response.code == 404, f"Artifact {name} reveals a non-generic status")
            if "xy_recolor_chart" in tools:
                denied = client.send("tools/call", {"name": "xy_recolor_chart", "arguments": {
                    "render_id": rendered["structuredContent"]["render_id"], "render_key": "A" * 43,
                    "colorset": "colorset2" if colorset == "colorset1" else "colorset1"}})
                require(denied.get("isError") is True, "A wrong render capability could recolor another result")
        summary["checks"].append("real_xy_tool_results_both_palettes")
        summary["checks"].append("native_downloads_and_capability_boundaries")
        invalid = client.send("tools/call", {"name": "xy_render_chart", "arguments": {"spec_json": '{"preset":"__import__","colorset":"colorset1"}'}})
        require(invalid.get("isError") is True, "Hostile chart spec did not return an MCP tool error")
        summary["checks"].append("invalid_spec_is_structured_tool_error")
        auth = {"Authorization": "Bearer " + client.token} if client.token else {}
        probes = [
            ("cross_origin", {"Origin": "https://attacker.invalid"}, b"{}", 403),
            ("unexpected_host", {"Host": "attacker.invalid"}, b"{}", 403),
            ("unsupported_compression", {"Content-Encoding": "gzip"}, b"{}", 400),
            ("oversize_body", {}, b" " * 262145, 400),
        ]
        for name, extra, payload, expected in probes:
            request = urllib.request.Request(args.url, payload, headers={
                "Content-Type": "application/json", "Accept": "application/json, text/event-stream", **auth, **extra}, method="POST")
            try:
                urllib.request.urlopen(request, timeout=10).close()
                raise AssertionError(f"HTTP boundary did not reject {name}")
            except urllib.error.HTTPError as denied:
                require(denied.code == expected, f"Unexpected HTTP status for {name}: {denied.code}")
        summary["checks"].append("http_origin_host_encoding_and_size_boundaries")
        summary["passed"] = True
    except Exception as error:
        summary["failure"] = f"{type(error).__name__}: {error}"
    finally:
        # Headers and authentication tokens are intentionally absent.
        (args.output_dir / "transcript.json").write_text(json.dumps(client.transcript, indent=2) + "\n", encoding="utf-8")
        (args.output_dir / "report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key not in {"tools", "resource_meta"}}))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
