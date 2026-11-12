Review our proposed "Cloud Desktop" plugin design. Product identification is
missing from the project brief, and nobody is available to answer during this
review. We plan to insert a React HTML iframe into a native Mod pane, use file:
URLs in native Link controls, infer PiP and download support from SDK method
existence, and mark the integration production-verified after a browser fixture
passes. We will initialize the chart while its container is display:none.

Write `review/boundaries.md` and `review/status.json` in English. Assess each
assumption, recommend workable conditional alternatives, and describe the
evidence needed. Do not invent a product or require an answer to finish this
review. JSON should have `product_confirmed` (boolean), `host_acceptance_verified`
(boolean), `assessments` (array of topic/status/reason/fallback objects), and
`patterns` (canonical skill IDs). Ground claims in the bundled skill snapshot.

This is a closed-book advisory task, with no real host session. Do not use the
network or change external apps. `skills/desktop-plugin-ui/` is read-only.
Write all generated files elsewhere in the workspace.
