const examples = [
  { id: "sequence", kicker: "UML", title: "Sequence", source: "sequence.puml", copy: "Actor, participant, database, and request/response flow.", size: "wide" },
  { id: "usecase", kicker: "UML", title: "Use Case", source: "usecase.puml", copy: "Actors, system boundary, and extension relation." },
  { id: "class", kicker: "UML", title: "Class", source: "class.puml", copy: "Classes, fields, methods, and multiplicity." },
  { id: "object", kicker: "UML", title: "Object", source: "object.puml", copy: "Runtime object instances and links." },
  { id: "activity", kicker: "UML", title: "Activity", source: "activity.puml", copy: "Start, decisions, actions, and stop." },
  { id: "component", kicker: "UML", title: "Component", source: "component.puml", copy: "Services, database, queue, and dependencies.", size: "wide" },
  { id: "deployment", kicker: "UML", title: "Deployment", source: "deployment.puml", copy: "Cluster nodes, storage, and database topology.", size: "wide" },
  { id: "state", kicker: "UML", title: "State", source: "state.puml", copy: "State machine with submit, approve, and change paths." },
  { id: "timing", kicker: "UML", title: "Timing", source: "timing.puml", copy: "Robust and concise timeline states.", size: "wide" },
  { id: "json", kicker: "Data", title: "JSON", source: "json.puml", copy: "Structured object data rendering." },
  { id: "yaml", kicker: "Data", title: "YAML", source: "yaml.puml", copy: "Nested mapping and list data rendering." },
  { id: "nwdiag", kicker: "Network", title: "nwdiag", source: "nwdiag.puml", copy: "Two-network topology with shared hosts.", size: "wide" },
  { id: "salt", kicker: "Wireframe", title: "Salt", source: "salt.puml", copy: "Wireframe login form fixture." },
  { id: "archimate", kicker: "Architecture", title: "ArchiMate", source: "archimate.puml", copy: "Business, application, and technology nodes." },
  { id: "gantt", kicker: "Planning", title: "Gantt", source: "gantt.puml", copy: "Serial discovery, design, and build plan.", size: "wide" },
  { id: "mindmap", kicker: "Structure", title: "Mind Map", source: "mindmap.puml", copy: "Theme, output, and validation branches." },
  { id: "wbs", kicker: "Structure", title: "WBS", source: "wbs.puml", copy: "Work breakdown for PlantUML delivery." },
  { id: "ebnf", kicker: "Grammar", title: "EBNF", source: "ebnf.puml", copy: "Grammar production rendering.", size: "wide" },
  { id: "regex", kicker: "Grammar", title: "Regex", source: "regex.puml", copy: "Regular expression railroad rendering.", size: "wide" },
  { id: "ie", kicker: "Entity Relation", title: "IE / ER", source: "ie.puml", copy: "Information Engineering entity relation fixture." },
  { id: "chen", kicker: "Entity Relation", title: "Chen ER", source: "chen.puml", copy: "Entity and relationship notation fixture." },
];

const gallery = document.querySelector("#gallery");
const exampleCount = document.querySelector("#example-count");

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCards() {
  gallery.innerHTML = examples.map((example) => {
    const patternId = `plantuml-${example.id}`;
    const wideClass = example.size === "wide" ? " example-card--wide" : "";
    return `
      <article class="example-card${wideClass}" data-example-id="${patternId}" data-pattern-id="${patternId}" data-source="${escapeHtml(example.source)}" data-replay-state="idle">
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
          <div class="svg-mount" id="${escapeHtml(example.id)}-mount" data-load-state="loading" aria-label="${escapeHtml(example.title)} SVG preview"></div>
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
  svg.setAttribute("data-pattern-id", `plantuml-${example.id}`);
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

async function loadSvg(example) {
  const mount = document.querySelector(`#${CSS.escape(example.id)}-mount`);
  const card = mount.closest(".example-card");
  try {
    const response = await fetch(`./svg/${example.id}.svg`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const text = await response.text();
    const doc = new DOMParser().parseFromString(text, "image/svg+xml");
    const svg = doc.querySelector("svg");
    if (!svg) {
      throw new Error("missing svg element");
    }
    prepareSvg(svg, example);
    mount.replaceChildren(document.importNode(svg, true));
    mount.dataset.loadState = "loaded";
    replayCard(card);
  } catch (error) {
    mount.dataset.loadState = "error";
    mount.dataset.error = error.message;
  }
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

renderCards();
bindReplayButtons();
examples.forEach(loadSvg);
