# Service Observatory source

This workspace adapts the D3 operational-dashboard starter into linked graph,
metrics, table and inspector views. Change the synthetic domain source in
`../scripts/make_data.py`; generated data files are local build output.

Run `node projects/plugin-ui-rich-interfaces/scripts/build.mjs` and
`node projects/plugin-ui-rich-interfaces/scripts/verify-browser.mjs` from the
repository root. Generated packages and screenshots belong under this project's
ignored `artifacts/`, not alongside authored web sources.

See the [lab guide](../../../docs/plugin-ui-rich-interfaces.md) for the six
host routes, reproduction and evidence limits. This is a local project,
separate from published galleries and runtime skill bundles.
