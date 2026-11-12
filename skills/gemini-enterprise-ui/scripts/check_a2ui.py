#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check a bounded v0.9 A2UI stream profile; do not certify a host catalog."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


OPERATIONS = {"createSurface", "updateComponents", "updateDataModel", "deleteSurface"}


def check_messages(messages: object) -> dict:
    findings: list[dict] = []
    surfaces: set[str] = set()
    message_count = len(messages) if isinstance(messages, list) else 0

    def add(index: int, code: str, detail: str) -> None:
        findings.append({"message_index": index, "code": code, "detail": detail})

    if not isinstance(messages, list) or not messages:
        add(-1, "invalid-stream", "Expected a nonempty JSON array of message envelopes.")
        messages = []
    for index, envelope in enumerate(messages):
        if not isinstance(envelope, dict):
            add(index, "invalid-envelope", "Expected an object.")
            continue
        if envelope.get("version") != "v0.9":
            add(index, "unsupported-version", "This profile accepts only v0.9 wire messages.")
        operations = OPERATIONS.intersection(envelope)
        if len(operations) != 1 or set(envelope) != {"version", *operations}:
            add(index, "invalid-operation", "Expected version and exactly one known operation.")
            continue
        operation = next(iter(operations))
        payload = envelope[operation]
        if not isinstance(payload, dict):
            add(index, "invalid-payload", "Expected an operation object.")
            continue
        surface = payload.get("surfaceId")
        if not isinstance(surface, str) or not surface:
            add(index, "invalid-surface", "Expected a nonempty surfaceId.")
            continue
        if operation == "createSurface":
            if surface in surfaces:
                add(index, "duplicate-surface", "A live surface cannot be created twice.")
            if not isinstance(payload.get("catalogId"), str) or not payload["catalogId"]:
                add(index, "invalid-catalog", "Expected a nonempty catalogId.")
            surfaces.add(surface)
            continue
        if surface not in surfaces:
            add(index, "unknown-surface", "Create the surface before updating or deleting it.")
            continue
        if operation == "deleteSurface":
            surfaces.remove(surface)
        elif operation == "updateDataModel":
            path = payload.get("path")
            if not isinstance(path, str) or (path != "" and not path.startswith("/")) or re.search(r"~(?![01])", path):
                add(index, "invalid-path", "Expected a JSON Pointer model path.")
            if "value" not in payload:
                add(index, "missing-value", "A model update needs a value, including explicit null.")
        elif operation == "updateComponents":
            components = payload.get("components")
            if not isinstance(components, list) or not components:
                add(index, "invalid-components", "Expected a nonempty complete component tree.")
                continue
            nodes: dict[str, dict] = {}
            for component in components:
                if not isinstance(component, dict):
                    add(index, "invalid-component", "Each component must be an object.")
                    continue
                identifier = component.get("id")
                if not isinstance(identifier, str) or not identifier:
                    add(index, "invalid-id", "Expected a nonempty component ID.")
                    continue
                if identifier in nodes:
                    add(index, "duplicate-id", f"Duplicate component ID: {identifier}")
                nodes[identifier] = component
                if not isinstance(component.get("component"), str) or not component["component"]:
                    add(index, "invalid-type", f"Missing component type: {identifier}")
            if "root" not in nodes:
                add(index, "missing-root", "This profile requires a root component in each update batch.")
            edges: dict[str, list[str]] = {}
            for identifier, component in nodes.items():
                children = component.get("children", [])
                if not isinstance(children, list) or any(not isinstance(child, str) or not child for child in children):
                    add(index, "unsupported-children", "This profile accepts only explicit child ID arrays.")
                    children = []
                if "child" in component:
                    if isinstance(component["child"], str) and component["child"]:
                        children = [*children, component["child"]]
                    else:
                        add(index, "invalid-child", "A child reference must be a nonempty ID.")
                edges[identifier] = children
                for child in children:
                    if child not in nodes:
                        add(index, "unresolved-child", f"{identifier} references missing child {child}.")
            # Iterative traversal keeps malformed deep input from overflowing
            # Python's call stack. This is structural, not renderer validation.
            colors: dict[str, int] = {}
            for start in nodes:
                if colors.get(start):
                    continue
                stack = [(start, False)]
                while stack:
                    identifier, leaving = stack.pop()
                    if leaving:
                        colors[identifier] = 2
                        continue
                    if colors.get(identifier) == 1:
                        add(index, "component-cycle", f"Cycle at component {identifier}.")
                        continue
                    if colors.get(identifier) == 2 or identifier not in nodes:
                        continue
                    colors[identifier] = 1
                    stack.append((identifier, True))
                    stack.extend((child, False) for child in reversed(edges[identifier]))
    return {"passed": not findings, "profile": "v0.9-closed-component-tree",
            "message_count": message_count, "live_surfaces": sorted(surfaces),
            "catalog_schema_validated": False, "host_paint_tested": False,
            "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("messages", type=Path)
    parser.add_argument("--output", type=Path, help="Write the same JSON report to an explicit task path.")
    args = parser.parse_args()
    try:
        result = check_messages(json.loads(args.messages.read_text(encoding="utf-8-sig")))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        result = {"passed": False, "profile": "v0.9-closed-component-tree",
                  "catalog_schema_validated": False, "host_paint_tested": False,
                  "findings": [{"code": "input-error", "detail": str(error)}]}
    rendered = json.dumps(result, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
