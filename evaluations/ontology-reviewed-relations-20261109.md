# Reviewed relation identity across document versions

The relation comparison mode resolves directed roles through a reviewed
glossary for each source version. It compares the resulting roles and
polarity, modality, time and scope. It preserves the exact relation and
binding citations, and reports source and reviewed-input digests
separately from the relation graph fingerprints.

| Check | Result |
| --- | --- |
| Full skill suite | 234/234 on Python 3.11 and 3.14 |
| Independent frozen audit | 40/40 expected outcomes across 52 CLI invocations |
| Previous modes | Five CLI modes reproduced their previous reports byte for byte |
| Isolated GPT-6 Luna low | Two final strict runs produced equal semantic reports |
| Exact input replay | Identical source and reviewed input bytes produced byte-identical reports |

The strict runtime case changed an alias while preserving the stable
courier role. The permission became a requirement, so the comparator
reported one modality change. A second input withheld the head subject
binding, which produced an abstention with the citation and missing
role intact. The two model runs encoded equivalent reviewed JSON with
different whitespace. Their input provenance digests differed and
their remaining report fields agreed.

| Exact input replay | Report SHA-256 |
| --- | --- |
| Reviewed modification | `437fa7390617ad90f6ceda454f2c4678b8251f8436e7431f29c112ca94909a3b` |
| Unresolved subject | `c7d42dec5638819f59fecc09375819949e06bfcff62e504c53fda3c2d6f0880b` |

An eight-pair extraction pilot provided reviewed vocabularies and short
explicit source texts. With stable identifiers visible in the model
input, Luna emitted those values where the draft expected local keys.
The comparator held those inputs. Giving Luna the local code lists
and keeping the stable maps with the comparator produced two
independent runs with eight expected outcomes each. The seven
resolvable relation graph fingerprints repeated, and the unresolved
case held in both runs. The pilot covers reviewed vocabularies and
controlled source statements.

[Reviewed relation workflow](../skills/curate-semantic-model/references/document-versions.md#compare-reviewed-qualified-relations)
