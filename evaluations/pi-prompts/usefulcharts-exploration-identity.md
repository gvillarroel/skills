Use the supplied UsefulCharts-style skill to compare the two BSD posters in `input/manifest.json`. Read `skills/usefulcharts-style/references/visible-discovery.md`, then actually view all six listed PNGs and the supplied source inventory. The identifiers are neutral and convey no quality or chronology. Do not browse, change inputs, or read external project material.

First bind your visual observations to each candidate. Its review sheet prints a neutral identifier above the unchanged chart image. Report the exact whole/detail paths, the identifier you actually see, the chart's own main title, and a distinctive description of its layout. Do this for both candidates before choosing a preference. Keep that mapping consistent throughout the result; if uncertain, reopen the images. A preference for the wrong identifier is invalid even if the criticism is useful.

Write exactly `review.json` and `review.md` at the workspace root. Compare image ownership, connected reading paths, semantic color and visual rhythm. Choose the candidate that better supports exploration, or neither. Describe three source-answerable reading routes in the chosen candidate, using tracing and comparison, with the question, supported answer, visible steps and any detached lookup needed. Keep lineage and code contribution distinct. Describe remaining weaknesses in both candidates and a concrete next repair. State what remains unverified about the reference target and knowledge density. Do not invent measurements, completed visual paths or blinded indistinguishability.

Use this JSON shape:

```json
{"candidate_inventory":[{"id":"...","visible_id":"...","whole_path":"input/...","detail_path":"input/...","main_title":"...","layout_fingerprint":"..."}],"preferred_id":"CEDAR|MAPLE|neither","comparison":{"image_ownership":"...","paths":"...","color":"...","rhythm":"..."},"routes":[{"question":"...","answer":"...","steps":["..."],"operation":"trace|compare|time"}],"remaining_weaknesses":{"CEDAR":["..."],"MAPLE":["..."]},"next_repair":"...","reference_target":"pass|not-established|fail","reference_density":"pending|verified|failed","evidence_boundary":"..."}
```

The Markdown should explain the result naturally using the same identifiers. Treat process success, correct candidate identity, source accuracy and aesthetic judgment as separate outcomes. Keep the copied skill read-only.
