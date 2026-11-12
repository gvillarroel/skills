#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Freeze focused rich-interface forward cases without exposing project fixtures."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects/plugin-ui-rich-interfaces"
HOSTS = {
    "desktop-chat-plugin-ui": "ordinary Claude Desktop Chat",
    "code-native-plugin-ui": "Claude Code terminal and Desktop Code native Mods",
    "pi-extension-ui": "Pi Coding Agent TUI, RPC and JSON-print modes",
    "codex-plugin-ui": "Codex desktop with a CLI fallback; exact desktop renderer acceptance is unknown",
    "chatgpt-desktop-plugin-ui": "ChatGPT Desktop local-thread MCP Apps",
    "gemini-enterprise-ui": "Google Cloud Gemini Enterprise with its documented v0.9 composite catalog",
    "desktop-plugin-ui": "a cross-host comparison of Claude Desktop Chat, Claude Code, Pi, Codex, ChatGPT Desktop and Gemini Enterprise",
}
DATA = """The synthetic workflow has nodes ingest, validate, enrich, store, publish and notify.
Their display names match their IDs. Directed edges: ingest->validate (120 jobs/hour),
validate->enrich (110), validate->notify (10), enrich->store (110), store->publish (105),
publish->notify (105). These rates are observations, not a conserved flow model.
The selected node is enrich, with latency [90,100,95,130,160,180] ms at UTC hours
[0,4,8,12,16,20]. Its objective is 150 ms. State is degraded, owner is Data.
All other nodes are healthy. Provide exact values and clear units. No production
connection or editing action is requested."""


def main():
    folder = ROOT / "evaluations/pi-prompts"
    cases = []
    for skill, host in HOSTS.items():
        isolation = f"Target {host}. Treat skills/{skill}/ as a read-only resource. Write task files only outside that skill, within this workspace. Use only this supplied skill and normal local tools. Do not read other skills, repository docs, installed examples, personal configuration or anything outside this workspace. Do not install, deploy, change settings or contact a live service. Keep temporary state task-local.\n\n"
        old = (folder / f"host-split-{skill}-contract.md").read_text(encoding="utf-8")
        contract = old.replace("Create the deliverables directory", "Read references/rich-interfaces.md inside the supplied skill. Create the deliverables directory")
        path = folder / f"rich-ui-{skill}-contract.md"
        path.write_text(contract + "\nInclude one host-specific graph/chart alternative in the route notes.\n", encoding="utf-8")
        cases.append({"skill": skill, "case": "contract", "prompt": path.relative_to(ROOT).as_posix(), "expected": ["deliverables/design.json", "deliverables/route.md"]})
        if skill in {"desktop-chat-plugin-ui", "chatgpt-desktop-plugin-ui", "codex-plugin-ui"}:
            delivery = """Create a self-contained interactive frontend prototype at deliverables/workspace.html.
Keep scripts/styles/data local and dependency-free. Include a selectable directed
graph, a latency chart, exact values, a filter, a selected-item inspector and a
clean narrow layout. This task asks for the authored view, not a complete MCP
package or a claimed host installation. Write deliverables/review.json with
keys host, route, alternatives (array), testsPerformed (array), untested (array),
and critique (array of observation/userCost/repair objects). Run meaningful local
checks using available tools and describe their real scope."""
            expected = ["deliverables/workspace.html", "deliverables/review.json"]
        elif skill == "code-native-plugin-ui":
            delivery = """Create a native Mod renderer source at deliverables/view.ts exporting register(on).
Use real native controls for the selected workflow node and Dependencies/Metrics
views, useful direct-command text, a terminal relationship/chart alternative,
and an appropriate Desktop Code preview. Keep it dependency-free and embed
the synthetic data. The command name is workflow-view. Do not substitute HTML
for the native renderer. Write deliverables/review.json with keys host, route,
alternatives (array), testsPerformed (array), untested (array), and critique
(array of observation/userCost/repair objects). Check source locally within
available evidence; do not claim signed-in host paint."""
            expected = ["deliverables/view.ts", "deliverables/review.json"]
        elif skill == "pi-extension-ui":
            delivery = """Create a Pi TypeScript extension at deliverables/view.ts with command workflow-view.
Offer node/view selection in supported interactive modes, compact relationships
and a latency display, and useful direct arguments for JSON/print. Embed data.
Keep deterministic inspection free of model work. Stage multi-step selections
until the final choice is accepted. Write deliverables/review.json with keys
host, route, alternatives (array), testsPerformed (array), untested (array),
and critique (array of observation/userCost/repair objects). Check what can be
checked locally; do not claim TUI or RPC-client paint from a source check."""
            expected = ["deliverables/view.ts", "deliverables/review.json"]
        elif skill == "gemini-enterprise-ui":
            delivery = """Create a v0.9 A2UI message-array file at deliverables/interface.json using the
documented Gemini Enterprise composite catalog. Make a clean native analysis
view with a quantitative chart and exact table, plus direction-preserving
dependency information. Include the selected node's values without external
data URLs. Write deliverables/review.json with keys host, route, alternatives
(array), testsPerformed (array), untested (array), and critique (array of
observation/userCost/repair objects). Use the supplied skill's bounded checker
where suitable, and distinguish it from official catalog/host validation."""
            expected = ["deliverables/interface.json", "deliverables/review.json"]
        else:
            delivery = """Write deliverables/blueprint.json as an object with hostAdapters (one entry for
each of the six hosts, naming mechanism, graph, chart, state, fallback and test),
sharedData and layoutAlternatives. Write deliverables/review.json with keys
host, route, alternatives (array), testsPerformed (array), untested (array),
and critique (array of observation/userCost/repair objects). Make concrete
adapter choices for this workflow and keep browser prototypes, native engine
tests, schema checks and signed-in host paint separate."""
            expected = ["deliverables/blueprint.json", "deliverables/review.json"]
        prompt = isolation + "Build a clean workflow inspection interface.\n\n" + DATA + "\n\n" + delivery + "\n"
        path = folder / f"rich-ui-{skill}-naturalistic.md"
        path.write_text(prompt, encoding="utf-8")
        cases.append({"skill": skill, "case": "naturalistic", "prompt": path.relative_to(ROOT).as_posix(), "expected": expected})
        prompt = isolation + """We are adapting this UI to an incident investigation graph with 12,000 nodes,
60,000 directed edges and one million time-series rows. An analyst needs the
direct causes of one selected entity and its last day of metrics. The surface
can be 320 CSS pixels wide (web) or 60 columns (terminal). A filter may exclude
the selected entity. Refresh may fail or complete after cancellation. No
destructive actions or production access are needed.

Write deliverables/blueprint.json as an object with keys host, primarySurface,
graphPlan, chartPlan, statePlan, alternatives (array), testPlan (array), and
evidenceLimits (array). Make the choices specific to the actual host/modes and
state which rich route is conditional. Address density, scope/aggregation,
exact values, keyboard access, reflow, no-result recovery, stale responses and
an alternative that reduces complexity. Do not promise a host capability from
a model name, SDK method, valid JSON stream or generic browser screenshot.
This is an implementation plan, not a request to fabricate a full dataset.
"""
        path = folder / f"rich-ui-{skill}-boundary-generalization.md"
        path.write_text(prompt, encoding="utf-8")
        cases.append({"skill": skill, "case": "boundary-generalization", "prompt": path.relative_to(ROOT).as_posix(), "expected": ["deliverables/blueprint.json"]})
    reflex_isolation = "Use only skills/reflex-xy/ as a read-only skill resource and normal tools. Do not read installed examples, other skills, repository docs or personal settings. Keep all task output inside this workspace and outside the skill. Do not render through a live service or install/deploy a plugin.\n\n"
    contract = reflex_isolation + "Create deliverables/ and write deliverables/route.md first. Run this exact command as a standalone bash call:\n\n```bash\nuv run --script skills/reflex-xy/scripts/xy_colorsets.py --colorset colorset1 > deliverables/design.json\n```\n\nInspect the palette and the focused chart recipes. Explain the connected Sankey endpoint identity contract and a concrete way to keep an upward trend's last value clear of its legend in deliverables/route.md.\n"
    path = folder / "rich-ui-reflex-xy-contract.md"
    path.write_text(contract, encoding="utf-8")
    cases.append({"skill": "reflex-xy", "case": "contract", "prompt": path.relative_to(ROOT).as_posix(), "expected": ["deliverables/design.json", "deliverables/route.md"]})
    natural = reflex_isolation + """Prepare two JSON request specs for the deterministic connected XY renderer,
without calling it. Write deliverables/flow.json for this synthetic job flow:
nodes Queue, Worker A, Worker B, Archive; observed jobs/hour Queue->Worker A=60,
Queue->Worker B=40, Worker A->Archive=60, Worker B->Archive=40. Use a meaningful
quantitative flow view and preserve these exact identities and values.

Write deliverables/latency.json for hourly observations x=[0,1,2,3] with latency
y=[120,130,160,190] ms and a 150 ms objective. Preserve paired data, units and
the observed endpoint. Choose a clean legend placement so the objective crossing
and final high value remain clear. Use the default palette. Write
deliverables/review.json with route, alternatives (array), testsPerformed
(array) and untested (array). Check the JSON and describe the actual scope.
"""
    path = folder / "rich-ui-reflex-xy-naturalistic.md"
    path.write_text(natural, encoding="utf-8")
    cases.append({"skill": "reflex-xy", "case": "naturalistic", "prompt": path.relative_to(ROOT).as_posix(), "expected": ["deliverables/flow.json", "deliverables/latency.json", "deliverables/review.json"]})
    (PROJECT / "evaluation-cases.json").write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(cases)} cases; contract once, naturalistic and boundary/generalization three times.")


if __name__ == "__main__":
    main()
