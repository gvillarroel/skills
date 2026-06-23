# Slidev Video Recording Workflow

Use this reference for first-run setup and the normal validate-then-record path.

## Baseline Commands

Install recorder dependencies in the target deck, not in the skill folder:

```powershell
npm install --save-dev playwright tsx
```

Validate without recording video:

```powershell
npx tsx C:\path\to\.agents\skills\slidev-video\scripts\record-slidev-video.ts --deck C:\path\to\deck --skip-video
```

Record final video artifacts:

```powershell
npx tsx C:\path\to\.agents\skills\slidev-video\scripts\record-slidev-video.ts --deck C:\path\to\deck --out C:\path\to\projects\deck-video\artifacts\videos
```

## Requirements

- The deck must provide `@slidev/cli` through local dependencies or `npx`.
- The deck should provide `playwright` and `tsx` as dev dependencies.
- `ffmpeg` is optional but required for MP4 conversion and contact sheet generation.
- Use the bundled recorder for unattended MP4/WebM. Slidev's official export path covers PDF, PPTX, PNG, and Markdown, while Slidev browser recording is interactive.

## Output Layout

The output directory contains:

- `recording-manifest.json`: slide plan, clicked states, screenshots, video paths, warnings, and failures.
- `slides/slide-001.png`: one final-state screenshot per recorded slide.
- `slide-contact-sheet.png`: tiled screenshot review image when `ffmpeg` is available.
- `<deck-name>.webm`: raw Playwright browser recording.
- `<deck-name>.mp4`: H.264 conversion when `ffmpeg` is available. The MP4 trims browser load lead-in by default.

## Default Recording Behavior

- Use `1280x720` viewport and video dimensions unless the deck targets another aspect ratio.
- Use native Slidev navigation between contiguous slides so configured deck transitions are recorded.
- Detect standard `<v-clicks>`, `<v-click>`, and `v-click` click states from `slides.md`.
- Write a manifest and screenshots even when `--skip-video` is used.
- Prefer MP4 as the delivery artifact when available; keep WebM as the raw capture or fallback.
