# Visual Metaphor Design

## Concept claim

Plant growth is a chain of visible conversions: environmental inputs activate a seed, roots collect resources, leaves turn inputs into sugars, transport routes those sugars to growth zones, and mature plants make new seeds.

## Mechanic

Inputs enter a living system and become material growth. The core verbs are enter, split, rise, convert, route, divide, enlarge, and return.

## Candidate metaphors

- Factory pipeline: clear input/output logic for photosynthesis, but too industrial for germination and life cycle.
- Lifecycle wheel: strong ending and continuity, but weak for showing intake and internal transport.
- Living transport map: roots, veins, and stems become routes where particles visibly move, and the lifecycle wheel appears only when it is semantically needed.

## Chosen metaphor

Use a living transport map that gradually changes scale: seed cutaway, root intake, shoot emergence, leaf conversion chamber, growth-zone routing, and final lifecycle wheel. This keeps the same plant identity while letting each shot use the right visual grammar.

## Visual vocabulary

- Seed: warm yellow oval with a darker coat; it changes state by swelling and cracking.
- Water: blue droplets and blue upward stream.
- Oxygen and CO2: small air particles with distinct labels and motion directions.
- Minerals: orange and purple dots in soil, entering only through roots.
- Plant tissue: green strokes and leaf shapes; growth is represented by extension, unfolding, and cell division.
- Sugar: purple square packets; sugar always moves from leaves toward growth zones.
- Xylem: blue upward route; phloem: purple downward/outward route.
- Cycle: radial ring only in the final scene, where continuation is the concept.

## Reuse decision

The renderer reuses the repository's deterministic HTML/SVG capture pattern and D3 for SVG drawing. It does not reuse an existing D3 gallery scene because the plant growth mechanism needs domain-specific root, leaf, transport, and lifecycle geometry.

## Narration split

There is no recorded narration. The frame uses concise labels for biological nouns only: seed, water, roots, leaves, CO2, sugars, O2, xylem, phloem, new cells, and seeds. It avoids paragraph explanations on screen.
