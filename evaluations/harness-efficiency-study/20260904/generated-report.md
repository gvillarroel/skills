# Harness efficiency simulation report

All numerical comparisons below are conditional on the declared synthetic mechanism, parameter ranges, and rate-card snapshot. They are not empirical proof that one harness is better on real repositories.

## Study-level summaries

### controlled-harness

Displayed cohort: `primary` design points.

- `pi-cli-copilot-route`: acceptance 0.204; provider ledger $10.1810/task; marginal cash $10.0329/task; allocated cash $10.1629/task; economic loss $126.40/task; wall time 1636.5 s/task.
- `pi-cli-openai-api`: acceptance 0.204; provider ledger $10.1810/task; marginal cash $10.2663/task; allocated cash $10.2663/task; economic loss $126.50/task; wall time 1636.5 s/task.
- `copilot-cli-copilot-route`: acceptance 0.248; provider ledger $10.2336/task; marginal cash $10.1187/task; allocated cash $10.2487/task; economic loss $125.02/task; wall time 1625.6 s/task.

### monthly-economics

Displayed cohort: `all` design points.

- `pi-copilot-proplus-auto`: acceptance 0.260; provider ledger $10.4191/task; marginal cash $8.6710/task; allocated cash $9.2012/task; economic loss $133.32/task; wall time 1676.9 s/task.
- `pi-openai-api-auto`: acceptance 0.260; provider ledger $10.4191/task; marginal cash $10.5067/task; allocated cash $10.5067/task; economic loss $134.62/task; wall time 1676.9 s/task.
- `copilot-proplus-auto`: acceptance 0.253; provider ledger $10.4867/task; marginal cash $8.7633/task; allocated cash $9.2935/task; economic loss $135.30/task; wall time 1716.4 s/task.

### usage-policy

Displayed cohort: `primary` design points.

- `resource-aware-frontier`: acceptance 0.236; provider ledger $9.0238/task; marginal cash $9.0975/task; allocated cash $9.0975/task; economic loss $120.03/task; wall time 1584.8 s/task.
- `resource-aware-phase-routing`: acceptance 0.231; provider ledger $8.6997/task; marginal cash $8.7734/task; allocated cash $8.7734/task; economic loss $120.18/task; wall time 1589.8 s/task.
- `resource-unaware-frontier`: acceptance 0.242; provider ledger $26.8064/task; marginal cash $26.9049/task; allocated cash $26.9049/task; economic loss $145.58/task; wall time 1916.5 s/task.

## Preregistered hypotheses

### controlled-harness

- `h-pi-copilot-normalized-cost`: **challenges-under-model**; challenge reversals: challenge-cold-prefix-churn, challenge-hot-stable-prefix, challenge-pi-favoring-minimal-loop, challenge-tool-registry-sprawl, challenge-unreliable-tools.
- `h-pi-copilot-quality-noninferior`: **challenges-under-model**; challenge reversals: challenge-copilot-favoring-diverse-tools, challenge-hot-stable-prefix.
- `h-provider-route-ledger-equivalence`: **supports-under-model**.
- `h-provider-route-marginal-cash`: **supports-under-model**.
- `h-real-world-best-harness`: **not-identifiable-from-design**.

### monthly-economics

- `h-direct-cash-without-auto-discount`: **supports-under-model**.
- `h-high-volume-subscription-marginal-cash`: **supports-under-model**.
- `h-low-volume-direct-allocated-cash`: **challenges-under-model**; challenge reversals: high-browser-low-reuse, high-feature-mixed, high-integration-cold, high-localized-hot, high-long-hot, medium-feature-mixed, medium-integration-cold, medium-localized-hot, medium-long-hot.
- `h-monthly-pi-harness-cost`: **challenges-under-model**; challenge reversals: high-integration-cold, high-localized-hot, low-localized-hot.
- `h-real-monthly-value`: **not-identifiable-from-design**.

### usage-policy

- `h-aware-cost-reduction`: **challenges-under-model**; challenge reversals: challenge-copilot-cli-hot-cache, challenge-pi-cli-hot-cache.
- `h-aware-latency-reduction`: **challenges-under-model**; challenge reversals: challenge-copilot-cli-hot-cache, challenge-pi-cli-hot-cache.
- `h-aware-quality-noninferior`: **challenges-under-model**; challenge reversals: challenge-copilot-cli-hot-cache, challenge-pi-cli-hot-cache.
- `h-phase-routing-cost`: **challenges-under-model**; challenge reversals: challenge-copilot-cli-cache-churn, challenge-copilot-cli-hot-cache, challenge-copilot-cli-unreliable-tools, challenge-pi-cli-cache-churn, challenge-pi-cli-hot-cache, challenge-pi-cli-unreliable-tools.
- `h-phase-routing-quality`: **supports-under-model**.

## Strongest preregistered counterexample

The largest threshold contradiction was `usage-policy/challenge-pi-cli-hot-cache` for `h-aware-latency-reduction`: comparison-minus-baseline 6.01838 versus the `le` threshold -0.1.

## Monthly economics boundary

Across 12 simulated monthly design points, allocated cash was lower for Copilot Pro+ in 11, for Pi with direct OpenAI API in 1, and tied in 0. Interpolation rows are emitted only when comparable points bracket a crossover.

## Decision guidance under the model

- Compare `harness × provider route × model × tool policy`; a product label alone is not an intervention.
- Minimize the visible tool registry and retained tool output while preserving every tool the task actually requires.
- Keep stable prompt prefixes and sessions within the cache lifetime; separately track cache reads and writes.
- Route model strength by phase only when quality noninferiority survives the challenge points.
- Choose subscriptions from expected monthly volume and allowance exhaustion, not from nominal token prices alone.
- Validate on matched real repository tasks with a fixed external verifier before making a production-standard choice.

## Exploration files

Use `scenario-summary.csv` for portfolio averages, `workload-ranking.csv` for task-family slices, `pairwise-deltas.csv` for preregistered contrasts, `pareto-frontier.csv` for cost/quality/time trade-offs, and `break-even.csv` for monthly-plan decisions. Each original bundle also contains `analysis/explore.sql`, `analysis/summary.csv`, a data dictionary, and replication-level outcomes.
