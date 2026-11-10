# Native preflight for a separate Harbor verifier

The dataset authoring skill now routes authors to a reference-solution
trial through the native executor and separate verifier before model
inference. The check covers the verifier build context and entrypoint,
Linux shell line endings, artifact transfer and full reference credit.
Missing evaluator resources are classified separately from incorrect
submissions.

Two Power Automate Harbor comparisons exercised this path through
separate Docker actor and verifier environments. Each passed eleven
local and Docker controls and a native reference replay with inference
and authentication disabled. These runs established that the actor's
artifacts reached the verifier through the declared mount.
[Product catalog protocol and receipts](../ontology-product-catalog-20261110.md)

## Isolated skill check

The [synthetic prompt](../pi-prompts/harbor-native-verifier-preflight.md)
describes a host reference check and an actor image build without a
native verifier run. The frozen six checks require the decision to
hold model execution, use a zero-model native reference run, verify
the separate verifier build context and its inputs, check shell line
endings, observe artifact transfer and full reward, and classify
missing verifier resources as infrastructure failures.

Each row used one isolated GPT-6 Luna low attempt in strict mode.
The first and last rows used the same prompt bytes. The intermediate
prompt explicitly requested the linked reference.

| Variant | Strict runtime | Reference read | Checks met |
| --- | ---: | ---: | ---: |
| Reference update alone | 1/1 | No | 3/6 |
| Reference update with explicitly requested read | 1/1 | Yes | 6/6 |
| Final skill with reference linked at the verifier step | 1/1 | Yes | 6/6 |

The initial run proposed a native reference test and a separate
verifier but omitted the zero-model condition, context and input
details, and LF check. The final run issued four tool calls with
zero errors and produced the requested artifact. Eleven planner
and report consolidator tests passed. This is one synthetic
development task, with one observation per condition.

```sh
uv run --script scripts/run-pi-skill-eval.py harbor-author-evaluation-datasets \
  --prompt-file evaluations/pi-prompts/harbor-native-verifier-preflight.md \
  --mode json --strict --model github-copilot/gpt-6-luna --thinking low \
  --run-id harbor-native-verifier-preflight-repeat --timeout-seconds 180 \
  --expect-output preflight-decision.json \
  --expect-output-json-field 'preflight-decision.json::release_now=false'
```

| Local receipt | SHA-256 |
| --- | --- |
| Reference update | `4adafb5a9809c141da993e7adf9ac89e06f492857b9bcbe2725ec3546df5de99` |
| Explicit reference read | `0b868b87ffc59fb87f14320e16c3b4f8733c56987dc10009261ca2bdcf4f05c6` |
| Final routed skill | `aa28ed087993ec5a4402531561b755fa4524d145f2a40959271c606071f125a7` |
| Final decision artifact | `ea18b949b0992756cac45f3c27b6106ea8d1e609cd4233b88d038968950fcda6` |
