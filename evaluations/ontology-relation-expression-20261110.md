# Relation expression projection and open evidence retrieval

This development study separates the roles expressed by a source,
the direction required by the ontology, and the evidence that
supports the resulting claim. The GitLab inventory previously
confused the operation waiting on a prerequisite with the operation
that causes the delay. Descriptive relation IDs reduced inversions
and left that error in both retained repeats.
[Prior relation and evidence transfer](ontology-evidence-transfer-20261110.md)

## Project from source roles

The experimental projector accepts either ontology-ordered roles or
source-ordered roles with an explicitly approved expression form.
The scope declares whether each form keeps or swaps the two endpoints.
For example, a source expression of the form “deploy waits for the
optional test” places the waiting operation first. Its declared inverse
form yields the ontology edge from the optional test to deploy start.

The projector requires one decision per scoped opportunity. Supported
decisions supply evidence for the relation and separately name every
required guard. Refuted decisions retain a reason and citation, and
insufficient decisions retain a question. Both remain outside the
asserted graph. The review record preserves the submitted role order,
the expression form, and the distinction between relation and guard
citations. The assertion plan carries the unique cited source ranges.

The independent command-line audit passed **55/55 controls** on
Python 3.11 and **55/55** on Python 3.14. Reports were byte-identical
with no skipped controls. The GitLab replay projected the reviewed
dependency expression and a direct artifact-supply relation. Both
bound to exact source text through the published materializer.
Equivalent direct and inverse submissions produced the same assertions.
Controls covered invalid forms and endpoints, missing or empty guards,
malformed locators, order permutations, and existing output targets.
[GitLab optional dependencies at the pinned revision](https://gitlab.com/gitlab-org/gitlab/-/blob/0e842e9d238cd11398afe923838497280fdd5dd7/doc/ci/yaml/needs.md#L483-489)

The projector checks the shape of the locator and guard data. The
materializer resolves source IDs and line bounds. The audit replaced
the citation for the absent-prerequisite branch with a valid exact
line about the test that always exists. Both tools accepted the
locator, and independent review found the passage insufficient for
that guard. The tools preserve what was cited for subsequent semantic
review.

## Use declared OWL direction

A separate authority probe checked 11 mappings against pinned PROV-O,
its inverse extension, and SOSA modules. Six resolved as inverses, one
kept the direction by identity, and four remained unproven. Results
matched byte for byte on Python 3.11 and 3.14. The resolver followed
declared inverse and equivalent object properties and retained the
axiom path and module for each result. A two-inverse chain kept the
direction. Synthetic controls retained ambiguity when both parities
were reachable.

The PROV-O core annotation that names an inverse did not authorize a
swap. Including the separate PROV-O inverse extension supplied the
axiom for that mapping. An independent OWL RL cross-check reproduced
the positive direction results and confirmed that subproperty
entailment in one direction did not establish equivalence.
[OWL 2 inverse object properties](https://www.w3.org/TR/owl2-syntax/#Inverse_Object_Properties) ·
[PROV-O core](https://www.w3.org/ns/prov-o.ttl) ·
[PROV-O inverse extension](https://www.w3.org/ns/prov-o-inverses) ·
[SOSA ontology](https://www.w3.org/ns/sosa/sosa.ttl)

Direct and source-ordered plans for the canonical replay reproduced
the same asserted graph and evidence files on both Python versions.
The first replay reproduced the asserted graph alone. Fresh blank
node labels in the merged ontology changed its byte digest and the
evidence ledger. Canonicalizing the merged test ontology stabilized
both. The ontology pin in the ordinary materializer still identifies
the exact supplied bytes.
A separate RDFC-1.0 probe produced the same canonical bytes for RDF
datasets whose triples were reordered and blank nodes renamed.
Removing the inverse axiom changed the canonical fingerprint.
These checks establish artifact identity under the tested
transformations. OWL direction and the source's support for a claim
are evaluated separately.
[W3C RDF Dataset Canonicalization](https://www.w3.org/TR/rdf-canon/)

## Open retrieval and selective evidence review on Flask

The transfer used six complete official Flask 3.1.2 documentation
files pinned to one Git commit. Each file matched its GitHub blob ID.
A lexical ranker generated 310 overlapping windows from 48,263 source
bytes. Rankings were byte-identical on Python 3.11 and 3.14. Whole-corpus
BM25 selection recovered the complete reviewed witness for 3/6
questions at 600 characters, 4/6 at 1,200, and 5/6 at 2,400.
The fixed 2,400-character pool generated up to 12 single-window
and two-window options per question, each limited to 1,200 characters.
The resulting candidates contained a complete witness for five of
the six questions. The separate scoring oracle supplied no windows
to the retriever.
[Flask 3.1.2 pinned documentation tree](https://github.com/pallets/flask/tree/2c1b30d0503cfb064f1cb252e6614a06915a362a/docs)

The same frozen candidate options fed both review paths. The selective
path used the previous V50 local entailment model and unchanged
thresholds. A local decision required the direct, contrast and joint
scores to select the same option and all meet or exceed their respective
thresholds. Every other question went to GPT-6 Luna low. The local
model scored 276 pairs, with at most 295 input tokens in a pair.
Both Harbor arms used one attempt and zero retries. The five cases
present in both Luna prompts had byte-identical option sections.

| Outcome | Luna on all cases | Local entailment with Luna referral |
| --- | ---: | ---: |
| Strict native admission | 1/1 | 1/1 |
| Correct complete decisions | 5/6 | 6/6 |
| Local acceptances | 0 | 1 |
| Incorrect local acceptances | 0 | 0 |
| Cases sent to Luna | 6 | 5 |
| Luna prompt characters | 44,092 | 35,463 |
| Observed Luna input tokens including cache | 26,477 | 32,789 |
| Observed Luna output tokens | 810 | 963 |
| Observed Luna cost | $0.002108225 | $0.002010990 |

The missing witness concerned manual test request contexts. The
retriever found an example that explicitly invokes
`app.preprocess_request()` and missed the nearby statement that creating
the context alone runs no dispatch and calls no `before_request`
handlers. The all-Luna response treated the example as sufficient.
The referred response identified the missing statement and withheld
the claim. The manual semantic review confirmed the exact-witness
scores. The selective prompt was 19.6% shorter. The observed token
counts still rose in the selective trial, and its observed provider
cost was slightly lower. One run per arm on one source family leaves
repeatability and broader cost effects open.
[Flask testing context at the pinned revision](https://github.com/pallets/flask/blob/2c1b30d0503cfb064f1cb252e6614a06915a362a/docs/testing.rst#L309-L319)

## Paired Ansible and GitLab development trials

The fresh Ansible fixture had ten decisions across handler activation,
tag inheritance, delegated fact attribution, and file transfer.
It contained five supported, three explicitly refuted, and two
insufficient scenarios. The supplemental GitLab family contributed
five previously developed decisions. Both arms used the same scenarios
and supplied evidence passages. Each arm ran two GPT-6 Luna low
attempts on Harbor 0.18.0 with zero retries. Local and Docker
preflights checked 25 controls, including actor isolation.
[Pinned Ansible guides](https://github.com/ansible/ansible-documentation/tree/06ea6cf03e532c8d9eaf59d6378a5375ca4e798a/docs/docsite/rst/playbook_guide) ·
[Pinned Ansible modules](https://github.com/ansible/ansible/tree/fd540eda9f96783955b227e84e229ca51f041cae/lib/ansible/modules)

All four original files passed the projector and all four traces
met the trace contract. Exact-window admission was 1/2 in the
ontology-order arm and 0/2 in the source-order arm. Three files
merged two supplied passages separated by one verified blank line.
A diagnostic split the merged citations back into their supplied
windows and preserved the graph bytes. Complete exact decisions
across all four files were 13/30 versus 17/30 on that diagnostic.
The strict native full pass remained 0/2 in each arm.

A separate reviewer received all four raw projections without the
arm key and accepted semantically sufficient alternative citations.
The two arms had 25/30 and 29/30 complete decisions. Both had 19/20
on Ansible. Each cited an exact passage about loops in one Ansible
case where the applicable claim concerned an ordinary unchanged
task. The aggregate difference came from a GitLab run that mistook
the endpoint roster for a direction claim and asserted edges under
inactive or unknown conditions.

### Follow-up with passage identifiers

A new frozen protocol replaced manually copied coordinates with
case-local passage IDs. The adapter reconstructed the original
locators before invoking the same projector. Thirty-three local
and Docker controls passed, including byte-equivalent projection
of the approved decisions under both carriers.

| Result, two new attempts per arm | Ontology order | Source order |
| --- | ---: | ---: |
| Final files using valid passage IDs | 2/2 | 2/2 |
| Strict native admission | 1/2 | 2/2 |
| Native full pass | 0/2 | 0/2 |
| Complete exact decisions in admitted runs | 9/15 | 13/30 |
| Complete independently reviewed decisions in admitted runs | 15/15 | 29/30 |
| Complete independently reviewed decisions across final files | 30/30 | 29/30 |
| Correct expected positive directions across final files | 16/16 | 15/16 |

One ontology-order run generated invalid JSON and three tool errors
before repairing the artifact. The final-file diagnostic retains
its 15/15 independent semantic result. The strict counts exclude it.
The source-order error projected the Ansible fetch from controller to
managed host after citing the reverse flow. The first experiment's
semantic advantage did not recur. Exact joint decisions tied at
13/30 across final files even though independent review accepted
additional evidence sets. Both protocols test interpretation of
supplied passages on development cases. The experimental projector
and retrieval routes remain outside the default skill workflow.
[Pinned Ansible fetch reference](https://github.com/ansible/ansible/blob/fd540eda9f96783955b227e84e229ca51f041cae/lib/ansible/modules/fetch.py)

## Receipts

| Local artifact | SHA-256 |
| --- | --- |
| Source-role projector | `abc33678cf1384b1de4f933322f0174579b7cb7e35ef24c2d506b6c45c76ca70` |
| Independent projector audit, both Python versions | `e46d3cca1cc6b41cb3318d775ba03c2c36600459014d2d050095a37d3dd47524` |
| PROV-O and SOSA source lock | `100051cd03ff1c7183a2a39d728140337a1883fc7cf829911ba9f9b1d7bbfa18` |
| OWL direction audit, both Python versions | `dc51fd13a6180f4fe54c44e681e405681d6909768823d714c678a76f18c6b324` |
| Independent OWL RL cross-check | `9fa393aa39b3f4b52db95bb1f33b8ef2fe877cc07dcdcc9b25132bd2ce3ca2f1` |
| Direct and inverse canonical replay, both Python versions | `1e29bad8961538d7728c6e59b725269b5ce9bcca3a7daccac77ce35486d09f49` |
| RDFC-1.0 replay | `78e0e18ceb1924d8512d131c582dff3e8644447548f7431fa7bec558ff150ba4` |
| Flask actor source freeze | `547c7833aaa1da0be65cdf84db62f38588ffbee0a32d2ffad53b0e607e1e15a3` |
| Flask corpus-wide ranking, both Python versions | `0bb9b8cd29f540299917978b907c9904576d14bcff7b3b3affef4e6923189aa8` |
| Flask study protocol | `1c5378457ec5d2f8a1dda4727fc2163443911ab433da5d991a7db6057a91b7e6` |
| Flask local entailment scores | `d558690d6754669c116d0ec1073f56c6e705bae57e260bdb8ff83c3fe8d500b3` |
| Flask native protocol | `a9b0289a60a765ed46595d7db0f988c12a0b7b21087a4362245c8b400c42cf48` |
| Flask paired decision comparison | `c77c187521c1c36bf3e270990c1f46526c023127fa6a9b948d137684731696ce` |
| Flask manual semantic audit | `f3349a6aca461f8360dac066f8e15e6feb3868395c5823f6aa81dc1c6312266e` |
| Ansible actor freeze | `79689aa388806977afbc007e8653d09fe7a7af6bac3d92b2156d3e0740e1404d` |
| Original Ansible and GitLab native protocol | `bc85db24bae3fcb4f9652b713311f4c47bd74dfd4349aad13cad4aa6a7cc98ff` |
| Original native comparison | `30a32487771c2abf12797536dd7be78347d726bce26162a6f10bf2e63ef7a9ba` |
| Blank-line citation replay | `d6d972438b1946651fcc1aed926a019d2936292b1ef60f5369e626fe2f475cda` |
| Original blind semantic audit | `5ecc515ff9510deecd2da8384d77b20f14903756c200626e53aafcc5ef4f80b6` |
| Passage ID protocol | `3abf9616bbae3b806d5d34a695a486b4a4acbb265edda7f2c7a4a55cd6873798` |
| Passage ID native comparison | `51348c55d8063597495f0249d9b1d3e35f3682a4d44c4a32cfd002799b137e45` |
| Passage ID blind semantic audit | `b0906c952dee9b68dc255706b88fbd6727765038cacfc82dec7e7d623ef9e9e4` |
