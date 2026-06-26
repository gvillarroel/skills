(function () {
  const sheets = [
    {
      id: "balance-symmetry",
      order: "01",
      tab: "Balance",
      title: "Balance and Symmetry",
      metric: "center axes, mirrored weight, quadrant balance",
      summary: "Use the vertical and horizontal center lines to make dense or asymmetric data feel stable inside a larger page.",
      prompt: "Treat the main mark cluster as the center mass; use secondary labels, legends, or annotations as counterweight."
    },
    {
      id: "diagonal-armature",
      order: "02",
      tab: "Diagonal",
      title: "Diagonal Armature",
      metric: "major diagonal, minor diagonal, reciprocal diagonals",
      summary: "Use diagonal motion to connect origin, transformation, and result when a pattern needs directional energy.",
      prompt: "Place the strongest entry and exit marks on opposing corners, then let links, paths, or labels support the diagonal."
    },
    {
      id: "golden-root",
      order: "03",
      tab: "Golden Root",
      title: "Golden and Root Divisions",
      metric: "golden section, root-2, root-3, root-5",
      summary: "Use proportional divisions for editorial or explanatory layouts where one dominant field needs a supporting field.",
      prompt: "Anchor the main data field on the long section and reserve the short section for legend, explanation, or comparison."
    },
    {
      id: "thirds-fifths-grid",
      order: "04",
      tab: "Grid",
      title: "Thirds and Fifths Grid",
      metric: "third lines, fifth lines, modular rows",
      summary: "Use a modular grid when many patterns need to sit together as a larger dashboard, catalog, or report page.",
      prompt: "Snap titles, axes, panel breaks, tables, and small multiples to a shared set of rows and columns."
    },
    {
      id: "radial-rosette",
      order: "05",
      tab: "Radial",
      title: "Radial and Rosette Composition",
      metric: "center, rings, spokes, rotational balance",
      summary: "Use radial order when categories, cycles, or peer concepts orbit a shared center.",
      prompt: "Put the semantic hub at center, then distribute peers around rings or spokes without letting text fight the radius."
    },
    {
      id: "flow-spine",
      order: "06",
      tab: "Flow",
      title: "Flow Spine",
      metric: "source, transform, checkpoint, output",
      summary: "Use a reading-order spine when the pattern contributes one stage to a larger process or story.",
      prompt: "Assign each pattern to a source-transform-result role and keep labels outside the primary movement path."
    },
    {
      id: "dense-label-lanes",
      order: "07",
      tab: "Dense Labels",
      title: "Dense Label and Leader Lanes",
      metric: "external lanes, clearance bands, leader underpasses",
      summary: "Use external lanes when the pattern has many labels, dots, routes, or annotations competing with the data field.",
      prompt: "Keep data marks in the active field, move text to lanes, and route leaders as a readable secondary layer."
    }
  ];

  const macros = {
    "balance-symmetry": ["center anchor", "left counterweight", "right counterweight", "upper context", "lower support"],
    "diagonal-armature": ["entry corner", "diagonal bridge", "turning node", "exit corner", "counter diagonal"],
    "golden-root": ["large field", "short field", "golden hinge", "root guide", "margin reserve"],
    "thirds-fifths-grid": ["module tile", "row strip", "column strip", "summary cell", "detail cell"],
    "radial-rosette": ["hub", "outer petal", "orbit segment", "radial label", "center support"],
    "flow-spine": ["source", "transform", "handoff", "checkpoint", "output"],
    "dense-label-lanes": ["label lane", "anchor cluster", "underpass route", "clearance band", "focus marker"]
  };

  const fitRules = {
    "balance-symmetry": {
      strong: ["symmetric", "rosette", "flower", "pyramid", "radar", "correlogram", "matrix", "waffle", "venn", "overlap", "box", "violin", "circle pack"],
      ready: ["hierarchy", "tree", "treemap", "kanban", "table", "heat", "parallel", "profile", "comparison", "scatter"]
    },
    "diagonal-armature": {
      strong: ["route", "flow", "sankey", "alluvial", "slope", "bump", "line", "connected", "arc", "trajectory", "path", "network", "dag", "state", "sequence"],
      ready: ["scatter", "map", "attention", "projection", "zoom", "curve", "dependency", "bridge", "gantt"]
    },
    "golden-root": {
      strong: ["treemap", "sunburst", "icicle", "hierarchy", "pack", "document", "table", "scorecard", "comparison", "dashboard", "rank"],
      ready: ["bar", "matrix", "calendar", "heat", "map", "annotation", "model", "token", "density"]
    },
    "thirds-fifths-grid": {
      strong: ["table", "matrix", "heat", "calendar", "waffle", "kanban", "bar", "histogram", "rank", "profile", "small", "grid", "context"],
      ready: ["scatter", "map", "diagram", "gantt", "document", "tile", "column", "row"]
    },
    "radial-rosette": {
      strong: ["radial", "circular", "polar", "sunburst", "pie", "donut", "rosette", "flower", "orbit", "clock", "star", "solar", "rope", "roulette", "circle"],
      ready: ["network", "hierarchy", "chord", "radar", "projection", "cyclic", "arc"]
    },
    "flow-spine": {
      strong: ["sankey", "alluvial", "flow", "pipeline", "sequence", "gantt", "state", "git", "kanban", "journey", "attention", "qkv", "lora", "flash", "moe", "decode", "cache", "load"],
      ready: ["temporal", "transition", "line", "route", "network", "tree", "rank", "sort"]
    },
    "dense-label-lanes": {
      strong: ["label", "overlap", "scatter", "point", "map", "pen", "voronoi", "network", "route", "task", "occlusion", "airports"],
      ready: ["table", "matrix", "document", "cluster", "density", "annotation", "hierarchy", "timeline"]
    }
  };

  const examples = (window.D3_ANIMATED_SVG_EXAMPLES || []).map((example, index) => ({ ...example, index }));

  window.D3_COMPOSITION_SHEETS = sheets;
  window.D3_COMPOSITION_PATTERN_COUNT = examples.length;

  const state = {
    sheetId: resolveInitialSheetId(),
    query: ""
  };

  function resolveInitialSheetId() {
    const hash = window.location.hash.replace(/^#/, "");
    return sheets.some(sheet => sheet.id === hash) ? hash : sheets[0].id;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function normalizedText(example) {
    return `${example.id} ${example.patternId} ${example.kicker} ${example.title} ${example.copy}`.toLowerCase();
  }

  function fitForSheet(example, sheet) {
    const text = normalizedText(example);
    const rules = fitRules[sheet.id];
    if (rules.strong.some(term => text.includes(term))) return "strong";
    if (rules.ready.some(term => text.includes(term))) return "ready";
    return "support";
  }

  function macroFor(example, sheet) {
    const roles = macros[sheet.id];
    return roles[example.index % roles.length];
  }

  function patternSubject(example) {
    const text = normalizedText(example);
    if (text.includes("table") || text.includes("matrix")) return "cells and headers";
    if (text.includes("map") || text.includes("projection") || text.includes("geo")) return "projected geography";
    if (text.includes("network") || text.includes("tree") || text.includes("hierarchy")) return "node structure";
    if (text.includes("label") || text.includes("document")) return "text blocks";
    if (text.includes("flow") || text.includes("sankey") || text.includes("alluvial")) return "handoff paths";
    if (text.includes("radial") || text.includes("circle") || text.includes("polar")) return "circular marks";
    if (text.includes("scatter") || text.includes("point") || text.includes("density")) return "point field";
    return "primary marks";
  }

  function planForSheet(example, sheet) {
    const subject = patternSubject(example);
    if (sheet.id === "balance-symmetry") {
      return `Balance ${subject} around the center axes; use legends, annotations, or empty margins as counterweight.`;
    }
    if (sheet.id === "diagonal-armature") {
      return `Run ${subject} from one corner toward the opposite diagonal; place the decision or peak near a diagonal crossing.`;
    }
    if (sheet.id === "golden-root") {
      return `Reserve the long proportional field for ${subject}; use the short field for labels, legend, or comparison.`;
    }
    if (sheet.id === "thirds-fifths-grid") {
      return `Snap ${subject} to modular rows or columns; keep titles, axes, and summaries on shared third/fifth lines.`;
    }
    if (sheet.id === "radial-rosette") {
      return `Use ${subject} as a hub, ring, or spoke system; preserve equal angular spacing for peer categories.`;
    }
    if (sheet.id === "flow-spine") {
      return `Place ${subject} on a left-to-right or top-to-bottom spine with clear source, transform, and output roles.`;
    }
    return `Keep ${subject} in the active field and move labels or explanations into external lanes with audited clearance.`;
  }

  function sheetCounts(sheet) {
    const counts = { strong: 0, ready: 0, support: 0 };
    examples.forEach(example => {
      counts[fitForSheet(example, sheet)] += 1;
    });
    return counts;
  }

  function armatureSvg(sheet) {
    const line = 'stroke="#333e48" stroke-opacity=".36" stroke-width="1.6"';
    const strong = 'stroke="#9e1b32" stroke-opacity=".9" stroke-width="2.4"';
    const soft = 'stroke="#007298" stroke-opacity=".46" stroke-width="1.5"';
    const mark = 'fill="#ffffff" stroke="#9e1b32" stroke-width="2"';
    const open = `<svg viewBox="0 0 480 300" role="img" aria-label="${escapeHtml(sheet.title)} armature"><rect x="18" y="18" width="444" height="264" rx="8" fill="#ffffff" stroke="#cfcfcf"/>`;
    const close = "</svg>";
    if (sheet.id === "balance-symmetry") {
      return `${open}<line x1="240" y1="18" x2="240" y2="282" ${strong}/><line x1="18" y1="150" x2="462" y2="150" ${strong}/><line x1="18" y1="18" x2="462" y2="282" ${line}/><line x1="18" y1="282" x2="462" y2="18" ${line}/><circle cx="240" cy="150" r="34" fill="#cdf3ff" stroke="#007298" stroke-width="2"/><circle cx="136" cy="150" r="18" ${mark}/><circle cx="344" cy="150" r="18" ${mark}/>${close}`;
    }
    if (sheet.id === "diagonal-armature") {
      return `${open}<line x1="18" y1="18" x2="462" y2="282" ${strong}/><line x1="18" y1="282" x2="462" y2="18" ${soft}/><line x1="18" y1="92" x2="332" y2="282" ${line}/><line x1="148" y1="18" x2="462" y2="208" ${line}/><circle cx="142" cy="92" r="16" ${mark}/><circle cx="240" cy="150" r="20" fill="#fff4cc" stroke="#e77204" stroke-width="2"/><circle cx="338" cy="208" r="16" ${mark}/>${close}`;
    }
    if (sheet.id === "golden-root") {
      return `${open}<rect x="18" y="18" width="274" height="264" fill="#cdf3ff" fill-opacity=".52"/><rect x="292" y="18" width="170" height="264" fill="#fff4cc" fill-opacity=".7"/><line x1="292" y1="18" x2="292" y2="282" ${strong}/><line x1="18" y1="120" x2="462" y2="120" ${soft}/><line x1="148" y1="18" x2="148" y2="282" ${line}/><line x1="18" y1="196" x2="462" y2="196" ${line}/><circle cx="292" cy="120" r="18" ${mark}/>${close}`;
    }
    if (sheet.id === "thirds-fifths-grid") {
      const verticals = [106.8, 195.6, 240, 284.4, 373.2].map(x => `<line x1="${x}" y1="18" x2="${x}" y2="282" ${line}/>`).join("");
      const horizontals = [70.8, 123.6, 150, 176.4, 229.2].map(y => `<line x1="18" y1="${y}" x2="462" y2="${y}" ${line}/>`).join("");
      return `${open}${verticals}${horizontals}<rect x="106.8" y="70.8" width="177.6" height="105.6" fill="#dbffcc" fill-opacity=".65" stroke="#45842a" stroke-width="2"/><rect x="284.4" y="176.4" width="88.8" height="52.8" fill="#f9ccff" fill-opacity=".7" stroke="#652f6c" stroke-width="2"/>${close}`;
    }
    if (sheet.id === "radial-rosette") {
      const spokes = Array.from({ length: 12 }, (_, index) => {
        const angle = (-90 + index * 30) * Math.PI / 180;
        const x = 240 + Math.cos(angle) * 116;
        const y = 150 + Math.sin(angle) * 116;
        return `<line x1="240" y1="150" x2="${x.toFixed(2)}" y2="${y.toFixed(2)}" ${line}/>`;
      }).join("");
      const petals = Array.from({ length: 6 }, (_, index) => {
        const angle = (-90 + index * 60) * Math.PI / 180;
        const x = 240 + Math.cos(angle) * 82;
        const y = 150 + Math.sin(angle) * 82;
        return `<circle cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="24" fill="#cdf3ff" stroke="#007298" stroke-width="2"/>`;
      }).join("");
      return `${open}<circle cx="240" cy="150" r="116" fill="none" ${soft}/><circle cx="240" cy="150" r="64" fill="none" ${line}/>${spokes}${petals}<circle cx="240" cy="150" r="30" fill="#ffccd5" stroke="#9e1b32" stroke-width="2"/>${close}`;
    }
    if (sheet.id === "flow-spine") {
      return `${open}<path d="M58 150 C128 86 174 86 240 150 S352 214 422 150" fill="none" ${strong}/><line x1="58" y1="84" x2="58" y2="216" ${line}/><line x1="240" y1="58" x2="240" y2="242" ${soft}/><line x1="422" y1="84" x2="422" y2="216" ${line}/><circle cx="58" cy="150" r="20" fill="#cdf3ff" stroke="#007298" stroke-width="2"/><circle cx="240" cy="150" r="24" fill="#fff4cc" stroke="#e77204" stroke-width="2"/><circle cx="422" cy="150" r="20" fill="#dbffcc" stroke="#45842a" stroke-width="2"/>${close}`;
    }
    return `${open}<rect x="18" y="18" width="100" height="264" fill="#f9ccff" fill-opacity=".75"/><rect x="362" y="18" width="100" height="264" fill="#f9ccff" fill-opacity=".75"/><rect x="140" y="52" width="200" height="196" fill="#cdf3ff" fill-opacity=".42" stroke="#007298" stroke-width="2"/><line x1="140" y1="88" x2="118" y2="62" ${strong}/><line x1="340" y1="108" x2="362" y2="82" ${strong}/><line x1="140" y1="184" x2="118" y2="204" ${strong}/><line x1="340" y1="206" x2="362" y2="226" ${strong}/><circle cx="206" cy="138" r="9" ${mark}/><circle cx="268" cy="168" r="9" ${mark}/>${close}`;
  }

  function renderTabs() {
    const tabs = document.getElementById("sheet-tabs");
    tabs.innerHTML = sheets.map(sheet => `
      <button class="sheet-tab" type="button" id="tab-${sheet.id}" data-sheet-tab="${sheet.id}" role="tab" aria-selected="${sheet.id === state.sheetId ? "true" : "false"}">
        ${sheet.order} ${escapeHtml(sheet.tab)}
      </button>
    `).join("");
  }

  function renderOverview(sheet) {
    const counts = sheetCounts(sheet);
    document.getElementById("sheet-overview").innerHTML = `
      <div class="armature-panel">${armatureSvg(sheet)}</div>
      <div class="sheet-copy">
        <p class="sheet-kicker">Sheet ${sheet.order}</p>
        <h2>${escapeHtml(sheet.title)}</h2>
        <p>${escapeHtml(sheet.summary)}</p>
        <p>${escapeHtml(sheet.prompt)}</p>
        <div class="sheet-metrics">
          <span class="metric"><strong>${examples.length}</strong> patterns</span>
          <span class="metric"><strong>${counts.strong}</strong> strong fits</span>
          <span class="metric"><strong>${counts.ready}</strong> ready fits</span>
          <span class="metric"><strong>${counts.support}</strong> support fits</span>
          <span class="metric">${escapeHtml(sheet.metric)}</span>
        </div>
      </div>
    `;
  }

  function renderRows(sheet) {
    const grid = document.getElementById("sheet-grid");
    grid.innerHTML = examples.map(example => {
      const fit = fitForSheet(example, sheet);
      const macro = macroFor(example, sheet);
      const plan = planForSheet(example, sheet);
      const search = `${example.patternId} ${example.id} ${example.kicker} ${example.title} ${example.copy} ${fit} ${macro} ${plan}`.toLowerCase();
      return `
        <article class="pattern-row" id="composition-${sheet.id}-${example.id}" data-composition-id="${sheet.id}" data-example-id="${example.id}" data-pattern-id="${example.patternId}" data-fit="${fit}" data-search="${escapeHtml(search)}">
          <div class="pattern-header">
            <div>
              <p class="pattern-kicker">${escapeHtml(example.kicker)}</p>
              <h3>${escapeHtml(example.title)}</h3>
            </div>
            <span class="fit-badge" data-fit="${fit}">${fit}</span>
          </div>
          <div>
            <p class="pattern-id">${escapeHtml(example.patternId)}</p>
            <p class="pattern-copy">${escapeHtml(example.copy)}</p>
            <p class="plan-text"><strong>Composition:</strong> ${escapeHtml(plan)}</p>
            <p class="macro-text"><strong>Larger role:</strong> ${escapeHtml(macro)}</p>
          </div>
          <a class="pattern-link" href="./index.html#${encodeURIComponent(example.patternId)}">Open pattern</a>
        </article>
      `;
    }).join("");
    applyFilter();
  }

  function applyFilter() {
    const query = state.query.trim().toLowerCase();
    const rows = Array.from(document.querySelectorAll(".pattern-row"));
    let visible = 0;
    rows.forEach(row => {
      const matches = !query || row.dataset.search.includes(query);
      row.hidden = !matches;
      if (matches) visible += 1;
    });
    document.body.dataset.visiblePatternCount = String(visible);
  }

  function renderSheet() {
    const sheet = sheets.find(item => item.id === state.sheetId) || sheets[0];
    state.sheetId = sheet.id;
    document.body.dataset.activeCompositionSheet = sheet.id;
    window.location.hash = sheet.id;
    renderTabs();
    renderOverview(sheet);
    renderRows(sheet);
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
    document.body.dataset.patternCount = String(examples.length);
    document.getElementById("sheet-count").textContent = String(sheets.length);
    document.getElementById("pattern-count").textContent = String(examples.length);
    if (!examples.length) {
      renderEmptyState("Pattern metadata is unavailable.");
      return;
    }
    bindEvents();
    renderSheet();
  }

  init();
})();
