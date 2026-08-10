# Evaluation Datasets

Use one lowercase hyphen-case directory per reusable evaluation dataset:

```text
evaluations/datasets/<dataset-id>/
|-- README.md
|-- manifest.json
|-- schema.json
|-- config.yaml
|-- raw/
`-- processed/
```

The dataset root contains the durable source contract:

- `README.md` explains purpose, provenance, rights, scope, limitations, and regeneration.
- `manifest.json` identifies immutable sources, hashes, retrieval dates, schema versions, and expected outputs.
- `schema.json` or `*.schema.json` defines machine-checkable data contracts when useful.
- `config.json`, `config.yaml`, `config.yml`, or `config.toml` records deterministic transformation settings.

`raw/` is for downloaded, captured, or otherwise source-like data. `processed/` is for normalized rows, indexes, caches, embeddings, and generated exports. Git ignores the data in both directories while allowing lightweight README, manifest, schema, config, and `.gitkeep` control files.

Prefer commands that rebuild `processed/` from `raw/` plus the versioned root controls. Do not commit credentials, private payloads, or bulky generated data.
