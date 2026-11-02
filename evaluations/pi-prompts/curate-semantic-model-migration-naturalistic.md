# Consolidate a requirements ballot

Our team has a small requirements ballot. Please give us the smallest useful canonical model for comparing tools while preserving what each voter actually chose. Work locally from these supplied records only. Treat the copied skill as read-only; do not inspect hidden files, repository or sibling content, acceptance examples, or external services. Use only its runtime instructions and whichever compact references or scripts the task needs.

The records are:

| ID | Locator | Original text | Selected |
|---|---|---|---|
| `s:lookup` | `ballot:7` | Find stored procedures by name or description. | true |
| `s:search` | `ballot:12` | Search the procedure library using a name or a description. | false |
| `s:save` | `ballot:19` | Save a reusable procedure for later retrieval. | true |
| `s:learn` | `ballot:22` | Learn a new procedure automatically from a successful interaction. | false |

Use stable source IDs, preserve all original text and selections, and represent every source. Make consolidation decisions explicit. A shared topic is not sufficient to transfer a selection. We must still be able to distinguish retrieval, persistence, and learning and ask which original records were selected. Selection can be queried directly from preserved source records if the native competency-query language does not cover source fields; document and run that separate query. Avoid extra hierarchy unless it improves a stated query. Do not invent users, votes, approvals, or a formal reasoner run.

Write exactly `model.json`, `contract.json`, `validation.json`, and `review.md` in the workspace root. The model and type contract must be executable by the copied skill. Include competency queries that detect loss of the three behavioral distinctions and source bindings. Run the bundled contract validator and put the actual result in `validation.json`. Explain each proposed equivalence or separation, the original-to-canonical mapping, preservation of selections, any ambiguity, and the limits of the validation in `review.md`. Supply a usable result without asking follow-up questions.

Temporary workspace files are permitted; all required final artifacts must use the exact paths above.
