# Lucidchart SVG local contract

Use the read-only skill at `skills/lucidchart-svg/`. Work only in this isolated workspace. Do not browse, access an account, or change the skill payload.

Create `inputs/graph.json` from this explicit graph:

```json
{"title":"Contract flow","nodes":[{"id":"start","type":"rectangle","x":20,"y":30,"width":100,"height":50,"label":"Start <draft> & review"},{"id":"end","type":"rectangle","x":220,"y":30,"width":100,"height":50,"label":"Finish"}],"edges":[{"id":"link","source":"start","target":"end","label":"approved"}]}
```

Run this exact command:

```sh
uv run --script skills/lucidchart-svg/scripts/build_native.py inputs/graph.json --output deliverables/flow.lucid --document-json deliverables/document.json
```

Also write `deliverables/status.md` describing what was actually created and whether an authenticated Lucid import occurred. Preserve labels as literal text. The `.lucid` archive and separate document JSON must contain the same document, two native shapes, and one connector attached to those shapes.
