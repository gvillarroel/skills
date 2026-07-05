Run this command first from the isolated workspace root: `uv run --script skills/html-d3-anime-video-workflow/scripts/check_standalone_pattern_contracts.py --output projects/pattern-contract-check/artifacts/reviews/pattern-contract-check.json`

Validate the standalone scaffold pattern catalog for the copied `html-d3-anime-video-workflow` skill.

Required exact outputs:

- `projects/pattern-contract-check/artifacts/reviews/pattern-contract-check.json`

After the command finishes, verify the JSON report exists, is non-empty, has `"passed": true`, checks at least 17 patterns, and has an empty `findings` array. Keep generated task files under `projects/pattern-contract-check/`; do not write into the copied skill directory.
