# Mathematical behavior and uncertainty

Use this contract when a user asks what a system should do, what can go wrong,
or how much confidence to place in simulated behavior. Execute the mathematical
representation only. No disturbance below authorizes touching a real target.

## Specify the mathematical object

Record state, policy decisions, inputs, units, outputs, and time scale. A useful
discrete-time contract is:

```text
x[t+1] = f(x[t], u[t], z[t]; theta, mechanism)
y[t]   = g(x[t], u[t], z[t]; theta, mechanism)
```

`x` is simulated state; `u` is the policy; `z` contains stochastic disturbances;
`theta` contains uncertain parameters. An algebraic, event-driven, or continuous
model can replace this form, but must expose the equivalent assumptions.
Identify the outcome unit: one request, one session, one queue trajectory, or
one whole month. Simulated tool calls are events and token counts, not commands.

## Model realistic disturbances

For each material disturbance, freeze its ID, affected state/output,
distribution or transition mechanism, parameters and units, support, occurrence
frequency, dependence, source, and rationale. Omit irrelevant disturbances with
a reason. Do not add arbitrary noise merely to make an output look realistic.

| Mechanism | Mathematical representation to consider | Assumption to challenge |
| --- | --- | --- |
| Variable demand and burst arrivals | Time-varying arrivals, overdispersed counts, or a latent normal/burst state | Constant-rate independent arrivals |
| Variable work size, token count, or service duration | Empirical resampling or a bounded/positive skewed distribution | Gaussian noise that creates negative or implausible values |
| Cache hits, expiry, and invalidation | Prefix identity, access timing, TTL state, and invalidation events | Independent cache-hit draws unrelated to workload history |
| Failures and recovery | Bernoulli hazards conditional on state, outage duration, retry state | Independent identical retries despite persistent faults |
| Shared load or environmental shocks | A latent factor affecting several quantities or correlated innovations | Independent latency, failure, and throughput draws |
| Drift and regime changes | Piecewise parameters, time-dependent rates, or a declared Markov transition model | Stationarity over the whole forecast horizon |
| Queueing and saturation | Discrete-event capacity, backlog, service, and abandonment | Linear cost/latency extrapolation beyond capacity |
| Information loss and context degradation | Task-stratum quality, critical-fact retention, and exposure mechanisms | Average fidelity standing in for every required fact |

These are candidate mechanisms, not measured facts about every system. Fit only
to existing relevant evidence, or declare assumed parameters and test ranges.
Check marginal distributions and joint/temporal behavior. Resample whole clusters
or time blocks when row-wise resampling would erase relevant dependence.

In ordinary usage, “chaos” often means variability, shocks, or unpredictability.
Do not claim deterministic chaos merely because a model has random noise.
When sensitive dependence on initial conditions is the actual mechanism, test
nearby initial states and numerical resolution separately from stochastic
replications; report a finite predictability horizon when warranted.

## Keep four uncertainty layers separate

| Layer | Question | Evidence/report |
| --- | --- | --- |
| System variability | How much would outcomes vary under this fixed model and parameter setting? | Predictive distribution, quantiles, and threshold-exceedance probabilities |
| Finite simulation error | How precisely did the numerical experiment estimate those quantities? | MCSE and a justified interval for each requested estimand |
| Parameter uncertainty | What if rates, correlations, costs, or baseline quality differ? | Outer parameter points or justified probability distributions, with provenance |
| Structural and numerical uncertainty | What if the mechanism, dependence, horizon, or solver is wrong? | Rival-model comparisons and numerical convergence checks, separately labeled |

Use independent simulation replications inside each fixed parameter/mechanism
point. Do not call a range across arbitrary sensitivity settings a confidence
interval. If parameter distributions are justified, distinguish a predictive
mixture over them from fixed-parameter behavior. A precise simulated mean is not
evidence that the underlying model is accurate.

Do not conflate process failures with simulator failures. A simulated outage or
unsuccessful task is a valid domain outcome that belongs in risk estimates. An
exception, impossible state, or broken conservation law is a model/solver error
that must fail the corresponding diagnostic instead of becoming a rare event.

## State exactly what “confidence” means

Before running, declare the estimand, unit, horizon, target precision, interval
method and level, replication budget, and family of comparisons. Use the
diagnostics reference for fixed-count, paired, small-sample, and rare-event rules.

- A P05–P95 predictive range describes the middle 90% of the modeled outcome
  distribution. It is not a 90% confidence interval for the mean, nor a bound
  guaranteed to contain all real outcomes. Its estimated endpoints have their
  own Monte Carlo uncertainty.
- An interval for a mean or probability quantifies estimation uncertainty under
  the declared sampling assumptions. A frequentist 95% procedure has nominal
  repeated-sampling coverage; it is not a 95% probability that the whole model
  is true or that the next outcome will fall inside it.
- A probability such as `P(monthly_cost > budget | model, theta)` is a modeled
  risk. Report its finite-simulation uncertainty separately and test sensitivity
  to the assumptions. Do not manufacture risk probabilities from unweighted grid
  frequencies or zero observed events.
- More replications reduce Monte Carlo error, not missing calibration, systematic
  bias, unmodeled common shocks, or structural uncertainty. Avoid a single
  unsupported “confidence score” that combines these layers.

The bundled analyzer supports mean contrasts, not every predictive quantile,
tail probability, ratio, or sequential estimator. Compute unsupported estimands
with an appropriate local mathematical analysis, preserve its code and interval
definitions, and validate an extension artifact from the replication-level data.
Do not relabel a core mean-contrast interval as a predictive interval.

## Scale the modeled system, not just the mean

Distinguish the number of operational tasks `N` from the number of Monte Carlo
replications `R`. Under fixed identical marginal means, expected total is
`N * E[cost]`, but total-risk uncertainty also depends on covariance:

```text
Var(sum_i cost[i]) = sum_i Var(cost[i]) + 2 * sum_(i<j) Cov(cost[i], cost[j])
```

Do not multiply a one-task percentile by a million and call it a monthly
percentile. Model full-month trajectories or use a justified aggregate
distribution that preserves shared shocks, workload changes, cache state, and
capacity effects. When those effects change marginal costs, even the fixed-mean
scaling assumption must be revisited.

## Required handoff

For each recommended strategy, report:

1. expected outcome and relevant predictive quantiles, with units and horizon;
2. the probability of crossing a declared cost, latency, or failure threshold;
3. MCSE/intervals for the estimated quantities, their method, and replication
   count, or why a quantity is not estimable from the design;
4. the assumptions and competing mechanisms under which the decision reverses;
5. calibration coverage and missing evidence, without attempting a live run;
6. tidy per-replication results, parameter/mechanism identifiers, units, source
   labels, and reproducible exploration queries.

Mark irrelevant outputs not applicable rather than inventing a threshold or
confidence level. Summarize as “under this model and these assumptions” and state
which uncertainty layers are quantified, only explored, or unresolved.
