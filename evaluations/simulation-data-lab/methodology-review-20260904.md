# Simulation Data Lab methodology review — 2026-09-04

## Scope and outcome

Reviewed and improved the canonical `skills/simulation-data-lab` bundle. The
review uses code inspection, primary statistical references, deterministic
counterexamples, regression tests, and a separate challenge to the frozen
context-rot study. No Pi, Copilot, model, or provider API was executed in this
review. The skill remains `validating`: the user expressly excluded the real
agent forward runs required for promotion by repository policy.

The central finding is that arithmetic correctness, statistical adequacy, and
robustness to alternative mechanisms must have distinct evidence. Large grids,
millions of recomputations, and a fixed seed cannot substitute for the latter
two checks.

## Findings and changes

| Finding | Consequence | Implemented response |
| --- | --- | --- |
| Zero observed contrast variance produced a zero-width normal interval and a definite decision. | A finite stochastic sample could be mistaken for population certainty. | `mean-difference-v2` retains the descriptive estimate and MCSE but makes the point inconclusive with a machine-readable diagnostic. |
| Two observations were sufficient for an automated normal-Wald decision. | Very small samples could generate fragile conclusions. | A conservative 30-replication automation floor; documentation explicitly rejects treating this floor as proof of normal coverage. |
| A search for any contradictory design point used pointwise intervals. | The declared interval level was not simultaneous coverage of the displayed family. | Bonferroni normal intervals are the new template default, with the adjusted marginal level in each interval and explicit within-hypothesis scope. Plain pointwise analysis remains available and labeled. |
| Specification hashes did not show whether settings reached the mechanism. | A faithfully recorded but unused parameter could create false sensitivity confidence. | Parameter-activation checks using perturbations and mechanism-specific oracles are now required. |
| OFAT accounting could be read as the total effect of a real intervention. | Removing a tool can change quality, retries, and later context, not just token cost. | Separate frozen accounting effects from responsive policy effects; test interactions and do not treat arbitrary grid frequencies as probabilities. |
| Planning optional stopping was not enough to justify fixed-sample intervals. | Repeated looks or candidate selection can invalidate nominal coverage. | Require sequentially valid methods or a fresh, frozen confirmation sample. |
| Required context-quality structural challenges were described but not inventoried. | A coefficient grid could be mistaken for tests of retry dependence or critical-fact loss. | Require tested/deferred/not-applicable challenge records and surface unresolved decision-critical mechanisms. Add a compact, self-contained retry-economics reference. |

The validator independently implements both analyzer versions. It rejects
removed inference diagnostics, pointwise bounds presented as Bonferroni bounds,
unsupported identities, and non-string analyzer identities. Extreme confidence
levels that round the normal quantile to one produce a domain error rather than
an uncontrolled statistics exception. The bundle envelope remains schema 1;
old compatible v1 reports are replayed without rewriting their conclusions.

The guard against zero variance is deliberately conservative, including a
constant paired difference. A model-specific analytical proof may identify the
effect despite that sample; evaluate such a proof separately rather than
relabeling a stochastic model as deterministic. Rare-event, skewed, clustered,
weighted, and ratio estimands still need an appropriate analysis method.

## Same-data regression

The old compatible 128-run inventory bundle at
`evaluations/runs/simulation-data-lab-local-final-20260904-1` and the new bundle
at `evaluations/runs/simulation-methodology-review-20260904` have identical:

- outcomes SHA-256: `33e5b27a2b27ef869712478f9a8f7c9137939df354c34c6c4e9543f35472d115`;
- runs SHA-256: `00900b91a4e2ac88042d2ceb2f68fa125eabb26d8f6b54566e8c3ea1ac740634`.

Both contain 128 valid runs, 256 outcomes, 128 diagnostics, and eight summaries.
At the low-demand challenge point, all 32 observed paired differences are zero.
V1 returned `challenges`; v2 returns `inconclusive` with
`zero-observed-contrast-variance`. The overall result is now
`inconclusive-under-model`. This changes inference, not the data or the
underlying model. An integrity audit can pass with an inconclusive result;
`releaseEligible` certifies the bundle contract, not empirical truth or adequacy
for every statistical claim.

The older strict-smoke bundle
`simulation-data-lab-contract-smoke-20260903-spark-5` was also inspected. It
predates the `time_unit` table hardening and was correctly rejected for a schema
mismatch. It was not altered. The later compatible v1 bundle above passed full
replay, including its original report digest
`933233952f1625f8fb1997c575428e9c6263c26c4d3ebee0f993f1031f611049`.

## Context-rot structural challenge

The original study's primary case assumes independent attempts conditional on
task stratum and strategy. This review holds all original quality probabilities,
costs, task weights, and the three-attempt cap fixed and changes only the retry
mechanism. With probability `rho`, every planned attempt shares one Bernoulli
outcome; otherwise attempts are independent. Within a nondegenerate stratum,
`rho` is the correlation between planned attempt outcomes. It is an assumed
sensitivity variable, not a measured agent correlation.

The frozen source is `study-results.json`, SHA-256
`edf0d43d7e4e797964be4616d2485e005e89d1fd7691cf2a5dde139d6a009cb2`.
The new script verifies that digest and refuses to overwrite its destination.
Linearity of the mixture allows combining the original stratum-weighted
independent endpoint with the weighted persistent endpoint. It does not apply
the nonlinear independent-retry transform to an averaged success probability.

For the primary Luna 200k uncached-compaction strategy:

| Assumed within-stratum rho | Completion | Provider value per completed session | Meets 95% completion target? |
| --- | ---: | ---: | --- |
| 0.00 | 96.7227% | $0.815647 | Yes |
| 0.10 | 94.6173% | $0.843933 | No |
| 0.25 | 91.4593% | $0.888805 | No |
| 0.50 | 86.1959% | $0.970899 | No |
| 1.00 | 75.6691% | $1.169347 | No |

The completion target is met only through `rho = 0.0818225423957884` in this
specific mixture. At perfect persistence, failures still pay all three attempts;
this is not economically equivalent to allowing just one attempt.

Compaction remains cheaper per completion than growing to 800k at every tested
mixture weight. The challenged conclusion is the 95% service target, not a
reversal of the provider-cost ranking in this narrow case. In particular, the
original 83.963% per-compaction-fidelity threshold for 95% completion is
conditional on independent retries and the original quality link. It is not a
generally sufficient production threshold.

The exact challenge includes 80 independently enumerated binary-sequence oracle
cases, including zero/one success, one attempt, independent, intermediate, and
perfectly persistent endpoints. It exports ten scenario rows and two SLO
boundaries. All are deterministic model-conditional calculations, not new
empirical measurements. Provider value is not necessarily incremental cash.

Artifacts:

- [Challenge metadata, equations' results, and inventory](methodology-review-20260904/retry-challenge.json).
- [Tidy retry-mixture data](methodology-review-20260904/retry-mixture.csv).
- [Reproduction script](../../projects/harness-efficiency-study/scripts/audit_context_retry_assumptions.py).

Critical-fact loss, peak-context cliffs, and changed retry prompts/cache/costs
remain explicitly deferred in this focused challenge, not silently counted as
tested. The reusable guidance now requires an explicit status for them. Real
target-model calibration remains absent and was not attempted.

## Validation commands and results

All commands run locally without model calls:

```text
python -B skills/simulation-data-lab/scripts/test_run_simulation_experiment.py
python -B skills/simulation-data-lab/scripts/test_analyze_simulation_hypotheses.py
python -B skills/simulation-data-lab/scripts/test_validate_simulation_bundle.py
python -B projects/harness-efficiency-study/scripts/audit_context_retry_assumptions.py --source evaluations/harness-efficiency-study/20260904/pi-context-rot/study-results.json --output-dir <fresh-output-directory>
python -B skills/simulation-data-lab/scripts/validate_simulation_bundle.py --root evaluations/runs/simulation-data-lab-local-final-20260904-1
```

The final suites pass 48/48 tests: 20 runner, 16 analyzer, and 12 validator.
The independent retry challenge passes 80/80 enumeration cases. A fresh
template plan/run/analyze/validate sequence completes all 128 planned runs and
passes the independent audit. The compatible historical v1 bundle also passes.
Python compilation, skill quick validation, pattern IDs, repository validation,
skill independence, payload, diff checks, and targeted local skill
synchronization are checked before handoff. No claim of a new isolated agent
runtime pass is made.

Repository gates:

```text
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py --source skills/simulation-data-lab --destination .agents/skills/simulation-data-lab
uv run --script scripts/sync-local-skills.py --source skills/simulation-data-lab --destination .agents/skills/simulation-data-lab --check
```

## Statistical references and interpretation limits

- [Morris, White, and Crowther: simulation study design and Monte Carlo error](https://pmc.ncbi.nlm.nih.gov/articles/PMC6492164/).
- [NIST exact binomial confidence limits](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm). For zero events among 32 IID Bernoulli trials, the exact one-sided 95% upper limit is approximately 8.94%, not zero. This is a single-probability illustration, not a paired-difference interval.
- [NIST Bonferroni simultaneous intervals](https://www.itl.nist.gov/div898/handbook/prc/section4/prc463.htm). Twenty independent exact-normal 95% pointwise intervals have simultaneous coverage `0.95^20 = 35.85%`. This is not the false-challenge probability of the skill's directional rule. An all-points support test has different intersection-union logic; the correction here covers the displayed interval family and a search for any contradictory point.

Bonferroni requires valid marginal intervals; it cannot repair a bad normal
approximation. Its configured family covers design points within one hypothesis,
not every hypothesis, outcome, adaptive analysis, or future study.
