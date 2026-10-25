#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently inspect a console-creation forward trial without running its code."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


def evaluate(workspace: Path) -> dict:
    workspace = workspace.resolve(strict=True)
    output = workspace / "outputs"
    console = output / "console"
    checks: list[dict] = []

    def check(name: str, action):
        try:
            detail = action()
            checks.append({"name": name, "passed": True, "detail": detail})
        except Exception as error:
            checks.append({"name": name, "passed": False, "error": str(error)})

    def resources():
        manifest = json.loads((console / "scaffold-manifest.json").read_text(encoding="utf-8"))
        assert manifest["runtimeIndependent"] and manifest["agentCreationIncluded"]
        files = manifest["files"]
        for name in ("src/agent-creation.ts", "src/creation-ui.ts", "src/creation-review.ts", "service-template/src/tools/workspace.ts", "service-template/package-lock.json"):
            assert name in files, name
        for name, digest in files.items():
            path = (console / name).resolve(strict=True)
            assert path.is_relative_to(console.resolve()), name
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
        registry = json.loads((console / "durable-agents.json").read_text(encoding="utf-8"))
        assert registry == {"version": 1, "services": []}
        return {"authoredFiles": len(files), "emptyRegistry": True}

    def plan():
        value = json.loads((output / "plan.json").read_text(encoding="utf-8"))
        folder = (output / "workspace with spaces").resolve(strict=True)
        assert folder.is_dir()
        assert value["id"] == "workspace-helper" and value["name"] == "Workspace helper"
        assert Path(value["baseDir"]).resolve() == folder
        assert Path(value["projectDir"]).resolve() == folder / ".pi/durable/workspace-helper"
        assert not Path(value["projectDir"]).exists(), "Preparation started or wrote the service project."
        assert value["provider"] == "faux" and value["requestedModel"] == "latest:sol" and value["task"] == "coding"
        assert value["target"] == "workspace-helper/workspace-helper"
        assert not value.get("repository"), "Unexpected event subscription."
        assert value["instructions"] == "Read requested source files and report observable findings."
        return {"chosenFolder": str(folder), "projectNotCreated": True}

    def notes():
        text = (output / "report.md").read_text(encoding="utf-8")
        for expression in (r"/durable new", r"/durable(?: list)?", r"/durable-chat", r"(?:base|working|workspace) folder", r"(?:PgUp|PgDn|scroll)", r"(?:RPC|rpc)", r"(?:login|log.out|logout)"):
            assert re.search(expression, text, re.I), expression
        assert "workspace_list" in text and "workspace_read" in text, "Local tool scope is missing."
        assert re.search(r"(?:no|neither)\b[^.\n]{0,100}\b(?:shell|writ|edit)", text, re.I), "Local tool limits are missing."
        assert len(text) > 600, "Operational notes are incomplete."
        return {"characters": len(text)}

    check("Independent hashed factory payload and empty registry", resources)
    check("Exact folder/model plan without creation or startup", plan)
    check("Reviewable Pi operations and scope notes", notes)
    return {"passed": all(item["passed"] for item in checks), "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(args.workspace)
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(args.workspace.resolve()) or target.exists():
            parser.error("Write the evaluator receipt to a new file outside the candidate workspace.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
