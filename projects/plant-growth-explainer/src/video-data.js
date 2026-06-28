export const video = {
  id: "plant-growth-explainer",
  title: "How Plants Grow",
  durationSeconds: 48,
  width: 1280,
  height: 720,
  shots: [
    {
      id: "s01-seed-awakens",
      start: 0,
      duration: 8,
      labels: ["seed", "water", "oxygen", "warmth", "first root"]
    },
    {
      id: "s02-roots-feed",
      start: 8,
      duration: 8,
      labels: ["roots", "water", "minerals", "anchor"]
    },
    {
      id: "s03-shoot-finds-light",
      start: 16,
      duration: 8,
      labels: ["shoot", "leaves", "light"]
    },
    {
      id: "s04-leaf-makes-sugar",
      start: 24,
      duration: 10,
      labels: ["light", "CO2", "water", "sugars", "O2"]
    },
    {
      id: "s05-growth-zones",
      start: 34,
      duration: 8,
      labels: ["xylem", "phloem", "new cells"]
    },
    {
      id: "s06-cycle-continues",
      start: 42,
      duration: 6,
      labels: ["flower", "fruit", "seeds"]
    }
  ],
  transitions: [
    { id: "t01-seed-to-roots", start: 7.2, duration: 1.2 },
    { id: "t02-roots-to-shoot", start: 15.2, duration: 1.2 },
    { id: "t03-shoot-to-leaf", start: 23.2, duration: 1.2 },
    { id: "t04-leaf-to-growth-zones", start: 33, duration: 1.2 },
    { id: "t05-growth-to-cycle", start: 41.2, duration: 1 }
  ]
};
