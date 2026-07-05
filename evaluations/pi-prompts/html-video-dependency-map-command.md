# First Action: Read `../prompt.md` Before Any Shell Command

First tool call requirement: use the read tool on `../prompt.md`. Do not run `ls`, `pwd`, `find`, `test`, `cat`, shell probes, or any directory listing before that read. After reading `../prompt.md`, run exactly one shell command: the scaffold command below. Do not read `SKILL.md`, helper script source, checker script source, generated reports, or generated manifests unless the scaffold command fails; the outer evaluation harness checks required paths.

Run exactly one scaffold command:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/dependency-map-video/artifacts/reviews/prompt-contract-build.json
```

Required exact outputs:

- `projects/dependency-map-video/source/source-package.json`
- `projects/dependency-map-video/source/production-notes.md`
- `projects/dependency-map-video/src/index.html`
- `projects/dependency-map-video/src/render.mjs`
- `projects/dependency-map-video/artifacts/video-renders/draft/videos/dependency-map-explainer.mp4`
- `projects/dependency-map-video/artifacts/video-renders/draft/review/dependency-map-explainer-contact-sheet.jpg`
- `projects/dependency-map-video/artifacts/video-renders/draft/review/dependency-map-explainer-contact-sheet.json`
- `projects/dependency-map-video/artifacts/reviews/self-review.md`
- `projects/dependency-map-video/artifacts/reviews/prompt-contract-build.json`

Additional exact browser-state output:

- `projects/dependency-map-video/artifacts/reviews/render-state-check.json`

Video title: Dependency Map Explainer
Topic: migration dependency map for a release cutover
Checked date: 2026-07-04

Use 12 seconds, 12 fps, and 1280x720.
Use the `dependency-map` scaffold.

Preserve these source facts:

- The rollout has shared source and identity prerequisites.
- The schema normalizer is blocked until both upstream sources are ready.
- The integration service is the bottleneck for release readiness.
- Cutover must wait for upstream proof before the release gate opens.
- A rollback route should be visible before the release boundary is treated as safe.

Preserve these visual anchors:

- dependency graph
- cluster boundary
- shared prerequisite
- risk edge
- bottleneck
- cutover gate
- fallback path
- release readiness

Preserve these dependency labels:

- catalog feed
- identity sync
- schema normalizer
- policy review
- contract tests
- integration service
- release gate
- rollback route

Preserve these dependency clusters:

- source systems
- integration layer
- release boundary

After the command finishes, verify the wrapper report. It must show `passed: true`, no findings, source preservation with no missing facts, anchors, dependency labels, or dependency clusters, 12.0 seconds, 12 fps, 1280x720 media, and a passing derived `stateCheck` that includes final-state checks including `edgeCount=7`, transition checks, label-containment, monotonic `visibleMechanismCount`, monotonic `edgeCount`, distinct edge-count progression, and `visualPattern=dependency-map` checks. Do not read helper script source unless the command fails.
