# Standalone motion integration

Use only the loaded `line-world-video` skill and normal local tools. Its copied
directory is read-only. Keep generated files under `artifacts/`.

Create `artifacts/scene.html`, an offline 14-second 800×450 SVG scene. Four
simple self-authored geometric marks act as identity placeholders, each with a
short adjacent label. Keep the complete mark/label groups gently floating with
distinct stable phases. Include a separate static source image as a data-URI SVG
containing a red circle, gray diagonal and white background. A slow detail view
should focus on that image, hold long enough to inspect it and return once.
Keep its caption fixed outside the clipped image viewport. Expose pure
`renderAt(seconds)`. Do not add a visible title, center divider or panel borders.

Use the skill's actual bundled motion helper and run its browser tests. Verify
the consumer scene in a browser at several times and after backward seeking.
Write `artifacts/reading.png` and `artifacts/quality.json`. The JSON should
identify the actual runtime, tested times, original source-image identity,
observed motion, fixed caption, detail return and repeated seek outcome.
Do not render a full movie, access accounts, search the repository or read
acceptance examples. Report observed limitations honestly.
