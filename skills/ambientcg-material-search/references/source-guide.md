# ambientCG source guide

## Resource types and search

Use `--type material` for PBR surfaces. Other documented v3 values are `hdri`,
`substance`, `decal`, `atlas`, `3d-model`, `plain-image`, `brush`, `terrain`, and
`hdri-element`. A material package contains several maps; a plain image is not
a complete material. Choose the type from the user's use case.

Useful search families include wood, brick, paving stones, concrete, plaster,
metal, fabric, leather, ground, sand, rocks, ice and snow. They are descriptive
search aids, not a promise that the live taxonomy remains unchanged.

The API treats space/comma separated words as AND. Try `wood`, then `wood dark`
or `wood rough`; do not send a full translated sentence with many constraints.
Use metadata and visual review to assess criteria the query cannot express.

```sh
uv run --script <skill-dir>/scripts/ambientcg.py search --query "concrete" --type material --sort popular --offset 6 --limit 6 --out more.json --html more.html
uv run --script <skill-dir>/scripts/ambientcg.py search --query "sunset" --type hdri --out lighting.json --html lighting.html
uv run --script <skill-dir>/scripts/ambientcg.py inspect --id Wood095 --out selected.json
```

Allowed sort values: `popular`, `latest`, `downloads`, `oldest`, `alphabet`.
`--limit` is 1–20; `--offset` skips fetched assets. Retain `has_more` and `total`
from the manifest. An empty window is not proof the catalog has no relevant asset.

## Files and identity

Use `previews --manifest options.json --output-dir artifacts/previews` to save
bounded thumbnail files for image-tool review. The directory must be new and
inside the active workspace. Returned local paths preserve the saved option IDs;
no full material package is downloaded by this command.

Selection uses `--id ASSET_ID`, or `--manifest FILE` plus exactly one `--option`
or `--id`. `inspect` refreshes only that asset. `variants[].key` combines the
provider's attributes and extension, for example `1K-JPG/zip` or `4K-PNG/zip`.
The variants are not interchangeable. Read available `maps` and the returned ZIP
member inventory; do not infer that every package includes every map.

`--max-mib 512` bounds the downloaded package. The helper validates HTTP length,
API-reported size, container signatures and ZIP CRCs. It records a locally
computed SHA-256, not a provider checksum when the provider supplied none.
It rejects malformed/unsafe archive paths and reports failures as JSON with exit 2.
Partial transfers are removed; existing outputs and receipts are protected.

Prefer the full ZIP for PBR work because color, normal, roughness and displacement
must stay associated. Follow the application's OpenGL/DirectX normal convention
when assigning extracted maps. For HDRI lighting choose the available HDR/EXR
variant, not a display thumbnail.

## Sources and access

Verified on 2026-09-27:

- [API overview](https://docs.ambientcg.com/api/) and
  [v3 assets contract](https://docs.ambientcg.com/api/v3/assets/).
- API base: `https://ambientcg.com/api/v3/assets`. Search uses `q`, `type`,
  `sort`, `limit`, `offset`; exact lookup uses `id`. Request the fields needed
  with `include`. The helper reads `assets`, `totalResults`, and `nextPageHttp`.
- [License](https://docs.ambientcg.com/license/): released asset files and their
  material preview renders use CC0, including commercial use without attribution.
- [Catalog](https://ambientcg.com/): free public resources; supporter perks such
  as early access are separate. Do not use supporter credentials for this workflow.

Use the provider's actual `downloads[].url`; redirects currently lead to the
ambientCG download CDN. If its host changes, inspect the official page before
updating the helper's allowed origins.
