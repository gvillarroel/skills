# PlantUML Diagram-Type Coverage

Use `diagram-types.json` as the machine-readable source of truth. It freezes the 27 families in the PlantUML v1.2026.6 `Supported Diagram Types` list and adds `packetdiag` as a mandatory release-extra introduced in v1.2026.2. The acceptance surface is 28 families, 29 fixtures, and 28 published renderable variants.

| ID | Taxonomy | Fixture(s) | Directive(s) | Theme | Formats | Availability |
| --- | --- | --- | --- | --- | --- | --- |
| `sequence` | canonical UML | `sequence.puml` | `@startuml` | inject | SVG, PNG | available |
| `usecase` | canonical UML | `usecase.puml` | `@startuml` | inject | SVG, PNG | available |
| `class` | canonical UML | `class.puml` | `@startuml` | inject | SVG, PNG | available |
| `object` | canonical UML | `object.puml` | `@startuml` | inject | SVG, PNG | available |
| `activity` | canonical UML | `activity.puml` | `@startuml` | inject | SVG, PNG | available |
| `component` | canonical UML | `component.puml` | `@startuml` | inject | SVG, PNG | available |
| `deployment` | canonical UML | `deployment.puml` | `@startuml` | inject | SVG, PNG | available |
| `state` | canonical UML | `state.puml` | `@startuml` | inject | SVG, PNG | available |
| `timing` | canonical UML | `timing.puml` | `@startuml` | inject | SVG, PNG | available |
| `json` | canonical | `json.puml` | `@startjson` | inject | SVG, PNG | available |
| `yaml` | canonical | `yaml.puml` | `@startyaml` | inject | SVG, PNG | available |
| `ebnf` | canonical | `ebnf.puml` | `@startebnf` | inject | SVG, PNG | available |
| `regex` | canonical | `regex.puml` | `@startregex` | inject | SVG, PNG | available |
| `nwdiag` | canonical | `nwdiag.puml` | `@startnwdiag` | inject | SVG, PNG | available |
| `salt` | canonical | `salt.puml` | `@startsalt` | inject | SVG, PNG | available |
| `archimate` | canonical | `archimate.puml` | `@startuml` | inject | SVG, PNG | available |
| `sdl` | canonical | `sdl.puml` | `@startuml` | inject | SVG, PNG | available |
| `ditaa` | canonical | `ditaa.puml` | `@startditaa` | none | PNG | available |
| `gantt` | canonical | `gantt.puml` | `@startgantt` | inject | SVG, PNG | available |
| `chronology` | canonical | `chronology.puml` | `@startchronology` | none | none | upstream unavailable |
| `mindmap` | canonical | `mindmap.puml` | `@startmindmap` | inject | SVG, PNG | available |
| `wbs` | canonical | `wbs.puml` | `@startwbs` | inject | SVG, PNG | available |
| `math` | canonical | `math.puml`, `latex.puml` | `@startmath`, `@startlatex` | none | SVG, PNG | available |
| `ie` | canonical | `ie.puml` | `@startuml` | inject | SVG, PNG | available |
| `chen` | canonical | `chen.puml` | `@startchen` | inject | SVG, PNG | available |
| `chart` | canonical | `chart.puml` | `@startchart` | inject | SVG, PNG | available |
| `files` | canonical | `files.puml` | `@startfiles` | inject | SVG, PNG | available |
| `packetdiag` | release-extra | `packetdiag.puml` | `@startpacketdiag` | inject | SVG, PNG | available |

## Capability Rules

- Never inject PlantUML theme text into Ditaa, standalone AsciiMath, or standalone LaTeX. Ditaa treats injected text as diagram content; standalone math renderers ignore it.
- Route Ditaa through Kroki's `ditaa` endpoint, stripping PlantUML wrapper directives from the Kroki payload. Other families use Kroki's `plantuml` endpoint.
- Treat Chronology as `expected-unavailable` for the frozen v1.2026.6 gate. Keep its fixture and family ID in exact-set validation, but do not claim a rendered artifact until PlantUML restores it.
- Keep arbitrary user rendering unchanged unless `--coverage-manifest` is explicitly supplied. Coverage mode applies per-fixture formats, availability, and publication policy.
- Validate exact family IDs, fixture IDs, sources, directives, formats, duplicates, counts, and gallery assets. A matching numeric count alone is not coverage.
