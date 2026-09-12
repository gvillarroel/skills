# Naturalistic development case: mechanical and optical traditions

Use the loaded UsefulCharts-style skill to create a polished educational poster titled **From Workshops to Optical Science** from the fictional data below. This case reuses a disclosed subset of an authored development study; it is not a blind or holdout evaluation.

Compose the history as related local chapters. Let the mechanical institutions form a coherent early history and let the later optical tradition expand where shorter mechanical stories finish. Follow causal predecessors, not a common proportional calendar: keep every exact founding date visible, but unrelated institutions with similar dates need not share a row. Keep the predecessors of a merger near its successor. Avoid equal persistent columns, widely scattered final mergers and unrelated edges sharing a visible trunk. Preserve a legitimate shared junction among siblings or the parents of a stated merger.

Keep every supplied record ID, name, founding year, category, visible note and typed relationship. Retain the three supplied category colors. The empty notes deliberately leave ordinary records with a name and date; do not add a generic sentence under every institution. Make the House of Inquiry, Academy of Mechanical Arts, College of Light and Institute of Optical Physics useful landmarks, with quieter supporting names. Include at least two appropriate bundled illustrations on selected landmarks. State clearly that all history is fictional and that vertical spacing is schematic.

Create exactly `result/source.json`, `result/poster.svg`, `result/poster.html`, `result/layout.json`, `result/browser.json`, and `result/poster.png`. Open the final PNG with an image-reading tool, criticize the whole page and a dense connection group, and repair visible problems. Review composition warnings as well as geometry failures. Write a short `result/review.md` stating the largest remaining differences from the intended poster grammar; do not claim indistinguishability without evidence.

The skill directory is read-only. Write generated work only inside this workspace. Use bundled resources without network research or repository discovery. Choose the composition and implementation yourself.

```json
{
  "groups": [
    {
      "id": "g2",
      "label": "Mechanics",
      "color": "#F2C529"
    },
    {
      "id": "g3",
      "label": "Optics",
      "color": "#98BD92"
    },
    {
      "id": "g5",
      "label": "Common origins",
      "color": "#A6A18B"
    }
  ],
  "nodes": [
    {
      "id": "oral",
      "label": "Seasonal calendars",
      "group": "g5",
      "founded": 860,
      "detail": ""
    },
    {
      "id": "craft",
      "label": "Artisan knowledge",
      "group": "g5",
      "founded": 940,
      "detail": ""
    },
    {
      "id": "record",
      "label": "Written reckonings",
      "group": "g5",
      "founded": 962,
      "detail": ""
    },
    {
      "id": "instruments",
      "label": "Measures and instruments",
      "group": "g5",
      "founded": 1018,
      "detail": ""
    },
    {
      "id": "tables",
      "label": "Calendar tables",
      "group": "g5",
      "founded": 1041,
      "detail": ""
    },
    {
      "id": "natural",
      "label": "Schools of natural study",
      "group": "g5",
      "founded": 1082,
      "detail": ""
    },
    {
      "id": "chroniclers",
      "label": "Court chroniclers",
      "group": "g5",
      "founded": 1096,
      "detail": "No institutional successors"
    },
    {
      "id": "inquiry",
      "label": "THE HOUSE OF INQUIRY",
      "group": "g5",
      "founded": 1134,
      "detail": ""
    },
    {
      "id": "archive",
      "label": "The common archive",
      "group": "g5",
      "founded": 1161,
      "detail": ""
    },
    {
      "id": "makers",
      "label": "GUILD OF INSTRUMENT MAKERS",
      "group": "g2",
      "founded": 1193,
      "detail": ""
    },
    {
      "id": "brass",
      "label": "Brassworkers of Lorn",
      "group": "g2",
      "founded": 1228,
      "detail": ""
    },
    {
      "id": "water",
      "label": "Water-engine fraternity",
      "group": "g2",
      "founded": 1246,
      "detail": ""
    },
    {
      "id": "glass",
      "label": "Corven glass furnaces",
      "group": "g2",
      "founded": 1281,
      "detail": "An independent craft"
    },
    {
      "id": "scales",
      "label": "Public assay office",
      "group": "g2",
      "founded": 1267,
      "detail": ""
    },
    {
      "id": "dials",
      "label": "Alder dial-makers",
      "group": "g2",
      "founded": 1275,
      "detail": ""
    },
    {
      "id": "millwrights",
      "label": "Fellowship of millwrights",
      "group": "g2",
      "founded": 1308,
      "detail": ""
    },
    {
      "id": "pumps",
      "label": "Mine-drainage company",
      "group": "g2",
      "founded": 1322,
      "detail": "Closed after the floods"
    },
    {
      "id": "clear-glass",
      "label": "Clear-glass workshop",
      "group": "g2",
      "founded": 1314,
      "detail": ""
    },
    {
      "id": "balance",
      "label": "College of Weights",
      "group": "g2",
      "founded": 1340,
      "detail": ""
    },
    {
      "id": "clockmakers",
      "label": "Brotherhood of Clockmakers",
      "group": "g2",
      "founded": 1351,
      "detail": ""
    },
    {
      "id": "hydraulic",
      "label": "School of Hydraulic Arts",
      "group": "g2",
      "founded": 1386,
      "detail": ""
    },
    {
      "id": "glass-union",
      "label": "Union of Glassworkers",
      "group": "g2",
      "founded": 1392,
      "detail": "Furnaces join a common guild"
    },
    {
      "id": "testing",
      "label": "Bureau of Testing",
      "group": "g2",
      "founded": 1420,
      "detail": ""
    },
    {
      "id": "standards",
      "label": "Lorn Standards Office",
      "group": "g2",
      "founded": 1446,
      "detail": ""
    },
    {
      "id": "pendulum",
      "label": "The Pendulum Circle",
      "group": "g2",
      "founded": 1427,
      "detail": "An informal research society"
    },
    {
      "id": "horology",
      "label": "Royal College of Horology",
      "group": "g2",
      "founded": 1458,
      "detail": ""
    },
    {
      "id": "canals",
      "label": "Canal engineers",
      "group": "g2",
      "founded": 1462,
      "detail": ""
    },
    {
      "id": "pump-school",
      "label": "Alder Pump School",
      "group": "g2",
      "founded": 1498,
      "detail": "Disbanded in 1531"
    },
    {
      "id": "mechanical",
      "label": "ACADEMY OF MECHANICAL ARTS",
      "group": "g2",
      "founded": 1544,
      "detail": "The colleges unite"
    },
    {
      "id": "metrology",
      "label": "National Metrology Bureau",
      "group": "g2",
      "founded": 1571,
      "detail": "Two civic offices combined"
    },
    {
      "id": "engines",
      "label": "Institute of Engines",
      "group": "g2",
      "founded": 1610,
      "detail": ""
    },
    {
      "id": "precision",
      "label": "Precision Instrument Society",
      "group": "g2",
      "founded": 1628,
      "detail": "Makers and observers collaborate"
    },
    {
      "id": "engines-west",
      "label": "Western Engine Works",
      "group": "g2",
      "founded": 1691,
      "detail": "Transferred to the city in 1730"
    },
    {
      "id": "rail",
      "label": "College of Rail Engineering",
      "group": "g2",
      "founded": 1786,
      "detail": ""
    },
    {
      "id": "machine",
      "label": "Machine Research Bureau",
      "group": "g2",
      "founded": 1842,
      "detail": ""
    },
    {
      "id": "calibration",
      "label": "Central Calibration Service",
      "group": "g2",
      "founded": 1904,
      "detail": ""
    },
    {
      "id": "lenses",
      "label": "The Lens Grinders",
      "group": "g3",
      "founded": 1405,
      "detail": ""
    },
    {
      "id": "light",
      "label": "COLLEGE OF LIGHT",
      "group": "g3",
      "founded": 1491,
      "detail": "An independent school of optical craft"
    },
    {
      "id": "mirror",
      "label": "Mirror makers of Tarn",
      "group": "g3",
      "founded": 1548,
      "detail": ""
    },
    {
      "id": "refraction",
      "label": "Circle of Refraction",
      "group": "g3",
      "founded": 1577,
      "detail": ""
    },
    {
      "id": "telescope",
      "label": "Long-tube workshop",
      "group": "g3",
      "founded": 1612,
      "detail": ""
    },
    {
      "id": "glassworks",
      "label": "Tarn Glassworks",
      "group": "g3",
      "founded": 1626,
      "detail": ""
    },
    {
      "id": "camera",
      "label": "Camera-obscura school",
      "group": "g3",
      "founded": 1641,
      "detail": ""
    },
    {
      "id": "spectrum",
      "label": "The Spectrum Society",
      "group": "g3",
      "founded": 1679,
      "detail": "Light studied as a physical problem"
    },
    {
      "id": "opticians",
      "label": "Guild of Practical Opticians",
      "group": "g3",
      "founded": 1706,
      "detail": ""
    },
    {
      "id": "glass-research",
      "label": "Glass Research House",
      "group": "g3",
      "founded": 1750,
      "detail": ""
    },
    {
      "id": "silver-image",
      "label": "Silver-image experimenters",
      "group": "g3",
      "founded": 1793,
      "detail": ""
    },
    {
      "id": "wave",
      "label": "Wave Theory Seminar",
      "group": "g3",
      "founded": 1822,
      "detail": ""
    },
    {
      "id": "instrument-firm",
      "label": "Fenn Optical Instruments",
      "group": "g3",
      "founded": 1836,
      "detail": ""
    },
    {
      "id": "photographic",
      "label": "Photographic Society",
      "group": "g3",
      "founded": 1854,
      "detail": "Experimenters and manufacturers unite"
    },
    {
      "id": "optical-physics",
      "label": "Institute of Optical Physics",
      "group": "g3",
      "founded": 1888,
      "detail": ""
    },
    {
      "id": "medical-lenses",
      "label": "Medical lens makers",
      "group": "g3",
      "founded": 1896,
      "detail": ""
    },
    {
      "id": "cinema",
      "label": "Moving-image Circle",
      "group": "g3",
      "founded": 1906,
      "detail": ""
    },
    {
      "id": "color",
      "label": "Colour Laboratory",
      "group": "g3",
      "founded": 1923,
      "detail": ""
    },
    {
      "id": "laser",
      "label": "Coherent Light Laboratory",
      "group": "g3",
      "founded": 1959,
      "detail": ""
    },
    {
      "id": "microscopy",
      "label": "Centre for Microscopy",
      "group": "g3",
      "founded": 1964,
      "detail": ""
    },
    {
      "id": "moving-image",
      "label": "Institute of Moving Images",
      "group": "g3",
      "founded": 1978,
      "detail": "Teaching and colour research merge"
    },
    {
      "id": "photonics",
      "label": "Photonics Research Council",
      "group": "g3",
      "founded": 1993,
      "detail": ""
    },
    {
      "id": "imaging",
      "label": "Imaging Sciences Institute",
      "group": "g3",
      "founded": 2004,
      "detail": "A multidisciplinary institute"
    }
  ],
  "edges": [
    {
      "id": "oral-to-craft",
      "source": "oral",
      "target": "craft",
      "kind": "branch"
    },
    {
      "id": "oral-to-record",
      "source": "oral",
      "target": "record",
      "kind": "branch"
    },
    {
      "id": "craft-to-instruments",
      "source": "craft",
      "target": "instruments",
      "kind": "branch"
    },
    {
      "id": "record-to-tables",
      "source": "record",
      "target": "tables",
      "kind": "branch"
    },
    {
      "id": "instruments-to-natural",
      "source": "instruments",
      "target": "natural",
      "kind": "branch"
    },
    {
      "id": "tables-to-natural",
      "source": "tables",
      "target": "natural",
      "kind": "branch"
    },
    {
      "id": "record-to-chroniclers",
      "source": "record",
      "target": "chroniclers",
      "kind": "branch"
    },
    {
      "id": "natural-to-inquiry",
      "source": "natural",
      "target": "inquiry",
      "kind": "branch"
    },
    {
      "id": "inquiry-to-archive",
      "source": "inquiry",
      "target": "archive",
      "kind": "branch"
    },
    {
      "id": "archive-to-makers",
      "source": "archive",
      "target": "makers",
      "kind": "branch"
    },
    {
      "id": "makers-to-brass",
      "source": "makers",
      "target": "brass",
      "kind": "branch"
    },
    {
      "id": "makers-to-water",
      "source": "makers",
      "target": "water",
      "kind": "branch"
    },
    {
      "id": "makers-to-glass",
      "source": "makers",
      "target": "glass",
      "kind": "branch"
    },
    {
      "id": "brass-to-scales",
      "source": "brass",
      "target": "scales",
      "kind": "branch"
    },
    {
      "id": "brass-to-dials",
      "source": "brass",
      "target": "dials",
      "kind": "branch"
    },
    {
      "id": "water-to-millwrights",
      "source": "water",
      "target": "millwrights",
      "kind": "branch"
    },
    {
      "id": "water-to-pumps",
      "source": "water",
      "target": "pumps",
      "kind": "branch"
    },
    {
      "id": "glass-to-clear-glass",
      "source": "glass",
      "target": "clear-glass",
      "kind": "branch"
    },
    {
      "id": "scales-to-balance",
      "source": "scales",
      "target": "balance",
      "kind": "branch"
    },
    {
      "id": "dials-to-clockmakers",
      "source": "dials",
      "target": "clockmakers",
      "kind": "branch"
    },
    {
      "id": "millwrights-to-hydraulic",
      "source": "millwrights",
      "target": "hydraulic",
      "kind": "branch"
    },
    {
      "id": "clear-glass-to-glass-union",
      "source": "clear-glass",
      "target": "glass-union",
      "kind": "branch"
    },
    {
      "id": "balance-to-testing",
      "source": "balance",
      "target": "testing",
      "kind": "branch"
    },
    {
      "id": "balance-to-standards",
      "source": "balance",
      "target": "standards",
      "kind": "branch"
    },
    {
      "id": "clockmakers-to-pendulum",
      "source": "clockmakers",
      "target": "pendulum",
      "kind": "branch"
    },
    {
      "id": "clockmakers-to-horology",
      "source": "clockmakers",
      "target": "horology",
      "kind": "branch"
    },
    {
      "id": "hydraulic-to-canals",
      "source": "hydraulic",
      "target": "canals",
      "kind": "branch"
    },
    {
      "id": "hydraulic-to-pump-school",
      "source": "hydraulic",
      "target": "pump-school",
      "kind": "branch"
    },
    {
      "id": "horology-to-mechanical",
      "source": "horology",
      "target": "mechanical",
      "kind": "branch"
    },
    {
      "id": "canals-to-mechanical",
      "source": "canals",
      "target": "mechanical",
      "kind": "branch"
    },
    {
      "id": "testing-to-metrology",
      "source": "testing",
      "target": "metrology",
      "kind": "branch"
    },
    {
      "id": "standards-to-metrology",
      "source": "standards",
      "target": "metrology",
      "kind": "branch"
    },
    {
      "id": "mechanical-to-engines",
      "source": "mechanical",
      "target": "engines",
      "kind": "branch"
    },
    {
      "id": "mechanical-to-precision",
      "source": "mechanical",
      "target": "precision",
      "kind": "branch"
    },
    {
      "id": "engines-to-engines-west",
      "source": "engines",
      "target": "engines-west",
      "kind": "branch"
    },
    {
      "id": "engines-west-to-rail",
      "source": "engines-west",
      "target": "rail",
      "kind": "branch"
    },
    {
      "id": "rail-to-machine",
      "source": "rail",
      "target": "machine",
      "kind": "branch"
    },
    {
      "id": "metrology-to-calibration",
      "source": "metrology",
      "target": "calibration",
      "kind": "branch"
    },
    {
      "id": "glass-union-to-lenses",
      "source": "glass-union",
      "target": "lenses",
      "kind": "branch"
    },
    {
      "id": "lenses-to-light",
      "source": "lenses",
      "target": "light",
      "kind": "branch"
    },
    {
      "id": "light-to-mirror",
      "source": "light",
      "target": "mirror",
      "kind": "branch"
    },
    {
      "id": "light-to-refraction",
      "source": "light",
      "target": "refraction",
      "kind": "branch"
    },
    {
      "id": "light-to-telescope",
      "source": "light",
      "target": "telescope",
      "kind": "branch"
    },
    {
      "id": "mirror-to-glassworks",
      "source": "mirror",
      "target": "glassworks",
      "kind": "branch"
    },
    {
      "id": "refraction-to-camera",
      "source": "refraction",
      "target": "camera",
      "kind": "branch"
    },
    {
      "id": "refraction-to-spectrum",
      "source": "refraction",
      "target": "spectrum",
      "kind": "branch"
    },
    {
      "id": "telescope-to-opticians",
      "source": "telescope",
      "target": "opticians",
      "kind": "branch"
    },
    {
      "id": "glassworks-to-glass-research",
      "source": "glassworks",
      "target": "glass-research",
      "kind": "branch"
    },
    {
      "id": "camera-to-silver-image",
      "source": "camera",
      "target": "silver-image",
      "kind": "branch"
    },
    {
      "id": "spectrum-to-wave",
      "source": "spectrum",
      "target": "wave",
      "kind": "branch"
    },
    {
      "id": "opticians-to-instrument-firm",
      "source": "opticians",
      "target": "instrument-firm",
      "kind": "branch"
    },
    {
      "id": "silver-image-to-photographic",
      "source": "silver-image",
      "target": "photographic",
      "kind": "branch"
    },
    {
      "id": "glass-research-to-photographic",
      "source": "glass-research",
      "target": "photographic",
      "kind": "branch"
    },
    {
      "id": "wave-to-optical-physics",
      "source": "wave",
      "target": "optical-physics",
      "kind": "branch"
    },
    {
      "id": "instrument-firm-to-medical-lenses",
      "source": "instrument-firm",
      "target": "medical-lenses",
      "kind": "branch"
    },
    {
      "id": "photographic-to-cinema",
      "source": "photographic",
      "target": "cinema",
      "kind": "branch"
    },
    {
      "id": "photographic-to-color",
      "source": "photographic",
      "target": "color",
      "kind": "branch"
    },
    {
      "id": "optical-physics-to-color",
      "source": "optical-physics",
      "target": "color",
      "kind": "influence"
    },
    {
      "id": "optical-physics-to-laser",
      "source": "optical-physics",
      "target": "laser",
      "kind": "branch"
    },
    {
      "id": "medical-lenses-to-microscopy",
      "source": "medical-lenses",
      "target": "microscopy",
      "kind": "branch"
    },
    {
      "id": "cinema-to-moving-image",
      "source": "cinema",
      "target": "moving-image",
      "kind": "branch"
    },
    {
      "id": "color-to-moving-image",
      "source": "color",
      "target": "moving-image",
      "kind": "branch"
    },
    {
      "id": "laser-to-photonics",
      "source": "laser",
      "target": "photonics",
      "kind": "branch"
    },
    {
      "id": "microscopy-to-imaging",
      "source": "microscopy",
      "target": "imaging",
      "kind": "branch"
    },
    {
      "id": "color-to-imaging",
      "source": "color",
      "target": "imaging",
      "kind": "branch"
    }
  ]
}
```
