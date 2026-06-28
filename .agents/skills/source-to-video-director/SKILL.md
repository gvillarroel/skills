---
name: source-to-video-director
description: Create engine-agnostic video source packages, storyboards, shot contracts, and validation checklists from source material such as PRs, product notes, URLs, topic briefs, transcripts, music briefs, existing footage notes, or local assets. Use before rendering with HTML/D3/Anime.js, Slidev, Manim, CSS/WAAPI, or any other video engine when source facts must be frozen, routes chosen, and shot-level contracts written without committing to GSAP or engine-specific timelines.
---

# Source To Video Director

## Workflow

1. Route the request by source and deliverable before planning:
   - `code-change`: PR, diff, changelog, release note, commit, or code walkthrough.
   - `site-or-product`: website, landing page, product notes, app UI, feature launch, or demo.
   - `topic-explainer`: concept, research, process, technical explanation, or educational narrative.
   - `short-motion`: kinetic type, stat hit, quote, headline, lower third, poster, or unnarrated motion graphic.
   - `audio-led`: music, transcript, narration, beat sheet, or caption timing source.
   - `footage-or-assets`: existing video, screenshots, images, logos, diagrams, or local media.
2. Treat prompt tables, bullet lists, field/value blocks, and inline facts as source material. Before declaring source material missing, scan the user's prompt for supplied titles, routes, files, constants, events, durations, audience, style, audio, and output constraints.
3. Write exact requested artifact paths. Do not rename `source-package.json`, `storyboard.md`, `shot-contract.json`, or user-specified output files.
4. Freeze facts before story. If the prompt gives facts, copy the literals into the source package. If a fact is missing and no source can be inspected, mark the field `null` or add a `missingFacts` item; do not invent values.
5. Before writing artifacts, make a literal extraction checklist from the prompt. Verify every non-empty source table row and every named anchor appears in `source-package.json` or `shot-contract.json`; verify the storyboard repeats the important viewer-facing anchors.
6. Read `references/source-package.md` before creating or revising a source package.
7. Read `references/storyboard-contract.md` before creating a storyboard, shot plan, render contract, or handoff for another video skill.
8. Keep output engine-agnostic. Describe motion as semantic intent and timestamped states, not as library calls or framework code. Do not include GSAP dependencies, timeline snippets, or renderer-specific implementation unless the user explicitly asks for that renderer.
9. For implementation after the contract is approved, route to the owning renderer skill:
   - Use `html-d3-anime-video-workflow` for standalone HTML, D3, Anime.js preview, Playwright frame capture, and ffmpeg workflows.
   - Use `d3-animated-svg`, `echarts-animated-svg`, `mermaid-animated-svg`, or `threejs-animated-3d` for component visuals.
   - Use `slidev-video`, `manim-svg-video`, or `animated-svg-to-gif` for their specific export surfaces.
10. Validate the contract before handoff. Prefer `scripts/validate_video_contract.py` when JSON artifacts exist. Add one `--require-anchor` for each supplied title, identifier, filename, event, constant, behavior phrase, audience, duration, style, and audio constraint that must survive into the artifacts. If the prompt gives an exact shot count or range, pass `--expect-shots`, `--min-shots`, or `--max-shots`. Also inspect the files manually for literal source facts, missing paths, placeholder text, forbidden engine terms, and shot/story mismatch.

## Required Artifacts

When the user asks for a video plan or pre-production handoff, create:

- `source-package.json`: frozen facts, route, constraints, assets, literal anchors, omissions, and risks.
- `storyboard.md`: human-readable beat sequence with source facts and frame summaries.
- `shot-contract.json`: machine-readable shot list with timing, visual roles, motion intent, media needs, and validation anchors.

If the user asks for only one artifact, create that exact artifact and include enough internal structure that a later run can produce the others without re-reading the original source.

## Validation

After changing this skill, run:

```powershell
uv run --script scripts/validate-skills.py
```

For generated contracts, run the bundled validator when practical:

```powershell
uv run --script .agents/skills/source-to-video-director/scripts/validate_video_contract.py --source-package source-package.json --storyboard storyboard.md --shot-contract shot-contract.json --forbid gsap
```
