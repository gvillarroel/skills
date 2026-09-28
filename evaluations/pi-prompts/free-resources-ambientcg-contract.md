# ambientCG command contract

Treat `skills/ambientcg-material-search/` as a read-only resource. Run:

```sh
uv run --script skills/ambientcg-material-search/scripts/ambientcg.py download --id Wood095 --variant 1K-JPG/zip --output artifacts/wood.zip --max-mib 10
```

Inspect the receipt and write `artifacts/review.md` identifying the exact asset,
variant, archive members and transfer validation. Required outputs:
`artifacts/wood.zip`, `artifacts/wood.zip.json`, `artifacts/review.md`.
