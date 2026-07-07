Use the PlantUML colorset renderer skill to create a small non-sensitive PlantUML workspace, render it to both SVG and PNG with the CS2 theme, and validate the report.

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
** CS2 theme
** SVG
** PNG
@endmindmap
PUML
uv run --script skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py inputs --output outputs/plantuml --format svg --format png --engine kroki --report outputs/plantuml/report.json
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report outputs/plantuml/report.json --output outputs/plantuml --expected-diagrams 3 --expect-format svg --expect-format png > outputs/plantuml/validation.json
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

The final report and validation JSON must both have `ok: true`.
