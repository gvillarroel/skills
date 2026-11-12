#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write bounded, reproducible host-split forward prompts and a run manifest."""
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[3]
HOSTS = {
    "desktop-chat-plugin-ui": "ordinary Claude Desktop Chat",
    "code-native-plugin-ui": "Claude Code terminal and Desktop Code tab",
    "pi-extension-ui": "Pi Coding Agent",
    "codex-plugin-ui": "Codex desktop and CLI",
    "chatgpt-desktop-plugin-ui": "ChatGPT Desktop local threads",
    "gemini-enterprise-ui": "Google Cloud Gemini Enterprise",
    "desktop-plugin-ui": "a cross-host assistant UI comparison",
}

NATURAL = {
    "desktop-chat-plugin-ui": """Build a small read-only inventory connector for ordinary Claude Desktop Chat.
Use three synthetic items with stable IDs, names and stock counts. The user
should see the items, filter in the interface, and recover from a failed refresh.
Produce a runnable local MCP server and actual MCP App resource at
`deliverables/connector/`, including `package.json`, `server.mjs`, and the
component's source. Include a real protocol test and run it. Return useful
text/structured results as well as UI. Do not install in the personal Desktop
account or expose a public endpoint. Write `deliverables/review.json` with
`host`, `mechanism`, `tests`, `remaining_host_checks`, and `heuristics`.
Record exact setup/test commands; keep live host checks separate from fixtures.
""",
    "code-native-plugin-ui": """Build a read-only native Claude Code plugin for a three-item deployment queue.
Rows DEP-1 and DEP-3 are pending, and DEP-2 is complete. Let users select all,
pending, or complete without a model call, close the view, and reopen it. A
direct argument must work when a pane is unavailable. Create the runnable
plugin at `deliverables/deployment-view/` with authentic native-engine tests,
and run strict package validation and those tests using task-local host state.
Keep other plugins' command and pane behavior usable. Do not modify personal
host settings or install globally. Write `deliverables/review.json` with
`host`, `mechanism`, `tests`, `remaining_host_checks`, and `heuristics`.
""",
    "pi-extension-ui": """Build a Pi extension for selecting a report format: summary or detailed.
Create `deliverables/report-format.ts`. Use a deterministic native command,
keep the selected format in memory, and support a direct argument in a
noninteractive run. Cancellation must preserve the previous choice. Use the
actual local Pi RPC runtime to verify discovery, selection, cancel, invalid
input recovery, and a valid explicit argument without a model turn. Do not
install globally or add a web service. Write `deliverables/review.json` with
`host`, `mechanism`, `tests`, `remaining_host_checks`, and `heuristics`.
""",
    "codex-plugin-ui": """Prepare a portable local Codex plugin that exposes a read-only build summary
for synthetic build B-42 with status passed and seven checks. Include an MCP
App summary view when a frontend supports it, and a usable text result for the
CLI. Create the runnable package at `deliverables/build-summary/`, including
root `plugin.json`, root `mcp.json`, `package.json`, and `server.mjs`. Verify
initialize/discovery/a useful direct tool and resource from a clean runtime
copy. Do not change personal catalogs, start a model turn to test discovery,
or claim stock Codex desktop/IDE painting from a protocol response. Write
`deliverables/review.json` with `host`, `mechanism`, `tests`,
`remaining_host_checks`, and `heuristics`.
""",
    "chatgpt-desktop-plugin-ui": """Build a ChatGPT Desktop local-thread plugin for inspecting three synthetic
support tickets and their status. Include an interactive MCP App with local
filtering and a refresh action, plus useful text/structured tool output.
Create the runnable package at `deliverables/ticket-view/`, including root
`plugin.json`, root `mcp.json`, `package.json`, `server.mjs`, and component
sources. Validate the packaged runtime with a real MCP client. Do not publish,
register a public tunnel, or modify personal settings. Write
`deliverables/review.json` with `host`, `mechanism`, `tests`,
`remaining_host_checks`, and `heuristics`. Keep Desktop acceptance and optional
OpenAI APIs explicit if they cannot be exercised locally.
""",
    "gemini-enterprise-ui": """Prepare an A2UI deployment-status panel for the Google Cloud Gemini Enterprise
app. Show release R-17, readiness Ready, and region us-central1 with accessible
English labels. Create `deliverables/release-panel.json` as a message stream
using the documented host-supported Material catalog, and an illustrative
A2A agent card at `deliverables/agent-card.json` for the placeholder endpoint
https://agent.example.invalid. The card should describe the UI/catalog
capability. Run the bundled integrity checker against your stream and save
`deliverables/check.json`. Write `deliverables/review.json` with `host`,
`mechanism`, `tests`, `remaining_host_checks`, and `heuristics`. Explain the
remaining server/stream/action, hosting and administrator work; do not deploy,
register anything, or claim live host rendering. This is a read-only panel.
""",
    "desktop-plugin-ui": """Plan a small release-inspection tool spanning Claude Desktop Chat, Claude
Code, Pi TUI and RPC, Codex CLI and desktop, ChatGPT Desktop local threads,
and Google Cloud Gemini Enterprise. Use one shared release/domain contract
and small host adapters. A release has ID, status, and checks; users can inspect
and filter it without model inference. Explain the package, transport, UI
mechanism, fallback, conditions, and validation for each actual surface.
Write `deliverables/plan.md` and `deliverables/adapters.json`. The JSON must
have an `adapters` array whose records contain `host`, `surface`, `mechanism`,
`validation`, and `remaining_host_checks`. Keep the blueprint proportionate;
do not implement, install, register, or deploy the adapters. Distinguish
source declarations from executed host acceptance.
""",
}

BOUNDARY = {
    "desktop-chat-plugin-ui": "The teammate supplied a Claude Code Mod and expects it to draw a panel in ordinary Claude Desktop Chat. They also copied a ChatGPT widget domain for a local stdio connector. Diagnose this route and prepare a corrected local build plan, with remote hosting kept out of scope.",
    "code-native-plugin-ui": "A hook registers command name deployment-view and handles command.run by reading event.name. Its tests fabricate the same name field and pass. The team also assumes terminal SVG and Desktop controls have identical support. Diagnose the event and frontend issues and provide an authentic test plan.",
    "pi-extension-ui": "A teammate uses ctx.hasUI to call ctx.ui.custom in RPC and confirms an edit after a newer update to the same row. They want a JSON/print fallback too. Explain the actual mode and authority boundaries and provide a concrete recovery/test plan for this report-editing workflow.",
    "codex-plugin-ui": "A portable plugin appears in a catalog and its app-server callback returns HTML. The team wants to report that the stock Codex desktop/IDE painted it, and to retry a declined elicitation after changing never approval policy. Explain what is actually established and propose independent loader, protocol, and frontend checks without bypassing the policy.",
    "chatgpt-desktop-plugin-ui": "A standard-bridge browser fixture works and a web setup screen reached consent. The team wants to claim Desktop local-thread installation, optional window.openai modal support, and remote tunnel deployment all passed. Explain the separate missing checks and prepare a compact local-first acceptance plan without publishing anything.",
    "gemini-enterprise-ui": "The upstream A2UI website now recommends v1.0. A teammate wants to upgrade a Google Cloud Gemini Enterprise panel immediately, send it as an MCP App, and promise an arbitrary custom sidebar. Explain the host-bound contract and prepare a supported integration and validation plan for a read-only regional job-status table.",
    "desktop-plugin-ui": "A team assumes that using the same model and MCP server means Claude Desktop Chat, Claude Code, Pi RPC, Codex desktop, ChatGPT Desktop, and Gemini Enterprise can share one universal UI manifest and renderer. Review this claim and prepare one shared domain contract with appropriately separate adapter and host-acceptance checks.",
}


def main():
    directory = ROOT / "evaluations/pi-prompts"
    directory.mkdir(exist_ok=True)
    runs = []
    for skill, host in HOSTS.items():
        prefix = f"Use the copied skill for {host}. Treat `skills/{skill}/` as read-only. Write task artifacts only in this workspace outside the skill. Keep temporary state and caches task-local. Use only the supplied skill and normal local tools. Do not discover other skills or read installed host documentation, host examples, personal configuration, or any source outside this workspace. Running installed tool executables is allowed.\n\n"
        for case in ("contract", "naturalistic", "boundary-generalization"):
            expected = []
            if case == "contract":
                body = f"Create the deliverables directory and write deliverables/route.md first. Then execute the following exact bundled command as a standalone bash call, without prefixing other commands:\n\n```bash\npython skills/{skill}/scripts/design_values.py --palette colorset1 --list-tokens > deliverables/design.json\n```\n\nInspect the result and write `deliverables/route.md` recommending the appropriate UI route for {host}. Explain its actual transport/rendering boundary and the next host acceptance check. Do not install, deploy, or change any account settings.\n"
                expected = ["deliverables/design.json", "deliverables/route.md"]
            elif case == "naturalistic":
                body = NATURAL[skill]
                expected = {
                    "desktop-chat-plugin-ui": ["deliverables/connector/package.json", "deliverables/connector/server.mjs", "deliverables/review.json"],
                    "code-native-plugin-ui": ["deliverables/deployment-view/.claude-plugin/plugin.json", "deliverables/deployment-view/hooks/register.ts", "deliverables/review.json"],
                    "pi-extension-ui": ["deliverables/report-format.ts", "deliverables/review.json"],
                    "codex-plugin-ui": ["deliverables/build-summary/plugin.json", "deliverables/build-summary/mcp.json", "deliverables/build-summary/server.mjs", "deliverables/review.json"],
                    "chatgpt-desktop-plugin-ui": ["deliverables/ticket-view/plugin.json", "deliverables/ticket-view/mcp.json", "deliverables/ticket-view/server.mjs", "deliverables/review.json"],
                    "gemini-enterprise-ui": ["deliverables/release-panel.json", "deliverables/agent-card.json", "deliverables/check.json", "deliverables/review.json"],
                    "desktop-plugin-ui": ["deliverables/plan.md", "deliverables/adapters.json"],
                }[skill]
            else:
                body = BOUNDARY[skill] + "\n\nWrite `deliverables/recovery.md` and `deliverables/checks.json`. The JSON must have a `checks` array with records containing `layer`, `action`, `expected`, and `status`. Keep planned checks distinct from executed results. Do not run a live installation, account change, deployment, or model call to probe the target host. Use the available bundled sources; identify any current source question that remains unresolved.\n"
                expected = ["deliverables/recovery.md", "deliverables/checks.json"]
            path = directory / f"host-split-{skill}-{case}.md"
            path.write_text(prefix + body, encoding="utf-8")
            runs.append({"skill": skill, "case": case, "prompt": path.relative_to(ROOT).as_posix(), "expected": expected})
    target = ROOT / "projects/plugin-ui-host-split/evaluation-cases.json"
    target.write_text(json.dumps(runs, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(runs)} isolated cases with exact outputs and read-only skill resources.")


if __name__ == "__main__":
    main()
