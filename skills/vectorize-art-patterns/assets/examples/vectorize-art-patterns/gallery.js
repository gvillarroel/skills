(() => {
  "use strict";

  const PAGE_SIZE = 24;
  const body = document.body;
  const gallery = document.querySelector("#pattern-gallery");
  const template = document.querySelector("#pattern-card-template");
  const status = document.querySelector("#visible-status");
  const pageNumber = document.querySelector("#page-number");
  const pageTotal = document.querySelector("#page-total");
  const previousButton = document.querySelector("#previous-page");
  const nextButton = document.querySelector("#next-page");
  const modeFilter = document.querySelector("#mode-filter");
  const familyFilter = document.querySelector("#family-filter");
  const searchInput = document.querySelector("#pattern-search");
  const resetButton = document.querySelector("#reset-filters");
  const colorsetButtons = [
    ...document.querySelectorAll("[data-colorset-filter]"),
  ];
  const state = {
    manifest: null,
    colorset: "all",
    mode: "all",
    family: "all",
    query: "",
    page: 1,
  };

  const markImageState = (image, loaded) => {
    const card = image.closest(".pattern-card");
    card.dataset.renderState = loaded ? "loaded" : "error";
    card.querySelector(".render-state").textContent = loaded
      ? "SVG ready"
      : "Load error";
  };

  const setText = (card, field, value) => {
    card.querySelector(`[data-field="${field}"]`).textContent = String(value);
  };

  const createCard = (item, visibleIndex) => {
    const card = template.content.firstElementChild.cloneNode(true);
    card.id = item.id;
    card.dataset.patternId = item.id;
    card.dataset.exampleId = item.exampleId;
    card.dataset.family = item.familyId;
    card.dataset.mode = item.mode;
    card.dataset.colorset = item.colorset;
    card.dataset.geometrySha256 = item.geometrySha256;
    card.dataset.compositionSha256 = item.compositionSha256;
    card.dataset.ordinal = item.ordinal;

    const image = card.querySelector("img");
    image.src = item.svg;
    image.alt = `${item.colorsetLabel} ${item.mode} pattern: ${item.title}`;
    image.loading = visibleIndex < 4 ? "eager" : "lazy";
    image.addEventListener("load", () => markImageState(image, true));
    image.addEventListener("error", () => markImageState(image, false));

    setText(card, "mode", `${item.familyTitle} · ${item.colorsetLabel}`);
    setText(card, "title", item.title);
    setText(card, "id", item.id);
    setText(card, "description", item.description);
    setText(card, "pathCount", item.pathCount);
    setText(card, "contourCount", item.contourCount);
    setText(card, "family", item.familyTitle);

    const palette = card.querySelector("[data-palette]");
    palette.setAttribute("aria-label", `${item.colorsetLabel} output colors`);
    item.palette.forEach((color) => {
      const swatch = document.createElement("span");
      swatch.style.backgroundColor = color;
      swatch.title = color;
      palette.appendChild(swatch);
    });

    const download = card.querySelector('[data-link="download"]');
    download.href = item.svg;
    const source = card.querySelector('[data-link="source"]');
    source.href = item.sourcePage;
    const direct = card.querySelector('[data-link="direct"]');
    direct.href = `#${item.id}`;
    direct.addEventListener("click", (event) => {
      event.preventDefault();
      history.replaceState({}, "", `#${item.id}`);
      card.scrollIntoView({ block: "start", behavior: "smooth" });
    });
    return card;
  };

  const filteredPatterns = () => {
    const query = state.query.trim().toLowerCase();
    return state.manifest.patterns.filter((item) => {
      if (state.colorset !== "all" && item.colorset !== state.colorset) {
        return false;
      }
      if (state.mode !== "all" && item.mode !== state.mode) return false;
      if (state.family !== "all" && item.familyId !== state.family) return false;
      if (
        query &&
        !`${item.id} ${item.title} ${item.familyTitle} ${item.description}`
          .toLowerCase()
          .includes(query)
      ) {
        return false;
      }
      return true;
    });
  };

  const writeUrl = () => {
    const url = new URL(location.href);
    for (const [key, value, defaultValue] of [
      ["colorset", state.colorset, "all"],
      ["mode", state.mode, "all"],
      ["family", state.family, "all"],
      ["query", state.query.trim(), ""],
      ["page", String(state.page), "1"],
    ]) {
      if (value === defaultValue) url.searchParams.delete(key);
      else url.searchParams.set(key, value);
    }
    history.replaceState({}, "", url);
  };

  const render = ({ updateUrl = true, focusId = "" } = {}) => {
    const patterns = filteredPatterns();
    const pageCount = Math.max(1, Math.ceil(patterns.length / PAGE_SIZE));
    state.page = Math.max(1, Math.min(state.page, pageCount));
    const start = (state.page - 1) * PAGE_SIZE;
    const visible = patterns.slice(start, start + PAGE_SIZE);
    const fragment = document.createDocumentFragment();
    visible.forEach((item, index) => {
      fragment.appendChild(createCard(item, index));
    });
    gallery.replaceChildren(fragment);

    const first = patterns.length ? start + 1 : 0;
    const last = Math.min(start + visible.length, patterns.length);
    status.textContent = `Showing ${first}–${last} of ${patterns.length} unique patterns`;
    pageNumber.textContent = `Page ${state.page}`;
    pageTotal.textContent = ` of ${pageCount}`;
    previousButton.disabled = state.page <= 1;
    nextButton.disabled = state.page >= pageCount;
    body.dataset.colorset = state.colorset;
    colorsetButtons.forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.colorsetFilter === state.colorset),
      );
    });
    modeFilter.value = state.mode;
    familyFilter.value = state.family;
    if (searchInput.value !== state.query) searchInput.value = state.query;
    if (updateUrl) writeUrl();

    if (focusId) {
      requestAnimationFrame(() => {
        document.getElementById(focusId)?.scrollIntoView({
          block: "start",
          behavior: "auto",
        });
      });
    }
  };

  const readUrlState = () => {
    const url = new URL(location.href);
    const colorset = url.searchParams.get("colorset");
    const mode = url.searchParams.get("mode");
    const family = url.searchParams.get("family");
    state.colorset = ["all", "colorset1", "colorset2"].includes(colorset)
      ? colorset
      : "all";
    state.mode = ["all", "organic", "stain", "ink", "collage"].includes(mode)
      ? mode
      : "all";
    state.family = state.manifest.families.some((item) => item.id === family)
      ? family
      : "all";
    state.query = url.searchParams.get("query") || "";
    const page = Number.parseInt(url.searchParams.get("page") || "1", 10);
    state.page = Number.isFinite(page) && page > 0 ? page : 1;

    const hashId = decodeURIComponent(location.hash.slice(1));
    const target = state.manifest.patterns.find((item) => item.id === hashId);
    if (target) {
      state.colorset = target.colorset;
      state.mode = "all";
      state.family = target.familyId;
      state.query = "";
      const familyMatches = state.manifest.patterns.filter(
        (item) =>
          item.familyId === target.familyId && item.colorset === target.colorset,
      );
      state.page =
        Math.floor(
          familyMatches.findIndex((item) => item.id === target.id) / PAGE_SIZE,
        ) + 1;
    }
    return target?.id || "";
  };

  const populateFamilies = () => {
    state.manifest.families.forEach((family) => {
      const option = document.createElement("option");
      option.value = family.id;
      option.textContent = `${family.title} (${family.patternCount})`;
      familyFilter.appendChild(option);
    });
  };

  colorsetButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.colorset = button.dataset.colorsetFilter;
      state.page = 1;
      location.hash = "";
      render();
    });
  });
  modeFilter.addEventListener("change", () => {
    state.mode = modeFilter.value;
    state.page = 1;
    location.hash = "";
    render();
  });
  familyFilter.addEventListener("change", () => {
    state.family = familyFilter.value;
    state.page = 1;
    location.hash = "";
    render();
  });
  searchInput.addEventListener("input", () => {
    state.query = searchInput.value;
    state.page = 1;
    location.hash = "";
    render();
  });
  resetButton.addEventListener("click", () => {
    Object.assign(state, {
      colorset: "all",
      mode: "all",
      family: "all",
      query: "",
      page: 1,
    });
    location.hash = "";
    render();
  });
  previousButton.addEventListener("click", () => {
    state.page -= 1;
    render();
    document.querySelector(".gallery-heading").scrollIntoView();
  });
  nextButton.addEventListener("click", () => {
    state.page += 1;
    render();
    document.querySelector(".gallery-heading").scrollIntoView();
  });

  const hydrate = async () => {
    const response = await fetch("manifest.json");
    if (!response.ok) {
      throw new Error(`Manifest request failed: ${response.status}`);
    }
    const manifest = await response.json();
    if (
      manifest.patternCount !== 300 ||
      manifest.uniqueGeometryCount !== 300 ||
      manifest.uniquenessContract.pathDataReuseAllowed !== false
    ) {
      throw new Error("Manifest uniqueness contract is incomplete");
    }
    state.manifest = manifest;
    document.querySelector('[data-stat="patterns"]').textContent =
      manifest.patternCount;
    document.querySelector('[data-stat="families"]').textContent =
      manifest.familyCount;
    document.querySelector('[data-stat="reused-paths"]').textContent = "0";
    document.querySelector("[data-collection-summary]").textContent =
      `${manifest.uniqueGeometryCount.toLocaleString()} geometries · ` +
      `${manifest.uniquePathCount.toLocaleString()} non-repeated path signatures · ` +
      `${Object.keys(manifest.sourceCounts).length} verified open sources`;
    populateFamilies();
    const focusId = readUrlState();
    render({ updateUrl: false, focusId });
    document.documentElement.dataset.ready = "true";
  };

  hydrate().catch((error) => {
    document.documentElement.dataset.ready = "error";
    status.textContent = `Gallery metadata error: ${error.message}`;
  });
})();
