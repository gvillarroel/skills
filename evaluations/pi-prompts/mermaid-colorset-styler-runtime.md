Use the `mermaid-colorset-styler` skill to style already-generated Mermaid diagrams in a directory.

Create the exact input files and run the exact commands below. Do not write generated outputs inside `skills/mermaid-colorset-styler/`; treat the copied skill directory as read-only. Finish only after all expected files exist and the check command reports no missing style updates.
The two report files are written at the workspace root as `styled-report.json` and `styled-check.json`, not inside `source/`.

```bash
mkdir -p source
cat > source/base-flow.mmd <<'EOF'
flowchart LR
  Intake[Request]:::csPrimary --> Review{Review}:::csWarning
  Review -->|approve| Ship[Ship]:::csSuccess
  Review -->|reject| Fix[Fix]:::csCritical
  Ship e1@--> Done[Done]:::csAccent
  class e1 csMuted
EOF
cat > source/base-state.mmd <<'EOF'
stateDiagram-v2
  [*] --> Draft
  Draft:::csMuted --> Active:::csPrimary
  Active --> Blocked:::csCritical
  Blocked --> Active
  Active --> Done:::csSuccess
EOF
{
  echo '# Generated Mermaid notes'
  echo
  echo '```mermaid'
  echo 'sequenceDiagram'
  echo '  participant Client'
  echo '  participant Service'
  echo '  Client->>Service: Request'
  echo '  Service-->>Client: Response'
  echo '```'
  echo
  echo '```mermaid'
  echo 'treemap-beta'
  echo '  "Base"'
  echo '    "Primary": 10:::csPrimary'
  echo '    "Accent": 5:::csAccent'
  echo '```'
} > source/notes.md
uv run --script skills/mermaid-colorset-styler/scripts/style_mermaid_directory.py source --colorset colorset1 --write --report styled-report.json
uv run --script skills/mermaid-colorset-styler/scripts/style_mermaid_directory.py source --colorset colorset1 --check --report styled-check.json
```

Required exact outputs:

- `source/base-flow.mmd`
- `source/base-state.mmd`
- `source/notes.md`
- `styled-report.json`
- `styled-check.json`

Expected result:

- Every Mermaid block uses YAML frontmatter config with `theme` set to `base` and `colorset1` theme variables.
- Only the class-capable diagrams with referenced color classes receive generated `classDef` lines.
- `styled-check.json` reports `missingStyleCount` equal to `0`.
