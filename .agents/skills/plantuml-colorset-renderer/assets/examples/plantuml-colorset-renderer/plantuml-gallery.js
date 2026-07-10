let examples = [];

const gallery = document.querySelector("#gallery");
const exampleCount = document.querySelector("#example-count");
const styleVersion = document.body.dataset.styleVersion || "colorset2";
const patternSuffix = styleVersion === "cs1" ? "-cs1" : "";

function patternIdFor(example) {
  return `plantuml-${example.id}${patternSuffix}`;
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
    const wideClass = example.size === "wide" ? " example-card--wide" : "";
    return `
      <article class="example-card${wideClass}" data-example-id="${patternId}" data-pattern-id="${patternId}" data-source="${escapeHtml(example.source)}" data-asset-format="${escapeHtml(example.assetFormat)}" data-replay-state="idle">
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
}

function prepareSvg(svg, example) {
  svg.removeAttribute("width");
  svg.removeAttribute("height");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-labelledby", `${example.id}-svg-title`);
  svg.setAttribute("data-pattern-id", patternIdFor(example));
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

async function loadExample(example) {
  const mount = document.querySelector(`#${CSS.escape(example.id)}-mount`);
  const card = mount.closest(".example-card");
  try {
    if (example.assetFormat === "svg") {
      const text = await fetchSvgText(`./${example.asset}`);
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
      image.src = `./${example.asset}`;
      await image.decode();
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

async function loadAllExamples() {
  let nextIndex = 0;
  const workerCount = Math.min(1, examples.length);
  const workers = Array.from({ length: workerCount }, async () => {
    while (nextIndex < examples.length) {
      const example = examples[nextIndex];
      nextIndex += 1;
      await loadExample(example);
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

async function initialize() {
  const response = await fetch("./coverage.json");
  if (!response.ok) {
    throw new Error(`coverage metadata HTTP ${response.status}`);
  }
  const metadata = await response.json();
  if (!Array.isArray(metadata.items)) {
    throw new Error("coverage metadata items must be an array");
  }
  examples = metadata.items;
  renderCards();
  bindReplayButtons();
  await loadAllExamples();
}

initialize().catch((error) => {
  document.body.dataset.loadState = "error";
  document.body.dataset.error = error.message;
});
