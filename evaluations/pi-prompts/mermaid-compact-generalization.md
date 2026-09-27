Prepare a Mermaid ER diagram for a lending system using the skill's normal styling defaults. Include these entity and attribute names exactly:

- READER: `int reader_id PK`, `string name`.
- BOOK: `int book_id PK`, `string title`.
- LOAN: `int loan_id PK`, `int reader_id FK`, `int book_id FK`, `date due_date`.

Every LOAN belongs to exactly one READER and exactly one BOOK. A READER can have zero or many LOAN records; a BOOK can appear in zero or many LOAN records. Use the relationship labels `borrows` for READER to LOAN and `records` for BOOK to LOAN. Include a concise accessible title and description.

Deliver `deliverables/lending.mmd` and `deliverables/check.json`. Rendering is delegated to the evaluator. Treat `skills/mermaid/` as read-only, keep generated files in this workspace, and use only the copied skill and ordinary local tools. Do not read acceptance examples or external repositories.
