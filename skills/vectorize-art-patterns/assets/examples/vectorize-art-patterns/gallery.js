(() => {
  "use strict";

  const body = document.body;
  const cards = [...document.querySelectorAll(".pattern-card")];
  const buttons = [...document.querySelectorAll("[data-colorset-choice]")];
  const description = document.querySelector("#palette-description");
  const status = document.querySelector("#visible-status");
  const descriptions = {
    colorset1: "Colorset 1 uses a restrained red-neutral hierarchy while retaining the same paths as colorset 2.",
    colorset2: "Colorset 2 uses expressive multi-hue roles while retaining the same paths as colorset 1.",
  };

  const setColorset = (colorset, updateUrl = true) => {
    if (!(colorset in descriptions)) return;
    body.dataset.colorset = colorset;
    cards.forEach((card) => {
      card.hidden = card.dataset.colorset !== colorset;
    });
    buttons.forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.colorsetChoice === colorset),
      );
    });
    description.textContent = descriptions[colorset];
    status.textContent = `Showing 4 ${colorset} variants`;
    if (updateUrl) {
      const url = new URL(window.location.href);
      url.searchParams.set("colorset", colorset);
      window.history.replaceState({}, "", url);
    }
  };

  const markImageState = (image, state) => {
    const card = image.closest(".pattern-card");
    card.dataset.renderState = state;
    card.querySelector(".render-state").textContent =
      state === "loaded" ? "SVG ready" : "Load error";
  };

  const hydrate = async () => {
    const response = await fetch("manifest.json");
    if (!response.ok) throw new Error(`Manifest request failed: ${response.status}`);
    const manifest = await response.json();
    const byId = new Map(manifest.patterns.map((item) => [item.id, item]));
    cards.forEach((card) => {
      const item = byId.get(card.dataset.patternId);
      if (!item) throw new Error(`Manifest is missing ${card.dataset.patternId}`);
      card.dataset.geometrySha256 = item.geometrySha256;
      card.querySelector('[data-field="pathCount"]').textContent = item.pathCount;
      card.querySelector('[data-field="contourCount"]').textContent = item.contourCount;
      const palette = card.querySelector("[data-palette]");
      item.palette.forEach((color) => {
        const swatch = document.createElement("span");
        swatch.style.backgroundColor = color;
        swatch.title = color;
        palette.appendChild(swatch);
      });
    });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      setColorset(button.dataset.colorsetChoice);
    });
  });

  cards.forEach((card) => {
    const image = card.querySelector("img");
    image.addEventListener("load", () => markImageState(image, "loaded"));
    image.addEventListener("error", () => markImageState(image, "error"));
    if (image.complete) {
      markImageState(image, image.naturalWidth > 0 ? "loaded" : "error");
    }
  });

  const hashTarget = window.location.hash
    ? document.querySelector(window.location.hash)
    : null;
  const requested = new URL(window.location.href).searchParams.get("colorset");
  setColorset(
    hashTarget?.dataset.colorset ||
      (requested in descriptions ? requested : "colorset2"),
    false,
  );

  hydrate()
    .then(() => {
      document.documentElement.dataset.ready = "true";
    })
    .catch((error) => {
      document.documentElement.dataset.ready = "error";
      status.textContent = `Gallery metadata error: ${error.message}`;
    });
})();
