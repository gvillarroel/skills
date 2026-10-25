#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check frozen generated sources and evidence-readiness scenario dispositions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(run: Path, kind: str) -> dict:
    workspace = run / "workspace"
    checks: list[dict] = []

    def require(name: str, passed: bool):
        checks.append({"name": name, "passed": bool(passed)})

    require("strict-forward", load(run / "evaluation-result.json")["passed"])
    require("immutable-skill", load(run / "skill-integrity-check.json")["passed"])
    if kind == "contract":
        project = workspace / "outputs/agent"
        manifest = load(project / "scaffold-manifest.json")
        require("independent-project", manifest["runtimeIndependent"] is True)
        files = manifest["files"]
        require("generated-instructions-present", {"AGENTS.md", "prompts/pr-reviewer.md"} <= files.keys())
        for name, expected in files.items():
            path = project / name
            require(f"initial-source:{name}", path.is_file() and digest(path) == expected)
        original = workspace / "skills/pi-durable/assets/templates/service"
        for name in ("AGENTS.md", "prompts/pr-reviewer.md"):
            require(f"frozen-template-transfer:{name}", digest(project / name) == digest(original / name))
        require("no-live-state", not (project / "state").exists())
    else:
        cases = load(workspace / "outputs/readiness.json")["cases"]
        expected = {"startup": "insufficient", "path": "bounded-reproduction", "selection": "insufficient"}
        require("exact-scenario-identities", len(cases) == 3 and {case["id"] for case in cases} == set(expected))
        for case in cases:
            name = case["id"]
            require(f"goal-bound-readiness:{name}", case["disposition"] == expected.get(name))
            require(f"scoped-next-step:{name}", all(isinstance(case.get(key), str) and case[key].strip() for key in ("claimScope", "nextStep")))
            missing = case.get("missingObservations")
            require(f"explicit-observation-gaps:{name}", isinstance(missing, list) and (bool(missing) or name == "path") and all(isinstance(item, str) and item.strip() for item in missing))
    return {"passed": all(item["passed"] for item in checks), "kind": kind, "run": str(run), "checks": checks, "manualReviewRequired": "Inspect handoff/prompt/operations prose, read surface and executed commands independently."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--kind", choices=["contract", "naturalistic"], required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check(args.run.resolve(), args.kind)
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "kind": args.kind, "checks": len(result["checks"])}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
