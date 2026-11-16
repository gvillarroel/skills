#!/usr/bin/env -S node --experimental-strip-types
// Run with Node.js >=24: node scripts/hf.ts <HyperFrames command>.
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {existsSync} from 'node:fs';
const project = path.resolve(import.meta.dirname, '..');
const candidates = [process.env.HYPERFRAMES_BROWSER_PATH, 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', '/usr/bin/google-chrome', '/usr/bin/chromium',
  '/usr/bin/chromium-browser', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'].filter(Boolean);
const browser = candidates.find(p => existsSync(p!));
const args = process.argv.slice(2);
for (let i=0; i<args.length; i++) {
  if (args[i] === '--output' && args[i+1]) args[i+1] = path.resolve(args[i+1]);
  else if (args[i].startsWith('--output=')) args[i] = '--output=' + path.resolve(args[i].slice(9));
}
const result = spawnSync(process.execPath, ['--import', pathToFileURL(path.join(project, 'scripts/local-runtime.ts')).href,
  path.join(project, 'node_modules/hyperframes/bin/hyperframes.mjs'), ...args], {
  cwd: project, stdio: 'inherit', env: {...process.env,
    npm_config_cache: path.join(project, '.cache/npm'), PUPPETEER_CACHE_DIR: path.join(project, '.cache/browser'),
    HYPERFRAMES_FONT_CACHE_DIR: path.join(project, '.cache/fonts'), HYPERFRAMES_EXTRACT_CACHE_DIR: path.join(project, '.cache/frames'),
    HYPERFRAMES_SKIP_SKILLS: '1', DO_NOT_TRACK: '1', ...(browser ? {HYPERFRAMES_BROWSER_PATH: browser} : {}),
  },
});
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 2);
