# Choose by the viewer's question

Select a visual grammar before a renderer. Record the semantic reason and a
rejected alternative in each panel. The following are decision aids, not quotas.

| Question / relationship | Good candidates | Space behavior and reasons to switch |
| --- | --- | --- |
| What happens next, with real branching decisions? | Flowchart, activity diagram | LR for few stages with parallel lanes; TB for deep sequence. Reject for unordered tools or categories. |
| Who interacts with whom over time? | Sequence diagram, swimlanes | Width grows with actors, height with events. Compress repeated exchanges only when faithful; use a matrix for timeless permissions. |
| What belongs inside what? | Nested containers, layered architecture, tree | Nesting communicates boundaries. Tall trees suit depth; horizontal trees suit long labels. Treemaps imply area, so use only with a meaningful size measure. |
| Which independent dimensions differ? | Comparison matrix, aligned small multiples | Shared axes and compact row labels beat repeated prose. A table is often the most honest dense diagram. |
| Which services share one mediator or capability? | Hub-and-spoke, radial neighborhood | Near-square and effective for a real hub with few peers. Do not invent a center for a distributed mesh; do not imply hierarchy from radial distance. |
| Which peers are linked, without order? | Direct node-link view, adjacency matrix | Small sparse networks favor direct links; dense networks favor matrices. Reorder rows/columns by shared groups without hiding edges. |
| What recurs? | Cycle, feedback loop | Use a ring only when the last state returns to the first. Label delay/sign/conditions if supplied; a decorative circle does not establish feedback. |
| When and for how long? | Timeline, interval lanes, Gantt | Horizontal time supports comparison; vertical time fits narrow tall space. Shared dates must share a scale. |
| How do parts connect across system boundaries? | Layered architecture, boundary map, ports | Use containment for ownership/trust, links for specified communication. Avoid turning layers into an invented execution pipeline. |
| How much, relative to a reference? | Bars, dot plots, dumbbells, bullet charts | Shared position is compact and precise. Keep units, baselines, and uncertainty. A radial gauge usually wastes space for comparison. |
| How is a total divided or transferred? | Stacked bars, Sankey, alluvial | Only scale area/width from supplied nonnegative measures with compatible units. Conserve totals; otherwise show unweighted relationships. |
| Which items overlap? | Set membership matrix, UpSet-style view, small Venn | Venn works for very few sets; intersections become illegible quickly. Do not imply proportional areas without data. |
| Where is something spatially? | Map, section, annotated schematic | Preserve coordinates or explicitly declare a schematic. Do not rearrange physical adjacency merely to fill a grid. |
| How do the panels jointly support the thesis? | Synthesis matrix, shared boundary model, dependency bridge | Explain a new combined conclusion. Do not repeat both panels or add an unexplained central box. |

Do not confuse a graph with a flowchart: a graph may describe unordered peer
relations, so arrows require an actual direction. Do not use a network for data
that is easier to compare as aligned rows. Do not use 3D for planar relationships
unless depth is part of the subject. Use specialized UML/ER/state notation when
its semantics (cardinality, state transition, inheritance) are the message.

For a multi-panel page, consistency means consistent identities and encodings,
not identical geometry. A topology, permissions matrix, and synthesis stack can
share concepts while answering different questions. Conversely, three regional
networks should often remain three aligned networks to make comparison easy.

Keep a fidelity ledger in the planning note when compressing supplied material:
facts kept, wording shortened, repeated names moved to a legend, and secondary
detail moved to a named companion. Never treat a text budget as permission to
omit qualifiers, invert direction, merge distinct entities, or invent measures.

In capability/permission diagrams, an unspecified capability is unknown. Sharing
a workspace or appearing in the same view does not grant read/write/publish
access. Preserve each named role's exact scope; for example, permission to publish
an artifact does not establish that every connected peer can read it. Use explicit
containment for requested trust/review boundaries, not just a label on another node.
