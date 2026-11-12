Use the copied skill for Claude Code terminal and Desktop Code tab. Treat `skills/code-native-plugin-ui/` as read-only. Write task artifacts only in this workspace outside the skill. Keep temporary state and caches task-local. Use only the supplied skill and normal local tools. Do not discover other skills or read installed host documentation, host examples, personal configuration, or any source outside this workspace. Running installed tool executables is allowed.

Build a read-only native Claude Code plugin for a three-item deployment queue.
Rows DEP-1 and DEP-3 are pending, and DEP-2 is complete. Let users select all,
pending, or complete without a model call, close the view, and reopen it. A
direct argument must work when a pane is unavailable. Create the runnable
plugin at `deliverables/deployment-view/` with authentic native-engine tests,
and run strict package validation and those tests using task-local host state.
Keep other plugins' command and pane behavior usable. Do not modify personal
host settings or install globally. Write `deliverables/review.json` with
`host`, `mechanism`, `tests`, `remaining_host_checks`, and `heuristics`.
