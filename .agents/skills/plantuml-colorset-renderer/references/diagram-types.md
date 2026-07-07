# PlantUML Diagram-Type Coverage

Use the bundled examples under `assets/examples/base/` as acceptance fixtures when maintaining this skill. Normal runtime tasks should not read those examples unless the user is explicitly asking to inspect or update fixtures.

The fixture covers one compact source for each supported family this skill validates:

| ID | Source | Diagram family |
| --- | --- | --- |
| `sequence` | `sequence.puml` | UML sequence |
| `usecase` | `usecase.puml` | UML use case |
| `class` | `class.puml` | UML class |
| `object` | `object.puml` | UML object |
| `activity` | `activity.puml` | UML activity |
| `component` | `component.puml` | UML component |
| `deployment` | `deployment.puml` | UML deployment |
| `state` | `state.puml` | UML state |
| `timing` | `timing.puml` | UML timing |
| `json` | `json.puml` | JSON data |
| `yaml` | `yaml.puml` | YAML data |
| `nwdiag` | `nwdiag.puml` | Network diagram |
| `salt` | `salt.puml` | Wireframe / Salt UI |
| `archimate` | `archimate.puml` | ArchiMate |
| `gantt` | `gantt.puml` | Gantt |
| `mindmap` | `mindmap.puml` | Mind map |
| `wbs` | `wbs.puml` | Work breakdown structure |
| `ebnf` | `ebnf.puml` | EBNF grammar |
| `regex` | `regex.puml` | Regular expression |
| `ie` | `ie.puml` | Information Engineering / ER |
| `chen` | `chen.puml` | Chen ER notation |

## Maintenance Rules

- Keep examples small and renderable through the bundled script.
- Add a new example when PlantUML adds a stable diagram family that the renderer should claim to support.
- Keep custom colors in `assets/themes/cs2.puml`; do not duplicate palette values in examples.
- Use family-specific start/end directives when PlantUML has them. `nwdiag` must use `@startnwdiag`/`@endnwdiag`; putting `nwdiag { ... }` behind a general `@startuml` can fail after theme injection.
- If a syntax family rejects general `skinparam` or `<style>` directives, update `render_plantuml_directory.py` with a family-specific injection rule and record it here.
- Validate both `.svg` and `.png` output after changing examples, theme, or renderer behavior.
