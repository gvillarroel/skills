# Production Loop

Use this reference for standalone HTML+D3+Anime.js video pipelines that are not Slidev decks.

## 1. Refresh Script Claims

- Recheck current facts before visual production when the script mentions products, pricing, plan limits, model support, security guidance, standards, or recent capabilities.
- Prefer primary sources and record the exact check date in production notes.
- Keep unstable claims conservative in the rendered video. Put exact live pricing or plan limits in notes unless the user explicitly asks for them on-screen.

## 2. Design The Visual Metaphor Before Reuse

- Start with the concept's causal mechanic, not with the last successful scene or the nearest gallery component.
- For broader video requests, read `html-video-orchestration-patterns.md` before the metaphor pass so the source package, storyboard contract, media plan, and validation gates are clear before scene code begins.
- Read `visual-metaphor-design.md` for new concept videos, weak beats, or feedback that the video copied an old pattern without explaining the new idea.
- Read `scene-pattern-recipes.md` after a metaphor is chosen and before reusing an approved scene, shared helper, or example module.
- Generate multiple candidate metaphors and reject the weaker ones before writing scene code.
- Define a local visual vocabulary: which shapes are nouns, which motions are verbs, and which colors or state changes are adjectives.
- Reuse a previous scene pattern only when the repeated marks keep the same semantic role. Reuse helpers freely, but do not reuse a matrix, meter, loop, or machine box as a generic placeholder.
- Reuse a previous motion pattern only when the motion keeps the same semantic role. If a repeated sweep, pulse, cursor, or ambient layer exists only to avoid a static frame, replace it with each scene's own visual verb.
- The selected metaphor should let a viewer infer the mechanic with narration muted. If it cannot, improve the metaphor before adding labels or legends.

## 3. Storyboard Mechanisms Before Text

- Start each beat with the visible mechanism: what enters, splits, moves, stacks, ranks, branches, blocks, transforms, repeats, or exits.
- For narrated explainers, render no visible explanatory text by default. Avoid titles, bullets, labels, captions, legends, and callouts unless the user explicitly asks for on-screen words.
- Do not add progress, duration, timeline, chapter, watermark, or status components to the rendered frame unless they are part of the concept model itself.
- For every scene, identify the simultaneous animation systems that will carry meaning, such as moving tokens, changing ranks, growing meters, trace lines, highlights, feedback loops, or state transitions.
- During review, flag any frame where reading text is required or where text appears as a crutch. Replace it with motion, geometry, color, ordering, or cause/effect sequencing.

Before coding a beat, answer or ask concise visual preference questions:

- What mechanism must the viewer see: splitting, ranking, sampling, routing, accumulation, capacity, or transformation?
- What shape metaphor should carry the idea: matrix, wheel, queue, stack, network, path, meter, grid, or layered machine?
- What can narration say so the frame can omit it?
- Which on-screen words are data or unavoidable labels, and which are explanatory text that should be removed?
- Which existing D3/gallery/example component can express the chosen metaphor after it is selected?
- What must the first and last frame match if this beat touches an adjacent approved segment?

For layout and motion:

- Define layout regions first, such as full-height rows, horizontal columns, or quadrants. Then scale objects to those regions instead of placing unrelated coordinates by hand.
- Keep peer objects on shared baselines with matching visual weight when the scene compares or connects them.
- For silent diagram videos that need on-screen labels, render scene titles and critical SVG labels in a top text layer after mechanisms, and use a `paint-order: stroke` halo or equivalent so rays, routes, particles, and compression cannot make them unreadable. Inspect full-size frames where moving marks cross labels.
- Bind label and callout opacity to the mechanism they name. A route, conversion, or output label should not become fully visible before the route, conversion, or output itself is visible.
- Treat approved recurring marks as visual-language components, not redraw suggestions. When a model box, matrix, roulette, meter, or other semantic object is approved and will appear in another beat, extract it into a shared helper before the next segment render. Remove local variants that change geometry, color, internal placement, or activation style unless the semantic role intentionally changes.
- Prefer direct mechanical paths over decorative curves. If a guide line accompanies a moving object, make the line share the same source, target, timing, and fade as the object.
- Avoid persistent motion trails when the moving object already explains the transformation. A trail must be a semantic mark, not residue; if it survives arrival or shows up as a visible streak in contact sheets, remove it or fade it to zero before landing.
- For multi-scene composition tests, vary D3 structures by scene job and keep continuity through palette, typography, spacing, token identity, and named motion verbs. Use network routing, branch splitting, bar filling, radial completion, or another scene-local mechanism instead of a shared decorative background layer.
- When a model or processor box becomes active, animate the internal mechanism instead of adding a generic glow. For neural-network metaphors, adapt an existing D3 MLP activation pattern: keep the primary label centered, keep the network small and secondary, pulse nodes and links by layer, and use a soft translucent brand color so activation reads as work without competing with the main concept.
- For model-as-enclosure scenes, draw flow objects that enter or exit the model on a lower layer than the model box, border, label, and internal activation. The enclosing box should hide tokens while they are inside it, so output appears from the model boundary rather than floating over the box. Inspect full-size frames, not only contact sheets, for z-order leaks.
- Keep exact numeric readouts, prices, or cost totals in fixed secondary panels aligned to their reference table. Let meters, ticks, and accumulated marks carry the mechanic; avoid attaching precise numbers to moving dots or tokens unless the number itself is the object being tracked.
- Keep legends compact and inside the semantic region of the mark they explain. Avoid adding a legend when color or order can explain the state directly.
- For repeated loops, make the same data object visibly re-enter the system and append to the accumulated state. Add a short pulse on the newly occupied state cell after append; this often explains growth more clearly than a label.
- In probability or ranking scenes, show relative magnitude with bars, wedges, ordering, or area before showing numbers. Remove percentages when narration can explain probability and the visual ordering is unambiguous.

For tokenizer or context-window scenes:

- Render prompt text as token-owned groups from the first frame. Each token group owns its text node, invisible or low-emphasis rectangle, and later visual states. Do not draw rectangles over a separate sentence; text measurement and glyph overhangs will drift.
- Use explicit inter-token spacing and measured token widths. Do not rely on trailing spaces in SVG text for token boundaries.
- Show the mechanical chain as token boxes -> numeric ID boxes -> colored square cells. Make each element keep identity through the transformation.
- Use a square neutral context-window matrix for capacity. Fill occupied cells left-to-right, top-to-bottom in concept order, and avoid decorative outer borders unless the border itself is part of the model.

## 4. Build One Data Model

Create one structured module for:

- video IDs and titles
- exact duration
- beat start/end times
- scene headlines, bullets, and callouts
- references and research notes
- visual metrics and palette tokens
- output filenames

For input-driven videos, create a source package first and point the data model at it. Website/product packages should freeze screenshots, visible text, brand tokens, and selected assets. PR packages should freeze metadata, files, selected diff hunks, and contributor notes. Topic explainers should keep the verbatim source text and checked facts. Music-driven pieces should keep the canonical audio map. Existing footage workflows should keep transcript, keep-out, and overlay timing data. Do not let final render code fetch or infer these facts live.

Avoid scattering script text across HTML, renderer code, and export scripts.

For long videos, keep one orchestrating entry point but split implementation by approved beat or substantial subscene. Use shared modules for palette tokens, timing helpers, token geometry, matrix geometry, and layout regions. New work should usually start in a new beat file once the previous beat is approved, so late-video iteration does not require editing one oversized renderer.

## 5. Use Deterministic Timestamp Rendering

For final export, expose a browser callable function similar to:

```js
window.renderConceptFrame = (conceptId, seconds, options = {}) => {
  // update DOM text
  // redraw D3 SVG from the current timestamp
  // return a small validation state
}
```

Make the rendered frame depend on `conceptId` and `seconds`, not wall-clock animation state. This makes rerenders, reviews, and individual frame debugging repeatable.

Use Anime.js for live preview cues, authoring ergonomics, or interaction demos. Do not make final capture depend on Anime.js timers unless the export script can seek them deterministically.

Build each beat's static hero frame before adding motion. Verify fixed canvas dimensions, resolved container heights, safe padding, wrapping, and peak clearance for pulsing or overshooting elements. Then animate from or through that known-good layout with transforms, opacity, color, and deterministic redraws.

## 6. Serve HTML Over Local HTTP

Do not rely on `file://` for ES modules. Chromium blocks module loading from `file://` in common capture paths. Use a local static server inside the export script or run an explicit local preview server.

For export scripts:

- bind to `127.0.0.1`
- choose an available port automatically when possible
- serve only the intended deck or example root
- close the server in a `finally` block

## 7. Capture Frames, Then Encode

For deterministic standalone web videos:

1. Launch Chromium with the target viewport.
2. Load the local HTTP URL.
3. Wait for fonts and initial network idle.
4. For each frame, call `renderConceptFrame(id, frame / fps, { capture: true })`.
5. Capture a PNG screenshot.
6. Encode numbered frames with ffmpeg to H.264 MP4.
7. Generate contact sheets from the MP4, not from raw frames.

Keep raw frames only while diagnosing. Delete them by default to avoid large transient output.

For final quality:

- Use at least 30 fps. Use 6 fps only for drafts and contact-sheet iteration.
- Use CRF 16-18 for H.264 diagram videos unless file size is the primary constraint.
- Supersample raster captures when practical, such as Chromium `deviceScaleFactor: 2`, then downscale with Lanczos during encoding.
- Encode diagram-heavy motion with a slow preset and animation tuning when ffmpeg supports it.
- Check the final MP4 at normal playback speed, not only contact sheets; contact sheets hide temporal stutter.

For faster iteration, expose explicit render tiers instead of making every preview pay final-render cost:

- `quick`: 6 fps, CRF 24, device scale 1, veryfast encoding, no contact sheet. Use only for storyboard timing and rough layout.
- `draft`: 12 fps, CRF 24, device scale 1, veryfast encoding, no contact sheet. Use for most visual-shape iterations before judging smoothness.
- `motion`: 30 fps, CRF 20, device scale 1, faster encoding, contact sheet enabled. Use when the animation timing or stutter is the thing being reviewed.
- `fast`: 30 fps, CRF 16, device scale 2, veryfast encoding, no contact sheet. Use when the user needs a near-final-looking segment without paying for slow encoding or review artifacts.
- `final`: 30 fps, CRF 16, device scale 2, slow encoding, contact sheet enabled. Use for approved segments and deliverables.

Prefer rendering only the changed time range with `--start` and `--duration`. Render full videos only for continuity checks, final review, or when a change touches shared helpers across multiple beats.

When using npm scripts with extra renderer flags in PowerShell, pass a double separator so npm does not consume option names:

```powershell
npm run render:fast -- -- --concept 01-what-is-an-llm --start 36 --duration 30
```

Calling the renderer directly is also valid for segment work:

```powershell
node projects/ai-concept-videos/scripts/render-videos.mjs --preset fast --concept 01-what-is-an-llm --start 36 --duration 30
```

For separately rendered or separately authored segments, lock continuity at boundaries. Render both adjacent segments with raw frames kept, then compare the previous segment's last intended frame (`duration * fps - 1`) against the next segment's first frame by hash or pixel diff. Treat a mismatch as a visual bug unless the cut is intentionally visible.

## 8. Review In Three Passes

Apply at least three concrete improvement passes before final delivery:

- Pass 1: source, metaphor, and storyboard. Verify references, simplify claims, align the data model, decide the visual metaphor, and ensure every video has the expected beat structure.
- Pass 2: coordinated animation. Add at least two simultaneous animation systems per concept, such as D3 visual motion, metric updates, beat progress, token/packet movement, or HTML panel reveals.
- Pass 3: visual QA polish. Review contact sheets, fix text fit, balance palette use, remove clutter, and verify the output does not read as static.

Record the passes in production notes with one row per video.

For videos with planned transitions, add transition midpoint screenshots to the smoke or review pass. Contact sheets sampled every few seconds can miss a cut that violates its transition contract, such as a planned zoom, portal, or morph that renders only as a generic pulse.

## 9. Automated Review Gate

Use `ffprobe` and `ffmpeg` checks before delivery:

- duration within tolerance
- expected resolution
- expected frame count or frame rate
- black frame detection
- freeze detection with a threshold that does not false-positive on small UI motion
- contact sheet generation

Treat failures as blocking unless the user explicitly accepts them.

Scale validation to the source and route. For input-driven videos, also verify the source package exists and that unstable claims have checked dates. For multi-beat videos, verify the storyboard tiles the duration and every beat has a visible mechanism. For motion-heavy work, review key timestamps for expected state changes before paying for a final render. If freeze detection fails, first add or extend semantic scene-local motion such as a packet route, branch lane fill, chart cursor, or checklist orbit. Do not solve it with a global repeated sweep unless that sweep is the subject of the video.

Make review artifacts honest. Choose contact-sheet tile geometry that matches the number of sampled frames, or compose sheets with a layout that cannot introduce empty black cells. Empty cells create false visual defects and can hide whether the last sampled frames were actually generated. Regenerate contact sheets after the final render, not only after a draft.

Inspect full-size keyframes for every shared lower-third, rail, watermark, recurring packet, or reusable symbol. Contact sheets can hide collisions between small repeated labels and scene-specific chips. When a shared symbol overlaps local scene text, remove the duplicate label or move the symbol; do not shrink critical text to make decorative continuity fit.

## 10. Output Layout

Use `projects/<project-id>/artifacts/` for generated artifacts:

```text
projects/<project-id>/
  scripts/
  source/
  artifacts/
    documents/
    svgs/
    gifs/
    images/
    data/
    manifests/
    video-renders/
      final/
        videos/
        review/
        render-manifest.json
        production-notes.md
      draft-pass/
      smoke/
    videos/
    screenshots/
    reviews/
```

For the AI concept video project, the default renderer layout is:

```text
projects/ai-concept-videos/artifacts/video-renders/
  final/
    videos/
    review/
    render-manifest.json
    production-notes.md
  draft-pass/
  smoke/
```

Keep reusable example source under the owning skill's `assets/examples/<project>/` directory, project-specific automation under `projects/<project-id>/scripts/`, and generated documents, videos, SVGs, GIFs, screenshots, manifests, review output, and data under `projects/<project-id>/artifacts/`.
