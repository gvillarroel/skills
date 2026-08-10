Use the `mermaid` skill to create a batch of Mermaid source diagrams from the eight independent requests below.

Work only from the copied skill and this prompt. Treat `skills/mermaid/` as read-only. Keep generated files in the workspace. Do not inspect repository files, sibling skills, acceptance galleries, prior runs, or network resources. The evaluator will render the sources independently, so do not install packages or create SVG/PNG files.

For every diagram:

- Preserve every supplied name, relationship, order, date, unit, weight, and coordinate.
- Honor an explicitly requested diagram type. When no type is named, choose the Mermaid family that best communicates the data.
- Use the standard palette unless that individual request explicitly asks for extended colors.
- Apply palettes with the bundled styling script and finish with a successful `--check` pass.

## Requests

### case-01

The stakeholder explicitly requests a flowchart for this approval process:

- Intake leads to Validate.
- Valid requests lead to Authorize.
- Invalid requests lead to Repair, then return to Validate.
- Authorize leads to Archive.

Use the standard palette.

### case-02

The stakeholder explicitly requests a sequence diagram and explicitly wants extended colors. Preserve this interaction order:

1. Client sends `Submit order` to Gateway.
2. Gateway sends `Reserve items` to Inventory.
3. Inventory returns `Reserved` to Gateway.
4. Gateway sends `Charge 125 USD` to Payment.
5. Payment returns `Approved` to Gateway.
6. Gateway returns `Order confirmed` to Client.

### case-03

Choose the most appropriate diagram for this commerce data model. Use the standard palette.

- CUSTOMER: customer_id PK, email
- ORDER: order_id PK, customer_id FK, placed_at
- ORDER_ITEM: order_id PK/FK, product_id PK/FK, quantity
- PRODUCT: product_id PK, name, unit_price_usd
- One CUSTOMER may place zero or many ORDER records; each ORDER belongs to exactly one CUSTOMER.
- Each ORDER contains one or many ORDER_ITEM records; each ORDER_ITEM belongs to exactly one ORDER.
- Each PRODUCT may occur in zero or many ORDER_ITEM records; each ORDER_ITEM references exactly one PRODUCT.

### case-04

Choose the most appropriate diagram for these weighted energy transfers and explicitly use extended colors. Values are GWh and must stay exact.

```text
Solar -> Grid: 42
Wind -> Grid: 35
Grid -> Residential: 46
Grid -> Industry: 24
Grid -> Storage: 7
Storage -> Residential: 4
```

### case-05

Choose the most appropriate diagram for these support-ticket lifecycle rules. Use the standard palette.

- New can become Triaged.
- Triaged can become In Progress or Rejected.
- In Progress can become Waiting on Customer or Resolved.
- Waiting on Customer can return to In Progress.
- Resolved can become Closed or Reopened.
- Reopened returns to In Progress.
- Closed and Rejected are terminal.

### case-06

Choose the most appropriate diagram for quarterly revenue. Use the standard palette, preserve USD millions, and keep the quarters ordered.

```text
Q1: 12
Q2: 18
Q3: 15
Q4: 24
```

### case-07

Choose the most appropriate diagram for this release plan. Use the standard palette and preserve all dates and dependencies.

- Design: starts 2026-09-01, lasts 5 days.
- API: starts after Design, lasts 8 days.
- UI: starts after Design, lasts 6 days.
- Integration: starts after both API and UI, lasts 4 days.
- Release: milestone after Integration on 2026-09-22.

### case-08

Choose the most appropriate diagram for feature prioritization and explicitly use extended colors. The x-axis is Effort from low to high; the y-axis is Impact from low to high. Preserve these normalized coordinates:

```text
Search: (0.25, 0.82)
Bulk export: (0.70, 0.45)
Audit log: (0.45, 0.74)
Theme picker: (0.20, 0.30)
```

## Exact Outputs

Create exactly these required files (additional temporary reports are allowed outside `skills/mermaid/`):

- `deliverables/standard/case-01.mmd`
- `deliverables/extended/case-02.mmd`
- `deliverables/standard/case-03.mmd`
- `deliverables/extended/case-04.mmd`
- `deliverables/standard/case-05.mmd`
- `deliverables/standard/case-06.mmd`
- `deliverables/standard/case-07.mmd`
- `deliverables/extended/case-08.mmd`
- `deliverables/selection.json`
- `deliverables/style-standard-report.json`
- `deliverables/style-standard-check.json`
- `deliverables/style-extended-report.json`
- `deliverables/style-extended-check.json`

`deliverables/selection.json` must be valid JSON with a top-level `cases` array containing exactly eight objects in case order. Each object must have `id`, `output`, `selectedFamily`, `declaration`, `colorset`, and a concise `reason`. Use the canonical family ID from `references/diagram-types.json` for `selectedFamily`. Record only the first Mermaid declaration token (without orientation or arguments) in `declaration`, and record exactly `colorset1` or `colorset2` in `colorset`.

The two check reports must end with `missingStyleCount` equal to `0`. Do not finish until every exact output exists and is non-empty.
