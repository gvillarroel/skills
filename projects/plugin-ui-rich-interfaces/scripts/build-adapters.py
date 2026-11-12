#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build independent host adapters from the common synthetic observation set."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = "https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json"


def stream(surface, components, model):
    return [{"version": "v0.9", "createSurface": {"surfaceId": surface, "catalogId": CATALOG}},
            {"version": "v0.9", "updateComponents": {"surfaceId": surface, "components": components}},
            {"version": "v0.9", "updateDataModel": {"surfaceId": surface, "path": "/", "value": model}}]


def main():
    data = json.loads((ROOT / "data/observatory.json").read_text(encoding="utf-8"))
    for relative in ["claude/assets/data.ts", "pi/data.ts"]:
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("// Generated from the shared synthetic dataset.\nexport const DATA = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")
    output = ROOT / "artifacts/payloads/gemini"
    output.mkdir(parents=True, exist_ok=True)
    services = [{"service": s["name"], "state": s["status"], "latency": f'{s["p95"]} ms', "errors": f'{s["error"]:.2f}%', "team": s["team"]} for s in data["services"]]
    selected = next(s for s in data["services"] if s["id"] == "payments")
    spec = {"$schema": "https://vega.github.io/schema/vega-lite/v5.json", "description": "Synthetic hourly Payments P95 latency; UTC; milliseconds.", "width": "container", "height": 260, "data": {"values": selected["history"]}, "layer": [
        {"mark": {"type": "line", "color": "#9e1b32", "point": True}, "encoding": {"x": {"field": "hour", "type": "quantitative", "title": "Hour (UTC)", "scale": {"domain": [0, 23]}}, "y": {"field": "p95", "type": "quantitative", "title": "P95 latency (ms)", "scale": {"domain": [0, 350]}}}},
        {"data": {"values": [{"objective": 250}]}, "mark": {"type": "rule", "color": "#696969", "strokeDash": [4, 4]}, "encoding": {"y": {"field": "objective", "type": "quantitative"}}}]}
    components = [
        {"id": "root", "component": "MaterialColumn", "children": ["title", "summary", "tabs"]},
        {"id": "title", "component": "MaterialText", "text": "Service Observatory · synthetic data"},
        {"id": "summary", "component": "MaterialText", "text": "12 services · 13 directed relationships · Payments P95 268 ms · objective 250 ms"},
        {"id": "tabs", "component": "MaterialTabs", "activeTab": {"path": "/activeTab"}, "ariaLabel": "Service analysis", "tabs": [{"label": "Metrics", "content": "metric-content"}, {"label": "Service table", "content": "records"}, {"label": "Dependencies", "content": "relationships"}]},
        {"id": "metric-content", "component": "MaterialColumn", "children": ["chart", "objective", "exact"]},
        {"id": "chart", "component": "VegaChart", "spec": {"path": "/chart"}, "height": 300},
        {"id": "objective", "component": "MaterialText", "text": "Dashed rule: 250 ms objective. The latest observation is 268 ms. Exact values follow."},
        {"id": "exact", "component": "MaterialTable", "caption": "Payments hourly P95 latency (synthetic)", "ariaLabel": "Exact hourly P95 latency", "columns": [{"header": "UTC hour", "field": "hour"}, {"header": "P95 (ms)", "field": "p95"}], "rows": [{"hour": f'{p["hour"]:02}:00', "p95": str(p["p95"])} for p in selected["history"]]},
        {"id": "records", "component": "MaterialTable", "caption": "Synthetic service observations", "ariaLabel": "Service state and current metrics", "columns": [{"header": "Service", "field": "service"}, {"header": "State", "field": "state"}, {"header": "P95", "field": "latency"}, {"header": "Errors", "field": "errors"}, {"header": "Team", "field": "team"}], "rows": {"path": "/services"}},
        {"id": "relationships", "component": "MaterialTable", "caption": "Directed dependencies; no quantitative flow conservation is implied", "ariaLabel": "Directed service relationships", "columns": [{"header": "Source", "field": "source"}, {"header": "Target", "field": "target"}, {"header": "Kind", "field": "kind"}, {"header": "Rate", "field": "rate"}], "rows": [{"source": e["source"], "target": e["target"], "kind": e["kind"], "rate": str(e["rps"])} for e in data["edges"]]},
    ]
    native = stream("observatory-native", components, {"activeTab": 0, "services": services, "chart": spec})
    html = (ROOT / "artifacts/packages/service-observatory/standalone.html").read_text(encoding="utf-8")
    # The embed is a snapshot with local interactions only. No server refresh,
    # external fetch, model action or host event wrapper is fabricated.
    embed_script = "document.getElementById('refresh').hidden=true;document.getElementById('export').hidden=true;window.ServiceObservatory.setConnection('Embedded snapshot · local inspection');"
    html = html.replace("</body>", "<script>" + embed_script + "</script></body>")
    canvas = stream("observatory-canvas", [
        {"id": "root", "component": "Canvas", "children": ["embed"], "autoOpen": False, "autoFullscreen": False, "cardTitle": "Service Observatory", "cardDescription": "Explore 12 synthetic services, metrics and exact values", "cardIcon": "hub"},
        {"id": "embed", "component": "IFrameSrcdoc", "title": "Synthetic service dependencies and metrics", "height": 1120, "htmlContent": html},
    ], {})
    for name, messages in [("native", native), ("canvas", canvas)]:
        (output / f"{name}-messages.json").write_text(json.dumps(messages, indent=2) + "\n", encoding="utf-8")
    catalog = ROOT / "artifacts/data/gemini-catalog.json"
    (output / "source-manifest.json").write_text(json.dumps({"catalog": CATALOG, "retrieved": "2026-11-12", "sha256": hashlib.sha256(catalog.read_bytes()).hexdigest(), "scope": "Official component schema inspection; no Gemini Enterprise deployment or paint claim.", "alternatives": ["Native MaterialTabs/MaterialTable + VegaChart", "User-opened Canvas root + self-contained IFrameSrcdoc with connect-src none"]}, indent=2) + "\n", encoding="utf-8")
    print("Built independent native Claude Code, Pi, and two Gemini Enterprise adapter variants.")


if __name__ == "__main__":
    main()
