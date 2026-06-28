# HTML Video Orchestration Patterns

Use this reference when a standalone HTML+D3+Anime.js video request resembles a broader video-production workflow: product or website source material, arbitrary text explainers, PR/code-change videos, short motion graphics, music-driven edits, captions, or multi-frame generated compositions.

These are distilled workflow patterns, not a dependency on HyperFrames or any external skill. Translate them into this repository's stack: structured data modules, deterministic timestamp rendering, Playwright screenshots, ffmpeg encoding, contact sheets, and project artifacts under `projects/<project-id>/artifacts/`.

## 1. Route By Input And Deliverable

Classify the request before choosing visuals:

| Input or goal | Local handling |
| --- | --- |
| Standalone HTML animation, concept explainer, or generated diagram video | Use this skill, then load D3/Anime/SVG skills only for component-local details. |
| Slide deck, presentation, or native Slidev transition capture | Route to the Slidev skills. |
| Existing SVG assets composed into a video | Route to `manim-svg-video` unless the task needs a custom browser renderer. |
| Website or product URL used as source material | Build a source package from screenshots, visible text, brand tokens, and selected assets before storyboarding. |
| Arbitrary article, notes, or topic | Use a no-capture source package: raw text plus optional user-provided brand tokens; invent visuals downstream. |
| GitHub PR or code change | Build an offline source package from PR metadata, file list, selected diff hunks, and contributor metadata; do not treat it as website capture. |
| Music track drives the video | Analyze the track once into deterministic timing data and let phrases, beats, energy, and hard stops drive frame boundaries. |
| Existing footage with subtitles or overlays | Treat footage as source media; do not alter timing or content unless the user explicitly asks for editing. |
| Short unnarrated motion-first piece | Keep the plan compact: one shot, one source/asset strategy, one render, one verification pass. |

If the route is unclear, identify the missing source type or output type first. Duration, aspect ratio, and narration style are defaults unless they change the route.

## 2. Create A Source Package Before Story

Turn the user's input into a stable project-local source package before writing storyboard beats. The package prevents live fetches during render and gives every later step the same facts.

Preserve literal anchors from the input. Product names, PR titles, event names, constants, filenames, metric labels, timestamps, and user-supplied durations are not optional examples; they are source facts. Carry them into the source package and into any requested plan or storyboard so the output proves it is about this task rather than a generic pipeline.

Recommended shape:

```text
projects/<project-id>/
  source/
    input.txt | pr.json | website-notes.md | audiomap.json
    research-notes.md
    brand-tokens.json
    asset-ledger.json
    screenshots/
    media/
```

Use the smallest package that fits the source:

- **Website/product:** screenshots, visible text, computed colors/fonts, selected image/video/icon assets, and notes about what was skipped.
- **PR/code:** title, author, additions/deletions, changed files, selected diff hunks, release/change summary, and optional contributor avatars.
- **Topic/article:** verbatim source text, checked facts with dates, any user-provided brand constraints, and no fake asset inventory.
- **Music:** canonical audio path, duration, phrases, onsets, energy regions, hard stops, and whether the beat grid is reliable.
- **Existing footage:** source media path, transcript/word timings when available, graphic keep-out regions, and whether footage timing is locked.

Do not fetch network resources, query current facts, or derive layout from live browser state during final frame capture. Research and capture happen before the renderer.

### PR/code-change plan starter

When producing a plan for a PR or code change, start the artifact with a source facts table before any generic pipeline sections:

| Field | Copy from input |
| --- | --- |
| PR title | Exact title or summary string |
| Change size | Exact file count and additions/deletions if supplied |
| Behavior | Exact behavior change in one sentence |
| Files | Exact filenames and their roles |
| Constants/events/API names | Exact literal identifiers such as config keys, event names, function names, or test names |
| Audience/style | Exact requested audience, narration, music, caption, and visual constraints |

Then build the storyboard from those facts. Do not write a generic "PR video pipeline" that could apply to any pull request.

If the input supplies a value, fill the table with that value. Do not leave placeholders such as `_[exact title]_`, `TBD`, or `replace later` for PR title, constants, event names, filenames, duration, audience, or style constraints that are already present in the prompt.

## 3. Make The Storyboard The Build Contract

Create one structured storyboard or data module before HTML:

- global format, audience, message, duration, aspect, source package path, and output IDs
- one beat/frame record per visual unit
- beat start/end or duration
- the visible mechanism, not just a title
- narration or audio cue, if any
- source assets or source facts used by the beat
- transition intent
- validation cues, such as poster time, key moment, or expected visible state

For multi-scene work, approve or lock the storyboard before building. For small edits or one-shot motion graphics, the contract can be a compact JSON object or a short note, but it should still name the source, duration, visual mechanic, and validation target.

Do not let the HTML become the first place where story, timing, assets, and claims are decided.

## 4. Design Static Layout Before Motion

For every beat, build the most visible frame first:

- define fixed canvas dimensions and resolved container heights
- use rows, columns, grids, quadrants, safe padding, and max widths before absolute coordinates
- place every object in its final readable position
- verify text wraps inside its container at the target viewport
- reserve peak clearance for elements that scale, pulse, blur, or overshoot
- only then add entrance, exit, or camera motion

The renderer should animate from or through a known-good layout. If a scene is positioned from hidden/offscreen start states before the final frame is inspected, overlaps and clipping stay invisible until late review.

## 5. Keep Final Rendering Seek-Deterministic

Final capture must be a pure function of video ID and timestamp.

Use:

- `renderFrame(videoId, seconds, options)` or an equivalent deterministic entry point
- seeded pseudo-randomness for natural-looking placement
- precomputed data and media paths
- transform/opacity/color changes over layout-affecting animation when possible
- finite loops bounded by the clip duration

Avoid:

- `Date.now()`, `performance.now()`, `requestAnimationFrame`, or runtime timers for visual state
- unseeded `Math.random()`
- required network fetches
- hover, focus, scroll, or pointer state
- infinite animation loops in final render paths
- animating `display`, `visibility`, `top`, `left`, width, or height when transform-based motion can express the same change

Live Anime.js previews are fine for authoring, but the exported frames should be reproducible by timestamp.

## 6. Compose Motion From Named Verbs

Before coding motion, assign each meaningful element a verb: enter, split, route, append, rank, sample, count, fill, lock, pulse, sweep, reveal, block, merge, or exit.

Use two to four motion systems per substantial beat, such as:

- a primary object transformation
- a secondary metric, meter, or state update
- a camera or viewport move
- a transition handoff
- a subtle ambient layer tied to the scene's concept

Avoid a scene where every element simply fades or slides in with the same easing. For adjacent beats, make exits and entries feel intentional: hard cut for rapid lists, velocity-matched blur/position handoff for continuous motion, or a larger transition for the main reveal.

## 7. Treat Video Composition Differently From Web UI

A brand spec defines identity, not the whole frame layout. Adapt the brand to video scale:

- use background, midground, and foreground layers
- include structural details such as rules, marks, small metadata, dividers, or data bars when they carry the frame language
- keep type, borders, spacing, and accent color strong enough to survive video compression
- prefer edge-anchored or split-frame layouts over centered web-page stacks
- give the eye at least two intentional focal points in dense scenes
- avoid flat single-color frames unless emptiness is the concept

Do not add decorative chrome that conflicts with this skill's core rule to graph only the concept. Foreground detail should support the video language or source material, not become generic UI.

## 8. Separate Audio, Captions, And Media From Scene Code

Use one manifest for generated or resolved media:

- voice/audio file paths
- word timings
- BGM/SFX paths and offsets
- captions or lyric groups
- source provenance and fallback notes

Mount media from the manifest in the renderer. Do not scatter hard-coded audio paths, word timings, and SFX offsets across scene files. Existing footage should remain untouched unless the request is explicitly an edit; overlays and captions align to transcript time.

## 9. Split Work By Beat After The Contract Is Stable

For longer videos, keep one orchestration entry point and one shared data layer. Split implementation by beat or approved segment:

- each beat module reads the shared source/story data and timestamp
- shared helpers own palette, typography, token geometry, model boxes, metrics, and layout regions
- beat modules do not mutate the storyboard or source package
- assembled render order is deterministic

This keeps late feedback local and avoids one renderer file accumulating unrelated visual systems.

## 10. Validate In Gates

Run the cheapest useful gate as soon as each layer exists:

1. **Source/package gate:** required input files exist; current claims have checked dates when needed.
2. **Storyboard gate:** beats tile the duration; every beat has a mechanism, source facts, and validation cue.
3. **Static layout gate:** hero frames render without overlap or clipping before motion is added.
4. **Browser smoke gate:** local HTTP load, fonts ready, no console errors, nonblank frame.
5. **Motion gate:** key timestamps show expected state changes; no wall-clock-only animation.
6. **Draft render gate:** short range or cheap preset for timing and shape.
7. **Automated media gate:** `ffprobe`, duration, frame count, resolution, black/freeze checks.
8. **Visual review gate:** contact sheet plus normal-speed playback.
9. **Final gate:** final preset render, manifest, and explicit note of anything not verified.

If a gate fails, fix the earliest layer that explains the failure. Do not hide a sync or layout issue by changing duration, dropping frames, or cropping the problem away.
