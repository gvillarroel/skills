# Data and provenance contract

The bundled helpers provide a dependency-free core contract for Python adapters.
They produce tidy CSV data that opens everywhere and starter DuckDB SQL. For
large observations or events, add Parquet while retaining the core run, outcome,
summary, manifest, and preview surfaces.

## Bundle layout

```text
experiment/
|-- experiment.json
|-- model.py
|-- design/
|   |-- run-plan.csv
|   |-- scenario-factors.csv
|   |-- design-point-parameters.csv
|   `-- plan-manifest.json
|-- data/
|   |-- runs.csv
|   |-- outcomes.csv
|   |-- observations.csv
|   |-- events.csv
|   `-- diagnostics.csv
|-- analysis/
|   |-- summary.csv
|   |-- explore.sql
|   `-- hypothesis-results.json
|-- data-dictionary.json
|-- execution-manifest.json
`-- validation-report.json
```

The `plan` and `run` commands refuse to replace their output directories. Use a
fresh bundle for a changed spec, seed, model, or analysis rather than mixing
provenance from multiple attempts.

## Adapter interface

The model file implements equations or synthetic state transitions, not a
wrapper around target execution. It must expose concrete metadata and a one-run
function:

```python
import random

MODEL_METADATA = {
    "modelId": "queue-policy-model",
    "modelVersion": "1.0.0",
    "engine": "python-standard-library",
    "engineVersion": "3.13.7",
    "rng": "random.Random-MT19937",
    "rngVersion": "3.13.7",
    "reproducibility": "exact-within-locked-environment",
}

def simulate(run):
    rng = random.Random(run["seed"])
    # run also contains scenario_id, design_point_id, replicate_id,
    # coupling_id, parameters, parameter_units, and parameter_sources.
    # When experiment.timeUnit is declared, run also contains time_unit.
    return {
        "outcomes": {"mean_wait_minutes": 4.2},
        "observations": [],
        "events": [],
        "diagnostics": [],
    }
```

Use the installed version, never `latest` or `unknown`. Reproducibility is one
of `bitwise`, `exact-within-locked-environment`, or `statistical-only`. Do not
claim cross-platform bitwise reproducibility without testing it.
`MODEL_METADATA.engine` must exactly equal `experiment.engine.name`. Adapters
must return built-in JSON numeric values; cast scientific-library scalar types to
`int` or `float` before returning them.

Each declared outcome must appear exactly once per valid run and be finite.
Declare top-level `experiment.timeUnit` for any model that emits observations or
events. Model-returned observation rows use `sim_time`, `variable`, `value`,
`unit`, optional `entity_type`/`entity_id`, and `is_warmup`; model-returned events
use `sim_time`, `event_type`, optional entity fields, and a JSON-safe `payload`.
The runner repeats the declared unit in the generated `time_unit` column of both
tables and rejects time-bearing rows when the declaration is absent. Diagnostics use
`check_id`, `pass|warn|fail`, a message, optional numeric value/threshold, and
whether the finding invalidates hypothesis analysis. Set
`invalidates_hypotheses=true` when a failed numerical, conservation, accounting,
or structural invariant makes the run unfit for inference; its status must then
be `fail`. Keep advisory diagnostics non-invalidating.

For common random numbers, the planner gives corresponding scenarios the same
semantic run seed. Split that seed into stable, named streams before any
scenario-dependent code can alter draw counts. Use a domain-separated digest,
not Python's process-randomized `hash()`:

```python
import hashlib

def named_seed(run_seed: int, stream: str) -> int:
    material = f"simulation-data-lab/substream/v1\0{run_seed}\0{stream}".encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")

arrival_rng = random.Random(named_seed(run["seed"], "arrivals"))
service_rng = random.Random(named_seed(run["seed"], "service"))
```

Keep stream names stable across compared scenarios and make the draw-generating
mechanism scenario-invariant when the proposed pairing requires it. If scenarios
change the population or event sequence so correspondence no longer exists, use
independent seeds instead of claiming a paired contrast.

## Table grains

| Table | One row represents | Stable keys |
| --- | --- | --- |
| `runs.csv` | Planned scenario/design-point replication | `run_id` |
| `outcomes.csv` | Replication-level numeric outcome | `run_id`, `outcome_name` |
| `observations.csv` | Long-form state measurement | `run_id`, `observation_index` |
| `events.csv` | Ordered event | `run_id`, `event_index` |
| `diagnostics.csv` | Model or numerical check | `run_id`, `diagnostic_index` |
| `summary.csv` | Descriptive distribution within one design point | `scenario_id`, `design_point_id`, `outcome_name` |

Core outputs always use `source_type=simulated`. Parameter inputs retain
`assumed`, `calibrated`, `observed`, `synthetic`, or `literature`. Never mix
observed and simulated values in one unlabeled field. Use an explicit unit for
every numeric measure; use `1` for dimensionless outcomes. Interpret
observation/event `sim_time` only with its adjacent `time_unit`.

The runner preserves failed and diagnostically invalid runs in `runs.csv` and
excludes them from summaries. Empty strings are reserved for optional fields;
do not encode missing numeric values as `-999`, `NA`, or `NaN`.

## Machine-readable hypothesis analysis

Do not encode the authoritative decision only in prose. Each identifiable v1
hypothesis uses a structured mean-difference analysis:

```json
{
  "kind": "scenario-contrast",
  "estimator": "mean-difference",
  "baselineScenarioId": "baseline-stock",
  "comparisonScenarioId": "higher-stock",
  "primaryDesignPointIds": ["typical-demand"],
  "challengeDesignPointIds": ["low-demand"],
  "pairing": "paired",
  "intervalMethod": "normal-approximation-bonferroni",
  "intervalLevel": 0.95,
  "aggregationRule": "all-design-points"
}
```

The effect is always `mean(comparison) - mean(baseline)`. Every experiment
design point must appear exactly once as primary or challenge. The two roles are
disjoint, and a challenge point must have a parameter map different from each
primary point. The practical threshold is on the contrast scale:

```json
{"operator":"ge","unit":"1","value":0.05}
```

- `ge` supports an increase when the complete interval is greater than or equal
  to the threshold.
- `le` supports a decrease when the complete interval is less than or equal to
  the threshold. A reduction of at least 3 units is therefore `value=-3`, not
  `value=3`.

For a stochastic experiment, use `paired` with
`paired-across-scenarios` or `independent` with `independent-by-run`.
`normal-approximation-bonferroni` uses the declared `intervalLevel` as the nominal
family coverage over all primary and challenge points in this hypothesis. Each
exported interval records its adjusted marginal level
`1-(1-intervalLevel)/number_of_points` and a `bonferroni-v2` method suffix.
`normal-approximation` retains pointwise intervals and explicitly states the
absence of simultaneous coverage. Neither option controls error across separate
hypotheses. Both assume adequate marginal normal approximations. For a
deterministic experiment, use exactly one replication, `independent-by-run`,
`pairing=deterministic`, `intervalMethod=none`, and `intervalLevel=null`. The
result then has `mcse=0` and no interval; this does not remove structural or
parameter uncertainty.

The current analyzer ID is `mean-difference-v2`; the bundle envelope remains
schema 1. Each point adds `inferenceDiagnostics`. Stochastic points with fewer
than 30 replications or zero observed contrast variance are `inconclusive`, even
when their descriptive interval falls wholly on one side of the threshold.
Diagnostics do not invalidate the simulated measurements. Do not interpret a
zero-width empirical interval as a population bound. Resolve it with an
appropriate method or a separate exact oracle. The 30-replication rule is a
conservative automation floor, not proof that the normal approximation is valid.

The validator can replay immutable `mean-difference-v1` reports under their
original pointwise arithmetic. This preserves historical evidence; replay does
not upgrade its statistical coverage. Generate new analyses in fresh bundles
and keep their analyzer identity. Never relabel an old report as v2 or edit its
conclusions in place.

When the requested contrast is absent, declare it instead of inventing a
mechanism:

```json
{
  "kind": "not-identifiable",
  "reason": "No intervention scenario or counterfactual mechanism was supplied."
}
```

After a complete run, invoke `analyze_simulation_hypotheses.py`. It writes
canonical `analysis/hypothesis-results.json` with one estimate, interval, MCSE,
sample-count object, and status per design point. It also records input hashes,
the structured method, aggregate model-conditional status, challenge reversals,
and limitations derived from declared assumptions. Do not edit this output.

The final validator implements the paired, independent, deterministic, threshold,
coverage, aggregate-status, and challenge calculations separately and rejects
any reported number or conclusion that differs from the generated CSV evidence.
The generated `analysis/explore.sql` also defines
`v_paired_outcome_differences`, which exposes scenario-pair differences for
matching `coupling_id` values. Its column name states the direction explicitly:
`difference_b_minus_a`. Filter to the declared baseline and comparison before
interpreting it as a hypothesis contrast.

## Scaling to Parquet

Keep `runs.csv`, replication-level `outcomes.csv`, and `summary.csv` as compact
portable indexes. The bundled v1 runner and validator certify only their core
CSV inventory. For larger observations or events, use an engine-native adapter
that writes typed Parquet partitioned by low-cardinality fields such as scenario
or cohort, not by `run_id`. Define and validate a namespaced extension manifest
covering every added path, schema, hash, row count, and partition rule before
calling that extension auditable.

[Apache Arrow](https://arrow.apache.org/docs/index.html) is a language-neutral
columnar interchange ecosystem, and [DuckDB can query Parquet directly](https://duckdb.org/docs/current/guides/file_formats/query_parquet).
Avoid hiding commonly filtered scenario factors or parameter values inside JSON;
reserve JSON for sparse event payloads and namespaced extensions.

## Provenance and safety

The generated plan binds the raw and normalized experiment spec to stable run
IDs and semantic seeds. The execution manifest records model/spec/plan hashes,
engine and RNG versions, environment, timestamps, status counts, table hashes,
and row counts. The bundle audit reconstructs the plan, verifies hashes, keys,
outcomes, and summaries, and independently recomputes hypothesis contrasts.

The core runner reads, hashes, compiles, and executes the same `model.py` source
bytes directly, bypassing stale bytecode caches, and rejects source mutation
during import or execution. It does not sandbox that code or discover and hash
every imported module, native library, or external file. Review source before
import; reject target launches, network/inference clients, real agent/tool
execution, credential access, and undeclared side effects. A model that fetches
live data or runs the target violates this skill even if its output says
`source_type=simulated`. Keep adapters self-contained; prepare immutable existing
calibration inputs outside their execution path and record input hashes,
classification, licenses, and dependency locks. Integrity validation does not
certify that arbitrary Python is harmless or that the target was isolated.

The local runner also enforces a one-million-row joint materialization budget
across the plan, run records, outcomes, summaries, observations, events, and
diagnostics. Treat that as a safety ceiling, not a performance target. Use a
streaming or partitioned adapter for larger studies.

For publication-grade work, extend provenance with a lockfile or container
digest, external input identities and licenses, calibration/validation split,
analysis-code digest, protocol deviations, and optionally
[RO-Crate](https://www.researchobject.org/ro-crate/specification/1.3/introduction.html)
or [W3C PROV](https://www.w3.org/TR/prov-o/). Do not record credentials,
environment-variable values, private prompts, or sensitive absolute paths.
