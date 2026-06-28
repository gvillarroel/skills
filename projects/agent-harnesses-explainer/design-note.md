# Visual Metaphor Design

## Concept Claim

A viewer should understand that an agent harness is the controlled execution system around a coding assistant: it lets the model use tools, observe results, respect limits, record traces, and verify work.

## Mechanic

A task enters the system, the harness routes it through a repeated observe-decide-act-verify loop, tool results become evidence, and checks decide whether a patch exits as acceptable output.

## Candidate Metaphors

- Pipeline: useful for tool handoffs, but too linear for retries and observation loops.
- Circuit board: communicates connectivity, but can become decorative and hide the control loop.
- Runtime chassis around a model: shows that the model is inside a larger operating system, while still allowing loop, gates, and evidence stacks.

Rejected: the circuit board metaphor, because the viewer may infer electrical activity rather than tool-mediated coding work.

## Chosen Metaphor

Use a runtime chassis enclosing a model core, then zoom into the harness as a loop and tool route. This makes cause and effect visible: the harness encloses the model, chooses tools, observes tool output, blocks risky actions, records evidence, and gates the final patch.

## Visual Vocabulary

- Rounded frame: the harness boundary.
- Circle: the model core.
- Small packets: task, action, and result objects that preserve identity while moving.
- Rectangular panels: tools or records, such as repo context, editor, terminal, tests, trace, and evaluation.
- Green gates: validated output.
- Red gates: blocked or risky action.
- Blue motion paths: controlled routing.
- Amber highlights: attention, active loop step, or pending evidence.

## Reuse Decision

No existing gallery scene is reused wholesale. The production reuses only low-level SVG helpers, fixed layout regions, and deterministic frame capture patterns from the local HTML video workflow.

## Narration Split

There is no local Spanish narration voice available. The video carries the explanation through concise Spanish on-screen text, while motion shows the causal chain.
