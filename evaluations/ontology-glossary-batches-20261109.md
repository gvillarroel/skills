# Document-level glossary batch compilation

Glossary proposal batches use a pinned document roster and one physical
line per document. The line starts with the document ID and a tab.
Keeping the ID outside the JSON lets the compiler identify which
document to quarantine when a body is malformed or a duplicate body
cannot be parsed. Independently valid documents retain their candidate
ledgers. A damaged ID leaves an unattributed diagnostic and the batch
status remains partial.

## Canonical compiler checks

| Check | Result |
| --- | --- |
| Skill tests | 10/10 on Python 3.11 and 3.14, including five batch tests |
| Frozen independent CLI controls | 50/50 on both versions: 7 complete, 35 partial, 8 fatal |
| Additional CLI invocations | 3 byte-identical replays, 2 existing-output checks, 1 invalid UTF-8 manifest, 1 escaping symlink |
| Retained Luna proposal replay | 18/18 document ledgers matched, including two reviewed-empty documents |

The independent controls checked the accepted document roster, per-line
diagnostics, exact candidate ledgers and source, draft, manifest and
records digests. The two Python versions produced the same audit
report. Its SHA-256 is
`60e0e8b50939b3fdb1b126225ea924a1f8bdecbcdeb10ba176adcde139be7293`.

Two strict GPT-6 Luna low runs on the final skill independently
compiled the same supplied batch. Both retained three documents,
including a reviewed-empty document, and two definitions with
different source scopes. Both cited the passages separately and
asked whether the two readings should share a glossary identity.
The ledger bytes matched with SHA-256
`57ff1c1fd05d1e4aa1d91763c5f0c82820085cf240e9cee86c2ef7f2e59093ee`.

## Transport comparison

The probe repackaged 18 source-verified documents from 16 cases in
three retained GPT-6 Luna runs. All three formats reproduced the same
document ledgers on intact input. The fractions below count recovered
ledgers among eligible documents, after excluding the affected
document when applicable. The JSON Lines comparison decoded strict
JSON rows independently and read the document ID from inside each
row. An additional canonical CLI replay checked the tagged results
and recovered 17 documents after one source changed on disk.

| Injected fault | Aggregate JSON | JSON Lines | Document ID + tab + JSON |
| --- | ---: | ---: | ---: |
| Truncated final row | 0/17 | 17/17 | 17/17 |
| Malformed middle row | 0/17 | 17/17 | 17/17 |
| Malformed duplicate | 0/17 | 17/17 plus one ambiguous document | 17/17, affected document excluded |
| Invalid UTF-8 in one body | 0/17 | 17/17 | 17/17 |
| Valid duplicate, missing document, or wrong source pin | 17/17 each | 17/17 each | 17/17 each |
| Unexpected document ID | 18/18 | 18/18 | 18/18 |

All faulted batches were reported as partial. The normalized hash of
the matching document ledgers is
`a8d75388d56cb859529422e5ce176928cbc0c472e5f463a9f4124ec3e06dd23f`.
The transport comparison measures recovery and preservation of
already generated proposals. Proposal-generation correctness is
evaluated separately.

[RFC 7464 record recovery](https://www.rfc-editor.org/rfc/rfc7464.html#section-2.3) ·
[JSON Lines framing](https://jsonlines.org/)

## Native Harbor generation pilot

A separate paired pilot asked GPT-6 Luna low to generate the same
glossary candidates in aggregate JSON and in ID-prefixed records.
It used four cases of three source documents each, drawn from
Kubernetes, Git, W3C semantic standards and data serialization
specifications. The pilot used an independent verifier for both
carriers and checked source evidence, term identity and agreement
between the two outputs.

Harbor job `4f478044-37bb-4276-8b97-2928ed282cf0` completed after
40 verifier controls passed in Docker. Aggregate JSON passed all
four cases and all twelve documents.
The ID-prefixed carrier passed three cases and nine documents.
The same three cases passed the joint equality and semantic gate.
In the Git case, all three IDs were readable and all three JSON
bodies missed a closing brace. Harbor recorded zero execution
exceptions. The pilot used one model attempt per case. These
results separate resilience to partial corruption from the model's
ability to generate valid records directly.

[Batch and review workflow](../skills/extract-ontologies/references/glossary.md#compile-and-review-documents-independently)
