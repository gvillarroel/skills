# First Action: Read `../prompt.md` Before Any Shell Command

First tool call requirement: use the read tool on `../prompt.md`. Do not run `ls`, `pwd`, `find`, `test`, `cat`, shell probes, or any directory listing before that read. After reading `../prompt.md`, run the scaffold command below. Do not read helper script source or checker script source unless the scaffold command fails.

Run this scaffold command:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/sequence-trace-video/artifacts/reviews/prompt-contract-build.json
```

Required exact outputs:

- `projects/sequence-trace-video/source/source-package.json`
- `projects/sequence-trace-video/source/production-notes.md`
- `projects/sequence-trace-video/src/index.html`
- `projects/sequence-trace-video/src/render.mjs`
- `projects/sequence-trace-video/artifacts/video-renders/draft/videos/sequence-trace-explainer.mp4`
- `projects/sequence-trace-video/artifacts/video-renders/draft/review/sequence-trace-explainer-contact-sheet.jpg`
- `projects/sequence-trace-video/artifacts/video-renders/draft/review/sequence-trace-explainer-contact-sheet.json`
- `projects/sequence-trace-video/artifacts/reviews/self-review.md`
- `projects/sequence-trace-video/artifacts/reviews/prompt-contract-build.json`

Additional exact browser-state output:

- `projects/sequence-trace-video/artifacts/reviews/render-state-check.json`

Video title: Sequence Trace Explainer
Topic: distributed trace latency investigation for checkout
Checked date: 2026-07-04

Use 12 seconds, 12 fps, and 1280x720.
Use the `sequence-trace` scaffold.

Preserve these source facts:

- A slow checkout request crosses gateway, auth, inventory, payment, and database spans.
- The database wait dominates the critical path.
- Retry should be visible only after the slow span is exposed.
- Fallback cache is a late resilience branch, not a primary happy path.
- The response should return only after latency budget and fallback are clear.

Preserve these visual anchors:

- trace waterfall
- service lane
- span duration
- handoff marker
- critical path
- latency budget
- retry branch
- fallback response

Preserve these trace labels:

- checkout client
- edge gateway
- auth service
- inventory service
- payment service
- orders database
- fallback cache
- checkout response

After the command finishes, read `projects/sequence-trace-video/artifacts/reviews/prompt-contract-build.json` and verify that it shows `passed: true`, no findings, no missing source facts, no missing anchors, no missing trace labels, 12.0 seconds, 12 fps, 1280x720 media, passing `contactSheet`, `openingTile`, `finalTile`, and a passing derived `stateCheck`. The state check must include `visualPattern=sequence-trace`, trace-label containment, final-state checks including `activeSpanCount=7`, `false->true` transition checks, monotonic `visibleMechanismCount`, monotonic `activeSpanCount`, and distinct span-count progression.
