# Simulation methodology review — 2026-09-06

## Scope and outcome

Reviewed the canonical simulation skill's experiment design, interval methods,
threshold decisions, and independent verification. Implemented
`mean-difference-v3`: finite-support Hoeffding-Bonferroni mean contrasts and
full-precision decision arithmetic. The bounded inventory template now uses
that method with an explicit mechanism-based support assumption. The skill
remains `validating` because the repository's real-agent forward gate is outside
the user's permitted simulation-only scope. No Pi, Copilot, local LLM, provider
API, or emulated tool was executed. LLM evaluation model: not applicable.

This is a development review using mathematical counterexamples and numerical
regression tests, not a fresh empirical study or an independent agent holdout.
The existing cost and context-rot studies were not recalibrated or rewritten.

## Demonstrated defects and changes

1. The old analyzer rounded authoritative numbers to 15 significant digits
   before deciding. For a deterministic `ge 1` claim,
   `0.9999999999999999` rounded to `1.0` and became `supports` instead of
   `challenges`. V3 uses full binary64 round-trip values. Tests also cover the
   reversed inequality and a stochastic interval endpoint adjacent to a
   threshold. This repairs formatting-induced decisions, not solver error.
2. The normal method's 30-replication and nonzero-variance guards do not provide
   coverage under rare shocks. The previous documentation warned about this,
   but supplied no executable finite-sample alternative. V3 adds a conservative
   bounded method for paired and independent contrasts, with a priori support
   and an explicit assumption link. It rejects out-of-support values, unknown
   assumptions, invalid or unrepresentable ranges, and legacy relabeling.
3. The template's demand description was ambiguous. It now specifies
   `max(0, Gaussian(mean, sd))`, including its point mass at zero; this is a
   clipped distribution, not a conditionally truncated Gaussian. The numerical
   mechanism and generated outcomes did not change.

The new compact [bounded-inference reference](../../skills/simulation-data-lab/references/bounded-mean-inference.md)
documents formulas, dependence requirements, fixed-budget precision planning,
support verification, and tradeoffs. Choosing the method after seeing which
answer it favors is explicitly excluded. Arbitrary sample extrema cannot become
population bounds. Unbounded costs, ratio/quantile estimands, clustered
replications, and sequential stopping still require another justified method.

Primary method sources: [Hoeffding's bounded-sum inequality](https://doi.org/10.1080/01621459.1963.10500830)
and [NIST guidance for intervals with few failures](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

## Exact rare-shock counterexample

Consider a hypothetical loss in unit 1, with baseline fixed at zero. The
comparison's replication outcome is 0 with probability 0.495, 0.001 with
probability 0.495, and 1 with probability 0.01. Its true mean is 0.010495.
The claim `mean difference >= 0.005` is therefore true under this model.

Freeze 32 independent pairs, a two-point family, and 95% family coverage. Audit
one point's 97.5% marginal interval. Enumeration covers all 561 distinct count
vectors and their exact multinomial probabilities, evaluated with floating-point
arithmetic. Both implementations agree on all 1,122 interval/decision results.

| Method | Actual mean-interval coverage at the audited point | Erroneous contradiction probability | Inconclusive probability |
| --- | ---: | ---: | ---: |
| Normal-Wald with Bonferroni and existing guards | 27.500698% | 72.498034% | 27.500359% |
| Bounded Hoeffding-Bonferroni | 99.999999998% | 0% | 99.999999998% |

Without the rare shock, small routine variation usually clears the normal
zero-variance guard but produces a misleadingly narrow interval. The event
"no shock, but nonzero routine sample variance" alone has probability
`0.99^32 - 2*0.495^32 = 0.7249803356202581`.

The bounded method's result is not a magically precise estimate: it is almost
always inconclusive at this small budget. The table is a conditional result for
this deliberately constructed distribution, not a measured failure rate for
agents and not a universal coverage estimate for either method. In particular,
the point's coverage must not be relabeled as measured simultaneous family
coverage. The finite-sample family guarantee comes from the bound and its
assumptions, not from this one enumeration.

- [Compact audit, distribution, and source hashes](methodology-review-20260906/coverage-audit.json).
- [Reproduction code](../../projects/simulation-methodology-review/scripts/audit_interval_coverage.py).
- Full 561-row exploration data remains locally in the ignored directory
  `evaluations/runs/simulation-coverage-review-20260906-final/sampling-distribution.csv`.

## Integration, replay, and limitations

All 63 tests pass: 20 runner, 16 normal-analyzer, 12 validator, 3 simulation-only
boundary, and 12 new bounded/numerical tests. The new suite includes 32 exact
binomial coverage configurations, analytical paired/independent radius oracles,
support and type failures, constant arms, threshold-adjacent values, and full
paired/independent bundle tamper checks.

A fresh canonical template integration completed 128/128 mathematical runs,
256 outcomes, 128 valid diagnostics, and eight summaries. An independent
skill-only copy of all 20 source files also completed plan/run/analyze/validate
from its isolated workspace without sibling or repository resources. That is a
mathematical bundle check, not an isolated LLM forward test. Both integrations
return `inconclusive-under-model`, with integrity `releaseEligible=true`.
Integrity eligibility is not statistical support or real-world validation.

The old v1 and v2 bundles pass immutable replay under their original arithmetic:

- `evaluations/runs/simulation-data-lab-local-final-20260904-1` (v1);
- `evaluations/runs/simulation-only-template-20260904` (v2).

The new canonical and isolated bundles are respectively:

- `evaluations/runs/simulation-bounded-template-20260906`;
- `evaluations/runs/simulation-isolated-math-20260906/experiment`.

All four have identical outcomes SHA-256
`33e5b27a2b27ef869712478f9a8f7c9137939df354c34c6c4e9543f35472d115`.
The new canonical report SHA-256 is
`2595285e6f76e8387b08fa0e5daf1b137ec2605241132831a5ea49fd7d09d86c`.
Historical replay preserves evidence; it does not retroactively improve old
coverage or boundary decisions.

## Reproduction and repository checks

Run from the repository root. Use a fresh output directory for each audit.
Set `TEMP` and `TMP` to a repository-local temporary directory when running
tests to keep generated files inside the authorized workspace.

```text
uv run --script skills/simulation-data-lab/scripts/test_run_simulation_experiment.py
uv run --script skills/simulation-data-lab/scripts/test_analyze_simulation_hypotheses.py
uv run --script skills/simulation-data-lab/scripts/test_validate_simulation_bundle.py
uv run --script skills/simulation-data-lab/scripts/test_simulation_only_boundary.py
uv run --script skills/simulation-data-lab/scripts/test_bounded_inference.py
uv run --script projects/simulation-methodology-review/scripts/audit_interval_coverage.py --skill skills/simulation-data-lab --output-dir <fresh-output-directory>
uv run --script skills/simulation-data-lab/scripts/validate_simulation_bundle.py --root <bundle>
python C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/simulation-data-lab
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py --source skills/simulation-data-lab --destination .agents/skills/simulation-data-lab
uv run --script scripts/sync-local-skills.py --source skills/simulation-data-lab --destination .agents/skills/simulation-data-lab --check
git diff --check
```

Repository gates, quick validation, and targeted synchronization pass. The
simulation-only boundary remains in the skill, templates, and references. No
empirical evidence gap or promotion requirement authorizes real target execution.
