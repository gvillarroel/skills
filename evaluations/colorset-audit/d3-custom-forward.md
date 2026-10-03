Create a portable circuit signal diagram at artifacts/circuit.html using the
bundled Circuit Signal Traces builder and its normal default styling. Retain
Source, Filter, Gate, Sink, Clock, Router, Store, Diagnostic and Fallback plus
their signal paths. Create an explicit full-color variant at
artifacts/circuit-cs2.html. Validate both actual generated HTML paint contracts
and render a settled preview of the default to artifacts/circuit.svg and
artifacts/circuit.png. Inspect the preview. Keep all outputs outside the
read-only skill bundle, preserve exact output paths, and do not read acceptance
examples. Report the active palette of each final artifact.

Also prepare a derived recreation seed from artifacts/circuit.svg at
artifacts/templates/circuit.seed.svg, its portable browser template at
artifacts/templates/circuit.template.html, and the editable candidate at
artifacts/expected/circuit.svg. Keep the original circuit.svg immutable.
Use the bundled dithering helper to create artifacts/circuit-dither.svg and
artifacts/circuit-dither.png with its default palette. Validate the authored
seed and dither colorsets and retain the original source signature separately.
The seed helper intentionally substitutes labels; preserve the original
circuit labels in circuit.svg and use the seed inventory for the recreation.
