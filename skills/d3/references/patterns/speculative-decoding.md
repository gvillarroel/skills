# Speculative Decode Verify

## Contents

- [Reuse Contract](#reuse-contract)
- [Parameterized Builder](#parameterized-builder)
- [Source Excerpt](#source-excerpt)

- **Pattern ID:** `d3-speculative-decoding`
- **Gallery source ID:** `speculative-decoding`
- **Family:** Inference
- **Use when:** Draft tokens branch ahead while the target model accepts a prefix and rejects the tail.
- **Renderer:** `renderSpeculativeDecodingVerify`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.
- Adapt caption anchors and complete text envelopes with the geometry when changing the source viewport. Keep the resumed-token caption inside the requested width; wrap or reposition it instead of enlarging the canvas. Inspect a settled preview at that size before accepting the illustration.

## Parameterized Builder

For a linear draft proposal, accepted prefix, rejected tail, and target continuation, run `scripts/build_speculative_decoding.py --help` and use the builder. It writes the requested HTML and SVG together, uses the bundled palette, supplies native finite animation and HTML replay, and keeps the moving indicator away from text. Pass the user's literal tokens in order; do not substitute the excerpt's sample data. The optional `--alternate POSITION:LABEL` attaches one alternate to a 1-based draft position.

```powershell
python <d3-skill>/scripts/build_speculative_decoding.py --output-html out/decode.html --output-svg out/decode.svg --draft-token the --draft-token answer --draft-token is --draft-token 42 --accepted-count 3 --resume-token next --colorset colorset2 --width 720 --height 440
python <d3-skill>/scripts/check_self_contained_html.py out/decode.html
python <d3-skill>/scripts/check_palette_contract.py out/decode.html --colorset colorset2 --require-extended
python <d3-skill>/scripts/check_palette_contract.py out/decode.svg --colorset colorset2 --require-extended
python <d3-skill>/scripts/check_visual_contract.py out/decode.svg --require-attribute "viewBox=0 0 720 440" --require-text the --require-text answer --require-text is --require-text 42 --require-text next
uv run --script <d3-skill>/scripts/verify_speculative_decoding.py out/decode.html --svg out/decode.svg --screenshot scratch/preview.png --json-report scratch/browser-check.json
```

Choose colorset1 unless the user requests colorset2. Use the corresponding palette flag and omit `--require-extended` for colorset1. Create scratch output in the writable workspace. Run the bundled browser verifier with `uv run --script`: it declares Playwright, falls back to installed Edge/Chrome, clicks Replay twice, checks settled/reduced-motion text and matching viewports, and writes the inspection PNG. Inspect that PNG and check that token labels remain readable during motion. Use this verifier rather than constructing an iframe or ad hoc replay harness. The SVG is meaningful even when its finite animation is disabled. Check HTML-specific controls such as Replay against the HTML; the portable SVG intentionally contains only the explanation. `check_visual_contract.py` accepts repeated `--require-text`, not the report builder's `--required-term`.

The builder supports 1–12 tokens and one alternate per draft position, subject to readable fit at the exact requested dimensions. It rejects empty/control-character labels, invalid prefix counts, dense layouts, and output paths inside the skill before writing. For other branch structures, unusually long tokens, or smaller viewports, use the source excerpt and focused helpers to build custom geometry; preserve the literal data, palette, exact viewport, visibility and replay checks. Do not post-edit builder output for supported inputs.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderSpeculativeDecodingVerify() {
    const svg = prepareSvg("speculative-decoding", "Speculative decoding verify", "A draft model proposes future tokens while the target model accepts a prefix and rejects the divergent tail.");
    const x = d3.scalePoint().domain(d3.range(6)).range([66, 494]);
    const nodes = [
      { id: "prompt", label: "prompt", x: x(0), y: 196, status: "base", color: palette.ink },
      { id: "draft1", label: "the", x: x(1), y: 196, status: "accept", color: palette.blue },
      { id: "draft2", label: "answer", x: x(2), y: 196, status: "accept", color: palette.blue },
      { id: "draft3", label: "is", x: x(3), y: 196, status: "accept", color: palette.green },
      { id: "draft4", label: "42", x: x(4), y: 196, status: "reject", color: palette.red },
      { id: "target", label: "next", x: x(5), y: 196, status: "target", color: palette.purple },
      { id: "alt2", label: "maybe", x: x(2), y: 126, status: "branch", color: palette.gray400 },
      { id: "alt3", label: "was", x: x(3), y: 126, status: "branch", color: palette.gray400 },
      { id: "alt4", label: "late", x: x(4), y: 276, status: "branch", color: palette.gray400 }
    ];
    const byId = new Map(nodes.map(node => [node.id, node]));
    const line = d3.line().x(d => d.x).y(d => d.y).curve(d3.curveMonotoneX);
    const draftPath = line(["prompt", "draft1", "draft2", "draft3", "draft4"].map(id => byId.get(id)));
    const acceptedPath = line(["prompt", "draft1", "draft2", "draft3"].map(id => byId.get(id)));
    const rejectedPath = line(["draft3", "draft4", "target"].map(id => byId.get(id)));

    svg.append("rect").attr("x", 52).attr("y", 62).attr("width", 456).attr("height", 44).attr("rx", 10).attr("fill", palette.yellowHighlight).attr("stroke", palette.gold).attr("stroke-width", 2);
    const sweep = svg.append("rect").attr("x", 66).attr("y", 72).attr("width", 396).attr("height", 24).attr("rx", 6).attr("fill", palette.gold);
    sweep.append("animate").attr("attributeName", "width").attr("from", 0).attr("to", 396).attr("dur", "1.15s").attr("begin", ".8s").attr("fill", "freeze");
    svg.append("text").attr("class", "mark-label").attr("x", 280).attr("y", 90).attr("text-anchor", "middle").attr("font-weight", 800).text("target model verifies draft tokens in parallel");

    const branchLinks = [
      ["draft1", "alt2", palette.gray300],
      ["alt2", "alt3", palette.gray300],
      ["draft3", "alt4", palette.gray300]
    ];
    branchLinks.forEach(([sourceId, targetId, stroke], i) => {
      const source = byId.get(sourceId);
      const target = byId.get(targetId);
      const path = svg.append("path")
        .attr("d", line([source, { x: (source.x + target.x) / 2, y: target.y }, target]))
        .attr("fill", "none")
        .attr("stroke", stroke)
        .attr("stroke-width", 2)
        .attr("stroke-linecap", "round")
        .attr("stroke-opacity", .72);
      drawPath(path, .25 + i * .12, .7);
    });

    const draft = svg.append("path")
      .attr("id", "speculative-decoding-draft")
      .attr("d", draftPath)
      .attr("fill", "none")
      .attr("stroke", palette.gray300)
      .attr("stroke-width", 3)
      .attr("stroke-linecap", "round");
    drawPath(draft, .18, 1.05);
    const accept = svg.append("path")
      .attr("d", acceptedPath)
      .attr("fill", "none")
      .attr("stroke", palette.green)
      .attr("stroke-width", 5)
      .attr("stroke-linecap", "round")
      .attr("stroke-opacity", .62);
    drawPath(accept, 1.05, .75);
    const reject = svg.append("path")
      .attr("d", rejectedPath)
      .attr("fill", "none")
      .attr("stroke", palette.red)
      .attr("stroke-width", 3)
      .attr("stroke-linecap", "round")
      .attr("stroke-opacity", .72);
    drawPath(reject, 1.35, .65);

    const dot = svg.append("circle").attr("r", 6).attr("fill", palette.orange).attr("stroke", palette.surface).attr("stroke-width", 2);
    dot.append("animateMotion")
      .attr("dur", "1.2s")
      .attr("begin", ".24s")
      .attr("fill", "freeze")
      .append("mpath")
      .attr("href", "#speculative-decoding-draft");

    const nodeGroups = svg.append("g").selectAll("g.spec-node").data(nodes).join("g")
      .attr("class", "spec-node")
      .attr("transform", d => `translate(${d.x},${d.y})`);
    nodeGroups.append("rect")
      .attr("x", -29)
      .attr("y", -17)
      .attr("width", 58)
      .attr("height", 34)
      .attr("rx", 8)
      .attr("fill", d => d.status === "branch" ? palette.gray100 : d.color)
      .attr("stroke", d => d.status === "reject" ? palette.redHover : palette.surface)
      .attr("stroke-width", d => d.status === "reject" ? 2.4 : 1.4);
    nodeGroups.append("text")
      .attr("class", d => d.status === "branch" ? "mark-label" : "reverse-label")
      .attr("x", 0)
      .attr("y", 5)
      .attr("text-anchor", "middle")
      .attr("font-weight", 800)
      .style("font-size", "10px")
      .text(d => d.label);
    fadeIn(nodeGroups, .08, .36);

    [
      { id: "draft1", text: "accept", color: palette.green },
      { id: "draft2", text: "accept", color: palette.green },
      { id: "draft3", text: "accept", color: palette.green },
      { id: "draft4", text: "drop", color: palette.red }
    ].forEach((badge, i) => {
      const node = byId.get(badge.id);
      const group = svg.append("g").attr("transform", `translate(${node.x},${node.y + 43})`);
      group.append("rect").attr("x", -22).attr("y", -13).attr("width", 44).attr("height", 21).attr("rx", 7).attr("fill", badge.color);
      group.append("text").attr("class", "reverse-label").attr("x", 0).attr("y", 2).attr("text-anchor", "middle").style("font-size", "9px").text(badge.text);
      fadeIn(group, 1.2 + i * .12, .24);
    });

    svg.append("text").attr("class", "caption").attr("x", 68).attr("y", 342).text("accepted prefix commits immediately");
    svg.append("text").attr("class", "caption").attr("x", 352).attr("y", 342).text("target resumes after mismatch");
  }
```
