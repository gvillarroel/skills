# Kenney command contract

Treat `skills/kenney-asset-search/` as read-only. Run this command exactly:

```sh
uv run --script skills/kenney-asset-search/scripts/kenney.py download --id pattern-pack --output artifacts/patterns.zip --max-mib 10
```

Read the receipt. Write `artifacts/review.md` identifying the selected pack,
free download source and whether the archive contains a license file. Required
outputs: `artifacts/patterns.zip`, `artifacts/patterns.zip.json`,
`artifacts/review.md`.
