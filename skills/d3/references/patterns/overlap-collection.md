# Overlap Pattern Collection

Use the pattern index to route directly to one section in this compact collection. Read only that section and any reference it explicitly names.

## d3-overlap-3-chain

### Asymmetric Three Circle Chain

- **Pattern ID:** `d3-overlap-3-chain`
- **Gallery source ID:** `overlap-3-chain`
- **Family:** Asymmetric Overlap
- **Use when:** One bridge set overlaps two endpoints while the endpoints remain mostly separate.
- **Renderer:** `renderAsymmetricThreeCircleChain`

Read `references/overlap-pattern-contracts.md`. Use Source `(184,214,r84)`, Bridge `(280,214,r84)`, and Target `(376,214,r84)` with blue, orange, and green. Keep center `(280,214)` labeled `bridge / set` and `data-layout="asymmetric-3-chain"`.

Validate 3 equal circles, overlap only along the chain, and the note `A overlaps B, B overlaps C`.

## d3-overlap-5-rosette

### Symmetric Five Circle Rosette

- **Pattern ID:** `d3-overlap-5-rosette`
- **Gallery source ID:** `overlap-5-rosette`
- **Family:** Symmetric Overlap
- **Use when:** Five equal domains need 72-degree rotational balance around one shared strategy.
- **Renderer:** `renderSymmetricFiveCircleRosette`

Read `references/overlap-pattern-contracts.md`. Place Product, Research, Infra, Design, and Risk on a ring of radius `66` around `(280,210)`; every circle has radius `96`. Keep center `shared / strategy`, guide radius `68`, and `data-layout="symmetric-5-rosette"`.

Validate equal radii, five 72-degree slots, 5 labels, and risk as the only red semantic set.

## d3-overlap-3-rosette

### Symmetric Three Circle Rosette

- **Pattern ID:** `d3-overlap-3-rosette`
- **Gallery source ID:** `overlap-3-rosette`
- **Family:** Symmetric Overlap
- **Use when:** Three equal concepts need explicit 120-degree rotational balance.
- **Renderer:** `renderSymmetricThreeCircleRosette`

Read `references/overlap-pattern-contracts.md`. Place Syntax, Meaning, and Context on a ring of radius `56` around `(280,210)`; every circle has radius `108`. Keep the center label `balanced / center`, guide radius `58`, blue/orange/green peer colors, and `data-layout="symmetric-3-rosette"`.

Validate equal radii, three angular gaps of 120 degrees, and exactly 3 source entities.

## d3-venn-5

### Venn Five Overlap

- **Pattern ID:** `d3-venn-5`
- **Gallery source ID:** `venn-5`
- **Family:** Set Overlap
- **Use when:** Five peer domains converge around one operational center.
- **Renderer:** `renderVennFiveOverlap`

Read `references/overlap-pattern-contracts.md`. Place Data, Model, Eval, Product, and Policy on a 5-slot ring of radius `64` around `(280,210)`; give every circle radius `98`. Use blue, orange, green, purple, and red respectively. Keep center radius `34` with `shared / pilot`, guide radius `66`, and `data-layout="five-circle-shared-center"`.

Validate 5 unique circles and labels, 72-degree slots, one shared center, and no label collision at the lower note.

## d3-overlap-5-cluster

### Asymmetric Five Circle Cluster

- **Pattern ID:** `d3-overlap-5-cluster`
- **Gallery source ID:** `overlap-5-cluster`
- **Family:** Asymmetric Overlap
- **Use when:** A primary three-set block needs two attached context domains.
- **Renderer:** `renderAsymmetricFiveCircleCluster`

Read `references/overlap-pattern-contracts.md`. Use Prompt `(190,178,r78)`, Model `(268,166,r82)`, Data `(236,252,r80)`, Eval `(334,244,r72)`, and Policy `(390,168,r64)`. Keep semantic center `(258,208,r30)` with `main / block`, blue/orange/green/purple/red roles, and `data-layout="asymmetric-5-cluster"`.

Validate all 5 distinct radii/centers and preserve the intended `3+2 attached context` asymmetry.

## d3-venn-7

### Venn Seven Overlap

- **Pattern ID:** `d3-venn-7`
- **Gallery source ID:** `venn-7`
- **Family:** Set Overlap
- **Use when:** Seven LLM workstreams need one visible alignment zone without implying a hierarchy.
- **Renderer:** `renderVennSevenOverlap`

Read `references/overlap-pattern-contracts.md`. Arrange Prompt, Retrieval, Memory, Tools, Evals, Safety, and Product on a 7-slot ring of radius `75` around `(280,206)`; each circle has radius `85`. Use center radius `38` with `LLM / alignment`, guide radius `78`, and `data-layout="seven-circle-ecosystem"`.

Validate exactly 7 peers, 7 external labels, one center, and preserved rotational order. Do not collapse the seven entities into a generic flower.

## d3-overlap-7-bridge

### Asymmetric Seven Circle Bridge

- **Pattern ID:** `d3-overlap-7-bridge`
- **Gallery source ID:** `overlap-7-bridge`
- **Family:** Asymmetric Overlap
- **Use when:** Two three-set blocks need one explicit bridging set.
- **Renderer:** `renderAsymmetricSevenCircleBridge`

Read `references/overlap-pattern-contracts.md`. Use seven radius-66 circles: Left A `(158,176)`, Left B `(214,144)`, Left C `(214,226)`, Bridge `(280,202)`, Right A `(346,144)`, Right B `(402,176)`, and Right C `(346,226)`. Keep semantic center `(280,206,r31)` with `bridge / circle` and `data-layout="asymmetric-7-bridge-3-1-3"`.

Validate exactly 3 left sets, 1 bridge, 3 right sets, 7 unique labels, and preserved left-to-right grouping.

## d3-venn-3

### Venn Three Circle

- **Pattern ID:** `d3-venn-3`
- **Gallery source ID:** `venn-3`
- **Family:** Set Overlap
- **Use when:** Three peer concepts need readable single, pairwise, and shared-center regions.
- **Renderer:** `renderVennThreeCircle`

Read `references/overlap-pattern-contracts.md`, then use three circles in a `560x420` viewBox: Prompt `(232,174,r92)`, Data `(328,174,r92)`, and Model `(280,252,r92)`. Use semantic center `(280,214)` with radius `31` and the two-line label `shared / meaning`. Preserve the exact three entities, use blue/orange/green in that order, and expose `data-layout="three-circle-classic"`.

Validate exactly 3 set circles, 3 external labels, one center disk, and the note `classic three-set overlap`.
