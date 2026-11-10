# Evidence-addressed decisions for a product inventory

V49 separates the caller's inventory structure from the model's
source judgments. The caller declares a product, named operations,
allowed classes and bounded directed relation candidates. The model
provides the product witness, one identity witness and one class
witness per accepted operation, and separate witnesses for any
asserted relations. An open classification requires a question.
The model can also withhold an operation or relation. A withheld
candidate contributes to review and emits zero RDF claims.

The compiler expands accepted decisions to explicit RDF types,
labels, product membership and selected edges. The published binder
checks the immutable sources and reconstructs exact citations.
The compiler checks coverage of the declared decisions, references,
graph vocabulary and evidence coordinates. Entailment, source
sufficiency and the caller's SHACL constraints have separate gates.

Typed plan compilation, slot-aligned evidence and pair-specific
relation retrieval motivated the experiment. The comparison uses
the exact same approved source corpus and relation candidates for
both workflows. It tests the use of this structure over a supplied
scope. [PlanCompiler](https://arxiv.org/abs/2604.13092) ·
[Executable Schema Contracts](https://arxiv.org/abs/2606.05415) ·
[The Alignment Bottleneck](https://arxiv.org/abs/2602.10380) ·
[Entity Pair-guided Relation Summarization and Retrieval](https://aclanthology.org/2025.findings-naacl.224/)

## Mechanical audit

The exact compiler passed 60/60 controls on each of Python 3.11
and 3.14 with zero skips. The independent audit replayed all 47
reviewed GitHub assertions across 14 sources with byte-identical
RDF and evidence, and verified the published SHACL shapes. It also
tested reordered decisions, held and undeclared relations, missing
and conflicting identifiers, invalid addresses, CRLF, BOM, and
existing output paths. An exact but irrelevant passage and a quote
above the prior task's 1,800-character limit still bound exactly.
Those are independent semantic and task-level checks.

## Paired Luna evaluation

### Zed development and path correction

Both initial arms used two GPT-6 Luna low attempts and zero retries.
The baseline overlay left the location of the review file implicit.
Both agents wrote their review to the workspace root. The native
structural result was 0/2 for the explicit plan and 1/2 for the
compiler. Exact recovery of the successful baseline writes gave
2/2 structural baseline artifacts in a separate read-only replay.
One compiler actor rewrote the generated review, which failed the
exact compiler replay gate. The original scores and artifacts remain
separate. On the restored masked packet, independently sufficient
class citations improved from 7/14 to 10/14, the required guarded
edge went from 2/2 to 1/2, and both arms had 0/2 full semantic passes.

A new protocol fixed the artifact paths explicitly in both arms
and kept the corpus, candidate and semantic wording frozen. The
path audit confirms the exact delta. Two fresh Luna low runs per
arm completed with zero retries.

| Corrected Zed result | Explicit RDF plan | Decision compiler |
| --- | ---: | ---: |
| Strict native admission | 1/2 | 2/2 |
| Strict admission and structural pass | 0/2 | 2/2 |
| Retained SHACL and structural pass | 1/2 | 2/2 |
| Correct Product-owned identities | 7/14 | 14/14 |
| Correct classes independent of ownership | 11/14 | 10/14 |
| Sufficiently cited correct classes with required ownership | 4/14 | 8/14 |
| Supported qualified edge | 1/2 | 2/2 |
| Direct questions for open mechanisms | 1/4 | 0/4 |
| Full semantic artifact pass | 0/2 | 0/2 |
| Equal asserted graphs across repeats | No | Yes |

The strictly admitted explicit run emitted seven feature self-links
in place of Product membership. The other explicit run had the
right structure but tried to publish into an existing directory.
Both compiler runs emitted the same 24-triple graph. They assigned
the same incorrect non-AI classes to language-server completion
and external formatting. The docs establish delegation and leave
the mechanisms of the selected implementations open. The ledgers
differed across both pairs of independently authored plans. Each
fixed authored input replayed byte for byte. The corrected archive
contained 5,575 and 7,430 bytes for explicit plans, compared with
2,001 and 1,921 for decision records. The compiler arm used 3,106 model output tokens compared with
5,944 for the explicit arm. The semantic gate remained unmet.

The actor-facing tool-result trace confirms both compiled Zed runs
received the shell-launch passage, the distinction between completion
paths, and the formatter boundary before writing their decisions.
The large search results did contain those passages. Their presence
did not make the model use them as the operative evidence.

### Home Assistant transfer

The independently authored public transfer fixes seven documented
operations and four relation decisions, including the reversed
precedence and two direct-provider hard negatives. The source
fixture pins seven official documents and separates the actor
workspace from the reference and adjudication. The same actor
instruction and verified publication helper ran the published
explicit path or the exact compiler path. Each arm used two GPT-6
Luna low attempts and zero retries. The 10 structural controls
passed both locally and in Docker. An actual zero-inference Harbor
boundary probe also passed.

| Home Assistant result | Explicit RDF plan | Decision compiler |
| --- | ---: | ---: |
| Strict admission and structural pass | 1/2 | 2/2 |
| Retained correct types independent of ownership | 14/14 | 14/14 |
| Correct Product-owned identities | 7/14 | 14/14 |
| Sufficient class witnesses in the masked review | 4/14 | 6/14 |
| Forward precedence edge | 2/2 | 0/2 |
| Forward edge with both required guard and direction | 1/2 | 0/2 |
| Direct question for the unresolved mechanism | 1/2 | 1/2 |
| Explicit provider denials | 4/4 | 4/4 |
| Full semantic artifact pass | 0/2 | 0/2 |
| Equal asserted graphs across repeats | No | Yes |

One explicit trial submitted competing source rosters before
recovering. Its final graph used the wrong membership predicate.
The compiler removed that structural failure in the two retained
graphs. Their ledgers still differed. All four fixed plans replayed
their graph and evidence byte for byte.

The masked reviewer found the same reverse edge in both compiler
outputs. The actor notes described the correct direction but called
it `r01`. In the shared scope, `r01` addressed built-in intent
matching → configured sentence trigger. The expected direction had
ID `r02`. The compiler followed the selected ID. A read-only
diagnostic mapped the manually confirmed endpoints back to their
declared address. It detected the mismatch in both cases. Replaying
those two reviewed address changes with the same compiler replaced
exactly one edge in each graph and reproduced the independently
reviewed reference graph byte for byte. The raw results, artifact
reviews and semantic rewards remain unchanged. This diagnostic
does not qualify the sufficiency of every citation in the replayed
graphs.
[Home Assistant sentence-trigger rule](https://github.com/home-assistant/home-assistant.io/blob/a58a0c9a793de47098c81d6c39a2635c7d850475/source/_triggers/conversation.markdown#L88-L89)

### Separate class reviewer

A follow-up froze the first lexicographic retained compiler trial
from corrected Zed and Home Assistant. An independent Luna low
reviewer saw the scoped class options, prior cited passages and
pinned documents. Its patch could change class decisions, class
citations and open questions. Product, identities, membership,
and relations stayed fixed. The 14 mechanical controls covered
no-op byte replay and the nonclass invariants. One strict run per
product completed with zero retries.

The prompt showed both class keys and full IRIs without explicitly
requiring the short keys in patches. Both actors supplied exact
allowed IRIs. The frozen verifier rejected both patches. A separate
no-inference replay translated only the nine exact IRIs to their
unique allowed keys and preserved every chosen class, witness and
question. Both diagnostic graphs passed SHACL and retained every
nonclass triple and citation.

| Masked diagnostic | Zed before → after | Home Assistant before → after |
| --- | ---: | ---: |
| Correct scoped classes | 5/7 → 6/7 | 7/7 → 6/7 |
| Sufficient class citations | 4/7 → 6/7 | 2/7 → 3/7 |
| Direct unknown questions | 0/2 → 0/2 | 1/1 → 1/1 |
| Full semantic artifact pass | 0 → 0 | 0 → 0 |

The reviewer correctly reopened the mechanism of Zed's external
formatter. Its question asked about general capabilities instead of
the configured formatter. It kept the insufficient non-AI claim for
language-server completion. In Home Assistant it replaced a correct
class for documented fixed intent matching with an open class.
The independently reviewed evidence improved in both artifacts,
while the class corrections had opposite effects. This replay
preserves the original native score of zero accepted patches.

### Relation IDs that name both roles

A separate adaptive development test kept the exact Home Assistant
candidate, documentation, ontology, instructions, helper and
verifier. The only task-file differences were the four relation ID
strings in the actor scope and its verifier mirror. Each new ID
spells out the subject, predicate and object. The diff is
reversible. Ten local and Docker controls and the actual
no-inference Harbor boundary passed before two fresh concurrent
Luna low attempts with zero retries.

Both new trials passed strict execution, the native structural
verifier and SHACL. Their graphs matched each other and the
independent reference byte for byte. The two historical attempts
with ordinal IDs had reproduced the same reversed edge. The two
fresh attempts recovered the required forward edge, with zero
reverse or extra edges. Evidence differed across the two runs.
The independent masked assessment accepted the guarded forward
edge in both. It credited 7/14 class citations as sufficient,
compared with 6/14 for the historical compiler pair, and one of
the two open-mechanism questions directly requested the decisive
fact. Both documented the two provider denials and rejected the
reverse edge. The full semantic gate remained at 0/2.

The comparison uses historical trials as its development comparator.
Only a fresh independent corpus can qualify transfer of the role
addressing technique.

## Retrieval experiments

The lexical diagnostic compared bag of words, TF-IDF, BM25 and
seven variants of slot coverage, title and heading priors, and
early-section bias. Each method ranked the same pinned windows
without the reviewed witness annotations. The reported maximum
budget is 2,400 source characters per target, with duplicates
counted once. A separate scorer checks whether the selected
lines cover the accepted witnesses and all separately required
groups. Coverage is a retrieval measure. It gives no credit for
correct conclusions or citation sufficiency after generation.
[Coverage-aware context construction](https://arxiv.org/abs/2610.40314)

| Method | Zed | Home Assistant | GitHub |
| --- | ---: | ---: | ---: |
| Bag of words | 7/8 | 4/11 | 5/19 |
| TF-IDF | 6/8 | 6/11 | 7/19 |
| BM25 | 6/8 | 6/11 | 6/19 |
| Slot coverage | 6/8 | 8/11 | 4/19 |
| Slot coverage with an identity anchor | 6/8 | 8/11 | 4/19 |
| BM25 with document title prior | 6/8 | 8/11 | 6/19 |
| BM25 with section heading prior | 6/8 | 4/11 | 7/19 |
| Reserved introductory passage | 8/8 | 4/11 | 3/19 |
| Lead-biased bag of words | 8/8 | 5/11 | 7/19 |
| Lead-biased BM25 | 8/8 | 5/11 | 9/19 |

The Zed development selection was lead-biased bag of words. It
covered 8/8 reviewed targets with the primary budget and 3/8
with the 600-character budget, where bag of words covered 5/8.
On Home Assistant, the selected method lost to the two stronger
lexical baselines. Three variants already in the frozen comparison
covered 8/11 Home Assistant targets. The anchor-based one included
zero hard-negative-only selections among targets with incomplete
support, compared with one for the other two tied methods. A
separate GitHub probe selected that anchor-based method before
scoring and obtained 4/19. That probe uses a historical corpus
and prior reviewed claims as the target roster. It measures
evidence retrieval for known claims. The best GitHub result, 9/19,
came from a diagnostic variant.

Zed and Home Assistant rankings reproduced byte for byte on Python
3.11 and 3.14 before witness scoring. The three corpus outcomes
give different ranker preferences. No retriever became a required
part of the skill.

## Focused witness-selection check

Two strict isolated Luna low runs received the same eight bounded
cases with competing passages from Zed, Home Assistant and GitHub.
The treatment added a check of operation stage, actor, condition and
counterfactual sufficiency. Both returned 8/8 exact assertion or
withhold decisions and minimum passage sets, including selection of
the documented shell dispatch over the task picker. One item put a
deployment premise inside the proposition under review. Both models
treated the premise as something the documents had to establish.
Withholding the AI classification was still supported. The item
does not test whether the model retains a stipulated deployment
premise. The other seven cases also tied. This diagnostic supplies
the relevant passages and leaves the end-to-end retrieval and
selection problem open.

## Reviewed guard and relation consequence

The Home Assistant fixture pins seven official documents. It
requires source evidence for both the active local trigger path
and the overlap rule. A model-free consequence probe translated
the two official passages into six reviewed Boolean atoms. The
actual semantic comparison CLI accepted the scoped precedence,
refuted built-in execution in the active overlapping case, and
found two independent claims when the scope was dropped or a
necessary setting was read as sufficient. A separate enumeration
matched all six CLI classifications over 64 assignments, of which
47 satisfy the reviewed premises. The first attempt used a bare
scenario atom and was rejected by the CLI's rule grammar. The
corrected probe uses the conjunction as the reviewed candidate.
[Sentence-trigger precedence and local handling](https://github.com/home-assistant/home-assistant.io/blob/a58a0c9a793de47098c81d6c39a2635c7d850475/source/_triggers/conversation.markdown#L88-L89)

## Receipts

| Local evidence | SHA-256 |
| --- | --- |
| Exact compiler | `64c39dc324047624bc3f61fb0e220a48b34dd3bb100027b9b5493e5f5e44830f` |
| Mechanical audit, both Python versions | `1c08203c86ab70b6909ad6f32372107948a2ede4d599af699f05a53a7102bd73` |
| Zed initial bound semantic comparison | `4545823c351932052942946dc4496619e8d5a0ddfb3323c89a2da65cdaf7aae7` |
| Zed corrected protocol | `b551f82bf486ba98ac99db2ba819a3a2f4e97ecb1743cb07151e74d1b2b2749a` |
| Zed corrected bound semantic comparison | `566a3b1b6464096692609849c4a235f0c0e966548fd5981b1a01ebc075e8f3eb` |
| Zed evidence exposure trace audit | `1b1b6b202076976baa3475e5454a7895c9284deb4e6b4313fca407fa5c3154b7` |
| Home Assistant input freeze | `84a3c4c2bd01c7527490fe1f513bc83ce849a740d9859ba785e5c91739448fb7` |
| Home Assistant native aggregate | `fc59d2b0aa894450eecf1dd4d11c5a13ed9d0ff97d6c30057f0fc02b4eb0dbad` |
| Retrieval protocol | `a25a03970ff5f78bd6fbf6dcc13b1d816da1f7bcc61be46081772659e089f593` |
| Home Assistant retrieval results | `adaf43d4aba0bea582f6d85b4745cfb5c4394ef133f1791b6505cc22176ff4a1` |
| GitHub retrieval results | `ce758832dcba5f1bb9ac7d8481884c7df2832c6ee8cbca78c25c01a9c6e90d06` |
| Reviewed guard check | `39d41994bd57904a0ad7d60db90c3b9ef5a22a04af0bb930c4a267f644d8d8ed` |
| Home Assistant bound semantic comparison | `08fcb907c3a6da30c9489eb3d6035ea2a0c61236f017293747b3af73808fe44a` |
| Home Assistant role-address replay | `a06adfbd023487924eef436f9bea30e13d64bc7f9aa9e9c54c7340df3e448877` |
| Class reviewer no-inference alias replay | `731c0e648a96a13607a3516574c1af352cda45f87b8470edf2b47e836b57a352` |
| Class reviewer masked verdict | `b6502bfe4245c6ee10296f5084ed2930764c9673889792c5b083074427198f8d` |
| Home Assistant role-address protocol | `c2ea43879c58a8685e77ff26150725eb4fafabd431961c3fd6a916e6b2f9fd3e` |
| Home Assistant role-address native aggregate | `37402d5037f098ff34a05b9841d4e7bc7db82bfe46ed3017dbe0b4f6e7a0a65d` |
| Home Assistant role-address masked verdict | `2d131f25b1fb2e313bf4693af2fdb622b7c0c47737a70655adbfe416e8cb7c0d` |
