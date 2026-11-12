#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.26", "referencing>=0.37"]
# ///
"""Validate streams with fetched primary v0.9 envelope and host catalog schemas."""
from pathlib import Path
import argparse
import hashlib
import json
from urllib.parse import urldefrag, urlsplit
from urllib.request import urlopen

from jsonschema import Draft202012Validator, Draft7Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "artifacts/data/official-schemas"
ENVELOPE = "https://a2ui.org/specification/v0_9/server_to_client.json"
CATALOG = "https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("messages", nargs="+", type=Path)
    parser.add_argument("--label", default="starter")
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    sources = {}

    def fetch(url):
        url = urldefrag(url)[0]
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname not in {"a2ui.org", "www.gstatic.com"}:
            raise ValueError(f"Unapproved schema source: {url}")
        target = DATA / (hashlib.sha256(url.encode()).hexdigest() + ".json")
        if not target.is_file():
            with urlopen(url, timeout=30) as response:
                raw = response.read()
            json.loads(raw)
            target.write_bytes(raw)
        raw = target.read_bytes()
        sources[url] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    def retrieve(url):
        return Resource.from_contents(fetch(url), default_specification=DRAFT202012)

    registry = Registry(retrieve=retrieve)
    envelope, catalog = fetch(ENVELOPE), fetch(CATALOG)
    # The upstream envelope deliberately references a selected catalog at a
    # relative catalog.json URI. Bind that slot to the actual host union;
    # preserve every official component schema and its original base URI.
    binding_uri = "https://a2ui.org/specification/v0_9/catalog.json"
    binding = {"$id": binding_uri, "$defs": {
        "anyComponent": {"oneOf": [{"$ref": f"{CATALOG}#/components/{name}"}
                                  for name in catalog["components"]]},
        "anyFunction": {"oneOf": [{"$ref": f"{CATALOG}#/functions/{name}"}
                                 for name in catalog["functions"]]},
        "theme": {"type": "object"},
    }}
    registry = registry.with_resources([(ENVELOPE, Resource.from_contents(envelope)),
                                        (CATALOG, Resource.from_contents(catalog)),
                                        (binding_uri, Resource.from_contents(binding, default_specification=DRAFT202012))])
    rows = []
    for path in args.messages:
        errors = []
        messages = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(messages, list) or not messages:
            errors.append("Expected a nonempty stream array.")
            messages = []
        components = 0
        models = {}
        for message in messages:
            update = message.get("updateDataModel", {})
            if update.get("path") == "/":
                models[update.get("surfaceId")] = update.get("value", {})
        for index, message in enumerate(messages):
            errors.extend(f"message {index}: {error.message}" for error in Draft202012Validator(envelope, registry=registry).iter_errors(message))
            for component in message.get("updateComponents", {}).get("components", []):
                name = component.get("component")
                if name not in catalog["components"]:
                    errors.append(f"message {index}: Unknown host component {name!r}")
                    continue
                schema = {**catalog, "$ref": f"#/components/{name}"}
                errors.extend(f"message {index}, component {component.get('id')}: {error.message}" for error in Draft202012Validator(schema, registry=registry).iter_errors(component))
                if name == "VegaChart":
                    spec = component.get("spec", {})
                    if isinstance(spec, dict) and "path" in spec:
                        spec = models.get(message["updateComponents"]["surfaceId"], {})
                        for part in component["spec"]["path"].strip("/").split("/"):
                            spec = spec.get(part, {}) if isinstance(spec, dict) else {}
                    schema_path = ROOT / "artifacts/data/vega-lite-v5.schema.json"
                    if not schema_path.is_file():
                        errors.append("Missing separately pinned Vega-Lite v5 schema.")
                    else:
                        raw = schema_path.read_bytes()
                        sources["https://vega.github.io/schema/vega-lite/v5.json"] = hashlib.sha256(raw).hexdigest()
                        errors.extend(f"VegaChart {component.get('id')}: {error.message}" for error in Draft7Validator(json.loads(raw)).iter_errors(spec))
                if name == "Canvas" and component.get("id") != "root":
                    errors.append("Canvas must be the root of its surface.")
                components += 1
        rows.append({"path": str(path), "passed": not errors, "messages": len(messages), "components": components, "errors": errors})
    report = {"passed": all(row["passed"] for row in rows), "sources": sources,
              "catalog_binding": "Official host component union bound to the envelope's catalog.json slot. Theme-property semantics are outside this check.",
              "streams": rows, "scope": "Official JSON envelope and host catalog validation; A2A transport and Gemini Enterprise paint remain untested."}
    output = DATA.parent / f"a2ui-catalog-{args.label}.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
