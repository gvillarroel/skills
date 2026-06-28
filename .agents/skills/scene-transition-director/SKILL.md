---
name: scene-transition-director
description: Design and validate memorable transitions between video, animation, Slidev, HTML/D3/Anime.js, Three.js, Manim, or storyboard scenes. Use when Codex needs to decide what persists across cuts, how a surprising recurring element evolves, how attention is handed off, and whether composition, color, zoom, depth, camera, space, or rhythm should change between scenes before implementation or final render.
---

# Scene Transition Director

## Core Workflow

0. Start with a mechanical source extraction pass from the current user message. The current user message is always allowed source material and is the highest-priority contract:
   - Before reading references or searching for files, check whether `../prompt.md` exists. If it exists, read it immediately and treat it as the current user message for this run. If the file-read tool cannot open `../prompt.md` because it is outside the workspace, read it with `cat ../prompt.md` from the shell instead.
   - Copy the exact requested output path.
   - Copy the exact persistent element name, if supplied.
   - Copy the exact scene IDs in order, with their durations and visual states.
   - Copy exact required phrases such as `yellow task card`, `blue tool packet`, and `green proof card`.
   - Copy any exact transition count or validator arguments.
   - If transition source details appear in the current user message, do not ask the user to provide them again. Create the requested output artifact from that text.
   If the prompt already lists source scenes, do not run filesystem searches to discover alternate source material. Read only this `SKILL.md`, the required references below, the validator script when needed, and the generated plan you are validating.
   In isolated harnesses, `../prompt.md` is the only allowed parent-directory source file. Do not read any other parent-directory prompt or run artifact.
   In isolated validation, the normal read surface is the current user message, or exactly `../prompt.md` when the harness does not expose the live message, plus `skills/scene-transition-director/SKILL.md`, required files under `skills/scene-transition-director/references/`, the validator script, and the plan you write in the current workspace. Do not read other parent folders, old run outputs, previous prompts, or example transition plans as source facts.
1. Preserve the upstream scene facts. Keep scene IDs, durations, source anchors, audience, style, and media constraints from the storyboard or shot contract.
   - Do not invent extra scenes, products, systems, examples, or source facts.
   - Treat the user's current prompt as source material. Do not search parent directories, sibling workspaces, `evaluations/runs`, old validation outputs, or previous prompts for replacement source facts.
   - If the prompt lists scene IDs, use those exact IDs in `fromScene` and `toScene`.
   - If the prompt gives an exact transition count, produce exactly that count.
   - If no exact count is given, default to one transition per adjacent scene boundary.
   - If the prompt names a persistent element, copy that name exactly into `persistentElement.name`. Do not substitute example names such as `task packet`, `data token`, `request packet`, or `work item` unless the prompt uses that exact phrase.
   - Literal substitutions are validation failures. For example, `work packet` must not become `control token`, `blue data packet`, or `task packet`; `s01-intake` must not become `s01-problem-intro`; `s02-tool-use` must not become `s02-queue`; and `s03-proof` must not become `s03-complete`.
2. Identify the persistent element before choosing transition effects:
   - It may be an object, token, packet, cursor, camera target, trace line, color role, sound cue, spatial axis, or layout rule.
   - Give it a stable semantic role and state how it changes from scene to scene.
   - Avoid decorative elements that only look continuous; the persistent element must carry meaning.
3. Read `references/transition-decision-guide.md` when designing more than one transition, revising weak cuts, or deciding color, zoom, space, camera, surprise, persistence, or rhythm.
4. Read `references/transition-pattern-catalog.md` when the user asks to experiment, provide several transition types, build a transition vocabulary, or make adjacent cuts feel visibly different.
5. Plan each cut as a transition beat, not as the end of one scene and start of another:
   - `outgoing state`: what the viewer is holding at the end of the source scene.
   - `bridge action`: what persists, transforms, wipes, pulls focus, or changes space.
   - `incoming state`: what lands in the target scene and why attention is already in the right place.
6. Use transition families intentionally:
   - `match cut` when shape, position, or role continues.
   - `persistent object` when the same entity carries story state.
   - `camera move` when scale, zoom, pan, or depth explains a change of abstraction.
   - `color handoff` when a role changes state or becomes the next focal system.
   - `spatial portal` when the viewer moves between conceptual spaces.
   - `morph` when one diagram role becomes another.
   - `interrupt` when surprise or contrast is the point.
7. Vary transitions across a sequence. Repeat the same transition only when the repeated structure is the lesson. In an experimental or spectacle pass, prefer scene-level mechanics over repeated object flight: static anchor sweep, object color cover, extreme zoom reframe, full-screen color card, color-to-white reset, portal reveal, camera/parallax move, interrupt gate, or morph.
8. Write a transition plan before implementation when the request affects multiple scenes.
9. Validate JSON plans with `scripts/validate_transition_plan.py` when practical.

## Source Preservation Gate

Before writing a plan, make a short internal checklist:

- exact output path
- exact scene IDs and order
- exact scene count and transition count
- exact persistent element name, if supplied
- exact required terms such as color, object names, scene labels, or deliverable paths

Reject any draft that substitutes its own scenario, adds unrequested scenes, changes the persistent element name, changes supplied scene IDs, changes supplied color/object phrases, or copies example content from this skill instead of the user's source.

For prompts that list scenes, build the transition chain mechanically:

1. Copy the scene IDs in order exactly as written.
2. Create one transition for each adjacent pair unless the prompt gives a different exact count.
3. Set `fromScene` to scene ID `i` and `toScene` to scene ID `i + 1`.
4. Set `persistentElement.name` to the exact supplied persistent element name.
5. Keep supplied object/color phrases in the relevant transition text.
6. Run the validator with `--expect-chain` when the scene chain is known.

If the prompt supplies a validator command or expected arguments, copy those arguments literally into the validation command before finishing and fix the JSON until it passes. A bare `--plan transition-plan.json` validation is insufficient when the prompt supplies stricter arguments. Do not replace supplied expectations with easier values, and do not finish with a plan that only passes a weakened validator command. A file that exists but fails the supplied validator is not a completed deliverable. Never finish by validating against a transition count, persistent name, or scene chain that differs from the supplied prompt.
If validation fails, fix the exact failed fields in the existing JSON. Do not ignore a failed validator and do not replace the user's source scenario with a generic transition sequence.

Example: `s01-intake`, `s02-tool-use`, `s03-proof` means exactly two transitions: `s01-intake -> s02-tool-use` and `s02-tool-use -> s03-proof`.

## Output Shape

For planning or renderer handoff, create one of:

- `transition-plan.md`: readable transition direction and per-cut briefs.
- `transition-plan.json`: machine-readable transition plan.
- An added `Transitions` section in an existing storyboard or production notes.

For `transition-plan.json`, use this shape:

```json
{
  "version": 1,
  "videoId": "stable-video-id",
  "persistentElement": {
    "name": "task packet",
    "role": "viewer-tracked work item",
    "states": ["task", "loop packet", "tool request", "blocked action", "final proof"]
  },
  "transitions": [
    {
      "id": "t01",
      "fromScene": "s01",
      "toScene": "s02",
      "start": 8.2,
      "duration": 1.1,
      "family": "persistent object",
      "surprise": "The task packet exits the harness frame and becomes the loop packet.",
      "outgoingState": "Patch packet is visible at the right edge.",
      "bridgeAction": "Packet pulls a teal trace line across the cut.",
      "incomingState": "Packet lands on the observe node.",
      "compositionShift": "Centered enclosure becomes radial loop.",
      "colorShift": "Teal harness boundary becomes active loop path.",
      "cameraShift": "Subtle zoom-in then settle.",
      "spaceShift": "Runtime chassis changes into process loop space.",
      "validationChecks": ["persistent element appears on both sides", "attention lands on observe node"]
    }
  ]
}
```

## Implementation Handoff

- Hand off scene layout to `scene-composition-director`.
- Hand off standalone HTML/D3/Anime.js render work to `html-d3-anime-video-workflow`.
- Hand off Slidev, Manim, SVG, ECharts, D3, or Three.js specifics to the owning skill.
- Keep transition planning renderer-neutral until implementation is requested.
- If implementing, verify the transition in full-speed playback and a contact sheet; contact sheets alone often miss temporal continuity failures.

## Validation

Run the bundled validator for JSON transition plans:

```powershell
uv run --script .agents/skills/scene-transition-director/scripts/validate_transition_plan.py --plan transition-plan.json --expect-transitions 4 --require-anchor "task packet" --forbid gsap
```

When the prompt gives an exact transition count, pass `--expect-transitions`. When it names a persistent element, pass `--expect-persistent-name`. When it lists exact scene IDs, pass `--expect-chain` with those IDs joined by commas.

After changing this skill, run:

```powershell
uv run --script scripts/validate-skills.py
```
