Use the copied read-only Line World skill to make a six-second silent tutorial
fixture with two control focus stops. It tests preserved screenshot pixels and
clear semantic routing; it is not an actual website capture. Generate one
900 by 500 PNG under `film/media/` with a white background, a gray rectangle at
[120,140,260,80] labeled Search and another at [520,140,260,80] labeled Open.
Use a normal local image tool with declared dependencies. Keep the screenshot
unchanged after creation. Use scale 1.7, adjacent source-pixel ports [100,180]
and [500,180], and local cue times 1 and 4.5 seconds. No audio, accounts,
network captures or acceptance galleries are involved.

Write `film/story.json` with truthful synthetic source metadata and the
documented screenshot-tour contract. Use the bundled builder/renderer; keep
the copied skill read-only and all generated files in this workspace. Run these
exact commands:

```bash
uv run --script skills/line-world-video/scripts/website_video.py build --project film --story film/story.json
```

```bash
uv run --script skills/line-world-video/scripts/website_video.py render --project film --output film/final.mp4 --report film/review.json --poster film/poster.png
```

Inspect the poster and an actual encoded frame. In `review.md`, record source
preservation, reading clearance, exact duration/frame checks, the fixture's
synthetic nature and remaining limits. Required exact outputs: `film/story.json`,
`film/index.html`, `film/preview.html`, `film/tour.json`, `film/final.mp4`,
`film/review.json`, `film/poster.png` and `review.md`.
