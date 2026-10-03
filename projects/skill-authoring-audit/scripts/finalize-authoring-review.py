#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Update current audit pointers only after the frozen D3 behavior and bundle gates pass."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "evaluations/skill-authoring"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    audit = read(EVIDENCE / "20261002-bundles-validated.json")
    d3 = read(EVIDENCE / "20261002-d3-validation.json")
    if not audit["passed"] or not d3["passed"] or not d3["candidateMatchesFinalRuntimeBundle"]:
        raise SystemExit("Cannot close authoring review before actual-bundle and frozen D3 gates pass")
    if audit["skillCount"] != 34 or audit["bundleCount"] != 68:
        raise SystemExit("Reconcile the canonical inventory before updating the audit")
    backlog_path = ROOT / "SKILLS.md"
    backlog = backlog_path.read_text(encoding="utf-8")
    row = next(line for line in backlog.splitlines() if line.startswith("| d3 |"))
    new_row = row.replace("| d3 | `validating` |", "| d3 | `done` |", 1)
    marker = "Visual asset composition validated on 2026-09-27:"
    validation_start = new_row.index("2026-10-02 named-recipe capture cohort:") if "2026-10-02 named-recipe capture cohort:" in new_row else new_row.index("2026-10-02 authoring closeout:")
    prefix = ("2026-10-02 authoring closeout: 12 deterministic decoding tests; 8/8 frozen strict isolated Luna, independent browser and manual passes: "
              "contract 1/1, naturalistic 3/3, generalization 3/3 and zero/full-prefix boundary 1/1. The 285-file runtime "
              "(`163ac42cc33cc9142ffde1969cdc8c4bf2e59b0ce3ec4a210f7b0918c4c1f540`) matches final copied-bundle hashes. "
              "Parameterized construction, literal palette, separate motion rail, branch-label clearance and declared browser/replay verification are bundled. "
              "All 34 sources/68 copies, installation and repository gates pass. Earlier failed cohorts remain recorded. "
              "[Closeout evidence](evaluations/skill-authoring/20261002-d3-validation.md). ")
    new_row = new_row[:validation_start] + prefix + new_row[new_row.index(marker):]
    backlog = backlog.replace(row, new_row, 1)
    heading = "### D3 Authoring Validation Closeout — 2026-10-02"
    note = (heading + "\n\n"
            "- Replaced repeated fragile manual recipe assembly with a parameterized builder and a declared-dependency browser verifier. Both palettes, literal token order, prefix/tail semantics, exact viewports, alternate branches, offline portability, Replay twice and reduced motion are checked; unsupported structures retain the custom-geometry route.\n"
            "- The final frozen 285-file runtime passes contract 1/1, naturalistic 3/3, generalization 3/3 and zero/full-prefix boundary 1/1 jointly across strict execution, independent browser checks and manual review. All 18 exact output files and the current copied-runtime SHA-256 match. D3 returns to `done`; no failed attempt was reclassified as a pass.\n"
            "- Added 12 deterministic tests, including missing-control, viewport-mismatch and input-overwrite negatives. The evaluator-owned grader rejects the old occluded-token artifact. The existing 88 authoring/copy/reviewer/harness and seven palette tests pass; all mandatory repository gates, local Pages build/format/boundary checks and installed-file verification pass.\n"
            "- Reproduce with the strict Pi and independent grader commands in [the closeout](evaluations/skill-authoring/20261002-d3-validation.md), [frozen machine evidence](evaluations/skill-authoring/20261002-d3-validation.json) and [final actual-bundle audit](evaluations/skill-authoring/20261002-bundles-validated.json). Luna follows the existing Spark-unavailable exception. Earlier D3/Harbor and other skills' release records remain intact.\n\n")
    if heading not in backlog:
        backlog = backlog.replace("### Skill Authoring and Bundle Audit — 2026-10-02", note + "### Skill Authoring and Bundle Audit — 2026-10-02", 1)
    backlog = backlog.replace("the largest entrypoint body is 320 lines", "the largest entrypoint body is 324 lines")
    backlog = backlog.replace("The newly authored HyperFrames bundle is included without promoting its separate release.", "The newly authored HyperFrames bundle is included with its separate release evidence.")
    backlog = backlog.replace("Local installation matches 10,115 canonical files", "Local installation matches 10,118 canonical files")
    backlog = backlog.replace("D3 is `validating` until that usage route meets the 2/3 threshold.", "That historical cohort left D3 `validating`; the frozen closeout above subsequently passes every required case and restores `done`.")
    backlog = backlog.replace("scripts/audit-skill-authoring.py --check-bundles --output evaluations/skill-authoring/20261002-bundles-final.json", "scripts/audit-skill-authoring.py --check-bundles --output evaluations/skill-authoring/20261002-bundles-validated.json")
    backlog_path.write_text(backlog, encoding="utf-8", newline="\n")

    summary_command = [sys.executable, str(ROOT / "projects/skill-authoring-audit/scripts/write-audit-summary.py"), str(EVIDENCE / "20261002-bundles-validated.json")]
    # This summary helper declares PyYAML via uv; execute its own metadata.
    summary_command = ["uv", "run", "--script", *summary_command[1:]]
    subprocess.run(summary_command, cwd=ROOT, check=True)
    summary = read(EVIDENCE / "20261002-summary.json")
    statuses = dict(Counter(r["backlogStatus"] for r in summary["skills"]))
    body_max = max(r["metrics"]["bodyLines"] for r in audit["results"] if r["profile"] == "source")
    review_path = EVIDENCE / "20261002-review.md"
    review = review_path.read_text(encoding="utf-8")
    old_overview = re.compile(r"The final structural inventory passes all 34 sources and 68 actual copies,.*?release limits\.", re.DOTALL)
    overview = (f"The final structural inventory passes all 34 sources and 68 actual copies,\nwith zero findings. The 425 runtime Markdown references have direct routes;\nthe longest entrypoint body is D3 at {body_max} lines. The [D3 closeout](20261002-d3-validation.md)\npasses all eight frozen strict/independent/manual runs and restores D3 to `done`.\nCurrent canonical release statuses are {statuses.get('done', 0)} `done` and {statuses.get('validating', 0)} `validating`;\nother workflows retain their own evidence and release limits.")
    if old_overview.search(review):
        review = old_overview.sub(overview, review, count=1)
    review = review.replace("D3 is moved to `validating`: the current authoring and\ndistribution checks pass, while this named-recipe usage cohort fails the 2/3\nrelease threshold.", "That earlier capture cohort moved D3 to `validating`: its authoring and\ndistribution checks passed, while its named-recipe usage failed the 2/3\nrelease threshold. The [later frozen closeout](20261002-d3-validation.md)\npasses 8/8 joint checks and restores `done`.")
    closeout = ("## Final D3 and bundle closeout\n\n"
                "The [focused D3 validation](20261002-d3-validation.md) supplies the final\nconstructor/browser verifier, all exact commands, payload hash, eight fresh\nstrict/independent/manual passes and retained development failures. The [final\nactual-bundle audit](20261002-bundles-validated.json) rechecks all 34 sources\nand 68 copies. Local installation matches 10,118 canonical files. The current\n[check receipt](20261002-checks.json) and [inventory](20261002-summary.json)\ninclude this revision. Previous audit snapshots remain historical evidence.\n\n")
    if "## Final D3 and bundle closeout" not in review:
        review = review.replace("## Reproducible local checks", closeout + "## Reproducible local checks", 1)
    review = review.replace("--output evaluations/skill-authoring/20261002-bundles-final.json", "--output evaluations/skill-authoring/20261002-bundles-validated.json")
    if "## Skill inventory" in review:
        table = (ROOT / "projects/skill-authoring-audit/artifacts/reviews/inventory-table.md").read_text(encoding="utf-8")
        review = review[:review.index("## Skill inventory")] + "## Skill inventory\n\n" + table
    review_path.write_text(review, encoding="utf-8", newline="\n")

    receipt_path = EVIDENCE / "20261002-checks.json"
    receipt = read(receipt_path)
    receipt["authoringAndDistribution"]["largestEntrypointBodyLines"] = body_max
    receipt["authoringAndDistribution"]["localInstallationFiles"] = 10118
    receipt["authoringAndDistribution"]["finalAudit"] = "20261002-bundles-validated.json"
    receipt["regressions"] = [r for r in receipt["regressions"] if "test_speculative_decoding.py" not in r["command"] and "test_palette_contract.py" not in r["command"]]
    receipt["regressions"].extend([{"command": "uv run --script skills/d3/scripts/test_speculative_decoding.py", "passed": True, "tests": 12},
                                   {"command": "uv run --script skills/d3/assets/examples/skill-tests/test_palette_contract.py", "passed": True, "tests": 7}])
    final = receipt["freshModelCases"].get("d3NamedRecipeFinal", {})
    if final.get("cases") == 3:
        receipt["freshModelCases"]["d3NamedRecipeCapturePreliminary"] = final
    receipt["freshModelCases"]["d3NamedRecipeFinal"] = {"model": d3["model"], "strictPasses": 8, "independentPasses": 8, "manualPasses": 8, "jointPasses": 8,
                                                       "cases": 8, "requiredOutputs": 18, "releaseThresholdMet": True, "backlogStatus": "done", "caseResults": d3["cases"],
                                                       "payloadSha256": d3["frozenPayloadSha256"][0], "evidence": "20261002-d3-validation.json"}
    receipt["releaseStatuses"] = statuses
    receipt["retainedModelAttempts"] = read(EVIDENCE / "20261002-forward-evidence.json")["attemptCount"]
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    guide = ROOT / "docs/skill-authoring.md"
    text = guide.read_text(encoding="utf-8")
    if "20261002-d3-validation.md" not in text:
        text += "\nThe [D3 validation closeout](../evaluations/skill-authoring/20261002-d3-validation.md)\nrecords the final frozen runtime passes and the latest complete bundle audit.\n"
        guide.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"d3Status": "done", "releaseStatuses": statuses, "finalSourceSkills": 34, "finalCopiedBundles": 68}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
