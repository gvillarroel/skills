# Model coverage and variable review

Use this review before every new simulation and revisit it after results. It is
an auditable explanation of modeling choices for the human, not private internal
deliberation and not a promise that every possible variable has been discovered.
More variables do not automatically make a model more credible: unsupported
detail can add uncertainty or obscure the decision. Aim for decision-relevant
coverage with explicit omissions, not a completeness percentage.

## Discover candidates before choosing the model

Start from the decision, estimands, population, units, horizon and constraints.
Trace each requested outcome backward through identities and mechanisms to
inputs, state and disturbances. Then scan beyond the user's named levers. Review
all eight dimensions below, proportionately; record why a dimension is not
applicable instead of inventing factors to fill it.

| Dimension ID | Questions to expose blind spots |
| --- | --- |
| `outcome-backtrace` | What determines each outcome? Is the measured proxy the actual decision objective? Which denominators or derived quantities could change? |
| `lifecycle` | What occurs before initialization, during normal work, at failure/recovery, and after termination? What relevant state crosses these boundaries? |
| `dependencies-and-feedback` | Which inputs share causes, move together, mediate an intervention or feed back into future state? What thresholds or interactions could reverse a one-factor result? |
| `heterogeneity-and-selection` | Do task, user or workload groups respond differently? Is existing evidence selected, censored, missing or transferable to this population? |
| `time-and-scale` | Are there bursts, drift, expiry, warm-up, queues, capacity limits or shared shocks? Does a monthly extrapolation preserve these mechanisms? |
| `constraints-and-accounting` | What must conserve, balance, remain feasible or stay in bounds? Are units and cost buckets consistent? Is the objective missing opportunity cost or quality? |
| `rival-mechanisms` | Could another plausible equation, distribution family, behavioral rule or causal direction explain the same evidence and change the decision? |
| `evidence-gaps` | Which inputs are assumed, weakly supported or unidentifiable? What omitted mechanism would the human most expect to change the answer? |

Write a concise mechanism sketch: equations, state transitions, or a small
dependency diagram when it clarifies the problem. Give each candidate a reason
for inclusion or exclusion. Do not describe an absent mechanism as tested because
some coefficient was swept. Existing evidence may inform candidates; missing
evidence never authorizes live target executions, benchmarks, inference calls,
or delegated agent evaluation.

## Freeze an inspectable declaration

For the bundled planner, populate
`extensions["simulation-data-lab"]["variableReview"]` in `experiment.json`.
Adapt the inventory template; do not carry its domain-specific list into a new
problem. The schema is exact: no undeclared keys. Keep the review concise (at
most 200 entries in each list, 2,000 characters per text field).

Top-level fields are `schemaVersion: 1`, `scope`, `variables`, `interactions`,
`coverageChecks`, and `openQuestions`. The scope distinguishes the calculation
actually identified from a broader human decision it cannot yet settle.

Each candidate in `variables` records:

- `variableId`: unique lowercase hyphen-case ID, at most 64 characters;
- `label`, `unit`, and `role`: `control`, `exogenous`, `state`, `derived`,
  `structural`, or `outcome`;
- `treatment`: `modeled` (represented and allowed to vary or be derived), `fixed`
  (represented but held to the stated condition), `excluded` (deliberately out
  of this model), or `unresolved` (relevance, mechanism or treatment not settled);
- `parameterNames`: exact owned scenario/design-point parameter names, or `[]`
  for an unparameterized mechanism, state, derived output, or omission;
- `affectsOutcomes`: exact declared outcome names; use `[]` only for a candidate
  relevant to the broader decision but not the current outcomes;
- `mechanism`: how it could change the answer, including equation/state linkage;
- `evidence`: assumption IDs, existing evidence paths/source IDs, transfer scope,
  or explicit absence of evidence. A familiar effect is not measured calibration;
- `decisionImpact`: `high`, `medium`, `low`, or `unknown`, assessed before
  sensitivity results. Explain plausible decision reversal, not spurious precision;
- `reason`: why this treatment is sufficient for the stated scope, or why it is
  still a gap. Being convenient to omit is not evidence of low impact;
- `nextCheck`: a concrete mathematical activation/sensitivity/structural check,
  an existing-evidence question, or an explicit scope-based reason no check is
  needed. Identify the relevant range or boundary when known.

Cover every declared parameter exactly once with matching units. Represent
shared effects as interactions, not duplicate ownership. Never vary a derived
quantity independently of its defining identity. A fixed factor can be highly
influential: document its value or mechanism and challenge its plausible range
when it could change the decision. Fixed does not mean validated or negligible.
Store numeric experimental settings in the canonical parameters, not only prose;
the exported review derives their values, units and provenance from the spec.

Each interaction records `interactionId`, `variableIds`, `treatment`,
`decisionImpact`, `mechanism`, `reason`, and `nextCheck`. Use two or more
participants for an interaction or one for self-feedback. Include dependence,
thresholds, mediation, constraints and feedback where relevant. A represented
interaction cannot include a variable declared excluded or unresolved.

Each coverage check records `dimension`, `status` (`reviewed` or
`not-applicable`), `variableIds`, and `note`. Include each of the eight dimensions
exactly once; link at least one candidate for a reviewed dimension. Record the
actual findings or scope-based exclusion, not merely "checked". `openQuestions`
contains concise questions that would refine the human's decision or uncover a
plausible missing mechanism. It may be empty if none remain identified.

Run `plan` with `--require-variable-review` for a new study. Legacy specs without
the extension remain replayable without that flag and report `not-recorded`;
do not silently upgrade their historical methodological evidence.

## Inspect the generated review with the human

The planner produces and hashes two frozen views under `design/`:

- `model-review.md`: candidate table, mechanisms, assumptions, treatment reasons,
  critical omissions, interactions, eight blind-spot checks, and human questions;
- `variable-inventory.csv`: one row per candidate keyed by `experiment_id` and
  `variable_id`. `source_type=model-review-declaration` means authored review,
  not simulated or observed evidence. `affects_outcomes_json` lists outcome
  links; `parameter_bindings_json` contains actual settings by scope and owner.
  Remaining columns mirror the candidate fields in snake_case. Import text as
  text in spreadsheet tools; the CSV is an analysis table, not executable content.

The runner checks declared links, units and coverage of declared parameters and
outcomes, then regenerates these views before model import. Missing or altered
views fail plan verification. This does not verify that the code actually uses
a parameter or that the author found an unlisted factor. Independently test
activation, dimensions, accounting identities and expected boundary responses.

The bundle validator reports `modelReview.status` separately from hypothesis
inference. `limitations-required` flags excluded/unresolved variables or
interactions with `high` or `unknown` impact. `review-recorded` is not a
completeness certificate; `releaseEligible` still concerns computational
integrity, not model adequacy. Even an accurately computed conditional contrast
may not identify the broader decision.

Do not stop on every unknown. Proceed with labeled exploratory assumptions when
the scope is clear. Ask a targeted question when a missing objective, constraint,
or material choice could redirect the problem. Show the most consequential
omissions first, and make a recommendation conditional while they remain open.

## Convert the review into mathematical challenges

First test that represented inputs and mechanisms activate. Then prioritize
plausible decision reversals: fixed assumptions, uncertain high-impact factors,
interactions near thresholds, omitted mechanisms and competing model structures.
Use the design reference for a matched sensitivity method; do not treat
one-factor changes as a global sensitivity decomposition.

Freeze two distinct interpretations when useful:

1. A controlled accounting comparison holds named mediators constant to answer
   "what is the direct change under these frozen conditions?"
2. A policy comparison propagates the intervention through dependent state,
   quality, retries and constraints. It needs those mechanisms, not just a new
   input value in an otherwise unchanged ledger.

For harness costs, use the candidate inventory and accounting-versus-policy
example in [context-quality-cost.md](context-quality-cost.md). If quality or
retry mechanisms are absent, do not generalize token savings into overall
efficiency. Check pricing and cache semantics against existing relevant evidence.

## Revisit after results without rewriting history

Author `analysis/model-review-followup.md` after the numerical analysis. It is
a required human-facing deliverable, not automatically certified by the core
validator. Include:

- links to the frozen review and actual activation/sensitivity evidence;
- which candidates and interactions were tested, untested, or not applicable,
  and why; separate predicted impact from simulated sensitivity;
- the strongest decision reversal or stability region actually checked;
- surprising outputs, failed regions, or newly recognized missing variables;
- remaining decision-critical limitations, prioritized next mathematical checks
  or existing-evidence questions, and the scope of the final recommendation.

Do not invent completed checks or quantify the probability that the inventory
is complete. A changed input, mechanism, hypothesis, or selected policy gets a
fresh spec and bundle; keep exploratory discovery separate from confirmation.
More replications cannot repair structural omissions. Conclude with what the
model can establish and what remains unknown, not an unconditional winner.

## Methodological basis

This workflow applies the distinction between verification and fitness for
purpose, lifecycle assurance, and visible assumption/decision records discussed
in the UK Government's [AQuA Book](https://www.gov.uk/guidance/the-aqua-book).
It is not a claim of formal AQuA compliance or real-system validation.
