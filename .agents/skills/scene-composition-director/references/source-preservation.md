# Source Preservation

Use this file before designing when the prompt supplies exact scene or shot IDs, scene counts, durations, source anchors, output paths, validator arguments, or an isolated `../prompt.md` source.

## Source Extraction

The current user message is always allowed source material and is the highest-priority contract.

Before reading other references or searching files:

1. In isolated harnesses, read `../prompt.md` directly and treat it as the current user message for this run.
2. Do not probe for `../prompt.md` with shell listings or existence checks.
3. If the file-read tool cannot open `../prompt.md` because it is outside the workspace, read it once with `cat ../prompt.md` from the shell.

Copy these values before designing:

- requested output path and format
- exact scene or shot IDs
- exact scene count
- durations
- source anchors
- audience and style constraints
- alignment mode, grid language, axis system, aspect ratio, typography constraints, edge/corner policy, zero box-padding policy, grayscale hierarchy rules, and prohibited motifs
- caption and media constraints
- validator arguments

If scene or shot details appear in the current user message, do not ask the user to provide them again. Create the requested output artifact from that text.

## Read Surface In Isolated Runs

If the current prompt already lists scenes or shots, do not run filesystem searches to discover alternate source material. Read only:

- current user message, or exactly `../prompt.md` when the harness does not expose the live message
- `skills/scene-composition-director/SKILL.md`
- required files under `skills/scene-composition-director/references/`
- the validator script when needed
- the generated plan you are validating

In isolated harnesses, `../prompt.md` is the only allowed parent-directory source file. Do not read other parent-directory prompts, sibling run folders, previous project artifacts, old prompts, example outputs, `C:/Users/.../projects/...`, `evaluations/runs/...`, or old `composition-plan.json` files as source facts.

## Preservation Rules

- Treat the user's current prompt as source material.
- If the prompt lists exact scene or shot IDs, copy them into a checklist before designing.
- Use exactly one output scene per supplied input scene unless the user explicitly asks to merge or split scenes.
- The output must contain exactly the supplied scene IDs unless the user explicitly asks for a different count.
- If the prompt lists required anchors or a validator command, copy every anchor literally into `videoDirection.sourceAnchors` and relevant scenes before adding composition rationale.
- Treat strict alignment, square/no-rounded edges, hard-edge panels, zero internal box padding, grayscale hierarchy levels, palette limits, typography rules, aspect ratio, and prohibited motifs as hard source constraints, not taste preferences.
- Do not search parent directories, sibling workspaces, old validation outputs, or previous prompts for replacement source facts.

## Validation

Validate machine-readable plans with:

```powershell
uv run --script .agents/skills/scene-composition-director/scripts/validate_scene_composition_plan.py --plan composition-plan.json --forbid gsap
```

If the prompt supplies `--expect-scenes`, `--require-anchor`, or `--forbid`, copy those arguments literally into the validation command before finishing and fix the plan until it passes. Do not replace supplied expectations with easier values.

For strict-grid or square-edge styles, add:

```powershell
--require-strict-alignment --require-square-edges --require-validation-contract
```

For no-padding or grayscale-level critiques, also add:

```powershell
--require-zero-box-padding --require-grayscale-hierarchy
```

Never finish by asking for a shot list after reading a prompt that contains a `Shots:` or `Scenes:` section.
