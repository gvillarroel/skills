#!/usr/bin/env node
import { createReadStream, mkdirSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { video } from "../src/video-data.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = resolve(__dirname, "..");
const screenshotDir = resolve(projectDir, "artifacts", "screenshots", "smoke");

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

async function main() {
  mkdirSync(screenshotDir, { recursive: true });
  const staticServer = await startStaticServer(projectDir);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: video.width, height: video.height }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));
  try {
    await page.goto(`${staticServer.url}/index.html`, { waitUntil: "networkidle" });
    await page.evaluate(async () => {
      if (document.fonts?.ready) await document.fonts.ready;
    });
    const times = [0.5, 7.5, 7.9, 12, 15.8, 19, 23.8, 27, 33.6, 37, 41.6, 46.5];
    const states = [];
    for (const time of times) {
      const state = await page.evaluate(({ id, t }) => window.renderConceptFrame(id, t, { capture: true }), {
        id: video.id,
        t: time
      });
      states.push(state);
      if (state.elementCount < 40) throw new Error(`Frame ${time}s is likely blank: ${state.elementCount} elements.`);
      await page.screenshot({ path: join(screenshotDir, `${String(time).replace(".", "p")}s.png`), animations: "disabled" });
    }
    if (errors.length) throw new Error(`Browser errors:\n${errors.join("\n")}`);
    console.log(JSON.stringify({ status: "pass", states }, null, 2));
  } finally {
    await browser.close();
    staticServer.server.close();
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
