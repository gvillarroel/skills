(function () {
  const SVG_NS = "http://www.w3.org/2000/svg";

  const sheets = [
    {
      id: "balance-symmetry",
      order: "01",
      tab: "Balance",
      title: "Balance and Symmetry",
      metric: "center axes, mirrored weight, quadrant balance",
      summary: "Curated variants where the pattern reads from a stable center of mass instead of a loose default layout.",
      prompt: "Use these when the larger composition needs calm, comparison, or equal visual weight."
    },
    {
      id: "diagonal-armature",
      order: "02",
      tab: "Diagonal",
      title: "Diagonal Armature",
      metric: "major diagonal, minor diagonal, reciprocal diagonals",
      summary: "Curated variants where the same pattern family is reimagined as directional movement across the frame.",
      prompt: "Use these when a story needs entry, transition, conflict, or output energy."
    },
    {
      id: "golden-root",
      order: "03",
      tab: "Golden Root",
      title: "Golden and Root Divisions",
      metric: "golden section, root-2, root-3, root-5",
      summary: "Curated variants where a dominant field and a context field are separated by proportional divisions.",
      prompt: "Use these when one view is primary and the explanation, legend, or comparison is secondary."
    },
    {
      id: "thirds-fifths-grid",
      order: "04",
      tab: "Grid",
      title: "Thirds and Fifths Grid",
      metric: "third lines, fifth lines, modular rows",
      summary: "Curated variants where the pattern becomes a modular panel that can join a larger dashboard or report.",
      prompt: "Use these when repeated examples need shared rows, columns, headings, or aligned summaries."
    },
    {
      id: "radial-rosette",
      order: "05",
      tab: "Radial",
      title: "Radial and Rosette Composition",
      metric: "center, rings, spokes, rotational balance",
      summary: "Curated variants where the pattern works as a hub, orbit, ring, spoke system, or cyclic comparison.",
      prompt: "Use these when peer concepts should orbit a shared center or when the visual story is cyclical."
    },
    {
      id: "flow-spine",
      order: "06",
      tab: "Flow",
      title: "Flow Spine",
      metric: "source, transform, checkpoint, output",
      summary: "Curated variants where the pattern becomes one stage in a larger process or narrative path.",
      prompt: "Use these when the viewer should follow a source-to-output sequence."
    },
    {
      id: "dense-label-lanes",
      order: "07",
      tab: "Dense Labels",
      title: "Dense Label and Leader Lanes",
      metric: "external lanes, clearance bands, leader underpasses",
      summary: "Curated variants where dense points, labels, or annotations are separated into readable lanes.",
      prompt: "Use these when the data field must stay visible while text remains inspectable."
    }
  ];

  const variants = [
    ["balance-symmetry", "force-network", "network", "balanced network", "Split clusters around the center axis and keep bridge nodes near the visual middle."],
    ["diagonal-armature", "force-network", "network", "diagonal network", "Place source cluster low-left and outcome cluster high-right with bridges on the major diagonal."],
    ["radial-rosette", "force-network", "network", "radial network", "Turn the graph into a hub with peer clusters orbiting in rings."],
    ["balance-symmetry", "asymmetric-task-overlap", "set-overlap", "balanced overlap", "Center the shared task field and counterweight each side with scope labels."],
    ["dense-label-lanes", "asymmetric-task-overlap-saturated", "lanes", "external label lanes", "Keep the 100-task field central and move all text to audited outside lanes."],
    ["balance-symmetry", "mirrored-beeswarm", "scatter", "mirrored distribution", "Use mirrored swarms as left/right balance around a shared baseline."],
    ["diagonal-armature", "connected-scatter", "scatter", "diagonal trajectory", "Use the path as a diagonal change vector, with labels outside the route."],
    ["thirds-fifths-grid", "scatterplot-matrix", "matrix", "matrix grid", "Make every small panel share modular row and column guides."],
    ["dense-label-lanes", "pen-label-optimizer", "lanes", "optimized labels", "Move label candidates into lanes and reserve the active field for points."],
    ["dense-label-lanes", "occlusion-labels", "lanes", "label visibility lanes", "Keep only readable labels in the data field and push secondary labels outside."],
    ["golden-root", "treemap", "hierarchy", "golden treemap", "Give the largest branch the long field and reserve the short field for context."],
    ["thirds-fifths-grid", "treemap", "hierarchy", "modular treemap", "Snap group blocks to fifth columns so it can join a dashboard grid."],
    ["balance-symmetry", "circle-pack", "hierarchy", "centered pack", "Keep parent mass centered and distribute child bubbles as counterweights."],
    ["radial-rosette", "radial-hierarchy", "hierarchy", "radial hierarchy", "Use root-to-leaf branches as spokes around a central node."],
    ["radial-rosette", "sunburst", "radial", "partition rosette", "Use nested rings to keep hierarchy and cycle visible at once."],
    ["golden-root", "sunburst", "radial", "golden radial field", "Let the radial field dominate and use a short side strip for totals."],
    ["flow-spine", "sankey", "flow", "spine sankey", "Align source, transform, and output stages on one reading path."],
    ["diagonal-armature", "sankey", "flow", "diagonal sankey", "Tilt stage centers along the diagonal to show escalation or progress."],
    ["flow-spine", "alluvial", "flow", "category handoff spine", "Use the alluvial bands as a left-to-right handoff system."],
    ["diagonal-armature", "geo-route", "route", "diagonal route", "Use the route as the major diagonal and pin waypoints to reciprocal nodes."],
    ["flow-spine", "flow-tokens", "flow", "token stream", "Use moving tokens along the spine to show cadence and direction."],
    ["flow-spine", "critical-path", "flow", "critical path spine", "Place dependencies on a clear process spine and reserve branches for risks."],
    ["diagonal-armature", "critical-path", "flow", "diagonal critical path", "Put the critical dependency path on the major diagonal."],
    ["thirds-fifths-grid", "data-table-grid", "table", "structured table grid", "Use row bands and column fifths for scan-friendly tabular comparison."],
    ["golden-root", "inline-bar-table", "table", "dominant table field", "Let values use the long field and keep notes in the short field."],
    ["thirds-fifths-grid", "pivot-heat-table", "table", "modular heat table", "Snap heat cells to a modular grid so totals and rows align."],
    ["thirds-fifths-grid", "sortable-rank-table", "table", "rank modules", "Use grid rows as stable landing positions for sorted rows."],
    ["thirds-fifths-grid", "calendar-year", "matrix", "calendar module", "Use fifth columns and repeated rows to make the calendar a dashboard tile."],
    ["thirds-fifths-grid", "waffle", "matrix", "unit grid", "Use exact modular cells for part-to-whole composition."],
    ["thirds-fifths-grid", "context-window-matrix", "matrix", "context grid", "Use the grid as a finite capacity field with clear filled and empty slots."],
    ["thirds-fifths-grid", "attention-matrix-tiles", "matrix", "attention tile grid", "Keep rows, columns, and masked regions snapped to consistent modules."],
    ["golden-root", "document-token-quality", "document", "document plus summary", "Use the document as the long field and place quality summary in the short field."],
    ["golden-root", "gemma-comparison", "table", "scorecard split", "Give metrics the long side and keep model identity or caveats in the short side."],
    ["balance-symmetry", "population-pyramid", "bar", "mirrored age bars", "Use mirrored bars as explicit left/right balance."],
    ["diagonal-armature", "slope", "bar", "slope diagonal", "Use before and after endpoints as a diagonal comparison path."],
    ["flow-spine", "bar-race", "bar", "rank movement spine", "Let bars move along a stable track with winners landing at the output end."],
    ["radial-rosette", "chord", "radial", "chord rosette", "Use symmetric ring placement for reciprocal category flow."],
    ["radial-rosette", "token-roulette-sampler", "radial", "roulette wheel", "Keep weighted probabilities on a circular field with a fixed pointer."],
    ["radial-rosette", "circular-bar", "radial", "radial magnitude", "Use equal angular slots to compare categories around a ring."],
    ["radial-rosette", "radar", "radial", "metric rosette", "Use spokes as peer metric axes around one profile center."],
    ["radial-rosette", "polar-clock", "radial", "cycle clock", "Use circular time to organize a repeated sequence."],
    ["radial-rosette", "moon-phases", "radial", "phase ring", "Place phases around a cycle so state changes feel continuous."],
    ["radial-rosette", "symmetric-five-circle-rosette", "set-overlap", "five circle rosette", "Use equal peer circles as petals around a shared concept."],
    ["flow-spine", "d3-sequence-lifelines", "flow", "sequence spine", "Use lifelines as parallel tracks along the reading path."],
    ["flow-spine", "d3-state-machine", "flow", "state transition spine", "Place start, decision, and final states on a clear process path."],
    ["flow-spine", "d3-gantt-rollout", "flow", "rollout spine", "Use time as the main spine and reserve milestones for crossing nodes."],
    ["flow-spine", "d3-git-graph", "flow", "branch spine", "Treat mainline commits as spine and branches as temporary excursions."],
    ["flow-spine", "qkv-projection-flow", "flow", "QKV split spine", "Keep token input, projection split, and attention output on one path."],
    ["flow-spine", "flashattention-blocks", "matrix", "block movement spine", "Use memory transfer as a repeated checkpoint flow."],
    ["flow-spine", "moe-router-capacity", "flow", "router spine", "Use source tokens, routing decisions, expert capacity, and overflow as stages."],
    ["flow-spine", "speculative-decoding-verify", "flow", "verify spine", "Show draft, accept, reject, and target correction as sequential checkpoints."],
    ["flow-spine", "web-load-timeline", "flow", "page load spine", "Use load phases as a single timeline with secondary lanes."],
    ["dense-label-lanes", "airports-voronoi", "lanes", "service labels", "Keep service regions visible while airport names sit in outside lanes."],
    ["dense-label-lanes", "bubble-scatter", "scatter", "bubble label lanes", "Keep bubbles in the active field and route callouts to margins."],
    ["dense-label-lanes", "point-cloud", "scatter", "point cloud lanes", "Use outside lanes for selected points so the cloud remains legible."],
    ["dense-label-lanes", "hr-diagram", "scatter", "star labels", "Reserve lane labels for standout stars while preserving dense field texture."],
    ["dense-label-lanes", "word-cloud", "labels", "word field lanes", "Use the largest words as anchors and shift secondary text into bands."],
    ["diagonal-armature", "attention-arc-decoding", "flow", "attention diagonal", "Let the next-token slot pull attention arcs along a diagonal read."],
    ["diagonal-armature", "qkv-projection-flow", "flow", "projection diagonal", "Use the diagonal to show embedding split and recombination."],
    ["diagonal-armature", "lora-rank-update", "matrix", "rank bridge", "Use a diagonal bridge between frozen matrix and low-rank update."],
    ["balance-symmetry", "kanban-assignee-virtual-legend", "table", "balanced kanban", "Use the virtual legend column as right-side counterweight."],
    ["thirds-fifths-grid", "kanban-assignee-board", "table", "kanban modules", "Snap columns and cards to consistent modular tracks."],
    ["golden-root", "token-probability-sampler", "bar", "probability focus", "Use the long field for probabilities and the short field for selected output."],
    ["balance-symmetry", "boxplot", "bar", "balanced distribution", "Center group summaries and use whiskers as horizontal counterweight."]
  ].map(([compositionId, sourceId, kind, variantTitle, recipe]) => ({
    compositionId,
    sourceId,
    kind,
    variantTitle,
    recipe,
    id: `d3-composition-${compositionId}-${sourceId}`
  }));

  const metadata = (window.D3_ANIMATED_SVG_EXAMPLES || []).map((example, index) => ({ ...example, index }));
  const sourceById = new Map(metadata.map(example => [example.id, example]));

  window.D3_COMPOSITION_SHEETS = sheets;
  window.D3_COMPOSITION_VARIANTS = variants;

  const state = {
    sheetId: resolveInitialSheetId(),
    query: ""
  };

  function resolveInitialSheetId() {
    const hash = window.location.hash.replace(/^#/, "");
    if (sheets.some(sheet => sheet.id === hash)) return hash;
    const variant = variants.find(item => item.id === hash);
    return variant ? variant.compositionId : sheets[0].id;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function el(name, attrs = {}, children = []) {
    const node = document.createElementNS(SVG_NS, name);
    for (const [key, value] of Object.entries(attrs)) {
      if (value !== undefined && value !== null) node.setAttribute(key, String(value));
    }
    for (const child of children) node.appendChild(child);
    return node;
  }

  function textNode(value) {
    return document.createTextNode(value);
  }

  function appendText(parent, x, y, value, attrs = {}) {
    const node = el("text", { x, y, ...attrs });
    node.appendChild(textNode(value));
    parent.appendChild(node);
    return node;
  }

  function addLine(parent, x1, y1, x2, y2, attrs = {}) {
    return parent.appendChild(el("line", { x1, y1, x2, y2, ...attrs }));
  }

  function addCircle(parent, cx, cy, r, attrs = {}) {
    return parent.appendChild(el("circle", { cx, cy, r, ...attrs }));
  }

  function addRect(parent, x, y, width, height, attrs = {}) {
    return parent.appendChild(el("rect", { x, y, width, height, ...attrs }));
  }

  function addPath(parent, d, attrs = {}) {
    return parent.appendChild(el("path", { d, ...attrs }));
  }

  const palette = {
    red: "#9e1b32",
    orange: "#e77204",
    yellow: "#f1c319",
    green: "#45842a",
    blue: "#007298",
    purple: "#652f6c",
    cyan: "#00ace6",
    ink: "#333e48",
    muted: "#696969",
    line: "#cfcfcf",
    softLine: "#e7e7e7",
    surface: "#ffffff",
    blueHighlight: "#cdf3ff",
    orangeHighlight: "#ffe5cc",
    yellowHighlight: "#fff4cc",
    greenHighlight: "#dbffcc",
    purpleHighlight: "#f9ccff",
    redHighlight: "#ffccd5"
  };

  function renderTabs() {
    const tabs = document.getElementById("sheet-tabs");
    tabs.innerHTML = sheets.map(sheet => {
      const count = variants.filter(variant => variant.compositionId === sheet.id).length;
      return `
        <button class="sheet-tab" type="button" id="tab-${sheet.id}" data-sheet-tab="${sheet.id}" role="tab" aria-selected="${sheet.id === state.sheetId ? "true" : "false"}">
          <span>${sheet.order} ${escapeHtml(sheet.tab)}</span>
          <span class="count-badge">${count}</span>
        </button>
      `;
    }).join("");
  }

  function armatureSvg(sheet) {
    const line = 'stroke="#333e48" stroke-opacity=".36" stroke-width="1.6"';
    const primaryGuide = 'stroke="#9e1b32" stroke-opacity=".9" stroke-width="2.4"';
    const soft = 'stroke="#007298" stroke-opacity=".46" stroke-width="1.5"';
    const mark = 'fill="#ffffff" stroke="#9e1b32" stroke-width="2"';
    const open = `<svg viewBox="0 0 480 300" role="img" aria-label="${escapeHtml(sheet.title)} armature"><rect x="18" y="18" width="444" height="264" rx="8" fill="#ffffff" stroke="#cfcfcf"/>`;
    const close = "</svg>";
    if (sheet.id === "balance-symmetry") {
      return `${open}<line x1="240" y1="18" x2="240" y2="282" ${primaryGuide}/><line x1="18" y1="150" x2="462" y2="150" ${primaryGuide}/><line x1="18" y1="18" x2="462" y2="282" ${line}/><line x1="18" y1="282" x2="462" y2="18" ${line}/><circle cx="240" cy="150" r="34" fill="#cdf3ff" stroke="#007298" stroke-width="2"/><circle cx="136" cy="150" r="18" ${mark}/><circle cx="344" cy="150" r="18" ${mark}/>${close}`;
    }
    if (sheet.id === "diagonal-armature") {
      return `${open}<line x1="18" y1="18" x2="462" y2="282" ${primaryGuide}/><line x1="18" y1="282" x2="462" y2="18" ${soft}/><line x1="18" y1="92" x2="332" y2="282" ${line}/><line x1="148" y1="18" x2="462" y2="208" ${line}/><circle cx="142" cy="92" r="16" ${mark}/><circle cx="240" cy="150" r="20" fill="#fff4cc" stroke="#e77204" stroke-width="2"/><circle cx="338" cy="208" r="16" ${mark}/>${close}`;
    }
    if (sheet.id === "golden-root") {
      return `${open}<rect x="18" y="18" width="274" height="264" fill="#cdf3ff" fill-opacity=".52"/><rect x="292" y="18" width="170" height="264" fill="#fff4cc" fill-opacity=".7"/><line x1="292" y1="18" x2="292" y2="282" ${primaryGuide}/><line x1="18" y1="120" x2="462" y2="120" ${soft}/><line x1="148" y1="18" x2="148" y2="282" ${line}/><line x1="18" y1="196" x2="462" y2="196" ${line}/><circle cx="292" cy="120" r="18" ${mark}/>${close}`;
    }
    if (sheet.id === "thirds-fifths-grid") {
      const verticals = [106.8, 195.6, 240, 284.4, 373.2].map(x => `<line x1="${x}" y1="18" x2="${x}" y2="282" ${line}/>`).join("");
      const horizontals = [70.8, 123.6, 150, 176.4, 229.2].map(y => `<line x1="18" y1="${y}" x2="462" y2="${y}" ${line}/>`).join("");
      return `${open}${verticals}${horizontals}<rect x="106.8" y="70.8" width="177.6" height="105.6" fill="#dbffcc" fill-opacity=".65" stroke="#45842a" stroke-width="2"/><rect x="284.4" y="176.4" width="88.8" height="52.8" fill="#f9ccff" fill-opacity=".7" stroke="#652f6c" stroke-width="2"/>${close}`;
    }
    if (sheet.id === "radial-rosette") {
      const spokes = Array.from({ length: 12 }, (_, index) => {
        const angle = (-90 + index * 30) * Math.PI / 180;
        return `<line x1="240" y1="150" x2="${(240 + Math.cos(angle) * 116).toFixed(2)}" y2="${(150 + Math.sin(angle) * 116).toFixed(2)}" ${line}/>`;
      }).join("");
      const petals = Array.from({ length: 6 }, (_, index) => {
        const angle = (-90 + index * 60) * Math.PI / 180;
        return `<circle cx="${(240 + Math.cos(angle) * 82).toFixed(2)}" cy="${(150 + Math.sin(angle) * 82).toFixed(2)}" r="24" fill="#cdf3ff" stroke="#007298" stroke-width="2"/>`;
      }).join("");
      return `${open}<circle cx="240" cy="150" r="116" fill="none" ${soft}/><circle cx="240" cy="150" r="64" fill="none" ${line}/>${spokes}${petals}<circle cx="240" cy="150" r="30" fill="#ffccd5" stroke="#9e1b32" stroke-width="2"/>${close}`;
    }
    if (sheet.id === "flow-spine") {
      return `${open}<path d="M58 150 C128 86 174 86 240 150 S352 214 422 150" fill="none" ${primaryGuide}/><line x1="58" y1="84" x2="58" y2="216" ${line}/><line x1="240" y1="58" x2="240" y2="242" ${soft}/><line x1="422" y1="84" x2="422" y2="216" ${line}/><circle cx="58" cy="150" r="20" fill="#cdf3ff" stroke="#007298" stroke-width="2"/><circle cx="240" cy="150" r="24" fill="#fff4cc" stroke="#e77204" stroke-width="2"/><circle cx="422" cy="150" r="20" fill="#dbffcc" stroke="#45842a" stroke-width="2"/>${close}`;
    }
    return `${open}<rect x="18" y="18" width="100" height="264" fill="#f9ccff" fill-opacity=".75"/><rect x="362" y="18" width="100" height="264" fill="#f9ccff" fill-opacity=".75"/><rect x="140" y="52" width="200" height="196" fill="#cdf3ff" fill-opacity=".42" stroke="#007298" stroke-width="2"/><line x1="140" y1="88" x2="118" y2="62" ${primaryGuide}/><line x1="340" y1="108" x2="362" y2="82" ${primaryGuide}/><line x1="140" y1="184" x2="118" y2="204" ${primaryGuide}/><line x1="340" y1="206" x2="362" y2="226" ${primaryGuide}/><circle cx="206" cy="138" r="9" ${mark}/><circle cx="268" cy="168" r="9" ${mark}/>${close}`;
  }

  function renderOverview(sheet, sheetVariants) {
    document.getElementById("sheet-overview").innerHTML = `
      <div class="armature-panel">${armatureSvg(sheet)}</div>
      <div class="sheet-copy">
        <p class="sheet-kicker">Sheet ${sheet.order}</p>
        <h2>${escapeHtml(sheet.title)}</h2>
        <p>${escapeHtml(sheet.summary)}</p>
        <p>${escapeHtml(sheet.prompt)}</p>
        <div class="sheet-metrics">
          <span class="metric"><span class="count-value">${sheetVariants.length}</span> curated variants</span>
          <span class="metric">${escapeHtml(sheet.metric)}</span>
        </div>
      </div>
    `;
  }

  function renderRows(sheet, sheetVariants) {
    const grid = document.getElementById("sheet-grid");
    grid.innerHTML = sheetVariants.map(variant => {
      const source = sourceById.get(variant.sourceId) || {};
      const patternId = source.patternId || `d3-pattern-${variant.sourceId}`;
      const title = source.title || variant.sourceId;
      const search = `${variant.id} ${patternId} ${variant.compositionId} ${variant.sourceId} ${variant.kind} ${title} ${variant.variantTitle} ${variant.recipe}`.toLowerCase();
      return `
        <article class="composition-card" id="${variant.id}" data-composition-id="${variant.compositionId}" data-example-id="${variant.sourceId}" data-pattern-id="${patternId}" data-composition-pattern-id="${variant.id}" data-kind="${variant.kind}" data-search="${escapeHtml(search)}">
          <div class="preview-frame">
            <svg id="${variant.id}-svg" data-composition-pattern-id="${variant.id}" data-pattern-id="${patternId}" role="img"></svg>
          </div>
          <div class="composition-card-body">
            <p class="pattern-kicker">${escapeHtml(sheet.tab)} / ${escapeHtml(source.kicker || variant.kind)}</p>
            <h3>${escapeHtml(title)}</h3>
            <p class="composition-id">${escapeHtml(variant.id)}</p>
            <p class="pattern-copy">${escapeHtml(variant.variantTitle)}</p>
            <p class="plan-text">${escapeHtml(variant.recipe)}</p>
          </div>
          <a class="pattern-link" href="./index.html#${encodeURIComponent(patternId)}">Open base pattern</a>
        </article>
      `;
    }).join("");
    renderPreviews(sheetVariants);
    applyFilter();
  }

  function renderPreviews(sheetVariants) {
    sheetVariants.forEach(variant => {
      const svg = document.getElementById(`${variant.id}-svg`);
      const source = sourceById.get(variant.sourceId) || {};
      if (!svg) return;
      svg.replaceChildren();
      svg.setAttribute("viewBox", "0 0 360 220");
      svg.setAttribute("aria-labelledby", `${variant.id}-title ${variant.id}-desc`);
      svg.appendChild(el("title", { id: `${variant.id}-title` }, [textNode(`${source.title || variant.sourceId} ${variant.variantTitle}`)]));
      svg.appendChild(el("desc", { id: `${variant.id}-desc` }, [textNode(variant.recipe)]));
      addRect(svg, 8, 8, 344, 204, { rx: 8, fill: palette.surface, stroke: palette.softLine });
      addGuideLayer(svg, variant.compositionId);
      renderVariantMarks(svg, variant);
    });
  }

  function addGuideLayer(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "composition-guide", "stroke-linecap": "round" }));
    const guide = { stroke: palette.line, "stroke-width": 1, "stroke-dasharray": "4 6", "stroke-opacity": 0.72 };
    if (compositionId === "balance-symmetry") {
      addLine(g, 180, 18, 180, 202, guide);
      addLine(g, 22, 110, 338, 110, guide);
    } else if (compositionId === "diagonal-armature") {
      addLine(g, 34, 186, 326, 34, { ...guide, stroke: palette.red, "stroke-opacity": 0.58 });
      addLine(g, 34, 34, 326, 186, guide);
    } else if (compositionId === "golden-root") {
      addLine(g, 220, 18, 220, 202, { ...guide, stroke: palette.red, "stroke-opacity": 0.58 });
      addLine(g, 22, 84, 338, 84, guide);
    } else if (compositionId === "thirds-fifths-grid") {
      [74, 137, 180, 223, 286].forEach(x => addLine(g, x, 22, x, 198, guide));
      [66, 110, 154].forEach(y => addLine(g, 22, y, 338, y, guide));
    } else if (compositionId === "radial-rosette") {
      addCircle(g, 180, 110, 72, { fill: "none", stroke: palette.line, "stroke-dasharray": "4 6", "stroke-opacity": 0.72 });
      addCircle(g, 180, 110, 34, { fill: "none", stroke: palette.line, "stroke-dasharray": "4 6", "stroke-opacity": 0.72 });
      for (let i = 0; i < 8; i += 1) {
        const angle = i * Math.PI / 4;
        addLine(g, 180, 110, 180 + Math.cos(angle) * 92, 110 + Math.sin(angle) * 92, guide);
      }
    } else if (compositionId === "flow-spine") {
      addPath(g, "M36 112 C108 54 252 166 324 88", { fill: "none", stroke: palette.red, "stroke-width": 1.4, "stroke-dasharray": "5 6", "stroke-opacity": 0.62 });
    } else {
      addRect(g, 22, 22, 74, 176, { fill: palette.purpleHighlight, "fill-opacity": 0.44, stroke: "none" });
      addRect(g, 264, 22, 74, 176, { fill: palette.purpleHighlight, "fill-opacity": 0.44, stroke: "none" });
    }
  }

  function renderVariantMarks(svg, variant) {
    if (variant.kind === "network") return renderNetwork(svg, variant.compositionId);
    if (variant.kind === "flow" || variant.kind === "route") return renderFlow(svg, variant.compositionId);
    if (variant.kind === "matrix") return renderMatrix(svg, variant.compositionId);
    if (variant.kind === "radial") return renderRadial(svg, variant.compositionId);
    if (variant.kind === "set-overlap") return renderSetOverlap(svg, variant.compositionId);
    if (variant.kind === "hierarchy") return renderHierarchy(svg, variant.compositionId);
    if (variant.kind === "scatter") return renderScatter(svg, variant.compositionId);
    if (variant.kind === "lanes" || variant.kind === "labels") return renderLanes(svg, variant.compositionId);
    if (variant.kind === "table" || variant.kind === "document") return renderTable(svg, variant.compositionId);
    if (variant.kind === "bar") return renderBars(svg, variant.compositionId);
    return renderGeneric(svg, variant.compositionId);
  }

  function renderNetwork(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "preview-network" }));
    let nodes;
    if (compositionId === "radial-rosette") {
      nodes = Array.from({ length: 10 }, (_, i) => {
        const angle = -Math.PI / 2 + i * Math.PI * 2 / 10;
        return { x: 180 + Math.cos(angle) * 68, y: 110 + Math.sin(angle) * 68, r: i % 3 === 0 ? 7 : 5 };
      });
      nodes.push({ x: 180, y: 110, r: 11 });
    } else if (compositionId === "diagonal-armature") {
      nodes = [
        { x: 64, y: 166, r: 10 }, { x: 94, y: 146, r: 6 }, { x: 122, y: 152, r: 6 },
        { x: 164, y: 124, r: 7 }, { x: 198, y: 106, r: 7 }, { x: 238, y: 84, r: 6 },
        { x: 276, y: 70, r: 6 }, { x: 306, y: 48, r: 10 }
      ];
    } else {
      nodes = [
        { x: 122, y: 84, r: 8 }, { x: 102, y: 128, r: 6 }, { x: 138, y: 138, r: 6 },
        { x: 180, y: 110, r: 10 }, { x: 222, y: 82, r: 6 }, { x: 252, y: 120, r: 8 }, { x: 228, y: 148, r: 6 }
      ];
    }
    const links = nodes.slice(0, -1).map((_, index) => [index, index + 1]).concat([[0, 3], [2, 3], [3, nodes.length - 1]]);
    links.forEach(([a, b], index) => addLine(g, nodes[a].x, nodes[a].y, nodes[b].x, nodes[b].y, { stroke: index % 2 ? palette.line : palette.blue, "stroke-width": 1.8, "stroke-opacity": 0.64 }));
    nodes.forEach((node, index) => addCircle(g, node.x, node.y, node.r, { fill: index === nodes.length - 1 ? palette.red : index % 2 ? palette.blueHighlight : palette.greenHighlight, stroke: index === nodes.length - 1 ? palette.red : palette.blue, "stroke-width": 1.8 }));
  }

  function renderFlow(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "preview-flow" }));
    const points = compositionId === "diagonal-armature"
      ? [[50, 170], [112, 142], [178, 112], [246, 76], [310, 46]]
      : [[44, 128], [112, 88], [180, 112], [248, 144], [316, 90]];
    points.forEach((point, index) => {
      if (index > 0) {
        const prev = points[index - 1];
        addPath(g, `M${prev[0]} ${prev[1]} C${(prev[0] + point[0]) / 2} ${prev[1] - 26}, ${(prev[0] + point[0]) / 2} ${point[1] + 26}, ${point[0]} ${point[1]}`, { fill: "none", stroke: index % 2 ? palette.blue : palette.orange, "stroke-width": 7 - index * 0.6, "stroke-opacity": 0.62, "stroke-linecap": "round" });
      }
    });
    points.forEach((point, index) => addCircle(g, point[0], point[1], index === 0 || index === points.length - 1 ? 11 : 8, { fill: index === points.length - 1 ? palette.greenHighlight : palette.surface, stroke: index === points.length - 1 ? palette.green : palette.red, "stroke-width": 2 }));
    appendText(g, points[0][0], points[0][1] + 30, "source", { "text-anchor": "middle", "font-size": 10, fill: palette.muted });
    appendText(g, points.at(-1)[0], points.at(-1)[1] + 30, "output", { "text-anchor": "middle", "font-size": 10, fill: palette.muted });
  }

  function renderMatrix(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "preview-matrix" }));
    const startX = compositionId === "golden-root" ? 46 : 58;
    const startY = 48;
    const cols = compositionId === "thirds-fifths-grid" ? 10 : 8;
    const rows = 5;
    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < cols; col += 1) {
        const value = (row * 3 + col * 5) % 10;
        addRect(g, startX + col * 22, startY + row * 22, 17, 17, { rx: 3, fill: value > 6 ? palette.redHighlight : value > 3 ? palette.blueHighlight : palette.greenHighlight, stroke: palette.surface, "stroke-width": 1 });
      }
    }
    addRect(g, startX - 8, startY - 8, cols * 22 + 2, rows * 22 + 2, { fill: "none", stroke: palette.ink, "stroke-opacity": 0.28 });
    addRect(g, 250, 54, 58, 86, { rx: 5, fill: palette.yellowHighlight, stroke: palette.orange });
    appendText(g, 279, 103, "key", { "text-anchor": "middle", "font-size": 12, "font-weight": 800, fill: palette.ink });
  }

  function renderRadial(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "preview-radial" }));
    const cx = 180;
    const cy = 110;
    addCircle(g, cx, cy, 76, { fill: palette.blueHighlight, "fill-opacity": 0.24, stroke: palette.blue, "stroke-width": 1.8 });
    addCircle(g, cx, cy, 38, { fill: palette.yellowHighlight, "fill-opacity": 0.7, stroke: palette.orange, "stroke-width": 1.8 });
    for (let i = 0; i < 10; i += 1) {
      const angle0 = -Math.PI / 2 + i * Math.PI * 2 / 10;
      const angle1 = angle0 + Math.PI * 2 / 16;
      const r0 = 46;
      const r1 = 78;
      const d = `M${cx + Math.cos(angle0) * r0} ${cy + Math.sin(angle0) * r0} L${cx + Math.cos(angle0) * r1} ${cy + Math.sin(angle0) * r1} A${r1} ${r1} 0 0 1 ${cx + Math.cos(angle1) * r1} ${cy + Math.sin(angle1) * r1} L${cx + Math.cos(angle1) * r0} ${cy + Math.sin(angle1) * r0} Z`;
      addPath(g, d, { fill: i % 3 === 0 ? palette.red : i % 3 === 1 ? palette.blue : palette.green, "fill-opacity": 0.72, stroke: palette.surface, "stroke-width": 1 });
    }
    addCircle(g, cx, cy, 17, { fill: palette.surface, stroke: palette.red, "stroke-width": 2 });
  }

  function renderSetOverlap(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "preview-set-overlap" }));
    const centers = compositionId === "radial-rosette"
      ? [[180, 68], [220, 100], [204, 148], [156, 148], [140, 100]]
      : [[132, 104], [174, 86], [218, 104], [156, 138], [202, 138]];
    centers.forEach((point, index) => {
      addCircle(g, point[0], point[1], 42, {
        fill: index % 5 === 0 ? palette.blueHighlight : index % 5 === 1 ? palette.greenHighlight : index % 5 === 2 ? palette.redHighlight : index % 5 === 3 ? palette.yellowHighlight : palette.purpleHighlight,
        "fill-opacity": 0.58,
        stroke: index % 2 ? palette.blue : palette.red,
        "stroke-width": 2
      });
    });
    addCircle(g, 180, 114, 10, { fill: palette.surface, stroke: palette.ink, "stroke-width": 1.8 });
    [[92, 68], [268, 68], [92, 162], [268, 162]].forEach((point, index) => {
      addRect(g, point[0], point[1], 42, 12, { rx: 4, fill: palette.surface, stroke: index % 2 ? palette.blue : palette.green });
      addLine(g, point[0] + (point[0] < 180 ? 42 : 0), point[1] + 6, 180, 114, { stroke: palette.line, "stroke-width": 1, "stroke-opacity": 0.72 });
    });
  }

  function renderHierarchy(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "preview-hierarchy" }));
    const root = compositionId === "golden-root" ? [114, 84] : [180, 62];
    const children = compositionId === "golden-root"
      ? [[70, 140], [128, 146], [190, 126], [254, 152]]
      : [[86, 146], [144, 136], [216, 136], [274, 146]];
    children.forEach((point, index) => {
      addPath(g, `M${root[0]} ${root[1]} C${root[0]} ${(root[1] + point[1]) / 2}, ${point[0]} ${(root[1] + point[1]) / 2}, ${point[0]} ${point[1]}`, { fill: "none", stroke: index % 2 ? palette.blue : palette.green, "stroke-width": 2, "stroke-opacity": 0.72 });
      addCircle(g, point[0], point[1], 16 + index * 2, { fill: index % 2 ? palette.blueHighlight : palette.greenHighlight, stroke: index % 2 ? palette.blue : palette.green, "stroke-width": 1.8 });
    });
    addCircle(g, root[0], root[1], 20, { fill: palette.redHighlight, stroke: palette.red, "stroke-width": 2 });
  }

  function renderScatter(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "preview-scatter" }));
    const points = Array.from({ length: 38 }, (_, index) => {
      const angle = index * 2.399;
      const radius = compositionId === "balance-symmetry" ? 18 + (index % 9) * 8 : 12 + index * 2.5;
      const x = compositionId === "diagonal-armature" ? 58 + index * 7 : 180 + Math.cos(angle) * radius;
      const y = compositionId === "diagonal-armature" ? 168 - index * 3.3 + Math.sin(angle) * 10 : 110 + Math.sin(angle) * radius * 0.62;
      return { x, y, r: 2.8 + (index % 4) * 0.8 };
    });
    points.forEach((point, index) => addCircle(g, point.x, point.y, point.r, { fill: index % 5 === 0 ? palette.red : index % 2 ? palette.blue : palette.green, "fill-opacity": 0.72, stroke: palette.surface, "stroke-width": 0.8 }));
    addPath(g, compositionId === "diagonal-armature" ? "M54 172 L306 48" : "M78 110 H282", { stroke: palette.ink, "stroke-opacity": 0.32, "stroke-width": 2, fill: "none" });
  }

  function renderLanes(svg) {
    const g = svg.appendChild(el("g", { class: "preview-lanes" }));
    addRect(g, 112, 44, 136, 124, { rx: 6, fill: palette.blueHighlight, "fill-opacity": 0.42, stroke: palette.blue });
    for (let i = 0; i < 22; i += 1) {
      const x = 132 + (i * 37) % 96;
      const y = 62 + (i * 29) % 82;
      addCircle(g, x, y, 3.2, { fill: i % 3 === 0 ? palette.red : i % 3 === 1 ? palette.blue : palette.orange, stroke: palette.surface, "stroke-width": 0.8 });
      const left = i % 2 === 0;
      const laneX = left ? 28 : 282;
      const laneY = 30 + (i % 8) * 20;
      addLine(g, x, y, laneX + (left ? 70 : 0), laneY + 7, { stroke: i % 3 === 0 ? palette.red : palette.blue, "stroke-width": 1, "stroke-opacity": 0.44 });
    }
    for (let i = 0; i < 8; i += 1) {
      addRect(g, 24, 28 + i * 20, 74, 12, { rx: 3, fill: palette.surface, stroke: palette.line });
      addRect(g, 262, 28 + i * 20, 74, 12, { rx: 3, fill: palette.surface, stroke: palette.line });
    }
  }

  function renderTable(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "preview-table" }));
    const x = compositionId === "golden-root" ? 42 : 54;
    const y = 46;
    const cols = compositionId === "golden-root" ? 4 : 5;
    const rows = 5;
    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < cols; col += 1) {
        addRect(g, x + col * 42, y + row * 24, 36, 16, { rx: 2, fill: row === 0 ? palette.redHighlight : palette.surface, stroke: palette.line });
        if (row > 0 && col === cols - 1) {
          addRect(g, x + col * 42 + 5, y + row * 24 + 5, 20 + (row * 3) % 11, 5, { rx: 2, fill: row % 2 ? palette.blue : palette.green, stroke: "none" });
        }
      }
    }
    if (compositionId === "golden-root") {
      addRect(g, 248, 54, 64, 82, { rx: 6, fill: palette.yellowHighlight, stroke: palette.orange });
      appendText(g, 280, 100, "note", { "text-anchor": "middle", "font-size": 12, "font-weight": 800, fill: palette.ink });
    }
  }

  function renderBars(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "preview-bars" }));
    const values = [44, 72, 58, 96, 66, 84];
    values.forEach((value, index) => {
      const x = 70 + index * 36;
      const y = 166 - value;
      addRect(g, x, y, 22, value, { rx: 3, fill: index % 2 ? palette.blue : palette.green, "fill-opacity": 0.82, stroke: palette.surface });
      if (compositionId === "diagonal-armature") addCircle(g, x + 11, y, 4, { fill: palette.red });
    });
    addLine(g, 52, 166, 310, 166, { stroke: palette.ink, "stroke-opacity": 0.42 });
    if (compositionId === "diagonal-armature") addLine(g, 70, 154, 270, 66, { stroke: palette.red, "stroke-width": 2, "stroke-opacity": 0.72 });
  }

  function renderGeneric(svg) {
    const g = svg.appendChild(el("g", { class: "preview-generic" }));
    addRect(g, 70, 58, 92, 92, { rx: 7, fill: palette.blueHighlight, stroke: palette.blue, "stroke-width": 2 });
    addRect(g, 188, 72, 98, 64, { rx: 7, fill: palette.greenHighlight, stroke: palette.green, "stroke-width": 2 });
    addPath(g, "M158 104 C186 64 216 154 246 110", { fill: "none", stroke: palette.red, "stroke-width": 3, "stroke-linecap": "round" });
  }

  function renderSheet() {
    const sheet = sheets.find(item => item.id === state.sheetId) || sheets[0];
    const sheetVariants = variants.filter(variant => variant.compositionId === sheet.id);
    state.sheetId = sheet.id;
    document.body.dataset.activeCompositionSheet = sheet.id;
    window.location.hash = sheet.id;
    renderTabs();
    renderOverview(sheet, sheetVariants);
    renderRows(sheet, sheetVariants);
  }

  function applyFilter() {
    const query = state.query.trim().toLowerCase();
    const rows = Array.from(document.querySelectorAll(".composition-card"));
    let visible = 0;
    rows.forEach(row => {
      const matches = !query || row.dataset.search.includes(query);
      row.hidden = !matches;
      if (matches) visible += 1;
    });
    document.body.dataset.visibleVariantCount = String(visible);
  }

  function bindEvents() {
    document.getElementById("sheet-tabs").addEventListener("click", event => {
      const button = event.target.closest("[data-sheet-tab]");
      if (!button) return;
      state.sheetId = button.dataset.sheetTab;
      renderSheet();
    });
    document.getElementById("pattern-search").addEventListener("input", event => {
      state.query = event.target.value;
      applyFilter();
    });
    window.addEventListener("hashchange", () => {
      const next = resolveInitialSheetId();
      if (next === state.sheetId) return;
      state.sheetId = next;
      renderSheet();
    });
  }

  function renderEmptyState(message) {
    document.getElementById("sheet-overview").innerHTML = `<div class="sheet-copy"><h2>${escapeHtml(message)}</h2></div>`;
  }

  function init() {
    document.body.dataset.compositionSheetCount = String(sheets.length);
    document.body.dataset.compositionVariantCount = String(variants.length);
    document.getElementById("sheet-count").textContent = String(sheets.length);
    document.getElementById("variant-count").textContent = String(variants.length);
    if (!metadata.length) {
      renderEmptyState("Pattern metadata is unavailable.");
      return;
    }
    bindEvents();
    renderSheet();
  }

  init();
})();
