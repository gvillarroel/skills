Use $awsome-videos.

Create a production-package scaffold for a source-backed 80-second compressed explainer titled "How Cache Stampedes Happen". The promise is: "See one expired hot key turn into an origin overload, then watch request coalescing stop it." Write the package to `outputs/cache-stampede` and preserve the skill's stable scene, beat, asset, composition, routing, provenance, and review contracts.

Run these exact commands from the workspace root:

```bash
bash -lc 'mkdir -p outputs && uv run --script skills/awsome-videos/scripts/scaffold_production_package.py outputs/cache-stampede --title "How Cache Stampedes Happen" --promise "See one expired hot key turn into an origin overload, then watch request coalescing stop it." --audience "Backend developers who know basic caching" --format "compressed explainer" --runtime 1:20 --project-id cache-stampede --skill-path skills/awsome-videos --json > outputs/scaffold-result.json'
bash -lc 'uv run --script skills/awsome-videos/scripts/check_visual_contract.py --asset-manifest outputs/cache-stampede/source/asset-manifest.json --composition-plan outputs/cache-stampede/source/composition-plan.json --brief outputs/cache-stampede/source/brief.md --project-root outputs/cache-stampede --min-assets 8 --min-scenes 8 --output outputs/visual-contract-structural.json --json > outputs/visual-contract-stdout.json'
```

Required outputs:

- `outputs/scaffold-result.json`
- `outputs/visual-contract-structural.json`
- `outputs/visual-contract-stdout.json`
- `outputs/cache-stampede/source/asset-manifest.json`
- `outputs/cache-stampede/source/composition-plan.json`
- `outputs/cache-stampede/source/source-package.json`
- `outputs/cache-stampede/source/shot-contract.json`
- `outputs/cache-stampede/source/transition-plan.json`
- `outputs/cache-stampede/artifacts/reviews/visual-review.json`
- `outputs/cache-stampede/source/package-manifest.json`
- `outputs/cache-stampede/src/index.html`

After both commands finish, read only the required JSON outputs plus the generated source, shot, asset, composition, transition, review, and package contracts. Do not inspect script source or acceptance examples.

Report whether structural validation has `ok: true`; the number of assets, scenes, composition choices, armatures, and materially distinct spatial layouts; whether every scene/beat/asset seam is bound; which specialist skills own source, composition, transitions, assets, and rendering; whether each planned route carries a proof path; and why the generated `AWSOME_SCAFFOLD_WIREFRAME` renderer must not be delivered as a finished video. Also confirm that final validation remains pending until URL-backed facts and their shot mapping are frozen, real asset files and passing producer/route proofs exist, the renderer actually loads those assets, every ordered scene/seam frame matches the exact candidate MP4, full-speed playback is approved, and final package validation has rerun the browser renderer and readiness scorer.
