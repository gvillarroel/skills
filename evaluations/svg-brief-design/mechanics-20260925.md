# SVG Brief Design: construction-mechanism follow-up

Status: complete, keep baseline. Three proposals produced 30 native
development trials; all were evaluable and technically valid, with no execution
errors or retries. None qualified to replace the original guide.

| Complete evolution-set candidate | Mean visual similarity | Change from original |
| --- | ---: | ---: |
| Original guide | 0.634608 | — |
| Proposal 2: shared anchors and relationship checks | 0.595336 | -0.039272 |

Proposals 1 and 3 failed their matched three-case filters. Proposal 2 passed
its initial filter, but regressed on five of six cases in the complete-set
comparison. The fixed GEPA selection retained the original bundle. Validation
and holdout therefore remained unopened; their outcome is unavailable, not a
failure score. These scores must not be compared with the preceding campaign's
different six-task cohort as if that were a performance improvement.

All 30 exact-model, input-isolation, allowed-tool, provenance, and bundle-integrity
checks passed. Recorded native usage was 127,253 tokens; reflection used 11,493
tokens. USD cost remains unavailable. The canonical and installed skill were
not modified by this campaign.

Manual review covered the exact complete-set native outputs. The proposed
guide made the inventory label more legible, while its similarity score fell;
the spacecraft-like silhouette and some diagram relationships also drifted.
This demonstrates why the visual proxy does not establish semantic correctness
or general design quality. The observation did not change rewards, selection,
or the frozen stopping rule. No further mutation was run after this follow-up.

This is one additional bounded campaign after the completed
[six-proposal GEPA study](gepa-20260925.md). Its visual review showed that broad
paraphrases preserved construction defects. The new hypothesis is that compact
planning with shared geometric anchors, coherent proportions, and explicit
relationship checks can improve the output. Reflection is instructed to make
one or two linked procedural changes, without examples, coordinate recipes,
task lookup tables, reference shapes, or SVG source.

Six additional development tasks, one per existing development family, were
chosen before any new inference using minimum SHA-256 of
`svg-gepa-mechanics-v1|id`, excluding the previous six tasks. Their natural
briefs and technical contracts are unchanged. Prior observations are declared
discovery exposure. The unchanged original guide is freshly measured on this
cohort; results will not be pooled with the previous study's different cohort.

The same unopened validation and holdout sets remain isolated from reflection.
There are at most three proposals and 42 development metric calls. Independent
validation and holdout retain three attempts per task and side, the original
+0.015 gain gates, technical validity, and provenance requirements. At most
72 new native trials are authorized by this protocol. No old outcomes are
retried, substituted, or discarded. A failed gate ends this follow-up with the
baseline preserved; private feedback must not guide further mutation.

The working Harbor/GEPA adapter, model, medium reasoning, SSE transport,
sanitized feedback, verifier 1.1.0, reward weights, and skill-file scope remain
unchanged. The thin launcher is digest-bound in the new protocol. It starts
outside the repository, although the dependency still scanned Git metadata
from its package location. That read-only query completed after an initial
delay; no process was terminated or native trial retried. Both the dry run and
environment doctor passed before native inference.

Evidence root: `evaluations/runs/svg-brief-design-mechanics-20260925/`.

- `protocol.json`: complete prospective declaration, task hashes, parent result
  digests, launcher digest, boundaries, budgets, and stopping rule.
- `evolution-async-compatible.json`: the registered native configuration.
- `async-compatible-execution-seal.json`: unchanged runtime component digests.
- `run-async-compatible/`: all native evidence and the frozen keep-baseline decision.
- `audit.json`: completed provenance, exact-model, integrity, artifact, and usage audit.
- `review-development-pool/development.jpg`: reference, original guide, and
  complete-set proposed guide; `manifest.json` binds the exact scored artifacts.

Read progress without opening private outcomes:

```powershell
uv run --script projects/svg-brief-design/scripts/gepa_status.py --study evaluations/runs/svg-brief-design-mechanics-20260925
```

The canonical skill remains the original three-file guidance bundle. The study
is closed without promotion. Independent generalization and unforced routing
remain unverified; the registry retains `validating` status.
