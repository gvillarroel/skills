---
name: slidev-video
description: Record, export, and validate Slidev decks as video artifacts. Use when Codex needs to turn any Slidev presentation into MP4 or WebM, preserve native Slidev transitions, automate slide and click traversal with Playwright, create recording manifests and screenshots, trim video startup, troubleshoot video export issues, or verify that a Slidev deck renders correctly before delivering a video.
---

# Slidev Video

## Core Workflow

1. Locate the Slidev deck root, usually the directory containing `package.json` and `slides.md`.
2. Prefer the bundled Playwright recorder over manual screen capture. Keep generated artifacts outside skill directories, typically under `output/`.
3. Start unfamiliar or high-stakes decks with a no-video validation pass, then record MP4/WebM after the manifest is clean.
4. Treat non-empty `recording-manifest.json` failures as blocking unless the user explicitly accepts them.
5. For final videos, preserve deck transitions with native navigation. Use direct route jumps only for focused debugging or non-contiguous spot checks.
6. Inspect final screenshots and the MP4. Verify nonblank slides, correct framing, expected click states, clean console/page errors, and a first frame that starts on rendered slide content.

## Resource Routing

- Read `references/recording-workflow.md` for first-run setup, baseline commands, output layout, and the normal validate-then-record sequence.
- Read `references/recorder-options.md` when tuning dimensions, ranges, click counts, browser channel, output names, MP4/WebM behavior, or script flags.
- Read `references/video-quality.md` when the task cares about polished transitions, timing, MP4 start trimming, final artifact review, or deck preparation for video.
- Read `references/troubleshooting.md` when the server fails, Playwright cannot launch, slides are blank, MP4 conversion fails, or the manifest reports failures.
- Run `scripts/record-slidev-video.ts` directly. Read or patch the script only when changing recorder behavior or diagnosing a script bug.
