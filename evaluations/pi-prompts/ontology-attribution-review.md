# Review the provenance of a bounded ontology projection

The project models two public output fields and an internal record
attachment. Review the attribution of the candidate assertions below.
Use only the permitted evidence for each candidate. An output that
returns nothing has no RDF value. Treat the quoted requirements as
authoritative within this exercise.

| ID | Source statement |
| --- | --- |
| s1 | Any edge using publicManifest points to a ManifestFile. |
| s2 | A queued job's internal envelope stores a ManifestFile as its audit attachment. |
| s3 | The exportRoute getter returns no value when the export bundle has no audit attachment. Otherwise it returns that bundle's audit attachment. |
| s4 | An export bundle's audit attachment, if present, is a ManifestFile. |
| s5 | Each publicManifest value is a ManifestFile. |
| s6 | A retried task may have no audit attachment. |

Review these five cases.

| ID | Candidate and permitted evidence |
| --- | --- |
| global | A property-wide range of ManifestFile on publicManifest. Assess s1 and s5 as independent evidence candidates. |
| local | CompletedJob is restricted to publicManifest values of type ManifestFile. The formal background contains the property-wide publicManifest range from s1. Check whether the background supports this without a direct CompletedJob assertion. |
| returned | Any value returned by an export bundle's exportRoute has type ManifestFile. Assess s3 and s4. |
| layer | A property-wide range of ManifestFile on publicManifest, attributed specifically to s2 alone. |
| presence | Every export bundle has at least one audit attachment, attributed to s4 and s6. |

Create `findings.json` with a top-level object whose five keys are the
case IDs. Each value has a `status` chosen from `direct`, `joint`,
`derived`, and `unsupported`, a `locators` array of the supporting
source IDs, and a `rationale` explaining the support or gap.
For a derived result, cite the origin of the formal background.
For an unsupported result, leave `locators` empty and name the
evaluated fragments in the rationale. Create no other task artifact.
