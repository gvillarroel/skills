#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize all retained rich-interface attempts and explicitly frozen cohorts."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[3]
PROJECT = REPO / "projects/plugin-ui-rich-interfaces"
OUTPUT = PROJECT / "artifacts/evaluations"
LATEST = {
    "desktop-chat-plugin-ui": ["sol-2", "sol-3", "sol-4"],
    "chatgpt-desktop-plugin-ui": ["sol-2", "sol-3", "sol-4"],
    "code-native-plugin-ui": ["final-1", "final-2", "final-3"],
    "pi-extension-ui": ["pi-final-1", "pi-final-2", "pi-final-3"],
    "codex-plugin-ui": ["polish-1", "polish-2", "polish-3"],
    "gemini-enterprise-ui": ["final-1", "final-2", "final-3"],
    "desktop-plugin-ui": ["polish-1", "polish-2", "polish-3"],
    "reflex-xy": ["final-1", "final-2", "final-3"],
}


def summarize(row):
    run = REPO / "evaluations/runs" / row["run_id"]
    target = OUTPUT / "traces" / (row["run_id"] + ".json")
    if not (run / "events.jsonl").is_file():
        return {"passed": False, "reason": "No completed event file."}
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "scripts/summarize-pi-json-events.py", str(run / "events.jsonl"), "--require-model", "gpt-6.1-sol", "--fail-on-invalid-json", "--fail-on-tool-error", "--output", str(target)]
    result = subprocess.run(command, cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if not target.is_file():
        return {"passed": False, "reason": result.stderr[-300:]}
    data = json.loads(target.read_text(encoding="utf-8"))
    return {"passed": data.get("passed", False), "exitCode": result.returncode,
            "models": data.get("models", {}), "toolErrors": len(data.get("toolErrors", [])),
            "readPaths": [p["path"] for p in data.get("paths", [])], "findings": data.get("findings", [])}


def main():
    records = []
    for file in sorted(OUTPUT.glob("results-*.json")):
        records.extend(json.loads(file.read_text(encoding="utf-8")))
    independent = {r["run"]: r for r in json.loads((PROJECT / "artifacts/reviews/generated/reviews.json").read_text(encoding="utf-8"))}
    rows, preflight = [], []
    for record in records:
        run = REPO / "evaluations/runs" / record["run_id"]
        if not (run / "run-manifest.json").is_file():
            preflight.append({"run_id": record["run_id"], "exit_code": record["exit_code"], "classification": "source validation before model execution"})
            continue
        manifest = json.loads((run / "run-manifest.json").read_text(encoding="utf-8"))
        evaluation = json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))
        event_check = json.loads((run / "event-check.json").read_text(encoding="utf-8")) if (run / "event-check.json").is_file() else {}
        grade = independent.get(record["run_id"], {})
        rows.append({**record, "strictPassed": evaluation["passed"], "artifactPassed": grade.get("passed", False),
                     "timedOut": evaluation.get("timedOut", False), "payload": manifest["skill"],
                     "eventFindings": event_check.get("findings", []), "artifactFindings": [c for c in grade.get("checks", []) if not c["passed"]],
                     "artifactErrors": grade.get("errors", [])})
    with ThreadPoolExecutor(max_workers=6) as pool:
        for row, trace in zip(rows, pool.map(summarize, rows)):
            row["traceSummary"] = trace
    latest = []
    for skill, attempts in LATEST.items():
        members = [next(r for r in rows if r["skill"] == skill and r["case"] == "naturalistic" and r["run_id"].endswith("-" + attempt)) for attempt in attempts]
        digests = sorted({r["payload"]["payloadSha256"] for r in members})
        if len(digests) != 1:
            raise ValueError(f"The named naturalistic cohort is not frozen: {skill}")
        latest.append({"skill": skill, "runIds": [r["run_id"] for r in members], "payload": members[0]["payload"],
                       "strictPassed": sum(r["strictPassed"] for r in members), "artifactPassed": sum(r["artifactPassed"] for r in members),
                       "jointPassed": sum(r["strictPassed"] and r["artifactPassed"] for r in members), "total": len(members)})
    summary = {"date": "2026-11-12", "model": "openai-codex/gpt-6.1-sol", "thinking": "medium",
               "modelException": "Recorded account rejection of Spark in the preceding host-split campaign; explicit per-run Sol exception, no global model change.",
               "completedModelRuns": len(rows), "strictPassed": sum(r["strictPassed"] for r in rows), "artifactPassed": sum(r["artifactPassed"] for r in rows),
               "jointPassed": sum(r["strictPassed"] and r["artifactPassed"] for r in rows), "timeouts": sum(r["timedOut"] for r in rows),
               "preflight": preflight, "latestCohorts": latest, "runs": rows}
    target = REPO / "evaluations/desktop-plugin-ui/rich-interfaces-20261112.json"
    target.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = ["# Rich plugin interface validation", "", "Date: November 12, 2026.", "",
             "The local Service Observatory project compares one synthetic inspection task across six host routes. Seven UI skills now contain self-contained graph/chart/workspace guidance; the owning Reflex XY skill also gains a connected-request recipe and checker. All broad skills remain `validating`: runtime and prototype evidence is separated from each product's actual installation and paint.", "",
             "## Local implementation evidence", "",
             "- Shared synthetic source: 12 services, 13 directed relationships and 24 hourly observations per service. The daily window is explicitly November 11 UTC; the snapshot timestamp is November 12, 00:05 UTC.",
             "- Portable MCP App: real SDK/server stdio, exact resource/MIME, direct refresh, optional-capability behavior, filtered JSON scope, cancel/late-result guards, keyboard selection, 44px mobile control targets and layouts at 320/390/768/1280/1440 CSS pixels. The browser report contains 55 passing checks.",
             "- Native Claude Code 2.1.302: 10 passing real-engine tests cover direct output, selectors, missing/denied panes, terminal/Desktop/VS Code surfaces, narrow columns and close behavior. Original SVG payloads are also rendered in the local preview; this does not establish signed-in native pixels.",
             "- Pi 1.4.0: 29 passing real RPC/print and geometry checks; a separate 16-check bundled-template RPC run covers staged cancellation and exact output. Actual 80-column TUI key/character output was observed. Browser text previews are identified as previews.",
             "- Installed Codex core 0.167.0-alpha.3.2: five passing app-server checks under a task-local home verify initialization, an ephemeral read-only thread, configured MCP discovery, the exact direct tool result, and no model turn. This uses MCP configuration, not a portable marketplace installation or stock frontend rendering.",
             "- Gemini Enterprise: both native Material/VegaChart and Canvas/IFrameSrcdoc streams pass the official v0.9 envelope and current host catalog; the bound chart spec also passes the separate Vega-Lite v5 schema. The five-component bundled chart/table template passes these checks too. A2A transport, cloud registration and actual Gemini host paint are untested.",
             "- Twelve local preview checks pass. The iframe fixture applies the catalog's documented connect-src policy and observes a securitypolicyviolation event; a generic failed fetch alone was discarded as insufficient proof.",
             "- Existing Reflex XY paint and More options were observed in actual Claude Desktop 4.4212.0. A newly rendered 24-point XY latency chart and its exports were inspected; this is separate from paint of the new portable package.",
             "- The advertised Excalidraw reference tool returned an unknown-tool error. It is recorded as a connector availability mismatch, not a product UI limitation or unsupported-host result.", "",
             "## Frozen forward cohorts", "",
             f"Retained model executions: {len(rows)}; strict passes: {summary['strictPassed']}; independent artifact passes: {summary['artifactPassed']}; joint passes: {summary['jointPassed']}; timeouts: {summary['timeouts']}. {len(preflight)} source preflights failed before a model ran. They are retained separately and are not model repetitions.", "",
             "Each latest naturalistic cohort contains three fresh workspaces with one identical runtime payload. Older failed or repaired candidates are preserved below and are not pooled into its threshold. The model was gpt-6.1-sol with medium thinking under the explicit Spark-account exception. No global setting changed.", "",
             "| Skill | Strict | Artifact | Joint | Runtime files | Payload SHA-256 |", "| --- | --- | --- | --- | --- | --- |"]
    for row in latest:
        lines.append(f"| {row['skill']} | {row['strictPassed']}/3 | {row['artifactPassed']}/3 | {row['jointPassed']}/3 | {row['payload']['fileCount']} | `{row['payload']['payloadSha256']}` |")
    lines += ["", "Contract smoke tests run the exact bundled palette command and verify outputs; each changed bundle has a final passing contract. Boundary/generalization planning runs cover a 12,000-node graph, 60,000 edges, one million samples, narrow surfaces, filter exclusion, cancellation and honest host limits. Their actual candidate identities and results are in the complete run inventory. New implementation templates and checkers receive dedicated real-engine/schema/RPC checks. Final source cohorts are not claims of broad production or complete accessibility acceptance.", "",
              "## Repairs and failure classifications", "",
              "- Missing contents sections in long new references caused source preflight failures. These were fixed before the corresponding model runs; no preflight was counted as a model pass/fail.",
              "- A generated native Svg omitted required alt text; the engine rejected it. The skill now includes the exact source/alt constructor contract. Generated final candidates are independently mounted with real selectors and exact/missing-data assertions.",
              "- Early Pi candidates read installed docs outside the restricted workspace or invented transport test assertions. The skill now explicitly respects resource restrictions, includes a complete staged inspector template, and supplies a real RPC/JSON-print checker. All earlier strict failures remain failures even when final artifacts work.",
              "- Early Gemini generations used header strings instead of column objects. The skill now includes exact header/field objects and a complete bound chart/table stream. Earlier structural checker passes did not establish official catalog acceptance.",
              "- An early XY request mixed a preset with guessed component/type fields. The connected-adapter reference and focused finite-line/Sankey checker now separate presets from version:1 marks/components. Four regression test groups cover exact labels, paired data, finite bounds and wire-shape errors.",
              "- A generated Codex browser prototype could expand the document at 320px. A minmax/min-width/contained-scroll recipe was added; later candidates are measured independently. The timeout remains a failed repetition.",
              "- The comparison skill's plan-only path now avoids building unrequested test projects. Earlier tool errors and timeout are retained rather than described as product failures.",
              "- Evaluator repairs are separate: a locator.evaluate argument mismatch, an opaque-frame screenshot/capture problem, Windows command quoting and unsupported native register re-export staging were corrected without changing evaluated outputs. The native evaluator loads the actual source directly. CORS rejection was replaced by a verified CSP violation. These are fixture defects, not renderer defects.", "",
              "## Reproduction and retained evidence", "",
              "See [the local lab guide](../../docs/plugin-ui-rich-interfaces.md) for build, package and domain checks. Project scripts and reusable prompts are versioned; large workspaces, screenshots, exports, archives and traces stay ignored under project artifacts or evaluations/runs.", "",
              "Campaign definition: [evaluation-cases.json](../../projects/plugin-ui-rich-interfaces/evaluation-cases.json). Strict entry point: `uv run --script projects/plugin-ui-rich-interfaces/scripts/run-evaluations.py --attempt <fresh-label> --workers 3` (select a case/skill for a focused run). Every required path is an --expect-output contract. The runner preserves all attempts and requested model settings.", "",
              "Trace command for every completed event file: `uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error`. Summaries and read paths are retained locally under project artifacts/evaluations/traces. The strict event gate additionally enforces prompt-first, allowed reads, zero tool errors and unchanged skill payload.", "",
              "Independent grader: `node projects/plugin-ui-rich-interfaces/scripts/review-generated.mjs`. It loads generated browser views, checks narrow geometry and interactions, mounts generated native controls in the real engine, invokes actual Pi JSON print, and validates generated A2UI and connected XY requests. Pixel inspection supplements these checks. A self-reported test or valid JSON alone is insufficient.", "",
              "## Spot pixel critique", "",
              "Technical artifact pass counts do not assert pixel perfection or complete accessibility acceptance. Representative populated, changed-selection and narrow screenshots were inspected separately. The preserved Desktop Chat sol-2 example has a minor selected-label overflow and a crowded objective caption; the source data and interactions still pass their recorded technical criteria. The authored Service Observatory uses bounded label/detail/state regions, a left-side objective caption and a direct-neighborhood mobile view. The ChatGPT example preserves missing data explicitly, and the later Codex mobile example reflows its chart and exact table. These findings and concrete repairs are in [the manual review](rich-interfaces-20261112-review.json); no original evaluation output was silently edited.", "",
              "## Complete model-run inventory", "", "| Run | Strict | Artifact | Failure detail |", "| --- | --- | --- | --- |"]
    for row in rows:
        details = ["timeout"] if row["timedOut"] else []
        details.extend(sorted({f.get("code", "event finding") for f in row["eventFindings"]}))
        details.extend(c["name"] for c in row["artifactFindings"])
        details.extend(row["artifactErrors"])
        lines.append(f"| `{row['run_id']}` | {'pass' if row['strictPassed'] else 'fail'} | {'pass' if row['artifactPassed'] else 'fail'} | {('; '.join(details) or 'none').replace('|', '/')} |")
    lines += ["", "The companion JSON preserves commands, elapsed time, exact outputs, observed models, payload hashes, event findings, read paths and independent checks. Checks not performed in a product are untested; none of these rows certifies universal host compatibility."]
    (target.with_suffix(".md")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(rows), "strict": summary["strictPassed"], "artifacts": summary["artifactPassed"], "joint": summary["jointPassed"], "preflights": len(preflight), "latest": [{k: r[k] for k in ["skill", "strictPassed", "artifactPassed", "jointPassed"]} for r in latest]}))


if __name__ == "__main__":
    main()
