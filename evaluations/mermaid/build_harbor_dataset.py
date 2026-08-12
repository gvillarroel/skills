#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Build the private native-Harbor Mermaid selection evaluation datasets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path


MERMAID_VERSION = "11.16.0"
MODEL = "gpt-5.6-luna"
REASONING_EFFORT = "medium"
CODEX_VERSION = "0.147.0"


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    split: str
    prompt: str
    family: str
    declarations: tuple[str, ...]
    colorset: str
    required_terms: tuple[str, ...]
    patterns: tuple[str, ...] = ()
    forbidden_patterns: tuple[str, ...] = ()
    ordered_terms: tuple[str, ...] = ()
    minimum_arrow_count: int = 0
    minimum_indented_lines: int = 0
    visible_terms: tuple[str, ...] = ()
    minimum_rendered_text_items: int = 0
    maximum_aspect_ratio: float = 0.0
    reason_patterns: tuple[str, ...] = ()
    required_visual_groups: tuple[str, ...] = ()
    minimum_visible_colors: int = 1
    minimum_palette_ratio: float = 0.001


TASKS = (
    TaskSpec(
        task_id="dev-explicit-xy-standard",
        split="development",
        prompt="""Hazme un gráfico XY de tickets resueltos por semana. Conserva el orden y la unidad `tickets`: Week 1 = 18, Week 2 = 27, Week 3 = 24, Week 4 = 36. Usa la paleta normal; no estoy pidiendo colores extended.""",
        family="xyChart",
        declarations=("xychart", "xychart-beta"),
        colorset="colorset1",
        required_terms=("Week 1", "Week 2", "Week 3", "Week 4", "18", "27", "24", "36", "tickets"),
        patterns=(r"(?:bar|line)\s*\[\s*18\s*,\s*27\s*,\s*24\s*,\s*36\s*\]",),
        ordered_terms=("Week 1", "Week 2", "Week 3", "Week 4"),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="dev-infer-weighted-flow-extended",
        split="development",
        prompt="""Make a visualization from these directed material transfers. Choose the Mermaid diagram yourself and keep every tonne exact. Use the extended/full-color palette. Mine -> Plant: 64; Recycled -> Plant: 21; Plant -> Product: 70; Plant -> Waste: 15; Waste -> Recovery: 9; Recovery -> Secondary product: 6.""",
        family="sankey",
        declarations=("sankey", "sankey-beta"),
        colorset="colorset2",
        required_terms=("Mine", "Plant", "Recycled", "Product", "Waste", "Recovery", "Secondary product", "tonne", "64", "21", "70", "15", "9", "6"),
        patterns=(
            r"Mine\s*,\s*Plant\s*,\s*64(?:\.0+)?\b",
            r"Recycled\s*,\s*Plant\s*,\s*21(?:\.0+)?\b",
            r"Plant\s*,\s*Product\s*,\s*70(?:\.0+)?\b",
            r"Plant\s*,\s*Waste\s*,\s*15(?:\.0+)?\b",
            r"Waste\s*,\s*Recovery\s*,\s*9(?:\.0+)?\b",
            r"Recovery\s*,\s*Secondary product\s*,\s*6(?:\.0+)?\b",
        ),
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="dev-infer-data-model-standard",
        split="development",
        prompt="""Choose and create the clearest Mermaid diagram for this stored data model. MEMBER has member_id PK and email. LOAN has loan_id PK, member_id FK, and borrowed_at. COPY has copy_id PK and isbn. A MEMBER may have zero or many LOAN records; every LOAN belongs to exactly one MEMBER. A COPY may appear in zero or many LOAN records; every LOAN references exactly one COPY. Use the standard palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset1",
        required_terms=("MEMBER", "LOAN", "COPY", "member_id", "loan_id", "copy_id", "borrowed_at", "isbn", "email", "PK", "FK"),
        patterns=(
            r"(?:MEMBER\s+\|\|\s*--\s*o\{\s+LOAN|LOAN\s+\}o\s*--\s*\|\|\s+MEMBER)",
            r"(?:COPY\s+\|\|\s*--\s*o\{\s+LOAN|LOAN\s+\}o\s*--\s*\|\|\s+COPY)",
        ),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="dev-infer-schedule-extended",
        split="development",
        prompt="""Visualize this launch plan in Mermaid, choosing the appropriate diagram. Discovery starts 2026-10-05, lasts 4d, and is done. Prototype starts after Discovery, lasts 6d, and is active. Validation starts after Prototype and lasts 3d as a normal pending task. Security review starts after Validation, lasts 2d, and is critical. Launch is a milestone on 2026-10-22. Preserve those statuses so the extended multicolor palette is visibly used.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset2",
        required_terms=("Discovery", "Prototype", "Validation", "Security review", "Launch", "2026-10-05", "4d", "6d", "3d", "2d", "2026-10-22", "done", "active", "crit", "milestone", "after"),
        patterns=(
            r"Discovery[^\n]*\bdone\b|\bdone\b[^\n]*Discovery",
            r"Prototype[^\n]*\bactive\b|\bactive\b[^\n]*Prototype",
            r"Security review[^\n]*\bcrit\b|\bcrit\b[^\n]*Security review",
            r"Prototype[^\n]*after\s+\w+[^\n]*6d",
            r"Validation[^\n]*after\s+\w+[^\n]*3d",
        ),
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.03,
    ),
    TaskSpec(
        task_id="dev-infer-two-axis-extended",
        split="development",
        prompt="""Crea la visualización Mermaid más apropiada para priorizar iniciativas. Eje x: Coste, de bajo a alto. Eje y: Valor, de bajo a alto. Preserve exactamente: Quick search (0.18, 0.84), Data export (0.72, 0.58), Audit trail (0.48, 0.76), Custom themes (0.30, 0.32). Usa explícitamente el color set extended.""",
        family="quadrantChart",
        declarations=("quadrantChart",),
        colorset="colorset2",
        required_terms=("Coste", "Valor", "Quick search", "Data export", "Audit trail", "Custom themes", "0.18", "0.84", "0.72", "0.58", "0.48", "0.76", "0.30", "0.32"),
        patterns=(
            r"Quick search[\"']?\s*:\s*\[\s*0\.18\s*,\s*0\.84\s*\]",
            r"Data export[\"']?\s*:\s*\[\s*0\.72\s*,\s*0\.58\s*\]",
            r"Audit trail[\"']?\s*:\s*\[\s*0\.48\s*,\s*0\.76\s*\]",
            r"Custom themes[\"']?\s*:\s*\[\s*0\.30\s*,\s*0\.32\s*\]",
        ),
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.15,
    ),
    TaskSpec(
        task_id="holdout-explicit-sequence-standard",
        split="holdout",
        prompt="""Generate a Mermaid sequence diagram and keep this exact message order and wording: Cliente sends `Enviar consulta` to API; API sends `Buscar resultado` to Caché; Caché returns `No encontrado` to API; API sends `Ejecutar consulta` to Base de datos; Base de datos returns `Filas` to API; API returns `Respuesta` to Cliente. Use the standard palette.""",
        family="sequenceDiagram",
        declarations=("sequenceDiagram",),
        colorset="colorset1",
        required_terms=("Cliente", "API", "Caché", "Base de datos", "Enviar consulta", "Buscar resultado", "No encontrado", "Ejecutar consulta", "Filas", "Respuesta"),
        ordered_terms=("Enviar consulta", "Buscar resultado", "No encontrado", "Ejecutar consulta", "Filas", "Respuesta"),
        minimum_arrow_count=6,
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="holdout-infer-parts-standard",
        split="holdout",
        prompt="""Hazme una visualización Mermaid con estos datos y elige el tipo que muestre más directamente partes de un mismo total de 100 GB: Documentos 52, Imágenes 28, Vídeo 15, Otros 5. Conserva literalmente las etiquetas y usa la paleta estándar.""",
        family="pie",
        declarations=("pie",),
        colorset="colorset1",
        required_terms=("Documentos", "Imágenes", "Vídeo", "Otros", "52", "28", "15", "5", "GB"),
        patterns=(
            r"[\"']?Documentos[\"']?\s*:\s*52(?:\.0+)?\b",
            r"[\"']?Imágenes[\"']?\s*:\s*28(?:\.0+)?\b",
            r"[\"']?Vídeo[\"']?\s*:\s*15(?:\.0+)?\b",
            r"[\"']?Otros[\"']?\s*:\s*5(?:\.0+)?\b",
        ),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="holdout-infer-concepts-standard",
        split="holdout",
        prompt="""Genera el diagrama Mermaid que mejor organice estos conceptos como una descomposición conceptual. Plataforma de datos contiene Ingesta, Procesamiento y Consumo. Ingesta contiene Lotes y Eventos. Procesamiento contiene Limpieza y Enriquecimiento. Consumo contiene Informes y Modelos. Conserva las etiquetas en español y usa la paleta estándar.""",
        family="mindmap",
        declarations=("mindmap",),
        colorset="colorset1",
        required_terms=("Plataforma de datos", "Ingesta", "Procesamiento", "Consumo", "Lotes", "Eventos", "Limpieza", "Enriquecimiento", "Informes", "Modelos"),
        minimum_indented_lines=8,
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="holdout-infer-release-plan-extended",
        split="holdout",
        prompt="""Hazme una visualización Mermaid de este plan, eligiendo el tipo apropiado. Investigación comienza 2027-01-11, dura 3d y está done. Diseño comienza después de Investigación, dura 5d y está active. Construcción comienza después de Diseño y dura 8d como tarea pendiente normal. Revisión final comienza después de Construcción, dura 2d y es critical. Puesta en producción es un milestone el 2027-02-05. Mantén literalmente los nombres y estados y usa los colores extended de forma visible.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset2",
        required_terms=("Investigación", "Diseño", "Construcción", "Revisión final", "Puesta en producción", "2027-01-11", "3d", "5d", "8d", "2d", "2027-02-05", "done", "active", "crit", "milestone", "after"),
        patterns=(
            r"Investigación[^\n]*\bdone\b|\bdone\b[^\n]*Investigación",
            r"Diseño[^\n]*\bactive\b|\bactive\b[^\n]*Diseño",
            r"Revisión final[^\n]*\bcrit\b|\bcrit\b[^\n]*Revisión final",
            r"Diseño[^\n]*after\s+\w+[^\n]*5d",
            r"Construcción[^\n]*after\s+\w+[^\n]*8d",
        ),
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.03,
    ),
    TaskSpec(
        task_id="holdout-infer-two-axis-extended",
        split="holdout",
        prompt="""Crea la visualización Mermaid más apropiada para priorizar experimentos. Eje x: Complejidad, de baja a alta. Eje y: Beneficio, de bajo a alto. Conserva exactamente: Inicio rápido (0.14, 0.79), Automatización (0.68, 0.91), Limpieza interna (0.42, 0.36), Cambio de proveedor (0.87, 0.55). Usa explícitamente el color set extended.""",
        family="quadrantChart",
        declarations=("quadrantChart",),
        colorset="colorset2",
        required_terms=("Complejidad", "Beneficio", "Inicio rápido", "Automatización", "Limpieza interna", "Cambio de proveedor", "0.14", "0.79", "0.68", "0.91", "0.42", "0.36", "0.87", "0.55"),
        patterns=(
            r"Inicio rápido[\"']?\s*:\s*\[\s*0\.14\s*,\s*0\.79\s*\]",
            r"Automatización[\"']?\s*:\s*\[\s*0\.68\s*,\s*0\.91\s*\]",
            r"Limpieza interna[\"']?\s*:\s*\[\s*0\.42\s*,\s*0\.36\s*\]",
            r"Cambio de proveedor[\"']?\s*:\s*\[\s*0\.87\s*,\s*0\.55\s*\]",
        ),
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.15,
    ),
)


PARETO_TASKS = (
    TaskSpec(
        task_id="pareto-dev-explicit-flowchart-standard",
        split="development",
        prompt="""Create a Mermaid flowchart for this exact approval path: Intake goes to Triage. Triage asks `Complete?`. `No` goes to `Request details`, then back to Triage. `Yes` goes to `Risk review`. Risk review asks `Approved?`. `No` goes to `Decline`; `Yes` goes to `Schedule`. Keep every label and direction exact. Use the standard palette.""",
        family="flowchart",
        declarations=("flowchart", "graph"),
        colorset="colorset1",
        required_terms=("Intake", "Triage", "Complete?", "No", "Request details", "Yes", "Risk review", "Approved?", "Decline", "Schedule"),
        minimum_arrow_count=8,
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="pareto-dev-infer-energy-flow-extended",
        split="development",
        prompt="""Make the clearest Mermaid visualization for these directed energy transfers and choose the diagram family yourself. Preserve every value exactly and make the literal unit `MWh` visible. Use the extended full-color palette. Solar -> Grid: 47 MWh; Wind -> Grid: 35 MWh; Grid -> Homes: 51 MWh; Grid -> Industry: 23 MWh; Grid -> Storage: 8 MWh; Storage -> Homes: 6 MWh.""",
        family="sankey",
        declarations=("sankey", "sankey-beta"),
        colorset="colorset2",
        required_terms=("Solar", "Grid", "Wind", "Homes", "Industry", "Storage", "MWh", "47", "35", "51", "23", "8", "6"),
        patterns=(
            r"Solar\s*,\s*Grid\s*,\s*47(?:\.0+)?\b",
            r"Wind\s*,\s*Grid\s*,\s*35(?:\.0+)?\b",
            r"Grid\s*,\s*Homes\s*,\s*51(?:\.0+)?\b",
            r"Grid\s*,\s*Industry\s*,\s*23(?:\.0+)?\b",
            r"Grid\s*,\s*Storage\s*,\s*8(?:\.0+)?\b",
            r"Storage\s*,\s*Homes\s*,\s*6(?:\.0+)?\b",
        ),
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="pareto-dev-infer-lifecycle-standard",
        split="development",
        prompt="""Choose the Mermaid diagram that best shows this lifecycle. Represent a new Request entering Draft as an initial transition labeled `Request`. `Submit` moves Draft to Review. `Return` moves Review back to Draft. `Accept` moves Review to Approved. `Publish` moves Approved to Live. `Retire` moves Live to Archived. Preserve the labels and directions exactly and use the standard palette.""",
        family="stateDiagram",
        declarations=("stateDiagram", "stateDiagram-v2"),
        colorset="colorset1",
        required_terms=("Request", "Draft", "Submit", "Review", "Return", "Accept", "Approved", "Publish", "Live", "Retire", "Archived"),
        ordered_terms=("Submit", "Return", "Accept", "Publish", "Retire"),
        minimum_arrow_count=6,
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="pareto-dev-infer-campaign-schedule-extended",
        split="development",
        prompt="""Visualize this campaign schedule in Mermaid and choose the appropriate family. Research starts 2027-03-01, lasts 3d, and is done. Creative starts after Research, lasts 5d, and is active. Production starts after Creative and lasts 7d as a normal pending task. Legal review starts after Production, lasts 2d, and is critical. Release is a milestone on 2027-03-22. Preserve the names, dependencies, dates, durations, and statuses. Use extended colors visibly.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset2",
        required_terms=("Research", "Creative", "Production", "Legal review", "Release", "2027-03-01", "3d", "5d", "7d", "2d", "2027-03-22", "done", "active", "crit", "milestone", "after"),
        patterns=(
            r"Research[^\n]*\bdone\b|\bdone\b[^\n]*Research",
            r"Creative[^\n]*\bactive\b|\bactive\b[^\n]*Creative",
            r"Legal review[^\n]*\bcrit\b|\bcrit\b[^\n]*Legal review",
            r"Creative[^\n]*after\s+\w+[^\n]*5d",
            r"Production[^\n]*after\s+\w+[^\n]*7d",
        ),
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.03,
    ),
    TaskSpec(
        task_id="pareto-holdout-explicit-sequence-standard",
        split="holdout",
        prompt="""Generate a Mermaid sequence diagram and preserve this exact message order and wording: Operator sends `Start import` to Portal; Portal sends `Queue batch` to Worker; Worker sends `Read records` to Archive; Archive returns `Records` to Worker; Worker returns `Import complete` to Portal; Portal returns `Summary` to Operator. Use the standard palette.""",
        family="sequenceDiagram",
        declarations=("sequenceDiagram",),
        colorset="colorset1",
        required_terms=("Operator", "Portal", "Worker", "Archive", "Start import", "Queue batch", "Read records", "Records", "Import complete", "Summary"),
        ordered_terms=("Start import", "Queue batch", "Read records", "Records", "Import complete", "Summary"),
        minimum_arrow_count=6,
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="pareto-holdout-infer-library-model-standard",
        split="holdout",
        prompt="""Choose and create the clearest Mermaid diagram for this stored data model. AUTHOR has author_id PK and name. BOOK has book_id PK, author_id FK, and title. EDITION has edition_id PK, book_id FK, and published_on. An AUTHOR may write zero or many BOOK records; every BOOK has exactly one AUTHOR. A BOOK may have zero or many EDITION records; every EDITION belongs to exactly one BOOK. Use the standard palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset1",
        required_terms=("AUTHOR", "BOOK", "EDITION", "author_id", "book_id", "edition_id", "name", "title", "published_on", "PK", "FK"),
        patterns=(
            r"(?:AUTHOR\s+\|\|\s*--\s*o\{\s+BOOK|BOOK\s+\}o\s*--\s*\|\|\s+AUTHOR)",
            r"(?:BOOK\s+\|\|\s*--\s*o\{\s+EDITION|EDITION\s+\}o\s*--\s*\|\|\s+BOOK)",
        ),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="pareto-holdout-infer-portfolio-extended",
        split="holdout",
        prompt="""Create the most appropriate Mermaid visualization for prioritizing this portfolio. x-axis: Effort, low to high. y-axis: Impact, low to high. Preserve exactly: Search refresh (0.22, 0.81), Billing migration (0.76, 0.69), Log cleanup (0.38, 0.27), Partner API (0.61, 0.88). Use the extended color set explicitly.""",
        family="quadrantChart",
        declarations=("quadrantChart",),
        colorset="colorset2",
        required_terms=("Effort", "Impact", "Search refresh", "Billing migration", "Log cleanup", "Partner API", "0.22", "0.81", "0.76", "0.69", "0.38", "0.27", "0.61", "0.88"),
        patterns=(
            r"Search refresh[\"']?\s*:\s*\[\s*0\.22\s*,\s*0\.81\s*\]",
            r"Billing migration[\"']?\s*:\s*\[\s*0\.76\s*,\s*0\.69\s*\]",
            r"Log cleanup[\"']?\s*:\s*\[\s*0\.38\s*,\s*0\.27\s*\]",
            r"Partner API[\"']?\s*:\s*\[\s*0\.61\s*,\s*0\.88\s*\]",
        ),
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.15,
    ),
    TaskSpec(
        task_id="pareto-holdout-infer-capability-map-standard",
        split="holdout",
        prompt="""Generate the Mermaid diagram that best organizes this conceptual decomposition. Operations contains Planning, Delivery, and Assurance. Planning contains Forecasting and Staffing. Delivery contains Fulfillment and Support. Assurance contains Audit and Reliability. Preserve every label and use the standard palette.""",
        family="mindmap",
        declarations=("mindmap",),
        colorset="colorset1",
        required_terms=("Operations", "Planning", "Delivery", "Assurance", "Forecasting", "Staffing", "Fulfillment", "Support", "Audit", "Reliability"),
        minimum_indented_lines=8,
        required_visual_groups=("primary",),
    ),
)


PARETO_V2_TASKS = (
    TaskSpec(
        task_id="evolve-dev-library-model-standard",
        split="development",
        prompt="""Choose and create the clearest Mermaid diagram for this stored data model. AUTHOR has author_id PK and name. BOOK has book_id PK, author_id FK, and title. EDITION has edition_id PK, book_id FK, and published_on. An AUTHOR may write zero or many BOOK records; every BOOK has exactly one AUTHOR. A BOOK may have zero or many EDITION records; every EDITION belongs to exactly one BOOK. Use the standard palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset1",
        required_terms=("AUTHOR", "BOOK", "EDITION", "author_id", "book_id", "edition_id", "name", "title", "published_on", "PK", "FK"),
        patterns=(
            r"(?:AUTHOR\s+\|\|\s*--\s*o\{\s+BOOK|BOOK\s+\}o\s*--\s*\|\|\s+AUTHOR)",
            r"(?:BOOK\s+\|\|\s*--\s*o\{\s+EDITION|EDITION\s+\}o\s*--\s*\|\|\s+BOOK)",
        ),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="evolve-dev-service-release-model-standard",
        split="development",
        prompt="""Create the most truthful Mermaid visualization for this stored schema. SERVICE has service_id PK and name. RELEASE has release_id PK, service_id FK, and version. DEPLOYMENT has deployment_id PK, release_id FK, and environment. A SERVICE may have zero or many RELEASE records; every RELEASE belongs to exactly one SERVICE. A RELEASE may have zero or many DEPLOYMENT records; every DEPLOYMENT belongs to exactly one RELEASE. Use the standard palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset1",
        required_terms=("SERVICE", "RELEASE", "DEPLOYMENT", "service_id", "release_id", "deployment_id", "name", "version", "environment", "PK", "FK"),
        patterns=(
            r"(?:SERVICE\s+\|\|\s*--\s*o\{\s+RELEASE|RELEASE\s+\}o\s*--\s*\|\|\s+SERVICE)",
            r"(?:RELEASE\s+\|\|\s*--\s*o\{\s+DEPLOYMENT|DEPLOYMENT\s+\}o\s*--\s*\|\|\s+RELEASE)",
        ),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="evolve-dev-explicit-reversed-er-standard",
        split="development",
        prompt="""Create a Mermaid ER diagram for this stored relation and place JOB_RUN on the left and PIPELINE on the right in the relationship line. PIPELINE has pipeline_id PK and name. JOB_RUN has run_id PK, pipeline_id FK, and started_at. A PIPELINE may have zero or many JOB_RUN records; every JOB_RUN belongs to exactly one PIPELINE. Preserve the child-to-parent orientation, attributes, keys, and cardinalities. Use the standard palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset1",
        required_terms=("JOB_RUN", "PIPELINE", "pipeline_id", "run_id", "name", "started_at", "PK", "FK"),
        patterns=(r"JOB_RUN\s+\}o\s*--\s*\|\|\s+PIPELINE",),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="evolve-dev-explicit-flowchart-standard",
        split="development",
        prompt="""Create a Mermaid flowchart for this exact support route: `Ticket received` goes to `Classify`. Classify asks `Urgent?`. `Yes` goes to `Page on-call`, then `Resolve`. `No` goes to `Assign queue`, then `Resolve`. Resolve goes to `Close ticket`. Preserve every label and direction and use the standard palette.""",
        family="flowchart",
        declarations=("flowchart", "graph"),
        colorset="colorset1",
        required_terms=("Ticket received", "Classify", "Urgent?", "Yes", "Page on-call", "No", "Assign queue", "Resolve", "Close ticket"),
        minimum_arrow_count=6,
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="evolve-dev-infer-water-flow-extended",
        split="development",
        prompt="""Choose the best Mermaid visualization for these directed water transfers. Preserve every value and make the literal unit `litres` visible. Reservoir -> Treatment: 88 litres; Rain capture -> Treatment: 17 litres; Treatment -> Homes: 61 litres; Treatment -> Farms: 29 litres; Treatment -> Storage: 15 litres; Storage -> Homes: 11 litres. Use the extended full-color palette.""",
        family="sankey",
        declarations=("sankey", "sankey-beta"),
        colorset="colorset2",
        required_terms=("Reservoir", "Treatment", "Rain capture", "Homes", "Farms", "Storage", "litres", "88", "17", "61", "29", "15", "11"),
        patterns=(
            r"Reservoir\s*,\s*Treatment\s*,\s*88(?:\.0+)?\b",
            r"Rain capture\s*,\s*Treatment\s*,\s*17(?:\.0+)?\b",
            r"Treatment\s*,\s*Homes\s*,\s*61(?:\.0+)?\b",
            r"Treatment\s*,\s*Farms\s*,\s*29(?:\.0+)?\b",
            r"Treatment\s*,\s*Storage\s*,\s*15(?:\.0+)?\b",
            r"Storage\s*,\s*Homes\s*,\s*11(?:\.0+)?\b",
        ),
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="evolve-dev-infer-state-standard",
        split="development",
        prompt="""Choose the Mermaid diagram that best represents these valid status transitions. A new Case enters Open through `Create`. `Investigate` moves Open to Checking. `Need info` moves Checking to Waiting. `Reply` moves Waiting back to Checking. `Confirm` moves Checking to Resolved. `Reopen` moves Resolved to Open. Preserve every label and direction and use the standard palette.""",
        family="stateDiagram",
        declarations=("stateDiagram", "stateDiagram-v2"),
        colorset="colorset1",
        required_terms=("Open", "Create", "Investigate", "Checking", "Need info", "Waiting", "Reply", "Confirm", "Resolved", "Reopen"),
        ordered_terms=("Create", "Investigate", "Need info", "Reply", "Confirm", "Reopen"),
        minimum_arrow_count=6,
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="evolve-holdout-warehouse-model-standard",
        split="holdout",
        prompt="""Choose and create the clearest Mermaid diagram for this stored model. WAREHOUSE has warehouse_id PK and city. BIN has bin_id PK, warehouse_id FK, and code. ITEM has item_id PK, bin_id FK, and sku. A WAREHOUSE may contain zero or many BIN records; every BIN belongs to exactly one WAREHOUSE. A BIN may hold zero or many ITEM records; every ITEM belongs to exactly one BIN. Use the standard palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset1",
        required_terms=("WAREHOUSE", "BIN", "ITEM", "warehouse_id", "bin_id", "item_id", "city", "code", "sku", "PK", "FK"),
        patterns=(
            r"(?:WAREHOUSE\s+\|\|\s*--\s*o\{\s+BIN|BIN\s+\}o\s*--\s*\|\|\s+WAREHOUSE)",
            r"(?:BIN\s+\|\|\s*--\s*o\{\s+ITEM|ITEM\s+\}o\s*--\s*\|\|\s+BIN)",
        ),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="evolve-holdout-enrollment-model-standard",
        split="holdout",
        prompt="""Create the Mermaid visualization that best preserves this enrollment schema. STUDENT has student_id PK and email. COURSE has course_id PK and title. ENROLLMENT has student_id PK, FK; course_id PK, FK; and enrolled_on. A STUDENT may have zero or many ENROLLMENT records, while every ENROLLMENT references exactly one STUDENT. A COURSE may have zero or many ENROLLMENT records, while every ENROLLMENT references exactly one COURSE. Use the standard palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset1",
        required_terms=("STUDENT", "COURSE", "ENROLLMENT", "student_id", "course_id", "email", "title", "enrolled_on", "PK", "FK"),
        patterns=(
            r"(?:STUDENT\s+\|\|\s*--\s*o\{\s+ENROLLMENT|ENROLLMENT\s+\}o\s*--\s*\|\|\s+STUDENT)",
            r"(?:COURSE\s+\|\|\s*--\s*o\{\s+ENROLLMENT|ENROLLMENT\s+\}o\s*--\s*\|\|\s+COURSE)",
        ),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="evolve-holdout-supply-flow-extended",
        split="holdout",
        prompt="""Make the most direct Mermaid visualization for these directed supply weights. Preserve every value and show the literal unit `kg`. Supplier A -> Hub: 73 kg; Supplier B -> Hub: 26 kg; Hub -> Retail: 58 kg; Hub -> Online: 31 kg; Hub -> Returns: 10 kg; Returns -> Refurbished: 7 kg. Use the extended multicolor palette.""",
        family="sankey",
        declarations=("sankey", "sankey-beta"),
        colorset="colorset2",
        required_terms=("Supplier A", "Supplier B", "Hub", "Retail", "Online", "Returns", "Refurbished", "kg", "73", "26", "58", "31", "10", "7"),
        patterns=(
            r"Supplier A\s*,\s*Hub\s*,\s*73(?:\.0+)?\b",
            r"Supplier B\s*,\s*Hub\s*,\s*26(?:\.0+)?\b",
            r"Hub\s*,\s*Retail\s*,\s*58(?:\.0+)?\b",
            r"Hub\s*,\s*Online\s*,\s*31(?:\.0+)?\b",
            r"Hub\s*,\s*Returns\s*,\s*10(?:\.0+)?\b",
            r"Returns\s*,\s*Refurbished\s*,\s*7(?:\.0+)?\b",
        ),
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="evolve-holdout-explicit-sequence-standard",
        split="holdout",
        prompt="""Generate a Mermaid sequence diagram and keep this exact message order and wording: Analyst sends `Open report` to Console; Console sends `Fetch metrics` to Service; Service sends `Query store` to Database; Database returns `Metric rows` to Service; Service returns `Metrics` to Console; Console returns `Rendered report` to Analyst. Use the standard palette.""",
        family="sequenceDiagram",
        declarations=("sequenceDiagram",),
        colorset="colorset1",
        required_terms=("Analyst", "Console", "Service", "Database", "Open report", "Fetch metrics", "Query store", "Metric rows", "Metrics", "Rendered report"),
        ordered_terms=("Open report", "Fetch metrics", "Query store", "Metric rows", "Metrics", "Rendered report"),
        minimum_arrow_count=6,
        required_visual_groups=("primary",),
    ),
)


PARETO_FINAL_HOLDOUT_TASKS = (
    TaskSpec(
        task_id="final-holdout-explicit-reversed-er-standard",
        split="holdout",
        prompt="""Create a Mermaid ER diagram for this stored relation and place SESSION on the left and USER_ACCOUNT on the right in the relationship line. USER_ACCOUNT has account_id PK and email. SESSION has session_id PK, account_id FK, and started_at. A USER_ACCOUNT may have zero or many SESSION records; every SESSION belongs to exactly one USER_ACCOUNT. Preserve the child-to-parent orientation, attributes, keys, and cardinalities. Use the standard palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset1",
        required_terms=("SESSION", "USER_ACCOUNT", "account_id", "session_id", "email", "started_at", "PK", "FK"),
        patterns=(r"SESSION\s+\}o\s*--\s*\|\|\s+USER_ACCOUNT",),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="final-holdout-infer-throughput-standard",
        split="holdout",
        prompt="""Hazme una visualización Mermaid con estos datos, eligiendo el tipo que compare más directamente el volumen diario. Conserva el orden y la unidad literal `solicitudes`: Lunes 14, Martes 21, Miércoles 18, Jueves 27, Viernes 24. Usa la paleta estándar.""",
        family="xyChart",
        declarations=("xychart", "xychart-beta"),
        colorset="colorset1",
        required_terms=("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "14", "21", "18", "27", "24", "solicitudes"),
        patterns=(r"(?:bar|line)\s*\[\s*14\s*,\s*21\s*,\s*18\s*,\s*27\s*,\s*24\s*\]",),
        ordered_terms=("Lunes", "Martes", "Miércoles", "Jueves", "Viernes"),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="final-holdout-infer-service-concepts-standard",
        split="holdout",
        prompt="""Generate the Mermaid diagram that best organizes this conceptual decomposition. Customer service contains Intake, Resolution, and Learning. Intake contains Email and Chat. Resolution contains Investigation and Response. Learning contains Review and Improvement. Preserve every label and use the standard palette.""",
        family="mindmap",
        declarations=("mindmap",),
        colorset="colorset1",
        required_terms=("Customer service", "Intake", "Resolution", "Learning", "Email", "Chat", "Investigation", "Response", "Review", "Improvement"),
        minimum_indented_lines=8,
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="final-holdout-infer-priority-extended",
        split="holdout",
        prompt="""Crea la visualización Mermaid más apropiada para priorizar iniciativas. Eje x: Urgencia, de baja a alta. Eje y: Impacto, de bajo a alto. Conserva exactamente: Renovar ayuda (0.20, 0.42), Reparar pagos (0.88, 0.94), Mejorar búsqueda (0.55, 0.81), Archivar registros (0.31, 0.24). Usa explícitamente el color set extended.""",
        family="quadrantChart",
        declarations=("quadrantChart",),
        colorset="colorset2",
        required_terms=("Urgencia", "Impacto", "Renovar ayuda", "Reparar pagos", "Mejorar búsqueda", "Archivar registros", "0.20", "0.42", "0.88", "0.94", "0.55", "0.81", "0.31", "0.24"),
        patterns=(
            r"Renovar ayuda[\"']?\s*:\s*\[\s*0\.20\s*,\s*0\.42\s*\]",
            r"Reparar pagos[\"']?\s*:\s*\[\s*0\.88\s*,\s*0\.94\s*\]",
            r"Mejorar búsqueda[\"']?\s*:\s*\[\s*0\.55\s*,\s*0\.81\s*\]",
            r"Archivar registros[\"']?\s*:\s*\[\s*0\.31\s*,\s*0\.24\s*\]",
        ),
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.15,
    ),
)


PARETO_SEALED_HOLDOUT_TASKS = (
    TaskSpec(
        task_id="sealed-holdout-explicit-reversed-er-standard",
        split="holdout",
        prompt="""Create a Mermaid ER diagram for this stored relation and place API_KEY on the left and APPLICATION on the right in the relationship line. APPLICATION has application_id PK and name. API_KEY has key_id PK, application_id FK, and issued_at. An APPLICATION may have zero or many API_KEY records; every API_KEY belongs to exactly one APPLICATION. Preserve the child-to-parent orientation, attributes, keys, and cardinalities. Use the standard palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset1",
        required_terms=("API_KEY", "APPLICATION", "application_id", "key_id", "name", "issued_at", "PK", "FK"),
        patterns=(r"API_KEY\s+\}o\s*--\s*\|\|\s+APPLICATION",),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="sealed-holdout-infer-storage-parts-standard",
        split="holdout",
        prompt="""Hazme una visualización Mermaid con estos datos y elige el tipo que muestre más directamente partes de un mismo total de 200 GB: Proyectos 92, Fotografías 54, Vídeos 38, Copias 16. Conserva literalmente las etiquetas, valores y la unidad `GB`. Usa la paleta estándar.""",
        family="pie",
        declarations=("pie",),
        colorset="colorset1",
        required_terms=("Proyectos", "Fotografías", "Vídeos", "Copias", "92", "54", "38", "16", "GB"),
        patterns=(
            r"[\"']?Proyectos[\"']?\s*:\s*92(?:\.0+)?\b",
            r"[\"']?Fotografías[\"']?\s*:\s*54(?:\.0+)?\b",
            r"[\"']?Vídeos[\"']?\s*:\s*38(?:\.0+)?\b",
            r"[\"']?Copias[\"']?\s*:\s*16(?:\.0+)?\b",
        ),
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="sealed-holdout-infer-product-concepts-standard",
        split="holdout",
        prompt="""Generate the Mermaid diagram that best organizes this conceptual decomposition. Product delivery contains Discovery, Build, and Operate. Discovery contains Interviews and Experiments. Build contains Design and Engineering. Operate contains Support and Observability. Preserve every label and use the standard palette.""",
        family="mindmap",
        declarations=("mindmap",),
        colorset="colorset1",
        required_terms=("Product delivery", "Discovery", "Build", "Operate", "Interviews", "Experiments", "Design", "Engineering", "Support", "Observability"),
        minimum_indented_lines=8,
        required_visual_groups=("primary",),
    ),
    TaskSpec(
        task_id="sealed-holdout-infer-release-schedule-extended",
        split="holdout",
        prompt="""Visualize this release schedule in Mermaid and choose the appropriate family. Scoping starts 2027-09-06, lasts 4d, and is done. Implementation starts after Scoping, lasts 8d, and is active. Verification starts after Implementation and lasts 3d as a normal pending task. Compliance review starts after Verification, lasts 2d, and is critical. Rollout is a milestone on 2027-10-01. Preserve the names, dependencies, dates, durations, and statuses. Use the extended full-color palette visibly.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset2",
        required_terms=("Scoping", "Implementation", "Verification", "Compliance review", "Rollout", "2027-09-06", "4d", "8d", "3d", "2d", "2027-10-01", "done", "active", "crit", "milestone", "after"),
        patterns=(
            r"Scoping[^\n]*\bdone\b|\bdone\b[^\n]*Scoping",
            r"Implementation[^\n]*\bactive\b|\bactive\b[^\n]*Implementation",
            r"Compliance review[^\n]*\bcrit\b|\bcrit\b[^\n]*Compliance review",
            r"Implementation[^\n]*after\s+\w+[^\n]*8d",
            r"Verification[^\n]*after\s+\w+[^\n]*3d",
        ),
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.03,
    ),
)


HARD_DEVELOPMENT_TASKS = (
    TaskSpec(
        task_id="hard-dev-conflicting-pie-request-standard",
        split="development",
        prompt="""Hazme un gráfico circular Mermaid con la variación interanual por región: Norte = +18.5%, Centro = -6.0%, Sur = +11.25%, Oeste = 0%. Conserva el orden, los signos, los decimales, las etiquetas y la unidad porcentual. Usa una presentación colorida, pero no estoy pidiendo el color set extended. Si el tipo solicitado distorsiona estos datos, elige una alternativa veraz y explica el conflicto.""",
        family="xyChart",
        declarations=("xychart", "xychart-beta"),
        colorset="colorset1",
        required_terms=("Norte", "Centro", "Sur", "Oeste", "18.5", "-6.0", "11.25", "0", "%"),
        patterns=(
            r"x-axis\s*\[\s*[\"']?Norte[\"']?\s*,\s*[\"']?Centro[\"']?\s*,\s*[\"']?Sur[\"']?\s*,\s*[\"']?Oeste[\"']?\s*\]",
            r"(?:bar|line)\s*\[\s*\+?18\.5\s*,\s*-6(?:\.0+)?\s*,\s*\+?11\.25\s*,\s*0(?:\.0+)?\s*\]",
        ),
        forbidden_patterns=(r"^\s*pie\b",),
        ordered_terms=("Norte", "Centro", "Sur", "Oeste"),
        visible_terms=("Norte", "Centro", "Sur", "Oeste"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=5.0,
        reason_patterns=(r"negativ|signo|signed|-\s*6(?:\.0+)?%|no (?:son|es) partes?",),
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-dev-infer-dated-events-standard",
        split="development",
        prompt="""Crea la visualización Mermaid más apropiada para estos hitos históricos sin duración: 2027-01-12 — Contrato firmado; 2027-03-04 — Piloto iniciado; 2027-06-18 — Auditoría aprobada; 2027-09-02 — Lanzamiento público. Conserva las fechas, el orden y cada etiqueta. No conviertas los hitos en tareas ni inventes duraciones. Usa la paleta estándar.""",
        family="timeline",
        declarations=("timeline",),
        colorset="colorset1",
        required_terms=("2027-01-12", "Contrato firmado", "2027-03-04", "Piloto iniciado", "2027-06-18", "Auditoría aprobada", "2027-09-02", "Lanzamiento público"),
        patterns=(
            r"2027-01-12\s*:\s*Contrato firmado",
            r"2027-03-04\s*:\s*Piloto iniciado",
            r"2027-06-18\s*:\s*Auditoría aprobada",
            r"2027-09-02\s*:\s*Lanzamiento público",
        ),
        ordered_terms=("2027-01-12", "2027-03-04", "2027-06-18", "2027-09-02"),
        visible_terms=("2027-01-12", "Contrato firmado", "2027-09-02", "Lanzamiento público"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-dev-infer-quantitative-hierarchy-extended",
        split="development",
        prompt="""Choose and create the Mermaid visualization that best shows this quantitative hierarchy, where area must encode annual recurring revenue in USD millions. Cloud revenue contains Americas and EMEA. Americas contains Enterprise = 48 and SMB = 22. EMEA contains Enterprise = 31 and SMB = 14. Preserve the hierarchy, every label, every value, and the unit `USD millions`. Use the extended full-color palette visibly.""",
        family="treemap",
        declarations=("treemap-beta", "treemap"),
        colorset="colorset2",
        required_terms=("Cloud revenue", "Americas", "EMEA", "Enterprise", "SMB", "48", "22", "31", "14", "USD millions"),
        patterns=(
            r"[\"']Enterprise[\"']\s*:\s*48(?:\.0+)?\b",
            r"[\"']SMB[\"']\s*:\s*22(?:\.0+)?\b",
            r"[\"']Enterprise[\"']\s*:\s*31(?:\.0+)?\b",
            r"[\"']SMB[\"']\s*:\s*14(?:\.0+)?\b",
        ),
        minimum_indented_lines=6,
        visible_terms=("Cloud revenue", "Americas", "EMEA", "Enterprise", "SMB"),
        minimum_rendered_text_items=7,
        maximum_aspect_ratio=4.0,
        required_visual_groups=("accent", "warning"),
        minimum_visible_colors=2,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-dev-infer-type-structure-standard",
        split="development",
        prompt="""Generate the Mermaid diagram that most directly communicates this software type structure, not a stored-record schema. Account exposes `account_id: UUID`, `balance: decimal`, and `credit(amount: decimal)`. SavingsAccount adds `rate: decimal` and inherits Account. Entry has `posted_at: datetime` and `amount: decimal`. One Account composes zero or more Entry objects. Preserve the type names, members, method signature, inheritance, composition, and multiplicities. Use the standard palette.""",
        family="classDiagram",
        declarations=("classDiagram", "classDiagram-v2"),
        colorset="colorset1",
        required_terms=("Account", "SavingsAccount", "Entry", "account_id", "UUID", "balance", "decimal", "credit", "amount", "rate", "posted_at", "datetime", "0..*", "1"),
        patterns=(
            r"(?:SavingsAccount\s+--\|>\s+Account|Account\s+<\|--\s+SavingsAccount)",
            r"(?:Account[^\n]*\*--[^\n]*Entry|Entry[^\n]*--\*[^\n]*Account)",
            r"credit\s*\(\s*amount\s*:\s*decimal\s*\)",
        ),
        visible_terms=("Account", "SavingsAccount", "Entry", "account_id", "credit", "posted_at"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-dev-infer-quoted-sankey-extended",
        split="development",
        prompt="""Make the Mermaid visualization that best shows these weighted directed transfers. Preserve labels containing commas exactly and keep every value and the unit `tonnes`: `North, inbound` -> `Refinery, east` = 51.5; `South inlet` -> `Refinery, east` = 18.25; `Refinery, east` -> `Finished fuel` = 62.75; `Refinery, east` -> `Process losses` = 7.0. Use the extended/full-color palette visibly.""",
        family="sankey",
        declarations=("sankey", "sankey-beta"),
        colorset="colorset2",
        required_terms=("North, inbound", "South inlet", "Refinery, east", "Finished fuel", "Process losses", "51.5", "18.25", "62.75", "7.0", "tonnes"),
        patterns=(
            r'"North, inbound"\s*,\s*"Refinery, east"\s*,\s*51\.5(?:0+)?\b',
            r'"South inlet"\s*,\s*"Refinery, east"\s*,\s*18\.25(?:0+)?\b',
            r'"Refinery, east"\s*,\s*"Finished fuel"\s*,\s*62\.75(?:0+)?\b',
            r'"Refinery, east"\s*,\s*"Process losses"\s*,\s*7(?:\.0+)?\b',
        ),
        visible_terms=("North, inbound", "South inlet", "Refinery, east", "Finished fuel", "Process losses"),
        minimum_rendered_text_items=5,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-dev-infer-multipredecessor-gantt-extended",
        split="development",
        prompt="""Visualize this delivery schedule in Mermaid. Use stable IDs `architecture`, `api`, `ui`, `integration`, and `rollout`. Architecture starts 2028-02-01, lasts 4d, and is done. API starts after Architecture, lasts 8d, and is active. UI starts after Architecture, lasts 6d, and is done. Integration depends on both API and UI, lasts 3d, and is critical; schedule it after the prerequisite that finishes last while keeping both dependencies visible in its human label. Rollout is a milestone on 2028-02-20. Preserve every date, duration, status, dependency, ID, and label. Use the extended full-color palette visibly.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset2",
        required_terms=("Architecture", "API", "UI", "Integration", "Rollout", "architecture", "api", "ui", "integration", "rollout", "2028-02-01", "4d", "8d", "6d", "3d", "2028-02-20", "done", "active", "crit", "milestone"),
        patterns=(
            r"Architecture[^\n]*\bdone\b[^\n]*\barchitecture\b[^\n]*2028-02-01[^\n]*4d",
            r"API[^\n]*\bactive\b[^\n]*\bapi\b[^\n]*after\s+architecture[^\n]*8d",
            r"UI[^\n]*\bdone\b[^\n]*\bui\b[^\n]*after\s+architecture[^\n]*6d",
            r"Integration \(after API and UI\)[^\n]*\bcrit\b[^\n]*\bintegration\b[^\n]*after\s+api[^\n]*3d",
            r"Rollout[^\n]*\bmilestone\b[^\n]*\brollout\b[^\n]*2028-02-20",
        ),
        forbidden_patterns=(
            r"Integration \(after API and UI\)\s*:[^\n]*\bafter\s+\w+[^\n]*\bafter\s+\w+",
        ),
        visible_terms=("Architecture", "API", "UI", "Integration (after API and UI)", "Rollout"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.03,
    ),
    TaskSpec(
        task_id="hard-dev-explicit-single-series-xy-extended",
        split="development",
        prompt="""Create an explicit Mermaid XY bar chart for quarterly operating margin. Keep the categories as category labels only and preserve their order and every signed decimal: Q1 = 12.5%, Q2 = -3.25%, Q3 = 21.75%, Q4 = 30.0%. Use one bar series, a truthful y-axis range, and the visible unit `percent`. Use the extended full-color palette visibly.""",
        family="xyChart",
        declarations=("xychart", "xychart-beta"),
        colorset="colorset2",
        required_terms=("Q1", "Q2", "Q3", "Q4", "12.5", "-3.25", "21.75", "30.0", "percent"),
        patterns=(
            r"x-axis\s*\[\s*[\"']?Q1[\"']?\s*,\s*[\"']?Q2[\"']?\s*,\s*[\"']?Q3[\"']?\s*,\s*[\"']?Q4[\"']?\s*\]",
            r"bar\s*\[\s*12\.5\s*,\s*-3\.25\s*,\s*21\.75\s*,\s*30\.0+\s*\]",
        ),
        forbidden_patterns=(r"^\s*(?:line|pie)\b",),
        ordered_terms=("Q1", "Q2", "Q3", "Q4"),
        visible_terms=("Q1", "Q2", "Q3", "Q4"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=5.0,
        required_visual_groups=("accent",),
        minimum_visible_colors=1,
        minimum_palette_ratio=0.05,
    ),
)


HARD_VISIBILITY_DEVELOPMENT_TASKS = HARD_DEVELOPMENT_TASKS + (
    TaskSpec(
        task_id="hard-dev-small-branch-treemap-standard",
        split="development",
        prompt="""Choose the Mermaid visualization where rectangle area best communicates this quantitative hierarchy. Program budget contains People, Platform, and Operations. People contains Engineering = 46 and Design = 14. Platform contains Compute = 20 and Data = 12. Operations contains Support = 8. Preserve hierarchy, labels, values, and the unit `budget points`. Use the standard palette, not extended. Every named branch and leaf must remain readable in the rendered diagram, including the smallest branch.""",
        family="treemap",
        declarations=("treemap-beta", "treemap"),
        colorset="colorset1",
        required_terms=("Program budget", "People", "Platform", "Operations", "Engineering", "Design", "Compute", "Data", "Support", "46", "14", "20", "12", "8", "budget points"),
        patterns=(
            r"[\"']Engineering[\"']\s*:\s*46(?:\.0+)?\b",
            r"[\"']Design[\"']\s*:\s*14(?:\.0+)?\b",
            r"[\"']Compute[\"']\s*:\s*20(?:\.0+)?\b",
            r"[\"']Data[\"']\s*:\s*12(?:\.0+)?\b",
            r"[\"']Support[\"']\s*:\s*8(?:\.0+)?\b",
        ),
        minimum_indented_lines=8,
        visible_terms=("Program budget", "People", "Platform", "Operations", "Engineering", "Design", "Compute", "Data", "Support"),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=4.0,
        required_visual_groups=("primary",),
        minimum_visible_colors=1,
        minimum_palette_ratio=0.01,
    ),
)


HARD_SEALED_HOLDOUT_TASKS = (
    TaskSpec(
        task_id="hard-sealed-infer-dated-events-extended",
        split="holdout",
        prompt="""Choose the Mermaid family that most directly shows these dated events, which have no task durations: 2030-02-14 — Prototype frozen; 2030-05-09 — Safety review passed; 2030-08-21 — Factory handoff; 2030-11-30 — First shipment. Preserve every date, label, and chronological order without inventing tasks or durations. Use the extended full-color palette visibly.""",
        family="timeline",
        declarations=("timeline",),
        colorset="colorset2",
        required_terms=("2030-02-14", "Prototype frozen", "2030-05-09", "Safety review passed", "2030-08-21", "Factory handoff", "2030-11-30", "First shipment"),
        patterns=(
            r"2030-02-14\s*:\s*Prototype frozen",
            r"2030-05-09\s*:\s*Safety review passed",
            r"2030-08-21\s*:\s*Factory handoff",
            r"2030-11-30\s*:\s*First shipment",
        ),
        ordered_terms=("2030-02-14", "2030-05-09", "2030-08-21", "2030-11-30"),
        visible_terms=("2030-02-14", "Prototype frozen", "2030-11-30", "First shipment"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-sealed-infer-capacity-treemap-standard",
        split="holdout",
        prompt="""Create the Mermaid visualization that best compares this quantitative hierarchy by area. Capacity plan contains Compute, Storage, and Network. Compute contains GPU = 44 and CPU = 26. Storage contains Object = 18 and Block = 8. Network contains Egress = 4. Preserve the hierarchy, every value, and the unit `capacity points`. Use the standard palette; extended colors are not requested.""",
        family="treemap",
        declarations=("treemap-beta", "treemap"),
        colorset="colorset1",
        required_terms=("Capacity plan", "Compute", "Storage", "Network", "GPU", "CPU", "Object", "Block", "Egress", "44", "26", "18", "8", "4", "capacity points"),
        patterns=(
            r"[\"']GPU[\"']\s*:\s*44(?:\.0+)?\b",
            r"[\"']CPU[\"']\s*:\s*26(?:\.0+)?\b",
            r"[\"']Object[\"']\s*:\s*18(?:\.0+)?\b",
            r"[\"']Block[\"']\s*:\s*8(?:\.0+)?\b",
            r"[\"']Egress[\"']\s*:\s*4(?:\.0+)?\b",
        ),
        minimum_indented_lines=8,
        visible_terms=("Capacity plan", "Compute", "Storage", "Network", "GPU", "CPU", "Object", "Block", "Egress"),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=4.0,
        required_visual_groups=("primary",),
        minimum_visible_colors=1,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-infer-labeled-state-standard",
        split="holdout",
        prompt="""Choose the Mermaid family that best shows these lifecycle transitions. Use stable IDs `NewRequest`, `InReview`, `WaitingCustomer`, and `Resolved` while displaying the exact labels `New request`, `In review`, `Waiting: customer`, and `Resolved`. New request moves to In review; In review moves to Waiting: customer; Waiting: customer moves to Resolved; Resolved can move back to In review with label `reopened`. Preserve direction and every human label. Use the standard palette.""",
        family="stateDiagram",
        declarations=("stateDiagram-v2", "stateDiagram"),
        colorset="colorset1",
        required_terms=("NewRequest", "InReview", "WaitingCustomer", "Resolved", "New request", "In review", "Waiting: customer", "reopened"),
        patterns=(
            r"state\s+[\"']New request[\"']\s+as\s+NewRequest",
            r"state\s+[\"']In review[\"']\s+as\s+InReview",
            r"state\s+[\"']Waiting: customer[\"']\s+as\s+WaitingCustomer",
            r"NewRequest\s*-->\s*InReview",
            r"InReview\s*-->\s*WaitingCustomer",
            r"WaitingCustomer\s*-->\s*Resolved",
            r"Resolved\s*-->\s*InReview\s*:\s*reopened",
        ),
        forbidden_patterns=(r"[\"'][^\n\"']+[\"']\s*-->",),
        minimum_arrow_count=4,
        visible_terms=("New request", "In review", "Waiting: customer", "Resolved", "reopened"),
        minimum_rendered_text_items=5,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-infer-work-board-standard",
        split="holdout",
        prompt="""Hazme la visualización Mermaid más apropiada para este tablero de trabajo estático, no para reglas de transición. Usa estos IDs y textos exactos. Columna `queued` = `Queued`: tarjeta `schema` = `Define schema`, tarjeta `auth` = `Threat model`. Columna `building` = `Building`: tarjeta `api` = `Implement API`, tarjeta `ui` = `Connect UI`. Columna `shipped` = `Shipped`: tarjeta `docs` = `Publish docs`. Conserva agrupación, orden, IDs y etiquetas. Usa una presentación con color, pero no el color set extended.""",
        family="kanban",
        declarations=("kanban",),
        colorset="colorset1",
        required_terms=("queued", "Queued", "schema", "Define schema", "auth", "Threat model", "building", "Building", "api", "Implement API", "ui", "Connect UI", "shipped", "Shipped", "docs", "Publish docs"),
        patterns=(
            r"queued\s*\[\s*Queued\s*\]",
            r"schema\s*\[\s*Define schema\s*\]",
            r"auth\s*\[\s*Threat model\s*\]",
            r"building\s*\[\s*Building\s*\]",
            r"api\s*\[\s*Implement API\s*\]",
            r"ui\s*\[\s*Connect UI\s*\]",
            r"shipped\s*\[\s*Shipped\s*\]",
            r"docs\s*\[\s*Publish docs\s*\]",
        ),
        ordered_terms=("queued", "schema", "auth", "building", "api", "ui", "shipped", "docs"),
        minimum_indented_lines=8,
        visible_terms=("Queued", "Define schema", "Threat model", "Building", "Implement API", "Connect UI", "Shipped", "Publish docs"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-explicit-sequence-extended",
        split="holdout",
        prompt="""Generate a Mermaid sequence diagram with participants Client, Gateway, and Worker. Preserve this order: Client -> Gateway `Submit job`; Gateway -> Worker `Start job`; activate Worker; loop `Retry up to 2`, Worker -> Gateway `Progress`; then alt `Success`, Worker -->> Gateway `Result` and Gateway -->> Client `Complete`; else `Failure`, Worker -->> Gateway `Error` and Gateway -->> Client `Explain failure`; end and deactivate Worker. Preserve participants, directions, message text, loop, branches, activation, and order. Use the extended full-color palette visibly.""",
        family="sequenceDiagram",
        declarations=("sequenceDiagram",),
        colorset="colorset2",
        required_terms=("Client", "Gateway", "Worker", "Submit job", "Start job", "Retry up to 2", "Progress", "Success", "Result", "Complete", "Failure", "Error", "Explain failure", "activate", "deactivate", "loop", "alt", "else"),
        patterns=(
            r"Client\s*->>\s*Gateway\s*:\s*Submit job",
            r"Gateway\s*->>\s*Worker\s*:\s*Start job",
            r"activate\s+Worker",
            r"loop\s+Retry up to 2",
            r"Worker\s*->>\s*Gateway\s*:\s*Progress",
            r"alt\s+Success",
            r"else\s+Failure",
            r"deactivate\s+Worker",
        ),
        ordered_terms=("Submit job", "Start job", "Retry up to 2", "Progress", "Success", "Result", "Complete", "Failure", "Error", "Explain failure"),
        minimum_arrow_count=7,
        visible_terms=("Client", "Gateway", "Worker", "Submit job", "Retry up to 2", "Success", "Failure", "Explain failure"),
        minimum_rendered_text_items=12,
        maximum_aspect_ratio=5.0,
        required_visual_groups=("accent", "warning"),
        minimum_visible_colors=2,
        minimum_palette_ratio=0.02,
    ),
)


HARD_SEALED_HOLDOUT_V2_TASKS = (
    TaskSpec(
        task_id="hard-sealed-v2-infer-multipredecessor-gantt-standard",
        split="holdout",
        prompt="""Create the most appropriate Mermaid visualization for this project schedule. Use stable IDs `discovery`, `backend`, `frontend`, `integration`, and `launch`. Discovery starts 2031-04-01, lasts 3d, and is done. Backend starts after Discovery, lasts 7d, and is active. Frontend starts after Discovery, lasts 5d, and is done. Integration depends on both Backend and Frontend, lasts 2d, and is critical; schedule it after the prerequisite that finishes last and keep both prerequisites in the human label. Launch is a milestone on 2031-04-20. Preserve dates, durations, states, IDs, dependencies, and labels. Use the standard palette.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset1",
        required_terms=("Discovery", "Backend", "Frontend", "Integration", "Launch", "discovery", "backend", "frontend", "integration", "launch", "2031-04-01", "3d", "7d", "5d", "2d", "2031-04-20", "done", "active", "crit", "milestone"),
        patterns=(
            r"Discovery[^\n]*\bdone\b[^\n]*\bdiscovery\b[^\n]*2031-04-01[^\n]*3d",
            r"Backend[^\n]*\bactive\b[^\n]*\bbackend\b[^\n]*after\s+discovery[^\n]*7d",
            r"Frontend[^\n]*\bdone\b[^\n]*\bfrontend\b[^\n]*after\s+discovery[^\n]*5d",
            r"Integration \(after Backend and Frontend\)[^\n]*\bcrit\b[^\n]*\bintegration\b[^\n]*after\s+backend[^\n]*2d",
            r"Launch[^\n]*\bmilestone\b[^\n]*\blaunch\b[^\n]*2031-04-20",
        ),
        forbidden_patterns=(
            r"Integration \(after Backend and Frontend\)\s*:[^\n]*\bafter\s+\w+[^\n]*\bafter\s+\w+",
            r"(?:Discovery|Backend|Frontend|Integration)[^\n]*:\s*(?:discovery|backend|frontend|integration)\s*,\s*(?:done|active|crit)\b",
        ),
        visible_terms=("Discovery", "Backend", "Frontend", "Integration (after Backend and Frontend)", "Launch"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.03,
    ),
    TaskSpec(
        task_id="hard-sealed-v2-explicit-single-line-xy-extended",
        split="holdout",
        prompt="""Generate an explicit Mermaid XY line chart with one line series for monthly latency change. Keep the category labels clean and in order, and preserve every signed decimal: Jan = +4.50 ms, Feb = -1.25 ms, Mar = +2.00 ms, Apr = -0.75 ms. Use a truthful y-axis range and display the unit `ms`. Use the extended full-color palette visibly.""",
        family="xyChart",
        declarations=("xychart", "xychart-beta"),
        colorset="colorset2",
        required_terms=("Jan", "Feb", "Mar", "Apr", "4.50", "-1.25", "2.00", "-0.75", "ms"),
        patterns=(
            r"x-axis\s*\[\s*[\"']?Jan[\"']?\s*,\s*[\"']?Feb[\"']?\s*,\s*[\"']?Mar[\"']?\s*,\s*[\"']?Apr[\"']?\s*\]",
            r"line\s*\[\s*\+?4\.50\s*,\s*-1\.25\s*,\s*\+?2\.00\s*,\s*-0\.75\s*\]",
        ),
        forbidden_patterns=(r"^\s*(?:bar|pie)\b",),
        ordered_terms=("Jan", "Feb", "Mar", "Apr"),
        visible_terms=("Jan", "Feb", "Mar", "Apr"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=5.0,
        required_visual_groups=("accent",),
        minimum_visible_colors=1,
        minimum_palette_ratio=0.001,
    ),
    TaskSpec(
        task_id="hard-sealed-v2-infer-quoted-sankey-standard",
        split="holdout",
        prompt="""Choose the Mermaid family that best represents these weighted directed transfers. Preserve labels containing commas, every magnitude, and the unit `kg`: `Raw, north` -> `Hub, central` = 40.5; `Raw south` -> `Hub, central` = 19.5; `Hub, central` -> `Finished output` = 55.0; `Hub, central` -> `Scrap` = 5.0. Use the standard palette, not extended.""",
        family="sankey",
        declarations=("sankey", "sankey-beta"),
        colorset="colorset1",
        required_terms=("Raw, north", "Raw south", "Hub, central", "Finished output", "Scrap", "40.5", "19.5", "55.0", "5.0", "kg"),
        patterns=(
            r'"Raw, north"\s*,\s*"Hub, central"\s*,\s*40\.5(?:0+)?\b',
            r'"Raw south"\s*,\s*"Hub, central"\s*,\s*19\.5(?:0+)?\b',
            r'"Hub, central"\s*,\s*"Finished output"\s*,\s*55(?:\.0+)?\b',
            r'"Hub, central"\s*,\s*"Scrap"\s*,\s*5(?:\.0+)?\b',
        ),
        visible_terms=("Raw, north", "Raw south", "Hub, central", "Finished output", "Scrap"),
        minimum_rendered_text_items=5,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-sealed-v2-explicit-reversed-er-extended",
        split="holdout",
        prompt="""Create a Mermaid ER diagram and place ACCESS_TOKEN on the left and SERVICE on the right in the relationship line. SERVICE has service_id PK and name. ACCESS_TOKEN has token_id PK, service_id FK, and expires_at. A SERVICE may issue zero or many ACCESS_TOKEN records; every ACCESS_TOKEN is issued for exactly one SERVICE. Preserve child-to-parent orientation, attributes, keys, and cardinalities, and use the relationship label `issued for`. Use the extended full-color palette visibly.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset2",
        required_terms=("ACCESS_TOKEN", "SERVICE", "service_id", "token_id", "name", "expires_at", "PK", "FK", "issued for"),
        patterns=(
            r"ACCESS_TOKEN\s+\}o\s*--\s*\|\|\s+SERVICE\s*:\s*[\"']issued for[\"']",
            r"unknown\s+service_id\s+FK",
            r"unknown\s+token_id\s+PK",
        ),
        visible_terms=("ACCESS_TOKEN", "SERVICE", "service_id", "token_id", "expires_at", "issued for"),
        minimum_rendered_text_items=6,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("accent",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-v2-infer-concept-map-standard",
        split="holdout",
        prompt="""Create the Mermaid visualization that best organizes this non-quantitative concept hierarchy. Knowledge pipeline contains Inputs, Processing, and Outputs. Inputs contains Documents and Events. Processing contains Parsing and Enrichment. Outputs contains Search and Alerts. Preserve every label and hierarchy; no value represents area or magnitude. Use the standard palette.""",
        family="mindmap",
        declarations=("mindmap",),
        colorset="colorset1",
        required_terms=("Knowledge pipeline", "Inputs", "Processing", "Outputs", "Documents", "Events", "Parsing", "Enrichment", "Search", "Alerts"),
        minimum_indented_lines=8,
        visible_terms=("Knowledge pipeline", "Inputs", "Processing", "Outputs", "Documents", "Events", "Parsing", "Enrichment", "Search", "Alerts"),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
)


HARD_SEALED_HOLDOUT_V3_TASKS = (
    TaskSpec(
        task_id="hard-sealed-v3-infer-decision-flow-standard",
        split="holdout",
        prompt="""Choose the Mermaid family that best communicates this directed request-handling process. `Receive request` leads to `Validate token`, then decision `Valid token?`. `No` leads to `Reject 401`. `Yes` leads to `Load account`, then `Return 200`. Preserve every label, branch label, direction, and order. Use a colorful presentation, but do not use the extended color set.""",
        family="flowchart",
        declarations=("flowchart", "graph"),
        colorset="colorset1",
        required_terms=("Receive request", "Validate token", "Valid token?", "No", "Reject 401", "Yes", "Load account", "Return 200"),
        patterns=(r"\{[^\n}]*Valid token\?[^\n}]*\}",),
        ordered_terms=("Receive request", "Validate token", "Valid token?"),
        minimum_arrow_count=5,
        visible_terms=("Receive request", "Validate token", "Valid token?", "No", "Reject 401", "Yes", "Load account", "Return 200"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-v3-infer-quadrant-extended",
        split="holdout",
        prompt="""Create the Mermaid visualization that best compares initiatives on two normalized dimensions. X axis is `Effort: Low` to `Effort: High`; y axis is `Value: Low` to `Value: High`. Preserve exactly: Cache cleanup [0.18, 0.32], Billing rewrite [0.86, 0.91], Search tuning [0.44, 0.73], Archive export [0.67, 0.24]. Use the extended full-color palette visibly.""",
        family="quadrantChart",
        declarations=("quadrantChart",),
        colorset="colorset2",
        required_terms=("Effort: Low", "Effort: High", "Value: Low", "Value: High", "Cache cleanup", "Billing rewrite", "Search tuning", "Archive export", "0.18", "0.32", "0.86", "0.91", "0.44", "0.73", "0.67", "0.24"),
        patterns=(
            r"Cache cleanup[\"']?\s*:\s*\[\s*0\.18\s*,\s*0\.32\s*\]",
            r"Billing rewrite[\"']?\s*:\s*\[\s*0\.86\s*,\s*0\.91\s*\]",
            r"Search tuning[\"']?\s*:\s*\[\s*0\.44\s*,\s*0\.73\s*\]",
            r"Archive export[\"']?\s*:\s*\[\s*0\.67\s*,\s*0\.24\s*\]",
        ),
        visible_terms=("Effort: Low", "Effort: High", "Value: Low", "Value: High", "Cache cleanup", "Billing rewrite", "Search tuning", "Archive export"),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=4.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.15,
    ),
    TaskSpec(
        task_id="hard-sealed-v3-infer-parts-whole-standard",
        split="holdout",
        prompt="""Create the Mermaid visualization that most directly shows parts of the same total of 120 seats: Engineering = 52, Sales = 31, Support = 22, Operations = 15. Preserve every label, value, and the unit `seats`. Use the standard palette, not extended.""",
        family="pie",
        declarations=("pie",),
        colorset="colorset1",
        required_terms=("Engineering", "Sales", "Support", "Operations", "52", "31", "22", "15", "seats"),
        patterns=(
            r"[\"']?Engineering[\"']?\s*:\s*52(?:\.0+)?\b",
            r"[\"']?Sales[\"']?\s*:\s*31(?:\.0+)?\b",
            r"[\"']?Support[\"']?\s*:\s*22(?:\.0+)?\b",
            r"[\"']?Operations[\"']?\s*:\s*15(?:\.0+)?\b",
        ),
        visible_terms=("Engineering", "Sales", "Support", "Operations", "52", "31", "22", "15"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=4.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-sealed-v3-infer-type-composition-extended",
        split="holdout",
        prompt="""Choose the Mermaid diagram that best communicates this software type structure. Document has `id: UUID` and `render(): bytes`. Report adds `pages: int` and inherits Document. Section has `title: string`. One Report composes one or more Section objects. Preserve type names, members, method signature, inheritance, composition, and multiplicities. Use the extended full-color palette visibly.""",
        family="classDiagram",
        declarations=("classDiagram", "classDiagram-v2"),
        colorset="colorset2",
        required_terms=("Document", "Report", "Section", "id", "UUID", "render", "bytes", "pages", "int", "title", "string", "1", "1..*"),
        patterns=(
            r"(?:Report\s+--\|>\s+Document|Document\s+<\|--\s+Report)",
            r"(?:Report[^\n]*\*--[^\n]*Section|Section[^\n]*--\*[^\n]*Report)",
            r"render\s*\(\s*\)\s*:\s*bytes|render\s*\(\s*\)\s+bytes",
        ),
        visible_terms=("Document", "Report", "Section", "id", "render", "pages", "title"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("accent",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-v3-explicit-git-history-extended",
        split="holdout",
        prompt="""Generate a Mermaid Git graph and preserve this history order. On main commit `BASE`; create branch `analytics`, check it out, and commit `METRICS`; check out `main` and commit `HOTFIX`; merge `analytics` into main with tag `v2.0`; then commit `RELEASE`. Preserve branch name, commit IDs, checkout order, merge direction, and tag. Use the extended full-color palette visibly.""",
        family="gitGraph",
        declarations=("gitGraph",),
        colorset="colorset2",
        required_terms=("BASE", "analytics", "METRICS", "main", "HOTFIX", "v2.0", "RELEASE", "branch", "checkout", "merge", "tag"),
        patterns=(
            r"commit\s+id\s*:\s*[\"']BASE[\"']",
            r"branch\s+analytics",
            r"checkout\s+analytics",
            r"commit\s+id\s*:\s*[\"']METRICS[\"']",
            r"checkout\s+main",
            r"commit\s+id\s*:\s*[\"']HOTFIX[\"']",
            r"merge\s+analytics[^\n]*tag\s*:\s*[\"']v2\.0[\"']",
            r"commit\s+id\s*:\s*[\"']RELEASE[\"']",
        ),
        ordered_terms=("BASE", "branch", "analytics", "METRICS", "main", "HOTFIX", "merge", "v2.0", "RELEASE"),
        visible_terms=("BASE", "analytics", "METRICS", "main", "HOTFIX", "v2.0", "RELEASE"),
        minimum_rendered_text_items=7,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent",),
        minimum_palette_ratio=0.005,
    ),
)


HARD_SEALED_HOLDOUT_V4_TASKS = (
    TaskSpec(
        task_id="hard-sealed-v4-infer-delivery-gantt-standard",
        split="holdout",
        prompt="""Choose and create the Mermaid diagram that best shows this delivery schedule. Use stable IDs `research`, `service`, `console`, `acceptance`, and `go_live`. Research starts 2032-01-10, lasts 5d, and is done. Service starts after Research, lasts 9d, and is active. Console starts after Research, lasts 7d, and is done. Acceptance depends on both Service and Console, lasts 4d, and is critical; schedule it after the prerequisite that finishes last and keep both prerequisites visible in its human label. Go live is a milestone on 2032-02-10. Preserve all facts and use the standard palette.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset1",
        required_terms=("Research", "Service", "Console", "Acceptance", "Go live", "research", "service", "console", "acceptance", "go_live", "2032-01-10", "5d", "9d", "7d", "4d", "2032-02-10", "done", "active", "crit", "milestone"),
        patterns=(
            r"Research[^\n]*\bdone\b[^\n]*\bresearch\b[^\n]*2032-01-10[^\n]*5d",
            r"Service[^\n]*\bactive\b[^\n]*\bservice\b[^\n]*after\s+research[^\n]*9d",
            r"Console[^\n]*\bdone\b[^\n]*\bconsole\b[^\n]*after\s+research[^\n]*7d",
            r"Acceptance \(after Service and Console\)[^\n]*\bcrit\b[^\n]*\bacceptance\b[^\n]*after\s+service[^\n]*4d",
            r"Go live[^\n]*\bmilestone\b[^\n]*\bgo_live\b[^\n]*2032-02-10",
        ),
        forbidden_patterns=(
            r"Acceptance \(after Service and Console\)\s*:[^\n]*\bafter\s+\w+[^\n]*\bafter\s+\w+",
            r"(?:Research|Service|Console|Acceptance)[^\n]*:\s*(?:research|service|console|acceptance)\s*,\s*(?:done|active|crit)\b",
        ),
        visible_terms=("Research", "Service", "Console", "Acceptance (after Service and Console)", "Go live"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.03,
    ),
    TaskSpec(
        task_id="hard-sealed-v4-explicit-line-xy-extended",
        split="holdout",
        prompt="""Create an explicit Mermaid XY line chart with one line series for daily queue-time change. Keep only the category names on the x-axis and preserve this order and every signed decimal: Mon = +1.20 s, Tue = -0.40 s, Wed = +2.75 s, Thu = 0.00 s, Fri = -1.10 s. Use a truthful y-axis and show the unit `seconds`. Use the extended full-color palette visibly.""",
        family="xyChart",
        declarations=("xychart", "xychart-beta"),
        colorset="colorset2",
        required_terms=("Mon", "Tue", "Wed", "Thu", "Fri", "1.20", "-0.40", "2.75", "0.00", "-1.10", "seconds"),
        patterns=(
            r"x-axis\s*\[\s*[\"']?Mon[\"']?\s*,\s*[\"']?Tue[\"']?\s*,\s*[\"']?Wed[\"']?\s*,\s*[\"']?Thu[\"']?\s*,\s*[\"']?Fri[\"']?\s*\]",
            r"line\s*\[\s*\+?1\.20\s*,\s*-0\.40\s*,\s*\+?2\.75\s*,\s*0\.00\s*,\s*-1\.10\s*\]",
        ),
        forbidden_patterns=(r"^\s*(?:bar|pie)\b",),
        ordered_terms=("Mon", "Tue", "Wed", "Thu", "Fri"),
        visible_terms=("Mon", "Tue", "Wed", "Thu", "Fri"),
        minimum_rendered_text_items=9,
        maximum_aspect_ratio=5.0,
        required_visual_groups=("accent",),
        minimum_visible_colors=1,
        minimum_palette_ratio=0.001,
    ),
    TaskSpec(
        task_id="hard-sealed-v4-infer-milestones-timeline-extended",
        split="holdout",
        prompt="""Choose the Mermaid visualization that most directly presents these dated milestones without task durations: 2033-01-08 — Charter approved; 2033-03-17 — Lab opened; 2033-06-05 — Trial completed; 2033-09-14 — Certification granted; 2033-12-01 — Service launched. Preserve dates, labels, and order; do not invent durations. Use the extended full-color palette visibly.""",
        family="timeline",
        declarations=("timeline",),
        colorset="colorset2",
        required_terms=("2033-01-08", "Charter approved", "2033-03-17", "Lab opened", "2033-06-05", "Trial completed", "2033-09-14", "Certification granted", "2033-12-01", "Service launched"),
        patterns=(
            r"2033-01-08\s*:\s*Charter approved",
            r"2033-03-17\s*:\s*Lab opened",
            r"2033-06-05\s*:\s*Trial completed",
            r"2033-09-14\s*:\s*Certification granted",
            r"2033-12-01\s*:\s*Service launched",
        ),
        ordered_terms=("2033-01-08", "2033-03-17", "2033-06-05", "2033-09-14", "2033-12-01"),
        visible_terms=("2033-01-08", "Charter approved", "2033-06-05", "Trial completed", "2033-12-01", "Service launched"),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-sealed-v4-infer-budget-treemap-standard",
        split="holdout",
        prompt="""Choose the Mermaid visualization where rectangle area best communicates this quantitative hierarchy. Program budget contains People, Platform, and Operations. People contains Engineering = 46 and Design = 14. Platform contains Compute = 20 and Data = 12. Operations contains Support = 8. Preserve hierarchy, labels, values, and the unit `budget points`. Use the standard palette, not extended.""",
        family="treemap",
        declarations=("treemap-beta", "treemap"),
        colorset="colorset1",
        required_terms=("Program budget", "People", "Platform", "Operations", "Engineering", "Design", "Compute", "Data", "Support", "46", "14", "20", "12", "8", "budget points"),
        patterns=(
            r"[\"']Engineering[\"']\s*:\s*46(?:\.0+)?\b",
            r"[\"']Design[\"']\s*:\s*14(?:\.0+)?\b",
            r"[\"']Compute[\"']\s*:\s*20(?:\.0+)?\b",
            r"[\"']Data[\"']\s*:\s*12(?:\.0+)?\b",
            r"[\"']Support[\"']\s*:\s*8(?:\.0+)?\b",
        ),
        minimum_indented_lines=8,
        visible_terms=("Program budget", "People", "Platform", "Operations", "Engineering", "Design", "Compute", "Data", "Support"),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=4.0,
        required_visual_groups=("primary",),
        minimum_visible_colors=1,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-v4-infer-asset-types-extended",
        split="holdout",
        prompt="""Choose the Mermaid family that best communicates this software type structure. Asset has `asset_id: UUID` and `export(): bytes`. ImageAsset adds `width: int` and inherits Asset. Layer has `name: string`. One ImageAsset composes one or more Layer objects. Preserve type names, members, method signature, inheritance, composition, and multiplicities. Use the extended full-color palette visibly.""",
        family="classDiagram",
        declarations=("classDiagram", "classDiagram-v2"),
        colorset="colorset2",
        required_terms=("Asset", "ImageAsset", "Layer", "asset_id", "UUID", "export", "bytes", "width", "int", "name", "string", "1", "1..*"),
        patterns=(
            r"(?:ImageAsset\s+--\|>\s+Asset|Asset\s+<\|--\s+ImageAsset)",
            r"(?:ImageAsset[^\n]*\*--[^\n]*Layer|Layer[^\n]*--\*[^\n]*ImageAsset)",
            r"export\s*\(\s*\)\s*:\s*bytes|export\s*\(\s*\)\s+bytes",
        ),
        visible_terms=("Asset", "ImageAsset", "Layer", "asset_id", "export", "width", "name"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("accent",),
        minimum_palette_ratio=0.01,
    ),
)


HARD_SEALED_HOLDOUT_V5_TASKS = (
    TaskSpec(
        task_id="hard-sealed-v5-infer-resource-treemap-extended",
        split="holdout",
        prompt="""Choose the Mermaid visualization where rectangle area best communicates this quantitative hierarchy. Portfolio allocation contains Product Delivery, Core Systems, and Governance. Product Delivery contains Mobile = 37.5 and Web = 22.5. Core Systems contains Compute = 18.0 and Data = 13.0. Governance contains Risk = 9.0. Preserve the hierarchy, every label, every decimal value, and the unit `allocation points`. Every named branch and leaf must remain readable, including the smallest branch. Use the extended full-color palette visibly.""",
        family="treemap",
        declarations=("treemap-beta", "treemap"),
        colorset="colorset2",
        required_terms=("Portfolio allocation", "Product Delivery", "Core Systems", "Governance", "Mobile", "Web", "Compute", "Data", "Risk", "37.5", "22.5", "18.0", "13.0", "9.0", "allocation points"),
        patterns=(
            r"[\"']Mobile[\"']\s*:\s*37\.5(?:0+)?\b",
            r"[\"']Web[\"']\s*:\s*22\.5(?:0+)?\b",
            r"[\"']Compute[\"']\s*:\s*18(?:\.0+)?\b",
            r"[\"']Data[\"']\s*:\s*13(?:\.0+)?\b",
            r"[\"']Risk[\"']\s*:\s*9(?:\.0+)?\b",
        ),
        minimum_indented_lines=8,
        visible_terms=("Portfolio allocation", "Product Delivery", "Core Systems", "Governance", "Mobile", "Web", "Compute", "Data", "Risk"),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=4.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-sealed-v5-conflicting-donut-standard",
        split="holdout",
        prompt="""Create a Mermaid donut or pie-style chart for signed regional conversion change: Alpha = +9.75%, Beta = -2.50%, Gamma = 0.00%, Delta = +4.25%. Preserve order, signs, decimals, labels, and the percentage unit. Use a colorful presentation, but do not use the extended color set. If the requested chart would misrepresent signed changes, choose a truthful Mermaid alternative and explain why.""",
        family="xyChart",
        declarations=("xychart", "xychart-beta"),
        colorset="colorset1",
        required_terms=("Alpha", "Beta", "Gamma", "Delta", "9.75", "-2.50", "0.00", "4.25", "%"),
        patterns=(
            r"x-axis\s*\[\s*[\"']?Alpha[\"']?\s*,\s*[\"']?Beta[\"']?\s*,\s*[\"']?Gamma[\"']?\s*,\s*[\"']?Delta[\"']?\s*\]",
            r"(?:bar|line)\s*\[\s*\+?9\.75\s*,\s*-2\.50\s*,\s*0\.00\s*,\s*\+?4\.25\s*\]",
        ),
        forbidden_patterns=(r"^\s*pie\b",),
        ordered_terms=("Alpha", "Beta", "Gamma", "Delta"),
        visible_terms=("Alpha", "Beta", "Gamma", "Delta"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=5.0,
        reason_patterns=(r"negativ|signed|sign|below zero|not parts|not proportions",),
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-v5-infer-milestones-timeline-extended",
        split="holdout",
        prompt="""Choose the Mermaid visualization that most directly presents these dated milestones without task durations: 2034-02-03 — Charter signed; 2034-04-19 — Prototype demonstrated; 2034-07-11 — Field trial passed; 2034-10-08 — License issued; 2035-01-15 — Service opened. Preserve every date, label, and chronological order; do not invent durations. Use the extended full-color palette visibly.""",
        family="timeline",
        declarations=("timeline",),
        colorset="colorset2",
        required_terms=("2034-02-03", "Charter signed", "2034-04-19", "Prototype demonstrated", "2034-07-11", "Field trial passed", "2034-10-08", "License issued", "2035-01-15", "Service opened"),
        patterns=(
            r"2034-02-03\s*:\s*Charter signed",
            r"2034-04-19\s*:\s*Prototype demonstrated",
            r"2034-07-11\s*:\s*Field trial passed",
            r"2034-10-08\s*:\s*License issued",
            r"2035-01-15\s*:\s*Service opened",
        ),
        ordered_terms=("2034-02-03", "2034-04-19", "2034-07-11", "2034-10-08", "2035-01-15"),
        visible_terms=("2034-02-03", "Charter signed", "2034-07-11", "Field trial passed", "2035-01-15", "Service opened"),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-sealed-v5-infer-message-types-standard",
        split="holdout",
        prompt="""Choose the Mermaid family that best communicates this software type structure. Message has `message_id: UUID` and `send(): bool`. EmailMessage adds `subject: string` and inherits Message. Attachment has `name: string`. One EmailMessage composes zero or more Attachment objects. Preserve type names, members, method signature, inheritance, composition, and multiplicities. Use the standard palette.""",
        family="classDiagram",
        declarations=("classDiagram", "classDiagram-v2"),
        colorset="colorset1",
        required_terms=("Message", "EmailMessage", "Attachment", "message_id", "UUID", "send", "bool", "subject", "string", "name", "0..*", "1"),
        patterns=(
            r"(?:EmailMessage\s+--\|>\s+Message|Message\s+<\|--\s+EmailMessage)",
            r"(?:EmailMessage[^\n]*\*--[^\n]*Attachment|Attachment[^\n]*--\*[^\n]*EmailMessage)",
            r"send\s*\(\s*\)\s*:\s*bool|send\s*\(\s*\)\s+bool",
        ),
        visible_terms=("Message", "EmailMessage", "Attachment", "message_id", "send", "subject", "name"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-v5-infer-release-gantt-extended",
        split="holdout",
        prompt="""Choose and create the Mermaid diagram that best shows this release schedule. Use stable IDs `brief`, `api`, `portal`, `certification`, and `release`. Brief starts 2035-03-03, lasts 4d, and is done. API starts after Brief, lasts 9d, and is active. Portal starts after Brief, lasts 7d, and is done. Certification depends on both API and Portal, lasts 3d, and is critical; schedule it after the prerequisite that finishes last and keep both prerequisites visible in its human label. Release is a milestone on 2035-03-24. Preserve all facts and use the extended full-color palette visibly.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset2",
        required_terms=("Brief", "API", "Portal", "Certification", "Release", "brief", "api", "portal", "certification", "release", "2035-03-03", "4d", "9d", "7d", "3d", "2035-03-24", "done", "active", "crit", "milestone"),
        patterns=(
            r"Brief[^\n]*\bdone\b[^\n]*\bbrief\b[^\n]*2035-03-03[^\n]*4d",
            r"API[^\n]*\bactive\b[^\n]*\bapi\b[^\n]*after\s+brief[^\n]*9d",
            r"Portal[^\n]*\bdone\b[^\n]*\bportal\b[^\n]*after\s+brief[^\n]*7d",
            r"Certification \(after API and Portal\)[^\n]*\bcrit\b[^\n]*\bcertification\b[^\n]*after\s+api[^\n]*3d",
            r"Release[^\n]*\bmilestone\b[^\n]*\brelease\b[^\n]*2035-03-24",
        ),
        forbidden_patterns=(
            r"Certification \(after API and Portal\)\s*:[^\n]*\bafter\s+\w+[^\n]*\bafter\s+\w+",
            r"(?:Brief|API|Portal|Certification)[^\n]*:\s*(?:brief|api|portal|certification)\s*,\s*(?:done|active|crit)\b",
        ),
        visible_terms=("Brief", "API", "Portal", "Certification (after API and Portal)", "Release"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.03,
    ),
    TaskSpec(
        task_id="hard-sealed-v5-infer-quoted-sankey-standard",
        split="holdout",
        prompt="""Choose the Mermaid visualization that best shows these weighted directed transfers. Preserve labels containing commas exactly and keep every value and the unit `tonnes`: `Inbound, north` -> `Mixer, one` = 42.75; `Inbound, south` -> `Mixer, one` = 17.25; `Mixer, one` -> `Saleable output` = 53.5; `Mixer, one` -> `Residual waste` = 6.5. Use the standard palette, not the extended color set.""",
        family="sankey",
        declarations=("sankey", "sankey-beta"),
        colorset="colorset1",
        required_terms=("Inbound, north", "Inbound, south", "Mixer, one", "Saleable output", "Residual waste", "42.75", "17.25", "53.5", "6.5", "tonnes"),
        patterns=(
            r'"Inbound, north"\s*,\s*"Mixer, one"\s*,\s*42\.75(?:0+)?\b',
            r'"Inbound, south"\s*,\s*"Mixer, one"\s*,\s*17\.25(?:0+)?\b',
            r'"Mixer, one"\s*,\s*"Saleable output"\s*,\s*53\.5(?:0+)?\b',
            r'"Mixer, one"\s*,\s*"Residual waste"\s*,\s*6\.5(?:0+)?\b',
        ),
        visible_terms=("Inbound, north", "Inbound, south", "Mixer, one", "Saleable output", "Residual waste"),
        minimum_rendered_text_items=5,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("primary",),
        minimum_visible_colors=1,
        minimum_palette_ratio=0.01,
    ),
)


HARD_SEALED_HOLDOUT_V6_TASKS = (
    TaskSpec(
        task_id="hard-sealed-v6-infer-capacity-treemap-extended",
        split="holdout",
        prompt="""Choose the Mermaid visualization where rectangle area best communicates this quantitative hierarchy. Service capacity contains Customer Experience, Platform Engineering, and Policy Operations. Customer Experience contains Chat = 26 and Voice = 18. Platform Engineering contains Runtime = 29 and Storage = 17. Policy Operations contains Compliance = 6 and Audit = 4. Preserve the hierarchy, every label, every value, and the unit `capacity points`. Every named branch and leaf must remain readable, including the smallest branch. Use the extended full-color palette visibly.""",
        family="treemap",
        declarations=("treemap-beta", "treemap"),
        colorset="colorset2",
        required_terms=("Service capacity", "Customer Experience", "Platform Engineering", "Policy Operations", "Chat", "Voice", "Runtime", "Storage", "Compliance", "Audit", "26", "18", "29", "17", "6", "4", "capacity points"),
        patterns=(
            r"[\"']Chat[\"']\s*:\s*26(?:\.0+)?\b",
            r"[\"']Voice[\"']\s*:\s*18(?:\.0+)?\b",
            r"[\"']Runtime[\"']\s*:\s*29(?:\.0+)?\b",
            r"[\"']Storage[\"']\s*:\s*17(?:\.0+)?\b",
            r"[\"']Compliance[\"']\s*:\s*6(?:\.0+)?\b",
            r"[\"']Audit[\"']\s*:\s*4(?:\.0+)?\b",
        ),
        minimum_indented_lines=9,
        visible_terms=("Service capacity", "Customer Experience", "Platform Engineering", "Policy Operations", "Chat", "Voice", "Runtime", "Storage", "Compliance", "Audit"),
        minimum_rendered_text_items=12,
        maximum_aspect_ratio=4.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-sealed-v6-conflicting-pie-standard",
        split="holdout",
        prompt="""Make a Mermaid pie chart for signed satisfaction change by channel: Store = +7.50%, Web = -1.25%, Partner = +3.00%, Direct = 0.00%. Preserve order, signs, decimals, labels, and the percentage unit. Use a colorful presentation, but do not use the extended color set. If the requested family would misrepresent signed changes, choose a truthful Mermaid alternative and explain why.""",
        family="xyChart",
        declarations=("xychart", "xychart-beta"),
        colorset="colorset1",
        required_terms=("Store", "Web", "Partner", "Direct", "7.50", "-1.25", "3.00", "0.00", "%"),
        patterns=(
            r"x-axis\s*\[\s*[\"']?Store[\"']?\s*,\s*[\"']?Web[\"']?\s*,\s*[\"']?Partner[\"']?\s*,\s*[\"']?Direct[\"']?\s*\]",
            r"(?:bar|line)\s*\[\s*\+?7\.50\s*,\s*-1\.25\s*,\s*\+?3\.00\s*,\s*0\.00\s*\]",
        ),
        forbidden_patterns=(r"^\s*pie\b",),
        ordered_terms=("Store", "Web", "Partner", "Direct"),
        visible_terms=("Store", "Web", "Partner", "Direct"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=5.0,
        reason_patterns=(r"negativ|signed|sign|below zero|not parts|not proportions",),
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-v6-infer-milestones-timeline-extended",
        split="holdout",
        prompt="""Choose the Mermaid visualization that most directly presents these dated milestones without task durations: 2036-01-21 — Scope ratified; 2036-04-02 — Lab commissioned; 2036-07-27 — Pilot certified; 2036-10-16 — Network authorized; 2037-02-05 — Operations commenced. Preserve every date, label, and chronological order; do not invent durations. Use the extended full-color palette visibly.""",
        family="timeline",
        declarations=("timeline",),
        colorset="colorset2",
        required_terms=("2036-01-21", "Scope ratified", "2036-04-02", "Lab commissioned", "2036-07-27", "Pilot certified", "2036-10-16", "Network authorized", "2037-02-05", "Operations commenced"),
        patterns=(
            r"2036-01-21\s*:\s*Scope ratified",
            r"2036-04-02\s*:\s*Lab commissioned",
            r"2036-07-27\s*:\s*Pilot certified",
            r"2036-10-16\s*:\s*Network authorized",
            r"2037-02-05\s*:\s*Operations commenced",
        ),
        ordered_terms=("2036-01-21", "2036-04-02", "2036-07-27", "2036-10-16", "2037-02-05"),
        visible_terms=("2036-01-21", "Scope ratified", "2036-07-27", "Pilot certified", "2037-02-05", "Operations commenced"),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="hard-sealed-v6-infer-document-types-standard",
        split="holdout",
        prompt="""Choose the Mermaid family that best communicates this software type structure. Document has `document_id: UUID` and `render(): bytes`. Report adds `period: string` and inherits Document. Section has `heading: string`. One Report composes one or more Section objects. Preserve type names, members, method signature, inheritance, composition, and multiplicities. Use the standard palette.""",
        family="classDiagram",
        declarations=("classDiagram", "classDiagram-v2"),
        colorset="colorset1",
        required_terms=("Document", "Report", "Section", "document_id", "UUID", "render", "bytes", "period", "string", "heading", "1..*", "1"),
        patterns=(
            r"(?:Report\s+--\|>\s+Document|Document\s+<\|--\s+Report)",
            r"(?:Report[^\n]*\*--[^\n]*Section|Section[^\n]*--\*[^\n]*Report)",
            r"render\s*\(\s*\)\s*:\s*bytes|render\s*\(\s*\)\s+bytes",
        ),
        visible_terms=("Document", "Report", "Section", "document_id", "render", "period", "heading"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="hard-sealed-v6-infer-deployment-gantt-extended",
        split="holdout",
        prompt="""Choose and create the Mermaid diagram that best shows this deployment schedule. Use stable IDs `plan`, `backend`, `client`, `assurance`, and `launch`. Plan starts 2037-05-04, lasts 3d, and is done. Backend starts after Plan, lasts 8d, and is active. Client starts after Plan, lasts 6d, and is done. Assurance depends on both Backend and Client, lasts 4d, and is critical; schedule it after the prerequisite that finishes last and keep both prerequisites visible in its human label. Launch is a milestone on 2037-05-25. Preserve all facts and use the extended full-color palette visibly.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset2",
        required_terms=("Plan", "Backend", "Client", "Assurance", "Launch", "plan", "backend", "client", "assurance", "launch", "2037-05-04", "3d", "8d", "6d", "4d", "2037-05-25", "done", "active", "crit", "milestone"),
        patterns=(
            r"Plan[^\n]*\bdone\b[^\n]*\bplan\b[^\n]*2037-05-04[^\n]*3d",
            r"Backend[^\n]*\bactive\b[^\n]*\bbackend\b[^\n]*after\s+plan[^\n]*8d",
            r"Client[^\n]*\bdone\b[^\n]*\bclient\b[^\n]*after\s+plan[^\n]*6d",
            r"Assurance \(after Backend and Client\)[^\n]*\bcrit\b[^\n]*\bassurance\b[^\n]*after\s+backend[^\n]*4d",
            r"Launch[^\n]*\bmilestone\b[^\n]*\blaunch\b[^\n]*2037-05-25",
        ),
        forbidden_patterns=(
            r"Assurance \(after Backend and Client\)\s*:[^\n]*\bafter\s+\w+[^\n]*\bafter\s+\w+",
            r"(?:Plan|Backend|Client|Assurance)[^\n]*:\s*(?:plan|backend|client|assurance)\s*,\s*(?:done|active|crit)\b",
        ),
        visible_terms=("Plan", "Backend", "Client", "Assurance (after Backend and Client)", "Launch"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.03,
    ),
)


MAX_CAPACITY_DEVELOPMENT_TASKS = (
    TaskSpec(
        task_id="capacity-dev-mindmap-standard",
        split="development",
        prompt="""Create a Mermaid mindmap that consumes every distinct first-level branch color once before cycling. Use the root label `Capacity map`. Name its direct children `Mind branch 01`, `Mind branch 02`, and so on, stopping exactly at Mermaid 11.16.0's last non-cycling first-level branch. Add no deeper child levels. Use the standard palette.""",
        family="mindmap",
        declarations=("mindmap",),
        colorset="colorset1",
        required_terms=("Capacity map",)
        + tuple(f"Mind branch {index:02d}" for index in range(1, 12)),
        patterns=tuple(
            rf"^\s+Mind branch {index:02d}\s*$" for index in range(1, 12)
        ),
        forbidden_patterns=(r"Mind branch 12",),
        minimum_indented_lines=11,
        visible_terms=("Capacity map", "Mind branch 01", "Mind branch 06", "Mind branch 11"),
        minimum_rendered_text_items=12,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-dev-gitgraph-extended",
        split="development",
        prompt="""Create a Mermaid GitGraph that consumes every branch color exactly once before cycling. Count the main branch as the first branch. Give main one commit named `main-slot`, then create sequential branches `branch-01`, `branch-02`, and so on through Mermaid 11.16.0's final distinct branch slot; give each branch one matching commit and return to main before creating the next. Stop before the palette cycles. Use the extended full-color palette.""",
        family="gitGraph",
        declarations=("gitGraph",),
        colorset="colorset2",
        required_terms=("main-slot",)
        + tuple(f"branch-{index:02d}" for index in range(1, 8)),
        patterns=tuple(
            rf"^\s*branch\s+branch-{index:02d}\s*$" for index in range(1, 8)
        ),
        forbidden_patterns=(r"branch-08",),
        visible_terms=("main", "branch-01", "branch-04", "branch-07"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="capacity-dev-journey-boundary-standard",
        split="development",
        prompt="""Create a Mermaid Journey that demonstrates its reachable section-color boundary. Use one task per section. Consume every distinct reachable section class once, then add exactly one more section that proves the first color cycle. Name sections sequentially `Journey slot 01`, `Journey slot 02`, and so on; name their tasks `Step 01`, `Step 02`, and so on. Use agent `Owner` and the standard palette.""",
        family="journey",
        declarations=("journey",),
        colorset="colorset1",
        required_terms=tuple(f"Journey slot {index:02d}" for index in range(1, 9))
        + tuple(f"Step {index:02d}" for index in range(1, 9)),
        patterns=tuple(
            rf"^\s*section\s+Journey slot {index:02d}\s*$"
            for index in range(1, 9)
        ),
        forbidden_patterns=(r"Journey slot 09", r"Step 09"),
        visible_terms=("Journey slot 01", "Journey slot 07", "Journey slot 08", "Step 08"),
        minimum_rendered_text_items=16,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
)


MAX_CAPACITY_HOLDOUT_TASKS = (
    TaskSpec(
        task_id="capacity-holdout-radar-extended",
        split="holdout",
        prompt="""Create a Mermaid Radar chart that consumes every non-cycling curve color exactly once. Use axes `Quality`, `Speed`, `Cost`, and `Reliability`. Name curves sequentially `Radar curve 01`, `Radar curve 02`, and so on, stopping at Mermaid 11.16.0's last distinct curve slot. Give every curve four values from 1 to 5 and keep every curve visible. Use the extended full-color palette.""",
        family="radar",
        declarations=("radar-beta",),
        colorset="colorset2",
        required_terms=("Quality", "Speed", "Cost", "Reliability")
        + tuple(f"Radar curve {index:02d}" for index in range(1, 13)),
        patterns=tuple(
            rf"^\s*curve\s+\w+\[\"Radar curve {index:02d}\"\]"
            for index in range(1, 13)
        ),
        forbidden_patterns=(r"Radar curve 13",),
        visible_terms=("Radar curve 01", "Radar curve 06", "Radar curve 12"),
        minimum_rendered_text_items=16,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.02,
    ),
    TaskSpec(
        task_id="capacity-holdout-treemap-standard",
        split="holdout",
        prompt="""Create a Mermaid Treemap that consumes every non-cycling group color exactly once. Use root `Capacity portfolio`. Add sequential direct groups `Treemap group 01`, `Treemap group 02`, and so on through Mermaid 11.16.0's final distinct group slot. Give each group exactly one matching leaf `Leaf 01`, `Leaf 02`, and so on, with descending positive integer values. Stop before the group palette cycles. Use the standard palette and keep every leaf label visible.""",
        family="treemap",
        declarations=("treemap-beta",),
        colorset="colorset1",
        required_terms=("Capacity portfolio",)
        + tuple(f"Treemap group {index:02d}" for index in range(1, 13))
        + tuple(f"Leaf {index:02d}" for index in range(1, 13)),
        patterns=tuple(
            rf"\"Treemap group {index:02d}\"" for index in range(1, 13)
        )
        + tuple(rf"\"Leaf {index:02d}\"\s*:" for index in range(1, 13)),
        forbidden_patterns=(r"Treemap group 13", r"Leaf 13"),
        visible_terms=("Leaf 01", "Leaf 06", "Leaf 12"),
        minimum_rendered_text_items=25,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-holdout-kanban-extended",
        split="holdout",
        prompt="""Create a Mermaid Kanban board that consumes every column color Mermaid 11.16.0 can reach before its generated section rules stop. Name columns sequentially `Kanban slot 01`, `Kanban slot 02`, and so on through the last reachable colored column. Put exactly one matching task `Work 01`, `Work 02`, and so on in each column. Do not add an uncolored overflow column. Use the extended full-color palette.""",
        family="kanban",
        declarations=("kanban",),
        colorset="colorset2",
        required_terms=tuple(f"Kanban slot {index:02d}" for index in range(1, 11))
        + tuple(f"Work {index:02d}" for index in range(1, 11)),
        patterns=tuple(
            rf"Kanban slot {index:02d}" for index in range(1, 11)
        ),
        forbidden_patterns=(r"Kanban slot 11", r"Work 11"),
        visible_terms=("Kanban slot 01", "Kanban slot 05", "Kanban slot 10", "Work 10"),
        minimum_rendered_text_items=20,
        maximum_aspect_ratio=12.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
)


# The v1 holdout is retained verbatim as historical evidence. Its failures were
# opened as v2 development evidence; the v2 holdout below uses new families and
# prompts so it remains disjoint and untouched until promotion time.
MAX_CAPACITY_V2_DEVELOPMENT_TASKS = (
    TaskSpec(
        task_id="capacity-v2-dev-radar-extended",
        split="development",
        prompt="""Create a Mermaid Radar chart that consumes every non-cycling curve color exactly once. Use axes `Quality`, `Speed`, `Cost`, and `Reliability`. Name curves sequentially `Radar curve 01`, `Radar curve 02`, and so on, stopping at Mermaid 11.16.0's last distinct curve slot. Give every curve four values from 1 to 5 and keep every curve visible. Use the extended full-color palette.""",
        family="radar",
        declarations=("radar-beta",),
        colorset="colorset2",
        required_terms=("Quality", "Speed", "Cost", "Reliability")
        + tuple(f"Radar curve {index:02d}" for index in range(1, 13)),
        patterns=tuple(
            rf"^\s*curve\s+\w+\[\"Radar curve {index:02d}\"\]"
            for index in range(1, 13)
        ),
        forbidden_patterns=(r"Radar curve 13",),
        visible_terms=("Radar curve 01", "Radar curve 06", "Radar curve 12"),
        minimum_rendered_text_items=16,
        maximum_aspect_ratio=6.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-v2-dev-treemap-standard",
        split="development",
        prompt="""Create a Mermaid Treemap that consumes every non-cycling named hierarchy color exactly once. Use the named wrapper root `Capacity portfolio`; remember that this wrapper owns the first visible color. Add sequential direct groups `Treemap group 01`, `Treemap group 02`, and so on through the last child group that remains colored before cycling. Give each group exactly one matching leaf `Leaf 01`, `Leaf 02`, and so on, with descending positive integer values. Use the standard palette and keep every leaf label visible.""",
        family="treemap",
        declarations=("treemap-beta",),
        colorset="colorset1",
        required_terms=("Capacity portfolio",)
        + tuple(f"Treemap group {index:02d}" for index in range(1, 12))
        + tuple(f"Leaf {index:02d}" for index in range(1, 12)),
        patterns=tuple(
            rf"\"Treemap group {index:02d}\"" for index in range(1, 12)
        )
        + tuple(rf"\"Leaf {index:02d}\"\s*:" for index in range(1, 12)),
        forbidden_patterns=(r"Treemap group 12", r"Leaf 12"),
        visible_terms=("Leaf 01", "Leaf 06", "Leaf 11"),
        minimum_rendered_text_items=23,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("primary",),
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-v2-dev-kanban-extended",
        split="development",
        prompt="""Create a Mermaid Kanban board that consumes every column color Mermaid 11.16.0 can reach before its generated section rules stop. Name columns sequentially `Kanban slot 01`, `Kanban slot 02`, and so on through the last reachable colored column. Put exactly one matching task `Work 01`, `Work 02`, and so on in each column. Do not add an uncolored overflow column. Use the extended full-color palette.""",
        family="kanban",
        declarations=("kanban",),
        colorset="colorset2",
        required_terms=tuple(f"Kanban slot {index:02d}" for index in range(1, 11))
        + tuple(f"Work {index:02d}" for index in range(1, 11)),
        patterns=tuple(rf"Kanban slot {index:02d}" for index in range(1, 11)),
        forbidden_patterns=(r"Kanban slot 11", r"Work 11"),
        visible_terms=("Kanban slot 01", "Kanban slot 05", "Kanban slot 10", "Work 10"),
        minimum_rendered_text_items=20,
        maximum_aspect_ratio=24.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
)


MAX_CAPACITY_V2_HOLDOUT_TASKS = (
    TaskSpec(
        task_id="capacity-v2-holdout-timeline-extended",
        split="holdout",
        prompt="""Create a Mermaid Timeline that consumes every section color exactly once before cycling. Name sections sequentially `Timeline slot 01`, `Timeline slot 02`, and so on through Mermaid 11.16.0's final distinct section slot. Give each section exactly one matching dated event `Event 01`, `Event 02`, and so on, using consecutive ISO dates beginning 2040-01-01. Stop before the palette cycles and use the extended full-color palette.""",
        family="timeline",
        declarations=("timeline",),
        colorset="colorset2",
        required_terms=tuple(f"Timeline slot {index:02d}" for index in range(1, 13))
        + tuple(f"Event {index:02d}" for index in range(1, 13)),
        patterns=tuple(
            rf"^\s*section\s+Timeline slot {index:02d}\s*$"
            for index in range(1, 13)
        ),
        forbidden_patterns=(r"Timeline slot 13", r"Event 13"),
        visible_terms=("Timeline slot 01", "Timeline slot 06", "Timeline slot 12", "Event 12"),
        minimum_rendered_text_items=24,
        maximum_aspect_ratio=10.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-v2-holdout-pie-extended",
        split="holdout",
        prompt="""Create a Mermaid Pie chart that consumes every slice color exactly once before cycling. Name slices sequentially `Pie slot 01`, `Pie slot 02`, and so on through Mermaid 11.16.0's final distinct slice slot. Assign descending positive integer values, show the data, stop before the palette cycles, and use the extended full-color palette.""",
        family="pie",
        declarations=("pie",),
        colorset="colorset2",
        required_terms=tuple(f"Pie slot {index:02d}" for index in range(1, 13)),
        patterns=tuple(
            rf"[\"']Pie slot {index:02d}[\"']\s*:\s*\d+"
            for index in range(1, 13)
        ),
        forbidden_patterns=(r"Pie slot 13",),
        visible_terms=("Pie slot 01", "Pie slot 06", "Pie slot 12"),
        minimum_rendered_text_items=24,
        maximum_aspect_ratio=4.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.05,
    ),
    TaskSpec(
        task_id="capacity-v2-holdout-venn-extended",
        split="holdout",
        prompt="""Create a Mermaid Venn diagram that consumes every distinct set color exactly once before cycling. Declare independent sets with stable IDs `S01`, `S02`, and so on and labels `Venn set 01`, `Venn set 02`, and so on through Mermaid 11.16.0's final distinct set slot. Give them descending positive sizes, declare no intersections, stop before the palette cycles, and use the extended full-color palette.""",
        family="venn",
        declarations=("venn-beta",),
        colorset="colorset2",
        required_terms=tuple(f"S{index:02d}" for index in range(1, 9))
        + tuple(f"Venn set {index:02d}" for index in range(1, 9)),
        patterns=tuple(
            rf"^\s*set\s+S{index:02d}\[\"Venn set {index:02d}\"\]\s*:\s*\d+"
            for index in range(1, 9)
        ),
        forbidden_patterns=(r"S09", r"Venn set 09"),
        visible_terms=("Venn set 01", "Venn set 04", "Venn set 08"),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.002,
    ),
)


# Every v2 holdout below has already been opened and reported. Reclassify those
# cases as development evidence for v3; the new holdout uses disjoint families,
# task identities, labels, and facts and remains sealed until a winner is frozen.
MAX_CAPACITY_V3_DEVELOPMENT_TASKS = (
    MAX_CAPACITY_DEVELOPMENT_TASKS
    + MAX_CAPACITY_V2_DEVELOPMENT_TASKS
    + tuple(
        replace(
            spec,
            task_id=spec.task_id.replace(
                "capacity-v2-holdout-", "capacity-v3-dev-exposed-"
            ),
            split="development",
        )
        for spec in MAX_CAPACITY_V2_HOLDOUT_TASKS
    )
)


MAX_CAPACITY_V3_HOLDOUT_TASKS = (
    TaskSpec(
        task_id="capacity-v3-holdout-sankey-extended",
        split="holdout",
        prompt="""Create a Mermaid Sankey diagram that consumes every configured node color exactly once before cycling. Build one weighted chain. Name its nodes sequentially `Transfer node 01`, `Transfer node 02`, and so on, stopping at Mermaid 11.16.0's final distinct Sankey node slot. Use descending positive integer weights, keep every node visible, add no overflow node, and use the extended full-color palette.""",
        family="sankey",
        declarations=("sankey", "sankey-beta"),
        colorset="colorset2",
        required_terms=tuple(f"Transfer node {index:02d}" for index in range(1, 9))
        + ("80", "70", "60", "50", "40", "30", "20"),
        patterns=tuple(
            rf"Transfer node {index:02d}\s*,\s*Transfer node {index + 1:02d}\s*,\s*{90 - index * 10}(?:\.0+)?\b"
            for index in range(1, 8)
        ),
        forbidden_patterns=(r"Transfer node 09",),
        visible_terms=(
            "Transfer node 01",
            "Transfer node 04",
            "Transfer node 08",
        ),
        minimum_rendered_text_items=8,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-v3-holdout-xy-standard-boundary",
        split="holdout",
        prompt="""Create a Mermaid XY chart titled `Standard plot boundary`. Use x-axis labels `A`, `B`, `C`, and `D`, and a y-axis labeled `Score` from 0 through 12. Consume every distinct standard plot color once, then add exactly one boundary plot that demonstrates the first color cycle. Alternate bar and line plots starting with bar. Use these arrays in order: `[1,2,3,4]`, `[2,3,4,5]`, `[3,4,5,6]`, `[4,5,6,7]`, `[5,6,7,8]`, and `[6,7,8,9]`. Add no other plot and use the standard palette.""",
        family="xyChart",
        declarations=("xychart", "xychart-beta"),
        colorset="colorset1",
        required_terms=("Standard plot boundary", "A", "B", "C", "D", "Score"),
        patterns=(
            r"^\s*bar\s*\[\s*1\s*,\s*2\s*,\s*3\s*,\s*4\s*\]",
            r"^\s*line\s*\[\s*2\s*,\s*3\s*,\s*4\s*,\s*5\s*\]",
            r"^\s*bar\s*\[\s*3\s*,\s*4\s*,\s*5\s*,\s*6\s*\]",
            r"^\s*line\s*\[\s*4\s*,\s*5\s*,\s*6\s*,\s*7\s*\]",
            r"^\s*bar\s*\[\s*5\s*,\s*6\s*,\s*7\s*,\s*8\s*\]",
            r"^\s*line\s*\[\s*6\s*,\s*7\s*,\s*8\s*,\s*9\s*\]",
        ),
        forbidden_patterns=(r"^\s*(?:bar|line)\s*\[\s*7\s*,",),
        visible_terms=("Standard plot boundary", "A", "D", "Score"),
        minimum_rendered_text_items=7,
        maximum_aspect_ratio=5.0,
        required_visual_groups=("primary",),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-v3-holdout-gantt-roles-extended",
        split="holdout",
        prompt="""Create an explicit Mermaid Gantt diagram titled `Release role matrix` with date format `YYYY-MM-DD`. Under section `Roles`, include exactly these six one-day tasks in order: `Queued work` is normal on 2044-02-01; `Running work` is active on 2044-02-02; `Finished work` is done on 2044-02-03; `Blocking work` is critical on 2044-02-04; `Running blocker` is active and critical on 2044-02-05; `Finished blocker` is done and critical on 2044-02-06. Give every task a stable lowercase underscore ID derived from its label. Preserve every semantic status and use the extended full-color palette visibly.""",
        family="gantt",
        declarations=("gantt",),
        colorset="colorset2",
        required_terms=(
            "Release role matrix",
            "Roles",
            "Queued work",
            "Running work",
            "Finished work",
            "Blocking work",
            "Running blocker",
            "Finished blocker",
            "2044-02-01",
            "2044-02-02",
            "2044-02-03",
            "2044-02-04",
            "2044-02-05",
            "2044-02-06",
            "queued_work",
            "running_work",
            "finished_work",
            "blocking_work",
            "running_blocker",
            "finished_blocker",
        ),
        patterns=(
            r"Queued work\s*:\s*queued_work\s*,\s*2044-02-01\s*,\s*1d",
            r"Running work\s*:\s*active\s*,\s*running_work\s*,\s*2044-02-02\s*,\s*1d",
            r"Finished work\s*:\s*done\s*,\s*finished_work\s*,\s*2044-02-03\s*,\s*1d",
            r"Blocking work\s*:\s*crit\s*,\s*blocking_work\s*,\s*2044-02-04\s*,\s*1d",
            r"Running blocker\s*:\s*crit\s*,\s*active\s*,\s*running_blocker\s*,\s*2044-02-05\s*,\s*1d",
            r"Finished blocker\s*:\s*crit\s*,\s*done\s*,\s*finished_blocker\s*,\s*2044-02-06\s*,\s*1d",
        ),
        visible_terms=(
            "Queued work",
            "Running work",
            "Finished work",
            "Blocking work",
            "Running blocker",
            "Finished blocker",
        ),
        minimum_rendered_text_items=10,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success"),
        minimum_visible_colors=3,
        minimum_palette_ratio=0.02,
    ),
)


# The v3 holdout exposed one skill gap and two verifier-contract gaps. Preserve
# the opened cases as v4 development evidence, with the Sankey weights made
# explicit so its exact-value oracle matches the task. The v4 holdout remains
# disjoint by exercising the nine semantic classes through three new grammars.
MAX_CAPACITY_V4_EXPOSED_PROMPTS = {
    "sankey": """Create a Mermaid Sankey diagram that consumes every configured node color exactly once before cycling. Build one weighted chain. Name its nodes sequentially `Transfer node 01`, `Transfer node 02`, and so on, stopping at Mermaid 11.16.0's final distinct Sankey node slot. Use these descending integer link weights in order: `80`, `70`, `60`, `50`, `40`, `30`, `20`. Keep every node visible, add no overflow node, and use the extended full-color palette.""",
}


MAX_CAPACITY_V4_DEVELOPMENT_TASKS = (
    MAX_CAPACITY_V3_DEVELOPMENT_TASKS
    + tuple(
        replace(
            spec,
            task_id=spec.task_id.replace(
                "capacity-v3-holdout-", "capacity-v4-dev-exposed-"
            ),
            split="development",
            prompt=MAX_CAPACITY_V4_EXPOSED_PROMPTS.get(spec.family, spec.prompt),
        )
        for spec in MAX_CAPACITY_V3_HOLDOUT_TASKS
    )
)


SEMANTIC_CLASS_ROLES = (
    "csPrimary",
    "csAccent",
    "csMuted",
    "csCritical",
    "csWarning",
    "csSuccess",
    "csInfo",
    "csSpecial",
    "csNeutral",
)


MAX_CAPACITY_V4_HOLDOUT_TASKS = (
    TaskSpec(
        task_id="capacity-v4-holdout-flowchart-semantic-extended",
        split="holdout",
        prompt="""Create a left-to-right Mermaid flowchart that exercises every semantic palette role exactly once in canonical order. Use stable node IDs `F01`, `F02`, and so on through the last role, with matching labels `Pipeline checkpoint 01`, `Pipeline checkpoint 02`, and so on. Connect them as one directed chain, add no overflow node, and use the extended full-color palette.""",
        family="flowchart",
        declarations=("flowchart", "graph"),
        colorset="colorset2",
        required_terms=tuple(f"F{index:02d}" for index in range(1, 10))
        + tuple(f"Pipeline checkpoint {index:02d}" for index in range(1, 10))
        + SEMANTIC_CLASS_ROLES,
        patterns=tuple(
            rf"(?:F{index:02d}[^\n]*:::\s*{role}|^\s*class\s+F{index:02d}\s+{role}\s*$)"
            for index, role in enumerate(SEMANTIC_CLASS_ROLES, start=1)
        ),
        forbidden_patterns=(r"F10", r"Pipeline checkpoint 10"),
        minimum_arrow_count=8,
        visible_terms=(
            "Pipeline checkpoint 01",
            "Pipeline checkpoint 05",
            "Pipeline checkpoint 09",
        ),
        minimum_rendered_text_items=9,
        maximum_aspect_ratio=16.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-v4-holdout-class-semantic-extended",
        split="holdout",
        prompt="""Create a Mermaid class diagram directed left to right that exercises every semantic palette role exactly once in canonical order. Declare stable classes `ServiceRole01`, `ServiceRole02`, and so on through the last role. Connect consecutive classes with directed associations, assign one role per class, add no overflow class, and use the extended full-color palette.""",
        family="classDiagram",
        declarations=("classDiagram",),
        colorset="colorset2",
        required_terms=tuple(f"ServiceRole{index:02d}" for index in range(1, 10))
        + SEMANTIC_CLASS_ROLES,
        patterns=tuple(
            rf"^\s*class\s+ServiceRole{index:02d}\s+{role}\s*$"
            for index, role in enumerate(SEMANTIC_CLASS_ROLES, start=1)
        ),
        forbidden_patterns=(r"ServiceRole10",),
        minimum_arrow_count=8,
        visible_terms=("ServiceRole01", "ServiceRole05", "ServiceRole09"),
        minimum_rendered_text_items=9,
        maximum_aspect_ratio=16.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-v4-holdout-block-semantic-extended",
        split="holdout",
        prompt="""Create a Mermaid block diagram with three columns that exercises every semantic palette role exactly once in canonical order. Use stable block IDs `B01`, `B02`, and so on through the last role, with matching labels `Delivery tile 01`, `Delivery tile 02`, and so on. Lay them out as three complete rows, connect each row left to right, assign one role per block, add no overflow block, and use the extended full-color palette.""",
        family="block",
        declarations=("block", "block-beta"),
        colorset="colorset2",
        required_terms=tuple(f"B{index:02d}" for index in range(1, 10))
        + tuple(f"Delivery tile {index:02d}" for index in range(1, 10))
        + SEMANTIC_CLASS_ROLES,
        patterns=tuple(
            rf"^\s*class\s+B{index:02d}\s+{role}\s*$"
            for index, role in enumerate(SEMANTIC_CLASS_ROLES, start=1)
        ),
        forbidden_patterns=(r"B10", r"Delivery tile 10"),
        minimum_arrow_count=6,
        visible_terms=("Delivery tile 01", "Delivery tile 05", "Delivery tile 09"),
        minimum_rendered_text_items=9,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
)


# V4 exposed grammar-specific assignment rules and overly narrow aspect-ratio
# contracts. Reopen those cases as corrected development tasks. V5 seals three
# new semantic-class families that have never appeared in a capacity holdout.
MAX_CAPACITY_V5_EXPOSED_OVERRIDES = {
    "flowchart": {
        "prompt": """Create a compact top-to-bottom Mermaid flowchart that exercises every semantic palette role exactly once in canonical order. Use stable node IDs `F01`, `F02`, and so on through the last role, with matching labels `Pipeline checkpoint 01`, `Pipeline checkpoint 02`, and so on. Attach each role inline with Mermaid's `:::` syntax, connect the nodes as one directed chain, add no overflow node, and use the extended full-color palette.""",
        "patterns": tuple(
            rf"F{index:02d}[^\n]*:::\s*{role}"
            for index, role in enumerate(SEMANTIC_CLASS_ROLES, start=1)
        ),
        "maximum_aspect_ratio": 8.0,
    },
    "classDiagram": {
        "prompt": """Create a compact top-to-bottom Mermaid class diagram that exercises every semantic palette role exactly once in canonical order. Declare stable classes `ServiceRole01`, `ServiceRole02`, and so on through the last role. Attach each role inline to its class declaration with `:::`, connect consecutive classes with directed associations, add no overflow class, and use the extended full-color palette.""",
        "patterns": tuple(
            rf"^\s*class\s+ServiceRole{index:02d}:::\s*{role}\s*$"
            for index, role in enumerate(SEMANTIC_CLASS_ROLES, start=1)
        ),
        "maximum_aspect_ratio": 8.0,
    },
    "block": {
        "prompt": """Create a Mermaid block diagram with three columns that exercises every semantic palette role exactly once in canonical order. Use stable block IDs `B01`, `B02`, and so on through the last role, with matching labels `Delivery tile 01`, `Delivery tile 02`, and so on. Lay them out as three complete rows, connect each row left to right, and assign roles with separate `class ID csRole` statements; do not use inline `:::` styling. Add no overflow block and use the extended full-color palette.""",
        "patterns": tuple(
            rf"^\s*class\s+B{index:02d}\s+{role}\s*$"
            for index, role in enumerate(SEMANTIC_CLASS_ROLES, start=1)
        ),
        "maximum_aspect_ratio": 8.0,
    },
}


MAX_CAPACITY_V5_DEVELOPMENT_TASKS = (
    MAX_CAPACITY_V4_DEVELOPMENT_TASKS
    + tuple(
        replace(
            spec,
            task_id=spec.task_id.replace(
                "capacity-v4-holdout-", "capacity-v5-dev-exposed-"
            ),
            split="development",
            **MAX_CAPACITY_V5_EXPOSED_OVERRIDES[spec.family],
        )
        for spec in MAX_CAPACITY_V4_HOLDOUT_TASKS
    )
)


MAX_CAPACITY_V5_HOLDOUT_TASKS = (
    TaskSpec(
        task_id="capacity-v5-holdout-swimlane-semantic-extended",
        split="holdout",
        prompt="""Create a Mermaid Swimlane diagram that exercises every semantic palette role exactly once in canonical order. Use three lanes named `Discovery lane`, `Delivery lane`, and `Assurance lane`. Use stable node IDs `W01`, `W02`, and so on through the last role, with matching labels `Work checkpoint 01`, `Work checkpoint 02`, and so on. Put three consecutive nodes in each lane, attach roles inline with `:::`, connect all nodes as one directed chain, add no overflow node, and use the extended full-color palette.""",
        family="swimlane",
        declarations=("swimlane-beta",),
        colorset="colorset2",
        required_terms=("Discovery lane", "Delivery lane", "Assurance lane")
        + tuple(f"W{index:02d}" for index in range(1, 10))
        + tuple(f"Work checkpoint {index:02d}" for index in range(1, 10))
        + SEMANTIC_CLASS_ROLES,
        patterns=tuple(
            rf"W{index:02d}[^\n]*:::\s*{role}"
            for index, role in enumerate(SEMANTIC_CLASS_ROLES, start=1)
        )
        + (
            r"^\s*subgraph\s+\w+\s*\[Discovery lane\]\s*$",
            r"^\s*subgraph\s+\w+\s*\[Delivery lane\]\s*$",
            r"^\s*subgraph\s+\w+\s*\[Assurance lane\]\s*$",
        ),
        forbidden_patterns=(r"W10", r"Work checkpoint 10"),
        minimum_arrow_count=8,
        visible_terms=(
            "Discovery lane",
            "Work checkpoint 01",
            "Work checkpoint 05",
            "Work checkpoint 09",
        ),
        minimum_rendered_text_items=12,
        maximum_aspect_ratio=32.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-v5-holdout-state-semantic-extended",
        split="holdout",
        prompt="""Create a compact top-to-bottom Mermaid state diagram that exercises every semantic palette role exactly once in canonical order. Use stable state IDs `LifecycleState01`, `LifecycleState02`, and so on through the last role. Connect consecutive states as one directed chain, assign roles with separate `class ID csRole` statements, add no overflow state, and use the extended full-color palette.""",
        family="stateDiagram",
        declarations=("stateDiagram", "stateDiagram-v2"),
        colorset="colorset2",
        required_terms=tuple(f"LifecycleState{index:02d}" for index in range(1, 10))
        + SEMANTIC_CLASS_ROLES,
        patterns=tuple(
            rf"^\s*class\s+LifecycleState{index:02d}\s+{role}\s*$"
            for index, role in enumerate(SEMANTIC_CLASS_ROLES, start=1)
        ),
        forbidden_patterns=(r"LifecycleState10",),
        minimum_arrow_count=8,
        visible_terms=("LifecycleState01", "LifecycleState05", "LifecycleState09"),
        minimum_rendered_text_items=9,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
    TaskSpec(
        task_id="capacity-v5-holdout-er-semantic-extended",
        split="holdout",
        prompt="""Create a Mermaid ER diagram that exercises every semantic palette role exactly once in canonical order. Use stable entity IDs `DOMAIN_01`, `DOMAIN_02`, and so on through the last role. Connect each consecutive pair with an exactly-one to zero-or-many relationship labeled `feeds`, assign roles with separate `class ID csRole` statements, add no overflow entity, and use the extended full-color palette.""",
        family="erDiagram",
        declarations=("erDiagram",),
        colorset="colorset2",
        required_terms=tuple(f"DOMAIN_{index:02d}" for index in range(1, 10))
        + ("feeds",)
        + SEMANTIC_CLASS_ROLES,
        patterns=tuple(
            rf"^\s*class\s+DOMAIN_{index:02d}\s+{role}\s*$"
            for index, role in enumerate(SEMANTIC_CLASS_ROLES, start=1)
        )
        + tuple(
            rf"^\s*DOMAIN_{index:02d}\s+\|\|\s*--\s*o\{{\s+DOMAIN_{index + 1:02d}\s*:\s*feeds\s*$"
            for index in range(1, 9)
        ),
        forbidden_patterns=(r"DOMAIN_10",),
        visible_terms=("DOMAIN_01", "DOMAIN_05", "DOMAIN_09", "feeds"),
        minimum_rendered_text_items=17,
        maximum_aspect_ratio=8.0,
        required_visual_groups=("accent", "warning", "success", "special"),
        minimum_visible_colors=4,
        minimum_palette_ratio=0.01,
    ),
)


TASK_PROFILES = {
    "visible-v6": TASKS,
    "pareto-v1": PARETO_TASKS,
    "pareto-v2": PARETO_V2_TASKS,
    "pareto-final": tuple(spec for spec in PARETO_V2_TASKS if spec.split == "development")
    + PARETO_FINAL_HOLDOUT_TASKS,
    "pareto-sealed": tuple(spec for spec in PARETO_V2_TASKS if spec.split == "development")
    + PARETO_SEALED_HOLDOUT_TASKS,
    "hard-discovery": HARD_DEVELOPMENT_TASKS + PARETO_SEALED_HOLDOUT_TASKS[:1],
    "hard-final": HARD_DEVELOPMENT_TASKS + HARD_SEALED_HOLDOUT_TASKS,
    "hard-final-v2": HARD_DEVELOPMENT_TASKS + HARD_SEALED_HOLDOUT_V2_TASKS,
    "hard-final-v3": HARD_DEVELOPMENT_TASKS + HARD_SEALED_HOLDOUT_V3_TASKS,
    "hard-final-v4": HARD_DEVELOPMENT_TASKS + HARD_SEALED_HOLDOUT_V4_TASKS,
    "hard-final-v5": HARD_VISIBILITY_DEVELOPMENT_TASKS + HARD_SEALED_HOLDOUT_V5_TASKS,
    "hard-final-v6": HARD_VISIBILITY_DEVELOPMENT_TASKS + HARD_SEALED_HOLDOUT_V6_TASKS,
    "hard-visibility-smoke": HARD_VISIBILITY_DEVELOPMENT_TASKS[-1:] + PARETO_SEALED_HOLDOUT_TASKS[:1],
    "hard-visibility-discovery": HARD_VISIBILITY_DEVELOPMENT_TASKS + PARETO_SEALED_HOLDOUT_TASKS[:1],
    "max-capacity-v1": MAX_CAPACITY_DEVELOPMENT_TASKS + MAX_CAPACITY_HOLDOUT_TASKS,
    "max-capacity-v2": MAX_CAPACITY_V2_DEVELOPMENT_TASKS + MAX_CAPACITY_V2_HOLDOUT_TASKS,
    "max-capacity-v3-pareto": MAX_CAPACITY_V3_DEVELOPMENT_TASKS
    + MAX_CAPACITY_V3_HOLDOUT_TASKS,
    "max-capacity-v4-pareto": MAX_CAPACITY_V4_DEVELOPMENT_TASKS
    + MAX_CAPACITY_V4_HOLDOUT_TASKS,
    "max-capacity-v5-pareto": MAX_CAPACITY_V5_DEVELOPMENT_TASKS
    + MAX_CAPACITY_V5_HOLDOUT_TASKS,
}


VERIFY_SCRIPT = r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from visual_palette import COLOR_GROUPS, COLORSET_GROUPS, evaluate_visual_palette, make_counterfactual_source


STANDARD_TOKENS = set(COLOR_GROUPS["primary"])
EXTENDED_TOKENS = {
    color
    for group in COLORSET_GROUPS["colorset2"]
    for color in COLOR_GROUPS[group]
}


def declaration(source: str) -> str:
    lines = source.splitlines()
    index = 0
    if lines and lines[0].strip() == "---":
        index = 1
        while index < len(lines) and lines[index].strip() != "---":
            index += 1
        index += 1
    for line in lines[index:]:
        stripped = line.strip()
        if stripped and not stripped.startswith("%%"):
            return stripped.split()[0].rstrip(":")
    return ""


def error_svg(path: Path) -> bool:
    root = ET.parse(path).getroot()
    if root.get("aria-roledescription") == "error":
        return True
    return any(
        {"error-icon", "error-text"} & set((node.get("class") or "").casefold().split())
        for node in root.iter()
    )


def rendered_svg_facts(path: Path) -> dict[str, object]:
    root = ET.parse(path).getroot()
    fragments = []

    def collect(node: ET.Element) -> None:
        tag = node.tag.rsplit("}", 1)[-1].casefold()
        if tag in {"style", "script", "metadata"}:
            return
        if node.text and node.text.strip():
            fragments.append(" ".join(node.text.split()))
        for child in node:
            collect(child)
            if child.tail and child.tail.strip():
                fragments.append(" ".join(child.tail.split()))

    collect(root)
    view_box = root.get("viewBox", "").replace(",", " ").split()
    aspect_ratio = None
    if len(view_box) == 4:
        width = abs(float(view_box[2]))
        height = abs(float(view_box[3]))
        if width > 0 and height > 0:
            aspect_ratio = max(width / height, height / width)
    return {
        "text": " ".join(fragments),
        "textItems": len(fragments),
        "aspectRatio": aspect_ratio,
    }


def render_mermaid(
    source_path: Path,
    output_path: Path,
    workspace: Path,
    log_dir: Path,
    label: str,
    *,
    transparent: bool = False,
) -> bool:
    npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
    command = [
        npx,
        "-y",
        "@mermaid-js/mermaid-cli@11.16.0",
        "-i",
        str(source_path),
        "-o",
        str(output_path),
    ]
    if transparent:
        command.extend(["-b", "transparent"])
    stdout_parts = []
    stderr_parts = []
    for attempt in range(1, 3):
        try:
            completed = subprocess.run(
                command,
                cwd=workspace,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=240,
                check=False,
            )
            stdout_parts.append(f"=== attempt {attempt} ===\n{completed.stdout}")
            stderr_parts.append(f"=== attempt {attempt} ===\n{completed.stderr}")
            if completed.returncode == 0 and output_path.is_file() and output_path.stat().st_size > 0:
                (log_dir / f"{label}-stdout.txt").write_text("\n".join(stdout_parts), encoding="utf-8")
                (log_dir / f"{label}-stderr.txt").write_text("\n".join(stderr_parts), encoding="utf-8")
                return True
        except subprocess.TimeoutExpired as exc:
            stdout_parts.append(f"=== attempt {attempt} timeout ===\n{exc.stdout or ''}")
            stderr_parts.append(f"=== attempt {attempt} timeout ===\n{exc.stderr or ''}")
        if attempt == 1:
            time.sleep(0.25)
    (log_dir / f"{label}-stdout.txt").write_text("\n".join(stdout_parts), encoding="utf-8")
    (log_dir / f"{label}-stderr.txt").write_text("\n".join(stderr_parts), encoding="utf-8")
    return False


def main() -> int:
    workspace = Path(os.environ.get("HARBOR_APP_DIR", Path.cwd())).resolve()
    log_dir = Path(os.environ.get("HARBOR_VERIFIER_LOG_DIR", workspace / ".harbor-verifier")).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    contract = json.loads((Path(__file__).with_name("contract.json")).read_text(encoding="utf-8"))
    source_path = workspace / "deliverables" / "diagram.mmd"
    decision_path = workspace / "deliverables" / "decision.json"
    findings = []
    source = ""
    decision = {}
    try:
        source = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        findings.append(f"source missing: {exc}")
    try:
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(f"decision metadata missing or invalid: {exc}")

    actual_declaration = declaration(source) if source else ""
    routing_ok = bool(
        actual_declaration in contract["declarations"]
        and decision.get("selectedFamily") == contract["family"]
        and str(decision.get("declaration", "")).split()[0].rstrip(":") == actual_declaration
    )
    if not routing_ok:
        findings.append(
            f"routing failed: declaration={actual_declaration!r}, family={decision.get('selectedFamily')!r}"
        )

    source_colors = {value.casefold() for value in re.findall(r"#[0-9a-fA-F]{6}", source)}
    source_palette_ok = bool(
        'theme: "base"' in source
        and f'colorset: "{contract["colorset"]}"' in source
        and decision.get("colorset") == contract["colorset"]
        and "%%{init:" not in source
    )
    if contract["colorset"] == "colorset1":
        source_palette_ok = source_palette_ok and bool(source_colors & STANDARD_TOKENS) and not bool(source_colors & EXTENDED_TOKENS)
    else:
        source_palette_ok = source_palette_ok and bool(source_colors & EXTENDED_TOKENS)
    if not source_palette_ok:
        findings.append(f"source palette failed for {contract['colorset']}")

    lowered = source.casefold()
    fidelity_findings = [
        f"missing term: {term}"
        for term in contract["requiredTerms"]
        if term.casefold() not in lowered
    ]
    for pattern in contract.get("patterns", []):
        if not re.search(pattern, source, re.IGNORECASE | re.MULTILINE):
            fidelity_findings.append(f"missing structured evidence: {pattern}")
    for pattern in contract.get("forbiddenPatterns", []):
        if re.search(pattern, source, re.IGNORECASE | re.MULTILINE):
            fidelity_findings.append(f"forbidden structured evidence: {pattern}")
    positions = [lowered.find(term.casefold()) for term in contract.get("orderedTerms", [])]
    if positions and (any(position < 0 for position in positions) or positions != sorted(positions)):
        fidelity_findings.append("ordered terms are not preserved")
    directed_relations = len(re.findall(r"(?:-->>|->>|-->|==>|-\.->)", source))
    if directed_relations < int(contract.get("minimumArrowCount", 0)):
        fidelity_findings.append("too few directed relations")
    indented = len(re.findall(r"^\s{2,}\S", source, re.MULTILINE))
    if indented < int(contract.get("minimumIndentedLines", 0)):
        fidelity_findings.append("hierarchy is not sufficiently nested")
    fidelity_ok = not fidelity_findings
    findings.extend(fidelity_findings)

    metadata_ok = bool(
        isinstance(decision.get("reason"), str)
        and decision.get("reason", "").strip()
        and set(decision) == {"selectedFamily", "declaration", "colorset", "reason"}
    )
    for pattern in contract.get("reasonPatterns", []):
        if not re.search(pattern, str(decision.get("reason", "")), re.IGNORECASE):
            metadata_ok = False
            findings.append(f"decision reason lacks required evidence: {pattern}")
    if not metadata_ok:
        findings.append("decision.json is incomplete")

    render_ok = False
    visual_fidelity_ok = False
    rendered_facts = {}
    visual_palette_ok = False
    palette_influence_ok = False
    visual_palette = {}
    counterfactual_replacements = 0
    svg_path = log_dir / "rendered.svg"
    png_path = log_dir / "rendered.png"
    counterfactual_source_path = log_dir / "counterfactual.mmd"
    counterfactual_png_path = log_dir / "counterfactual.png"
    if source:
        svg_rendered = render_mermaid(source_path, svg_path, workspace, log_dir, "renderer-svg")
        png_rendered = render_mermaid(
            source_path,
            png_path,
            workspace,
            log_dir,
            "renderer-png",
            transparent=True,
        )
        try:
            render_ok = svg_rendered and png_rendered and not error_svg(svg_path)
        except (OSError, ET.ParseError, ValueError):
            render_ok = False
        if render_ok:
            try:
                rendered_facts = rendered_svg_facts(svg_path)
                rendered_text = " ".join(str(rendered_facts.get("text", "")).split()).casefold()
                visual_findings = [
                    f"rendered SVG is missing visible term: {term}"
                    for term in contract.get("visibleTerms", [])
                    if " ".join(term.split()).casefold() not in rendered_text
                ]
                minimum_text_items = int(contract.get("minimumRenderedTextItems", 0))
                if int(rendered_facts.get("textItems", 0)) < minimum_text_items:
                    visual_findings.append(
                        f"rendered SVG has too few text items: {rendered_facts.get('textItems', 0)} < {minimum_text_items}"
                    )
                maximum_aspect_ratio = float(contract.get("maximumAspectRatio", 0.0))
                aspect_ratio = rendered_facts.get("aspectRatio")
                if maximum_aspect_ratio > 0 and (
                    aspect_ratio is None or float(aspect_ratio) > maximum_aspect_ratio
                ):
                    visual_findings.append(
                        f"rendered SVG aspect ratio is invalid or excessive: {aspect_ratio} > {maximum_aspect_ratio}"
                    )
                visual_fidelity_ok = not visual_findings
                findings.extend(visual_findings)
            except (OSError, ET.ParseError, TypeError, ValueError) as exc:
                findings.append(f"rendered SVG visual-fidelity analysis failed: {exc}")
            counterfactual_source, counterfactual_replacements = make_counterfactual_source(
                source,
                contract["colorset"],
            )
            counterfactual_source_path.write_text(counterfactual_source, encoding="utf-8")
            counterfactual_rendered = bool(
                counterfactual_replacements
                and render_mermaid(
                    counterfactual_source_path,
                    counterfactual_png_path,
                    workspace,
                    log_dir,
                    "renderer-counterfactual",
                    transparent=True,
                )
            )
            if counterfactual_rendered:
                try:
                    visual_palette = evaluate_visual_palette(
                        png_path,
                        counterfactual_png_path,
                        contract["colorset"],
                        contract["visualPalette"],
                    )
                    visual_palette_ok = bool(visual_palette.get("palette", {}).get("ok"))
                    palette_influence_ok = bool(visual_palette.get("influence", {}).get("ok"))
                except (OSError, ValueError) as exc:
                    findings.append(f"visual palette analysis failed: {exc}")
            else:
                findings.append("counterfactual palette render failed or replaced no signature colors")
        if not render_ok:
            findings.append(f"Mermaid {contract['mermaidVersion']} render failed")
        elif not visual_palette_ok:
            findings.append(f"rasterized SVG has insufficient visible {contract['colorset']} coverage")
        if render_ok and not palette_influence_ok:
            findings.append("palette configuration did not change enough visible rendered pixels")
    else:
        findings.append("render skipped because source is unavailable")

    palette_ok = source_palette_ok and visual_palette_ok and palette_influence_ok
    passed = routing_ok and palette_ok and render_ok and visual_fidelity_ok and fidelity_ok and metadata_ok
    rewards = {
        "reward": 1.0 if passed else 0.0,
        "routing": 1.0 if routing_ok else 0.0,
        "palette": 1.0 if palette_ok else 0.0,
        "visual_palette": 1.0 if visual_palette_ok else 0.0,
        "palette_influence": 1.0 if palette_influence_ok else 0.0,
        "render": 1.0 if render_ok else 0.0,
        "visual_fidelity": 1.0 if visual_fidelity_ok else 0.0,
        "fidelity": 1.0 if fidelity_ok else 0.0,
        "metadata": 1.0 if metadata_ok else 0.0,
    }
    result = {
        "ok": passed,
        "taskId": contract["taskId"],
        "expectedFamily": contract["family"],
        "actualDeclaration": actual_declaration,
        "expectedColorset": contract["colorset"],
        "counterfactualReplacements": counterfactual_replacements,
        "visualPalette": visual_palette,
        "renderedFacts": rendered_facts,
        "rewards": rewards,
        "findings": findings,
    }
    (log_dir / "verification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (log_dir / "reward.json").write_text(json.dumps(rewards, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
'''


TEST_SCRIPT = """#!/usr/bin/env bash
set -o pipefail
python3 \"$(dirname \"$0\")/verify.py\"
"""


TASK_TOML = """version = \"1.0\"

[metadata]

[verifier]
timeout_sec = 360.0

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 60.0
"""


INSTRUCTION_SUFFIX = """

Use the installed `mermaid` skill. Work only inside this Harbor task workspace and the installed skill; do not inspect repository paths, prior trials, test files, or network resources. The evaluator will render the source independently, so do not install packages and do not create SVG or PNG files.

Preserve every supplied label, relation, direction, order, unit, date, duration, weight, coordinate, attribute, and cardinality. Honor an explicit Mermaid type when it can represent the supplied facts truthfully. If it cannot, choose the closest truthful family and explain the conflict in `reason`. Otherwise choose the family that best communicates the relationship the viewer must understand. Use colorset1 unless this request explicitly asks for extended/full-color/multicolor styling, in which case use colorset2. Apply the palette with the bundled styler and complete its check successfully. The palette must affect visible diagram geometry; declaring unused color variables is not sufficient.

Create exactly these two non-empty files:

- `deliverables/diagram.mmd`
- `deliverables/decision.json`

`decision.json` must contain exactly one JSON object with `selectedFamily`, `declaration`, `colorset`, and a concise non-empty `reason`. Copy the canonical family ID from the skill manifest, record only the first declaration token, and record exactly `colorset1` or `colorset2`. Treat the installed skill as read-only.
"""


def sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        relative = path.relative_to(root).as_posix().encode()
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def write_task(root: Path, spec: TaskSpec) -> None:
    task_root = root / spec.split / spec.task_id
    (task_root / "environment").mkdir(parents=True)
    (task_root / "tests").mkdir(parents=True)
    (task_root / "environment" / ".gitkeep").write_text("", encoding="utf-8")
    (task_root / "task.toml").write_text(TASK_TOML, encoding="utf-8", newline="\n")
    (task_root / "instruction.md").write_text(spec.prompt.strip() + INSTRUCTION_SUFFIX, encoding="utf-8", newline="\n")
    contract = {
        "schemaVersion": 3,
        "taskId": spec.task_id,
        "family": spec.family,
        "declarations": list(spec.declarations),
        "colorset": spec.colorset,
        "requiredTerms": list(spec.required_terms),
        "patterns": list(spec.patterns),
        "forbiddenPatterns": list(spec.forbidden_patterns),
        "orderedTerms": list(spec.ordered_terms),
        "minimumArrowCount": spec.minimum_arrow_count,
        "minimumIndentedLines": spec.minimum_indented_lines,
        "visibleTerms": list(spec.visible_terms),
        "minimumRenderedTextItems": spec.minimum_rendered_text_items,
        "maximumAspectRatio": spec.maximum_aspect_ratio,
        "reasonPatterns": list(spec.reason_patterns),
        "mermaidVersion": MERMAID_VERSION,
        "visualPalette": {
            "requiredGroups": list(spec.required_visual_groups),
            "minDistinctColors": spec.minimum_visible_colors,
            "minPixelsPerColor": 24.0,
            "minPaletteEffectivePixels": 64.0,
            "minPaletteCoverageRatio": spec.minimum_palette_ratio,
            "minInfluenceEffectivePixels": 32.0,
            "minInfluenceRatio": 0.0005,
        },
    }
    (task_root / "tests" / "contract.json").write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    verifier = task_root / "tests" / "verify.py"
    verifier.write_text(VERIFY_SCRIPT, encoding="utf-8", newline="\n")
    visual_palette_module = Path(__file__).with_name("visual_palette.py").read_text(encoding="utf-8")
    (task_root / "tests" / "visual_palette.py").write_text(
        visual_palette_module,
        encoding="utf-8",
        newline="\n",
    )
    test_script = task_root / "tests" / "test.sh"
    test_script.write_text(TEST_SCRIPT, encoding="utf-8", newline="\n")
    os.chmod(verifier, 0o755)
    os.chmod(test_script, 0o755)


def quoted(value: str | Path) -> str:
    return json.dumps(Path(value).resolve().as_posix() if isinstance(value, Path) else value)


def write_job_config(
    output_root: Path,
    repo_root: Path,
    split: str,
    run_id: str,
    attempts: int,
) -> Path:
    config_path = output_root / f"{split}-job.yaml"
    job_name = f"{run_id}-{split}-luna-medium"
    config = f"""job_name: {quoted(job_name)}
jobs_dir: {quoted(output_root / 'jobs')}
n_attempts: {attempts}
n_concurrent_trials: 4
quiet: false
retry:
  max_retries: 0
environment:
  import_path: \"evaluations.mermaid.harbor_wsl_environment:WorkspaceWSLEnvironment\"
  delete: true
  cpu_enforcement_policy: ignore
  memory_enforcement_policy: ignore
  kwargs:
    shared_cache_dir: {quoted(repo_root / 'evaluations' / 'runs' / 'harbor-shared-cache')}
agents:
  - name: codex
    model_name: {quoted(MODEL)}
    skills:
      - {quoted(repo_root / 'skills' / 'mermaid')}
    kwargs:
      version: {quoted(CODEX_VERSION)}
      reasoning_effort: {quoted(REASONING_EFFORT)}
      reasoning_summary: concise
      web_search: disabled
    env:
      CODEX_FORCE_AUTH_JSON: \"true\"
datasets:
  - path: {quoted(output_root / split)}
artifacts:
  - source: \"/app/deliverables\"
    destination: \"deliverables\"
"""
    config_path.write_text(config, encoding="utf-8", newline="\n")
    return config_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_root", type=Path, help="New ignored run directory for generated Harbor inputs.")
    parser.add_argument("--run-id", required=True, help="Stable lowercase run identifier used in native job names.")
    parser.add_argument("--profile", choices=sorted(TASK_PROFILES), default="visible-v6")
    parser.add_argument("--attempts", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.attempts < 1:
        raise SystemExit("--attempts must be positive")
    tasks = TASK_PROFILES[args.profile]
    output_root = args.output_root.resolve()
    if output_root.exists() and any(output_root.iterdir()):
        raise SystemExit(f"Refusing to replace non-empty output root: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)
    repo_root = Path.cwd().resolve()
    for spec in tasks:
        write_task(output_root, spec)
    configs = {
        split: str(write_job_config(output_root, repo_root, split, args.run_id, args.attempts))
        for split in ("development", "holdout")
    }
    manifest = {
        "schemaVersion": 2,
        "runId": args.run_id,
        "profile": args.profile,
        "model": MODEL,
        "codexVersion": CODEX_VERSION,
        "reasoningEffort": REASONING_EFFORT,
        "attemptsPerTask": args.attempts,
        "mermaidVersion": MERMAID_VERSION,
        "paletteEvaluation": "raster-pixel-coverage-and-counterfactual-v2",
        "tasks": [asdict(spec) for spec in tasks],
        "datasetDigests": {
            split: sha256_tree(output_root / split) for split in ("development", "holdout")
        },
        "jobConfigs": configs,
    }
    (output_root / "generation-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({
        "outputRoot": str(output_root),
        "profile": args.profile,
        "taskCount": len(tasks),
        "developmentCount": sum(spec.split == "development" for spec in tasks),
        "holdoutCount": sum(spec.split == "holdout" for spec in tasks),
        "model": MODEL,
        "reasoningEffort": REASONING_EFFORT,
        "datasetDigests": manifest["datasetDigests"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
