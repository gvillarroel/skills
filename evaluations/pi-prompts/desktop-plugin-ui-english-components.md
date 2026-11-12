Refresh our support-queue status panel to follow the loaded skill's current
component contract. The following quoted Spanish legacy copy is source material
from the old interface, not a requirement to preserve its display wording:

```json
{
  "heading": "Cola de soporte",
  "search_label": "Buscar solicitudes",
  "search_placeholder": "Escribe un ID o un asunto",
  "priority_label": "Prioridad",
  "save_action": "Guardar prioridad",
  "cancel_action": "Cancelar edición",
  "refresh_action": "Actualizar cola",
  "explain_action": "Explicar selección",
  "export_action": "Exportar CSV",
  "busy_message": "Actualizando la cola…",
  "invalid_message": "Selecciona una prioridad válida.",
  "error_message": "No se pudo actualizar. Inténtalo de nuevo.",
  "cancelled_message": "Edición cancelada; no se guardaron los cambios.",
  "empty_message": "No hay solicitudes que coincidan.",
  "success_message": "Prioridad guardada.",
  "export_tooltip": "Exporta únicamente la selección actual.",
  "panel_accessible_name": "Panel de solicitudes de soporte",
  "sample_ticket": {
    "id": "T-104",
    "title": "No puedo acceder a mi cuenta",
    "priority_code": "high",
    "priority_label": "Alta",
    "status_code": "pending",
    "status_label": "Pendiente"
  },
  "tool_name": "queue_update_priority",
  "error_code": "E_INVALID_PRIORITY"
}
```

Create exactly `ui/status-panel.html` and `ui/component-copy.json`. Make the HTML
a self-contained browser preview with synthetic local interactions: search and
selection, staged priority editing, save/cancel, refresh success/failure, and an
empty result. Include busy, invalid, error, cancelled and success feedback,
accessible names/help, a tooltip, keyboard focus and useful fallback copy. The
preview must make these states reachable without a real assistant or service.

Use the skill contract to choose the displayed copy and styling. In JSON record
`language`, the authored component/accessibility/state copy, sample display data,
and equivalent native-control and terminal/text-fallback copy. Preserve exact
source identifiers, enum codes, tool names and protocol/error codes separately
from display wording. Record local checks and remaining host limitations; keep
`host_acceptance_verified` and `task_empirical_tests_performed` false. A browser
simulation is fixture evidence, not installed-host acceptance.

Work offline with the supplied skill and normal local tools. Do not install,
use network or providers, operate accounts or installed assistant hosts, or
change host configuration. The copied `skills/desktop-plugin-ui/` bundle is read-only.
Check both completed outputs with the bundled report checker, inspect its
`passed` result and repair findings before finishing.
