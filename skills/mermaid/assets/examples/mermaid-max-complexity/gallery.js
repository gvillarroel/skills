const gallery = document.querySelector("#gallery")
const familyNav = document.querySelector("#family-nav")
const searchInput = document.querySelector("#search")
const categoryFilter = document.querySelector("#category-filter")
const visibleCount = document.querySelector("#visible-count")
const emptyState = document.querySelector("#empty-state")
const paletteButtons = [...document.querySelectorAll("[data-palette-view]")]

const state = {
  manifest: null,
  paletteView: "both",
  search: "",
  category: "all",
  legacyMap: new Map(),
}

function element(tagName, attributes = {}, text = "") {
  const node = document.createElement(tagName)
  for (const [name, value] of Object.entries(attributes)) {
    if (value === undefined || value === null || value === false) continue
    if (name === "className") node.className = value
    else if (name === "dataset") Object.assign(node.dataset, value)
    else if (name === "hidden") node.hidden = Boolean(value)
    else node.setAttribute(name, String(value))
  }
  if (text) node.textContent = text
  return node
}

function patternFor(familyId, variant) {
  return state.manifest.patterns.find((pattern) => pattern.familyId === familyId && pattern.variant === variant)
}

function capacityLabel(family) {
  if (family.maxSlots === null) return "unbounded surface"
  if (family.capacityKind === "reachable-cycle") return `${family.maxSlots} distinct + boundary`
  return `${family.maxSlots} terminal slots`
}

function createActionLink(label, href) {
  return element("a", { href, target: "_blank", rel: "noreferrer" }, label)
}

function replayImage(image) {
  const base = image.dataset.baseSrc
  image.src = `${base}?replay=${Date.now()}`
}

async function toggleSource(button, pre, sourcePath) {
  if (!pre.dataset.loaded) {
    button.disabled = true
    button.textContent = "Loading…"
    try {
      const response = await fetch(sourcePath)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      pre.textContent = await response.text()
      pre.dataset.loaded = "true"
    } catch (error) {
      pre.textContent = `Source could not be loaded: ${error.message}`
    } finally {
      button.disabled = false
    }
  }
  pre.hidden = !pre.hidden
  button.textContent = pre.hidden ? "View source" : "Hide source"
  button.setAttribute("aria-expanded", String(!pre.hidden))
}

function createVariant(family, pattern, index) {
  const paletteName = pattern.variant === "cs1" ? "Colorset 1 · standard" : "Colorset 2 · extended"
  const variant = element("section", {
    className: "variant",
    id: pattern.id,
    dataset: {
      patternId: pattern.id,
      exampleId: family.slug,
      variant: pattern.variant,
      colorset: pattern.colorset,
    },
    "aria-labelledby": `${pattern.id}-title`,
  })

  const heading = element("div", { className: "variant__heading" })
  heading.append(
    element("h4", { id: `${pattern.id}-title` }, paletteName),
    element("span", { className: "variant__id", title: pattern.id }, pattern.id),
  )

  const preview = element("div", { className: "preview" })
  const image = element("img", {
    src: pattern.animatedSvg,
    alt: `${family.label} maximum-complexity diagram in ${paletteName}`,
    loading: index < 2 ? "eager" : "lazy",
    decoding: "async",
    dataset: {
      baseSrc: pattern.animatedSvg,
      exampleId: family.slug,
      patternId: pattern.id,
    },
  })
  preview.append(image)

  const actions = element("div", { className: "variant__actions" })
  const replay = element("button", { type: "button" }, "Replay")
  replay.addEventListener("click", () => replayImage(image))
  const sourceButton = element("button", { type: "button", "aria-expanded": "false" }, "View source")
  const copyButton = element("button", { type: "button" }, "Copy ID")
  copyButton.addEventListener("click", async () => {
    await navigator.clipboard.writeText(pattern.id)
    copyButton.textContent = "Copied"
    window.setTimeout(() => { copyButton.textContent = "Copy ID" }, 1200)
  })
  actions.append(
    replay,
    sourceButton,
    createActionLink("Static SVG", pattern.staticSvg),
    createActionLink("Animated SVG", pattern.animatedSvg),
    createActionLink("Source file", pattern.source),
    copyButton,
  )

  const sourceView = element("pre", { className: "source-view", hidden: true })
  sourceButton.addEventListener("click", () => toggleSource(sourceButton, sourceView, pattern.source))
  variant.append(heading, preview, actions, sourceView)
  return variant
}

function createContract(family) {
  const details = element("details")
  details.append(element("summary", {}, "Complexity and declaration contract"))
  const list = element("dl", { className: "contract-grid" })
  const contracts = [
    ["Capacity kind", family.capacityKind],
    ["Fixture elements", String(family.fixtureElementCount)],
    ["Accepted declarations", family.acceptedDeclarations.join(", ")],
  ]
  for (const [term, definition] of contracts) {
    const wrapper = element("div")
    wrapper.append(element("dt", {}, term), element("dd", {}, definition))
    list.append(wrapper)
  }
  details.append(list)
  return details
}

function createFamilyCard(family, index) {
  const cs1 = patternFor(family.familyId, "cs1")
  const cs2 = patternFor(family.familyId, "cs2")
  if (!cs1 || !cs2) throw new Error(`Missing palette variants for ${family.familyId}`)

  for (const legacyId of family.legacyIds || []) state.legacyMap.set(legacyId, cs1.id)

  const card = element("article", {
    className: "family-card",
    id: `family-${family.slug}`,
    dataset: {
      familyId: family.familyId,
      familySlug: family.slug,
      category: family.category,
      search: [family.label, family.declaration, family.category, family.relationship, family.complexityNote].join(" ").toLowerCase(),
    },
  })

  const header = element("header", { className: "family-card__header" })
  const titleGroup = element("div")
  titleGroup.append(
    element("h3", {}, family.label),
    element("code", { className: "family-card__declaration" }, family.declaration),
  )
  header.append(
    element("span", { className: "family-card__number", "aria-hidden": "true" }, String(index + 1).padStart(2, "0")),
    titleGroup,
    element("span", { className: "category-pill" }, family.category),
  )

  const summary = element("div", { className: "family-card__summary" })
  summary.append(
    element("p", {}, family.relationship),
    element("p", { className: "capacity-note" }),
  )
  summary.lastElementChild.append(
    element("span", { className: "capacity-pill" }, capacityLabel(family)),
    document.createTextNode(family.complexityNote),
  )

  const variants = element("div", { className: "variants", dataset: { paletteView: "both" } })
  variants.append(createVariant(family, cs1, index), createVariant(family, cs2, index))
  card.append(header, summary, variants, createContract(family))
  return card
}

function populateCategoryFilter(families) {
  const categories = [...new Set(families.map((family) => family.category))].sort()
  for (const category of categories) {
    categoryFilter.append(element("option", { value: category }, category[0].toUpperCase() + category.slice(1)))
  }
}

function populateFamilyNav(families) {
  const fragment = document.createDocumentFragment()
  for (const family of families) {
    fragment.append(element("a", { href: `#family-${family.slug}`, dataset: { familySlug: family.slug } }, family.label))
  }
  familyNav.replaceChildren(fragment)
}

function applyFilters() {
  const cards = [...gallery.querySelectorAll(".family-card")]
  let visible = 0
  for (const card of cards) {
    const matchesSearch = !state.search || card.dataset.search.includes(state.search)
    const matchesCategory = state.category === "all" || card.dataset.category === state.category
    card.hidden = !(matchesSearch && matchesCategory)
    if (!card.hidden) visible += 1
  }
  for (const link of familyNav.querySelectorAll("a")) {
    const card = gallery.querySelector(`[data-family-slug="${CSS.escape(link.dataset.familySlug)}"]`)
    link.hidden = card?.hidden ?? true
  }
  visibleCount.textContent = `${visible} of ${cards.length} families visible`
  emptyState.hidden = visible !== 0
}

function setPaletteView(view) {
  state.paletteView = view
  for (const button of paletteButtons) {
    const active = button.dataset.paletteView === view
    button.classList.toggle("is-active", active)
    button.setAttribute("aria-pressed", String(active))
  }
  for (const variants of gallery.querySelectorAll(".variants")) variants.dataset.paletteView = view
  for (const variant of gallery.querySelectorAll(".variant")) {
    variant.hidden = view !== "both" && variant.dataset.variant !== view
  }
}

function resolveHash() {
  const rawHash = decodeURIComponent(window.location.hash.slice(1))
  if (!rawHash) return
  const canonicalId = state.legacyMap.get(rawHash) || rawHash
  const target = document.getElementById(canonicalId)
  if (!target) return
  if (canonicalId !== rawHash) history.replaceState(null, "", `${location.pathname}${location.search}#${canonicalId}`)
  const variant = target.dataset.variant
  if (variant && state.paletteView !== "both" && state.paletteView !== variant) setPaletteView(variant)
  requestAnimationFrame(() => target.scrollIntoView({ block: "start" }))
}

async function loadGallery() {
  const response = await fetch("gallery.json")
  if (!response.ok) throw new Error(`Gallery manifest returned HTTP ${response.status}`)
  const manifest = await response.json()
  if (manifest.familyCount !== 31 || manifest.patternCount !== 62) {
    throw new Error(`Unexpected gallery coverage: ${manifest.familyCount} families and ${manifest.patternCount} patterns`)
  }
  state.manifest = manifest
  document.querySelector("#family-count").textContent = manifest.familyCount
  document.querySelector("#pattern-count").textContent = manifest.patternCount
  document.querySelector("#capacity-count").textContent = manifest.finiteCapacitySlots
  document.querySelector("#output-count").textContent = manifest.outputCount
  populateCategoryFilter(manifest.families)
  populateFamilyNav(manifest.families)

  const fragment = document.createDocumentFragment()
  manifest.families.forEach((family, index) => fragment.append(createFamilyCard(family, index)))
  gallery.replaceChildren(fragment)
  gallery.setAttribute("aria-busy", "false")
  document.documentElement.dataset.galleryReady = "true"
  applyFilters()
  setPaletteView("both")
  resolveHash()
}

searchInput.addEventListener("input", () => {
  state.search = searchInput.value.trim().toLowerCase()
  applyFilters()
})

categoryFilter.addEventListener("change", () => {
  state.category = categoryFilter.value
  applyFilters()
})

for (const button of paletteButtons) {
  button.addEventListener("click", () => setPaletteView(button.dataset.paletteView))
}

window.addEventListener("hashchange", resolveHash)

loadGallery().catch((error) => {
  gallery.setAttribute("aria-busy", "false")
  gallery.textContent = `The Mermaid gallery could not be loaded: ${error.message}`
  visibleCount.textContent = "Gallery unavailable"
  document.documentElement.dataset.galleryReady = "error"
})
