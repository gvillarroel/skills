Use the loaded D3 Animated SVG skill to create a self-contained HTML file named `failover.html` in the current workspace.

Read the matching pattern reference before building the artifact.

The artifact must use the exact pattern `d3-pattern-critical-replication-failover` and render one inline SVG showing deterministic database replication failover with a degraded primary, multiple replicas, replication links, animated replication pulses, replica lag thresholds, quorum votes, old-writer fencing, an RPO gap, a promotion path, a traffic reroute endpoint, failover runbook steps, and status cards. Use portable SVG animation, title/desc accessibility nodes, stable SVG data attributes, `data-rpo-events-at-risk`, `data-rto-target-seconds`, `data-write-fence-count`, `data-traffic-reroute-count`, `.replication-node`, `.primary-node`, `.replica-node`, `.witness-node`, `.replication-link`, `.replication-pulse`, `.lag-chart-line`, `.lag-threshold-band`, `.lag-sample-point`, `.quorum-vote`, `.write-fence`, `.failover-step`, `.promotion-path`, `.traffic-reroute`, `.traffic-reroute-path`, `.rpo-gap`, and `.replication-status-card` classes.

If the skill includes a bundled builder for this pattern, use it. Do not read files outside the current workspace.
