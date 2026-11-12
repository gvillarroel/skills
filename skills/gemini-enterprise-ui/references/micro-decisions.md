# One decision per agent micro UI

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

## Host adapter

Express the same bounded question with host-supported A2UI catalog components and typed A2A action/data-model updates. Use a compact choice/tree/table when arbitrary graphs are unavailable. Return through the registered agent action; do not insert MCP App messaging or arbitrary JavaScript into a catalog.
