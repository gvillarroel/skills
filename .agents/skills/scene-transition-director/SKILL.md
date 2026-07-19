---
name: scene-transition-director
description: Design and validate memorable transitions between video, animation, Slidev, HTML/D3/Anime.js, Three.js, Manim, or storyboard scenes. Use when Codex needs to decide what persists across cuts, how a surprising recurring element evolves, how attention is handed off, and whether composition, color, zoom, depth, camera, space, or rhythm should change between scenes before implementation or final render.
---

# Scene Transition Director

## Core Workflow

0. In isolated validation workspaces, read `../prompt.md` directly first when the prompt or harness names it. Do not probe for the prompt, skill bundle, workspace layout, or named output paths with `ls`, `dir`, `find`, `rg`, `rg --files`, `pwd`, `Get-ChildItem`, `Test-Path`, `head`, or equivalent searches; the prompt is the path contract, and expected outputs should be created directly. After reading the prompt, either read a directly required skill file by its known path or write/create the exact requested output path. Reading `SKILL.md` does not satisfy a prompt-reading requirement. The copied skill lives at `skills/scene-transition-director`, not `../skills/scene-transition-director`; read references from that path when the prompt requests them.
1. Start with a source extraction pass from the current user message. Read `references/source-preservation.md` before writing a plan when the prompt supplies scene IDs, transition counts, persistent element names, validator arguments, required phrases, or an isolated `../prompt.md` source.
2. Preserve upstream scene facts. Keep scene IDs, durations, source anchors, audience, style, media constraints, exact required phrases, and deliverable paths. Do not invent extra scenes, products, systems, examples, or source facts.
3. Identify the persistent element before choosing transition effects:
   - It may be an object, token, packet, cursor, camera target, trace line, color role, sound cue, spatial axis, or layout rule.
   - If the prompt names the persistent element, copy that phrase exactly into `persistentElement.name`. Treat any synonym, relabeling, or scenario-specific improvement as a validation failure.
   - Give it a stable semantic role and state how it changes from scene to scene without changing its exact name.
   - Avoid decorative elements that only look continuous; the persistent element must carry meaning.
4. Read `references/transition-decision-guide.md` when designing more than one transition, revising weak cuts, or deciding color, zoom, space, camera, surprise, persistence, or rhythm.
5. Read `references/transition-pattern-catalog.md` when the user asks to experiment, provide several transition types, build a transition vocabulary, or make adjacent cuts feel visibly different.
6. Plan each cut as a transition beat, not as the end of one scene and start of another:
   - `outgoing state`: what the viewer is holding at the end of the source scene.
   - `bridge action`: what persists, transforms, wipes, pulls focus, or changes space.
   - `incoming state`: what lands in the target scene and why attention is already in the right place.
   - `surprise`: the memorable perceptual turn or reveal that makes the transition worth seeing.
   - `semantic purpose`: why this transition exists.
   - `state change`: what changes in object state, attention, abstraction, space, or rhythm.
   - `generic motion rejected`: why a generic slide, pan, wipe, or pulse would be wrong for this cut.
   - `box padding rule`: whether masks, panels, cards, and apertures keep zero internal padding.
   - `grayscale hierarchy rule`: how hierarchy levels remain distinguishable through gray values during the cut.
7. Use transition families intentionally: `match cut`, `persistent object`, `camera move`, `color handoff`, `spatial portal`, `morph`, or `interrupt`.
8. Preserve style through the cut. When the sequence uses strict alignment, Metro, terminal, blueprint, technical, editorial-grid, or hard-edge aesthetics, keep paths orthogonal or grid-locked, use square apertures and rectangular masks, preserve stroke widths, keep boxes at zero internal padding, and preserve grayscale hierarchy levels. In validated JSON, do not write soft-corner contradiction terms even inside "no ..." phrases; use `0-radius`, `square`, `hard-edge`, or `curved` instead.
9. Vary transitions across a sequence. Repeat the same transition only when the repeated structure is the lesson.
10. Read `references/transition-plan-contract.md` before writing `transition-plan.md`, `transition-plan.json`, or an implementation handoff.
11. Validate JSON plans with `scripts/validate_transition_plan.py` when practical. If the prompt supplies a validator command, run that exact command and do not weaken `--expect-transitions`, `--expect-persistent-name`, `--expect-chain`, `--require-anchor`, or `--forbid` arguments. Before the first validation run, every transition must already include all required validator fields: `id`, `fromScene`, `toScene`, `start`, `duration`, `family`, `surprise`, `outgoingState`, `bridgeAction`, `incomingState`, `compositionShift`, `colorShift`, `cameraShift`, `spaceShift`, and `validationChecks`. For semantic, hard-edge, no-padding, or grayscale-level transition plans, add `--require-semantic-fields --require-square-edge-style --require-zero-box-padding --require-grayscale-hierarchy` and fix the JSON until it passes. These flags require the persistent element to appear in transition states, structured grayscale levels, zero internal padding without positive-padding contradictions, and no soft-corner contradictions. Do not include forbidden substrings in JSON as negative examples; validators treat them as plain text.

## Progressive Disclosure Map

- `references/source-preservation.md`: read before extracting source facts, using `../prompt.md`, preserving exact scene chains, or validating source anchors.
- `references/transition-decision-guide.md`: read for multi-transition design choices and weak-cut revisions.
- `references/transition-pattern-catalog.md`: read for a broader transition vocabulary or intentionally varied transition families.
- `references/transition-plan-contract.md`: read before writing Markdown or JSON transition deliverables.

## Implementation Handoff

- Hand off scene layout to `scene-composition-director`.
- Hand off standalone HTML/D3/Anime.js render work to `html-d3-anime-video-workflow`.
- Hand off Slidev, Manim, SVG, ECharts, D3, or Three.js specifics to the owning skill.
- Keep transition planning renderer-neutral until implementation is requested.
- If implementing, verify the transition in full-speed playback and a contact sheet; contact sheets alone often miss temporal continuity failures.

## Validation

After changing this skill, run:

```powershell
uv run --script scripts/validate-skills.py
```

When changing JSON output behavior, also validate at least one representative plan with:

```powershell
uv run --script skills/scene-transition-director/scripts/validate_transition_plan.py --plan <plan> --expect-transitions <count> --expect-persistent-name "<literal name>"
```

For isolated forward tests, prefer the checked prompt files that name exact output paths and validator arguments:

```powershell
uv run --script scripts/run-pi-skill-eval.py scene-transition-director --prompt-file evaluations/pi-prompts/scene-transition-director-zero-padding-gray.md --mode json --expect-output projects/zero-padding-transition/transition-plan.json
uv run --script scripts/run-pi-skill-eval.py scene-transition-director --prompt-file evaluations/pi-prompts/scene-transition-director-metro-hard-edge.md --mode json --expect-output projects/metro-transition-director-validation/transition-plan.json
```

When using SkillOpt or SkillOpt-Sleep on this skill, train only from reviewed tasks that include exact scene chains, persistent element names, output paths, and validator flags. Do not adopt proposals mined from unreviewed sessions unless the generated transition plan passes the bundled validator with the same strict prompt arguments.
