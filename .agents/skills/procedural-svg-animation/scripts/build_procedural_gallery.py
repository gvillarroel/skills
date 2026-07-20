#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Build the deterministic procedural SVG acceptance gallery.

The gallery is intentionally dependency-free at runtime. The builder delegates
each SVG to ``build_procedural_svg.py``, audits the result, then emits a static
HTML catalog, local CSS and JavaScript, and a machine-readable manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = SKILL_ROOT / "assets" / "pattern-specs.json"
GENERATOR_PATH = SKILL_ROOT / "scripts" / "build_procedural_svg.py"
DEFAULT_OUTPUT_DIR = (
    SKILL_ROOT / "assets" / "examples" / "procedural-svg-animation"
)
PAGE_ID = "procedural-svg-animation"
EXPECTED_PATTERN_COUNT = 60
EXPECTED_FAMILY_COUNT = 10
MANAGED_PAGE_FILES = ("index.html", "gallery.css", "gallery.js", "manifest.json")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REMOTE_REFERENCE_RE = re.compile(
    r"(?:href|src)\s*=\s*['\"]\s*(?:https?:)?//", re.IGNORECASE
)


GALLERY_CSS = r""":root {
  color-scheme: dark;
  --ink: #f7f8fc;
  --ink-muted: #aeb8c8;
  --paper: #f6f2e9;
  --paper-ink: #18202a;
  --paper-muted: #596473;
  --night: #08101a;
  --night-soft: #111c29;
  --night-line: rgba(255, 255, 255, 0.12);
  --accent: #7ee7dc;
  --accent-warm: #ffbf69;
  --focus: #fff27a;
  --radius-xl: 28px;
  --radius-lg: 20px;
  --shadow: 0 24px 70px rgba(0, 0, 0, 0.28);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-synthesis: none;
}

* { box-sizing: border-box; }

html {
  background: var(--night);
  scroll-behavior: smooth;
}

body {
  min-width: 320px;
  margin: 0;
  color: var(--ink);
  background:
    radial-gradient(circle at 12% -5%, rgba(126, 231, 220, 0.19), transparent 31rem),
    radial-gradient(circle at 92% 8%, rgba(255, 191, 105, 0.16), transparent 27rem),
    var(--night);
}

button, input, select { font: inherit; }

a { color: inherit; }

.skip-link {
  position: fixed;
  z-index: 100;
  top: 0.75rem;
  left: 0.75rem;
  padding: 0.7rem 1rem;
  color: #071019;
  background: var(--focus);
  border-radius: 999px;
  transform: translateY(-180%);
}

.skip-link:focus { transform: translateY(0); }

.page-shell {
  width: min(1540px, calc(100% - 2rem));
  margin: 0 auto;
  padding: 1rem 0 5rem;
}

.hero {
  position: relative;
  overflow: hidden;
  min-height: 420px;
  padding: clamp(2rem, 6vw, 5.5rem);
  border: 1px solid var(--night-line);
  border-radius: var(--radius-xl);
  background:
    linear-gradient(125deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.01)),
    var(--night-soft);
  box-shadow: var(--shadow);
}

.hero::after {
  content: "";
  position: absolute;
  right: -9rem;
  bottom: -15rem;
  width: 38rem;
  height: 38rem;
  border: 1px solid rgba(126, 231, 220, 0.23);
  border-radius: 50%;
  box-shadow:
    0 0 0 3rem rgba(126, 231, 220, 0.035),
    0 0 0 7rem rgba(255, 191, 105, 0.025);
  pointer-events: none;
}

.eyebrow {
  margin: 0 0 1rem;
  color: var(--accent);
  font-size: 0.77rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.hero h1 {
  max-width: 920px;
  margin: 0;
  font-size: clamp(2.8rem, 8vw, 7.4rem);
  font-weight: 770;
  letter-spacing: -0.065em;
  line-height: 0.9;
}

.hero-copy {
  max-width: 820px;
  margin: 1.7rem 0 0;
  color: var(--ink-muted);
  font-size: clamp(1.02rem, 2vw, 1.35rem);
  line-height: 1.65;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 2rem;
}

.hero-meta span, .manifest-link {
  display: inline-flex;
  align-items: center;
  min-height: 2.35rem;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--night-line);
  border-radius: 999px;
  color: var(--ink-muted);
  background: rgba(255, 255, 255, 0.035);
  font-size: 0.84rem;
  font-weight: 700;
  text-decoration: none;
}

.manifest-link:hover { color: var(--ink); border-color: var(--accent); }

.section-heading {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 560px);
  gap: 2rem;
  align-items: end;
  margin: clamp(4rem, 8vw, 7rem) 0 1.6rem;
}

.section-heading h2 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 4rem);
  letter-spacing: -0.04em;
  line-height: 1;
}

.section-heading p {
  margin: 0;
  color: var(--ink-muted);
  line-height: 1.65;
}

.family-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0.8rem;
}

.family-tile {
  position: relative;
  min-height: 210px;
  padding: 1.25rem;
  color: var(--ink);
  text-align: left;
  border: 1px solid var(--night-line);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.035);
  cursor: pointer;
}

.family-tile:hover, .family-tile[aria-pressed="true"] {
  border-color: var(--family-accent, var(--accent));
  background: color-mix(in srgb, var(--family-accent, var(--accent)) 13%, var(--night-soft));
  transform: translateY(-2px);
}

.family-count {
  display: inline-grid;
  width: 2.2rem;
  height: 2.2rem;
  place-items: center;
  margin-bottom: 1.25rem;
  color: #071019;
  background: var(--family-accent, var(--accent));
  border-radius: 50%;
  font-size: 0.78rem;
  font-weight: 900;
}

.family-tile strong { display: block; font-size: 1rem; line-height: 1.25; }
.family-tile small { display: block; margin-top: 0.6rem; color: var(--ink-muted); line-height: 1.45; }

.catalog-toolbar {
  position: sticky;
  z-index: 20;
  top: 0.7rem;
  display: grid;
  grid-template-columns: minmax(240px, 1.4fr) repeat(2, minmax(170px, 0.65fr)) auto;
  gap: 0.7rem;
  align-items: end;
  margin: 1.4rem 0;
  padding: 0.85rem;
  border: 1px solid var(--night-line);
  border-radius: 22px;
  background: rgba(8, 16, 26, 0.9);
  box-shadow: 0 16px 45px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(18px);
}

.control-field { display: grid; gap: 0.4rem; }
.control-field span { color: var(--ink-muted); font-size: 0.7rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }

.control-field input, .control-field select {
  width: 100%;
  min-height: 2.8rem;
  padding: 0.62rem 0.8rem;
  color: var(--ink);
  border: 1px solid var(--night-line);
  border-radius: 12px;
  background: #101b28;
  outline: none;
}

.control-field input:focus, .control-field select:focus,
.button:focus-visible, .family-tile:focus-visible, a:focus-visible {
  outline: 3px solid var(--focus);
  outline-offset: 3px;
}

.toolbar-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 0.5rem; }

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.7rem;
  padding: 0.62rem 0.86rem;
  border: 1px solid var(--night-line);
  border-radius: 12px;
  color: var(--ink);
  background: rgba(255, 255, 255, 0.045);
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
}

.button:hover { border-color: var(--accent); background: rgba(126, 231, 220, 0.1); }
.button.primary { color: #071019; border-color: var(--accent); background: var(--accent); }
.button.primary:hover { background: #a8fff5; }

.results-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.8rem;
  align-items: center;
  margin: 1rem 0 1.2rem;
  color: var(--ink-muted);
  font-size: 0.88rem;
}

.results-bar strong { color: var(--ink); }
.motion-note { display: none; color: var(--accent-warm); font-weight: 750; }
body[data-reduced-motion="true"] .motion-note { display: inline; }

.visually-hidden {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

.gallery {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.pattern-card {
  --family-accent: var(--accent);
  position: relative;
  overflow: clip;
  scroll-margin-top: 11rem;
  min-width: 0;
  border-radius: var(--radius-lg);
  color: var(--paper-ink);
  background: var(--paper);
  box-shadow: 0 16px 45px rgba(0, 0, 0, 0.2);
}

.pattern-card[hidden] { display: none; }

.pattern-card:target {
  outline: 4px solid var(--focus);
  outline-offset: 5px;
}

.preview-shell {
  position: relative;
  display: grid;
  aspect-ratio: 16 / 10;
  overflow: hidden;
  place-items: stretch;
  background:
    linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
    #0b1521;
  background-size: 24px 24px;
  border-bottom: 4px solid var(--family-accent);
}

.pattern-preview { width: 100%; height: 100%; border: 0; background: transparent; }

.preview-state {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  min-height: 1.8rem;
  padding: 0.35rem 0.58rem;
  color: #e8f2ff;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 999px;
  background: rgba(4, 10, 17, 0.72);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  backdrop-filter: blur(8px);
}

.card-body { padding: 1.15rem; }

.card-kicker {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
  color: var(--paper-muted);
  font-size: 0.7rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.family-label { color: color-mix(in srgb, var(--family-accent) 70%, #14202d); }

.pattern-card h3 {
  margin: 0.65rem 0 0;
  font-size: clamp(1.25rem, 2vw, 1.65rem);
  letter-spacing: -0.03em;
  line-height: 1.1;
}

.canonical-link {
  display: block;
  width: fit-content;
  max-width: 100%;
  margin-top: 0.45rem;
  color: #31586c;
  font-size: 0.72rem;
  font-weight: 760;
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
  overflow-wrap: anywhere;
}

.card-description { min-height: 4.6em; margin: 0.9rem 0 0; color: var(--paper-muted); font-size: 0.88rem; line-height: 1.55; }

.signature {
  margin: 0.85rem 0 0;
  padding: 0.75rem;
  overflow-x: auto;
  color: #283845;
  border: 1px solid rgba(24, 32, 42, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.55);
  font: 650 0.73rem/1.45 ui-monospace, SFMono-Regular, Consolas, monospace;
}

.metadata-list { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.85rem 0 0; padding: 0; list-style: none; }
.metadata-list li { padding: 0.35rem 0.52rem; color: #475362; border: 1px solid rgba(24,32,42,0.1); border-radius: 999px; background: rgba(255,255,255,0.47); font-size: 0.68rem; font-weight: 760; }

.card-controls {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.45rem;
  margin-top: 1rem;
}

.card-controls .button { min-height: 2.45rem; padding: 0.5rem; color: var(--paper-ink); border-color: rgba(24,32,42,0.15); background: rgba(255,255,255,0.58); }
.card-controls .button:hover { border-color: #31586c; background: #fff; }

.open-svg {
  display: inline-flex;
  margin-top: 0.8rem;
  color: #31586c;
  font-size: 0.76rem;
  font-weight: 800;
  text-underline-offset: 3px;
}

.empty-state {
  display: none;
  padding: 4rem 1rem;
  text-align: center;
  color: var(--ink-muted);
  border: 1px dashed var(--night-line);
  border-radius: var(--radius-lg);
}

.empty-state[data-visible="true"] { display: block; }

.page-footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 4rem;
  padding-top: 1.5rem;
  color: var(--ink-muted);
  border-top: 1px solid var(--night-line);
  font-size: 0.82rem;
}

[data-family-id="timing"], [data-family-filter="timing"] { --family-accent: #7ee7dc; }
[data-family-id="transform"], [data-family-filter="transform"] { --family-accent: #ffbf69; }
[data-family-id="path"], [data-family-filter="path"] { --family-accent: #8cb8ff; }
[data-family-id="parametric"], [data-family-filter="parametric"] { --family-accent: #ff8fb8; }
[data-family-id="field"], [data-family-filter="field"] { --family-accent: #a9ef8e; }
[data-family-id="simulation"], [data-family-filter="simulation"] { --family-accent: #d3a6ff; }
[data-family-id="growth"], [data-family-filter="growth"] { --family-accent: #75d59a; }
[data-family-id="tiling"], [data-family-filter="tiling"] { --family-accent: #f7dd72; }
[data-family-id="paint"], [data-family-filter="paint"] { --family-accent: #ff9776; }
[data-family-id="composition"], [data-family-filter="composition"] { --family-accent: #77d5ff; }

@media (max-width: 1180px) {
  .family-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .gallery { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .catalog-toolbar { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 700px) {
  .page-shell { width: min(100% - 1rem, 1540px); padding-top: 0.5rem; }
  .hero { min-height: 0; padding: 2rem 1.25rem 2.4rem; border-radius: 22px; }
  .hero::after { opacity: 0.45; }
  .hero h1 { font-size: clamp(2.65rem, 16vw, 4.8rem); }
  .section-heading { grid-template-columns: 1fr; gap: 0.8rem; }
  .family-grid, .gallery, .catalog-toolbar { grid-template-columns: 1fr; }
  .family-tile { min-height: 160px; }
  .catalog-toolbar { position: static; }
  .toolbar-actions { justify-content: stretch; }
  .toolbar-actions .button { flex: 1 1 8rem; }
  .card-description { min-height: 0; }
  .page-footer { display: block; }
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { transition-duration: 0.001ms !important; animation-duration: 0.001ms !important; animation-iteration-count: 1 !important; }
  .family-tile:hover { transform: none; }
}
"""


GALLERY_JS = r"""(() => {
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
    const id = decodeURIComponent(location.hash.slice(1));
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
    requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
  }

  const previewObserver = "IntersectionObserver" in window
    ? new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting || entry.target.hidden) return;
          loadPreview(entry.target);
          previewObserver.unobserve(entry.target);
        });
      }, { rootMargin: "1000px 0px" })
    : null;

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
"""


def load_catalog(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Could not load pattern catalog {path}: {error}") from error
    if not isinstance(value, dict):
        raise SystemExit(f"Pattern catalog must be a JSON object: {path}")
    return value


def require_text(value: Any, field: str, record: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"{record} requires a non-empty {field}.")
    return value.strip()


def validate_catalog(catalog: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if catalog.get("namespace") != "procedural-svg":
        raise SystemExit("Pattern catalog namespace must be procedural-svg.")
    families_value = catalog.get("families")
    patterns_value = catalog.get("patterns")
    if not isinstance(families_value, list) or not isinstance(patterns_value, list):
        raise SystemExit("Pattern catalog requires families and patterns arrays.")
    if len(families_value) != EXPECTED_FAMILY_COUNT:
        raise SystemExit(
            f"Gallery requires {EXPECTED_FAMILY_COUNT} families; found {len(families_value)}."
        )
    if len(patterns_value) != EXPECTED_PATTERN_COUNT:
        raise SystemExit(
            f"Gallery requires {EXPECTED_PATTERN_COUNT} patterns; found {len(patterns_value)}."
        )

    families: list[dict[str, Any]] = []
    family_ids: list[str] = []
    for index, raw in enumerate(families_value, start=1):
        if not isinstance(raw, dict):
            raise SystemExit(f"Family record {index} must be an object.")
        family_id = require_text(raw.get("id"), "id", f"Family {index}")
        if not ID_RE.fullmatch(family_id):
            raise SystemExit(f"Invalid family ID: {family_id}")
        families.append(
            {
                "id": family_id,
                "title": require_text(raw.get("title"), "title", family_id),
                "description": require_text(raw.get("description"), "description", family_id),
            }
        )
        family_ids.append(family_id)
    duplicate_families = sorted(key for key, count in Counter(family_ids).items() if count > 1)
    if duplicate_families:
        raise SystemExit(f"Duplicate family IDs: {', '.join(duplicate_families)}")

    valid_families = set(family_ids)
    patterns: list[dict[str, Any]] = []
    pattern_ids: list[str] = []
    example_ids: list[str] = []
    for index, raw in enumerate(patterns_value, start=1):
        if not isinstance(raw, dict):
            raise SystemExit(f"Pattern record {index} must be an object.")
        pattern_id = require_text(raw.get("id"), "id", f"Pattern {index}")
        if not ID_RE.fullmatch(pattern_id) or not pattern_id.startswith("procedural-svg-"):
            raise SystemExit(f"Invalid procedural SVG pattern ID: {pattern_id}")
        if len(pattern_id) > 64:
            raise SystemExit(f"Pattern ID exceeds 64 characters: {pattern_id}")
        example_id = pattern_id.removeprefix("procedural-svg-")
        family_id = require_text(raw.get("family"), "family", pattern_id)
        if family_id not in valid_families:
            raise SystemExit(f"Pattern {pattern_id} references unknown family {family_id}.")
        variant = raw.get("variant")
        if not isinstance(variant, int) or not 0 <= variant <= 5:
            raise SystemExit(f"Pattern {pattern_id} variant must be an integer from 0 to 5.")
        normalized = {
            "id": pattern_id,
            "exampleId": example_id,
            "name": require_text(raw.get("name"), "name", pattern_id),
            "family": family_id,
            "renderer": require_text(raw.get("renderer"), "renderer", pattern_id),
            "variant": variant,
            "driver": require_text(raw.get("driver"), "driver", pattern_id),
            "technique": require_text(raw.get("technique"), "technique", pattern_id),
            "signature": require_text(raw.get("signature"), "signature", pattern_id),
            "description": require_text(raw.get("description"), "description", pattern_id),
        }
        patterns.append(normalized)
        pattern_ids.append(pattern_id)
        example_ids.append(example_id)

    duplicates = sorted(key for key, count in Counter(pattern_ids).items() if count > 1)
    duplicate_examples = sorted(key for key, count in Counter(example_ids).items() if count > 1)
    if duplicates:
        raise SystemExit(f"Duplicate pattern IDs: {', '.join(duplicates)}")
    if duplicate_examples:
        raise SystemExit(f"Duplicate local example IDs: {', '.join(duplicate_examples)}")
    family_counts = Counter(pattern["family"] for pattern in patterns)
    unexpected_counts = {
        family_id: family_counts[family_id]
        for family_id in family_ids
        if family_counts[family_id] != 6
    }
    if unexpected_counts:
        raise SystemExit(f"Each family must contain six patterns; found {unexpected_counts}.")
    return families, patterns


def stable_seed(index: int, pattern_id: str, base_seed: int) -> int:
    digest = hashlib.sha256(pattern_id.encode("utf-8")).digest()
    offset = int.from_bytes(digest[:4], "big") % 900_000
    return base_seed + index * 1009 + offset


def generator_command(generator: Path, arguments: list[str]) -> list[str]:
    uv = shutil.which("uv")
    if uv:
        return [uv, "run", "--script", str(generator), *arguments]
    return [sys.executable, str(generator), *arguments]


def generate_svgs(
    patterns: list[dict[str, Any]],
    destination: Path,
    generator: Path,
    *,
    width: int,
    height: int,
    duration_ms: int,
    palette: str,
    base_seed: int,
) -> list[dict[str, Any]]:
    if not generator.is_file():
        raise SystemExit(
            "Procedural SVG generator is not available yet: "
            f"{generator}. Finish scripts/build_procedural_svg.py before building the gallery."
        )
    destination.mkdir(parents=True, exist_ok=True)
    generated: list[dict[str, Any]] = []
    for index, pattern in enumerate(patterns):
        pattern_id = str(pattern["id"])
        seed = stable_seed(index, pattern_id, base_seed)
        output = destination / f"{pattern_id}.svg"
        arguments = [
            "--pattern",
            pattern_id,
            "--output",
            str(output),
            "--seed",
            str(seed),
            "--width",
            str(width),
            "--height",
            str(height),
            "--duration-ms",
            str(duration_ms),
            "--palette",
            palette,
            "--motion",
            "full",
            "--force",
            "--json",
        ]
        command = generator_command(generator, arguments)
        completed = subprocess.run(
            command,
            cwd=generator.parent,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if completed.returncode != 0:
            details = "\n".join(
                part.strip()
                for part in (completed.stdout, completed.stderr)
                if part and part.strip()
            )
            raise SystemExit(
                f"Generator failed for {pattern_id} with exit code {completed.returncode}."
                + (f"\n{details}" if details else "")
            )
        if not output.is_file() or output.stat().st_size == 0:
            raise SystemExit(f"Generator did not create the expected SVG: {output}")
        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise SystemExit(
                f"Generator returned invalid JSON for {pattern_id}: {error}\n{completed.stdout}"
            ) from error
        if not isinstance(report, dict) or report.get("ok") is not True:
            raise SystemExit(f"Generator returned an unsuccessful report for {pattern_id}: {report!r}")
        outputs = report.get("outputs")
        if not isinstance(outputs, list) or len(outputs) != 1 or not isinstance(outputs[0], dict):
            raise SystemExit(f"Generator returned an invalid output report for {pattern_id}: {report!r}")
        output_report = outputs[0]
        if output_report.get("patternId") != pattern_id:
            raise SystemExit(
                f"Generator report ID mismatch for {pattern_id}: {output_report.get('patternId')!r}"
            )
        generated.append(
            {
                **pattern,
                "seed": seed,
                "svgPath": output,
                "generatorReport": output_report,
            }
        )
    return generated


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def first_text(root: ET.Element, name: str) -> str:
    for element in root.iter():
        if local_name(element.tag) == name:
            return " ".join("".join(element.itertext()).split())
    return ""


def reduced_motion_media_blocks(css_text: str) -> list[str]:
    """Extract balanced reduced-motion @media bodies for structural auditing."""

    text = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    start_pattern = re.compile(
        r"@media\b[^{}]*prefers-reduced-motion[^{}]*\{", re.IGNORECASE
    )
    blocks: list[str] = []
    for match in start_pattern.finditer(text):
        opening = match.end() - 1
        depth = 0
        quote: str | None = None
        escaped = False
        for index in range(opening, len(text)):
            character = text[index]
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if quote:
                if character == quote:
                    quote = None
                continue
            if character in {'"', "'"}:
                quote = character
            elif character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(text[opening + 1 : index])
                    break
    return blocks


def has_smil_reduced_motion_contract(root: ET.Element, css_text: str) -> bool:
    class_sets = [set((element.get("class") or "").split()) for element in root.iter()]
    if not any("psvg-motion-layer" in classes for classes in class_sets):
        return False
    if not any("psvg-reduced-layer" in classes for classes in class_sets):
        return False
    for block in reduced_motion_media_blocks(css_text):
        hides_motion = re.search(
            r"\.psvg-motion-layer\b[^{}]*\{[^{}]*\bdisplay\s*:\s*none\b[^{}]*\}",
            block,
            re.IGNORECASE,
        )
        shows_reduced = re.search(
            r"\.psvg-reduced-layer\b[^{}]*\{[^{}]*\bdisplay\s*:\s*(?!none\b)[-_A-Za-z]+\b[^{}]*\}",
            block,
            re.IGNORECASE,
        )
        if hides_motion and shows_reduced:
            return True
    return False


def root_data_attributes(root: ET.Element) -> dict[str, str]:
    return {
        key.removeprefix("data-"): value
        for key, value in sorted(root.attrib.items())
        if key.startswith("data-")
    }


def first_present(values: dict[str, str], names: Iterable[str], fallback: Any) -> Any:
    for name in names:
        if name in values and values[name] != "":
            return values[name]
    return fallback


def audit_svg(record: dict[str, Any]) -> dict[str, Any]:
    svg_path = Path(record["svgPath"])
    content = svg_path.read_bytes()
    text = content.decode("utf-8")
    try:
        root = ET.fromstring(content)
    except ET.ParseError as error:
        raise SystemExit(f"Generated SVG is not well-formed XML ({svg_path}): {error}") from error
    if local_name(root.tag) != "svg":
        raise SystemExit(f"Generated artifact does not have an SVG root: {svg_path}")
    data = root_data_attributes(root)
    report = record["generatorReport"]
    root_pattern_id = first_present(data, ("pattern-id", "procedural-pattern-id"), "")
    if root_pattern_id != record["id"]:
        raise SystemExit(
            f"SVG {record['id']} must expose matching data-pattern-id; found {root_pattern_id!r}."
        )
    root_family = first_present(data, ("family", "family-id", "pattern-family"), record["family"])
    if root_family != record["family"]:
        raise SystemExit(
            f"SVG {record['id']} family mismatch: expected {record['family']}, found {root_family}."
        )

    counts = Counter(local_name(element.tag) for element in root.iter())
    sha256 = hashlib.sha256(content).hexdigest()
    if report.get("svgSha256") != sha256:
        raise SystemExit(
            f"Generator report hash mismatch for {record['id']}: "
            f"expected {sha256}, found {report.get('svgSha256')}."
        )
    expected_root_values = {
        "example-id": record["exampleId"],
        "renderer": record["renderer"],
        "variant": str(record["variant"]),
        "seed": str(record["seed"]),
        "palette": str(report.get("palette")),
        "motion": str(report.get("motion")),
        "duration-ms": str(report.get("durationMs")),
        "parameter-hash": str(report.get("parameterHash")),
        "driver": record["driver"],
        "technique": record["technique"],
        "deterministic": "true",
        "standalone": "true",
    }
    for attribute, expected in expected_root_values.items():
        actual = data.get(attribute)
        if actual != expected:
            raise SystemExit(
                f"SVG {record['id']} audit mismatch for data-{attribute}: "
                f"expected {expected!r}, found {actual!r}."
            )
    motion_engine = data.get("motion-engine", "")
    if motion_engine not in {"css", "smil", "mixed", "static"}:
        raise SystemExit(
            f"SVG {record['id']} must expose a recognized data-motion-engine; "
            f"found {motion_engine!r}."
        )
    if not re.fullmatch(r"[0-9a-f]{64}", data.get("parameter-hash", "")):
        raise SystemExit(
            f"SVG {record['id']} must expose a 64-character lowercase SHA-256 "
            "data-parameter-hash."
        )
    title = first_text(root, "title")
    description = first_text(root, "desc")
    if not title or not description:
        raise SystemExit(f"SVG {record['id']} requires direct readable title and description text.")
    motion_element_count = sum(
        counts[name] for name in ("animate", "animateMotion", "animateTransform", "set")
    )
    style_text = "\n".join(
        " ".join("".join(element.itertext()).split())
        for element in root.iter()
        if local_name(element.tag) == "style"
    )
    reduced_motion_blocks = reduced_motion_media_blocks(style_text)
    smil_reduced_motion_contract = has_smil_reduced_motion_contract(root, style_text)
    audit = {
        "rootData": data,
        "title": title,
        "description": description,
        "sha256": sha256,
        "bytes": len(content),
        "seed": str(first_present(data, ("seed",), record["seed"])),
        "durationMs": str(
            first_present(data, ("duration-ms", "duration"), "unknown")
        ),
        "loop": str(first_present(data, ("loop", "looping"), "unknown")),
        "motionEngine": str(
            first_present(data, ("motion-engine", "driver", "engine"), record["driver"])
        ),
        "parameterHash": str(
            first_present(
                data,
                ("parameter-hash", "params-hash"),
                report.get("parameterHash", sha256[:16]),
            )
        ),
        "techniques": str(
            first_present(data, ("techniques", "technique"), record["technique"])
        ),
        "motionElementCount": motion_element_count,
        "cssKeyframeCount": len(re.findall(r"@(?:-webkit-)?keyframes\b", text)),
        "scriptCount": counts["script"],
        "hasReducedMotionRule": bool(reduced_motion_blocks),
        "hasSmilReducedMotionContract": smil_reduced_motion_contract,
        "hasRemoteReferences": bool(REMOTE_REFERENCE_RE.search(text)),
        "elementCount": sum(counts.values()),
    }
    if audit["scriptCount"]:
        raise SystemExit(f"Gallery SVG {record['id']} must not contain scripts.")
    if audit["hasRemoteReferences"]:
        raise SystemExit(f"Gallery SVG {record['id']} contains a remote runtime reference.")
    if not audit["hasReducedMotionRule"]:
        raise SystemExit(f"Gallery SVG {record['id']} must include prefers-reduced-motion handling.")
    if (
        data.get("motion") == "full"
        and motion_element_count > 0
        and not audit["hasSmilReducedMotionContract"]
    ):
        raise SystemExit(
            f"Gallery SVG {record['id']} uses SMIL and must include .psvg-motion-layer "
            "and .psvg-reduced-layer elements plus a reduced-motion media rule that "
            "hides motion and shows the reduced layer."
        )
    if motion_element_count + audit["cssKeyframeCount"] == 0:
        raise SystemExit(f"Gallery SVG {record['id']} does not expose declarative motion.")
    return audit


def escape(value: Any, *, quote: bool = False) -> str:
    return html.escape(str(value), quote=quote)


def family_tiles_html(
    families: list[dict[str, Any]], patterns: list[dict[str, Any]]
) -> str:
    counts = Counter(pattern["family"] for pattern in patterns)
    tiles: list[str] = []
    for family in families:
        family_id = str(family["id"])
        tiles.append(
            f'''      <button class="family-tile" type="button" data-family-filter="{escape(family_id, quote=True)}" aria-pressed="false">
        <span class="family-count">{counts[family_id]:02d}</span>
        <strong>{escape(family["title"])}</strong>
        <small>{escape(family["description"])}</small>
      </button>'''
        )
    return "\n".join(tiles)


def select_options(values: Iterable[str], labels: dict[str, str] | None = None) -> str:
    return "\n".join(
        f'          <option value="{escape(value, quote=True)}">{escape((labels or {}).get(value, value))}</option>'
        for value in values
    )


def pattern_cards_html(records: list[dict[str, Any]], family_map: dict[str, dict[str, Any]]) -> str:
    cards: list[str] = []
    for record in records:
        pattern_id = str(record["id"])
        example_id = str(record["exampleId"])
        family_id = str(record["family"])
        family = family_map[family_id]
        audit = record["svgAudit"]
        svg_url = f"./patterns/{pattern_id}.svg"
        search = " ".join(
            str(record[key])
            for key in ("id", "name", "family", "driver", "technique", "signature", "description")
        ).lower()
        short_hash = str(audit["sha256"])[:12]
        duration = str(audit["durationMs"])
        duration_label = f"{duration} ms" if duration.isdigit() else duration
        cards.append(
            f'''    <article class="pattern-card" id="{escape(pattern_id, quote=True)}" data-example-id="{escape(example_id, quote=True)}" data-pattern-id="{escape(pattern_id, quote=True)}" data-family-id="{escape(family_id, quote=True)}" data-driver="{escape(record['driver'], quote=True)}" data-renderer="{escape(record['renderer'], quote=True)}" data-technique="{escape(record['technique'], quote=True)}" data-search="{escape(search, quote=True)}" data-playback-state="queued" data-svg-seed="{escape(audit['seed'], quote=True)}" data-svg-duration-ms="{escape(audit['durationMs'], quote=True)}" data-svg-motion-engine="{escape(audit['motionEngine'], quote=True)}" data-svg-parameter-hash="{escape(audit['parameterHash'], quote=True)}" data-svg-sha256="{escape(audit['sha256'], quote=True)}" data-svg-motion-count="{audit['motionElementCount'] + audit['cssKeyframeCount']}" data-svg-reduced-motion="{str(audit['hasReducedMotionRule']).lower()}">
      <div class="preview-shell">
        <span class="preview-state" data-preview-state>Queued</span>
        <object class="pattern-preview" data-pattern-preview data-source="{escape(svg_url, quote=True)}" type="image/svg+xml" aria-label="Animated preview of {escape(record['name'], quote=True)}">
          <a href="{escape(svg_url, quote=True)}">Open {escape(record['name'])} SVG</a>
        </object>
      </div>
      <div class="card-body">
        <div class="card-kicker"><span class="family-label">{escape(family['title'])}</span><span>{escape(record['driver'])}</span></div>
        <h3>{escape(record['name'])}</h3>
        <a class="canonical-link" href="#{escape(pattern_id, quote=True)}" aria-label="Deep link to {escape(record['name'], quote=True)}"><code>{escape(pattern_id)}</code></a>
        <p class="card-description">{escape(record['description'])}</p>
        <p class="signature">{escape(record['signature'])}</p>
        <ul class="metadata-list" aria-label="SVG audit metadata">
          <li>{escape(record['technique'])}</li>
          <li>seed {escape(audit['seed'])}</li>
          <li>{escape(duration_label)}</li>
          <li>{audit['elementCount']} elements</li>
          <li>sha {escape(short_hash)}</li>
        </ul>
        <div class="card-controls" aria-label="Playback controls for {escape(record['name'], quote=True)}">
          <button class="button" type="button" data-action="pause">Pause</button>
          <button class="button" type="button" data-action="play">Play</button>
          <button class="button" type="button" data-action="replay">Replay</button>
        </div>
        <a class="open-svg" href="{escape(svg_url, quote=True)}" target="_blank" rel="noopener">Open standalone SVG</a>
      </div>
    </article>'''
        )
    return "\n".join(cards)


def render_index(
    families: list[dict[str, Any]],
    records: list[dict[str, Any]],
    catalog_hash: str,
) -> str:
    family_map = {str(family["id"]): family for family in families}
    family_labels = {str(family["id"]): str(family["title"]) for family in families}
    drivers = sorted({str(record["driver"]) for record in records}, key=str.casefold)
    family_options = select_options((str(family["id"]) for family in families), family_labels)
    driver_options = select_options(drivers)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Sixty deterministic procedural SVG animation patterns across ten reusable technique families.">
  <meta name="example-id" content="{PAGE_ID}">
  <meta name="pattern-id" content="{PAGE_ID}">
  <meta name="pattern-page" content="true">
  <meta name="pattern-count" content="{len(records)}">
  <meta name="family-count" content="{len(families)}">
  <meta name="catalog-hash" content="{catalog_hash}">
  <title>Procedural SVG Animation Patterns</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%23111827'/%3E%3Cpath d='M12 39C22 7 42 57 52 25' fill='none' stroke='%235eead4' stroke-width='7' stroke-linecap='round'/%3E%3C/svg%3E">
  <link rel="stylesheet" href="./gallery.css">
</head>
<body data-example-id="{PAGE_ID}" data-pattern-id="{PAGE_ID}" data-pattern-page="true" data-pattern-count="{len(records)}" data-family-count="{len(families)}" data-catalog-hash="{catalog_hash}" data-reduced-motion="false">
  <a class="skip-link" href="#catalog-heading">Skip to pattern catalog</a>
  <main class="page-shell">
    <header class="hero">
      <p class="eyebrow">Deterministic motion systems · acceptance catalog</p>
      <h1>Procedural SVG Animation</h1>
      <p class="hero-copy">Sixty self-contained SVG mechanisms organized as reusable families: timing, kinematics, path choreography, parametric curves, fields, simulation, growth, tiling, paint, and hybrid composition.</p>
      <div class="hero-meta" aria-label="Catalog summary">
        <span><strong>{len(records)}</strong>&nbsp;canonical patterns</span>
        <span><strong>{len(families)}</strong>&nbsp;families</span>
        <span>seeded · standalone · replayable</span>
        <a class="manifest-link" href="./manifest.json">JSON manifest</a>
      </div>
    </header>

    <section aria-labelledby="families-heading">
      <div class="section-heading">
        <h2 id="families-heading">Technique families</h2>
        <p>Each family shares a programmable mechanism. Select one to filter the catalog; select it again to return to all patterns.</p>
      </div>
      <div class="family-grid">
{family_tiles_html(families, records)}
      </div>
    </section>

    <section aria-labelledby="catalog-heading">
      <div class="section-heading">
        <h2 id="catalog-heading">Pattern catalog</h2>
        <p>Search by canonical ID, mechanism, formula, family, or driver. Every preview links to its standalone SVG and exposes deterministic audit metadata.</p>
      </div>

      <div class="catalog-toolbar" aria-label="Pattern filters and playback controls">
        <label class="control-field">
          <span>Search</span>
          <input id="pattern-search" type="search" placeholder="Try curl, morph, field, SMIL…" autocomplete="off">
        </label>
        <label class="control-field">
          <span>Family</span>
          <select id="family-filter">
            <option value="">All families</option>
{family_options}
          </select>
        </label>
        <label class="control-field">
          <span>Driver</span>
          <select id="driver-filter">
            <option value="">All drivers</option>
{driver_options}
          </select>
        </label>
        <div class="toolbar-actions">
          <button class="button" id="pause-all" type="button" aria-pressed="false">Pause all</button>
          <button class="button" id="play-all" type="button">Play loaded</button>
          <button class="button primary" id="replay-all" type="button">Replay loaded</button>
          <button class="button" id="reset-filters" type="button">Reset</button>
        </div>
      </div>

      <div class="results-bar">
        <span><strong id="visible-count">{len(records)}</strong> of {len(records)} patterns</span>
        <span class="motion-note">Reduced motion is active; previews start paused.</span>
        <span id="filter-status" class="visually-hidden" role="status" aria-live="polite"></span>
      </div>

      <div class="gallery" id="gallery" aria-label="Procedural SVG pattern cards">
{pattern_cards_html(records, family_map)}
      </div>
      <div class="empty-state" id="empty-state" data-visible="false">
        <h3>No patterns match those filters.</h3>
        <p>Reset the catalog or broaden the search term.</p>
      </div>
    </section>

    <footer class="page-footer">
      <span>Generated from <code>assets/pattern-specs.json</code>.</span>
      <span>Catalog fingerprint <code>{catalog_hash}</code></span>
    </footer>
  </main>
  <script src="./gallery.js"></script>
</body>
</html>
'''


def build_manifest(
    catalog: dict[str, Any],
    families: list[dict[str, Any]],
    records: list[dict[str, Any]],
    *,
    width: int,
    height: int,
    duration_ms: int,
    palette: str,
    base_seed: int,
    catalog_hash: str,
) -> dict[str, Any]:
    family_map = {str(family["id"]): family for family in families}
    return {
        "version": 1,
        "pageId": PAGE_ID,
        "title": "Procedural SVG Animation Patterns",
        "description": "Deterministic standalone SVG motion mechanisms and reusable combinations.",
        "generatedBy": "scripts/build_procedural_gallery.py",
        "sourceCatalog": "assets/pattern-specs.json",
        "sourceCatalogVersion": catalog.get("version"),
        "catalogHash": catalog_hash,
        "patternCount": len(records),
        "familyCount": len(families),
        "defaults": {
            "width": width,
            "height": height,
            "durationMs": duration_ms,
            "palette": palette,
            "baseSeed": base_seed,
        },
        "families": [
            {
                **family,
                "patternCount": sum(record["family"] == family["id"] for record in records),
            }
            for family in families
        ],
        "patterns": [
            {
                key: record[key]
                for key in (
                    "id",
                    "exampleId",
                    "name",
                    "family",
                    "renderer",
                    "variant",
                    "driver",
                    "technique",
                    "signature",
                    "description",
                    "seed",
                )
            }
            | {
                "familyTitle": family_map[str(record["family"])]["title"],
                "svg": {
                    "path": f"patterns/{record['id']}.svg",
                    **record["svgAudit"],
                },
            }
            for record in records
        ],
    }


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def materialize_build(
    destination: Path,
    catalog: dict[str, Any],
    families: list[dict[str, Any]],
    patterns: list[dict[str, Any]],
    generator: Path,
    *,
    width: int,
    height: int,
    duration_ms: int,
    palette: str,
    base_seed: int,
) -> dict[str, Any]:
    svg_dir = destination / "patterns"
    generated = generate_svgs(
        patterns,
        svg_dir,
        generator,
        width=width,
        height=height,
        duration_ms=duration_ms,
        palette=palette,
        base_seed=base_seed,
    )
    records: list[dict[str, Any]] = []
    for record in generated:
        records.append({**record, "svgAudit": audit_svg(record)})
    catalog_bytes = json.dumps(catalog, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    catalog_hash = hashlib.sha256(catalog_bytes).hexdigest()[:16]
    manifest = build_manifest(
        catalog,
        families,
        records,
        width=width,
        height=height,
        duration_ms=duration_ms,
        palette=palette,
        base_seed=base_seed,
        catalog_hash=catalog_hash,
    )
    write_text(destination / "gallery.css", GALLERY_CSS.strip() + "\n")
    write_text(destination / "gallery.js", GALLERY_JS.strip() + "\n")
    write_text(destination / "index.html", render_index(families, records, catalog_hash))
    write_text(
        destination / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )
    return manifest


def managed_relative_files(root: Path) -> list[Path]:
    paths = [Path(name) for name in MANAGED_PAGE_FILES if (root / name).is_file()]
    pattern_root = root / "patterns"
    if pattern_root.is_dir():
        paths.extend(path.relative_to(root) for path in sorted(pattern_root.glob("*.svg")))
    return sorted(paths, key=lambda path: path.as_posix())


def compare_build(expected: Path, actual: Path) -> dict[str, list[str]]:
    expected_files = set(managed_relative_files(expected))
    actual_files = set(managed_relative_files(actual))
    missing = sorted(path.as_posix() for path in expected_files - actual_files)
    extra = sorted(path.as_posix() for path in actual_files - expected_files)
    changed = sorted(
        path.as_posix()
        for path in expected_files & actual_files
        if (expected / path).read_bytes() != (actual / path).read_bytes()
    )
    return {"missing": missing, "extra": extra, "changed": changed}


def sync_build(expected: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    expected_files = set(managed_relative_files(expected))
    actual_files = set(managed_relative_files(destination))
    for relative in sorted(actual_files - expected_files, key=lambda path: path.as_posix()):
        target = (destination / relative).resolve()
        if destination.resolve() not in target.parents:
            raise SystemExit(f"Refusing to remove a path outside the gallery: {target}")
        target.unlink()
    for relative in sorted(expected_files, key=lambda path: path.as_posix()):
        source = expected / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the deterministic procedural SVG acceptance gallery."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Gallery destination (defaults to the published acceptance fixture)",
    )
    parser.add_argument(
        "--generator",
        type=Path,
        default=GENERATOR_PATH,
        help="Path to build_procedural_svg.py",
    )
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=600)
    parser.add_argument("--duration-ms", type=int, default=8000)
    parser.add_argument("--palette", choices=("colorset1", "colorset2"), default="colorset2")
    parser.add_argument("--base-seed", type=int, default=104729)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Rebuild in a temporary directory and fail if committed output differs",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not 320 <= args.width <= 4096:
        raise SystemExit("--width must be between 320 and 4096.")
    if not 240 <= args.height <= 4096:
        raise SystemExit("--height must be between 240 and 4096.")
    if not 400 <= args.duration_ms <= 120000:
        raise SystemExit("--duration-ms must be between 400 and 120000.")

    catalog = load_catalog(CATALOG_PATH)
    families, patterns = validate_catalog(catalog)
    output_dir = args.output_dir.expanduser().resolve()
    generator = args.generator.expanduser().resolve()
    with tempfile.TemporaryDirectory(prefix="procedural-svg-gallery-") as temporary:
        staged = Path(temporary) / PAGE_ID
        manifest = materialize_build(
            staged,
            catalog,
            families,
            patterns,
            generator,
            width=args.width,
            height=args.height,
            duration_ms=args.duration_ms,
            palette=args.palette,
            base_seed=args.base_seed,
        )
        if args.check:
            differences = compare_build(staged, output_dir)
            ok = not any(differences.values())
            print(
                json.dumps(
                    {
                        "ok": ok,
                        "mode": "check",
                        "outputDir": str(output_dir),
                        "patternCount": manifest["patternCount"],
                        "catalogHash": manifest["catalogHash"],
                        **differences,
                    },
                    indent=2,
                )
            )
            return 0 if ok else 1
        sync_build(staged, output_dir)

    result = {
        "ok": True,
        "mode": "build",
        "outputDir": str(output_dir),
        "page": str(output_dir / "index.html"),
        "manifest": str(output_dir / "manifest.json"),
        "patternCount": manifest["patternCount"],
        "familyCount": manifest["familyCount"],
        "catalogHash": manifest["catalogHash"],
        "standaloneSvgCount": len(list((output_dir / "patterns").glob("*.svg"))),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
