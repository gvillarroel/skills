Create a release-evidence ledger for the following synthetic lab notes. These
are supplied task fixtures, not new observations of installed products.
All records concern Lab UI Host 1.4.2 unless noted otherwise.

- Its inspected `widget.ts:40` handler calls requestDisplayMode(fullscreen).
  Nobody recorded that handler executing.
- `Host Contract section 2` documents an inline resource view.
- A tester reports that the chart was visible; no automated capture exists.
- The desktop paint check was not run because the lab had no signed-in session.
- A stale-edit probe expected E_STALE and preserved revision 8. The receipt
  shows E_STALE and revision 8 unchanged.
- A save probe expected revision 9. The receipt instead shows E_UNAVAILABLE
  and revision 8 unchanged.
- A proposed canvas depends on an enabled renderer and a supported session;
  neither prerequisite has been checked.
- `Host Contract section 4` explicitly says camera access is unsupported by
  this fixture build.

Use the loaded skill's deterministic evidence workflow. Create exactly the
required artifacts `audit/evidence.md` and `audit/evidence.json`; scratch input
files are allowed outside the skill. Use the helper to derive the ledger and
its Markdown table. Preserve unknown capture versions explicitly, and keep
source declarations, reports, unperformed work and executed probes separate.
The final JSON needs normalized `evidence_records`, `sources`,
`host_acceptance_verified:false` and `task_empirical_tests_performed:false`.
Every note above must be represented. Do not design UI or add product claims.

Stay offline and use only this prompt and read-only `skills/desktop-plugin-ui/`.
No provider, model, browser, account, host, installation or UI test is allowed.
Check both exact completed outputs with the report checker in its typed mode,
inspect `passed` and repair the inputs/outputs until clean. Generated content
must follow the bundle's language contract.
