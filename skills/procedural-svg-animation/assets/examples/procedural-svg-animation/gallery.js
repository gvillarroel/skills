(() => {
  "use strict";

  const cards = Array.from(document.querySelectorAll(".pattern-card"));
  const searchInput = document.querySelector("#pattern-search");
  const familySelect = document.querySelector("#family-filter");
  const driverSelect = document.querySelector("#driver-filter");
  const visibleCount = document.querySelector("#visible-count");
  const emptyState = document.querySelector("#empty-state");
  const filterStatus = document.querySelector("#filter-status");
  const familyButtons = Array.from(document.querySelectorAll("[data-family-filter]"));
  const reduceQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const pauseAllButton = document.querySelector("#pause-all");
  let replaySerial = 0;
  let globalPauseActive = false;

  function decodedHashId() {
    try { return decodeURIComponent(location.hash.slice(1)); }
    catch (_error) { return ""; }
  }

  const initialHashTarget = document.getElementById(decodedHashId());
  let deferHashNeighborLoading = Boolean(initialHashTarget?.classList.contains("pattern-card"));

  const normalize = value => String(value || "").trim().toLocaleLowerCase();

  function previewFor(card) {
    return card.querySelector("[data-pattern-preview]");
  }

  function loadPreview(card) {
    const preview = previewFor(card);
    if (!preview || preview.dataset.loaded === "true") return;
    preview.dataset.loaded = "true";
    setCardState(card, "Loading", "loading");
    preview.data = preview.dataset.source;
  }

  function setCardState(card, label, state) {
    card.dataset.playbackState = state;
    const output = card.querySelector("[data-preview-state]");
    if (output) output.textContent = label;
  }

  function animationsFor(preview) {
    try {
      return preview.contentDocument?.getAnimations?.() || [];
    } catch (_error) {
      return [];
    }
  }

  function svgRootFor(preview) {
    try {
      const root = preview.contentDocument?.documentElement || null;
      return root?.localName === "svg" && root.hasAttribute("data-pattern-id") ? root : null;
    } catch (_error) {
      return null;
    }
  }

  function installPauseStyle(preview) {
    try {
      const doc = preview.contentDocument;
      if (!doc || doc.getElementById("procedural-gallery-pause-style")) return;
      const style = doc.createElementNS("http://www.w3.org/2000/svg", "style");
      style.id = "procedural-gallery-pause-style";
      style.textContent = "[data-gallery-paused='true'] * { animation-play-state: paused !important; }";
      doc.documentElement.appendChild(style);
    } catch (_error) {
      // An SVG opened cross-origin remains usable through reload controls.
    }
  }

  function pauseCard(card, label = "Paused") {
    const preview = previewFor(card);
    const root = svgRootFor(preview);
    if (!root) {
      if (preview?.dataset.loaded === "true") setCardState(card, "Loading", "loading");
      return;
    }
    installPauseStyle(preview);
    try { root?.pauseAnimations?.(); } catch (_error) {}
    root?.setAttribute?.("data-gallery-paused", "true");
    animationsFor(preview).forEach(animation => animation.pause());
    setCardState(card, label, "paused");
  }

  function playCard(card) {
    const preview = previewFor(card);
    const root = svgRootFor(preview);
    if (!root) {
      loadPreview(card);
      return;
    }
    root?.removeAttribute?.("data-gallery-paused");
    try { root?.unpauseAnimations?.(); } catch (_error) {}
    animationsFor(preview).forEach(animation => animation.play());
    setCardState(card, "Playing", "playing");
  }

  function replayCard(card) {
    const preview = previewFor(card);
    const root = svgRootFor(preview);
    if (!root && preview?.dataset.loaded !== "true") {
      loadPreview(card);
      return;
    }
    let reset = false;
    try {
      if (root?.setCurrentTime) {
        root.setCurrentTime(0);
        root.unpauseAnimations?.();
        reset = true;
      }
      const animations = animationsFor(preview);
      animations.forEach(animation => {
        animation.currentTime = 0;
        animation.play();
      });
      reset ||= animations.length > 0;
    } catch (_error) {
      reset = false;
    }
    if (!reset) {
      replaySerial += 1;
      const source = preview.dataset.source;
      preview.data = `${source}?replay=${replaySerial}`;
      setCardState(card, "Reloading", "loading");
    } else {
      root?.removeAttribute?.("data-gallery-paused");
      setCardState(card, "Playing", "playing");
    }
  }

  function updateReducedMotion() {
    document.body.dataset.reducedMotion = String(reduceQuery.matches);
    if (reduceQuery.matches) {
      cards.filter(card => previewFor(card)?.dataset.loaded === "true").forEach(card => {
        if (card.dataset.playbackState === "manual-playing" || card.dataset.playbackState === "paused") return;
        card.dataset.reducedMotionPaused = "true";
        pauseCard(card, "Reduced motion");
      });
    } else {
      cards.filter(card => card.dataset.reducedMotionPaused === "true").forEach(card => {
        delete card.dataset.reducedMotionPaused;
        playCard(card);
      });
    }
  }

  function applyFilters({ announce = true } = {}) {
    const query = normalize(searchInput.value);
    const family = familySelect.value;
    const driver = driverSelect.value;
    let count = 0;
    cards.forEach(card => {
      const matchesSearch = !query || card.dataset.search.includes(query);
      const matchesFamily = !family || card.dataset.familyId === family;
      const matchesDriver = !driver || card.dataset.driver === driver;
      const visible = matchesSearch && matchesFamily && matchesDriver;
      card.hidden = !visible;
      if (visible) count += 1;
    });
    visibleCount.textContent = String(count);
    emptyState.dataset.visible = String(count === 0);
    familyButtons.forEach(button => {
      button.setAttribute("aria-pressed", String(button.dataset.familyFilter === family));
    });
    if (announce) filterStatus.textContent = `${count} patterns visible.`;
  }

  function resetFilters() {
    searchInput.value = "";
    familySelect.value = "";
    driverSelect.value = "";
    applyFilters();
    searchInput.focus();
  }

  function revealHashTarget() {
    const id = decodedHashId();
    if (!id) return;
    const target = document.getElementById(id);
    if (!target?.classList.contains("pattern-card")) return;
    if (target.hidden) {
      searchInput.value = "";
      familySelect.value = "";
      driverSelect.value = "";
      applyFilters({ announce: false });
    }
    loadPreview(target);
    requestAnimationFrame(() => {
      const root = document.documentElement;
      const previousBehavior = root.style.scrollBehavior;
      root.style.scrollBehavior = "auto";
      target.scrollIntoView({ block: "start", behavior: "instant" });
      requestAnimationFrame(() => {
        root.style.scrollBehavior = previousBehavior;
        if (deferHashNeighborLoading) {
          requestAnimationFrame(() => {
            window.addEventListener("scroll", releaseDeferredPreviewLoading, { once: true, passive: true });
          });
        }
      });
    });
  }

  let previewObserver = "IntersectionObserver" in window
    ? new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting || entry.target.hidden) return;
          if (deferHashNeighborLoading && entry.target !== initialHashTarget) return;
          loadPreview(entry.target);
          previewObserver.unobserve(entry.target);
        });
      }, { rootMargin: "180px 0px" })
    : null;

  function releaseDeferredPreviewLoading() {
    if (!deferHashNeighborLoading) return;
    deferHashNeighborLoading = false;
    if (!previewObserver) return;
    cards.forEach(card => {
      if (previewFor(card)?.dataset.loaded === "true") return;
      previewObserver.unobserve(card);
      previewObserver.observe(card);
    });
  }

  for (const eventName of ["wheel", "touchstart", "pointerdown", "keydown"]) {
    window.addEventListener(eventName, releaseDeferredPreviewLoading, { once: true, passive: true });
  }

  cards.forEach((card, index) => {
    const preview = previewFor(card);
    preview.addEventListener("load", () => {
      if (preview.dataset.loaded !== "true") return;
      if (!svgRootFor(preview)) {
        setCardState(card, "Load failed", "error");
        return;
      }
      installPauseStyle(preview);
      if (globalPauseActive) {
        pauseCard(card, "Paused globally");
      } else if (reduceQuery.matches) {
        card.dataset.reducedMotionPaused = "true";
        pauseCard(card, "Reduced motion");
      }
      else setCardState(card, "Playing", "playing");
    });
    card.querySelector("[data-action='pause']").addEventListener("click", () => {
      delete card.dataset.reducedMotionPaused;
      pauseCard(card);
    });
    card.querySelector("[data-action='play']").addEventListener("click", () => {
      delete card.dataset.reducedMotionPaused;
      card.dataset.playbackState = "manual-playing";
      playCard(card);
      card.dataset.playbackState = "manual-playing";
    });
    card.querySelector("[data-action='replay']").addEventListener("click", () => {
      delete card.dataset.reducedMotionPaused;
      replayCard(card);
    });
    if (previewObserver) previewObserver.observe(card);
    if (!previewObserver || index < 6) loadPreview(card);
  });

  searchInput.addEventListener("input", () => applyFilters());
  familySelect.addEventListener("change", () => applyFilters());
  driverSelect.addEventListener("change", () => applyFilters());
  document.querySelector("#reset-filters").addEventListener("click", resetFilters);
  const loadedCards = () => cards.filter(card => previewFor(card)?.dataset.loaded === "true");
  pauseAllButton.addEventListener("click", () => {
    globalPauseActive = true;
    pauseAllButton.setAttribute("aria-pressed", "true");
    loadedCards().forEach(card => {
      delete card.dataset.reducedMotionPaused;
      pauseCard(card, "Paused globally");
    });
    filterStatus.textContent = "All previews are paused, including previews loaded later.";
  });
  document.querySelector("#play-all").addEventListener("click", () => {
    globalPauseActive = false;
    pauseAllButton.setAttribute("aria-pressed", "false");
    loadedCards().forEach(card => {
      delete card.dataset.reducedMotionPaused;
      playCard(card);
    });
    filterStatus.textContent = "All loaded previews are playing.";
  });
  document.querySelector("#replay-all").addEventListener("click", () => {
    globalPauseActive = false;
    pauseAllButton.setAttribute("aria-pressed", "false");
    loadedCards().forEach(card => {
      delete card.dataset.reducedMotionPaused;
      replayCard(card);
    });
    filterStatus.textContent = "All loaded previews replayed.";
  });
  familyButtons.forEach(button => button.addEventListener("click", () => {
    familySelect.value = familySelect.value === button.dataset.familyFilter ? "" : button.dataset.familyFilter;
    applyFilters();
    document.querySelector("#catalog-heading").scrollIntoView({ block: "start" });
  }));

  if (typeof reduceQuery.addEventListener === "function") reduceQuery.addEventListener("change", updateReducedMotion);
  else reduceQuery.addListener(updateReducedMotion);
  window.addEventListener("hashchange", revealHashTarget);

  applyFilters({ announce: false });
  updateReducedMotion();
  revealHashTarget();
})();
