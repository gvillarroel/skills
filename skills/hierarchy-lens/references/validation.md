# Validation and scale

Run the deterministic tests when changing the builder or aggregation contract:

```text
uv run --script <skill-root>/scripts/test_explorer.py
```

The browser audit checks the actual embedded source, rendered IDs, geometry stability after switching lenses, full-domain numeric scales after focus, category highlight stability, search and keyboard interaction, null coverage, offline requests, export metadata, and horizontal overflow at desktop/mobile sizes. It writes a machine-readable report and optional overview screenshot. Browser errors or failed assertions fail the audit.

Visually inspect the overview and at least one focused branch and numeric state. Small marks are expected in a dense overview; clipped controls, unreadable inner labels, invisible selection, or a branch that cannot be reached through search are defects. Confirm that printed value definitions match the actual input.

For scale testing, generate increasing synthetic sizes through `--demo-size`, run the same audit, record elapsed render time and DOM mark count, and inspect the intended screen size. The validation cap is 20000 records. Rendering is synchronous native SVG, so do not advertise millions of entities or simultaneous legibility. When the source exceeds a usable browser workload, agree on a summarized hierarchy with explicit aggregation or implement lazy loading; do not quietly omit records.

For new domains, test one small hand-calculated tree containing a root metric, a leaf zero, a missing metric, an internal node, and an uneven branch. Confirm the root sum includes each known entity exactly once. Reject forests/cycles rather than silently inventing links. A successful browser audit is technical evidence; use the user's analytical question to judge visual usefulness.
