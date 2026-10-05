#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/slidev-layout-templates/scripts/test-layout-ssr.ts
// Node 24+. Uses the already installed acceptance deck's Vue/compiler-sfc;
// generated modules stay in ignored project artifacts, never in skill bundles.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire, stripTypeScriptTypes } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const require = createRequire(path.join(root, 'skills/slidev-echarts/assets/examples/slidev-echarts/package.json'));
const compiler = require('@vue/compiler-sfc');
const vueDirectory = path.dirname(require.resolve('vue/package.json'));
const vueUrl = pathToFileURL(path.join(vueDirectory, 'index.mjs')).href;
const ssrUrl = pathToFileURL(path.join(vueDirectory, 'server-renderer/index.mjs')).href;
const { createSSRApp, nextTick } = await import(vueUrl);
const { renderToString } = await import(ssrUrl);
assert.equal(typeof document, 'undefined');
assert.equal(typeof ResizeObserver, 'undefined');
const source = await fs.readFile(path.join(root, 'skills/slidev-echarts/assets/templates/slidev-layouts/components/SlidevLayout.vue'), 'utf8');
const descriptor = compiler.parse(source, { filename: 'SlidevLayout.vue' }).descriptor;
const compiled = compiler.compileScript(descriptor, { id: 'slidev-layout-ssr', inlineTemplate: true, templateOptions: { ssr: true } }).content;
const helperUrl = pathToFileURL(path.join(root, 'skills/slidev-echarts/assets/templates/slidev-layouts/lib/slidev-layouts.mjs')).href;
const runnable = stripTypeScriptTypes(compiled, { mode: 'strip' })
  .replaceAll("from 'vue'", `from '${vueUrl}'`)
  .replaceAll('from "vue"', `from '${vueUrl}'`)
  .replaceAll('from "vue/server-renderer"', `from '${ssrUrl}'`)
  .replaceAll("from '../lib/slidev-layouts.mjs'", `from '${helperUrl}'`);
const artifacts = path.join(root, 'projects/slidev-layout-templates/artifacts/ssr');
await fs.mkdir(artifacts, { recursive: true });
const modulePath = path.join(artifacts, 'SlidevLayout.ssr.mjs');
await fs.writeFile(modulePath, runnable);
const component = (await import(pathToFileURL(modulePath).href)).default;
const items = Array.from({ length: 7 }, (_, index) => ({ id: `item-${index + 1}`, title: `Component ${index + 1}`, body: 'Readable content.', width: 200 }));
let passed = 0;
for (const colorset of ['colorset1', 'colorset2']) {
  for (const mode of ['columns', 'grid', 'masonry-columns', 'masonry-rows']) {
    const rendered = await renderToString(createSSRApp(component, { items, colorset, mode, height: 700 }));
    await nextTick();
    assert.equal((rendered.match(/role="listitem"/g) ?? []).length, 7);
    assert(rendered.includes(`data-layout-mode="${mode}"`));
    assert(rendered.includes(`data-colorset="${colorset}"`));
    assert(rendered.includes('data-layout-fits="true"'));
    for (const item of items) assert(rendered.includes(`data-item-id="${item.id}"`));
    await fs.writeFile(path.join(artifacts, `${colorset}-${mode}.html`), rendered);
    console.log(`PASS SSR ${colorset}/${mode} without document or ResizeObserver`);
    passed++;
  }
}
const parentSource = await fs.readFile(path.join(root, 'skills/slidev-echarts/assets/templates/slidev-layouts/components/SlidevCollection.vue'), 'utf8');
const parentDescriptor = compiler.parse(parentSource, { filename: 'SlidevCollection.vue' }).descriptor;
const parentCompiled = compiler.compileScript(parentDescriptor, { id: 'slidev-collection-ssr', inlineTemplate: true, templateOptions: { ssr: true } }).content;
const parentRunnable = stripTypeScriptTypes(parentCompiled, { mode: 'strip' })
  .replaceAll("from 'vue'", `from '${vueUrl}'`)
  .replaceAll('from "vue"', `from '${vueUrl}'`)
  .replaceAll('from "vue/server-renderer"', `from '${ssrUrl}'`)
  .replaceAll("from '../lib/slidev-layouts.mjs'", `from '${helperUrl}'`)
  .replaceAll("from './SlidevLayout.vue'", `from '${pathToFileURL(modulePath).href}'`);
const parentModulePath = path.join(artifacts, 'SlidevCollection.ssr.mjs');
await fs.writeFile(parentModulePath, parentRunnable);
const parent = (await import(pathToFileURL(parentModulePath).href)).default;
const allItems = Array.from({ length: 11 }, (_, index) => ({ id: `item-${index + 1}`, title: `Component ${index + 1}`, body: 'Readable content.' }));
for (const colorset of ['colorset1', 'colorset2']) {
  for (const mode of ['columns', 'grid', 'masonry-columns', 'masonry-rows']) {
    for (const count of [3, 7, 11]) {
      const rendered = await renderToString(createSSRApp(parent, { items: allItems, count, colorset, mode }));
      await nextTick();
      assert(rendered.includes(`data-collection-count="${count}"`));
      assert(rendered.includes(`data-collection-mode="${mode}"`));
      assert(rendered.includes('aria-label="Previous page"'));
      assert(rendered.includes('aria-label="Next page"'));
      const visible = (rendered.match(/role="listitem"/g) ?? []).length;
      assert.equal(visible, Math.min(count, mode === 'masonry-rows' ? 3 : 9));
      await fs.writeFile(path.join(artifacts, `collection-${colorset}-${mode}-${count}.html`), rendered);
      console.log(`PASS collection SSR ${colorset}/${mode}/${count} without browser globals`);
      passed++;
    }
  }
}
console.log(JSON.stringify({ status: 'pass', passed, boundary: 'native Vue SSR with no browser globals' }));
