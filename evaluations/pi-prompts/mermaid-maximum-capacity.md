Use the `mermaid` skill to author three Mermaid source diagrams that exercise renderer-owned palette capacity boundaries.

Work only from the copied skill and this prompt. Treat `skills/mermaid/` as read-only. Keep generated files in the workspace. Do not inspect repository files, sibling skills, acceptance fixtures, prior runs, or network resources. Do not install packages or render SVG/PNG files.

The only conditional reference required for these cases is `skills/mermaid/references/palette-capacity.md`. Do not run broad exploratory searches for examples or fenced Markdown, and do not put Markdown backticks inside shell search patterns. Every shell command must exit successfully because the strict trace treats a no-match search as a tool error.

Read the skill's capacity reference and infer each terminal count from Mermaid 11.16.0. Do not guess a generic limit. Apply palettes with the bundled styling script and finish with a successful `--check` pass for each output directory.

## Cases

### mindmap

Create a standard-palette mindmap whose root is `Capacity map`. Add direct children named `Mind branch 01`, `Mind branch 02`, and so on through the last first-level branch that remains on a distinct color before cycling. Add no deeper levels and no overflow branch.

### journey

Create a standard-palette Journey that demonstrates the reachable section-color boundary. Use one section and one task per slot. Consume every distinct reachable section class once, then add exactly one boundary section that cycles to the first class. Name sections `Journey slot 01`, `Journey slot 02`, and so on; name tasks `Step 01`, `Step 02`, and so on. Give every task score 5 and agent `Owner`. Add no further section.

### kanban

Create an extended-palette Kanban board with every reachable colored column before Mermaid's generated section rules stop. Name columns `Kanban slot 01`, `Kanban slot 02`, and so on; put exactly one matching task `Work 01`, `Work 02`, and so on in each column. Add no uncolored overflow column.

## Exact outputs

Create exactly these required files; additional temporary reports are allowed outside `skills/mermaid/`:

- `deliverables/standard/mindmap.mmd`
- `deliverables/standard/journey.mmd`
- `deliverables/extended/kanban.mmd`
- `deliverables/capacities.json`
- `deliverables/style-standard-report.json`
- `deliverables/style-standard-check.json`
- `deliverables/style-extended-report.json`
- `deliverables/style-extended-check.json`

`deliverables/capacities.json` must be valid JSON with this shape:

```json
{
  "mermaidVersion": "11.16.0",
  "cases": [
    {
      "id": "mindmap",
      "family": "mindmap",
      "colorset": "colorset1",
      "paletteSlots": 0,
      "authoredElements": 0,
      "terminalLabel": ""
    }
  ]
}
```

Include exactly three case objects in the order `mindmap`, `journey`, `kanban`, replacing the placeholder values with the discovered capacities. For Journey, `paletteSlots` is the number of distinct reachable colors and `authoredElements` includes the additional cycling boundary section. For Mindmap, count the root in `paletteSlots` and `authoredElements`. For Kanban, count columns. Both check reports must end with `missingStyleCount` equal to `0`. Do not finish until every exact output exists and is non-empty.
