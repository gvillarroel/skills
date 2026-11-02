# Contract smoke: a local typed model

Create a reusable, validated semantic model for this one supplied record. Work only in this workspace and treat the copied skill as read-only. Read only `SKILL.md` and the compact runtime references or scripts that you need. Do not read hidden files, parent repository documents, sibling skills, acceptance examples, or external sources. Do not use network services. Python and `uv` are available.

Original record: ID `source:one`, locator `provided:one`, text `The catalog can retrieve a stored procedure by name.`, selected `true`.

Write exactly `model.json`, `contract.json`, `validation.json`, and `review.md` in the workspace root. Retain the original record, including its selection. Use one `Requirement` node with a definition that preserves the retrieval behavior, source binding, and a required boolean `selected` attribute in a closed type contract. Add an executable competency check for the source binding with the exact expected node ID. There are no relations or required formal ontology claims.

Run the bundled validator with this command after writing the inputs:

```bash
uv run --script skills/curate-semantic-model/scripts/semantic_model.py validate --model model.json --contract contract.json --report validation.json
```

In `review.md`, state the chosen representation level, explain why it is sufficient, and distinguish executed contract validation from semantic review and unperformed formal checks. Do not claim global minimality. Do not write to the copied skill.

Temporary workspace files are permitted; all required final artifacts must use the exact paths above.
