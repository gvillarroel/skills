#!/usr/bin/env node
import { createReadStream, mkdirSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { concepts, project } from "../src/concepts.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = resolve(__dirname, "..");
const screenshotRoot = resolve(projectDir, "artifacts", "screenshots", "smoke");
const manifestFile = resolve(projectDir, "artifacts", "manifests", "smoke-render.json");

function contentType(filePath) {
  const types = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png"
  };
  return types[extname(filePath).toLowerCase()] ?? "application/octet-stream";
}

function startStaticServer(root) {
  const staticRoot = resolve(root);
  const server = createServer((request, response) => {
    try {
      const requestUrl = new URL(request.url ?? "/", "http://127.0.0.1");
      const requestedPath = decodeURIComponent(requestUrl.pathname === "/" ? "/index.html" : requestUrl.pathname);
      const filePath = resolve(staticRoot, `.${requestedPath}`);
      if (filePath !== staticRoot && !filePath.startsWith(`${staticRoot}\\`) && !filePath.startsWith(`${staticRoot}/`)) {
        response.writeHead(403);
        response.end("Forbidden");
        return;
      }
      const stat = statSync(filePath);
      if (!stat.isFile()) {
        response.writeHead(404);
        response.end("Not found");
        return;
      }
      response.writeHead(200, { "Content-Type": contentType(filePath) });
      createReadStream(filePath).pipe(response);
    } catch (_) {
      response.writeHead(404);
      response.end("Not found");
    }
  });

  return new Promise((resolveServer) => {
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      resolveServer({ server, url: `http://127.0.0.1:${address.port}` });
    });
  });
}

function sceneTimes(concept) {
  const sceneDuration = concept.runtimeSeconds / concept.scenes.length;
  return concept.scenes.map((_, index) => Number((index * sceneDuration + sceneDuration * 0.5).toFixed(2)));
}

function validateState(state) {
  const failures = [];
  if (state.elementCount < 120) failures.push(`low element count ${state.elementCount}`);
  if (state.textCount < 25) failures.push(`low text count ${state.textCount}`);
  if (state.bbox.x < -60 || state.bbox.y < -60) failures.push(`bbox starts outside frame ${JSON.stringify(state.bbox)}`);
  if (state.bbox.x + state.bbox.width > project.width + 80) failures.push(`bbox exceeds width ${JSON.stringify(state.bbox)}`);
  if (state.bbox.y + state.bbox.height > project.height + 80) failures.push(`bbox exceeds height ${JSON.stringify(state.bbox)}`);
  return failures;
}

async function main() {
  mkdirSync(screenshotRoot, { recursive: true });
  mkdirSync(dirname(manifestFile), { recursive: true });
  const staticServer = await startStaticServer(projectDir);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: project.width, height: project.height }, deviceScaleFactor: 1 });
  const errors = [];
  const states = [];

  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  try {
    await page.goto(`${staticServer.url}/index.html`, { waitUntil: "networkidle" });
    await page.evaluate(async () => {
      if (document.fonts?.ready) await document.fonts.ready;
    });

    for (const concept of concepts) {
      const outDir = resolve(screenshotRoot, concept.id);
      mkdirSync(outDir, { recursive: true });
      for (const time of sceneTimes(concept)) {
        const state = await page.evaluate(({ id, t }) => window.renderConceptFrame(id, t, { capture: true }), {
          id: concept.id,
          t: time
        });
        const failures = validateState(state);
        states.push({ ...state, failures });
        if (failures.length) throw new Error(`${concept.id} at ${time}s failed smoke checks: ${failures.join("; ")}`);
        await page.screenshot({
          path: join(outDir, `${String(time).replace(".", "p")}s.png`),
          animations: "disabled"
        });
      }
    }

    if (errors.length) throw new Error(`Browser errors:\n${errors.join("\n")}`);
    const report = { status: "pass", generatedAt: new Date().toISOString(), concepts: concepts.length, states };
    writeFileSync(manifestFile, JSON.stringify(report, null, 2));
    console.log(JSON.stringify({ status: "pass", concepts: concepts.length, screenshots: states.length }, null, 2));
  } finally {
    await browser.close();
    staticServer.server.close();
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
