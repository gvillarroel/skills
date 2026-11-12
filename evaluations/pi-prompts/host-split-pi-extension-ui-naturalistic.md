Use the copied skill for Pi Coding Agent. Treat `skills/pi-extension-ui/` as read-only. Write task artifacts only in this workspace outside the skill. Keep temporary state and caches task-local. Use only the supplied skill and normal local tools. Do not discover other skills or read installed host documentation, host examples, personal configuration, or any source outside this workspace. Running installed tool executables is allowed.

Build a Pi extension for selecting a report format: summary or detailed.
Create `deliverables/report-format.ts`. Use a deterministic native command,
keep the selected format in memory, and support a direct argument in a
noninteractive run. Cancellation must preserve the previous choice. Use the
actual local Pi RPC runtime to verify discovery, selection, cancel, invalid
input recovery, and a valid explicit argument without a model turn. Do not
install globally or add a web service. Write `deliverables/review.json` with
`host`, `mechanism`, `tests`, `remaining_host_checks`, and `heuristics`.
