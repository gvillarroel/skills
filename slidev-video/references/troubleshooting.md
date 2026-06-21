# Slidev Video Troubleshooting

Use this reference when the recorder fails, produces blank output, or reports manifest failures.

## Server Startup

If the script times out waiting for Slidev:

- Run `npm install` in the deck.
- Confirm `npx slidev slides.md --port 3030` works from the deck directory.
- Pass `--slides <file>` when the deck entry file is not `slides.md`.
- Try `--port <number>` if another process is using the default port range.

## Playwright And Browser Launch

If Playwright cannot be imported, install it in the deck:

```powershell
npm install --save-dev playwright
```

If the configured browser channel fails, retry with the bundled browser:

```powershell
npx tsx /path/to/slidev-video/scripts/record-slidev-video.ts --deck /path/to/deck --channel none
```

## Blank Or Partial Slides

For blank screenshots or videos:

- Increase `--dwell` and `--click-dwell`.
- Increase `--transition-dwell` when a native transition is still settling.
- Check that components render at `1280x720`; pass `--width` and `--height` when the deck targets another aspect ratio.
- Remove uncached network dependencies or wait for them explicitly in deck code.
- Make chart, canvas, iframe, and video containers fixed-size before initialization.
- Run with `--headed` to observe the browser state.

## Click State Issues

If the video misses custom `$clicks` stages, pass a fallback:

```powershell
--default-clicks-for-dynamic 3
```

If slides use many expensive click states, cap exploratory runs with `--max-clicks` and remove the cap for the final recording.

Use `--require-click-change` for decks where every recorded click should visibly change the slide. Do not use it for slides that intentionally keep the same visible frame while advancing narration.

## Transition Or Timing Problems

Read `video-quality.md` for transition capture, native versus direct navigation, and MP4 start trimming.

## MP4 Conversion

The recorder always attempts WebM when video recording is enabled. MP4 requires `ffmpeg` on `PATH`.

If MP4 is missing but WebM exists:

- Run `ffmpeg -version`.
- Install or expose `ffmpeg`, then rerun.
- Deliver WebM when MP4 is not required.

## Manifest Failures

Treat these as blocking by default:

- `No visible Slidev layout`: the route did not render a slide.
- `Slide has no visible content`: the slide is likely blank, hidden, or still loading.
- `Browser console error` or `Page error`: inspect the deck code and browser console.
- `did not visibly change after recorded clicks`: the click plan may be wrong, the animation may be too slow, or the slide may not actually change.

Use `--strict-overflow` when final video quality requires failing on clipped text or horizontal layout overflow.
