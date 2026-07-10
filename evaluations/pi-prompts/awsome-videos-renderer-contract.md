Use $awsome-videos.

Create a deterministic renderer package for a short technical explainer. Work only in `outputs/`.

Run this exact scaffold command first:

```bash
bash -lc 'mkdir -p outputs && uv run --script skills/awsome-videos/scripts/scaffold_production_package.py outputs/cache-story --title "What Is A Cache Stampede?" --promise "Explain cache stampede as many requests missing the same expired key, then collapsing work with locks and stale responses." --project-id cache-stampede --skill-path skills/awsome-videos --json > outputs/scaffold-result.json'
```

Then run this exact renderer validation command:

```bash
bash -lc 'uv run --script skills/awsome-videos/scripts/check_renderer_contract.py outputs/cache-story/src/index.html --duration 70 --output outputs/cache-story/artifacts/reviews/render-state.json --install-browser --json > outputs/renderer-validation.json'
```

Required outputs:

- `outputs/scaffold-result.json`
- `outputs/renderer-validation.json`
- `outputs/cache-story/source/brief.md`
- `outputs/cache-story/source/production-notes.md`
- `outputs/cache-story/source/package-manifest.json`
- `outputs/cache-story/src/index.html`
- `outputs/cache-story/artifacts/reviews/render-state.json`

The final answer must report whether `outputs/renderer-validation.json` has `"ok": true`, how many sampled states were recorded, how many unique beats were sampled, and whether the scaffolded brief and production notes are concept-specific rather than blank templates.
