# MCP Desktop PoC acceptance

Frozen October 25, 2026, before generated artifacts. Evaluate the two corresponding
`evaluations/pi-prompts/desktop-plugin-ui-poc-*-desktop.md` tasks with the current
runtime-only desktop-plugin-ui bundle. First pass: one contract-style generation
per host, each using exact expected output paths, strict JSON harness, Sol 6.1
medium under the existing Spark-unavailable exception and 900-second budget.
Retain every attempt. A source repair requires a fresh frozen subject and fresh
generation; no repaired artifact can replace the failed original.

## Independent gates

- Require strict harness, exact paths, valid JSON/zero tool errors, observed model,
  clean read surface and unchanged skill. Preserve dependency network operations
  separately; registry/docs access is allowed, extra model/provider access is not.
- Parse package metadata and locks. Independently extract archive into an ignored
  fresh project artifact folder. Validate host manifest against primary schema,
  declared entrypoint and file/cwd substitution. Launch extracted package using
  Node only with no source checkout dependency or install step.
- Execute MCP initialization, tools/list, resources/list/read and tool calls.
  Check queue_open resource association and MIME, queue_filter app-only visibility,
  exact rows/values/counts for all three filters, text fallback, invalid-filter
  refusal and unknown tool refusal. stderr/stdout remain distinct.
- In an evaluator-owned sandboxed browser bridge fixture, initialize the actual
  returned resource and deliver the actual initial result. Interact by accessible
  names. Verify drafting sends no tool call; Apply filters via direct tools/call;
  Cancel restores the committed filter/result without a call; injected request
  failure retains data/draft and Retry succeeds. No model-message/sampling call.
- Check busy/double-submit behavior, keyboard focus, readable text, English copy,
  semantic status, error recovery, no authored horizontal overflow at 320/900px,
  no console errors/runtime network, palette token ownership and contrast.
  Save screenshots and inspect them; fixture pixels are not actual host pixels.
- Review H1-H10 and architecture complexity against the real artifact, not its
  self-reported pass. Host acceptance and user testing flags must stay false.

Joint success requires all applicable gates. Correct artifacts do not erase a
strict tool error. Classify missing/ambiguous APIs or packaging as skill issues,
sampled tool mistakes as agent issues, incorrect grader expectations as validator
issues, and host/provider/network outages separately. Do not infer unsupported
host behavior from a missing live-host check.
