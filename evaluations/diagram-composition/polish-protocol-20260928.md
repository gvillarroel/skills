# Composition polish evaluation protocol — 2026-09-28

## Objective and baseline

Improve the actual rendered quality of compact compositions, especially lines
that remain visible inside boxes and color application that looks inconsistent.
Preserve semantic decomposition, non-flow form choice, readable fixed-size grids,
SVG icons, and consistent concept identities. Passing an existing audit is not
sufficient evidence of visual quality.

The unchanged 16-file baseline is saved under the ignored local run directory
`evaluations/runs/diagram-polish-20260928-baseline/diagram-composition/` together
with the existing workspace SVG and screenshot. The previous runtime digest is
`a4c8124edb83d051adbecf8f067b60dccd8ebdbad25c3ee1b2c0c0d23a1d77fa`.

Observed gaps before changes: cross-panel paths are painted after every panel;
the audit tests text intersection but not object interiors, terminal direction,
or connector-to-connector ambiguity. Color checks inspect tagged channels but
can overlook a conflicting fill beside a correct tagged stroke. Prior fixtures
also show very long identity routes, shared unlabeled endpoints, and oversized
containers with sparse centered content.

## Acceptance dimensions

1. Terminal geometry: connectors contact the intended object boundary, approach
   from outside, and stop there. Arrowheads remain outside node interiors. A
   line may cross a containing region when it targets a child, but it must not
   cross unrelated semantic objects, labels, icons, or colored accents.
2. Layering and routing: opaque node surfaces hide background wiring without
   erasing meaningful endpoints. Repair avoidable crossings and coincident
   routes; do not make edges disappear wholesale or drop declared relations to
   pass. Nested containers and transparent groups retain their meanings.
3. Color: a concept preserves its palette across all occurrences. A correct
   token cannot cover a conflicting dominant fill or an obscured accent. Text
   remains readable; official brand artwork is excluded from semantic recoloring.
4. Composition: preserve fixed viewing scale, facts, requested spans and exact
   outputs. Keep form selection truthful and avoid unnecessary connector detours,
   empty stretched cards, duplicate prose, and technical color codes in legends.
5. Evaluation: retain the baseline, negative controls, positive controls, all
   forward attempts, exact frozen payloads, independent artifact checks, and
   screenshot-based reviews. Do not count a paint-only pass as full quality.

## Validation plan

Add deterministic controls for intrusion, wrong-side approach, obstacle routing,
endpoint binding, rounded/elliptical objects, nested boundaries, style overrides,
conflicting node fills, low-contrast labels, and obscured accents. Include correct
counterexamples so the verifier does not merely reject complex drawings.

Run strict isolated `pi` tests on a frozen final candidate: one command contract,
three naturalistic requests, a boundary/recovery case, and three fresh-domain
generalizations. Each naturalistic/generalization cohort requires at least 2/3
joint strict/artifact/manual passes; every final handoff artifact must pass.
Use the documented Luna model exception from the previous release after the
same-session Spark provider rejection; do not claim Spark validation.

Review screenshots independently at the requested display size. Validate exact
paths, source hashes, semantic relations, paint, readable labels, and skill-only
read surfaces. Run repository validators and local sync/check before marking the
skill done. Keep unrelated working-tree changes intact and generated media out
of versioned skill payloads. No publication is required for this local polish.
