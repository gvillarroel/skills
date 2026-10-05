# Runtime SVG pack contract

Copy the loaded skill's runtime SVG asset pack into a minimal Slidev deck
and create one slide using its timeline-machine component. Mount it, build
the deck, and verify the machine paths and moving signal appear in replay
and the settled click states. Keep the source asset geometry and readable
labels intact.

Write exactly `deck/slides.md`, `deck/package.json`,
`deck/components/SvgAssetSlide.vue` and `deliverables/layout-review.md`.
Record actual build and browser findings. Do not publish anything.

Treat `skills/slidev-animejs/` as read-only. Generated files belong outside
it. Copy only the runtime template, never acceptance examples. Use normal
local tools and install dependencies only inside this workspace.
