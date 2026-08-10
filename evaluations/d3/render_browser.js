#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { pathToFileURL } = require("url");

function findPlaywrightCore() {
  const explicit = process.env.HARBOR_PLAYWRIGHT_CORE_PATH;
  if (explicit && fs.existsSync(path.join(explicit, "package.json"))) {
    return explicit;
  }
  const roots = [
    process.env.npm_config_cache,
    process.env.NPM_CONFIG_CACHE,
    path.join(os.homedir(), ".npm"),
  ].filter(Boolean);
  for (const root of roots) {
    const npxRoot = path.join(root, "_npx");
    if (!fs.existsSync(npxRoot)) continue;
    for (const entry of fs.readdirSync(npxRoot).sort().reverse()) {
      const candidate = path.join(npxRoot, entry, "node_modules", "playwright-core");
      if (fs.existsSync(path.join(candidate, "package.json"))) return candidate;
    }
  }
  throw new Error(
    "playwright-core was not found; set HARBOR_PLAYWRIGHT_CORE_PATH or provide it in the declared npm cache"
  );
}

async function main() {
  const [sourceArg, screenshotArg, domArg] = process.argv.slice(2);
  if (!sourceArg || !screenshotArg || !domArg) {
    throw new Error("Usage: render_browser.js <source.html> <screenshot.png> <dom.html>");
  }
  const executablePath = process.env.HARBOR_BROWSER_PATH;
  if (!executablePath || !fs.existsSync(executablePath)) {
    throw new Error(`Chromium executable is unavailable: ${executablePath || "<unset>"}`);
  }
  const { chromium } = require(findPlaywrightCore());
  const browser = await chromium.launch({
    executablePath,
    headless: true,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--disable-background-networking"],
  });
  const pageErrors = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
    page.on("pageerror", error => pageErrors.push(`pageerror: ${error.message}`));
    page.on("console", message => {
      if (message.type() === "error") pageErrors.push(`console: ${message.text()}`);
    });
    await page.goto(pathToFileURL(path.resolve(sourceArg)).href, {
      waitUntil: "load",
      timeout: 45000,
    });
    await page.waitForTimeout(900);
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) await document.fonts.ready;
    });
    if (pageErrors.length) throw new Error(pageErrors.join("\n"));
    fs.mkdirSync(path.dirname(path.resolve(screenshotArg)), { recursive: true });
    fs.mkdirSync(path.dirname(path.resolve(domArg)), { recursive: true });
    await page.screenshot({ path: path.resolve(screenshotArg), fullPage: false });
    fs.writeFileSync(path.resolve(domArg), await page.content(), "utf8");
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  process.stderr.write(`${error.stack || error.message || error}\n`);
  process.exit(1);
});
