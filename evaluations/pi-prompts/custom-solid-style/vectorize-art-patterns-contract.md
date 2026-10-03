Vectorize the bundled public-domain Bailly source with this exact command. Inspect the SVG and report. Treat skills/vectorize-art-patterns/ as read-only and do not read acceptance fixtures or other skills. The bundled source manifest is the provenance authority. Keep outputs in this workspace.

```bash
uv run --script skills/vectorize-art-patterns/scripts/vectorize_art.py skills/vectorize-art-patterns/assets/base-images/bailly-beauties-fancy.jpg bailly.svg --mode organic --colors 12 --colorset colorset1 --max-dimension 320 --source-manifest skills/vectorize-art-patterns/assets/base-images/manifest.json --source-id bailly-beauties-fancy --report bailly.json
```
