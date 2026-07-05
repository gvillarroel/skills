Run this command first from the isolated workspace root: `uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/layered-architecture-video/artifacts/reviews/prompt-contract-build.json`

Create a deterministic standalone HTML video scaffold for a layered architecture readiness explainer.

Use the `layered-architecture` scaffold. Use 12 seconds, 12 fps, and 1280x720.

Topic: Layered architecture rollout
Video title: Layered Architecture Readiness
Checked date: July 4, 2026

Required exact scaffold outputs:

- `projects/layered-architecture-video/source/source-package.json`
- `projects/layered-architecture-video/source/production-notes.md`
- `projects/layered-architecture-video/src/index.html`
- `projects/layered-architecture-video/src/render.mjs`
- `projects/layered-architecture-video/artifacts/video-renders/draft/videos/layered-architecture-readiness.mp4`
- `projects/layered-architecture-video/artifacts/video-renders/draft/review/layered-architecture-readiness-contact-sheet.jpg`
- `projects/layered-architecture-video/artifacts/video-renders/draft/review/layered-architecture-readiness-contact-sheet.json`
- `projects/layered-architecture-video/artifacts/reviews/self-review.md`
- `projects/layered-architecture-video/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/layered-architecture-video/artifacts/reviews/render-state-check.json`.

Preserve these source facts:

- Layered architecture explainers should separate ownership boundaries from request flow.
- Cross-cutting policy, failure routing, observability, and rollout gates should not be hidden in the happy path.

Preserve these visual anchors:

- layer stack
- request path
- cross-cutting policy
- failure route
- observability
- rollout gate

Preserve these layer labels:

- Mobile client
- API gateway
- Application service
- Domain workflow
- Postgres data
- Kubernetes platform

Preserve these concern labels:

- zero-trust policy
- degraded fallback
- trace and metrics
- canary rollout

After the command finishes, verify the exact output paths, the wrapper report, the contact-sheet manifest, media properties, source preservation, and derived render-state check. Keep generated task files under `projects/layered-architecture-video/`; do not write into the copied skill directory.
