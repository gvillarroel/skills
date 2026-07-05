---
name: scene-transition-director
description: Design and validate memorable transitions between video, animation, Slidev, HTML/D3/Anime.js, Three.js, Manim, or storyboard scenes. Use when Codex needs to decide what persists across cuts, how a surprising recurring element evolves, how attention is handed off, and whether composition, color, zoom, depth, camera, space, or rhythm should change between scenes before implementation or final render.
---

# Scene Transition Director

## Core Workflow

0. In isolated validation workspaces, read `../prompt.md` directly first when the prompt or harness names it. Do not probe for it with `ls`, `dir`, `find`, `pwd`, `Get-ChildItem`, or `Test-Path`; the prompt is the path contract. Reading `SKILL.md` does not satisfy a prompt-reading requirement. The copied skill lives at `skills/scene-transition-director`, not `../skills/scene-transition-director`; read references from that path when the prompt requests them.
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
   - `semantic purpose`: why this transition exists.
   - `state change`: what changes in object state, attention, abstraction, space, or rhythm.
   - `generic motion rejected`: why a generic slide, pan, wipe, or pulse would be wrong for this cut.
   - `box padding rule`: whether masks, panels, cards, and apertures keep zero internal padding.
   - `grayscale hierarchy rule`: how hierarchy levels remain distinguishable through gray values during the cut.
7. Use transition families intentionally: `match cut`, `persistent object`, `camera move`, `color handoff`, `spatial portal`, `morph`, or `interrupt`.
8. Preserve style through the cut. When the sequence uses strict alignment, Metro, terminal, blueprint, technical, editorial-grid, or hard-edge aesthetics, keep paths orthogonal or grid-locked, use square apertures and rectangular masks, preserve stroke widths, keep boxes at zero internal padding, and preserve grayscale hierarchy levels. In validated JSON, do not write soft-corner contradiction terms even inside "no ..." phrases; use `0-radius`, `square`, `hard-edge`, or `curved` instead.
9. Vary transitions across a sequence. Repeat the same transition only when the repeated structure is the lesson.
10. Read `references/transition-plan-contract.md` before writing `transition-plan.md`, `transition-plan.json`, or an implementation handoff.
11. Validate JSON plans with `scripts/validate_transition_plan.py` when practical. If the prompt supplies a validator command, run that exact command and do not weaken `--expect-transitions`, `--expect-persistent-name`, `--expect-chain`, `--require-anchor`, or `--forbid` arguments. For semantic, hard-edge, no-padding, or grayscale-level transition plans, add `--require-semantic-fields --require-square-edge-style --require-zero-box-padding --require-grayscale-hierarchy` and fix the JSON until it passes. These flags require the persistent element to appear in transition states, structured grayscale levels, zero internal padding without positive-padding contradictions, and no soft-corner contradictions. Do not include forbidden substrings in JSON as negative examples; validators treat them as plain text.

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
