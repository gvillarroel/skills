# Source Preservation

Use this file before writing a transition plan when the prompt supplies exact source facts, transition counts, scene IDs, persistent element names, required phrases, or validator arguments.

## Source Extraction

The current user message is always allowed source material and is the highest-priority contract.

Before reading other references or searching files:

1. In isolated harnesses, read `../prompt.md` directly and treat it as the current user message for this run.
2. Do not probe for `../prompt.md` with shell listings or existence checks.
3. If the file-read tool cannot open `../prompt.md` because it is outside the workspace, read it once with `cat ../prompt.md` from the shell.

Copy these values before designing:

- exact requested output path
- exact persistent element name, if supplied
- exact scene IDs in order
- scene durations and visual states
- exact required phrases, object names, and color names
- style constraints such as strict alignment, square/0-radius edges, zero internal box padding, grayscale hierarchy levels, hard-edge masks, aspect ratio, typography constraints, palette limits, and prohibited motifs
- exact transition count
- validator arguments

If transition source details appear in the current user message, do not ask the user to provide them again. Create the requested output artifact from that text.

## Read Surface In Isolated Runs

If the prompt already lists source scenes, do not run filesystem searches to discover alternate source material. Read only:

- current user message, or exactly `../prompt.md` when the harness does not expose the live message
- `skills/scene-transition-director/SKILL.md`
- required files under `skills/scene-transition-director/references/`
- the validator script when needed
- the plan you write in the current workspace

In isolated harnesses, `../prompt.md` is the only allowed parent-directory source file. Do not read other parent folders, sibling workspaces, old run outputs, previous prompts, `evaluations/runs`, or example transition plans as source facts.

## Preservation Rules

- If the prompt lists scene IDs, use those exact IDs in `fromScene` and `toScene`.
- If the prompt gives an exact transition count, produce exactly that count.
- If no exact count is given, default to one transition per adjacent scene boundary.
- If the prompt names a persistent element, copy that name exactly into `persistentElement.name`.
- Treat strict alignment, square/0-radius edges, zero internal box padding, grayscale hierarchy levels, hard-edge masks, palette limits, and prohibited motifs as hard transition constraints, not optional polish.
- Do not substitute example names such as `task packet`, `data token`, `request packet`, or `work item` unless the prompt uses that exact phrase.
- Do not replace supplied expectations with easier validator values.

Literal substitutions are validation failures. For example, `work packet` must not become `control token`, `blue data packet`, or `task packet`; `s01-intake` must not become `s01-problem-intro`; `s02-tool-use` must not become `s02-queue`; and `s03-proof` must not become `s03-complete`.

## Mechanical Scene Chain

For prompts that list scenes:

1. Copy the scene IDs in order exactly as written.
2. Create one transition for each adjacent pair unless the prompt gives a different exact count.
3. Set `fromScene` to scene ID `i` and `toScene` to scene ID `i + 1`.
4. Set `persistentElement.name` to the exact supplied persistent element name.
5. Keep supplied object/color phrases in the relevant transition text.
6. Run the validator with `--expect-chain` when the scene chain is known.

Example: `s01-intake`, `s02-tool-use`, `s03-proof` means exactly two transitions: `s01-intake -> s02-tool-use` and `s02-tool-use -> s03-proof`.

If the prompt supplies a validator command or expected arguments, copy those arguments literally into the validation command before finishing and fix the JSON until it passes. A bare `--plan transition-plan.json` validation is insufficient when the prompt supplies stricter arguments.

For semantic hard-edge plans, add `--require-semantic-fields --require-square-edge-style` unless the prompt explicitly allows soft-corner transition geometry. For no-padding or grayscale-level critiques, also add `--require-zero-box-padding --require-grayscale-hierarchy`.
