Use the loaded D3 Animated SVG skill to create a self-contained HTML file named `queue.html` in the current workspace.

Read the matching pattern reference before building the artifact.

The artifact must use the exact pattern `d3-pattern-critical-queue-backpressure` and render one inline SVG showing deterministic queue overload and mitigation with producer sources, a bounded queue, queue segments, competing consumers, backpressure gates, load shedding, a dead-letter or sideline bin, queue-depth trend, message-age/TTL guard, status cards, and animated message pulses. Use portable SVG animation, title/desc accessibility nodes, stable SVG data attributes, `data-current-depth`, `data-backpressure-threshold`, `data-oldest-message-minutes`, `.producer-source`, `.bounded-queue`, `.queue-segment`, `.queue-flow-path`, `.consumer-worker`, `.backpressure-gate`, `.load-shed-path`, `.dead-letter-bin`, `.queue-age-guard`, `.queue-depth-line`, `.queue-capacity-marker`, `.queue-depth-point`, `.queue-status-card`, and `.queue-message-pulse` classes.

If the skill includes a bundled builder for this pattern, use it. Do not read files outside the current workspace.
