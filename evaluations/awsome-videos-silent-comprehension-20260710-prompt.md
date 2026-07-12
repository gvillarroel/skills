Use the `awsome-videos` skill to create a production-ready 70-second compressed technical explainer titled “Idempotency keys stop duplicate payments.” The audience is Spanish-speaking backend developers. Use these supplied source links as the frozen factual basis:

- https://docs.stripe.com/api/idempotent_requests
- https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/

Create exactly these non-empty files:

1. `outputs/idempotency-brief.md`
2. `outputs/silent-review-plan.json`
3. `outputs/brief-validation.json`

The brief must contain eight timed beats covering exactly 70 seconds, an eight-line Spanish voiceover draft, concrete visuals, semantic animation, transitions, audio direction, assets/sources, and evaluation criteria. Make every scene understandable with audio muted: the primary hold must expose a recognizable object, its causal action, and its visible result rather than anonymous moving geometry.

The review-plan JSON must use `schemaVersion: 1`. Its `scenes` field must be an array of eight objects ordered `s01` through `s08`. Give each scene `checks.silentComprehension: "pass"` plus `silentTest` with `durationSeconds` no greater than 3 and substantive `object`, `action`, and `result` strings. Include a short correction rule for what to change if the silent test fails.

Run this exact command from the isolated workspace root:

```shell
uv run --script skills/awsome-videos/scripts/check_video_brief.py outputs/idempotency-brief.md --require-voiceover --require-source-links --json
```

After that exact command succeeds, save its observed complete JSON result once to `outputs/brief-validation.json` without changing its values. Do not rerun the validator, compare the result, create temporary files, or create any other deliverable files.
