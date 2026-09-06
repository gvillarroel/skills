# Simulation variable-review methodology — 2026-09-06

## Scope and result

Skill: `simulation-data-lab`. Added a mandatory preflight variable/model review
for new studies and a human-facing post-run revisit. The workflow identifies
candidate factors beyond the user's named inputs, explains how they affect the
answer, separates represented/fixed/excluded/unresolved factors, and prioritizes
omissions and interactions that could reverse the decision.

This is skill development using local mathematical tests, not an independent
agent evaluation. LLM evaluation model: not applicable. No Pi, Copilot, inference
API, local LLM, real tool execution by a modeled agent, or live calibration was
performed. Keep the backlog `validating`: the required real-agent promotion gate
is prohibited by the user's simulation-only scope, not passed or waived.

## Implemented contract

- New studies author `extensions.simulation-data-lab.variableReview` and use
  `plan --require-variable-review`. The declaration covers outcome backtracing,
  lifecycle, dependence/feedback, heterogeneity/selection, time/scale,
  constraints/accounting, rival mechanisms, and evidence gaps.
- The planner generates `design/model-review.md` and
  `design/variable-inventory.csv` with actual parameter values, units, owner IDs
  and source classifications derived from the spec. Candidates also explain
  mechanisms, evidence, treatment reasons, impact judgments and next checks.
- The typed review rejects missing/duplicate parameter ownership, inconsistent
  units, nonexistent outcome or interaction links, unrepresented declared
  outcomes, incomplete review dimensions, malformed types and oversized lists.
  Both views are hash-bound and regenerated before mathematical model import;
  removing or rehashing a tampered view cannot bypass plan verification.
- The validator reports `modelReview` separately from statistical claims.
  `limitations-required` highlights excluded/unresolved high- or unknown-impact
  factors and interactions. `review-recorded` is not an exhaustiveness or actual
  code-coverage certificate. `releaseEligible` remains computational integrity,
  not model fitness, external validity, or permission for an unconditional policy.
- The required authored `analysis/model-review-followup.md` distinguishes checks
  actually performed from proposed work, revisits fixed assumptions and
  omissions, and links numerical evidence. Its substantive truth is not
  automatically certified by the core validator. Changed studies use fresh
  bundles; discovery is not silently reused as confirmatory evidence.
- Historical specs without a review remain byte-compatible at the plan level
  and report `not-recorded`. Their methodological evidence is not upgraded.

The compact [review reference](../../skills/simulation-data-lab/references/model-variable-review.md)
and the [context-cost workflow](../../skills/simulation-data-lab/references/context-quality-cost.md)
explain controlled one-factor accounting versus downstream policy effects. For
example, one fewer tool call may change evidence quality, future context, cache
reuse and retries; a token ledger alone cannot identify overall efficiency.

Methodological source: the UK Government's
[AQuA Book](https://www.gov.uk/guidance/the-aqua-book), particularly lifecycle
assurance, visible assumptions and decisions, and verification versus fitness
for purpose. This is not a formal compliance or real-system-validation claim.

## Cases and checks

| Case | Result | Limits |
| --- | --- | --- |
| Deterministic unit/contract regressions | 80/80 pass: 20 runner, 16 normal analyzer, 12 validator, 3 simulation-only, 12 bounded inference, 17 variable-review tests | Development tests, not an agent forward sample |
| New-study boundary/recovery | Missing required review, invalid ownership/units/references/dimensions/types, missing views, tampering and updated-hash tampering are rejected | Semantic omissions not written by the author cannot be discovered by a schema checker |
| Mathematical contract smoke | Fresh canonical plan/run/analyze/validate completes 128/128 runs, 256 outcomes, 128 passing diagnostics and 8 summaries | Inventory demonstration, not a cost or real-policy study |
| Skill-only mathematical contract smoke | All 23 source files copied into an isolated workspace; same pipeline passes with identical outcomes and generated review views | No Pi/LLM forward test, no claim about autonomous agent skill use |
| Historical replay | Immutable v1, v2 and pre-review v3 bundles pass their original analysis contracts and report review absence | Old inference is preserved, not repaired or relabeled |
| Direct artifact inspection | Read the full generated Markdown, checked candidate/outcome links, actual settings, CSV grain and follow-up limitations | No certificate that every possible factor is modeled |
| Repository checks | Pattern IDs, skill structure, independence, payload, quick skill validation, synchronization and diff checks pass | Real-runtime promotion remains unattempted |

There were no failing mathematical regression attempts. Adversarial cases
produce their expected rejections and count as successful boundary tests, not
hidden retries. The prior statistical methods and cost/context-rot studies were
not recalibrated or rewritten.

The demonstration records nine candidates, three interactions, all eight
coverage dimensions and three human questions. Four candidate omissions or
unresolved factors and one omitted interaction trigger explicit limitations.
The numerical hypothesis is still `inconclusive-under-model`, even though the
integrity check passes. This is deliberate separation of precision, model
coverage and decision applicability.

## Artifact identities

Canonical bundle:
`evaluations/runs/simulation-variable-review-20260906`.

Skill-only workspace:
`evaluations/runs/simulation-variable-review-isolated-final-20260906`, with its
generated bundle under `experiment/`. The isolated copy is an offline payload
check; source hashes are compared after execution.

An earlier passing skill-only rehearsal remains at
`evaluations/runs/simulation-variable-review-isolated-20260906`; the fresh final
copy repeats the pipeline after a readability-only manifest refactor. Both
copies are retained rather than silently overwritten.

Both bundles include the generated preflight Markdown/CSV, core data and
hypothesis analysis, validation report, and an authored post-run review. Their
raw artifacts remain ignored rather than becoming repository source.

Shared SHA-256 values:

- Outcomes: `33e5b27a2b27ef869712478f9a8f7c9137939df354c34c6c4e9543f35472d115`.
- Frozen readable review: `6be47613b00812e78e6ba7b0faed989ee1c566f91f977b57b70070567c412c30`.
- Variable inventory: `88b89d0b752722a2d412d42408209b7b7bce4ee2281e942e2de8f0179eef5cb5`.
- Plan manifest: `eb2ab0a1c77dff26db247bbfa7cc2edcbb4868a03a378fef24dc2f5b4f968eae`.

Historical replay roots:

- `evaluations/runs/simulation-data-lab-local-final-20260904-1`;
- `evaluations/runs/simulation-only-template-20260904`;
- `evaluations/runs/simulation-bounded-template-20260906`.

All five integrations/replays retain the same outcome digest above. Execution
and hypothesis-report hashes can differ between fresh runs because provenance
includes the distinct execution manifest; do not promise full-bundle byte identity.

## Reproduction commands

Run from the repository root. Set `TEMP` and `TMP` to a fresh directory under
`evaluations/runs/` for tests; use `PYTHONDONTWRITEBYTECODE=1` for read-only skill
copies. Never launch the modeled system to fill an evidence gap.

```text
uv run --script skills/simulation-data-lab/scripts/test_model_variable_review.py
uv run --script skills/simulation-data-lab/scripts/test_run_simulation_experiment.py
uv run --script skills/simulation-data-lab/scripts/test_analyze_simulation_hypotheses.py
uv run --script skills/simulation-data-lab/scripts/test_validate_simulation_bundle.py
uv run --script skills/simulation-data-lab/scripts/test_simulation_only_boundary.py
uv run --script skills/simulation-data-lab/scripts/test_bounded_inference.py
```

Copy the template spec/model into a fresh bundle, then:

```text
uv run --script skills/simulation-data-lab/scripts/run_simulation_experiment.py plan --spec <bundle>/experiment.json --output-dir <bundle>/design --require-variable-review
uv run --script skills/simulation-data-lab/scripts/run_simulation_experiment.py run --root <bundle> --model model.py
uv run --script skills/simulation-data-lab/scripts/analyze_simulation_hypotheses.py --root <bundle>
uv run --script skills/simulation-data-lab/scripts/validate_simulation_bundle.py --root <bundle> --report <bundle>/validation-report.json
```

Inspect the generated review and numerical evidence, then author the follow-up.
For legacy replay, run only the validator without overwriting old reports.
For the skill-only case, copy the canonical skill with the synchronization
helper into the isolated workspace, copy its templates into `experiment/`,
and execute the same four commands from that workspace using only the copy.

```text
python C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/simulation-data-lab
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py --source skills/simulation-data-lab --destination .agents/skills/simulation-data-lab
uv run --script scripts/sync-local-skills.py --source skills/simulation-data-lab --destination .agents/skills/simulation-data-lab --check
git diff --check
```
