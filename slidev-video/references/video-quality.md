# Slidev Video Quality

Use this reference when final video polish, transitions, timing, or visual QA matter.

## Transition Quality

Keep `--navigation native` for final videos. This records configured Slidev transitions, such as `slide-left`, because the recorder advances between contiguous slides with `ArrowRight` instead of reloading each route.

Native navigation preserves transitions only between contiguous slides. A range such as `1,4-6` jumps directly from slide 1 to slide 4, then preserves transitions from 4 to 5 and 5 to 6.

If transitions feel rushed or are clipped, increase:

```powershell
--transition-dwell 1000
```

Use `--navigation direct` only when transition capture is irrelevant or direct route reset is safer for debugging.

## MP4 Start Trim

The recorder trims MP4 start lead-in automatically so the video starts on rendered slide content instead of browser loading frames.

If the MP4 starts too early or too late, tune:

```powershell
--trim-start auto
--trim-start 1200
--no-trim-start
```

The WebM remains the raw Playwright capture and may include browser load lead-in.

## Visual Review

After recording:

1. Open `recording-manifest.json` and confirm `failures` is empty.
2. Check `slideCount`, `recordedStates`, and per-slide `clicksRecorded` against the intended story.
3. Review `slide-contact-sheet.png` or final screenshots for blank slides, clipped content, wrong theme mode, missing fonts, missing media, or stale click states.
4. Play the MP4 and verify timing, native slide transitions, final state pauses, and first-frame content.
5. For charts, canvas, WebGL, videos, or remote assets, run at least one full recording after any visual fix.

## Deck Preparation

Prepare decks for deterministic video export:

- Avoid random data unless it is seeded.
- Cache or vendor remote assets when possible.
- Give media, charts, iframes, WebGL scenes, and animations stable dimensions.
- Prefer local fonts or document system font requirements.
- Use `--dwell`, `--click-dwell`, and `--transition-dwell` values that leave enough time for animations to settle.
