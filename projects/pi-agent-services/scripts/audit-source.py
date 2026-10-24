#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record the canonical skill payload and verify its frozen forward-test copy."""
from pathlib import Path
import json
import runpy
import tempfile

project = Path(__file__).resolve().parents[1]
root = project.parents[1]
harness = runpy.run_path(str(root / "scripts/run-pi-skill-eval.py"))
artifact = project / "artifacts/manifests"
artifact.mkdir(parents=True, exist_ok=True)
results = {}
with tempfile.TemporaryDirectory(prefix="skill-audit-", dir=artifact) as temporary:
    for profile in ("runtime", "full"):
        destination = Path(temporary) / profile / "pi-durable"
        harness["copy_skill_only"](root / "skills/pi-durable", destination, profile)
        snapshot = harness["snapshot_tree"](destination)
        results[profile] = {"fileCount": len(snapshot), "payloadSha256": harness["snapshot_digest"](snapshot)}
run = root / "evaluations/runs/pi-durable-codex-bridge-20261024-final-2"
copy = harness["snapshot_tree"](run / "workspace/skills/pi-durable")
results["frozenCopyMatches"] = harness["snapshot_digest"](copy) == results["runtime"]["payloadSha256"]
assert results["frozenCopyMatches"], "The forward test must use the final canonical payload."
results["localInstallationMatches"] = harness["snapshot_tree"](root / ".agents/skills/pi-durable") == harness["snapshot_tree"](root / "skills/pi-durable")
assert results["localInstallationMatches"], "The repository-local Pi Durable installation must match the canonical bundle."
(artifact / "skill-payload.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2))
