import { expect, test } from "claude-code/testing";

const PANE = {
  plugin: "desktop-ui-probe", component: "Pane", requestId: "desktop-ui-probe",
  viewport: { columns: 100, rows: 30 },
  props: { title: "Probe", isFocused: true, bodyColumns: 80, placement: "inline", scroll: { bodyRows: 20, offset: 0 }, view: {} },
} as const;
async function mountCase($, selectedCase, surface = "desktop") {
  await $.command.run({ command: "probe-case", args: selectedCase });
  return $.ui.mount({ ...PANE, surface });
}
async function rejection($, selectedCase, surface, pattern) {
  let reason = "";
  try { await mountCase($, selectedCase, surface); } catch (error) { reason = String(error.message); }
  console.log(JSON.stringify({ probe: selectedCase, surface, outcome: "negative", reason }));
  expect(reason).toMatch(pattern);
}

test("common native layout, formatted text, controls and HTTPS links validate on desktop, terminal and vscode", async ($) => {
  for (const surface of ["desktop", "terminal", "vscode"]) {
    const ui = await mountCase($, "common", surface);
    for (const type of ["Box", "Text", "Button", "Input", "Select", "Link", "Code", "Markdown"]) expect(await ui.find({ type })).toBeDefined();
    await ui.unmount();
  }
});
test("button dispatch changes the native drawing without starting a model turn", async ($) => {
  const ui = await mountCase($, "controls");
  await ui.press({ key: "count" });
  expect(await ui.find({ type: "Text", text: "Count: 1" })).toBeDefined();
});
test("Input change updates draft without submitting", async ($) => {
  const ui = await mountCase($, "controls");
  await ui.input({ key: "query", text: "Draft only", kind: "change" });
  expect(await ui.find({ type: "Text", text: "Draft: Draft only" })).toBeDefined();
  expect(await ui.find({ type: "Text", text: "Submitted: " })).toBeDefined();
});
test("Input submit dispatches the supplied text", async ($) => {
  const ui = await mountCase($, "controls");
  await ui.input({ key: "query", text: "Submitted value" });
  expect(await ui.find({ type: "Text", text: "Submitted: Submitted value" })).toBeDefined();
});
test("Select dispatch updates selected value", async ($) => {
  const ui = await mountCase($, "controls");
  await ui.select({ key: "size", value: "large" });
  expect(await ui.find({ type: "Text", text: "Selected: large" })).toBeDefined();
});
test("Svg is valid on desktop and vscode", async ($) => {
  for (const surface of ["desktop", "vscode"]) {
    const ui = await mountCase($, "svg", surface);
    expect(await ui.find({ type: "Svg" })).toBeDefined();
    await ui.unmount();
  }
});
test("Svg is refused in the terminal tree", async ($) => rejection($, "svg", "terminal", /Svg|surface/));
test("Image RGBA payload is valid in terminal", async ($) => {
  const ui = await mountCase($, "image", "terminal");
  expect(await ui.find({ type: "Image" })).toBeDefined();
});
test("Image is refused in the desktop tree", async ($) => rejection($, "image", "desktop", /Image|surface/));
for (const selectedCase of ["file-link", "js-link", "remote-http-link"]) test(`${selectedCase} is downgraded to non-clickable text on desktop`, async ($) => {
  const ui = await mountCase($, selectedCase, "desktop");
  expect(await ui.find({ type: "Link" })).toBeUndefined();
  expect(await ui.find({ type: "Text" })).toBeDefined();
});
test("HTTPS Link and localhost HTTP Link are accepted", async ($) => {
  for (const selectedCase of ["https-link", "localhost-link"]) {
    const ui = await mountCase($, selectedCase);
    expect(await ui.find({ type: "Link" })).toBeDefined();
    await ui.unmount();
  }
});
test("oversized href refuses the drawing", async ($) => rejection($, "long-link", "desktop", /2048|Link|href/));
test("oversized Svg refuses the drawing", async ($) => rejection($, "long-svg", "desktop", /131072|Svg|longer/));
test("Image rejects invalid PNG bytes", async ($) => rejection($, "invalid-png", "terminal", /PNG|png/));
test("Image rejects a fractional generation counter", async ($) => rejection($, "invalid-generation", "terminal", /generation|whole number/));
test("arbitrary iframe tags cannot replace native primitives", async ($) => rejection($, "invalid-html", "desktop", /iframe|element|type/));
test("autoFocus false skips the hook and exposes the host fallback", async ($, on) => {
  on("ui.render", () => ({ type: "Text", props: {}, children: ["Host fallback"] }));
  const ui = await mountCase($, "autofocus-false", "desktop");
  expect(await ui.find({ type: "Button" })).toBeUndefined();
  expect(await ui.find({ type: "Text", text: "Host fallback" })).toBeDefined();
});
test("duplicate Select option values are rejected", async ($) => rejection($, "duplicate-select", "desktop", /Select|unique|duplicate/));
test("copy button sends the exact clipboard text through ui.copy", async ($, on) => {
  let copied = "";
  on("ui.copy", ($, e) => { copied = e.text; return { value: undefined }; });
  const ui = await mountCase($, "copy"); await ui.press({ key: "copy" });
  expect(copied).toBe("C:/work/result.html");
});
test("process boundary preserves argv and stdin without launching an executable", async ($, on) => {
  let invocation;
  on("process.run", ($, e) => { invocation = e; return { value: { exitCode: 0, stdout: "", stderr: "" } }; });
  const ui = await mountCase($, "process"); await ui.press({ key: "generate" });
  expect(invocation.argv).toEqual(["renderer", "--title", "literal $() ; value"]);
  expect(invocation.init.stdin).toBe('{"count":1}');
});
test("toast, status and log have distinct API events", async ($, on) => {
  const events = [];
  for (const event of ["ui.toast", "ui.status", "ui.log"]) on(event, ($, e) => { events.push([event, e.text]); return { value: undefined }; });
  const ui = await mountCase($, "notifications"); await ui.press({ key: "notify" });
  expect(events).toEqual([["ui.toast", "Complete"], ["ui.status", "1 ready"], ["ui.log", "Ready locally"]]);
});
test("an unplaced pane can return an explicit transcript fallback", async ($, on) => {
  let request;
  on("ui.open", ($, e) => { request = e; return { value: { isPlaced: false } }; });
  const result = await $.command.run({ command: "probe-open", args: "" });
  expect(result.text).toBe("Use the transcript fallback");
  expect(request.id).toBe("desktop-ui-probe"); expect(request.rows).toBe(8);
});
test("resolve compatibility names cannot prove a surface supports an element", async ($) => {
  const desktop = await mountCase($, "table", "desktop");
  expect(await desktop.find({ type: "Text", text: /Svg/ })).toBeDefined();
  expect(await desktop.find({ type: "Text", text: /Client/ })).toBeDefined();
  expect(await desktop.find({ type: "Text", text: /Raster/ })).toBeDefined();
  expect(await desktop.find({ type: "Text", text: /Image/ })).toBeDefined();
  await desktop.unmount();
  const terminal = await mountCase($, "table", "terminal");
  expect(await terminal.find({ type: "Text", text: /Raster/ })).toBeDefined();
  expect(await terminal.find({ type: "Text", text: /Image/ })).toBeDefined();
});
test("native leaves reject even an empty children array", async ($) => rejection($, "leaf-children", "desktop", /takes no children/));
test("hooks have no document, window or process although a loader require function exists", async ($) => {
  const result = await $.command.run({ command: "probe-environment", args: "" });
  expect(result.text).toBe("undefined,undefined,undefined,function");
});
test("the loader require cannot access the Node filesystem module", async ($) => {
  const result = await $.command.run({ command: "probe-node", args: "" });
  expect(result.text).toMatch(/node|module|require|unsupported/);
  expect(result.text).not.toMatch(/Unexpected Node access/);
});
test("Client draws its own native subtree on desktop and terminal", async ($) => {
  for (const surface of ["desktop", "terminal"]) {
    const ui = await mountCase($, "client", surface);
    expect(await ui.find({ type: "Text", text: "Label: Initial", in: "custom" })).toBeDefined();
    await ui.unmount();
  }
});
test("Client key events update its local state", async ($) => {
  const ui = await mountCase($, "client");
  await ui.key({ key: "right", in: "custom" });
  expect(await ui.find({ type: "Text", text: "Key: right", in: "custom" })).toBeDefined();
});
test("Client pointer events preserve region-relative coordinates", async ($) => {
  const ui = await mountCase($, "client");
  await ui.pointer({ type: "down", x: 3, y: 2, button: "left", in: "custom" });
  expect(await ui.find({ type: "Text", text: "Pointer: down:3,2", in: "custom" })).toBeDefined();
});
test("Client timer advances on the controlled frame clock", async ($) => {
  const ui = await mountCase($, "client");
  await ui.advance(2500);
  expect(await ui.find({ type: "Text", text: "Ticks: 2", in: "custom" })).toBeDefined();
});
test("Client post crosses ui.message and receives validated props", async ($) => {
  const ui = await mountCase($, "client");
  await ui.post({ label: "Checked" }, { in: "custom" });
  expect(await ui.find({ type: "Text", text: "Label: Checked", in: "custom" })).toBeDefined();
  await ui.post({ label: 42 }, { in: "custom" });
  expect(await ui.find({ type: "Text", text: "Label: Validated fallback", in: "custom" })).toBeDefined();
});
test("Client resize changes measured region size", async ($) => {
  const ui = await mountCase($, "client");
  await ui.resize({ columns: 42, rows: 8, in: "custom" });
  expect(await ui.find({ type: "Text", text: "Size: 42x8", in: "custom" })).toBeDefined();
});
