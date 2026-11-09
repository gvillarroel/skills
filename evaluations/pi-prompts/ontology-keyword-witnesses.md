Read the isolated extract-with-ontology skill's SKILL.md, references/mapping.md and references/keyword-witnesses.md. All task files you create belong at the workspace root.

Apply this fixed vocabulary to the supplied controlled-language source. The rule keys are retry-without-key and reuse-probe-key. The keyword map is MUST NOT -> forbidden, MAY -> permitted. Ignore the example sentence when deciding either rule. Use the documented local keyword helper.

Write source.txt with precisely the content encoded as this JSON string, including the trailing newline:
"Release checklist\nA retried request MUST\nNOT be sent without a request key.\nA read-only probe MAY reuse its prior request key.\nExample only: an archived note says requests MUST be resent.\n"

Write plan.json containing this JSON:
{
  "source_sha256": "157efed0e2e538a900e3c699f33de36eab01d94bc71525bdf94ef87835cc48e6",
  "keywords": [
    "MUST",
    "MUST NOT",
    "MAY"
  ],
  "units": [
    {
      "id": "release-checklist",
      "start": 18,
      "end": 127
    }
  ]
}

Execute:
```text
uv run --script skills/extract-with-ontology/scripts/index_source_keywords.py --source source.txt --plan plan.json --output witnesses.json
```

Read witnesses.json. Write review.json as a JSON object with one key per supplied rule, each value having modality and witness_id. Use the locally observed IDs and read back review.json. Use local tools only.
