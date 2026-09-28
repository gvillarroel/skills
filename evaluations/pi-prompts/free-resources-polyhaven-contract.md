# Poly Haven command contract

The copied `skills/polyhaven-asset-search/` bundle is read-only. All generated
files must be under this workspace. Run this command exactly:

```sh
uv run --script skills/polyhaven-asset-search/scripts/polyhaven.py download --id wood_floor_deck --variant Diffuse/1k/jpg --output artifacts/deck.jpg --max-mib 5
```

Inspect the resulting receipt and write `artifacts/review.md` identifying the
downloaded source, variant, byte size and whether its provider checksum passed.
Do not infer image content beyond the source metadata unless you inspect it.
Required outputs: `artifacts/deck.jpg`, `artifacts/deck.jpg.json`,
`artifacts/review.md`.
