const gallery = document.querySelector("#gallery");
const template = document.querySelector("#artwork-template");
const searchInput = document.querySelector("#search");
const genreFilter = document.querySelector("#genre-filter");
const visibleCount = document.querySelector("#visible-count");
const emptyState = document.querySelector("#empty-state");
const colorsetButtons = [...document.querySelectorAll(".colorset-button")];

const state = {
  manifest: null,
  colorset: "colorset1",
  search: "",
  genre: "",
  cards: [],
};

function normalized(value) {
  return String(value ?? "")
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();
}

function variantFor(artwork) {
  return artwork.variants[state.colorset];
}

function updateCardVariant(record) {
  const variant = variantFor(record.artwork);
  record.card.dataset.patternId = variant.patternId;
  record.image.src = variant.file;
  record.image.alt = `${record.artwork.title}, rendered with ${state.colorset}`;
  record.imageLink.href = variant.file;
  record.openLink.href = variant.file;
  record.downloadLink.href = variant.file;
  record.downloadLink.download = variant.file.split("/").pop();
  record.pathCount.textContent = variant.pathCount.toLocaleString();
}

function updateColorset(colorset) {
  state.colorset = colorset;
  document.documentElement.dataset.activeColorset = colorset;
  for (const button of colorsetButtons) {
    const active = button.dataset.colorset === colorset;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  }
  for (const record of state.cards) {
    updateCardVariant(record);
  }
}

function cardMatches(record) {
  const haystack = normalized(
    `${record.artwork.title} ${record.artwork.creator} ${record.artwork.date} ${record.artwork.id}`,
  );
  const searchMatches = !state.search || haystack.includes(state.search);
  const genreMatches = !state.genre || record.artwork.genre === state.genre;
  return searchMatches && genreMatches;
}

function applyFilters() {
  let count = 0;
  for (const record of state.cards) {
    const matches = cardMatches(record);
    record.card.hidden = !matches;
    if (matches) {
      count += 1;
    }
  }
  visibleCount.textContent = count.toLocaleString();
  emptyState.hidden = count !== 0;
}

function createCard(artwork, index) {
  const fragment = template.content.cloneNode(true);
  const card = fragment.querySelector(".artwork-card");
  const imageLink = fragment.querySelector(".image-link");
  const image = fragment.querySelector(".artwork-image");
  const openLink = fragment.querySelector(".open-svg");
  const downloadLink = fragment.querySelector(".download-svg");
  const sourceLink = fragment.querySelector(".source-link");
  const pathCount = fragment.querySelector(".path-count");

  card.id = artwork.id;
  card.dataset.exampleId = artwork.id;
  card.dataset.sourceId = artwork.sourceId;
  card.dataset.genre = artwork.genre;
  image.loading = index < 6 || index >= 27 ? "eager" : "lazy";
  image.decoding = "async";

  fragment.querySelector(".genre").textContent = artwork.genre;
  fragment.querySelector(".mode").textContent = `${artwork.mode} · VTracer`;
  fragment.querySelector("h3").textContent = artwork.title;
  fragment.querySelector(".creator").textContent = artwork.creator;
  fragment.querySelector(".date").textContent = artwork.date || "Date not recorded";
  fragment.querySelector(".source-id").textContent = artwork.sourceId;
  fragment.querySelector(".geometry").textContent = artwork.geometrySha256.slice(0, 12);
  fragment.querySelector(".license").textContent = artwork.license;
  sourceLink.href = artwork.sourcePage;

  const record = {
    artwork,
    card,
    image,
    imageLink,
    openLink,
    downloadLink,
    pathCount,
  };
  updateCardVariant(record);
  gallery.append(fragment);
  return record;
}

function populateGenres(genres) {
  for (const genre of genres) {
    const option = document.createElement("option");
    option.value = genre;
    option.textContent = genre.replaceAll("-", " ");
    genreFilter.append(option);
  }
}

function navigateToHash() {
  const id = decodeURIComponent(location.hash.slice(1));
  if (!id) {
    return;
  }
  const target = document.getElementById(id);
  if (target) {
    target.scrollIntoView({ block: "start" });
    target.querySelector(".image-link")?.focus({ preventScroll: true });
  }
}

async function initialize() {
  const response = await fetch("manifest.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Manifest request failed: HTTP ${response.status}`);
  }
  const manifest = await response.json();
  if (
    manifest.schemaVersion !== 3 ||
    manifest.pageId !== "vectorize-art-patterns" ||
    manifest.artworkCount !== 30 ||
    manifest.variantCount !== 60
  ) {
    throw new Error("Manifest contract does not match the open-masterpiece gallery");
  }
  state.manifest = manifest;
  document.querySelector("#artwork-count").textContent = manifest.artworkCount;
  document.querySelector("#variant-count").textContent = manifest.variantCount;
  populateGenres(manifest.genres);
  state.cards = manifest.artworks.map(createCard);
  updateColorset(state.colorset);
  applyFilters();
  requestAnimationFrame(navigateToHash);
}

for (const button of colorsetButtons) {
  button.addEventListener("click", () => updateColorset(button.dataset.colorset));
}

searchInput.addEventListener("input", () => {
  state.search = normalized(searchInput.value.trim());
  applyFilters();
});

genreFilter.addEventListener("change", () => {
  state.genre = genreFilter.value;
  applyFilters();
});

window.addEventListener("hashchange", navigateToHash);

initialize().catch((error) => {
  console.error(error);
  gallery.innerHTML = "";
  emptyState.hidden = false;
  emptyState.textContent = "The gallery could not load its validated manifest.";
});
