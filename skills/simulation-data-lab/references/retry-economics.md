# Retry economics and dependence

Use this reference when a simulation prices retries or estimates completion
under a bounded attempt cap. Treat the following mechanisms as declared
alternatives, not empirical estimates.

## Independent and conditional attempts

For independent attempts with constant success probability `p` and at most `K`
attempts:

```text
P_complete = 1 - (1 - p)^K
E[attempts] = sum_(j=0)^(K-1) (1 - p)^j
            = (1 - (1 - p)^K) / p
```

If each attempt costs `C`, expected provider spend is
`C * E[attempts]`. Cohort cost per completed task, including spend on exhausted
failures, is `expected_spend / P_complete`. For task strata, first weight
expected spend and completion probability across strata, then divide; averaging
stratum-level ratios answers a different question.

If attempt costs or success probabilities vary, use reach probabilities:

```text
Pr(reach attempt j) = product_(h < j) (1 - p_h)
expected_spend = sum_j Pr(reach attempt j) * C_j
P_complete = 1 - product_j (1 - p_j)
```

Here `p_j` must mean success **conditional on reaching attempt j** and `C_j`
must be the corresponding conditional expected cost. Multiplying unconditional
marginal failure probabilities is invalid for dependent attempts. Use the sum
form at `p=0`; its limit is `E[attempts]=K` and `P_complete=0`. Mark cost per
completion undefined in an extension table or status field, not as a finite
core outcome or a serialized NaN/infinity.

State whether a retry rebuilds context, reuses cache, changes the prompt, invokes
a human, or pays extra latency. Independence is often optimistic because the
same missing evidence or bad summary can make every retry fail. Include
perfectly correlated failures and a conditional-recovery model as challenge
cases.

## Persistent-failure challenge

One exact, auditable dependence challenge is a persistent-failure mixture. With
probability `rho`, all planned attempts share one Bernoulli result with success
`p`; otherwise their results are independent Bernoulli draws with the same `p`.
For `0<p<1`, `rho` is the pairwise correlation of planned attempt outcomes
conditional on the task stratum, not necessarily the pooled correlation:

```text
P_complete = rho*p + (1-rho)*(1-(1-p)^K)
E[attempts] = rho*(p+K*(1-p)) + (1-rho)*sum_(j=0)^(K-1)(1-p)^j
```

Apply the mixture within each stratum before weighting. Test `rho=0`, an
intermediate value, and `rho=1`; the latter leaves completion at `p` while still
paying for all `K` attempts on failures. Reducing the cap to one attempt is not
the same cost experiment as correlated failures with three paid attempts. This
mixture is a structural sensitivity case, not an estimate of real correlation.
For an SLO `q` lying between `p` and independent completion `P_ind`, the maximum
mixture weight meeting it is `(P_ind-q)/(P_ind-p)`. Report an absent crossing
when the interval does not bracket the target.

## Verify before applying

Enumerate all binary attempt-outcome sequences for a small cap independently
of the closed-form implementation. Weight a sequence by the independent mass
plus the shared-result mass, find its first success, and accumulate completion
and paid attempts. Test `p=0`, `p=1`, `K=1`, `rho=0`, `rho=1`, and an
intermediate mixture. For `p=0.5,K=3`, independence gives completion 0.875 and
1.75 expected attempts; perfect persistence gives completion 0.5 and 2 expected
attempts. Hash and preserve the original study; write a structural challenge to
a fresh bundle with its own assumptions and provenance.
