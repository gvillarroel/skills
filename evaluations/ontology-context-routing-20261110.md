# Bounded context routing for ontology evidence

This development study follows the
[relation and citation repair experiments](ontology-relation-verification-20261110.md).
It measures whether a router can recover a missing antecedent, scope,
or referenced fact from authorized documents. The anchor and claim
are fixed before ranking. A complete evidence bundle may require
multiple spans. Retrieval and semantic support are scored separately.
[CORRECT](https://aclanthology.org/2025.naacl-long.154/) ·
[Logical document structure and anaphora](https://aclanthology.org/L06-1147/)

## PostgreSQL DocBook sources

Four upstream SGML files were pinned to the PostgreSQL 17.5 release
commit. Each Git blob identity, SHA-256 digest, and size was verified
before parsing. The structural parser identified 1,025 regions. The
frozen case file contains 13 supported contextual targets, three
direct rebuttals, and one reference outside the supplied corpus.
Cases include parameter ownership, isolation scope, an exception,
a nested query plan, a compound command definition, and scope across
paragraphs. The original quote remains visible in all routes.
The character budget applies to the additional text per case.
[Pinned PostgreSQL documentation](https://github.com/postgres/postgres/tree/5e2f3df49d4298c6097789364a5a53be172f6e85/doc/src/sgml)

| Route | Complete at 400 added characters | At 800 | At 1,600 |
| --- | ---: | ---: | ---: |
| Seven preceding lines | 8/13 | 9/13 | 9/13 |
| Section title and first paragraph | 2/13 | 3/13 | 3/13 |
| Paragraph, parameter owner, and prior paragraph | 5/13 | 10/13 | 11/13 |
| Bounded prose and authorized links ranked by clause | 5/13 | 9/13 | 13/13 |
| Owner-aware route with a nearby-line fallback | 9/13 | 10/13 | 12/13 |

The initial structural route missed two positive cases at the
largest budget. A paragraph containing a nested list exceeded the
bound, hiding the statement about complete dump ordering. Ranking
a linked command's entire reference entry favored a per-command
example over its general description. Restricting retrieval to
the linked overview recovered the command context. Ranking its
obligations separately matched that coverage. Trimming a paragraph
before its nested block recovered the dump
scope. The combined route found all 13 supported bundles and
all three rebuttals. The unavailable configuration link remained
unresolved. [Row security](https://www.postgresql.org/docs/17/ddl-rowsecurity.html) ·
[CREATE POLICY](https://www.postgresql.org/docs/17/sql-createpolicy.html) ·
[Transaction isolation](https://www.postgresql.org/docs/17/transaction-iso.html) ·
[Populating a database](https://www.postgresql.org/docs/17/populate.html)

At the 800-character limit, the fallback exposed 8,409 added
characters across 17 cases, recovered 10 supported bundles and
all three rebuttals, and exposed none of the five nominated
unrequested passages. At 1,600 characters it recovered only
12 positive bundles, compared with 13 for the combined route.
The combined route exposed 14,934 added characters and six
lines of one nominated foil. Restricting earlier paragraphs to
the current parameter owner did not change the measured
1,600-character outcome. The five foils cover a bounded set of
potentially irrelevant passages.

The baseline replay remained byte-identical after the refinements.
Python 3.11 and 3.14 reproduced the baseline and final results.
Linux reproduced the final result. Seven mechanical controls
passed on each Windows interpreter, including source tampering,
source identity, range limits, comment-only links, malformed
structure, parameter boundaries, and the context budget.
The refinements were developed with access to these public cases.

## Independent HTTP documentation probe

A separately authored public development probe used the exact
HTML bytes of RFC 9110 and RFC 9111. It indexed 1,628 paragraph
and list-item spans. Its 12 cases include five local antecedents,
four cross-document obligations, one internal link, one
self-contained anchor, and one unavailable cited authority.
The initial and refined protocols froze before their respective
scores. The second design could use the initial development
outcomes. [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) ·
[RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html)

| Route | Complete at one passage | At three | At five | Local at three | Cross-document at three |
| --- | ---: | ---: | ---: | ---: | ---: |
| Proximity | 3/10 | 4/10 | 4/10 | 4/5 | 0/4 |
| Section and lexical ranking | 2/10 | 4/10 | 5/10 | 4/5 | 0/4 |
| Links and lexical role cues | 4/10 | 6/10 | 7/10 | 2/5 | 3/4 |
| Same reranker without links | 4/10 | 6/10 | 7/10 | 3/5 | 2/4 |
| Local priority with a reserved linked passage | 6/10 | 9/10 | 9/10 | 5/5 | 3/4 |
| Local priority and clause-based linked ranking | 6/10 | 9/10 | 9/10 | 5/5 | 3/4 |

The local-priority variants retained one local and one linked
passage among the first three for all five authorized-link cases.
Clause splitting improved the position of an alternative If-Range
witness without completing an additional case. Both variants
missed the initial eligible set in a multi-passage 304 case even
after finding the strong-validator rule. Removing approved
passages put a nominated decoy first in 6/10 cases with the
adaptive route, compared with 4/10 for the original link ranker.
Both explicit availability controls returned no added passage.
Two runs per protocol with distinct hash seeds and reversed
candidate order reproduced the same scores. This probes the
routing principle in a second format and family. The DocBook
and HTML implementations differ.

## Markdown transfer in the Compose Specification

An independent author froze ten cases and 15 official Markdown
chapters before scoring the Markdown router. The router and
scorer were frozen before viewing the answer key. Two source
captures reproduced the same bytes when retrieval order and
concurrency changed. The actor packet exposed the claim, focus,
anchor, and source files. The separate answer key contained
18 acceptable witness bundles and 30 nominated competing spans.
The scorer requires every span of one accepted bundle beyond
the supplied anchor. The eight positive cases cover three
local antecedents, one internal fragment, and four links
between chapters. The two remaining cases ask for an
unavailable external authority and an exact broken fragment.
[Pinned Compose Specification](https://github.com/compose-spec/compose-spec/tree/3a4a6995e4a971f6173dff9130cb3e38e6738651)

| Route | Complete at 400 added characters | At 800 | At 1,600 |
| --- | ---: | ---: | ---: |
| Seven preceding lines | 1/8 | 3/8 | 3/8 |
| Heading and section lead | 1/8 | 1/8 | 1/8 |
| Initial bounded local paragraphs | 2/8 | 2/8 | 3/8 |
| Initial links first | 4/8 | 4/8 | 5/8 |
| Initial local and linked clauses | 4/8 | 4/8 | 5/8 |
| Marked CommonMark or GFM blocks with links first | 4/8 | 4/8 | 5/8 |
| Marked GFM list items with links first | 4/8 | 4/8 | 4/8 |
| Descendant sections and symbolic operator matching | 5/8 | 6/8 | 7/8 |
| Descendants with merged neighboring blocks | 5/8 | 6/8 | 6/8 |
| Guarded descendants with a same-document table rule | 5/8 | 7/8 | 8/8 |
| Same route with a reserved local passage for cross-document links | 5/8 | 8/8 | 8/8 |

Marked 18.0.11 was already installed. Its raw token ranges
aligned with the source. The two whole-block modes returned
the same scores as the initial routes. Splitting list items
reduced the added text for the links-first route from 3,448
to 2,328 characters at the largest limit, while losing
one complete antecedent. This comparison changes segmentation
and keeps the ranking and link recognition fixed.
[Marked lexer](https://marked.js.org/using_pro#lexer)

The initial router found the generic append rule but missed the
port uniqueness key and its merge condition. A linked chapter
about interpolation ranked a nearby default value above the
required-variable operator from the anchor. A job inheritance
case required one local passage about the job endpoint and a
linked subsection about the file path. The refinements searched
descendant sections, preserved the punctuation in operators,
joined a selected table with its following same-section rule,
and reserved one local window when following a chapter link.
These choices used the public Compose misses. The resulting
8/8 measures recovery on the same development cases.

At 800 characters, the final route added 3,708 characters
across the ten cases and exposed eight lines from nominated
competing spans. Its explicit link guard added no text to
either unavailable-authority control. The initial links-first
route added 2,348 characters, exposed 13 nominated foil lines,
and supplied extra text in both controls. A subsequent semantic
review must still verify the authority and roles of a retrieved
passage before accepting a relation. Python 3.11 and 3.14
reproduced the fixture and score receipts. Three Markdown
parser, scope, and budget controls passed on both interpreters.

### Independent authority and scope controls

The 8/8 Compose route met both the required-evidence and
nominated-foil criteria on 2/10 independently authored
synthetic controls. The initial local-and-linked-clause route
met both criteria on 3/10. The refined route could follow an
incidental link, skip a valid answer with low lexical overlap,
or extend a table to unrelated prose in the same section.
It exposed a nominated foil in six of ten cases.

Three subsequent variants used the revealed failures. The
first prioritized the requested link label, filtered inline
code, bounded local fallback to the owning section, and added
a structural fallback for an authorized target. It passed
8/10. Selecting a uniquely named descendant section raised
the count to 9/10. Requiring lexical continuity before joining
table prose raised it to 10/10 with zero nominated foil
exposures. Compose stayed at 8/8 and both authority controls
remained clear at 800 characters. The new route exposed
nine nominated foil lines on Compose, compared with eight in
the previous route.

An independent author froze eight further synthetic transfer
cases and withheld their contents before this version froze.
The revised router passed 3/8 jointly, compared with 4/8 for
the earlier route. The revised router had zero exceptions and
one nominated-foil case, compared with one exception and two
foil cases before. Cases missing required evidence increased
from one to four. This result blocks selection of the revised
router on the current evidence. The synthetic transfer cases
are separate from the sealed Harbor cohorts.

### Explicit reference targets

A separate prototype keeps the parsed reference inventory and
its per-destination status before assigning a requested target.
It preserves occurrences, separates unavailable documents,
missing fragments, and malformed destinations, and returns
coordinates as candidates. An explicit caller selection uses
the literal destination. The same inventory also supports a
language-based selector for comparison.

The eight new frozen synthetic controls used the installed
markdown-it-py 4.2.0 parser. They produced 14 distinct
destinations from 15 occurrences. The parser preserved a
reference-style link and excluded a link shown inside code.
The caller supplied a correct destination declaration in seven
cases. With that declaration the prototype returned all seven
expected destination-and-status maps. The language selector
returned one of those seven. In the eighth case the caller
supplied only a natural question. The language selector chose
the correct target and the explicit interface requested a
selection. Counting that abstention, the scores are 7/8 and
2/8. The explicit interface received additional information
and its result measures use of that information. The
prototype records candidate locations for separate evidence
verification. [markdown-it-py tokens](https://markdown-it-py.readthedocs.io/en/latest/using.html)

## Matched Power Automate model diagnostic

A frozen four-decision packet isolated one change in evidence.
Both arms received the original provider citation from line 38
and the same three controls. The second arm also received
lines 23–29 from the same pinned file. Those lines supply the
heading and the operation that the phrase referring to the
capability depends on. No claim text, control, or other source
window changed.

While disk space was below the full-run threshold, a
development diagnostic used Pi 1.4.0's SDK with
in-memory sessions, tool calls disabled, and agent and provider
retries disabled. Each arm issued one GPT-6 Luna low model
request. The harness observed no writes and no retries. The
diagnostic delivered the frozen prompt as text and did not load
the skill or exercise Harbor artifact transfer.

With only the original provider sentence, Luna requested
evidence that identified the operation. With the antecedent,
it selected both passages and bound Azure OpenAI Service to the
cloud-flow creation capability. All three controls stayed
correct in both arms. Each response satisfied the four-decision
development rubric. There was one attempt per arm on a case
already studied during development.

### Strict Pi replay with the isolated skill bundle

Once disk space met the frozen threshold, each arm ran once
in the isolated Pi workspace using the same 13-file skill
payload and GPT-6 Luna low. Both runs met strict admission.
The traces showed the reads of the prompt and the copied
skill and the write of `decisions.json`. The comparator
verified the exact prompt, runtime digests, output schema,
evidence windows, and observed model. There were zero
retries. The invocation was `launch.ps1 -Arm original` and
`launch.ps1 -Arm antecedent` from the frozen protocol.

The original arm kept the provider-only citation. It supplied
the missing operation from the claim being tested. The
antecedent arm correctly selected both exact windows and
replaced the isolated citation. Exact decisions and evidence
improved from 3/4 to 4/4, with 3/3 correct and stable controls.
The frozen pair criterion required the original arm to ask
for evidence, so the pair failed that criterion. The tool-free
and full-skill runs therefore differed on the original target.

### Candidate verification instruction

A temporary candidate adds one sentence to the verification
step. It directs the reader to establish the decisive subject,
operation, and scope from the source windows, treat the claim
as a hypothesis, and request the exact missing antecedent.
The copied source and runtime payloads passed offline checks.
The candidate and both arms froze with the original prompts,
answer key, carrier, and strict runner. The initial launch
preflight measured zero free bytes twice against the 20 MiB
threshold. A later preflight cleared that threshold and each
candidate arm ran once with GPT-6 Luna low, without retries.

| Strict Pi measure | Published baseline | Source-only candidate |
| --- | ---: | ---: |
| Admitted arms | 2/2 | 2/2 |
| Correct decisions and exact evidence with the original citation | 3/4 | 3/4 |
| Correct decisions and exact evidence with the antecedent | 4/4 | 4/4 |
| Correct and stable controls | 3/3 | 3/3 |
| Frozen pair criterion | Fail | Fail |

All eight verdict and witness selections matched the baseline.
The candidate still kept the provider-only citation and used
the claim to supply the missing operation. With the added
source window it correctly identified the unresolved referent
in the original passage and selected both citations. The
unchanged failure on the original arm blocked promotion.
The private Harbor cohort remained sealed.

An independent in-memory diagnostic exercised the same rule on
eight frozen cases with pinned PostgreSQL and Power Automate
windows. The actor saw opaque source IDs and the claim and
source text. The evaluator retained the real-case and
counterfactual labels. One GPT-6 Luna low request per arm used
the same inputs, with one added instruction in the second arm,
zero retries, and zero observed writes.

| Measure | Standard instruction | Source-only verification |
| --- | ---: | ---: |
| Correct verdict and exact citation | 7/8 | 8/8 |
| Correct resolved controls | 5/5 | 5/5 |
| Correct unresolved decisions | 2/3 | 3/3 |
| Decisive question roles under the strict rubric | 1/4 | 4/4 |
| Fully decisive questions under the strict rubric | 0/3 | 3/3 |

The standard arm treated the identity in a Power Automate
claim as the referent of a pronoun in the source. The source-only
arm requested the antecedent. A more permissive reading of the
standard questions credits two roles and one complete question.
Two source-only questions still name the proposed identity
while requesting the exact source authority. The strict Pi
result above records the outcome when the same intervention
was tested in the full skill.

## Matched PostgreSQL model diagnostic

A second public development packet used the same in-memory
runner and changed only the source windows. Both arms received
the same five claims and original citations. The context arm
also received the Repeatable Read heading and scope, the
`check_expression` parameter name, and the lines identifying
the proposed new row. The four pinned source digests and Git
blob identities were checked before inference. The two prompts
and answer key were frozen before the two requests.

| Claim | Original citation | With recovered context |
| --- | --- | --- |
| The retry warning refers to Repeatable Read | Unresolved | Supported |
| `check_expression` applies to the proposed new row and rejects false or null | Unresolved | Supported |
| The same retry warning refers to Read Committed | Unresolved | Contradicted |
| A null `WITH CHECK` result raises an error | Supported | Supported |
| `seq_page_cost` can be set per tablespace | Unresolved | Unresolved |

Both answers matched the frozen verdict and evidence coordinates
on all five claims. All three expected changes occurred and both
controls kept their verdicts. Four of the five unresolved responses
met a strict requirement to name every relevant distinction
explicitly. The question about `check_expression` asked for the
parameter identity. Its anchor already refers to rows resulting
from the update, while the added evidence explicitly contrasts
the proposed and original rows. A rubric that accepts the anchor's
implication can consider the question sufficient. Each arm used
one GPT-6 Luna low request, with zero observed writes and zero
retries. These counts come from one attempt per arm using the
public development packet.
[Pinned CREATE POLICY source](https://github.com/postgres/postgres/blob/5e2f3df49d4298c6097789364a5a53be172f6e85/doc/src/sgml/ref/create_policy.sgml#L203-L217)

## Clarification question diagnostic

The diagnostic held the evidence and claims fixed and
compared the existing question instruction with one added
sentence. The new instruction asked for every still-decisive
obligation and used a contrastive check. If two interpretations
compatible with the supplied evidence could yield the same
answer and different verdicts, the question had to distinguish
them. Prior work motivates evaluating claim parts and the
decision value of a response. [WiCE](https://aclanthology.org/2023.emnlp-main.470/) ·
[Expected value of clarification](https://aclanthology.org/P18-1255/)

The nine frozen synthetic cases covered two missing roles,
each single-role omission, evidence from another release or
operation, a resolved disjunction, a refuted conjunction, and
requests that would repeat established facts. Each arm used
one in-memory GPT-6 Luna low request with the same response
contract, zero retries, and zero observed writes. Both arms
produced 9/9 correct verdicts, covered 6/6 decisive obligations,
asked 5/5 complete and minimal questions for unresolved cases,
and omitted the question in all four closed cases. The one-sentence
intervention tied the baseline on this packet.

## Private verifier feasibility

Synthetic probes isolated a child process from unauthorized
files and network sockets using Landlock and seccomp. A
root-created namespace also denied the worker access to host
mounts and the Docker socket. The operator with host privileges
could still read the synthetic canary. The installed Harbor
verifier interface accepted a synthetic custom verifier and
returned the expected reward without starting a full job.
Private validation requires an administrative boundary outside
the development principal. The private cohort remained sealed.

## Receipts

| Artifact | SHA-256 |
| --- | --- |
| PostgreSQL source manifest | `4063b2c5189dc63aadef7528d32faf9e1a88f718f1fcf230a008d841126c7da4` |
| PostgreSQL case freeze | `31f0ff258f92fe02ca1814c2a618d91b234c559a6b55b7625e5da5523926398f` |
| PostgreSQL baseline results | `4359a497791afd561e89d8c1ad0e6ddf2a633546be6a200296aba6e6c1b142a1` |
| PostgreSQL refined 1,600-character result | `48e9c92ad6fc2f579a4ccd25cea59cbaee8175173ecd82c617920b55da7675a7` |
| PostgreSQL nominated foil freeze | `3748e5c61042216a491845bc9225213b397a1286213d7fc2c1f6ec3f82851a41` |
| PostgreSQL guarded 400-character result | `e658bbad057e477f07bcc13c860b2a712a20562c0d8073ee70ffa80283162252` |
| PostgreSQL guarded 800-character result | `e05d12d12de1b222ba13c435151d85bd635d66349ed8a01ca714f974191d32e2` |
| PostgreSQL guarded 1,600-character result | `8d2d06aec1807a341295540f37f280e52f18e69652b81e511c7a648954342fcf` |
| RFC 9110 source HTML | `d431760660ea44e130f6e919dab216df2d0b3a490567a98089267523368fe1e5` |
| RFC 9111 source HTML | `ce91ee9848d2b9ac46386b0f0cbd4bfd9c0cd1948ebc363834cadc7e0997f3d7` |
| RFC original preregistration | `61e4c9a8641938c23f61b50efadd1b1c60913cfe0a1bd5eb6952114859895389` |
| RFC original results | `05ca095673da2414fbedeb15e24d3a6baeb62f88dba3080976e3004f248c8fda` |
| RFC local-priority preregistration | `79ca79d908ce39f562e1ceec09d8560e01f0233002d830c3983362fe4a6bdd2f` |
| RFC local-priority results | `b0906dd6e1484027f3ed0013576bc55f248f4cc4e30dacfc74c9173502bcbc40` |
| RFC reproducibility package manifest | `577f93173c84b24950324d6d07fb4cc706bae14e0d939fcbff4785857a350b46` |
| Compose fixture freeze | `b0221c82cdc72e14b24e9708289549db36b997e88e8724e1550d7147a65bf70d` |
| Initial Markdown router freeze | `ee2fef32d56fd0fbfb4c11541d3d3daa77390305a099147af40965ede271826f` |
| Initial Markdown scorer freeze | `faea398a07126fd7c3abad64702b1a9cd8698d39a3a290fc2d7b37a3593a6654` |
| Initial Compose results | `a24b3cdb631138be12b058ca954070038583b1fe302fab066db37319720b30df` |
| Compose Marked segmentation results | `6d354e76c726dfd6f570f9f66e7b4c58b7ba6c39e3a00288cf9b1845f786abe4` |
| First Compose refinement results | `09bf37da4eeed1a1c545d7ff853627fddb993d5bc941c8c823d9f6a284e5fe7c` |
| Final Compose development refinement results | `6ae51f186c7b71107eb6ffd8587ff8dad17a1f9e7f7a2cfcaa4e4224b8707cec` |
| First independent Markdown control fixture | `e6018d7cf0f348fbcf513b4776f1ab9dc0ce5ca18fcf6dbce70e960b2f3bf56a` |
| Revised Markdown authority router | `2d380cc6a3aef2b16a965cd7760d8d2d7c49e8d068009888e7d42f29a48ec1d1` |
| Revised router on Compose and the revealed controls | `f61a022fb91bea7d3bac2a57295e83f9f3a3e27c61d4e1933365d9ace8e42443` |
| Additional Markdown synthetic transfer fixture | `537efea79024a3bccf73f23cdb4fc187b91ace0e06059eb8198c2fa66d8cb3c8` |
| Revised router on the additional transfer fixture | `d269f64ec72216d8390856a611cd182c974b2955e2d570be1947a083f23ed19a` |
| Explicit Markdown reference controls | `ee8bde1424044856339b2c49e088ed440f92b0fc7e2308b80ebe345bc0fe97e1` |
| Explicit Markdown reference prototype results | `49aba08eefb1ccde93e755d60ab6a0b170548c29d1c5e06da15312c41450e0b8` |
| Frozen full-run Power Automate protocol | `adcde9f72ec3c52e369944c659da2c8889d0d5881f1908fa53a90cb8e214fadc` |
| Power Automate pre-inference carrier checks | `fa4f15b96ea895e7475c5d24ffc6ed72f3857c77e3435af534e09776793ce8e2` |
| Power Automate strict Pi pair receipt | `4f53e34b227fb4fe13728be7320728aafeaf4a0dcfd42a0ab06e957b0196dd27` |
| Frozen source-only verification candidate study | `05c1716db8ad9988b7c6c5bd956c539cfd49e34d749aa64a9f0c30577b1ef5da` |
| Source-only verification candidate payload | `3962cbfef9044bf17173ce5942f99388850ef37fe09d99226b4b55d49c8f1e89` |
| Strict source-only candidate comparison receipt | `48a146d858f5c6f1ebfcdf0d0fba8fb9b12a71149cfffd7dd5746815287fbf86` |
| Source-only model diagnostic frozen cases | `0fd5a5591a49723537345e87c7bd719611508988688dc33076bf2ee5a3714c24` |
| Source-only model diagnostic frozen rubric | `b81afcb2c73dccced875f3be55244bdd23f1ec3b525dff2b739c2f54cb4ff257` |
| Source-only model diagnostic standard reply | `d4422695a94cecb4d319aa09f8c5492ec4484c5b748cffea10e079369ace56f3` |
| Source-only model diagnostic intervention reply | `cd71f3fb877d5d25a982f7dce5fa6b2bfe1a77b3ce005b889ab4423c2666ca27` |
| In-memory Power Automate reply with the original citation | `a1e679078f4ec32e61333b2384cad8604c9f8525309249904a31ca8e63352885` |
| In-memory Power Automate reply with the recovered antecedent | `b82ea934876da6a01b1d5907e6717b5f41efe5c4c14e1a8df48d3aad45f5cba5` |
| In-memory PostgreSQL frozen answer key | `abd194ddeded240711e81058c2fca51a6de161917c8afdb4ba1f8d209f0491fa` |
| In-memory PostgreSQL prompt with the original citations | `64336d7ab9230faae4dd313b91c42f861d2de5ad9ff0406f32f7d1c83f25c07a` |
| In-memory PostgreSQL prompt with the recovered context | `3984f1c4053559c8712af624f1fe826f7ff7e0171ff69bd5d16acdf20ff195d5` |
| In-memory PostgreSQL reply with the original citations | `4634880e45217b137d673e4e41ec4547bdd7d7ebee153972d1f6828801251d82` |
| In-memory PostgreSQL reply with the recovered context | `4dd60a97427ac81d21e8b3bfec5143b2af6f4cec4de5600f13beb8583af849ae` |
| Clarification diagnostic frozen cases | `8502a4780f810a580123495e4cc0285c738970d9594131ad9ec2291cb3b2f747` |
| Clarification diagnostic frozen rubric | `248f8854dda9473d4bb7160cc47362b0dad30825d4ce03091a7460ed12c72ff3` |
| Clarification diagnostic standard reply | `e70483cf185ec1d02570d8eb5c1bc151b075539a754e287d05e2c99b27bc6c02` |
| Clarification diagnostic contrastive reply | `92a5d7a9f58f5b0a77768e6518325a4791ca021d180eecd6e8970632ed17fc3a` |
