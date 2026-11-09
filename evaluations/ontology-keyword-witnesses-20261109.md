# Source keyword witnesses for ontology-guided extraction

## Scope

The fixed vocabulary in each study asks for selected modality
assertions. The sources specify the actor, action, conditions, and
uppercase modal. A missing assertion stays absent in the graph.
The experiment compares two carriers. One asks GPT-6 Luna to copy an
exact quote and state the modality. The other asks it to select an
exact source span. A deterministic compiler recovers the modal and
the literal text from that selection. Source coordinates and graph
correctness are checked separately.

SemVer uses three published editions. HTTP uses RFC 7231 and RFC 9110.
Each comparison used the same approved source units within an edition.
HTTP competency questions omit the expected modal, and source unit and
witness IDs are assigned by position. Its source-only index contains 48
modal candidates for 16 expected assertions. Gold and scorer files were
outside the isolated actor workspace. Results are public development
measurements over these fixed vocabularies.

[SemVer source snapshots](https://github.com/semver/semver.org/tree/88e3357f2213196669a6fdefc5a59afe5ec17bee/spec) ·
[RFC 7231](https://www.rfc-editor.org/rfc/rfc7231.txt) ·
[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.txt)

| Corpus and carrier | Source-backed assertions per trial | Correct changes per trial | Identical repeated graphs |
| --- | --- | --- | --- |
| SemVer, exact quote | 32/34, 32/34 | 8/9, 8/9 | 3/3 editions |
| SemVer, span ID and local context | 34/34, 34/34 | 9/9, 9/9 | 3/3 editions |
| HTTP, exact quote | 15/16, 14/16 | 3/4, 2/4 | 1/2 editions |
| HTTP, span ID and local context | 16/16, 16/16 | 4/4, 4/4 | 2/2 editions |

These eight trials passed strict Pi admission. In SemVer the direct
actor twice omitted the modal from two citations. In HTTP it copied
nonliteral text or returned a quote that did not uniquely locate its
source. The first SemVer experiment is preserved separately. Both
direct trials failed admission after attempting to read a task file
inside the skill directory. Two span-ID trials were admissible and
scored 34/34 and 33/34. The comparison in the table used a clarified
workspace path in both arms. The span-ID arm also supplied local
context around each occurrence.

The released helper reproduced all 114 source keyword ranges and
their local contexts used in these experiments. Reordering the
approved units produced identical indexes. The helper keeps a
line-wrapped MUST NOT as one exact span, rejects changed source
hashes, and does not emit a partial token when a unit cuts a match.
The caller selects the governed units and verifies authority,
subject, and conditions. A keyword index can contain historical,
example, or quoted text whenever the supplied units include it.

## Release checks

Two isolated strict Pi runs with `github-copilot/gpt-6-luna` and low
thinking ran the bundled helper on the same checklist. Each recorded
the prohibition and permission with the expected IDs, omitted the
excluded example, and produced byte-identical indexes. The run reads
the keyword reference and the general mapping reference.
[Isolated runtime prompt](pi-prompts/ontology-keyword-witnesses.md)

A separate native Harbor 0.18.0 oracle smoke gave reward 1.0 with zero
exceptions and zero retries. It exercised the graph verifier with a
known solution. Local controls rejected a missing rule, a foreign
token, a neighboring rule's token, and a spurious assertion. The
Harbor job did not make a model call.

~~~powershell
python -B -m unittest discover -s evaluations/contracts -p 'test_ontology*.py'
uv run --script scripts/run-pi-skill-eval.py extract-with-ontology --prompt-file evaluations/pi-prompts/ontology-keyword-witnesses.md --model github-copilot/gpt-6-luna --thinking low --mode json --strict --run-id semantic-keyword-witnesses-replay --expect-output witnesses.json --expect-output review.json
uv run --script scripts/validate-skills.py
uv run --script scripts/check-repo-payload.py
~~~


## Rewrapped-source witness review

Two independent Luna trials used the same SemVer sentences with CRLF
and different line wrapping. Their exact source positions were rebuilt.
A single workspace-root input and bare token IDs passed strict custody
in both trials. Both recovered all 34 expected edges, with 33 reviewed
witnesses each. One trial added an unsupported metadata edge.

A local recheck selected 17 and 19 decisions with a neighboring
occurrence of the same modal or a reused witness. The first review
wording held a valid prohibition and finished at 33/34 in each trial.
A generic explanation in the isolated skill reference also finished
at 33/34. The final reference explicitly accepts a governing
MUST NOT or SHOULD NOT for a rule description phrased as an action.
Two isolated Luna trials read the final reference and rechecked the
same decision sets without the polarity wording in the task prompt.
Both finished with 34/34 edges, 34/34 reviewed witnesses, no extra
edges, and identical graph hashes across the three editions.

In an RFC 9110 transfer probe, the final reference preserved four
correct witnesses, repaired four swaps between client and origin
server modals, and rejected an unrelated HEAD witness. The prior
review prompt also passed all nine controls. These probes test
local witness review under a fixed vocabulary. They do not measure
the reproducibility of free-text ontology extraction.
[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.txt)
