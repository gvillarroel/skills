Check recovery from a bad line-world story without changing the copied skill.
Create a project at `boundary-film/`. Test a negative before value, duplicate
row IDs, mismatched history lengths, and a table beat too short to read all rows.
Each must be rejected, without replacing the last valid built timing manifest.
For expected negative cases, capture the validator exit code through a local
subprocess and report it; the surrounding test command should succeed when
rejection is the expected behavior. Restore valid project-owned data and rebuild.

Write `boundary-report.json` with each case, whether it was rejected, the final
valid duration and an overall pass flag. Do not render or install packages.
Use a `cases` array with `rejected` and `timingManifestUnchanged` booleans,
and top-level `validStoryRestored` and `pass` booleans.
Keep `skills/line-world-video/` read-only and use only that skill and normal local
tools, without other skills, repository files or global configuration.
