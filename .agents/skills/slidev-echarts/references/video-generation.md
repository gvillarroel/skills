# Automated Slidev ECharts Video Generation

Use this workflow when the user asks for a video, MP4, WebM, automatic recording, motion review, or slide-by-slide animation validation.

## Recorder Contract

Prefer a deterministic Playwright recorder over manual screen capture.

1. Add a deck-local script such as `scripts/record-video.mjs`.
2. Start the Slidev dev server from the script on an available local port.
3. Open the deck with Playwright at a fixed viewport, usually `1280x720`.
4. Record the browser context with `recordVideo`.
5. Visit every slide, start at `clicks=0`, then advance the slide's available click states with `ArrowRight`.
6. Wait long enough after each click for ECharts `animationDurationUpdate` to finish.
7. Capture final screenshots for every slide.
8. Write a JSON manifest with slide count, recorded state count, chart surface counts, chart hashes, console errors, page errors, and verification failures.
9. Convert the recorded WebM to H.264 MP4 with ffmpeg when ffmpeg is available.

Use `embedded=true` in the URL to reduce Slidev UI chrome during capture.

## Dependencies

Use deck-local dependencies so the recorder is reproducible:

```powershell
npm install --save-dev playwright
```

Check for ffmpeg before promising MP4:

```powershell
ffmpeg -version
```

If ffmpeg is unavailable, deliver the WebM and document that MP4 conversion was skipped.

## Slide And Click Plan

Avoid hard-coding only a few showcase slides when the user asks to review the deck. Parse `slides.md` or maintain a small declarative plan that includes every slide.

For Markdown-driven decks, count list items inside each `<v-clicks>` block and drive exactly that many clicks. If the parser cannot determine click count safely, use a conservative scene plan checked into the example project.

For each slide, record:

- slide number and title
- expected chart count
- available and recorded clicks
- initial and final chart surface hashes
- nonblank chart surface count
- screenshot path
- console and page errors

Fail the run when an expected chart surface is missing, blank, unchanged after click-driven animation, or the browser reports app errors.

## Composition Guidance

For video-focused Slidev ECharts decks, include more than one layout pattern:

- **Narrative build:** one chart plus copy and click-driven stage labels.
- **Dashboard:** several chart instances with synchronized state changes.
- **Spotlight:** one large chart with overlay metrics or callouts.
- **Comparison:** two charts side by side, updated from the same `$clicks` state.
- **Reference catalog:** one chart type per slide when the goal is skill validation.

Keep each composition useful as a final still frame. The recorder should pause after the final click so labels, axes, and overlays settle before advancing.

## Output Locations

Keep video artifacts outside skill directories:

```text
output/slidev-echarts/video/
  slidev-echarts-auto.mp4
  slidev-echarts-auto.webm
  recording-manifest.json
  slide-contact-sheet.png
  slides/
    slide-001.png
```

Do not commit generated videos or screenshots unless the repository explicitly treats `output/` artifacts as keepable validation evidence.

## Example Deck Commands

The validation deck in `.agents/skills/slidev-echarts/assets/examples/slidev-echarts/` exposes:

```powershell
npm run verify:video
npm run video
```

`npm run verify:video` traverses every slide and writes verification artifacts without producing a video. `npm run video` performs the same traversal, records WebM, converts MP4 with ffmpeg, and writes the same manifest.
