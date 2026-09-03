Use the provided `plantuml-colorset-renderer` skill to render three small,
synthetic, non-sensitive PlantUML diagrams with the bundled Colorset 2 theme.
Render both SVG and PNG, then validate the render report.

Treat `skills/plantuml-colorset-renderer/` as read-only. Write generated files
only under `inputs/` and `outputs/plantuml/`. Do not inspect repository-level
files, sibling skills, acceptance examples, or the network outside the Kroki
requests made by the bundled renderer. This task explicitly permits Kroki for
these synthetic fixtures.

Run this exact command from the isolated workspace:

```bash
mkdir -p inputs outputs/plantuml
cat > inputs/sequence.puml <<'PUML'
@startuml
title Runtime Sequence
actor User
participant API
database DB
User -> API : create order
API -> DB : insert
DB --> API : id
API --> User : accepted
@enduml
PUML
cat > inputs/class.puml <<'PUML'
@startuml
title Runtime Class
class Order {
  +id: string
  +status: string
}
class Payment {
  +authorize(): bool
}
Order --> Payment : uses
@enduml
PUML
cat > inputs/mindmap.puml <<'PUML'
@startmindmap
title Runtime Mindmap
* Renderer
** Colorset 2 theme
** SVG
** PNG
@endmindmap
PUML
uv run --script skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py inputs --output outputs/plantuml --colorset colorset2 --format svg --format png --engine kroki --report outputs/plantuml/report.json
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report outputs/plantuml/report.json --output outputs/plantuml --colorset colorset2 --expected-diagrams 3 --expect-format svg --expect-format png > outputs/plantuml/validation.json
```

Required outputs:

- `outputs/plantuml/report.json`
- `outputs/plantuml/validation.json`
- `outputs/plantuml/svg/sequence.svg`
- `outputs/plantuml/png/sequence.png`
- `outputs/plantuml/svg/class.svg`
- `outputs/plantuml/png/class.png`
- `outputs/plantuml/svg/mindmap.svg`
- `outputs/plantuml/png/mindmap.png`

Acceptance criteria:

- The report has `ok: true`, `colorset: "colorset2"`, `engine: "kroki"`,
  `sourceDiagramCount: 3`, `renderedDiagramCount: 3`, and
  `failedDiagramCount: 0`.
- The validation JSON has `ok: true` and `checkedDiagramCount: 3`.
- Every SVG and PNG artifact is non-empty and corresponds to its source.
