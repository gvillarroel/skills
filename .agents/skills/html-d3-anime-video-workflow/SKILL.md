---
name: html-d3-anime-video-workflow
description: Improve and run end-to-end video production workflows built from HTML, D3-generated SVG, Anime.js preview choreography, Playwright frame capture, and ffmpeg encoding. Use when Codex needs to create, polish, validate, or iterate on multi-video concept explainers, timestamp-driven web animation videos, research-backed scripted videos, or reusable production pipelines for this stack, while routing component-specific work to the existing D3, Anime.js, Slidev, SVG, and video skills instead of duplicating them.
---

# HTML D3 Anime Video Workflow

## Core Workflow

1. Route component work to the existing skill that owns it:
   - Use `d3-animated-svg` for D3 visualization form selection, deterministic SVG geometry, labels, token colors, and D3 gallery patterns.
   - Use `slidev-animejs` for Anime.js lifecycle, scoped selectors, cleanup, SVG helpers, text helpers, and Slidev click states.
   - Use `slidev-video` for Slidev deck recording, native navigation, MP4/WebM export, manifests, screenshots, and start trimming.
   - Use `slidev-quality-audit` for Slidev visual QA.
   - Use `animated-svg-to-gif` for GIF conversion from animated SVG assets.
   - Use `manim-svg-video` when the job is composing many existing SVG assets into a Manim-rendered MP4.
2. Use this skill only for the orchestration layer that those skills do not own: research-backed script refresh, multi-video planning, timestamp-driven HTML renderers, frame capture, ffmpeg encoding, repeated critique passes, manifests, and production notes.
3. When the user requests an artifact, write the exact requested output path. Do not substitute a descriptive filename, put the content only in chat, or write into the copied skill directory during isolated validation.
4. Apply the two production principles before writing scenes:
   - Show mechanics visually. Express each concept through cause/effect motion, state changes, flows, ranking, accumulation, branching, blocking, or feedback loops.
   - Default to zero visible explanatory text for narrated explainers. Assume narration carries names, definitions, and caveats; the video should carry diagrams, motion, and state changes.
   - Graph only the concept. Do not add video duration, progress bars, chapter rails, timestamps, watermarks, status widgets, or decorative UI chrome unless those elements are the thing being explained.
   - For tokenization scenes, render text as data-owned token groups from the first frame. Reveal a token group's own fill, border, numeric state, and destination instead of drawing boxes over an independent text node.
5. Before choosing D3 examples, reusing previous scenes, or coding a beat, design the visual metaphor. Write the concept claim, the causal mechanic, two or three candidate metaphors, the rejected alternatives, the chosen visual vocabulary, and the exact repeated roles for shapes, colors, motion, and layout. Reuse an old visual pattern only when it preserves the same semantic role.
6. Read `references/visual-metaphor-design.md` when designing a new concept video, redesigning a weak beat, or responding to feedback that a scene feels generic, copied, decorative, or text-dependent.
7. Read `references/scene-pattern-recipes.md` when reusing an approved scene pattern, extracting a shared visual component, or preserving a good example from `.agents/skills/html-d3-anime-video-workflow/assets/examples/ai-concept-videos`.
8. Before coding each beat, run a visual decision pass: identify the mechanism, the chosen shape metaphor, the visible data states, the elements omitted because narration carries them, and the existing D3/gallery/component example to adapt after the metaphor is chosen.
9. Define layout regions before drawing. Use explicit rows, columns, quadrants, shared baselines, and shared scale targets so related objects line up and keep consistent visual weight across a beat.
10. Split long videos into modules as soon as a block is approved or substantial: one orchestration entry point, shared data/palette/layout helpers, and separate files for beats or subscenes. Do not let one renderer file accumulate the full video.
11. When a user explicitly approves a video iteration, update this skill or the owning component skill with the transferable lesson before moving to the next beat.
12. Read `references/html-video-orchestration-patterns.md` when the request resembles a broader video workflow such as product/site source material, arbitrary text explainers, PR/code-change videos, short motion graphics, music-driven edits, captions, existing footage overlays, or multi-frame generated compositions.
13. Read `references/production-loop.md` before creating or improving a standalone HTML+D3+Anime.js video pipeline.
14. Read `references/routing.md` when the request overlaps another video, SVG, Slidev, D3, or Anime.js skill and the ownership boundary is unclear.
15. Keep one structured source of truth for video data: concepts, scenes, timings, references, metrics, color tokens, and output IDs.
16. Prefer deterministic timestamp rendering for final capture. Anime.js can enhance live preview, but final export should be reproducible from `renderFrame(conceptId, seconds)`.
17. Render drafts quickly, but never treat low-frame-rate drafts as final. Use 6 fps only for iteration; use at least 30 fps for final delivery, and consider 60 fps for subtle motion.
18. Validate in layers: content schema, browser smoke, draft render, automated MP4 review, visual contact-sheet critique, final render, final full review.

## Plan Artifact Tasks

When the task is to produce a Markdown plan, manifest, storyboard, production notes, or review file:

1. Read only the references needed for the requested source type and deliverable.
2. Write the requested file path in the workspace root or user-specified project directory before composing a final chat response.
3. Use the exact filename from the prompt, such as `production-plan.md`; do not rename it to `plan.md`, `implementation-plan.md`, or a project-specific default.
4. Preserve the user's source facts in the artifact. Include literal titles, identifiers, constants, event names, file names, durations, and named constraints from the prompt when they are part of the requested source package or plan.
5. Do not leave placeholders for facts the prompt already provides. A table cell like `_[exact title]_` is a validation failure when the title was supplied.
6. For PR/code-change plan artifacts, make the first section a filled `Source Facts` table copied from the prompt or source package. It must include exact PR title/summary, change size, behavior, filenames, constants, events, audience, style, and duration whenever supplied.
7. Verify the file exists, is non-empty, and contains the task's required literal anchors before final response.
8. Keep the final chat response brief and point to the created file.

## Non-Duplication Rules

- Do not copy D3 chart taxonomy, Anime.js API examples, Slidev recording options, or animated SVG conversion details into this skill. Link to the owning skill and load it when needed.
- Store workflow lessons here only when they affect the cross-stack production process.
- If a lesson is specific to D3 SVG extraction, Anime.js lifecycle, Slidev recording, or GIF encoding, update that owning skill instead of adding it here.

## Pattern Promotion

When an approved scene, shared helper, render preset, storyboard gate, production loop, or validation routine proves reusable, update `references/scene-pattern-recipes.md`, `references/visual-metaphor-design.md`, or `references/production-loop.md` before finishing. If the pattern is component-local, update the owning component skill instead. Include trigger, visual metaphor, data/timing contract, implementation steps, validation command, and isolated-workspace caveats when relevant.

## Validation

After changing this skill, run:

```powershell
uv run --script scripts/validate-skills.py
```

When changing a referenced example pipeline, also run its content validator, a browser smoke test, one representative render, and the final MP4 review script for the affected output set.
