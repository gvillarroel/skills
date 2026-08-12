# Mermaid Palette Capacity

Use this reference for dense diagrams whose elements consume indexed or semantic color slots. The limits below are pinned to Mermaid 11.16.0. They describe the number of distinct generated style slots, not a general limit on nodes or data rows.

## Indexed slots

| Family | Capacity to exercise | Authoring consequence |
| --- | ---: | --- |
| Mindmap | 11 level-one branches plus the root | The root consumes `cScale0`; the 11 branch sections consume `cScale1` through `cScale11` before cycling. The visible capacity is 12 fills, not 14. |
| Timeline | 12 sections or unsectioned periods | The `cScale0` through `cScale11` sequence then cycles. |
| Radar | 12 curves | Curves beyond index 11 have no additional generated scale slot. |
| Treemap | 12 colored named hierarchy nodes | Mermaid's implicit parser root consumes the transparent ordinal entry. The next 12 distinct named groups consume `cScale0` through `cScale11`. If the source includes a named wrapper root, that wrapper consumes `cScale0`, so add at most 11 direct child groups before cycling. |
| Kanban | 10 colored columns | Rendered columns use classes `section-1` through `section-10`, which map to the lightened forms of `cScale2` through `cScale11`. The generated `section--1` and `section-0` rules for `cScale0` and `cScale1` are unreachable by columns in Mermaid 11.16.0. Split a wider board or add deliberate custom CSS. |
| Journey | 7 distinct sections, plus an eighth boundary section | Mermaid 11.16.0 cycles section classes through `0` to `6` because its default `sectionFills` has seven entries. Configure all exposed `fillType0` through `fillType7` variables, but expect section eight to reuse class `section-type-0`. |
| Pie | 12 slices | `pie1` through `pie12` are the complete slice scheme before reuse. |
| Venn | 8 sets | `venn1` through `venn8` are the complete set scheme before reuse. |
| GitGraph | 8 branches including the main branch | `git0` through `git7`, their inverse colors, and all eight branch-label colors must be configured together. |

The general Mermaid theme scale contains 12 entries. Configure `cScale`, `cScaleLabel`, and `cScaleInv` for all 12 entries whenever a family consumes that scale. Treemap also consumes all 12 `cScalePeer` entries.

Kanban columns and cards require stable IDs before bracketed labels. Bare multiword lines do not parse:

```mermaid
kanban
  slot01[Kanban slot 01]
    card01[Work 01]
```

## Configured and semantic slots

- The generated Sankey node map uses eight colors and cycles only after eight distinct node IDs.
- The extended XY palette contains six plot colors; the standard palette contains five. A six-series acceptance case exercises both the extended tail and standard cycling behavior.
- Quadrant and Cynefin use four and five fixed domains respectively.
- Event Modeling uses five semantic element roles: UI, processor, read model, command, and event.
- Gantt has no maximum task count. Exercise normal, active, done, critical, active-critical, and done-critical tasks instead of inventing a node limit.
- Families using `classDef` can consume the skill's nine semantic classes. Exercise every class when maintaining the styler.

For families with unlimited, uniformly styled elements, do not claim a finite maximum. Use multiple elements to prove parsing and layout, and validate every distinct visual role the family actually exposes.
