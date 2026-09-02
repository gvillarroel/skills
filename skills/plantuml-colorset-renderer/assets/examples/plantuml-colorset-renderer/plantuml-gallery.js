let examples = [];
let activeThemeId = "colorset2";
let activeCapabilityId = "all";
let themeLoadVersion = 0;

const gallery = document.querySelector("#gallery");
const exampleCount = document.querySelector("#example-count");
const visibleCount = document.querySelector("#visible-count");
const activeThemeLabel = document.querySelector("#active-theme");
const activeRenderReport = document.querySelector("#active-render-report");
const themeButtons = [...document.querySelectorAll("[data-theme]")];
const capabilityButtons = [...document.querySelectorAll("[data-capability-filter]")];
const themeSources = {
  colorset2: {
    baseUrl: ".",
    styleVersion: "colorset2",
    colorSet: "colorset2",
    paletteName: "cs2",
    label: "Colorset 2",
    reportUrl: "./render-report.json"
  },
  colorset1: {
    baseUrl: "../plantuml-colorset-renderer-cs1",
    styleVersion: "cs1",
    colorSet: "colorset1",
    paletteName: "basic-red-neutral-style",
    label: "Colorset 1",
    reportUrl: "../plantuml-colorset-renderer-cs1/render-report.json"
  }
};
let styleVersion = themeSources[activeThemeId].styleVersion;
let patternSuffix = styleVersion === "cs1" ? "-cs1" : "-cs2";
const patternSlugs = new Map([
  ["usecase", "use-case"],
  ["math", "asciimath"],
  ["latex", "jlatexmath"],
  ["ie", "ie-er"],
  ["chen", "chen-er"],
  ["files", "file-tree"],
  ["packetdiag", "packet"]
]);
const capabilityByKicker = new Map([
  ["UML", "uml-behavior"],
  ["Workflow", "uml-behavior"],
  ["Architecture", "architecture-network"],
  ["Network", "architecture-network"],
  ["Data", "data-notation"],
  ["Grammar", "data-notation"],
  ["Entity Relation", "data-notation"],
  ["Planning", "planning-structure"],
  ["Structure", "planning-structure"],
  ["Wireframe", "visual-specialist"],
  ["ASCII Art", "visual-specialist"],
  ["Mathematics", "visual-specialist"],
  ["Chart", "visual-specialist"]
]);

function patternIdFor(example) {
  return `plantuml-${patternSlugs.get(example.id) || example.id}${patternSuffix}`;
}

function legacyPatternIdFor(example) {
  const legacyPatternId = `plantuml-${example.id}${styleVersion === "cs1" ? "-cs1" : ""}`;
  return legacyPatternId === patternIdFor(example) ? "" : legacyPatternId;
}

function capabilityIdFor(example) {
  return capabilityByKicker.get(example.kicker) || "visual-specialist";
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCards() {
  gallery.innerHTML = examples.map((example) => {
    const patternId = patternIdFor(example);
    const legacyPatternId = legacyPatternIdFor(example);
    const legacyPatternAttribute = legacyPatternId ? ` data-legacy-pattern-id="${legacyPatternId}"` : "";
    const capabilityId = capabilityIdFor(example);
    const wideClass = example.size === "wide" ? " example-card--wide" : "";
    return `
      <article class="example-card${wideClass}" id="${patternId}" data-example-id="${example.id}" data-pattern-id="${patternId}"${legacyPatternAttribute} data-capability="${capabilityId}" data-source="${escapeHtml(example.source)}" data-asset-format="${escapeHtml(example.assetFormat)}" data-replay-state="idle">
        <div class="example-header">
          <div class="example-header-top">
            <p class="example-kicker">${escapeHtml(example.kicker)}</p>
            <button class="card-replay-button" type="button" data-replay="${escapeHtml(example.id)}" aria-label="Replay ${escapeHtml(example.title)} animation"><span class="material-symbols-rounded" aria-hidden="true">replay</span><span>Replay</span></button>
          </div>
          <h2>${escapeHtml(example.title)}</h2>
          <p class="example-pattern-id">${patternId}</p>
          <p class="example-copy">${escapeHtml(example.copy)}</p>
        </div>
        <div class="viz-frame">
          <div class="svg-mount" id="${escapeHtml(example.id)}-mount" data-load-state="loading" aria-label="${escapeHtml(example.title)} ${escapeHtml(example.assetFormat.toUpperCase())} preview"></div>
        </div>
      </article>`;
  }).join("");
  exampleCount.textContent = String(examples.length);
  applyCapabilityFilter();
}

function applyCapabilityFilter() {
  let shown = 0;
  document.querySelectorAll(".example-card").forEach((card) => {
    const visible = activeCapabilityId === "all" || card.dataset.capability === activeCapabilityId;
    card.hidden = !visible;
    if (visible) shown += 1;
  });
  capabilityButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.capabilityFilter === activeCapabilityId));
  });
  visibleCount.textContent = String(shown);
}

function prepareSvg(svg, example) {
  svg.removeAttribute("width");
  svg.removeAttribute("height");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-labelledby", `${example.id}-svg-title`);
  svg.setAttribute("data-pattern-id", patternIdFor(example));
  const legacyPatternId = legacyPatternIdFor(example);
  if (legacyPatternId) {
    svg.setAttribute("data-legacy-pattern-id", legacyPatternId);
  } else {
    svg.removeAttribute("data-legacy-pattern-id");
  }
  svg.setAttribute("data-source", example.source);

  const existingTitle = svg.querySelector("title");
  if (existingTitle) {
    existingTitle.id = `${example.id}-svg-title`;
  } else {
    const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
    title.id = `${example.id}-svg-title`;
    title.textContent = `${example.title} PlantUML diagram`;
    svg.prepend(title);
  }

  const parts = svg.querySelectorAll("path,line,polyline,polygon,rect,ellipse,circle,text");
  parts.forEach((part, index) => {
    part.classList.add("plantuml-part");
    part.style.setProperty("--part-index", String(Math.min(index, 90)));
    if (typeof part.getTotalLength === "function") {
      try {
        const length = Math.max(1, Math.ceil(part.getTotalLength()));
        part.classList.add("plantuml-geometry");
        part.style.setProperty("--path-length", String(length));
      } catch {
        part.classList.remove("plantuml-geometry");
      }
    }
  });
}

function replayCard(card) {
  card.dataset.replayState = "idle";
  card.offsetWidth;
  card.dataset.replayState = "running";
  window.setTimeout(() => {
    card.dataset.replayState = "idle";
  }, 2300);
}

function wait(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

async function fetchSvgText(url) {
  let lastError = null;
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.text();
    } catch (error) {
      lastError = error;
      await wait(180 * (attempt + 1));
    }
  }
  throw lastError;
}

async function loadExample(example, loadVersion) {
  const mount = document.querySelector(`#${CSS.escape(example.id)}-mount`);
  const card = mount.closest(".example-card");
  const assetUrl = `${themeSources[activeThemeId].baseUrl}/${example.asset}`;
  try {
    if (example.assetFormat === "svg") {
      const text = await fetchSvgText(assetUrl);
      if (loadVersion !== themeLoadVersion) return;
      const doc = new DOMParser().parseFromString(text, "image/svg+xml");
      const svg = doc.querySelector("svg");
      if (!svg) {
        throw new Error("missing svg element");
      }
      prepareSvg(svg, example);
      mount.replaceChildren(document.importNode(svg, true));
    } else if (example.assetFormat === "png") {
      const image = new Image();
      image.className = "plantuml-raster";
      image.alt = `${example.title} PlantUML diagram`;
      image.src = assetUrl;
      await image.decode();
      if (loadVersion !== themeLoadVersion) return;
      mount.replaceChildren(image);
    } else {
      throw new Error(`unsupported asset format: ${example.assetFormat}`);
    }
    mount.dataset.loadState = "loaded";
    replayCard(card);
  } catch (error) {
    mount.dataset.loadState = "error";
    mount.dataset.error = error.message;
  }
}

async function loadAllExamples(loadVersion) {
  let nextIndex = 0;
  const workerCount = Math.min(1, examples.length);
  const workers = Array.from({ length: workerCount }, async () => {
    while (nextIndex < examples.length) {
      const example = examples[nextIndex];
      nextIndex += 1;
      await loadExample(example, loadVersion);
    }
  });
  await Promise.all(workers);
}

function bindReplayButtons() {
  gallery.addEventListener("click", (event) => {
    const button = event.target.closest("[data-replay]");
    if (!button) {
      return;
    }
    const card = button.closest(".example-card");
    replayCard(card);
  });
}

function themeIdFromHash() {
  const hash = decodeURIComponent(window.location.hash.slice(1));
  if (hash.endsWith("-cs1")) return "colorset1";
  if (hash.endsWith("-cs2")) return "colorset2";
  return "";
}

function initialThemeId() {
  const requested = new URL(window.location.href).searchParams.get("theme");
  if (requested && themeSources[requested]) return requested;
  return themeIdFromHash() || "colorset2";
}

function exampleIdFromCurrentHash() {
  const hash = decodeURIComponent(window.location.hash.slice(1));
  if (!hash) return "";
  const card = [...document.querySelectorAll(".example-card")].find(
    (item) => item.id === hash || item.dataset.legacyPatternId === hash
  );
  return card?.dataset.exampleId || "";
}

function updateThemeUi(themeId) {
  const theme = themeSources[themeId];
  document.body.dataset.styleVersion = theme.styleVersion;
  document.body.dataset.colorSet = theme.colorSet;
  document.body.dataset.paletteName = theme.paletteName;
  document.body.dataset.activeTheme = themeId;
  activeThemeLabel.textContent = theme.label;
  activeRenderReport.setAttribute("href", theme.reportUrl);
  themeButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.theme === themeId));
  });
  document.title = `PlantUML Skill Gallery · ${theme.label}`;
}

function updateThemeLocation(linkedExampleId = "") {
  const url = new URL(window.location.href);
  if (activeThemeId === "colorset1") {
    url.searchParams.set("theme", activeThemeId);
  } else {
    url.searchParams.delete("theme");
  }
  if (linkedExampleId) {
    const linkedExample = examples.find((example) => example.id === linkedExampleId);
    if (linkedExample) url.hash = patternIdFor(linkedExample);
  }
  history.replaceState(null, "", url.pathname + url.search + url.hash);
}

async function setTheme(themeId, { syncLocation = true } = {}) {
  const theme = themeSources[themeId];
  if (!theme) throw new Error(`unsupported theme: ${themeId}`);

  const linkedExampleId = exampleIdFromCurrentHash();
  const loadVersion = ++themeLoadVersion;
  activeThemeId = themeId;
  styleVersion = theme.styleVersion;
  patternSuffix = styleVersion === "cs1" ? "-cs1" : "-cs2";
  updateThemeUi(themeId);
  gallery.setAttribute("aria-busy", "true");

  const response = await fetch(`${theme.baseUrl}/coverage.json`);
  if (!response.ok) {
    throw new Error(`coverage metadata HTTP ${response.status}`);
  }
  const metadata = await response.json();
  if (!Array.isArray(metadata.items)) {
    throw new Error("coverage metadata items must be an array");
  }
  if (metadata.colorset !== theme.colorSet) {
    throw new Error(`coverage metadata expected ${theme.colorSet}, found ${metadata.colorset}`);
  }
  if (loadVersion !== themeLoadVersion) return;

  examples = metadata.items;
  renderCards();
  if (syncLocation) updateThemeLocation(linkedExampleId);
  redirectLegacyPatternHash();
  await loadAllExamples(loadVersion);
  if (loadVersion !== themeLoadVersion) return;
  gallery.setAttribute("aria-busy", "false");
  document.body.dataset.loadState = "loaded";
  delete document.body.dataset.error;
}

function bindThemeButtons() {
  themeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.theme === activeThemeId) return;
      setTheme(button.dataset.theme).catch(reportLoadError);
    });
  });
}

function bindCapabilityButtons() {
  capabilityButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeCapabilityId = button.dataset.capabilityFilter;
      applyCapabilityFilter();
    });
  });
}

function reportLoadError(error) {
  gallery.setAttribute("aria-busy", "false");
  document.body.dataset.loadState = "error";
  document.body.dataset.error = error.message;
}

async function initialize() {
  bindReplayButtons();
  bindThemeButtons();
  bindCapabilityButtons();
  window.addEventListener("hashchange", () => {
    const requestedTheme = themeIdFromHash();
    if (requestedTheme && requestedTheme !== activeThemeId) {
      setTheme(requestedTheme, { syncLocation: false }).catch(reportLoadError);
      return;
    }
    redirectLegacyPatternHash();
  });
  await setTheme(initialThemeId(), { syncLocation: false });
}

function redirectLegacyPatternHash() {
  const hash = decodeURIComponent(window.location.hash.slice(1));
  if (!hash) return;
  const card = [...document.querySelectorAll(".example-card")].find((item) => item.dataset.legacyPatternId === hash);
  if (!card) return;
  history.replaceState(null, "", location.pathname + location.search + "#" + card.dataset.patternId);
  card.scrollIntoView({ block: "start" });
}

initialize().catch((error) => {
  reportLoadError(error);
});
