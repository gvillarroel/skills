Use the loaded D3 Animated SVG skill to create a self-contained HTML file named `breaker.html` in the current workspace.

Read this exact pattern reference first: `skills/d3-animated-svg/references/patterns/critical-circuit-breaker.md`.

Then run the bundled builder `skills/d3-animated-svg/scripts/build_critical_circuit_breaker.py` to create `breaker.html`. Do not hand-author a substitute artifact unless the builder fails.

The artifact must use the exact pattern `d3-pattern-critical-circuit-breaker` and render one inline SVG showing deterministic caller pressure, a caller service, a circuit breaker in open state, retry suppression, downstream failure, fail-fast fallback, limited half-open probes, breaker state timeline, failure and latency metric lines, mitigation steps, and status cards. Use portable SVG animation, title/desc accessibility nodes, stable SVG data attributes, `data-breaker-state`, `data-failure-threshold`, `data-current-failure-rate`, `data-open-window-seconds`, `data-timeout-ms`, `data-retry-budget`, `data-probe-count`, `.breaker-client`, `.caller-service`, `.circuit-breaker`, `.downstream-service`, `.fallback-service`, `.breaker-flow-path`, `.breaker-request-pulse`, `.open-circuit-barrier`, `.retry-suppression-gate`, `.fail-fast-path`, `.fallback-path`, `.probe-path`, `.half-open-probe`, `.breaker-state-node`, `.trip-threshold-line`, `.breaker-failure-line`, `.breaker-latency-line`, `.breaker-failure-point`, `.breaker-latency-point`, `.breaker-mitigation-step`, and `.breaker-status-card` classes.

Do not read files outside the current workspace. Do not use CDN scripts, remote fonts, remote images, or external runtime dependencies.
