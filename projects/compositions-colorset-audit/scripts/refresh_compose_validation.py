#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Attach the final unchanged-byte composition validation without losing handoff data."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
path = ROOT / "evaluations/colorset-audit/compositions-20261002.json"
data = json.loads(path.read_text())
entry = next(entry for entry in data["skills"] if entry["skill"] == "compose-synchronized-svg")
run_id = "colorset-compose-synchronized-svg-20261002-8"
folder = ROOT / "evaluations/runs" / run_id
result = json.loads((folder / "evaluation-result.json").read_text())
integrity = json.loads((folder / "skill-integrity-check.json").read_text())
artifacts = json.loads((folder / "artifact-check.json").read_text())
assert result["passed"] and all(value is not False for value in result["gates"].values())
entry["isolatedValidation"] = {
    "runId": run_id, "model": "gpt-5.6-luna", "strict": True, "passed": result["passed"],
    "gates": result["gates"], "skillDigest": integrity["beforeDigest"],
    "outputs": [{"path": output["path"], "sha256": output["sha256"]} for output in artifacts["outputs"]],
    "traceSummaryCommand": f"uv run --script scripts/summarize-pi-json-events.py evaluations/runs/{run_id}/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error",
}
entry["supersededValidation"] = {
    "runId": "colorset-compose-synchronized-svg-20261002-7", "passed": True,
    "reason": "Accepted before the test_synchronized_svg_tools.py fixture diagnostic changed. Root's exact-byte closure audit detected the digest difference; run8 validates the current unchanged bundle.",
}
entry["testedCommands"].append({
    "command": f"uv run --script scripts/validate-colorsets.py --input evaluations/runs/{run_id}/workspace/output/diagram.svg --colorset colorset1",
    "result": "Final strict output passed exact colorset1 check; 0 findings", "passed": True,
})
data["allStrictPassed"] = all(entry["isolatedValidation"]["passed"] for entry in data["skills"])
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
markdown = ROOT / "evaluations/colorset-audit/compositions-20261002.md"
text = markdown.read_text().replace("colorset-compose-synchronized-svg-20261002-7", run_id)
text = text.replace("Earlier failures remain evidence:", "The earlier composition run7 passed its original payload. The root's final exact-byte audit found that one test fixture file changed afterward; run8 was repeated with the current frozen bundle and accepted digest `55c47702247f003387a31d5a1b83f2fd1524c2e230d51bcbd7e5d2ef87a1f633`. Its five exact outputs, strict event/model/read-surface gates and payload integrity passed; the final SVG independently passed colorset1 with zero findings.\n\nEarlier failures remain evidence:")
markdown.write_text(text, encoding="utf-8")
helper = ROOT / "projects/compositions-colorset-audit/scripts/finalize_coverage.py"
helper.write_text(helper.read_text().replace('"compose-synchronized-svg": 7,', '"compose-synchronized-svg": 8,'), encoding="utf-8")
print(json.dumps({"runId": run_id, "skillDigest": integrity["beforeDigest"], "allStrictPassed": data["allStrictPassed"]}, indent=2))
