Render this small synthetic approval diagram with the supplied skill. Save the source at `approval.mmd` exactly, preserving all labels and relations:

```text
flowchart TB
  accTitle: Synthetic approval
  accDescr: A received record is reviewed, and an approved record is archived.
  A["Record received"] -->|inspect record| B["Review decision"]
  B -->|approved| C["Approved archive"]
```

Read the skill's connected-layout guidance and use its standard compact presentation. Run these commands exactly, in separate shell calls:

```sh
uv run --script skills/mermaid/scripts/style_mermaid_directory.py approval.mmd --write --report style.json
```

```sh
uv run --script skills/mermaid/scripts/style_mermaid_directory.py approval.mmd --check --require-accessibility --report check.json
```

```sh
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py approval.mmd -o approval.svg --animation none --require-accessibility
```

Create `review.md` describing what can be verified from the final source/render, any actual visual inspection and any unresolved limitation. Exact required outputs are `approval.mmd`, `approval.svg`, `style.json`, `check.json`, `review.md`. Keep `skills/mermaid/` read-only and all generated files in the workspace. Do not read galleries or other skills; dependencies required by the bundled commands may resolve normally.
