#!/usr/bin/env -S node --experimental-strip-types
// Node.js >=24: loaded by scripts/hf.ts before the framework; project-scoped caches.
import os from 'node:os';
import path from 'node:path';
import {mkdirSync} from 'node:fs';
import {syncBuiltinESMExports} from 'node:module';
const project = path.resolve(import.meta.dirname, '..');
const taskHome = path.join(project, '.cache/home'), taskTemp = path.join(project, '.cache/tmp');
mkdirSync(taskHome, {recursive: true}); mkdirSync(taskTemp, {recursive: true});
os.homedir = () => taskHome; os.tmpdir = () => taskTemp;
syncBuiltinESMExports();
