Create a self-contained standalone HTML file at exactly `rate-limit.html`.

Read this exact pattern reference first: `skills/d3-animated-svg/references/patterns/critical-rate-limit-token-bucket.md`.

The only valid way to create the artifact is to run the bundled builder. First confirm the builder exists, then run it:

```powershell
Get-ChildItem skills/d3-animated-svg/scripts/build_critical_rate_limit_token_bucket.py
uv run --script skills/d3-animated-svg/scripts/build_critical_rate_limit_token_bucket.py rate-limit.html
```

Do not hand-author a substitute artifact. Do not create a canvas, CSS-only demo, generic HTML card, placeholder, or JavaScript-rendered empty SVG. If the builder command fails, stop and report the failure instead of writing any fallback file.

After running the builder, inspect `rate-limit.html` and confirm it contains both exact strings:

```text
<svg id="critical-rate-limit-token-bucket"
data-pattern-id="d3-pattern-critical-rate-limit-token-bucket"
```

The artifact must use the exact pattern `d3-pattern-critical-rate-limit-token-bucket` and render one inline SVG showing deterministic clients, API gateway, token bucket, token slots, refill clock, allowed path, throttled path, protected backend, 429 Retry-After response, incoming/allowed/rejected metric lines, policy steps, request pulses, and status cards. Use portable SVG animation, title/desc accessibility nodes, stable SVG data attributes, `data-bucket-capacity`, `data-current-tokens`, `data-refill-rate`, `data-burst-limit`, `data-retry-after-seconds`, `data-allowed-rate`, `data-throttled-rate`, `.rate-limit-client`, `.api-gateway`, `.token-bucket`, `.token-slot`, `.refill-clock`, `.rate-limit-flow-path`, `.rate-limit-request-pulse`, `.allowed-path`, `.throttled-path`, `.retry-after-response`, `.protected-backend`, `.rate-limit-metric-line`, `.rate-limit-metric-point`, `.limit-threshold-line`, `.rate-limit-policy-step`, and `.rate-limit-status-card` classes.

Do not read files outside the current workspace. Do not use CDN scripts, remote fonts, remote images, or external runtime dependencies.
