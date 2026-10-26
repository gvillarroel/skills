Use the supplied pi-durable skill to prepare the next evaluation plan for an independent event agent. Work only in this workspace and treat `skills/pi-durable/` as read-only. This is a planning task: do not implement candidates, run inference, install dependencies, start applications, inspect existing agents, contact services, or change a running study. Do not claim that proposed checks have run.

The agent watches completed build jobs, assembles release notes, and can publish an approved bundle through its fixed worker. Users can reconnect through a console or an existing conversation. Published tools expose configured destinations, permitted checks, pagination and operation outcomes to these consumers. Prompts, display metadata and worker receipt helpers may evolve; publication permissions and fixed mutation functions may not. The product promises Windows and macOS support, while the available executions were on Windows only. The active baseline has an unresolved unrelated edge case, so its name is not proof that it is safe to release for every task.

A completed development search has three paired observations on one original source snapshot:

| Pair | Baseline decision fidelity | Candidate decision fidelity | Baseline receipt coverage | Candidate receipt coverage | Baseline composite | Candidate composite |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| a | 0.88 | 0.88 | 0.00 | 0.50 | 0.44 | 0.69 |
| b | 0.92 | 0.90 | 0.00 | 0.75 | 0.46 | 0.825 |
| c, selected | 0.94 | 0.94 | 0.00 | 0.875 | 0.47 | 0.9075 |

Each arm used one fresh model completion for its whole decision batch. A successful producer build and the current safety/schema flags accompany every pair. Receipt coverage measures which observations the worker exports, not whether all configured checks ran. The table does not contain repeated decision-quality estimates, old-consumer results, native macOS results, or release-gate outcomes. Before search, an isolated unsafe worker failed a security negative control; a native faux run accepted a valid unchanged source mechanically but rejected its claimed improvement. Two retained Windows fixture-path setup failures preceded a successful fixture-only correction. No validation or holdout content has been opened. A schema/source check takes seconds, a private worker fixture tens of seconds, and a real paired model batch minutes. Those are local observations, not universal cost ratios.

Recommend what to test next and in what order before another search or activation. Include what can be learned cheaply, what needs paid or repeated model observations, controls that can expose a bad evaluator or candidate, stop conditions, and the limits of the current evidence. Leave any new tests for a new frozen protocol; this completed search must remain reproducible.

Write exactly `outputs/evolution-test-plan.json` and `outputs/priorities.md`. The Markdown should give a brief public explanation of the priorities and tradeoffs, not hidden reasoning or a transcript. Use this JSON contract; additional fields are allowed, and the number of tests or priority levels is your choice:

- `evidenceAssessment`: an object with booleans `modelQualityGainObserved`, `workerCoverageGainObserved`, `readyForActivation`, and a nonempty `claims` array. Each claim has `claim`, `basis` (`observed`, `inferred`, or `untested`), `evidence`, and `limit` strings.
- `tests`: a nonempty array of objects with unique `id`, a `target` (`model`, `worker`, `consumer`, `harness`, or `release`), a nonnegative integer `priority` (lower runs earlier; equal values may run independently), `dependsOn` (test IDs), `cost` (an object with nonnegative integer `modelCalls` and an `effort` string), `purpose`, `observableEvidence` (nonempty string array), `rejectWhen` (nonempty string array), `negativeControl` (a string, with a reason if inapplicable), and `appliesWhen`. Describe planned inference-call bounds rather than invented monetary cost.
- `studyPolicy`: an object with nonempty string arrays `mayAdapt`, `mustStayFrozen`, and `reservedEvidence`.
- `nextAction`: a concrete string describing the next authorized action and its stopping condition.

The plan must be usable independently of the skill. Preserve existing authorization and distinguish an untested condition, a demonstrated regression, and an incomplete new observation. Choose priorities from the task objective, observed evidence, consequence of failure, dependencies and local cost; do not present an unexplained universal score or weighting scheme as established fact.
