# Production Loop

Use this reference for standalone HTML+D3+Anime.js video pipelines that are not Slidev decks.

## 1. Refresh Script Claims

- Recheck current facts before visual production when the script mentions products, pricing, plan limits, model support, security guidance, standards, or recent capabilities.
- Prefer primary sources and record the exact check date in production notes.
- Keep unstable claims conservative in the rendered video. Put exact live pricing or plan limits in notes unless the user explicitly asks for them on-screen.

## 2. Storyboard Mechanisms Before Text

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
- Which existing D3/gallery/example component is closest to the needed motion before building a custom version?
- What must the first and last frame match if this beat touches an adjacent approved segment?

For layout and motion:

- Define layout regions first, such as full-height rows, horizontal columns, or quadrants. Then scale objects to those regions instead of placing unrelated coordinates by hand.
- Keep peer objects on shared baselines with matching visual weight when the scene compares or connects them.
- Prefer direct mechanical paths over decorative curves. If a guide line accompanies a moving object, make the line share the same source, target, timing, and fade as the object.
- Keep legends compact and inside the semantic region of the mark they explain. Avoid adding a legend when color or order can explain the state directly.
- For repeated loops, make the same data object visibly re-enter the system and append to the accumulated state. Add a short pulse on the newly occupied state cell after append; this often explains growth more clearly than a label.
- In probability or ranking scenes, show relative magnitude with bars, wedges, ordering, or area before showing numbers. Remove percentages when narration can explain probability and the visual ordering is unambiguous.

For tokenizer or context-window scenes:

- Render prompt text as token-owned groups from the first frame. Each token group owns its text node, invisible or low-emphasis rectangle, and later visual states. Do not draw rectangles over a separate sentence; text measurement and glyph overhangs will drift.
- Use explicit inter-token spacing and measured token widths. Do not rely on trailing spaces in SVG text for token boundaries.
- Show the mechanical chain as token boxes -> numeric ID boxes -> colored square cells. Make each element keep identity through the transformation.
- Use a square neutral context-window matrix for capacity. Fill occupied cells left-to-right, top-to-bottom in concept order, and avoid decorative outer borders unless the border itself is part of the model.

## 3. Build One Data Model

Create one structured module for:

- video IDs and titles
- exact duration
- beat start/end times
- scene headlines, bullets, and callouts
- references and research notes
- visual metrics and palette tokens
- output filenames

Avoid scattering script text across HTML, renderer code, and export scripts.

For long videos, keep one orchestrating entry point but split implementation by approved beat or substantial subscene. Use shared modules for palette tokens, timing helpers, token geometry, matrix geometry, and layout regions. New work should usually start in a new beat file once the previous beat is approved, so late-video iteration does not require editing one oversized renderer.

## 4. Use Deterministic Timestamp Rendering

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

## 5. Serve HTML Over Local HTTP

Do not rely on `file://` for ES modules. Chromium blocks module loading from `file://` in common capture paths. Use a local static server inside the export script or run an explicit local preview server.

For export scripts:

- bind to `127.0.0.1`
- choose an available port automatically when possible
- serve only the intended deck or example root
- close the server in a `finally` block

## 6. Capture Frames, Then Encode

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

For separately rendered or separately authored segments, lock continuity at boundaries. Render both adjacent segments with raw frames kept, then compare the previous segment's last intended frame (`duration * fps - 1`) against the next segment's first frame by hash or pixel diff. Treat a mismatch as a visual bug unless the cut is intentionally visible.

## 7. Review In Three Passes

Apply at least three concrete improvement passes before final delivery:

- Pass 1: source and storyboard. Verify references, simplify claims, align the data model, and ensure every video has the expected beat structure.
- Pass 2: coordinated animation. Add at least two simultaneous animation systems per concept, such as D3 visual motion, metric updates, beat progress, token/packet movement, or HTML panel reveals.
- Pass 3: visual QA polish. Review contact sheets, fix text fit, balance palette use, remove clutter, and verify the output does not read as static.

Record the passes in production notes with one row per video.

## 8. Automated Review Gate

Use `ffprobe` and `ffmpeg` checks before delivery:

- duration within tolerance
- expected resolution
- expected frame count or frame rate
- black frame detection
- freeze detection with a threshold that does not false-positive on small UI motion
- contact sheet generation

Treat failures as blocking unless the user explicitly accepts them.

## 9. Output Layout

Use `output/<project>/` for generated artifacts:

```text
output/<project>/
  final/
    videos/
    review/
    render-manifest.json
    production-notes.md
  draft-pass/
  smoke/
```

Keep example source under `examples/<project>/` and generated artifacts out of skill directories.
