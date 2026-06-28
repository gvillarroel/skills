export const video = {
  id: "agent-harnesses-explainer",
  title: "Harnesses de agentes",
  durationSeconds: 52,
  width: 1280,
  height: 720,
  shots: [
    {
      id: "s01-model-vs-harness",
      start: 0,
      duration: 9,
      headline: "Un harness no es el modelo.",
      subhead: "Es el entorno que lo hace trabajar con herramientas, reglas y pruebas.",
      labels: ["modelo", "harness", "herramientas", "memoria", "políticas", "pruebas"]
    },
    {
      id: "s02-agent-loop",
      start: 9,
      duration: 11,
      headline: "Convierte una intención en ciclos controlados.",
      subhead: "Observar, decidir, actuar y verificar se repite con trazas.",
      labels: ["observar", "decidir", "actuar", "verificar", "trazas"]
    },
    {
      id: "s03-coding-workflow",
      start: 20,
      duration: 12,
      headline: "Un harness convierte intención en patch validado.",
      subhead: "El agente usa contexto, edita, ejecuta y solo entrega después de probar.",
      labels: ["repo", "editor", "terminal", "pruebas", "patch"]
    },
    {
      id: "s04-boundaries-evidence",
      start: 32,
      duration: 11,
      headline: "El harness pone límites y deja evidencia.",
      subhead: "Bloquea acciones riesgosas y convierte cada paso en trazas evaluables.",
      labels: ["sandbox", "permisos", "trazas", "evaluación"]
    },
    {
      id: "s05-closing-formula",
      start: 43,
      duration: 9,
      headline: "Modelo + harness = ayudante operativo.",
      subhead: "El modelo razona; el harness opera, observa y verifica.",
      labels: ["modelo", "harness", "ayudante de codificación"]
    }
  ],
  transitions: [
    {
      id: "t01-harness-to-loop",
      fromScene: "s01-model-vs-harness",
      toScene: "s02-agent-loop",
      start: 8.25,
      duration: 1.5,
      family: "static anchor sweep",
      mechanic: "static-anchor-sweep",
      supportCue: "scene-exit-and-entry",
      label: "misma tarea",
      color: "#0f766e",
      secondaryColor: "#14b8a6",
      spaceColor: "#ccfbf1",
      outgoing: [1136, 352],
      bridge: [1210, 188],
      incoming: [420, 325],
      shift: [34, -12]
    },
    {
      id: "t02-loop-to-tools",
      fromScene: "s02-agent-loop",
      toScene: "s03-coding-workflow",
      start: 19.25,
      duration: 1.5,
      family: "spatial portal reveal",
      mechanic: "center-portal-reveal",
      supportCue: "blue-tool-corridor-aperture",
      label: "acción",
      color: "#2563eb",
      secondaryColor: "#38bdf8",
      spaceColor: "#dbeafe",
      outgoing: [1045, 405],
      bridge: [1168, 520],
      incoming: [160, 398],
      shift: [-30, 10]
    },
    {
      id: "t03-tools-to-boundaries",
      fromScene: "s03-coding-workflow",
      toScene: "s04-boundaries-evidence",
      start: 31.2,
      duration: 1.6,
      family: "extreme zoom reframe",
      mechanic: "extreme-zoom-reframe",
      supportCue: "zoom-through-check-to-policy",
      label: "verificar",
      color: "#dc2626",
      secondaryColor: "#f97316",
      spaceColor: "#fee2e2",
      outgoing: [1113, 462],
      bridge: [1210, 602],
      incoming: [792, 571],
      shift: [26, 14]
    },
    {
      id: "t04-evidence-to-formula",
      fromScene: "s04-boundaries-evidence",
      toScene: "s05-closing-formula",
      start: 42.25,
      duration: 1.5,
      family: "full-screen color card",
      mechanic: "full-screen-color-card",
      supportCue: "green-proof-to-white-reset",
      label: "prueba",
      color: "#16a34a",
      secondaryColor: "#22c55e",
      spaceColor: "#dcfce7",
      outgoing: [1101, 634],
      bridge: [1176, 424],
      incoming: [640, 445],
      shift: [-22, -10]
    }
  ]
};
