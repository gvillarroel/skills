# Mermaid Diagram Coverage

Use this reference when deciding whether the styler should add class definitions or only a base-theme colorset YAML config.

## Source Scope

The supported diagram declarations are the union of Mermaid 11.16.0 syntax navigation and Mermaid's public config schema. The syntax navigation lists Flowchart, Swimlanes, Sequence, Class, State, Entity Relationship, User Journey, Gantt, Pie, Quadrant, Requirement, GitGraph, C4, Mindmaps, Timeline, ZenUML, Sankey, XY Chart, Block, Packet, Kanban, Architecture, Radar, Event Modeling, Treemap, Venn, Ishikawa, Wardley, Cynefin, and TreeView. The config schema also exposes the Railroad family. Treat beta declarations such as `venn-beta` as supported source types even when a local renderer is older.

## Class Definition Support

Add Mermaid `classDef` lines only for these declarations:

| Family | Declarations | Classable objects |
| --- | --- | --- |
| Flowchart | `flowchart`, `graph` | Nodes and edge IDs referenced with `class` or `:::` |
| Swimlanes | `swimlane-beta` | Flowchart-style lane nodes and edge IDs |
| Class diagram | `classDiagram` | Class nodes referenced with `cssClass`, `class`, or `:::` |
| State diagram | `stateDiagram`, `stateDiagram-v2` | Named states; do not target start/end markers or composite internals |
| Requirement diagram | `requirementDiagram` | Requirements and elements |
| Treemap | `treemap-beta` | Tree nodes using `:::class` |

For all other declarations, style through the base theme variables only. Do not add class definitions to Sequence, ER, Journey, Gantt, Pie, Quadrant, GitGraph, C4, Mindmap, Timeline, ZenUML, Sankey, XY Chart, Block, Packet, Kanban, Architecture, Radar, Event Modeling, Venn (`venn-beta`), Ishikawa, Wardley, Cynefin, TreeView, or Railroad unless Mermaid's documented syntax adds `classDef` support later.

## Minimal Insertion Rule

For each Mermaid block:

1. Use Mermaid YAML frontmatter `config:` for the generated colorset theme.
2. Preserve existing Mermaid frontmatter, merge the generated colorset config into it, and replace only previous generated colorset config sections.
3. Preserve existing non-colorset Mermaid directives. Migrate previous generated colorset `%%{init: ...}%%` directives to YAML frontmatter.
4. Detect the diagram declaration after frontmatter, directives, and comments.
5. Detect referenced color classes from `:::class`, `class target className`, and `cssClass "target" className`.
6. Insert `classDef` lines only for referenced supported color classes and only when the diagram declaration supports class definitions.
