# API behavior and recovery

Verified on 2026-09-18 against the existing OpenRouter PoC and live endpoint.
Use `POST https://openrouter.ai/api/alpha/decisions` with
`Authorization: Bearer $OPENROUTER_API_KEY` and a body containing `model`,
`state`, and `questions`. The runner fixes the endpoint to OpenRouter and
disables redirects. Do not substitute the normal chat-completions endpoint,
`messages`, `response_format`, or an invented asynchronous batch endpoint.

Jev's native question IDs name returned answers but do not affect inference.
Explicit instructions must select the correct state item. The runner validates
all answer IDs/types, finite ranges, full probability keys and their sum,
choice argmax, score expectation, score legend, returned model identity, and
reported usage. Rounded distributions allow small numerical tolerances.

Choice/score confidence is an upstream distribution-derived statistic; `noul`
is the probability of yes. Validation proves conformance, not semantic truth.
Nothing in the runner executes decisions as refunds, deployments, messages,
or changes to an external system.

## Failure handling

- Missing credentials, malformed inputs, schema errors, context budget failures,
  and resume identity changes stop without starting dependent inference.
- HTTP 401/403, 402, other nontransient 4xx, malformed responses and mismatched
  model/schema are not retried automatically.
- HTTP 429, 500, 502, 503, 504 and 529 retry within `attempts`, using exponential
  jitter or `Retry-After`. A wait beyond 30 seconds stops for a later resume.
- Network failures and timeouts have uncertain billing and are not retried
  automatically. A later explicit resume can charge again for an uncheckpointed
  request. Failed HTTP attempts may also be billed; their unreported costs
  remain unknown, not zero.
- In-flight requests can finish after another request fails, up to the
  concurrency limit. Their checkpoints remain available to resume.
- The output directory lock prevents simultaneous writers. After an interrupted
  process, inspect the PID stored in `.lock`; only remove that lock after
  verifying the old process has ended. Do not delete checkpoints to hide errors.
- A resume revalidates checkpoints and rebuilds outputs in source order. A
  source, path order, job or runner change refuses reuse. This is local
  checkpoint reuse, not a provider guarantee of exactly-once billing.

The final metrics distinguish accepted requests, HTTP attempts, cache hits,
reported tokens/cost and attempts with unreported cost. The byte limit and
attempt cap bound workload, but neither is a dollar budget. Use the account's
existing billing controls for a monetary ceiling; do not alter them implicitly.
Report only measured cost, and include accounting gaps when present.

## Authoritative references

- [TypeSafe API contract](https://docs.typesafe.ai/api): native questions,
  answers, distributions, and score semantics.
- [Jev 1.13 on OpenRouter](https://openrouter.ai/typesafe/jev-1.13): model
  identity, current price, and advertised context capacity.
- [TypeSafe primitives](https://docs.typesafe.ai/concepts/system-one): the
  structured decision capability and intended use.

The alpha endpoint can change. Recheck the primary references and run a small
live probe when refreshing the skill; preserve the observed provider/model
and response contract instead of silently falling back to another model.
