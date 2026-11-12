#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Make decision-focused micro UIs the default for agent interactions."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
NAMES = ["desktop-plugin-ui", "desktop-chat-plugin-ui", "code-native-plugin-ui", "pi-extension-ui", "codex-plugin-ui", "chatgpt-desktop-plugin-ui", "gemini-enterprise-ui"]
COMMON = """# One decision per agent micro UI

Use a temporary decision surface when the agent needs a person's judgment to
continue. Start with one concrete unresolved question, its options and the
typed answer the agent needs. Keep the application/task state with the agent.

## Relevance gate

For every visible element, state how it can change this decision, justify an
option, reveal uncertainty or prevent a mistake. Remove elements without that
role. Conversation context often already supplies the project, product and
workflow; avoid repeating it as banners, titles, counters and permanent panels.
Use one question as the heading, a constraint only when necessary, comparable
alternatives, directly relevant evidence and one decision action.

Default to one decision per surface. Selection, inspecting evidence and testing
a relevant scenario are exploration within that decision. A second independent
decision belongs in a subsequent agent step. Allow deferral when evidence is
insufficient; do not force a default answer or silently convert Escape to one.

Do not turn an agent interaction into a miniature website. Omit global tabs,
directories, search, dashboards, generic settings and navigation unless they
are necessary to distinguish the actual options. A graph may be sophisticated
internally while exposing only the neighborhood that affects the choice. Show
coverage/omission counts only when they matter to the person's judgment. A
continuous application/workbench is appropriate when the user explicitly asks
for that broader workflow; capacity stress fixtures are not the agent default.

## Compare a taxonomic ambiguity

For a disputed primary parent, show the term's operative definition and two
local placement alternatives. Give them comparable geometry, label scale and
context. Highlight the disputed concept consistently and include only parents,
siblings or consequences needed to judge placement. A card's parent heading
can also label the root; avoid repeating it as another diagram title.

Give each alternative a short reason. Put passage evidence, scope boundaries or
counterexamples behind a named disclosure when needed. Evidence exploration
must return to the same pending choice. Keep unrelated branches and whole-
taxonomy navigation with the agent. Prefer a plain choice or text tree when
custom graph geometry adds no decision value.

## Return control to the agent

Define a bounded result such as `{decisionId, questionRevision, outcome,
optionId}` with `selected` or `deferred`. Validate the answer against the offered
IDs and question revision. Preserve receipt/idempotency and stale-question
checks internally; show implementation metadata only when it helps recover a
conflict. Recording a preference does not itself apply a taxonomy mutation.

Complete the host's pending interaction with the result, then let the agent
continue its task. A hidden panel, a server receipt and a model-context update
are different events. In MCP Apps, `updateModelContext` supplies a future turn;
it does not trigger a response. After the user's explicit continue action,
feature-detect the host's text-message capability and send at most one
continuation message. Check its acknowledgement. Do not automatically retry a
message after an unknown result. If continuation is unsupported, expose a
direct chat fallback and retain the recorded choice without claiming a resumed
agent turn. Keep controls unavailable until the actual bridge is ready.

Native awaited dialogs/custom components must resolve through their completion
callback with the typed choice. Explicit arguments supply print/JSON fallbacks.
A user-invoked demonstration command may put its result into model-visible
history without starting a model turn; report that boundary accurately.

## Semantic terminal presentation

Use the host theme's semantic roles where available: accent for active choice,
warning for the unresolved subject, success for an acknowledged selected
answer, error for a failed action, and muted/dim for supporting context. Keep
deferral neutral. Use labels, circles/checks and weight alongside color so the
interaction survives monochrome or accessibility themes. Do not hard-code RGB
escapes over a native theme. Owned terminals without theme roles may use a
documented semantic palette with contrast checks.

Use one strong question, bounded whitespace, subtle separators and aligned tree
connectors. Reserve the host's actual terminal rows. Fit both alternatives and
the decision keys at a short width, or use a decision-relevant disclosure.
Repeat the question/context when opening evidence. Avoid decorative frames and
permanent instruction paragraphs. Prefer native selection when formatting adds
no meaning; custom TUI is useful for comparative structure.

## Acceptance

Verify that every visible datum is relevant, one answer completes the task,
deferral chooses nothing, and evidence does not become global navigation.
Test selection, keyboard focus, returned IDs, duplicate clicks, stale question,
unknown acknowledgement and the host's actual continuation boundary. Capture
the undecided, selected and returned states at the allocated panel width or
terminal size. Inspect color meaning and label legibility in actual pixels.
Keep browser/protocol/native/stock-host results separate. Never call a fixture
message acknowledgement a live model continuation.

"""
HOST = {
    "desktop-plugin-ui": "Compare the one-decision adapter and result/continuation route across hosts. Keep the domain question shared and surface mechanisms independent. A plan request needs a plan, not an extra prototype.\n",
    "desktop-chat-plugin-ui": "Use a focused MCP App or ordinary text choice in Claude Chat. Verify the actual Chat resource, choice tool, host-message capability and acknowledgement independently. Desktop Code has a separate renderer.\n",
    "code-native-plugin-ui": "Use native Claude Code commands/Mods and supported controls. Keep any local tree within the choice; return through the real request/component completion route. Verify terminal, Desktop Code and VS Code separately. Do not embed arbitrary HTML in a native node.\n",
    "pi-extension-ui": "Use native select for simple choices, or a theme-aware TUI for meaningful comparative structure. Guard custom rendering with ctx.mode === tui; RPC needs native UI requests with matching response IDs. The bundled micro-choice.ts is a tested standalone formatted example with evidence disclosure, neutral deferral and model-visible result without a new turn.\n",
    "codex-plugin-ui": "Choose the actual executing Codex surface. Verify task-local loader/tool acceptance separately from an MCP App's paint and continuation. An integrated-browser demo is an owned browser surface. Keep absent host-message capability an explicit fallback.\n",
    "chatgpt-desktop-plugin-ui": "Use a focused MCP App when graph comparison helps. Check local/remote Desktop loader, actual component placement, direct tool receipt and host text-message capability. A context update alone is not continuation, and Codex mode does not establish stock ChatGPT acceptance.\n",
    "gemini-enterprise-ui": "Express the same bounded question with host-supported A2UI catalog components and typed A2A action/data-model updates. Use a compact choice/tree/table when arbitrary graphs are unavailable. Return through the registered agent action; do not insert MCP App messaging or arbitrary JavaScript into a catalog.\n",
}

def main():
    for name in NAMES:
        skill = ROOT / "skills" / name
        (skill / "references/micro-decisions.md").write_text(COMMON + "## Host adapter\n\n" + HOST[name], encoding="utf-8", newline="\n")
        p = skill / "SKILL.md"
        text = p.read_text(encoding="utf-8")
        introduction = "Start with the pending human decision. Read\n[micro-decisions.md](references/micro-decisions.md) for the default agent UI:\none bounded question, only decision-relevant evidence, and a typed result\nreturned to the agent. Use a full workspace only when the user requests it.\n\n"
        if "[micro-decisions.md]" not in text:
            at = text.index("For graphs, charts,")
            text = text[:at] + introduction + text[at:]
        if name == "pi-extension-ui" and "[micro-choice.ts]" not in text:
            text += "\nFor a formatted single-choice TUI with semantic theme colors, adapt\n[micro-choice.ts](assets/templates/pi-command/micro-choice.ts).\n"
        p.write_text(text, encoding="utf-8", newline="\n")
        p = skill / "agents/openai.yaml"
        lines = p.read_text(encoding="utf-8").splitlines()
        lines = [f'  default_prompt: "Use ${name} for one focused human decision, relevant evidence and a result returned to the agent; validate the actual host and use semantic native styling."' if line.strip().startswith("default_prompt:") else line for line in lines]
        p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    shutil.copy2(ROOT / "projects/plugin-ui-micro-decisions/pi/taxonomy-choice.ts", ROOT / "skills/pi-extension-ui/assets/templates/pi-command/micro-choice.ts")
    print("Promoted one-decision defaults, semantic terminal guidance and the verified Pi template to seven independent bundles.")

if __name__ == "__main__":
    main()
