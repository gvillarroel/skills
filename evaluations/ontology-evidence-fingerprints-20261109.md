# Stable fingerprints for reviewed rule evidence

The indexed Boolean comparator preserves the original source fragments for review and adds a SHA-256 fingerprint for their covered token positions. It binds the fingerprint to the raw source digest, cited line bounds and reviewed atom IDs. Two atoms can cite a shared predicate when their complete token coverage differs. The comparator rejects identical coverage even when the ranges are partitioned differently.

The document comparison reference now gives separate encodings for inclusive disjunction and exactly one of two branches. The review checks the two single-branch cases, both branches and neither branch under the same surrounding conditions. An unresolved overlap remains a review decision.

## Qualification

| Check | Observed result |
| --- | --- |
| Full skill test suite | 211/211 passed on Python 3.11 and 3.14 |
| Independent partition audit | 364 valid partitions across 126 distinct token sets preserved coverage identity and exact UTF-8 fragments |
| Duplicate coverage audit | 364 alternative partitions rejected when two atoms cited the same positions |
| Legacy reviewed inputs without token references | Two earlier complete JSON outputs reproduced byte for byte |
| Isolated GPT-6 Luna low runtime checks | 2/2 strict runs passed |

Both strict runs used the same reviewed inclusive-versus-exclusive choice and produced byte-identical outputs for each evidence representation. The contiguous output retained one B fragment. The partitioned output retained two. Both produced the same reviewed semantic fingerprints and head evidence fingerprint.

| Artifact | SHA-256 |
| --- | --- |
| Contiguous comparison | `2636bff7a1f7512810288916dfdf8ec0df98a81f2ddbaffc0cd40e7338215c24` |
| Partitioned comparison | `03eb8f87502506ae23bcfc9b1af4a4c3c2701ed95f970f345719e003211b1bcf` |
| Head evidence coverage | `3495a4d44fa40320f29f7a50bdee8b36eb9faf8d2602f64fa3924b92a264f295` |

The fingerprint compares coverage within a pinned source version and a reviewed vocabulary. Changes in selected positions produce a different fingerprint. Atom definitions and the correspondence between independently chosen IDs require separate review.

## Reproduction

~~~text
uv run --no-project --python 3.11 python -B -m unittest discover -s skills/curate-semantic-model/scripts -p 'test_*.py'
uv run --no-project --python 3.14 python -B -m unittest discover -s skills/curate-semantic-model/scripts -p 'test_*.py'
uv run --script scripts/validate-skills.py
uv run --script scripts/check-repo-payload.py
~~~

[Indexed evidence reference](../skills/curate-semantic-model/references/document-versions.md#bind-reviewed-atoms-by-token-number)
