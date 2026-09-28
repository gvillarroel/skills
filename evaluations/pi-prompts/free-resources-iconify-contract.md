# Iconify command contract

Treat `skills/iconify-icon-search/` as read-only. Run this exact command:

```sh
uv run --script skills/iconify-icon-search/scripts/iconify.py download --id lucide:house --color "#334155" --size 32 --output artifacts/house.svg
```

Read the SVG and receipt. Write `artifacts/review.md` with the exact identity,
height, color, source and collection license. Required outputs:
`artifacts/house.svg`, `artifacts/house.svg.json`, `artifacts/review.md`.
