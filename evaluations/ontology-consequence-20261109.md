# Deterministic consequence of reviewed Boolean rules

The `--boolean-consequence` mode evaluates a reviewed candidate against
reviewed premises. It retains the same source bindings, exact citations,
truth fingerprints and assignment regions as the symmetric comparison
mode. A satisfiable premise set can entail, refute or leave the
candidate independent. An inconsistent premise set holds for review.
The candidate and premise profiles distinguish tautologies,
contradictions and contingent formulas.

The smoke case tests a two-step rule chain. An authorized signer
suffices to approve the package signature, and approval suffices to
publish the release. The two premises entail that an authorized
signer suffices to publish the release. With only the first premise,
an authorized signer and an approved signature are compatible with an
unpublished release. The weakened result shows that assignment as a
counterexample.

| Validation | Result |
| --- | --- |
| Complete skill tests | 218/218 on Python 3.11 and 3.14 |
| Independent public CLI audit | 22/22 semantic cases and 7/7 integrity rejections across 42 invocations |
| Previous symmetric comparison artifacts | Four byte-identical replays |
| Isolated strict GPT-6 Luna low runs | Two runs reproduced both consequence artifacts byte for byte |

| Reviewed artifact | SHA-256 |
| --- | --- |
| Both premises | `ca30b298cf826e612cc1d9f368b215a74902b115b113bb2dd53b9cd77a81c6ab` |
| First premise only | `e85b4671282435f45d0259b1cf855414a4a6421a4ae9c5c57f56b60c601450bf` |

The audit independently enumerated satisfying and falsifying
assignments and checked stale source bytes, invalid citations,
atom-roster errors, inconsistent premises, candidate profiles and
cross-source identity controls. It also checked the effects of
irrelevant premises and of evaluating a bundle of candidates together.
The workflow requires a separately reviewed correspondence between
source phrases and atom IDs. The published checks qualify the
deterministic reasoning stage over those reviewed inputs.

[Consequence workflow](../skills/curate-semantic-model/references/document-versions.md#check-a-reviewed-boolean-consequence)
