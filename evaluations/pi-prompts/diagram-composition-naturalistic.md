Use diagram-composition to make a compact, readable figure for an internal
engineering discussion. It should explain how a team combines developer tools,
permissions, and one shared workspace. This is an illustrative proposal.

Facts: the editor, code assistant, and CI runner each connect directly to the
shared workspace. They are unordered peers, not steps in a process. The editor
can read and write source, the assistant can read source and propose changes,
and the CI runner can read source and publish build results. Proposals require a
human review before becoming source. The workspace contains source and build
results, with a review boundary around proposals. Do not imply that the assistant
can publish builds or write source without review.

I want the connectivity explanation in the upper-left two cells of a four-column
grid, the permissions comparison in the lower-left two cells, and an integrated
view spanning both rows on the right. Choose appropriate forms for those
questions. Use simple recognizable unbranded SVG symbols where they reduce
repeated text, with a shared visible key and accessible identities. Do not fetch
brands. Avoid repeated sentences inside boxes.

The figure must be 1200 by 780, legible when displayed at 1000px wide with
essential labels at least 14px. Deliver out/plan.json, out/figure.svg,
out/report.json, out/audit.json, out/preview.png, and out/review.md, with editable
panel SVGs under out/panels/. Verify the rendered result. The review should
explain conceptual decomposition, alternatives, and any unresolved issue.
The loaded skills/diagram-composition/ directory is read-only. Keep all generated
files inside this workspace. Do not read other skills, use the network, or
install tools. All the factual inputs are in this request.
