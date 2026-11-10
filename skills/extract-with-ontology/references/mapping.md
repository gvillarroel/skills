# Map files into a supplied ontology

## Establish the inputs

- Record the ontology IRI or name, version and byte digest, the local
  import closure actually used, and a roster of source files with stable
  IDs and versions. Bind model-relative terms to exact IRIs or schema
  identifiers. Ask for the effective version when competing versions
  would change the result and the source cannot resolve the choice.
- Keep the supplied ontology separate from extracted instance data.
  Map input facts to classes, properties, and controlled values already
  present in the effective vocabulary. Preserve an unmapped claim, term,
  or qualified relationship as a source-linked candidate for review.
  When the schema specifies a closed list of values, keep an unmatched
  source value in review with its original wording and locator.
- For spreadsheets and CSV, retain table, row and column context and
  distinguish blanks from asserted values. For rendered files or OCR,
  retain page and region locators and flag uncertain reading. Use stable
  exact source fragments for text, keeping the surrounding section or
  governing authority when it changes the interpretation.

When the source units have stable locators, select their IDs and copy
the quoted text from the source bytes. For a claim that spans files,
retain the distinct locators that establish the assertion and any
identity link or governing condition it depends on. Repeated names or
codes can help find passages. Verify their meaning in the cited records.

For UTF-8 files with line numbers, use the [evidence binder](artifacts.md#bind-exact-text-from-selected-lines)
to derive quotes and offsets directly from the pinned source and your
selected lines.

## Resolve evidence and identity

For each candidate, identify subject, predicate, object, type or unit,
polarity, scope, and source evidence. Use the property in its stated
direction. Check its meaning against the text and ontology, even when
the source and ontology use the same label.

Use source and ontology identifiers or explicitly supported aliases for
identity. Keep same-name individuals separate when their identifiers or
contexts differ. Create new individual IRIs under a documented stable
scheme when supported and permitted by the task. Bind IDs to durable
source identifiers, including the source namespace when identifiers are
local. Leave uncertain identity links in review.

Preserve datatype, precision, unit, language, time, and modality.
Keep a negated, hypothetical, or conditional mention out of the
positive fact graph unless the existing schema can represent it with
the evidence intact. Use separate evidence fragments when a claim
needs a table header, antecedent, operative edition, or another source
unit. If files conflict within comparable scopes, show both statements
and their evidence. Use a precedence rule only when the input or user
establishes one.

## Keep alternatives at their supported scope

- If the source explicitly asserts both facts, retain both with their
  evidence. Record any violation of a supplied constraint separately.
  Keep source-supported assertions distinguishable from a consumer's
  validated subset if the task calls for both.
- If a source says “A or B” without identifying which is true, keep the
  whole alternative and its qualifiers. Represent it in the supplied
  model only when there is a lossless expression for that alternative.
  Otherwise record the candidates and the evidence together in review.
  An identity ambiguity and an explicit domain rule are different cases.
- Apply inclusive or exclusive choice only where the supplied model or
  source establishes it. Distinguish a choice per value from a choice
  among whole record patterns. If several files provide evidence for
  one branch, verify that their identifiers and scope match.

## Review and validate

Check the file roster and summarize the claims accepted, withheld,
and not assessed. Give each withheld claim its locator, proposed mapping
when available, and reason. For accepted claims, check that the cited
evidence supports the actual subject, property, object, and qualifiers.

Run supplied SHACL shapes separately when appropriate. Pin the shapes,
data graph and optional ontology/inference regime. Record how the
shapes select focus nodes, especially when missing data can remove a
node from the target. A class target can include subclass instances
through hierarchy triples in the data graph with inference disabled.
For alternative patterns, inspect records that
satisfy each branch alone, both, and neither. Check mixed values for a
per-value constraint and a record outside the target when relevant.
Distinguish the count of conforming branches, the count of qualifying
values, and the count of all values on the supplied path.
Use the supplied shape's observed outcome and cite its focus node and
component. Treat OWL domain and range as type entailments. Record a
missing value as unestablished or as a violation of an applicable
record check. Keep inferred triples in a separately identified output
with their derivation basis.
