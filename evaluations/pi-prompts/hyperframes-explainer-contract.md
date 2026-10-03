# Exact-path preview smoke

Create a working explanatory preview from the bundle's illustrative starting
brief. This case checks the supplied command contract, so run these exact commands:

```bash
uv run --script skills/hyperframes-explainer/scripts/explainer.py preflight --brief skills/hyperframes-explainer/assets/templates/brief.json --report out/preflight.json
uv run --script skills/hyperframes-explainer/scripts/explainer.py build --brief skills/hyperframes-explainer/assets/templates/brief.json --project out/project --report out/build.json
```

Inspect both reports and confirm `ok: true`. Required outputs are exactly
`out/preflight.json`, `out/build.json`, `out/project/index.html`,
`out/project/preview.html` and `out/project/manifest.json`. The source skill is
read-only. Write all task files inside this workspace, never in the skill.
Do not install dependencies or encode a movie for this preview smoke. Do not
read sibling skills, repository docs, acceptance fixtures or external files.
