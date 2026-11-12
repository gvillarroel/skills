// Account-free acceptance fixture; execute with claude plugin test.
export function register(on) {
  let selectedCase = "common";
  let count = 0;
  let input = "";
  let submitted = "";
  let selection = "small";
  on("command.run", { command: "probe-case" }, async ($, e) => {
    selectedCase = e.args;
    return {};
  });
  on("command.run", { command: "probe-open" }, async ($) => {
    const result = await $.ui.open({ id: "desktop-ui-probe", title: "UI probe", rows: 8, columns: 50 });
    return { text: result?.isPlaced === false ? "Use the transcript fallback" : "Pane requested" };
  });
  on("command.run", { command: "probe-environment" }, async () => ({ text: [typeof document, typeof window, typeof process, typeof require].join(",") }));
  on("command.run", { command: "probe-node" }, async () => {
    try { const fs = require("node:fs"); return { text: "Unexpected Node access: " + typeof fs.readFileSync }; }
    catch (error) { return { text: String(error.message) }; }
  });
  on("ui.message", async ($, e) => ({ props: { label: typeof e.data?.label === "string" ? e.data.label.slice(0, 80) : "Validated fallback" } }));
  on("ui.render", { component: "Pane" }, async ($, e) => {
    const { Box, Text, Button, Input, Select, Link, Code, Markdown, Svg, Image, Raster, Client } = $.ui.resolve(e);
    const raw = (type, props) => ({ type, props });
    if (selectedCase.startsWith("html-")) return raw(selectedCase.slice(5), { children: "HTML probe" });
    if (selectedCase.startsWith("href-size-")) return Link({ href: "https://example.com/" + "a".repeat(Number(selectedCase.slice(10)) - 20), label: "Bounded link" });
    if (selectedCase.startsWith("svg-size-")) return raw("Svg", { source: "<svg>" + " ".repeat(Number(selectedCase.slice(9)) - 11) + "</svg>", alt: "Exact source length" });
    if (selectedCase === "raster") return raw("Raster", { key: "raster", columns: 1, rows: 1, cells: "iCUAAACA/wAAAAAB" });
    if (selectedCase === "invalid-raster-bytes") return raw("Raster", { key: "raster", columns: 1, rows: 1, cells: "AAAA" });
    if (selectedCase === "css-injection") return { type: "Box", props: { style: { background: "red" } }, children: [] };
    if (selectedCase === "missing-image-alt") return raw("Image", { source: { rgba: "/wAA/w==", width: 1, height: 1 }, columns: 1, rows: 1 });
    if (selectedCase === "bad-rgba-size") return raw("Image", { source: { rgba: "/wAA/w==", width: 2, height: 1 }, columns: 1, rows: 1, alt: "Wrong pixel count" });
    if (selectedCase === "image-columns-256") return raw("Image", { source: { rgba: "/wAA/w==", width: 1, height: 1 }, columns: 256, rows: 1, alt: "Too wide" });
    if (selectedCase === "image-file-missing") return raw("Image", { source: { file: "C:/synthetic-nonexistent/frame.png", format: "png", generation: 1 }, columns: 2, rows: 1, alt: "Missing file" });
    if (selectedCase === "raw-client") return raw("Client", { key: "custom", module: "./client.ts", props: { label: "Initial" }, width: 30, height: 4 });
    if (selectedCase === "raster-columns-513") return raw("Raster", { key: "raster", columns: 513, rows: 1, cells: "" });
    if (selectedCase === "raster-rows-257") return raw("Raster", { key: "raster", columns: 1, rows: 257, cells: "" });
    if (selectedCase.startsWith("option-size-")) return Select({ key: "bounded-select", options: [{ value: "x".repeat(Number(selectedCase.slice(12))), label: "Bounded option" }], onSelect: () => {} });
    if (selectedCase === "file-link") return Link({ href: "file:///C:/work/result.html", label: "Result" });
    if (selectedCase === "js-link") return Link({ href: "javascript:alert(1)", label: "Invalid" });
    if (selectedCase === "long-link") return Link({ href: "https://example.com/" + "a".repeat(2049), label: "Long" });
    if (selectedCase === "https-link") return Link({ href: "https://example.com/", label: "Example" });
    if (selectedCase === "localhost-link") return Link({ href: "http://localhost:3000/", label: "Local" });
    if (selectedCase === "remote-http-link") return Link({ href: "http://example.com/", label: "Invalid" });
    if (selectedCase === "svg") return raw("Svg", { source: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20" fill="red"/></svg>', alt: "Red square", isInteractive: true });
    if (selectedCase === "long-svg") return raw("Svg", { source: '<svg>' + " ".repeat(131073) + '</svg>', alt: "Oversized" });
    if (selectedCase === "image") return raw("Image", { key: "image", source: { rgba: "/wAA/w==", width: 1, height: 1 }, columns: 2, rows: 1, alt: "Red pixel" });
    if (selectedCase === "resolved-image") return Image({ key: "image", source: { rgba: "/wAA/w==", width: 1, height: 1 }, columns: 2, rows: 1, alt: "Red pixel" });
    if (selectedCase === "resolved-svg") return Svg({ source: '<svg xmlns="http://www.w3.org/2000/svg"/>', alt: "SVG" });
    if (selectedCase === "leaf-children") return { type: "Svg", props: { source: '<svg xmlns="http://www.w3.org/2000/svg"/>', alt: "SVG" }, children: [] };
    if (selectedCase === "invalid-png") return raw("Image", { source: { png: "YWJjZA==" }, columns: 2, rows: 1, alt: "Invalid bytes" });
    if (selectedCase === "invalid-generation") return raw("Image", { source: { file: "C:/work/frame.png", format: "png", generation: 1.5 }, columns: 2, rows: 1, alt: "Invalid generation" });
    if (selectedCase === "invalid-html") return raw("iframe", { src: "https://example.com/" });
    if (selectedCase === "table") return Text({ children: Object.keys($.ui.resolve(e)).sort().join(",") });
    if (selectedCase === "client") return Client({ key: "custom", module: "./client.ts", props: { label: "Initial" }, width: 30, height: 4 });
    if (selectedCase === "copy") return Button({ key: "copy", label: "Copy path", onPress: async () => { await $.ui.copy({ text: "C:/work/result.html" }); } });
    if (selectedCase === "process") return Button({ key: "generate", label: "Generate", onPress: async () => { await $.process.run(["renderer", "--title", "literal $() ; value"], { stdin: '{"count":1}' }); } });
    if (selectedCase === "notifications") return Button({ key: "notify", label: "Notify", onPress: async () => { await $.ui.toast("Complete"); await $.ui.status("1 ready"); $.ui.log("Ready locally"); } });
    if (selectedCase === "autofocus-false") return Button({ key: "bad-focus", label: "Invalid autofocus", autoFocus: false, onPress: () => {} });
    if (selectedCase === "duplicate-select") return Select({ key: "bad-select", options: [{ value: "a", label: "A" }, { value: "a", label: "Duplicate" }], onSelect: () => {} });
    if (selectedCase === "controls") {
      return Box({ flexDirection: "column", gap: "sm", children: [
        Text({ children: `Count: ${count}` }),
        Button({ key: "count", label: "Add one", onPress: () => { count++; $.ui.invalidate("ui.render"); } }),
        Input({ key: "query", label: "Query", value: input, onInput: value => { input = value; $.ui.invalidate("ui.render"); }, onSubmit: value => { submitted = value; $.ui.invalidate("ui.render"); } }),
        Text({ children: `Draft: ${input}` }), Text({ children: `Submitted: ${submitted}` }),
        Select({ key: "size", label: "Size", options: [{ value: "small", label: "Small" }, { value: "large", label: "Large" }], value: selection, onSelect: value => { selection = value; $.ui.invalidate("ui.render"); } }),
        Text({ children: `Selected: ${selection}` }),
      ] });
    }
    return Box({ key: "root", flexDirection: "column", gap: 1, children: [
      Text({ children: "UI probe", weight: "semibold", size: "heading", mono: true, tabular: true }),
      Markdown({ text: "**Formatted** content" }),
      Code({ source: "const ready = true;", language: "typescript" }),
      Link({ href: "https://example.com/", label: "Documentation" }),
      Button({ key: "action", label: "Continue", onPress: () => {} }),
      Input({ key: "input", label: "Text", onSubmit: () => {} }),
      Select({ key: "select", options: [{ value: "a", label: "A" }], onSelect: () => {} }),
    ] });
  });
}
