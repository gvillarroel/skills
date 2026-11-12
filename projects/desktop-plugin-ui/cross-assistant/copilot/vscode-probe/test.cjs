const vscode = require('vscode');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const output = path.resolve(__dirname, '../../../artifacts/cross-assistant/copilot/vscode-extension-host.json');
const rows = [];
const panels = [];
async function check(name, fn) {
  try { rows.push({ name, status: 'passed', actual: await fn() }); }
  catch (error) { rows.push({ name, status: 'failed', error: String(error) }); }
}
function panel(options) {
  const result = vscode.window.createWebviewPanel('ui-evidence-probe', 'UI Evidence Probe', vscode.ViewColumn.One, options);
  panels.push(result);
  return result;
}
function nextMessage(view, timeout = 7000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { sub.dispose(); reject(new Error('Webview message timeout')); }, timeout);
    const sub = view.webview.onDidReceiveMessage(message => { clearTimeout(timer); sub.dispose(); resolve(message); });
  });
}
exports.run = async () => {
  try {
    await check('installed-host-and-runtime-extension-inventory', async () => {
      return { vscode: vscode.version, copilotExtensions: vscode.extensions.all
        .filter(ext => /copilot/i.test(ext.id)).map(ext => ({id:ext.id,version:ext.packageJSON.version})),
        totalExtensions: vscode.extensions.all.length };
    });
    await check('webview-scripts-disabled-by-default', async () => {
      const view = panel({});
      let messages = 0;
      const listener = view.webview.onDidReceiveMessage(() => { messages++; });
      view.webview.html = '<!doctype html><html lang="en"><button>Probe</button><script>acquireVsCodeApi().postMessage({ran:true})</script>';
      await new Promise(resolve => setTimeout(resolve, 1600));
      listener.dispose();
      assert.equal(messages, 0);
      const options = { enableScripts: view.webview.options.enableScripts ?? false, receivedMessages: messages };
      view.dispose();
      return options;
    });
    await check('webview-scripts-buttons-bridge-and-isolation', async () => {
      const view = panel({enableScripts: true});
      const got = nextMessage(view);
      view.webview.html = `<!doctype html><html lang="en"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-evidence';"><button id="probe">Probe</button><script nonce="evidence">
        const api = acquireVsCodeApi(); let clicks = 0; document.getElementById('probe').onclick = () => clicks++;
        document.getElementById('probe').click();
        let parentDocument; try { window.parent.document; parentDocument='accessible'; } catch(error) { parentDocument=error.name; }
        let topDocument; try { window.top.document; topDocument='accessible'; } catch(error) { topDocument=error.name; }
        api.postMessage({clicks, parentDocument, topDocument, isTop:window === window.top, requireType:typeof require, processType:typeof process});
        </script>`;
      const value = await got;
      assert.equal(value.clicks, 1);
      assert.equal(value.topDocument, 'SecurityError');
      assert.equal(value.requireType, 'undefined');
      assert.equal(value.processType, 'undefined');
      view.dispose();
      return value;
    });
    await check('webview-csp-blocks-unapproved-inline-script', async () => {
      const view = panel({enableScripts: true});
      const got = nextMessage(view);
      view.webview.html = `<!doctype html><html lang="en"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-evidence';"><script nonce="evidence">
        const api = acquireVsCodeApi(); window.unapproved = false;
        document.addEventListener('securitypolicyviolation', e => api.postMessage({directive:e.effectiveDirective, unapproved:window.unapproved}));
        </script><script>window.unapproved = true;</script>`;
      const value = await got;
      assert.equal(value.unapproved, false);
      assert.match(value.directive, /^script-src/);
      view.dispose();
      return value;
    });
    await check('webview-disposal-event', async () => {
      const view = panel({});
      let disposed = false;
      view.onDidDispose(() => { disposed = true; });
      view.dispose();
      await new Promise(resolve => setTimeout(resolve, 200));
      assert.equal(disposed, true);
      return {disposed};
    });
  } finally {
    for (const item of panels) item.dispose();
    fs.mkdirSync(path.dirname(output), {recursive:true});
    fs.writeFileSync(output, JSON.stringify({timestampUtc:new Date().toISOString(), layer:'real-vscode-extension-host', modelPrompts:0, note:'VS Code extension webviews; this does not prove Copilot MCP App chat rendering.', rows}, null, 2));
  }
  if (rows.some(row => row.status === 'failed')) throw new Error('UI evidence probe had failures: ' + output);
};
