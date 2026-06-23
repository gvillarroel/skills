# Slidev Video Recorder Options

Use this reference when tuning recorder flags or adapting the command to a specific deck.

## Path And Output

- `--deck <dir>`: target deck directory. Defaults to the current directory.
- `--slides <file>`: Markdown entry file. Defaults to `<deck>/slides.md`.
- `--out <dir>`: artifact directory. Defaults to `output/slidev-video/<deck-name>` under the current directory.
- `--name <name>`: base filename for WebM and MP4.

## Viewport And Timing

- `--width <px>` and `--height <px>`: viewport and video dimensions. Defaults to `1280x720`.
- `--dwell <ms>`: wait after opening each slide. Defaults to `800`.
- `--click-dwell <ms>`: wait after each click. Defaults to `900`.
- `--transition-dwell <ms>`: wait after native slide transitions before inspecting the next slide. Defaults to `700`.
- `--timeout <ms>`: server, navigation, and readiness timeout. Defaults to `30000`.

## Navigation And Clicks

- `--navigation native`: preserve transitions between contiguous slides. This is the default for final videos.
- `--navigation direct`: jump by route. Use for debugging, isolated slides, or non-contiguous checks.
- `--direct-jumps`: alias for `--navigation direct`.
- `--range <spec>`: record selected slides, for example `1,4-6,10`.
- `--default-clicks-for-dynamic <n>`: fallback click count for slides that reference `$clicks` without detectable click markup.
- `--max-clicks <n>`: cap clicks per slide for exploratory runs.
- `--require-click-change`: fail when a slide with recorded clicks does not visibly change between states.

## Video Format

- `--skip-video`: run traversal, screenshots, contact sheet, and manifest without video capture.
- `--webm-only`: skip MP4 conversion.
- `--no-webm`: remove WebM after successful MP4 conversion.
- `--trim-start <auto|none|ms>`: trim the browser load lead-in from the MP4. Defaults to `auto`.
- `--no-trim-start`: alias for `--trim-start none`.

## Browser And Strictness

- `--channel <name>`: preferred Chromium channel such as `msedge` or `chrome`.
- `--channel none`: use Playwright's bundled browser.
- `--headed`: launch a visible browser for debugging.
- `--strict-overflow`: fail on detected text or horizontal overflow.
- `--no-strict`: report failures without setting a failing exit code.
