# <Title>

Promise:

Audience:

Format:

Runtime:

## Hook

Cold-open line:

First visual:

Audio cue:

## Timed Beat Table

Use `M:SS-M:SS` time ranges when possible, for example `0:00-0:05`.

| Time | Beat ID | Scene ID | Script purpose | Visual | Animation | Transition | Audio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0:00-0:05 | b01 | s01 | Claim or contradiction | Logo, source, UI, code, or mechanism anchor | Smash scale-in or reveal | Hard cut | Hit plus bed starts |
| 0:05-0:15 | b02 | s02 | Definition | Diagram, docs, UI, or code proof | Highlight sweep | Punch-in | Bed ducked |
| 0:15-0:25 | b03 | s03 | Mechanism step 1 | Source-bound visual | Trace or pan | Match cut | Tick or whoosh |
| 0:25-0:35 | b04 | s04 | Mechanism step 2 | Source-bound visual | State change | Hard cut | Light hit |
| 0:35-0:45 | b05 | s05 | Practical example | UI/code/output state | Build or type-on | Jump cut | Tick accents |
| 0:45-0:55 | b06 | s06 | Contrast or warning | Split screen or warning proof | Snap contrast or glitch | Smash cut | Dropout or low impact |
| 0:55-1:05 | b07 | s07 | Rule of thumb | Checklist, diagram, or code outcome | Chips or highlights | Wipe or hard cut | Bed returns |
| 1:05-1:10 | b08 | s08 | Callback | Final mechanism summary | Zoom out or resolve | Final cut | Final hit and tail |

## Visual Source Plan

- Screenshots:
- Code/UI captures:
- Diagrams/generated visuals:
- Source links: add concrete URLs or domains before using `--require-source-links`.
- Image/video assets:

## Visual Production Contract

- Stable scene/beat IDs: `s01`/`b01` through the final beat; preserve them across assets, composition, transitions, renderer state, and review evidence.
- Source package and shot contract: `source/source-package.json` and `source/shot-contract.json`; freeze fact, beat, scene, and source IDs before producing visuals.
- Asset manifest: `source/asset-manifest.json`; every asset needs provenance, rights, producer skill or fallback, final output path, technical target, beat/scene use, and quality checks.
- Composition plan: `source/composition-plan.json`; every scene needs anchors, rejected alternatives, text bounds, hierarchy, safe zones, four motion phases, reduced-motion intent, an outgoing seam, and screenshot checks.
- Transition plan: `source/transition-plan.json`; bind adjacent scenes through a persistent element, state change, attention handoff, and before/midpoint/after proof.
- Visual review: `artifacts/reviews/visual-review.json`; approve actual full-resolution frames and transition evidence after correction/rerender.
- Scaffold status: `src/index.html` is a wireframe until renderer state and visible DOM markers prove the declared asset and composition IDs.

## Animation And Transition Plan

- Visual punctuation cadence:
- Reusable motion vocabulary:
- Transition map:

## Music And SFX Plan

- Background bed:
- Voiceover ducking:
- Hits/stingers:
- Ticks/whooshes:
- Risers/dropouts:

Replace the starter voiceover lines below with concept-specific narration before validation; repeated or template-generic lines should fail `--require-voiceover`.

## Voiceover Draft

- 0:00-0:05: Open with the claim and name the consequence.
- 0:05-0:15: Define the concept in one compressed sentence.
- 0:15-0:25: Show the first mechanism step and why it matters.
- 0:25-0:35: Show the state change that makes the mechanism work.
- 0:35-0:45: Prove the practical output with a concrete example.
- 0:45-0:55: Contrast the failure path with the controlled path.
- 0:55-1:05: Give the rule of thumb viewers can reuse.
- 1:05-1:10: Callback to the hook and close on the practical rule.

## Script Style Notes

- Density:
- Joke/claim cadence:
- Setup/payoff:
- Final callback:

## Evaluation

- Hook is visible in the first 5 seconds.
- At least 8 timed beats are present.
- Every beat has script purpose, visual, animation, transition, and audio.
- A new visual idea appears every 6-10 seconds for short videos.
- Audio has bed, hits, cue timing, and ducking notes.
- Publishable audio will include a final audio report with duration coverage.
- For source-backed or publishable work, source links include concrete URLs/domains and pass `--require-source-links`.
- Final output will be validated with:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_brief.py path/to/brief.md --require-voiceover --require-source-links --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_visual_contract.py --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --video artifacts/videos/final.mp4 --brief source/brief.md --project-root . --require-ready-assets --require-specialist-routing --require-reviewed-scenes --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_style_fidelity.py --brief path/to/brief.md --pattern-blueprint path/to/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --require-source-links --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_video_readiness.py --brief path/to/brief.md --require-voiceover --require-source-links --json
```
