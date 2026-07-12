#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const here = path.dirname(fileURLToPath(import.meta.url));
const project = path.resolve(here, "..");
const dataDir = path.join(project, "artifacts", "data");
const outputDir = path.join(project, "artifacts", "documents");
const previewDir = path.join(project, "artifacts", "reviews", "workbook");
await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const categories = JSON.parse(await fs.readFile(path.join(project, "source", "categories.json"), "utf8"));
const rankedRows = JSON.parse(await fs.readFile(path.join(dataDir, "ranked-places.json"), "utf8"));
const invalidChildRows = rankedRows.filter((row) => row.children_allowed !== true);
if (invalidChildRows.length) {
  throw new Error(`Child-access gate failed for published rows: ${invalidChildRows.map((row) => row.name).join(", ")}`);
}
const rows = [...rankedRows].sort((a, b) => a.category_id.localeCompare(b.category_id) || Number(a.rank) - Number(b.rank));
const categorySummary = JSON.parse(await fs.readFile(path.join(dataDir, "category-summary.json"), "utf8"));

const categoryById = new Map(categories.map((item) => [item.id, item]));
const summaryById = new Map(categorySummary.map((item) => [item.category_id, item]));
const sheetNames = new Map([
  ["family-restaurants", "01 Restaurants"],
  ["bakeries-cafes-desserts", "02 Bakeries"],
  ["museums-science-history", "03 Museums"],
  ["arts-culture-spiritual-heritage", "04 Culture"],
  ["family-attractions-indoor-play", "05 Indoor Play"],
  ["geek-tech-anime-games-comics-vinyl", "06 Geek and Tech"],
  ["parks-hiking-lakes-nature", "07 Nature"],
  ["adventure-water-animals-farms", "08 Adventure"],
  ["shopping-markets-outlets", "09 Shopping"],
  ["sports-live-games", "10 Sports"],
  ["events-festivals-live-shows", "11 Events"],
  ["day-trips-unusual-experiences", "12 Day Trips"],
]);

const palette = {
  ink: "#263238",
  muted: "#59666F",
  paper: "#F6F3EE",
  white: "#FFFFFF",
  line: "#D7DDD8",
  soft: "#E9EFEB",
  green: "#3E6B4F",
  teal: "#1F6E67",
  amber: "#8A5A20",
  red: "#9B3D46",
};

function colName(index) {
  let n = index + 1;
  let result = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    result = String.fromCharCode(65 + rem) + result;
    n = Math.floor((n - 1) / 26);
  }
  return result;
}

function safeName(value) {
  return String(value).replace(/[^A-Za-z0-9]/g, "").slice(0, 180);
}

function quotedSheet(name) {
  return `'${name.replaceAll("'", "''")}'`;
}

function mapsSearchUrl(row) {
  if (Number.isFinite(row.latitude) && Number.isFinite(row.longitude)) {
    return `https://maps.google.com/?q=${Number(row.latitude).toFixed(6)},${Number(row.longitude).toFixed(6)}`;
  }
  const query = [row.name, row.address, row.city, row.state, row.zip].filter(Boolean).join(", ");
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}

function applyTitle(sheet, title, subtitle, accent, endCol = "Y") {
  sheet.getRange(`A1:${endCol}2`).merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A1:${endCol}2`).format = {
    fill: palette.soft,
    font: { bold: true, color: accent, size: 20, name: "Aptos Display" },
    verticalAlignment: "center",
    horizontalAlignment: "left",
    borders: { preset: "outside", style: "thin", color: accent },
  };
  sheet.getRange(`A3:${endCol}3`).merge();
  sheet.getRange("A3").values = [[subtitle]];
  sheet.getRange(`A3:${endCol}3`).format = {
    fill: palette.paper,
    font: { color: palette.muted, italic: true, size: 10, name: "Aptos" },
    verticalAlignment: "center",
  };
  sheet.getRange("A1").format.rowHeight = 30;
  sheet.getRange("A2").format.rowHeight = 30;
  sheet.getRange("A3").format.rowHeight = 25;
}

function formatHeader(range, accent = palette.ink) {
  range.format = {
    fill: palette.soft,
    font: { bold: true, color: accent, size: 10, name: "Aptos" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: accent },
  };
}

function setWidths(sheet, widths) {
  for (let i = 0; i < widths.length; i += 1) {
    sheet.getRange(`${colName(i)}:${colName(i)}`).format.columnWidth = widths[i];
  }
}

function datesLabel(row) {
  if (!row.start_date) return "Evergreen";
  if (row.start_date === row.end_date || !row.end_date) return row.start_date;
  return `${row.start_date} to ${row.end_date}`;
}

const workbook = Workbook.create();
const dashboard = workbook.worksheets.add("Dashboard");
const planner = workbook.worksheets.add("Family Planner");
const methodology = workbook.worksheets.add("Methodology");
const sources = workbook.worksheets.add("Sources");
const categorySheets = new Map();
for (const category of categories) {
  categorySheets.set(category.id, workbook.worksheets.add(sheetNames.get(category.id)));
}
const metrics = workbook.worksheets.add("Metrics");

for (const sheet of [dashboard, planner, methodology, sources, metrics, ...categorySheets.values()]) {
  sheet.showGridLines = false;
}

// Methodology is both documentation and the live scoring-input source.
applyTitle(
  methodology,
  "Holiday 2026 Ranking Methodology",
  "Child access is mandatory. Ranking then follows a strict hierarchy: culture, international experience, affordability, secondary quality.",
  palette.ink,
  "H",
);
methodology.getRange("A5:B9").values = [
  ["Reference point", "7010 Brassfield Dr, Cumming, GA 30041"],
  ["Research checked", new Date("2026-07-11T12:00:00")],
  ["Vacation window", "2026-07-11 through 2026-07-20"],
  ["Family audience", "Two adults and two girls; every published row must allow children."],
  ["Fallback interpretation", "If the verified eligible pool is below 50, publish the top half, rounded up."],
];
methodology.getRange("A5:A9").format = { fill: palette.soft, font: { bold: true, color: palette.ink } };
methodology.getRange("B6").format.numberFormat = "yyyy-mm-dd";
methodology.getRange("A11:C16").values = [
  ["Ranking gate / priority", "Order", "Application"],
  ["Children allowed", 0, "Mandatory gate; adult-only entries are excluded before ranking."],
  ["Cultural priority", 1, "Highest score first."],
  ["International / multicultural experience", 2, "Breaks cultural-priority ties."],
  ["Affordability", 3, "Low entry price breaks remaining ties; shopping entry is not purchase cost."],
  ["Secondary quality", 4, "Family fit, evidence, proximity, rating, uniqueness, plus timing for dated categories."],
];
formatHeader(methodology.getRange("A11:C11"), palette.teal);
methodology.getRange("A18:C24").values = [
  ["Secondary-quality component", "Evergreen weight", "Timed weight"],
  ["Family fit", 0.30, 0.25],
  ["Evidence quality", 0.25, 0.20],
  ["Proximity", 0.20, 0.15],
  ["Rating confidence", 0.15, 0.10],
  ["Uniqueness", 0.10, 0.10],
  ["Time urgency", 0.00, 0.20],
];
formatHeader(methodology.getRange("A18:C18"), palette.amber);
methodology.getRange("B19:C24").format.numberFormat = "0%";
methodology.getRange("A27:C35").values = [
  ["Driving-distance tier", "Miles", "Proximity score"],
  ["Very close", "0-5", 5.0],
  ["Nearby", ">5-15", 4.7],
  ["Local", ">15-25", 4.3],
  ["Metro near", ">25-40", 3.7],
  ["Metro", ">40-60", 3.0],
  ["Long metro", ">60-90", 2.2],
  ["Day trip", ">90-150", 1.4],
  ["Exceptional overnight", ">150", 0.5],
];
formatHeader(methodology.getRange("A27:C27"), palette.amber);
methodology.getRange("E5:H16").values = [
  ["Quality-control rule", "Application", null, null],
  ["Current operation", "Exclude known permanently closed venues.", null, null],
  ["Family scope", "Publish only children_allowed=true; label guardian, age, height, content, or late-hour conditions.", null, null],
  ["Food inference", "Normal restaurants and bakeries without adult-only evidence are retained as venue-type inferences.", null, null],
  ["Preference hierarchy", "Strict order: culture → international experience → affordability → secondary quality.", null, null],
  ["Evidence", "Keep source URLs and checked dates on every row.", null, null],
  ["Distance", "Use OSRM route miles when available; otherwise label the fallback estimate.", null, null],
  ["Events", "Dated options usable July 11-20 rank before later dates; evergreen activities remain usable.", null, null],
  ["Ratings", "Use published values only; missing ratings receive a neutral prior, not an invented rating.", null, null],
  ["Costs", "Affordability is derived from entry price, not subjective value; taxes, food, purchases and fees may be extra.", null, null],
  ["Images", "Use official source captures with attribution only for this private planning package.", null, null],
  ["Recheck", "Open the source or directions link before a time-sensitive trip.", null, null],
];
formatHeader(methodology.getRange("E5:H5"), palette.red);
methodology.getRange("E6:H16").format.wrapText = true;
setWidths(methodology, [30, 48, 58, 4, 25, 68, 12, 12]);
methodology.freezePanes.freezeRows(3);

// Category sheets: the component scores are inputs and the overall score/rank are formulas.
const headers = [
  "Rank", "Name", "Subtype", "Preference score / 100", "Child access", "Culture 1-5", "International 1-5",
  "Affordability 1-5", "Nation / culture", "Price", "Distance mi", "Drive min", "Distance tier", "Timing",
  "Available Jul 11-20", "Family fit", "Evidence", "Proximity", "Rating score", "Uniqueness", "Urgency",
  "Secondary quality", "Setting", "Visit hours", "Why it fits", "Caveat", "Age notes", "Official URL",
  "Directions URL", "Checked date", "Selection rule", "Pool size", "Ranking key",
];
for (const category of categories) {
  const sheet = categorySheets.get(category.id);
  const categoryRows = rows.filter((row) => row.category_id === category.id);
  const summary = summaryById.get(category.id) ?? { eligible_pool_size: 0, published_count: 0 };
  applyTitle(
    sheet,
    category.name,
    `${category.promise} Children allowed only; culture → international experience → affordability.`,
    category.accent,
    "O",
  );
  sheet.getRange("A5:J5").values = [[
    "Child-friendly pool", summary.eligible_pool_size, "Published", summary.published_count,
    "Cultural", summary.cultural_priority_count ?? 0, "International", summary.international_experience_count ?? 0,
    "Affordable", summary.affordable_count ?? 0,
  ]];
  sheet.getRange("A5:J5").format = {
    fill: palette.soft,
    font: { bold: true, color: palette.ink },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  const firstDataRow = 8;
  const lastDataRow = Math.max(firstDataRow, firstDataRow + categoryRows.length - 1);
  sheet.getRange("A7:AG7").values = [headers];
  formatHeader(sheet.getRange("A7:AG7"), category.accent);
  if (categoryRows.length) {
    const values = categoryRows.map((row) => [
      null,
      row.name,
      row.subtype,
      null,
      row.child_access_level,
      row.cultural_priority_1_5,
      row.international_experience_1_5,
      row.affordability_1_5,
      Array.isArray(row.nation_culture_tags) ? row.nation_culture_tags.join("; ") : String(row.nation_culture_tags ?? ""),
      row.price_level,
      row.distance_miles ?? null,
      row.drive_minutes ?? null,
      row.distance_tier,
      datesLabel(row),
      Boolean(row.available_during_vacation),
      row.family_fit_1_5,
      row.evidence_quality_1_5,
      row.proximity_score_1_5,
      row.rating_score_1_5,
      row.uniqueness_1_5,
      row.time_urgency_1_5,
      null,
      row.indoor_outdoor,
      row.estimated_visit_hours,
      row.why_good,
      row.caveat,
      row.age_notes,
      row.official_url,
      row.directions_url,
      row.checked_date ? new Date(`${row.checked_date}T12:00:00`) : null,
      row.selection_rule,
      row.pool_size,
      null,
    ]);
    sheet.getRange(`A${firstDataRow}:AG${lastDataRow}`).values = values;
    const timed = ["sports-live-games", "events-festivals-live-shows"].includes(category.id);
    const weightCol = timed ? "C" : "B";
    const secondaryFormula = `=ROUND(${quotedSheet("Methodology")}!$${weightCol}$19*P${firstDataRow}+${quotedSheet("Methodology")}!$${weightCol}$20*Q${firstDataRow}+${quotedSheet("Methodology")}!$${weightCol}$21*R${firstDataRow}+${quotedSheet("Methodology")}!$${weightCol}$22*S${firstDataRow}+${quotedSheet("Methodology")}!$${weightCol}$23*T${firstDataRow}+${quotedSheet("Methodology")}!$${weightCol}$24*U${firstDataRow},2)`;
    sheet.getRange(`V${firstDataRow}`).formulas = [[secondaryFormula]];
    sheet.getRange(`V${firstDataRow}:V${lastDataRow}`).fillDown();
    const rankingKeyFormula = `=IF(O${firstDataRow},6765201,0)+(((ROUND(F${firstDataRow}*10,0)*51+ROUND(G${firstDataRow}*10,0))*51+ROUND(H${firstDataRow}*10,0))*51+ROUND(V${firstDataRow}*10,0))`;
    sheet.getRange(`AG${firstDataRow}`).formulas = [[rankingKeyFormula]];
    sheet.getRange(`AG${firstDataRow}:AG${lastDataRow}`).fillDown();
    const scoreFormula = `=ROUND(20+80*((AG${firstDataRow}-IF(O${firstDataRow},6765201,0)-1353040)/5412160),1)`;
    sheet.getRange(`D${firstDataRow}`).formulas = [[scoreFormula]];
    sheet.getRange(`D${firstDataRow}:D${lastDataRow}`).fillDown();
    sheet.getRange(`A${firstDataRow}`).formulas = [[`=RANK(AG${firstDataRow},$AG$${firstDataRow}:$AG$${lastDataRow},0)+COUNTIF($AG$${firstDataRow}:AG${firstDataRow},AG${firstDataRow})-1`]];
    sheet.getRange(`A${firstDataRow}:A${lastDataRow}`).fillDown();
    const table = sheet.tables.add(`A7:AG${lastDataRow}`, true, `${safeName(category.video_slug)}Table`);
    table.style = "TableStyleLight1";
    table.showBandedRows = true;
    sheet.getRange(`D${firstDataRow}:D${lastDataRow}`).conditionalFormats.add("colorScale", {
      criteria: [
        { type: "lowestValue", color: "#F2D9DB" },
        { type: "percentile", value: 50, color: "#F3E3C8" },
        { type: "highestValue", color: "#D8ECE7" },
      ],
    });
    sheet.getRange(`K${firstDataRow}:K${lastDataRow}`).conditionalFormats.add("dataBar", {
      color: category.accent,
      gradient: true,
    });
    sheet.getRange(`F${firstDataRow}:H${lastDataRow}`).dataValidation = {
      rule: { type: "decimal", operator: "between", formula1: 1, formula2: 5 },
    };
    sheet.getRange(`P${firstDataRow}:V${lastDataRow}`).dataValidation = {
      rule: { type: "decimal", operator: "between", formula1: 1, formula2: 5 },
    };
    sheet.getRange(`D${firstDataRow}:D${lastDataRow}`).format.numberFormat = "0.0";
    sheet.getRange(`F${firstDataRow}:H${lastDataRow}`).format.numberFormat = "0.0";
    sheet.getRange(`K${firstDataRow}:L${lastDataRow}`).format.numberFormat = "0.0";
    sheet.getRange(`P${firstDataRow}:V${lastDataRow}`).format.numberFormat = "0.0";
    sheet.getRange(`X${firstDataRow}:X${lastDataRow}`).format.numberFormat = "0.0";
    sheet.getRange(`AD${firstDataRow}:AD${lastDataRow}`).format.numberFormat = "yyyy-mm-dd";
    sheet.getRange(`B${firstDataRow}:C${lastDataRow}`).format.wrapText = true;
    sheet.getRange(`E${firstDataRow}:J${lastDataRow}`).format.wrapText = true;
    sheet.getRange(`N${firstDataRow}:O${lastDataRow}`).format.wrapText = true;
    sheet.getRange(`Y${firstDataRow}:AC${lastDataRow}`).format.wrapText = true;
    sheet.getRange(`A${firstDataRow}:X${lastDataRow}`).format.verticalAlignment = "center";
    sheet.getRange(`Y${firstDataRow}:AC${lastDataRow}`).format.verticalAlignment = "top";
    sheet.getRange(`A${firstDataRow}:AG${lastDataRow}`).format.rowHeight = 48;
  } else {
    sheet.getRange("A8:AG8").values = [["No child-permitted candidates were available in this build.", ...Array(32).fill(null)]];
    sheet.getRange("A8:AG8").format = { fill: "#F3E3C8", font: { color: palette.ink, italic: true } };
  }
  setWidths(sheet, [7, 28, 21, 13, 26, 10, 12, 12, 24, 13, 11, 10, 13, 20, 15, 10, 10, 10, 11, 10, 9, 12, 11, 10, 45, 42, 34, 42, 42, 13, 30, 9, 16]);
  sheet.freezePanes.freezeRows(7);
  sheet.freezePanes.freezeColumns(2);
}

// Metrics sheet drives the dashboard charts with formulas linked to category sheets.
applyTitle(metrics, "Category Metrics", "Formula-backed child-friendly and preference summary used by the dashboard.", palette.teal, "M");
metrics.getRange("A5:M5").values = [["Category", "Child-friendly pool", "Published", "Avg score", "Avg distance", "Local", "Affordable", "Cultural", "International", "Vacation window", "Top pick", "Top-pick distance", "Video"]];
formatHeader(metrics.getRange("A5:M5"), palette.teal);
for (let i = 0; i < categories.length; i += 1) {
  const rowNum = 6 + i;
  const category = categories[i];
  const categoryRows = rows.filter((row) => row.category_id === category.id);
  const categorySheet = sheetNames.get(category.id);
  const last = Math.max(8, 7 + categoryRows.length);
  const summary = summaryById.get(category.id) ?? { eligible_pool_size: 0, published_count: 0 };
  metrics.getRange(`A${rowNum}:C${rowNum}`).values = [[category.short_name, summary.eligible_pool_size, summary.published_count]];
  if (categoryRows.length) {
    metrics.getRange(`D${rowNum}:F${rowNum}`).formulas = [[
      `=IFERROR(AVERAGE(${quotedSheet(categorySheet)}!$D$8:$D$${last}),0)`,
      `=IFERROR(AVERAGE(${quotedSheet(categorySheet)}!$K$8:$K$${last}),0)`,
      `=COUNTIF(${quotedSheet(categorySheet)}!$M$8:$M$${last},"Local")`,
    ]];
    metrics.getRange(`G${rowNum}:J${rowNum}`).values = [[
      categoryRows.filter((row) => Number(row.affordability_1_5) >= 4).length,
      categoryRows.filter((row) => Number(row.cultural_priority_1_5) >= 4).length,
      categoryRows.filter((row) => Number(row.international_experience_1_5) >= 4).length,
      categoryRows.filter((row) => row.vacation_window).length,
    ]];
    metrics.getRange(`K${rowNum}:L${rowNum}`).formulas = [[
      `=INDEX(${quotedSheet(categorySheet)}!$B$8:$B$${last},MATCH(1,${quotedSheet(categorySheet)}!$A$8:$A$${last},0))`,
      `=INDEX(${quotedSheet(categorySheet)}!$K$8:$K$${last},MATCH(1,${quotedSheet(categorySheet)}!$A$8:$A$${last},0))`,
    ]];
  } else {
    metrics.getRange(`D${rowNum}:L${rowNum}`).values = [[0, 0, 0, 0, 0, 0, 0, "N/A", 0]];
  }
  metrics.getRange(`M${rowNum}`).values = [[`artifacts/videos/${category.video_slug}.mp4`]];
}
metrics.getRange("D6:E17").format.numberFormat = "0.0";
metrics.getRange("L6:L17").format.numberFormat = "0.0";
metrics.getRange("A5:M17").format.borders = { preset: "outside", style: "thin", color: palette.line };
setWidths(metrics, [20, 16, 12, 12, 14, 9, 11, 10, 13, 16, 36, 16, 52]);
metrics.freezePanes.freezeRows(5);

// Dashboard with formula-backed KPIs, category table and two native charts.
applyTitle(dashboard, "Holiday 2026 Family Guide", "Children allowed only • Culture first • International experiences second • Low prices third", palette.ink, "X");
dashboard.getRange("A5:J7").values = [
  ["Categories", null, "Child-friendly choices", null, "Cultural choices", null, "International choices", null, "Affordable choices", null],
  [null, null, null, null, null, null, null, null, null, null],
  ["Open any category tab for ranking formulas, child-access conditions, source URLs and directions.", null, null, null, null, null, null, null, null, null],
];
for (const start of ["A5:B6", "C5:D6", "E5:F6", "G5:H6", "I5:J6"]) {
  dashboard.getRange(start).format = { fill: palette.soft, borders: { preset: "outside", style: "thin", color: palette.line } };
}
dashboard.getRange("A5:J5").format.font = { bold: true, color: palette.muted, size: 10 };
dashboard.getRange("A6").formulas = [["=COUNTA('Metrics'!$A$6:$A$17)"]];
dashboard.getRange("C6").formulas = [["=SUM('Metrics'!$C$6:$C$17)"]];
dashboard.getRange("E6").formulas = [["=SUM('Metrics'!$H$6:$H$17)"]];
dashboard.getRange("G6").formulas = [["=SUM('Metrics'!$I$6:$I$17)"]];
dashboard.getRange("I6").formulas = [["=SUM('Metrics'!$G$6:$G$17)"]];
dashboard.getRange("A6:J6").format.font = { bold: true, color: palette.ink, size: 18, name: "Aptos Display" };
dashboard.getRange("A7:J7").merge();
dashboard.getRange("A7:J7").format = { font: { italic: true, color: palette.muted }, fill: palette.paper };
dashboard.getRange("A9:M9").values = [["Category", "Child-friendly pool", "Published", "Avg score", "Avg distance", "Local", "Affordable", "Cultural", "International", "Vacation window", "Top pick", "Miles", "Video"]];
formatHeader(dashboard.getRange("A9:M9"), palette.teal);
for (let i = 0; i < categories.length; i += 1) {
  const dashRow = 10 + i;
  const metricRow = 6 + i;
  dashboard.getRange(`A${dashRow}:M${dashRow}`).formulas = [[
    `='Metrics'!A${metricRow}`, `='Metrics'!B${metricRow}`, `='Metrics'!C${metricRow}`, `='Metrics'!D${metricRow}`,
    `='Metrics'!E${metricRow}`, `='Metrics'!F${metricRow}`, `='Metrics'!G${metricRow}`, `='Metrics'!H${metricRow}`,
    `='Metrics'!I${metricRow}`, `='Metrics'!J${metricRow}`, `='Metrics'!K${metricRow}`, `='Metrics'!L${metricRow}`,
    `='Metrics'!M${metricRow}`,
  ]];
}
dashboard.getRange("D10:E21").format.numberFormat = "0.0";
dashboard.getRange("L10:L21").format.numberFormat = "0.0";
dashboard.getRange("K10:M21").format.wrapText = true;
dashboard.getRange("A9:M21").format.borders = { preset: "outside", style: "thin", color: palette.line };
dashboard.getRange("A10:M21").format.rowHeight = 30;
setWidths(dashboard, [20, 16, 10, 11, 13, 8, 11, 10, 13, 15, 34, 10, 48, 2, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13]);
const countChart = dashboard.charts.add("bar", dashboard.getRange("A9:C21"));
countChart.title = "Published choices by category";
countChart.hasLegend = true;
countChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
countChart.yAxis = { numberFormatCode: "0" };
countChart.setPosition("O5", "X17");
dashboard.getRange("O33:P33").values = [["Category", "Average distance (mi)"]];
for (let i = 0; i < categories.length; i += 1) {
  const sourceRow = 10 + i;
  const helperRow = 34 + i;
  dashboard.getRange(`O${helperRow}:P${helperRow}`).formulas = [[`=A${sourceRow}`, `=E${sourceRow}`]];
}
const distanceChart = dashboard.charts.add("bar", dashboard.getRange("O33:P45"));
distanceChart.title = "Average distance of published choices";
distanceChart.hasLegend = false;
distanceChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
distanceChart.yAxis = { numberFormatCode: "0.0" };
distanceChart.setPosition("O18", "X31");
dashboard.freezePanes.freezeRows(9);

// Planner: editable shortlist with data validation.
applyTitle(planner, "Family Planner", "Top three per category, all permitting children. Compare culture, international experience and affordability before booking.", palette.amber, "O");
planner.getRange("A5:O5").values = [["Category", "Rank", "Name", "Child access", "Culture", "International", "Nation / culture", "Affordability", "Distance mi", "Timing", "Price", "Decision", "Planned date", "Notes", "Directions"]];
formatHeader(planner.getRange("A5:O5"), palette.amber);
const shortlist = categories.flatMap((category) => rows.filter((row) => row.category_id === category.id).slice(0, 3).map((row) => ({ ...row, category_name: category.short_name })));
if (shortlist.length) {
  const values = shortlist.map((row) => [
    row.category_name,
    row.rank,
    row.name,
    row.child_access_level,
    row.cultural_priority_1_5,
    row.international_experience_1_5,
    Array.isArray(row.nation_culture_tags) ? row.nation_culture_tags.join("; ") : String(row.nation_culture_tags ?? ""),
    row.affordability_1_5,
    row.distance_miles,
    datesLabel(row),
    row.price_level,
    "Maybe",
    null,
    "",
    mapsSearchUrl(row),
  ]);
  const end = 6 + values.length - 1;
  planner.getRange(`A6:O${end}`).values = values;
  planner.getRange(`L6:L${end}`).dataValidation = { rule: { type: "list", values: ["Must do", "Maybe", "Skip", "Booked"] } };
  planner.getRange(`M6:M${end}`).format.numberFormat = "yyyy-mm-dd";
  planner.getRange(`E6:F${end}`).format.numberFormat = "0.0";
  planner.getRange(`H6:I${end}`).format.numberFormat = "0.0";
  planner.getRange(`C6:C${end}`).format.wrapText = true;
  planner.getRange(`D6:O${end}`).format.wrapText = true;
  planner.getRange(`A6:O${end}`).format.rowHeight = 40;
  const table = planner.tables.add(`A5:O${end}`, true, "FamilyPlannerTable");
  table.style = "TableStyleLight1";
}
setWidths(planner, [18, 7, 32, 25, 10, 12, 24, 13, 12, 22, 14, 13, 14, 34, 42]);
planner.freezePanes.freezeRows(5);

// Sources table contains the auditable URLs required for researched rows.
applyTitle(sources, "Source Ledger", "Every published row retains child-access basis, culture tags, source URLs, checked date and distance method.", palette.red, "L");
sources.getRange("A5:L5").values = [["Category", "Rank", "Name", "Child access", "Child policy basis", "Nation / culture", "Official URL", "Corroborating URL", "Checked", "Distance method", "Research file", "Directions"]];
formatHeader(sources.getRange("A5:L5"), palette.red);
if (rows.length) {
  const values = rows.map((row) => [
    categoryById.get(row.category_id)?.short_name ?? row.category_id,
    row.rank,
    row.name,
    row.child_access_level,
    row.child_policy_basis,
    Array.isArray(row.nation_culture_tags) ? row.nation_culture_tags.join("; ") : String(row.nation_culture_tags ?? ""),
    row.official_url,
    row.corroborating_url,
    row.checked_date ? new Date(`${row.checked_date}T12:00:00`) : null,
    row.distance_method,
    row.research_source_file,
    row.directions_url,
  ]);
  const end = 6 + values.length - 1;
  sources.getRange(`A6:L${end}`).values = values;
  sources.getRange(`D6:L${end}`).format.wrapText = true;
  sources.getRange(`I6:I${end}`).format.numberFormat = "yyyy-mm-dd";
  sources.getRange(`A6:L${end}`).format.rowHeight = 44;
  const table = sources.tables.add(`A5:L${end}`, true, "SourceLedgerTable");
  table.style = "TableStyleLight1";
}
setWidths(sources, [18, 7, 32, 26, 45, 24, 48, 48, 13, 23, 29, 48]);
sources.freezePanes.freezeRows(5);

await workbook.comments.setSelf({ displayName: "User" });
workbook.comments.addThread({ cell: methodology.getRange("A12") }, "Child access is a mandatory dataset gate. Rows with children_allowed=false cannot enter the workbook.");
workbook.comments.addThread({ cell: methodology.getRange("B19") }, "These cells are live secondary-quality assumptions. Culture, international experience and affordability remain strict higher-order priorities.");
workbook.comments.addThread({ cell: methodology.getRange("B9") }, "The top-half interpretation is recorded explicitly because the original instruction was ambiguous.");

// Compact inspections before export.
const keyInspection = await workbook.inspect({
  kind: "table",
  range: "Dashboard!A1:M21",
  include: "values,formulas",
  tableMaxRows: 24,
  tableMaxCols: 14,
  maxChars: 7000,
});
await fs.writeFile(path.join(previewDir, "dashboard-inspection.ndjson"), keyInspection.ndjson, "utf8");
const formulaErrors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
  maxChars: 7000,
});
await fs.writeFile(path.join(previewDir, "formula-error-scan.ndjson"), formulaErrors.ndjson, "utf8");

const renderNames = ["Dashboard", "Family Planner", "Methodology", "Sources", ...categories.map((item) => sheetNames.get(item.id)), "Metrics"];
const rendered = [];
for (const sheetName of renderNames) {
  if (sheetName === "Sources") {
    const lastSourceRow = 5 + rows.length;
    const sourceRanges = ["A1:L35"];
    for (let start = 36; start <= lastSourceRow; start += 100) {
      sourceRanges.push(`A${start}:L${Math.min(lastSourceRow, start + 99)}`);
    }
    for (let index = 0; index < sourceRanges.length; index += 1) {
      const blob = await workbook.render({ sheetName, range: sourceRanges[index], scale: 0.62, format: "png" });
      const filename = `${safeName(sheetName).toLowerCase()}-${String(index + 1).padStart(2, "0")}.png`;
      await fs.writeFile(path.join(previewDir, filename), new Uint8Array(await blob.arrayBuffer()));
      rendered.push(filename);
    }
    continue;
  }
  const category = categories.find((item) => sheetNames.get(item.id) === sheetName);
  const categoryCount = category ? rows.filter((row) => row.category_id === category.id).length : 0;
  if (category) {
    const lastCategoryRow = Math.max(8, 7 + categoryCount);
    const categoryRanges = [
      { suffix: "front", range: `A1:O${lastCategoryRow}` },
      { suffix: "details", range: `P7:AG${lastCategoryRow}` },
    ];
    for (const item of categoryRanges) {
      const blob = await workbook.render({ sheetName, range: item.range, scale: 0.72, format: "png" });
      const filename = `${safeName(sheetName).toLowerCase()}-${item.suffix}.png`;
      await fs.writeFile(path.join(previewDir, filename), new Uint8Array(await blob.arrayBuffer()));
      rendered.push(filename);
    }
    continue;
  }
  const range = sheetName === "Dashboard"
    ? "A1:X31"
    : sheetName === "Methodology"
      ? "A1:H35"
      : sheetName === "Family Planner"
        ? `A1:O${Math.max(8, 5 + shortlist.length)}`
        : sheetName === "Metrics"
          ? "A1:M18"
          : "A1:K30";
  const scale = sheetName === "Dashboard" ? 1.0 : 0.8;
  const blob = await workbook.render({ sheetName, range, scale, format: "png" });
  const filename = `${safeName(sheetName).toLowerCase()}.png`;
  await fs.writeFile(path.join(previewDir, filename), new Uint8Array(await blob.arrayBuffer()));
  rendered.push(filename);
}

const outputPath = path.join(outputDir, "holiday2026-family-guide.xlsx");
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
const report = {
  ok: true,
  output: outputPath,
  childAccessGate: invalidChildRows.length === 0,
  preferenceOrder: ["culture", "international experience", "affordability", "secondary quality"],
  sheets: renderNames,
  renderedPreviews: rendered,
  selectedRows: rows.length,
  categoryCounts: Object.fromEntries(categories.map((category) => [category.id, rows.filter((row) => row.category_id === category.id).length])),
};
await fs.writeFile(path.join(previewDir, "workbook-build-report.json"), JSON.stringify(report, null, 2) + "\n", "utf8");
console.log(JSON.stringify(report));
