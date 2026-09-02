# Decision: separate authored guides from generated Pages output

## Context

The Pages builder previously deleted docs/ before every build, and Git ignored
the entire directory. That made docs/ unsafe for maintained project guides.

## Decision

- Keep authored Markdown under docs/ and make it versionable.
- Generate the example site under ignored dist/pages/.
- Make the output validator and GitHub Actions artifact upload read dist/pages/.
- Restrict cleanup to that exact resolved directory; reject widened or redirected paths.
- Preserve existing example URLs and the public site layout: only the local
  artifact directory changes.
- Leave old local generated docs files ignored; do not delete them in migration.

## Verification

`uv run --script scripts/test-pages-output.py` checks preservation of authored
guides, unrelated dist files, and rejection of unsafe cleanup paths. A release
also requires the normal Pages build and generated-format validator.
