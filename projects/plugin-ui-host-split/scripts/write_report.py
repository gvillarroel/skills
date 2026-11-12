#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write the durable host-split result and narrowly update backlog records."""
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[3]
NAMES = ["desktop-chat-plugin-ui", "code-native-plugin-ui", "pi-extension-ui", "codex-plugin-ui",
         "chatgpt-desktop-plugin-ui", "gemini-enterprise-ui", "desktop-plugin-ui"]


def main():
    project = ROOT / "projects/plugin-ui-host-split/artifacts/manifests"
    reviews = json.loads((project / "evaluation-review.json").read_text())
    subjects = json.loads((project / "final-subjects.json").read_text())
    cases = json.loads((ROOT / "projects/plugin-ui-host-split/evaluation-cases.json").read_text())
    expected_ids = {f'20261111-host-split-{case["skill"]}-{case["case"]}-sol-1' for case in cases}
    for repetition in [2, 3]:
        expected_ids |= {f'20261111-host-split-{case["skill"]}-{case["case"]}-repeat-{repetition}' for case in cases if case["case"] != "contract"}
    actual = {row["run_id"] for row in reviews}
    if expected_ids - actual:
        raise RuntimeError(f"Required repetitions are still running: {sorted(expected_ids - actual)}")
    index = {row["run_id"]: row for row in reviews}
    table = []
    for skill in NAMES:
        contract_suffix = "sol-2" if skill in NAMES[:3] else "sol-1"
        contract = index[f"20261111-host-split-{skill}-contract-{contract_suffix}"]
        natural = [index[f"20261111-host-split-{skill}-naturalistic-{suffix}"] for suffix in ["sol-1", "repeat-2", "repeat-3"]]
        boundary = [index[f"20261111-host-split-{skill}-boundary-generalization-{suffix}"] for suffix in ["sol-1", "repeat-2", "repeat-3"]]
        table.append({"skill": skill, "contract_passed": contract["strict_passed"],
                      "naturalistic_strict": sum(row["strict_passed"] for row in natural),
                      "boundary_strict": sum(row["strict_passed"] for row in boundary)})
    out = ROOT / "evaluations/desktop-plugin-ui"
    durable = {"date": "2026-11-11", "timezone": "America/New_York", "status": "validating",
               "model": "openai-codex/gpt-6.1-sol", "thinking": "medium", "model_exception": "Spark rejected by ChatGPT account; zero usage; per-run Sol exception recorded in SKILLS.md.",
               "strict_passed": sum(row["strict_passed"] for row in reviews), "strict_total": len(reviews),
               "case_matrix": table, "subjects": subjects,
               "runs": [{**row, "event_findings": [{"code": finding["code"], "tool": finding.get("tool")} for finding in row["event_findings"]]} for row in reviews],
               "scope": "Independent host skill split with bounded runtime/artifact validation; no new signed-in host installation or cloud deployment."}
    (out / "host-split-20261111.json").write_text(json.dumps(durable, indent=2) + "\n", encoding="utf-8")
    lines = ["# Assistant plugin UI host separation", "", "Date: November 11, 2026 (America/New_York). Raw runs cross into November 12 UTC.", "",
             "Six independent host bundles now own their runtime guidance and resources. The original `desktop-plugin-ui` is a cross-host comparison/blueprint entrypoint. Historical references, source work and evidence remain available. All seven backlog records remain `validating`: this split does not establish every signed-in frontend, deployment route, or full generation reliability.", "",
             "## Bundles and scope", "", "| Skill | Files | Core lines | Runtime bytes |", "| --- | ---: | ---: | ---: |"]
    for row in subjects:
        lines.append(f'| `{row["skill"]}` | {row["file_count"]} | {row["core_lines"]} | {row["bytes"]} |')
    lines += ["", "All new bundles have their own palettes and design helper. Native Claude retains the tested starter; Pi retains the guarded intent primitive, a command starter, and version probe. Gemini has an original v0.9 panel and bounded checker. Shared runtime helpers/templates were checked byte-for-byte against the original source. Required bundle links and resources stay inside each bundle; no sibling skill is required.", "",
              "Claude-qualified directory names use `desktop-chat-plugin-ui` and `code-native-plugin-ui` because the existing repository authoring validator reserves `claude` and `anthropic` in skill names. Display names and descriptions identify the actual hosts. No validator was weakened.", "",
              "## Deterministic and independent checks", "",
              "- Repository pattern IDs, bundle validation, independence tests, and payload checks pass. Local sync/check validates source-owned installation parity.",
              "- Existing source checker: 81/81; design values: 16/16; version probe: 17/17. Google primary-source ownership and lookalike rejection were also checked. Only exact bundled/allowed URLs are accepted.",
              "- New bounded A2UI checker: 12/12 unit/CLI tests. The starter and three generated streams pass actual upstream envelope and host component schemas. The envelope's relative catalog slot is bound to the official host component union; theme-property semantics are explicitly excluded by that adapter. This is not host paint or A2A transport acceptance.",
              "- Copied Claude starter: strict manifest validation and 13/13 authentic native tests on Claude Code 2.1.302. Three corrected-source generated Claude plugins also pass independent strict validation/native engines.",
              "- Pi starter: 16/16 real Pi 1.4.0 RPC/JSON-print assertions, including discovery, selection, cancel, invalid recovery, direct arguments and zero model turns. Three generated Pi artifacts pass an independent direct JSON-print/no-inference check; RPC test sources/transcripts were reviewed separately.",
              "- Generated MCP packages were independently initialized over stdio, discovered, called for useful text/structured results, and read for actual linked HTML/MIME resources. Portable Codex/ChatGPT manifests were checked against both official schemas using their declared runtime entries. These checks do not establish frontend painting.",
              "- The first generated Desktop Chat app also passes an independently rerun protocol test. Its actual sandbox bridge tests and wide/narrow success/error screenshots were reviewed: readable labels, visible recovery, retained filters and no overflow. These are browser fixture results, not Claude Desktop acceptance.",
              "- Metadata-only routing: 11/11, including eight positive surface requests and three exclusions. No skill was forced and no body was provided. This does not measure automatic product discovery.", "",
              "## Isolated forward runs", "",
              "Spark was attempted first and rejected by the ChatGPT account with zero reported usage. The recorded per-run exception uses `openai-codex/gpt-6.1-sol`, medium thinking. Every normal run uses the runtime-only copied bundle, disabled ambient discovery, strict JSON/model/error/output/integrity gates, and exact expected output paths. The copied skill stays read-only.", "",
              f'{len(reviews)} Sol evaluations completed; {sum(row["strict_passed"] for row in reviews)} passed every strict harness gate. Failures are retained. Counts below use the initial run plus two fresh repetitions, including pre-repair failures; they are not a filtered best-of table.', "",
              "| Skill | Final contract | Naturalistic strict / 3 | Boundary/generalization strict / 3 |", "| --- | --- | ---: | ---: |"]
    for row in table:
        lines.append(f'| `{row["skill"]}` | {"Pass" if row["contract_passed"] else "Fail"} | {row["naturalistic_strict"]}/3 | {row["boundary_strict"]}/3 |')
    lines += ["", "Additional corrected-source diagnostics are separate from that matrix: native Claude `sol-recovery`, `repeat-2`, and `repeat-3` are all strict/independent passes. Pi `sol-recovery` retained a wrong test assertion about disposition; after promoting the exact JSON response into its reference, `repeat-2` and `repeat-3` passed strictly. Earlier outside-workspace host-doc reads remain failed isolation results.", "",
              "Failure classification and repairs:", "",
              "- Harness: two original contract prompts used a fence the exact-command parser did not recognize. Corrected bash fences and standalone-command wording passed in fresh workspaces; original failures remain.",
              "- Agent/isolation: initial Pi reads used installed documentation outside the allowed workspace. Explicit source isolation was clarified; later runs used only supplied guidance and normal executables.",
              "- Skill/agent: an added native render guard assumed an absent plugin event field. The host reference now distinguishes mount fixtures from real render events. Corrected-source generated plugins passed three strict runs and independent native checks.",
              "- Skill/agent: Pi's compact reference lacked the exact handled-prompt response. It now names `response.data.disposition === \"handled\"` and `response.data.commands`; the two subsequent runs passed strictly.",
              "- Agent/tooling: web runs retained exploratory commands with nonzero exits, dependency/peer-resolution or audit failures, browser setup/fixture issues, and a TypeScript check failure. Final artifacts can work while strict history remains failed; a repaired artifact does not erase a tool error.",
              "- Runtime budget: ChatGPT Desktop `repeat-2` reached the 600-second timeout. Its expected artifacts exist and its declared package later passes independent stdio/schema checks, but completed event gates are absent and the run remains a strict failure. The trace summarizer now explicitly records this case rather than inventing missing gate results.",
              "- Evaluator: an initial independent ChatGPT probe started the editable root server instead of the declared bundled entry. Its failure is preserved; the unchanged package passes after the evaluator reads `mcp.json`. An initial Pi starter verifier also read disposition at the wrong level; the corrected evaluator passes 16/16. A first official-schema probe tried to fetch the envelope's catalog placeholder; binding the actual host catalog fixed the evaluator and was promoted into the Gemini reference.", "",
              "## Reproduction and retained evidence", "",
              "Prompts are versioned under `evaluations/pi-prompts/host-split-*.md`; the precise case/output manifest is `projects/plugin-ui-host-split/evaluation-cases.json`. Run controls and independent validators live in that project's `scripts/`. Bulky workspaces, JSONL, packages, schemas, logs and images remain ignored under `evaluations/runs/20261111-host-split-*` and `projects/plugin-ui-host-split/artifacts/`.", "",
              "Representative contract:", "", "```powershell", "uv run --script scripts/run-pi-skill-eval.py gemini-enterprise-ui --prompt-file evaluations/pi-prompts/host-split-gemini-enterprise-ui-contract.md --mode json --strict --require-exact-command-from-prompt --model openai-codex/gpt-6.1-sol --thinking medium --expect-output deliverables/design.json --expect-output deliverables/route.md", "```", "",
              "Exact run commands and required paths are retained in each run manifest. `summarize_evaluations.py` applies `summarize-pi-json-events.py --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error` to every completed trace and separately checks requested artifact schemas. Full per-run results and final source digests are in [the durable record](host-split-20261111.json).", "",
              "Required repository gates:", "", "```powershell", "uv run --script scripts/validate-pattern-ids.py", "uv run --script scripts/validate-skills.py", "uv run --script scripts/test-skill-independence.py", "uv run --script scripts/check-repo-payload.py", "uv run --script scripts/sync-local-skills.py", "uv run --script scripts/sync-local-skills.py --check", "```", "",
              "Skill-specific commands:", "", "```powershell", "python skills/gemini-enterprise-ui/scripts/test_check_a2ui.py", "python projects/desktop-plugin-ui/scripts/test-source-checker.py", "python projects/desktop-plugin-ui/scripts/test-design-values.py", "python projects/desktop-plugin-ui/scripts/test-runtime-probe.py", "node projects/plugin-ui-host-split/scripts/verify_pi_starter.ts", "uv run --script projects/plugin-ui-host-split/scripts/verify_generated_native.py", "```", "",
              "For official catalog and MCP package checks, use `validate_a2ui_catalog.py <stream.json> --label <run-label>` and `verify_mcp_package.py <package-dir> --label <run-label>`. Keep the chosen input run and output label distinct to preserve evidence.", "",
              "## Remaining acceptance", "",
              "Current work does not install into personal accounts, alter approval policy, deploy cloud services, register Gemini agents, or publish GitHub changes. Actual Claude Desktop Chat/Code, Pi TUI or custom RPC-client paint, stock Codex desktop/IDE rendering, ChatGPT Desktop local UI, and Gemini Enterprise signed-in A2A/action/paint checks remain separately scoped. Existing historical observations are retained in host references and are not promoted to current acceptance. Broader release repetition and generation reliability still need work for the failing routes.", "",
              "Primary Gemini sources reviewed: [registration](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/register-and-manage-an-a2ui-agent), [component catalog](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/a2ui-component-gallery-reference), [hosting](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/tutorial-host-agent-cloud-run), and [A2A compatibility](https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-a2a-agent). The documented host route is A2UI v0.8/v0.9 over version-compatible A2A; a newer upstream version does not establish host support.", ""]
    (out / "host-split-20261111.md").write_text("\n".join(lines), encoding="utf-8")
    backlog = ROOT / "SKILLS.md"
    text = backlog.read_text(encoding="utf-8")
    updated = []
    for line in text.splitlines():
        name = next((name for name in NAMES[:-1] if line.startswith(f"| {name} |")), None)
        if name:
            columns = line.split("|")
            columns[2] = " `validating` "
            matrix = next(row for row in table if row["skill"] == name)
            columns[5] = f' Host split 2026-11-11: standalone gates and final contract pass; naturalistic strict {matrix["naturalistic_strict"]}/3, boundary/generalization {matrix["boundary_strict"]}/3 across retained repetitions. Per-run Sol 6.1/medium exception after Spark account rejection; live host acceptance remains scoped/untested. [Evidence, corrected-source runs and limits](evaluations/desktop-plugin-ui/host-split-20261111.md). '
            line = "|".join(columns)
        updated.append(line)
    text = "\n".join(updated) + "\n"
    start = text.index("### Assistant plugin UI host separation - 2026-11-11")
    end = text.find("\n### ", start + 4)
    if end == -1:
        raise RuntimeError("Cannot safely locate the end of the new validation note.")
    note = f'''### Assistant plugin UI host separation - 2026-11-11

Six independent bundles separate Claude Desktop Chat (`desktop-chat-plugin-ui`), native Claude Code (`code-native-plugin-ui`), Pi, Codex, ChatGPT Desktop, and Google Cloud Gemini Enterprise. The original `desktop-plugin-ui` now handles cross-host comparisons and blueprints; prior resources/evidence are preserved. All seven final command contracts pass; metadata routing is 11/11. {sum(row["strict_passed"] for row in reviews)}/{len(reviews)} retained Sol forward evaluations pass every strict gate, with three naturalistic and boundary/generalization repetitions per host plus explicitly separate repairs. Native starter 13/13, Pi RPC/print 16/16, A2UI helper 12/12, source/design/probe regressions 81/81, 16/16 and 17/17 pass. Official A2UI catalog and real MCP/portable-schema checks are kept separate from host paint. New bundles remain `validating` for generation/host coverage. Spark is unsupported by the account; these tests use the recorded per-run `openai-codex/gpt-6.1-sol` medium-thinking exception without changing global settings. [Commands, source identities, all failures, independent checks and remaining gates](evaluations/desktop-plugin-ui/host-split-20261111.md).
'''
    text = text[:start] + note + text[end:]
    backlog.write_text(text, encoding="utf-8")
    print(json.dumps({"runs": len(reviews), "strict_passed": sum(row["strict_passed"] for row in reviews), "matrix": table}, indent=2))


if __name__ == "__main__":
    main()
