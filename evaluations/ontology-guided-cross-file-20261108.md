# Multi-file extraction with an existing ontology

The comparison used eight synthetic source packets spanning seven
independent families. Two packets differ by the presence of an irrelevant
training file. Each packet supplied a fixed vocabulary and source files.
An independently authored rubric specified 12 directed facts, each
requiring evidence from at least two files. Three facts require three
files. Cases also cover homonyms, unresolved identity, conflicting
sources, negative or conditional claims, and exact datatype lexical forms.

Each method made one tool-disabled `github-copilot/gpt-6-luna` request per
packet in two fresh rounds. The methods saw the same complete files. The
first returned literal quotes, the second selected stable segment IDs,
and the third selected segment IDs with evidence roles and repeated-code
hints. A deterministic host copied exact text for both segment methods.
The repeated-code cue is a lexical analogue of path retrieval, evaluated
without a learned retriever. [Mr. Cod](https://aclanthology.org/2023.findings-acl.657/)

| Method | Exact graph per run | Correct graph in both rounds | Correct graph and evidence in both rounds | Supported claims | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| Literal quotes | 14/16 | 6/8 | 4/8 | 13/24 | 26,724 |
| Segment IDs | 16/16 | 8/8 | 8/8 | 24/24 | 25,042 |
| Segment IDs, roles, and hints | 11/16 | 5/8 | 5/8 | 19/24 | 30,400 |

All 48 model receipts matched the exact prompt, provider and model,
and tool-free event policy. The accepted artifacts contained zero false
assertions. Two quote responses used an unregistered subject or invalid
predicate. Five role-based responses selected the same coordinate for
multiple roles, which the original validator rejected as duplicate
evidence. A separate provider-free replay collapsed these roles onto one
citation per coordinate. All five rejections were reproducible and the
replayed method reached 8/8 strict pairs, 24/24 supported claims and
zero false assertions. The matched scores above retain the original
rejections. This pilot found no gain from adding the role format and
code hints together. Both coordinate arms received pre-segmented source
units and saw the complete files, so this study leaves large-corpus
retrieval and segmentation quality unmeasured.

Source-only inputs, a separate reference, the reproduction protocol,
the 48 audited run receipts, the matched report, and the role replay
are under `projects/semantic-skill-evaluation/artifacts/ontology-guided-skill-20261108/cross-file-transfer-v1/`.
The matched report SHA-256 is
`08733f565d7a185a1ee8f8ab4da1ac65a2237dc9a37689f1ca84f8cbcec13c43`.

## Isolated skill test with real RFC sources

Two clean Pi workspaces received the same runtime bundle, three pinned
RFC excerpts, and a local application profile based on the dated DCMI
vocabulary. The task projected titles, identifiers, and publication
months for RFC 9110, RFC 7230 and RFC 7231. Whole replacement was in scope.
RFC 9110's abstract and section 1.4 distinguish the full replacement of
RFC 7231 from the partial replacement of RFC 7230. The supplied excerpts
do not establish acceptance dates. [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110#section-1.4),
[RFC 7230](https://www.rfc-editor.org/rfc/rfc7230), [RFC 7231](https://www.rfc-editor.org/rfc/rfc7231),
[DCMI Metadata Terms 2020-01-20](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/).

Both Luna runs produced 10/10 exact RDF assertions with adequate
evidence and the same asserted graph SHA-256
`bdb6b017da8f1f8323b41db7d5913dbf1295fe45ebf49c5190029478d230bb85`.
Both preserved the distinction between whole and partial replacement
and recorded missing acceptance dates. The Markdown and CSV glossaries
covered all six entries and cited the supplied ontology.

Two evaluation artifacts needed separate, provider-free checks.
The raw Pi exact-command gate rejected the `powershell` fence in both
trials. Replaying the original events with that fence recognized in
the verifier confirmed the exact command, required files, valid
events, requested model, zero tool errors, and an unchanged bundle.
The original artifact grader passed one run and rejected the other's
six OWL kind names, such as `owl:DatatypeProperty`, because it expected
display labels. A separate replay accepted the three equivalent OWL
kind names and passed all six entries in both runs. It still rejected
a wrong-kind control. Original outputs and failures are preserved.

Fixture, grade, and replay receipts are under
`projects/semantic-skill-evaluation/artifacts/ontology-guided-skill-20261108/real-sources-v1/`.
Pi run IDs are `semantic-ontology-guided-rfc-20261108-a` and
`semantic-ontology-guided-rfc-20261108-b`. These runs evaluate a
bounded projection from supplied excerpts. Larger and less structured
sources need their own verification.

## Glossary and extraction routing

The final bundles were tested separately with `github-copilot/gpt-6-luna`
in strict Pi runtime workspaces. The supplied-model skill leaves the
ontology as a separate input. The authoring skill can deliver a glossary
directly from source evidence. Both use the same CSV fields.

| Case | Result | Evidence |
| --- | --- | --- |
| Apply the fixed permit ontology to CSV and prose, and deliver a status glossary | Two final runs each passed 6/6 reference assertions and their exact supporting register rows, plus 3/3 glossary entries. Both runs had the same asserted graph fingerprint. | `semantic-guided-permits-20261108-c`, `semantic-guided-permits-20261108-d` |
| Build a glossary only from a supplied SKOS vocabulary | 4/4 rows across two IRIs and two languages. Preserved the English homonyms and language-specific alias. One absent Spanish definition remained empty. Only the requested glossary files were produced. | `semantic-guided-glossary-only-20261108-a` |
| Author a glossary from source excerpts | 4/4 entries, including same-label concepts, supported aliases, and a term with attestation and no definition. | `semantic-glossary-authoring-routing-20261108-b` |
| Author a glossary with conflicting sources | 4/4 semantic checks. Both conflicting locators were retained, one wholly unattested term stayed empty, and a requested provisional entry was marked `working`. | `semantic-glossary-authoring-conflict-20261108-a` |

The permit fixture kept a historical use of “Filed” as a usage note.
The canonical definition stayed intact. The explicit “Submitted”
alias mapped to Filed. An unmatched status and a blank stayed out of
the graph and remained visible in review. The graph SHA-256 was
`16bf81436836cf87752a54d6cc3d79139e81385831abf22c40c0b0fe78dd0ae9`
in both final runs. Markdown glossaries and review notes were inspected
by hand. The independent grader verifies exact RDF, supporting
register rows, the checker report and the CSV glossary. It rejected
controls with missing status evidence, a wrong mapping accompanied by
matching evidence, a historical definition replacing the canonical
one, and an unsupported alias. The repeated graph fingerprint does not
imply byte-identical glossary or review text.

An earlier guided output combined `skos:Concept` and
`owl:NamedIndividual` in the same kind field. That incomplete pilot
was stopped after both final runs passed. The revised instructions use
one row per identifier, in-scope kind, and language. An earlier
authoring output included a catalog note in the kind field. The revised
authoring instructions keep that note with the attestation. Both final
bundles passed static validation, and the guided checker passed all 14
regression tests.

Repeat the permit test from the repository root, changing the run ID
for each clean workspace.

```powershell
uv run --script scripts/run-pi-skill-eval.py extract-with-ontology --prompt-file evaluations/pi-prompts/ontology-guided-permits.md --model github-copilot/gpt-6-luna --thinking low --mode json --strict --run-id semantic-guided-permits-replay --expect-output data.ttl --expect-output evidence.json --expect-output review.md --expect-output glossary.md --expect-output glossary.csv --expect-output checks.json --expect-output-json-field checks.json::status=passed --expect-output-json-field checks.json::asserted_triples=6 --expect-output-json-field checks.json::evidence_covered_triples=6
uv run --script evaluations/contracts/grade_ontology_guided_permits.py evaluations/runs/semantic-guided-permits-replay/workspace
```

The other three prompts and strict-run receipts are under their run IDs
in `evaluations/runs/`. These checks cover the supplied-input and
glossary boundary and do not count toward the independent Harbor gate.
