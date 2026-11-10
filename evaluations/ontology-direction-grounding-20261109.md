# Source roles, scope and directed extraction

V47 compared literal citation selection with explicit recovery of
the subject and object roles. Both treatments used GPT-6 Luna low
once per cell with zero retries. Document-level relation work
motivated separate evidence-locality and endpoint checks.
[DocRED](https://aclanthology.org/P19-1074/) ·
[Eider](https://arxiv.org/abs/2106.08657) ·
[DiVA-DocRE](https://arxiv.org/abs/2409.13717)

## Initial pilot and transport diagnosis

The 16 initial cases included synthetic and pinned Argo CD excerpts.
All eight strict trials ran and returned an artifact. Both arms
scored **5/16** with the frozen exact carrier because their five
abstentions passed and their submitted display labels failed the
short endpoint ID contract.

A separate deterministic replay translated only exact unique
display labels to their approved IDs. It preserved every submitted
direction, predicate and line range. That projection yielded 8/11
correct directed edges with the literal prompt and 11/11 with
roles. Sufficiently grounded edges were 7/11 and 11/11. The actual
materializer mechanically bound all 19 submitted quotations. The
raw outcome remains the evaluation result for that carrier.

## New cases with a corrected carrier

A fresh eight-case transfer used an explicit allowed entity
roster with identical canonical IDs in both arms. The 38 controls
checked exact roster identity, malformed and ambiguous identifiers,
wrong direction, unsupported scope and insufficient evidence.
Four strict cells ran. Each output used the canonical IDs
directly. Five cases came from two pinned Kubernetes pages and
three were synthetic.

| Metric | Literal citation | Role recovery |
| --- | ---: | ---: |
| Complete case | 8/8 | 7/8 |
| Correct edge and sufficient evidence | 5/5 | 5/5 |
| Directed edge precision | 5/5 | 5/6 |
| Correct abstention | 3/3 | 2/3 |
| Shortest reviewed span | 2/5 | 2/5 |

The extra triple from the role prompt claimed a call to `SubjectAccessReview`
for default kubelet authorization. The citation correctly describes
the configured Webhook mode. The prior section establishes
`AlwaysAllow` as the default. Binding the exact line reproduced
the wrong-scope triple. This transfer gives priority to verifying
the relevant scope before interpreting endpoint roles. The role
prompt remains experimental. [Kubernetes authorization scope](https://github.com/kubernetes/website/blob/7e043a0539947ec11ef64ce3cdcc780de39c6263/content/en/docs/reference/access-authn-authz/kubelet-authn-authz.md#L38-L52)

## Deterministic scope check on the observed failure

A follow-up used the existing Boolean consequence mode from
`curate-semantic-model` on the pinned Kubernetes source. The
reviewed premises retain the default-mode condition and the
configured Webhook condition separately. The checker entails the
AlwaysAllow default and the Webhook authorization call under their
respective guards. The default-mode Webhook call is independent of
those premises. One counterexample satisfies the reviewed defaults
with AlwaysAllow active, Webhook unconfigured and no
`SubjectAccessReview` call. The converse that a call establishes
configured Webhook is also independent.

The four results qualify the reasoning step over the reviewed
source-to-formula mapping. The method gives the reviewer a concrete
assignment that separates a supported scoped statement from an
unsupported generalization.
[Boolean consequence workflow](../skills/curate-semantic-model/references/document-versions.md#check-a-reviewed-boolean-consequence)

## Local reproducibility receipts

| Receipt | SHA-256 |
| --- | --- |
| Initial raw score | `e7f832fa2bdf342d1ebdac2532bbf2ae32e0545120275920431e26b21827f073` |
| Exact-label projection | `2867c74dbb021ee4d657149b62b4162db53746d551b59928e04473250673070f` |
| Corrected-carrier protocol | `06c73418bd60f7938d6ab13d5bd78ebc03849d2e28ae2b4a708f07fb937bee95` |
| Corrected-carrier score | `0306790f2e32435dad3993c596d9c0b02f1f96dd12c0a81ede3c4f3a33e387b6` |
| Corrected-carrier materializer replay | `128290d109b653c3cdc07871df7035339e0b181431dbb14c151a8bfda44427ea` |
