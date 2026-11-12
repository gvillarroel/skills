#!/usr/bin/env node
// Run with Node24: node projects/desktop-plugin-ui/scripts/probe-native-command.ts <plugin-dir> "/command args" <label>
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
const root=process.cwd();
const [pluginArgument,command,label]=process.argv.slice(2);
if(!pluginArgument||!command?.startsWith("/")||!label||!/^[a-z0-9-]+$/.test(label))throw new Error("Supply an in-repository plugin, native command and stable label");
const plugin=path.resolve(pluginArgument);
if(!plugin.startsWith(root+path.sep))throw new Error("The plugin must stay inside the repository");
const folder=path.join(root,"projects/desktop-plugin-ui/artifacts/plugin-pocs","headless-"+label);
if(fs.existsSync(path.join(folder,"stdout.json")))throw new Error("Refusing to overwrite a retained command probe; choose a new label");
const env={...process.env,CLAUDE_CONFIG_DIR:path.join(folder,"host-state"),CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:"1"};
for(const name of ["ANTHROPIC_API_KEY","ANTHROPIC_AUTH_TOKEN","CLAUDE_CODE_OAUTH_TOKEN","ANTHROPIC_BASE_URL","CLAUDE_CODE_USE_BEDROCK","CLAUDE_CODE_USE_VERTEX","CLAUDE_CODE_USE_FOUNDRY"])delete env[name];
fs.mkdirSync(env.CLAUDE_CONFIG_DIR,{recursive:true});
const args=["-p",command,"--plugin-dir",plugin,"--output-format","json","--no-session-persistence"];
const result=spawnSync("claude",args,{cwd:root,env,encoding:"utf8",timeout:45000,windowsHide:true});
fs.writeFileSync(path.join(folder,"stdout.json"),result.stdout||"");fs.writeFileSync(path.join(folder,"stderr.log"),result.stderr||"");
let receipt;try{receipt=JSON.parse(result.stdout);}catch{}
console.log(JSON.stringify({exitCode:result.status,error:result.error?.message,receipt}));
process.exit(result.status??1);
