---
name: scene-composition-director
description: Create scene-by-scene composition briefs and selection rationale for video, animation, Slidev, HTML/D3/Anime.js, Three.js, Manim, SVG, or storyboard handoffs. Use when Codex needs to choose framing, focal hierarchy, visual armature, safe areas, depth layers, asset roles, text placement, motion phases, and validation criteria for each scene or shot. Keep planning renderer-neutral by default, allow Anime.js as a downstream implementation or handoff runtime when useful, and avoid GSAP unless the user explicitly requests it.
---

# Scene Composition Director

## Core Workflow

0. In isolated validation workspaces, read `../prompt.md` directly first when the prompt or harness names it. Do not probe for the prompt, skill bundle, workspace layout, or named output paths with `ls`, `dir`, `find`, `rg`, `rg --files`, `pwd`, `Get-ChildItem`, `Test-Path`, `head`, or equivalent searches; the prompt is the path contract, and expected outputs should be created directly. After reading the prompt, either read a directly required skill file by its known path or write/create the exact requested output path. Reading `SKILL.md` does not satisfy a prompt-reading requirement. The copied skill lives at `skills/scene-composition-director`, not `../skills/scene-composition-director`; read references from that path when the prompt requests them.
1. Start with a source extraction pass from the current user message. Read `references/source-preservation.md` before designing when the prompt supplies exact scene/shot IDs, scene counts, durations, source anchors, output paths, validator arguments, or an isolated `../prompt.md` source.
2. Identify the input surface and exact deliverable before designing: storyboard, shot contract, script, narration, product brief, PR video plan, deck outline, or rough scene list. Write exact paths the user names; do not substitute a nicer filename.
3. Preserve upstream facts. If a scene comes from a `source-to-video-director` storyboard or shot contract, keep shot IDs, durations, source anchors, audience, style constraints, and media constraints intact. Do not invent missing product facts, metrics, file names, quotes, or assets.
4. Treat every normal scene as a fixed camera frame, not a web layout. Exception: when the prompt names Metro Minimal Tonal Motion, Masonry, megacanvas, strict-grid video, hard square geometry, no padding, gray hierarchy, or design feedback that the output is not following the design, plan a large navigable visual object first. Define the full megacanvas, functional zones, section bounds, camera path, and overview/detail frames before per-shot crops. Do not reduce that style to disconnected fixed slides.
5. Read `references/selection-guide.md` before choosing layouts for multiple scenes, when the user asks how to choose, or when scenes differ in role, density, assets, narration, data, or aspect ratio.
6. Read `references/composition-brief-contract.md` before writing a Markdown brief, JSON composition plan, or handoff for another video skill.
7. Write video-level direction once, then per-scene deltas:
   - format and safe zones. For Metro/design-repair prompts, set editorial/caption/title/subtitle reserved space to none unless the user explicitly asks for it; only allow functional text that belongs to visual objects.
   - shared palette/type source, without inventing colors or fonts.
   - alignment mode, grid or axis system, corner/edge policy, zero-padding box policy, grayscale hierarchy scale, and whether the operating model is fixed-frame or navigable megacanvas.
   - rhythm and held-scene allocation.
   - runtime policy: Anime.js is allowed for downstream implementation or handoff; GSAP stays out unless the user explicitly asks for it.
   - negative list. In validated JSON, do not write forbidden substrings such as `gsap` or contradictory geometry words such as `rounded`, even inside "no ..." phrases; use alternatives such as `renderer-neutral`, `square`, `0-radius`, `soft-corner`, or `curved` depending on the required meaning.
8. For each scene, make an explicit choice:
   - use exactly one output scene per supplied input scene, unless the user explicitly asks to merge or split scenes.
   - scene job and viewer task.
   - composition family and armature. For Metro/design-repair prompts, prefer Tonal Surface Megacanvas, Metro Block Board, Masonry Megacanvas, or another hard-edge modular family with a named camera path.
   - focal object, role map, text placement, safe zones, hierarchy, density, depth layers, alignment grid, edge/corner policy, box model, grayscale hierarchy, armature anchors, object bounds, and validation checks.
   - choice rationale: why this composition fits better than nearby alternatives.
9. Pace the scene across its whole duration. Use phases such as `entrance`, `development`, and `settle`, or time-coded windows when narration timing exists. Do not front-load the whole canvas in the first beat and then hold a static slide.
10. Keep planning output engine-agnostic. Describe what the viewer sees and how attention moves. It is fine to name Anime.js in `rendererHandoff` for a later renderer, but do not write HTML, Anime.js, Three.js, Manim, ffmpeg, or timeline code unless the user asks for implementation.
11. Validate machine-readable plans when practical, using the stricter expected arguments supplied by the prompt. For hard-edge, strict-grid, no-padding, or grayscale-level styles, add `--require-strict-alignment --require-square-edges --require-zero-box-padding --require-grayscale-hierarchy --require-validation-contract` to the validator command and fix the plan until it passes. These strict flags require structured `boxModel.internalPaddingPx: 0`, `contentFlushToBounds: true`, structured monotonic `grayscaleHierarchy`, concrete alignment fields, and no contradictory soft-corner or positive-padding language. When a prompt uses `--forbid gsap`, avoid unrelated substrings such as `Anime.js` in the JSON; use `renderer-neutral` instead unless the prompt explicitly requires an Anime.js handoff.

## Progressive Disclosure Map

- `references/source-preservation.md`: read before extracting source facts, using `../prompt.md`, preserving exact scene IDs, or validating required anchors.
- `references/selection-guide.md`: read for multi-scene composition choices, density, scene roles, aspect ratios, safe areas, and visual armatures.
- `references/composition-brief-contract.md`: read before writing Markdown briefs, JSON composition plans, or renderer handoffs.

## Output Shape

For a planning request, create one of these artifacts:

- `composition-plan.md`: human-readable video direction plus scene-by-scene composition briefs.
- `composition-plan.json`: machine-readable plan that follows `references/composition-brief-contract.md`.
- An in-place enrichment of an existing storyboard, keeping original scene text and appending composition fields.

If the user asks for both Markdown and JSON, make the Markdown readable by humans and the JSON strict enough for validation. If the user asks for only one file, include enough detail that a renderer skill can continue without re-reading the original prompt.

## Routing

- Use this skill after `source-to-video-director` when source facts and shot contracts already exist and the missing layer is visual composition per scene.
- Hand off implementation to `html-d3-anime-video-workflow`, `slidev-animejs`, `slidev-video`, `manim-svg-video`, `d3-animated-svg`, `echarts-animated-svg`, `mermaid-animated-svg`, or `threejs-animated-3d` only after the composition brief is clear.
- Use `d3-composition-recomposer` or `d3-composition-evaluator` for D3/SVG-only armature conversion or critique. Use this skill when the unit is a whole scene or shot.

## Validation

After changing this skill, run:

```powershell
uv run --script scripts/validate-skills.py
```

When changing JSON output behavior, also validate at least one representative plan with:

```powershell
uv run --script skills/scene-composition-director/scripts/validate_scene_composition_plan.py --plan <plan> --expect-scenes <count> --require-anchor "<literal source anchor>"
```

For isolated forward tests, prefer the checked prompt files that name exact output paths and validator arguments:

```powershell
uv run --script scripts/run-pi-skill-eval.py scene-composition-director --prompt-file evaluations/pi-prompts/scene-composition-director-zero-padding-gray.md --mode json --expect-output projects/zero-padding-composition/composition-plan.json
uv run --script scripts/run-pi-skill-eval.py scene-composition-director --prompt-file evaluations/pi-prompts/scene-composition-director-metro-hard-edge.md --mode json --expect-output projects/metro-composition-director-validation/composition-plan.json
```

When using SkillOpt or SkillOpt-Sleep on this skill, train only from reviewed tasks that include exact output paths plus validator flags. Do not adopt proposals mined from unreviewed sessions unless the generated plan passes the bundled validator with the same strict prompt arguments.
