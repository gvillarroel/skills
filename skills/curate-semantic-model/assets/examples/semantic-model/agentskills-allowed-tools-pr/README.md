# Agent Skills allowed-tools specification change

[Agent Skills PR #283](https://github.com/agentskills/agentskills/pull/283)
clarified how the specification describes the `allowed-tools` frontmatter
field. It replaced the list wording with string wording. The field remained
optional and experimental, and support still varied by implementation.
The reviewed assertions describe the specification. This pair supplies no
evidence of an implementation or compatibility change.

| Version | Pinned specification | Raw SHA-256 |
| --- | --- | --- |
| PR base | [5e7f3e2c](https://github.com/agentskills/agentskills/blob/5e7f3e2c4c9f5464fe342bf2fea72367a914e9b4/docs/specification.mdx) | `e4d2fbcc5e1b27d57eec8184d2883177e7b807adda695c90acc44b1bf094fb25` |
| PR head | [6f92fcdb](https://github.com/agentskills/agentskills/blob/6f92fcdb78af119d41544ce667e16eb20e94de8e/docs/specification.mdx) | `2dd6ed990a1d7f3c17b99b3bad9a0308e70458915958951169a4b9c895914045` |

## Replay the comparison

From the skills repository root, run these commands in a shell with curl and
uv. Use a fresh output directory for each replay.

~~~sh
skill=skills/curate-semantic-model
example=$skill/assets/examples/semantic-model/agentskills-allowed-tools-pr
run=output/curate-agentskills-allowed-tools
mkdir -p "$run"
curl -fLsS https://raw.githubusercontent.com/agentskills/agentskills/5e7f3e2c4c9f5464fe342bf2fea72367a914e9b4/docs/specification.mdx -o "$run/base.mdx"
curl -fLsS https://raw.githubusercontent.com/agentskills/agentskills/6f92fcdb78af119d41544ce667e16eb20e94de8e/docs/specification.mdx -o "$run/head.mdx"
uv run --script "$skill/scripts/compare_document_versions.py" \
  --base "$run/base.mdx" --head "$run/head.mdx" \
  --relation-pair "$example/relation-pair.json" --output "$run/delta.json"
~~~

[Reviewed assertions](relation-pair.json) pin both source digests and cite
the field's subsection in each revision. [Expected result](expected-delta.json)
lists the affected and preserved stable roles, both graph fingerprints and the
report digest. Each predicate and object uses the namespace shown in that
file. An object replacement is represented by an addition and a removal. A
reviewer can see the previous and new wording in the cited text and verify the
three preserved facts in both relation inventories.

The two sources come from the Agent Skills project. The reviewed input quotes
unmodified lines of its specification under the documentation license. The
reviewed predicates and stable IDs are annotations for this example.
[Agent Skills documentation license at the PR head](https://github.com/agentskills/agentskills/blob/6f92fcdb78af119d41544ce667e16eb20e94de8e/docs/LICENSE) ·
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
