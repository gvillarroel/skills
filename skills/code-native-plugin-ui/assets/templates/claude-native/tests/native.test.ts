// Run with the installed native test engine: claude plugin test <plugin>
import { expect, test } from "claude-code/testing";

const EXPECTED = { all: "T-1: open\nT-2: closed\nT-3: open", open: "T-1: open\nT-3: open", closed: "T-2: closed" };
const PANE = {
  plugin: "task-view", component: "Pane", requestId: "task-view",
  viewport: { columns: 100, rows: 30 },
  props: { title: "Task view", isFocused: true, bodyColumns: 60, placement: "inline", scroll: { offset: 0, bodyRows: 12 }, view: {} },
} as const;

test("session.start registers the public command using name", async ($, on) => {
  const names = [];
  on("command.register", ($, event) => { names.push(event.name); return { value: undefined }; });
  on("session.start", () => ({ cwd: "/work" }));
  await $.session.start({ surface: "terminal", isInteractive: true, cwd: "/work" });
  expect(names).toEqual(["task-view"]);
});

test("actual command events use command, and unrelated events pass through", async ($, on) => {
  on("command.run", () => ({ text: "HOST-FALLBACK" }));
  expect((await $.command.run({ command: "task-view", args: "open" })).text).toBe(EXPECTED.open);
  expect((await $.command.run({ command: "unrelated", args: "" })).text).toBe("HOST-FALLBACK");
  // A registration-shaped test input must not stand in for a real command event.
  expect((await $.command.run({ name: "task-view", args: "open" })).text).toBe("HOST-FALLBACK");
});

for (const filter of ["all", "open", "closed"]) test(`direct ${filter} returns exact text without opening a pane`, async ($, on) => {
  let opens = 0;
  on("ui.open", () => { opens++; return { value: { isPlaced: true } }; });
  expect((await $.command.run({ command: "task-view", args: filter })).text).toBe(EXPECTED[filter]);
  expect(opens).toBe(0);
});

test("help and invalid arguments offer the direct routes", async ($) => {
  for (const argument of ["help", "invalid", "open extra"]) {
    const answer = await $.command.run({ command: "task-view", args: argument });
    expect(answer.text).toContain("/task-view all");
    expect(answer.text).toContain("/task-view open");
    if (argument !== "help") expect(answer.text).toContain("Unknown task view");
  }
});

for (const denied of [false, true]) test(denied ? "denied pane has a text fallback" : "unplaced pane has a text fallback", async ($, on) => {
  on("ui.open", () => denied ? { deny: "Unavailable" } : { value: { isPlaced: false } });
  const answer = await $.command.run({ command: "task-view", args: "" });
  expect(answer.text).toContain(EXPECTED.all);
  expect(answer.text).toContain("/task-view open");
});

for (const surface of ["terminal", "desktop"]) for (const columns of [32, 80]) test(`${surface} ${columns}: native selection, close and reopen`, async ($, on) => {
  let closes = 0;
  on("ui.open", () => ({ value: { isPlaced: true } }));
  on("ui.close", ($, event) => { expect(event.id).toBe("task-view"); closes++; return { value: undefined }; });
  await $.command.run({ command: "task-view", args: "" });
  const mount = { ...PANE, surface, viewport: { columns, rows: 24 }, props: { ...PANE.props, bodyColumns: columns } };
  const ui = await $.ui.mount(mount);
  for (const filter of ["all", "open", "closed"]) {
    await ui.select({ key: "view", value: filter });
    expect(await ui.find({ type: "Text", text: EXPECTED[filter] })).toBeDefined();
  }
  await ui.press({ key: "cancel" });
  expect(closes).toBe(1);
  expect((await $.command.run({ command: "task-view", args: "all" })).text).toBe(EXPECTED.all);
  await ui.unmount();
  await $.command.run({ command: "task-view", args: "" });
  const reopened = await $.ui.mount(mount);
  expect(await reopened.find({ type: "Text", text: EXPECTED.all })).toBeDefined();
  await reopened.unmount();
});

test("another pane retains its own host drawing", async ($, on) => {
  on("ui.render", () => ({ type: "Text", props: {}, children: ["HOST-FALLBACK"] }));
  const ui = await $.ui.mount({ ...PANE, requestId: "another-pane", surface: "desktop" });
  expect(await ui.find({ type: "Text", text: "HOST-FALLBACK" })).toBeDefined();
  await ui.unmount();
});
