---
name: scene-composition-director
description: Create scene-by-scene composition briefs and selection rationale for video, animation, Slidev, HTML/D3/Anime.js, Three.js, Manim, SVG, or storyboard handoffs. Use when Codex needs to choose framing, focal hierarchy, visual armature, safe areas, depth layers, asset roles, text placement, motion phases, and validation criteria for each scene or shot. Keep planning renderer-neutral by default, allow Anime.js as a downstream implementation or handoff runtime when useful, and avoid GSAP unless the user explicitly requests it.
---

# Scene Composition Director

## Workflow

0. Start with a source extraction pass from the current user message. The current user message is always allowed source material and is the highest-priority contract:
   - Before reading references or searching for files, check whether `../prompt.md` exists. If it exists, read it immediately and treat it as the current user message for this run. If the file-read tool cannot open `../prompt.md` because it is outside the workspace, read it with `cat ../prompt.md` from the shell instead.
   - Copy the requested output path, exact scene/shot IDs, exact scene count, durations, source anchors, audience, style, caption/media constraints, and any validator arguments.
   - If scene or shot details appear in the current user message, do not ask the user to provide them again. Create the requested output artifact from that text.
   - If the current prompt already lists scenes or shots, do not run filesystem searches to discover alternate source material. Read only this `SKILL.md`, the required references below, and the generated plan you are validating.
   - In isolated harnesses, `../prompt.md` is the only allowed parent-directory source file. Do not read any other parent-directory prompt or run artifact.
   - Never use parent directories, sibling run folders, previous project artifacts, old prompts, or example outputs as source facts for a new plan.
   - In isolated validation, the normal read surface is the current user message, or exactly `../prompt.md` when the harness does not expose the live message, plus `skills/scene-composition-director/SKILL.md`, the required files under `skills/scene-composition-director/references/`, the validator script, and the plan you write in the current workspace. Do not read `C:/Users/.../projects/...`, `evaluations/runs/...`, old prompt files, or old `composition-plan.json` files as examples.
1. Identify the input surface and exact deliverable before designing:
   - storyboard, shot contract, script, narration, product brief, PR video plan, deck outline, or rough scene list.
   - requested output path and format. Write exact paths the user names; do not substitute a nicer filename.
2. Preserve upstream facts. If a scene comes from a `source-to-video-director` storyboard or shot contract, keep shot IDs, durations, source anchors, audience, style constraints, and media constraints intact. Do not invent missing product facts, metrics, file names, quotes, or assets.
   - Treat the user's current prompt as source material. Do not search parent directories, sibling workspaces, `evaluations/runs`, old validation outputs, or previous prompts for replacement source facts.
   - If the prompt lists exact scene or shot IDs, copy them into a checklist before designing. The output must contain exactly those scene IDs unless the user explicitly asks for a different count.
   - If the prompt lists required anchors or a validator command, copy every anchor literally into `videoDirection.sourceAnchors` and relevant scenes before adding composition rationale.
3. Treat every scene as a fixed camera frame, not a web layout. Plan the poster frame first: focal point, hierarchy, safe zones, armature, density, depth layers, and reading path. Then plan motion as semantic phases.
4. Read `references/selection-guide.md` before choosing layouts for multiple scenes, when the user asks how to choose, or when scenes differ in role, density, assets, narration, data, or aspect ratio.
5. Read `references/composition-brief-contract.md` before writing a Markdown brief, JSON composition plan, or handoff for another video skill.
6. Write video-level direction once, then per-scene deltas:
   - format and safe zones, including caption keep-out if captions may exist.
   - shared palette/type source, without inventing colors or fonts.
   - rhythm and held-scene allocation.
   - runtime policy: Anime.js is allowed for downstream implementation or handoff; GSAP stays out unless the user explicitly asks for it.
   - negative list, including no GSAP by default.
7. For each scene, make an explicit choice:
   - use exactly one output scene per supplied input scene, unless the user explicitly asks to merge or split scenes.
   - scene job and viewer task.
   - composition family and armature.
   - focal object, role map, text placement, safe zones, hierarchy, density, depth layers, and validation checks.
   - choice rationale: why this composition fits better than nearby alternatives.
8. Pace the scene across its whole duration. Use phases such as `entrance`, `development`, and `settle`, or time-coded windows when narration timing exists. Do not front-load the whole canvas in the first beat and then hold a static slide.
9. Keep planning output engine-agnostic. Describe what the viewer sees and how attention moves. It is fine to name Anime.js in `rendererHandoff` for a later renderer, but do not write HTML, Anime.js, Three.js, Manim, ffmpeg, or timeline code unless the user asks for implementation.
10. Validate machine-readable plans when practical:

```powershell
uv run --script .agents/skills/scene-composition-director/scripts/validate_scene_composition_plan.py --plan composition-plan.json --forbid gsap
```

If the prompt supplies `--expect-scenes`, `--require-anchor`, or `--forbid`, copy those arguments literally into the validation command before finishing and fix the plan until it passes. Do not replace supplied expectations with easier values, and do not finish with a plan that only passes a weakened validator command. Never finish by asking for a shot list after reading a prompt that contains a `Shots:` or `Scenes:` section.

## Output Shape

For a planning request, create one of these artifacts:

- `composition-plan.md`: human-readable video direction plus scene-by-scene composition briefs.
- `composition-plan.json`: machine-readable plan that follows `references/composition-brief-contract.md`.
- An in-place enrichment of an existing storyboard, keeping original scene text and appending composition fields.

If the user asks for both Markdown and JSON, make the Markdown readable by humans and the JSON strict enough for validation. If the user asks for only one file, include enough detail that a renderer skill can continue without re-reading the original prompt.

## Routing

- Use this skill after `source-to-video-director` when source facts and shot contracts already exist and the missing layer is visual composition per scene.
- Hand off implementation to `html-d3-anime-video-workflow`, `slidev-animejs`, `slidev-video`, `manim-svg-video`, `d3-animated-svg`, `echarts-animated-svg`, `mermaid-animated-svg`, or `threejs-animated-3d` only after the composition brief is clear. Prefer the Anime.js-capable skills when the user says Anime.js is acceptable or desired.
- Use `d3-composition-recomposer` or `d3-composition-evaluator` for D3/SVG-only armature conversion or critique. Use this skill when the unit is a whole scene or shot.

## Validation

After changing this skill, run:

```powershell
uv run --script scripts/validate-skills.py
```

For generated JSON plans, run the bundled validator with expected anchors and scene counts when supplied:

```powershell
uv run --script .agents/skills/scene-composition-director/scripts/validate_scene_composition_plan.py --plan composition-plan.json --expect-scenes 4 --require-anchor "final CTA" --forbid gsap
```
