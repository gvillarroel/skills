# Review two versioned Draft 7 schema comparisons

Use the schema validation graph workflow from the provided skill.
Write the following three JSON objects as separate schema files. Use
the complete objects in the specified order, with any JSON formatting.

Write before.json.

    {"$schema":"http://json-schema.org/draft-07/schema#","allOf":[{"oneOf":[{"type":"object","properties":{"scan":{"type":"string"}},"required":["scan"]},{"type":"object","properties":{"receipt":{"type":"string"}},"required":["receipt"]}]},{"type":"object","additionalProperties":false,"properties":{"scan":{"type":"string"},"receipt":{"type":"string"}}}]}

Write refactor.json.

    {"$schema":"http://json-schema.org/draft-07/schema#","$ref":"#/definitions/check","definitions":{"check":{"type":"object","additionalProperties":false,"properties":{"scan":{"type":"string"},"receipt":{"type":"string"}},"oneOf":[{"required":["receipt"]},{"required":["scan"]}]}}}

Write change.json.

    {"$schema":"http://json-schema.org/draft-07/schema#","type":"object","additionalProperties":false,"properties":{"scan":{"type":"string"},"receipt":{"type":"string"}},"anyOf":[{"required":["receipt"]},{"required":["scan"]}]}

Run the bundled schema graph checker on before.json and refactor.json.
Write its original report to refactor-report.json. Run it separately on
before.json and change.json and write change-report.json. Preserve the
three inputs. The two checker reports are required artifacts. In the
short final reply describe what each report establishes.
