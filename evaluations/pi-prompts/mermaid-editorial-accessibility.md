Use the provided Mermaid skill to create a balanced finite-capacity review-queue overview with verified accessible title and description metadata.

Create exactly these outputs:

- `deliverables/review-queue/queue.mmd`
- `deliverables/review-queue/queue.svg`
- `deliverables/review-queue/queue.static.svg`
- `deliverables/review-queue/style-write.json`
- `deliverables/review-queue/style-check.json`
- `deliverables/review-queue/fidelity-ledger.md`

Source facts, all of which must be accounted for:

- Producers: Web, Mobile, Partner API, Batch import.
- All producers enter through Gateway.
- Gateway feeds a review queue with capacity 2 items.
- Reviewer A and Reviewer B are identical replicas; together they serve 1 item per hour.
- Reviewed work exits as Approved.
- Queue overflow exits as Deferred.
- A Metrics hook and an Audit archive are secondary operational details.

Requirements:

- Use the standard colorset1 palette.
- Use exactly these nine concept-node IDs and no others: `web`, `mobile`, `partner`, `batch`, `gateway`, `queue`, `reviewers`, `approved`, and `deferred`.
- Use these exact visible labels for those IDs, respectively: `Web`, `Mobile`, `Partner API`, `Batch import`, `Gateway`, `Review queue`, `Reviewers`, `Approved`, and `Deferred`.
- Use exactly these eight directed relations and no others: `web --> gateway`, `mobile --> gateway`, `partner --> gateway`, `batch --> gateway`, `gateway --> queue`, `queue --> reviewers`, `queue --> deferred`, and `reviewers --> approved`. Labels may clarify slot availability and overflow, but must not change the endpoints.
- Keep the literal visible facts `capacity 2 items` and `1 item per hour`. Merge Reviewer A and Reviewer B into the single visible `reviewers` cohort.
- Move both secondary items, Metrics hook and Audit archive, to the named future target `operations-detail.mmd`. Do not draw either item, invent an edge for it, or mention it in `accDescr`; the description summarizes only the settled overview.
- In `fidelity-ledger.md`, use the exact table header `Source item | Decision | Drawn as or target | Reason` and account for exactly these 12 source items once each: `Producer: Web`, `Producer: Mobile`, `Producer: Partner API`, `Producer: Batch import`, `Gateway fan-in`, `Review queue capacity: 2 items`, `Reviewer A`, `Reviewer B`, `Approved outcome`, `Deferred overflow outcome`, `Metrics hook`, and `Audit archive`.
- Mark the first six plus both outcomes `Kept`; map them respectively to `web`, `mobile`, `partner`, `batch`, `gateway`, `queue`, `approved`, and `deferred`. Mark both reviewers `Merged` into `reviewers`. Mark Metrics hook and Audit archive `Moved to detail` with target `operations-detail.mmd`. Give every non-kept row a concrete reason.
- Include useful `accTitle` and `accDescr` directives in the Mermaid source.
- Read `skills/mermaid/references/accessible-svg-metadata.md` for the exact source and rendered metadata gate.
- Style the source, then run the styler check with `--require-accessibility`; both JSON reports must show `missingStyleCount: 0`, and the check report must show `missingAccessibilityCount: 0`.
- Render a static SVG with `animate_mermaid_svg.py --animation none --require-accessibility`; the successful command must prove that the rendered SVG has a non-empty accessible title and description whose ARIA references resolve.
- Keep every generated artifact outside the copied skill directory.
- Do not search for palette templates, routing metadata, diagram-type manifests, or a skill README, and do not inspect script source. Read only `skills/mermaid/SKILL.md`, `references/diagram-selection.md`, `references/editorial-diagram-contracts.md`, and `references/accessible-svg-metadata.md`; execute the bundled scripts directly.

After writing the Mermaid source and fidelity ledger, run these commands exactly in order:

```bash
uv run --script skills/mermaid/scripts/style_mermaid_directory.py deliverables/review-queue --write --report deliverables/review-queue/style-write.json
uv run --script skills/mermaid/scripts/style_mermaid_directory.py deliverables/review-queue --check --require-accessibility --report deliverables/review-queue/style-check.json
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py deliverables/review-queue/queue.mmd -o deliverables/review-queue/queue.svg --static-output deliverables/review-queue/queue.static.svg --animation none --require-accessibility
```
