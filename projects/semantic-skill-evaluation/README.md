# Native semantic evaluation maintenance

Reusable project utilities live in `scripts/`; bulky native runs and private
cohorts stay under ignored `artifacts/`. Published skill results are linked from
[the report catalog](../../docs/evaluation-reports.md).

## Deterministic projection component

The public [projection auditor](scripts/audit_catalog_projection.py) and its
[field/identity contract](catalog-projection-contract.md) are a separate
deterministic component. Its 49 tests pass, but its studied agent workflow did
not qualify for runtime-skill promotion. The complete candidate stays local;
[published results](../../evaluations/audit-catalog-projection/evolution-20261112.md)
separate structural checks from model correctness and execution errors.

## Required reward preflight

Before sealing a new study or calling its task model, run the actual packaged
canonical Oracle for every cohort and produce its owning `harbor-run-results`
final report. Check the complete reward interface against the exact frozen
schema2 trace configuration:

```sh
uv run --script projects/semantic-skill-evaluation/scripts/check_native_reward_contract.py \
  --config trace-config.json \
  --report public-oracle/final-report.json \
  --report private-oracle/final-report.json \
  --output new-reward-contract-receipt.json
```

Require exit 0 and `passed: true` for every cohort. Primary reward 1 alone is
insufficient when the later gate also requires `artifact_gate` or another named
reward. The preflight checks the canonical reports' completeness, Oracle identity,
primary contract and every declared required numeric reward. It emits only
aggregate failure counts and input digests, without private paths/case content.
The report sources must already be trusted and native-validated; this utility
does not authenticate them, score trials, repair values or replace a verifier.

Run the regression checks with:

```sh
uv run --script projects/semantic-skill-evaluation/scripts/test_native_reward_contract.py
```

The guard was added after the [invocation pilot](../../evaluations/audit-catalog-projection/evolution-20261112.md)
exposed a required-reward interface mismatch. The consumed cohort is not repaired,
rescored or reused as fresh validation. A corrected future instrument needs its
own preflight and untouched independent verification cases.

Custom-agent launchers also need a host import preflight under the exact working
directory/PYTHONPATH, verifying the intended source digest before allocating
trials. Preserve any aborted initialization trees; distinguish pending scaffolds
from actual model execution and never replace a semantic result.
