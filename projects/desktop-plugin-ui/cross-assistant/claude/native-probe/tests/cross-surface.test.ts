import { expect, test } from "claude-code/testing";

const PANE = {
  plugin: "desktop-ui-probe", component: "Pane", requestId: "desktop-ui-probe",
  viewport: { columns: 100, rows: 30 },
  props: { title: "Boundary probe", isFocused: true, bodyColumns: 80, placement: "inline", scroll: { bodyRows: 20, offset: 0 }, view: {} },
} as const;
async function mount($, selectedCase, surface = "terminal") {
  await $.command.run({ command: "probe-case", args: selectedCase });
  return $.ui.mount({ ...PANE, surface });
}
async function reject($, selectedCase, surface, pattern) {
  let reason = "";
  try { await mount($, selectedCase, surface); } catch (error) { reason = String(error.message); }
  console.log(JSON.stringify({ probe: selectedCase, surface, expected: "rejected", reason }));
  expect(reason).toMatch(pattern);
}
for (const tag of ["div", "canvas", "iframe", "script", "webview", "svg"]) {
  test(`raw HTML ${tag} is not a terminal native element`, async $ => reject($, `html-${tag}`, "terminal", /element|type|native|unknown|valid/));
}
for (const surface of ["desktop", "vscode"]) {
  test(`raw terminal Image cannot be drawn on ${surface}`, async $ => reject($, "image", surface, /Image|surface/));
  test(`raw terminal Raster cannot be drawn on ${surface}`, async $ => reject($, "raster", surface, /Raster|surface/));
}
test("terminal Raster accepts one correctly encoded cell", async $ => {
  const ui = await mount($, "raster");
  expect(await ui.find({ type: "Raster" })).toBeDefined();
});
test("terminal Raster refuses a payload with the wrong byte count", async $ => reject($, "invalid-raster-bytes", "terminal", /Raster|cells|byte/));
test("native Box refuses a React DOM style object", async $ => reject($, "css-injection", "desktop", /style|prop|Box/));
test("terminal Image refuses missing alternative text", async $ => reject($, "missing-image-alt", "terminal", /alt|Image/));
test("terminal Image refuses incorrect RGBA byte count", async $ => reject($, "bad-rgba-size", "terminal", /RGBA|rgba|byte|Image/));
test("terminal Image refuses 256 columns", async $ => reject($, "image-columns-256", "terminal", /255|columns|Image/));
test("a missing Image file can validate before the terminal reads it", async $ => {
  const ui = await mount($, "image-file-missing");
  expect(await ui.find({ type: "Image" })).toBeDefined();
});
test("2048-character href passes while 2049 refuses", async $ => {
  const ui = await mount($, "href-size-2048", "desktop");
  expect(await ui.find({ type: "Link" })).toBeDefined(); await ui.unmount();
  await reject($, "href-size-2049", "desktop", /2048|href|Link/);
});
test("131072-character SVG passes while 131073 refuses", async $ => {
  const ui = await mount($, "svg-size-131072", "desktop");
  expect(await ui.find({ type: "Svg" })).toBeDefined(); await ui.unmount();
  await reject($, "svg-size-131073", "desktop", /131072|Svg|source/);
});
test("raw Client cannot be drawn on VS Code", async $ => reject($, "raw-client", "vscode", /Client|surface/));
test("terminal Raster refuses 513 columns", async $ => reject($, "raster-columns-513", "terminal", /512|columns|Raster/));
test("terminal Raster refuses 257 rows", async $ => reject($, "raster-rows-257", "terminal", /256|rows|Raster/));
test("10000-character Select value passes while 10001 refuses", async $ => {
  const ui = await mount($, "option-size-10000", "terminal");
  expect(await ui.find({ type: "Select" })).toBeDefined(); await ui.unmount();
  await reject($, "option-size-10001", "terminal", /Select|option/);
});
