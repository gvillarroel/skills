# Slidev quality-audit wrapped-inline forward test

Use the loaded `slidev-quality-audit` skill to audit the evaluator-supplied two-slide fixture below. The first slide contains readable inline text that wraps into several fragments; it must not receive a `covered-content` finding. The second slide contains a genuine overlay control, which must still receive exactly one `covered-content` finding.

Create the fixture and install its pinned local dependencies by running this exact Bash command:

```bash
mkdir -p fixture outputs && cat > fixture/package.json <<'JSON'
{"name":"slidev-quality-audit-forward-fixture","version":"0.1.0","private":true,"type":"module","dependencies":{"@slidev/cli":"52.16.0","@slidev/theme-default":"0.25.0"},"devDependencies":{"playwright":"1.60.0","tsx":"4.23.12","vite":"8.0.16"}}
JSON
cat > fixture/slides.md <<'SLIDES'
---
theme: default
canvasWidth: 1280
aspectRatio: 16/9
colorSchema: light
---

# Wrapped inline regression

<div class="card"><p class="regression-stage"><span class="wrapped" data-testid="wrapped-inline">The first inline fragment remains fully visible.<br><br>The final inline fragment also remains fully visible.</span><code class="gap-token" data-testid="neighbor-token">audit-token</code></p></div>

---

# Genuine overlay control

<div class="card">A real overlay must remain detectable: <span class="cover-stage"><span data-testid="covered-target">genuinely covered words</span><span class="overlay" aria-label="intentional test overlay"></span></span></div>
SLIDES
cat > fixture/style.css <<'CSS'
.slidev-layout{background:#f7fafc;color:#172033;padding:64px 88px}h1{color:#17365d;font-size:42px;line-height:1.15;margin-bottom:32px}.card{background:#fff;border:2px solid #9fb3c8;border-radius:18px;box-shadow:0 14px 34px rgba(23,54,93,.12);font-size:25px;line-height:1.5;padding:30px 34px;width:520px}.card p{margin:0}.card code{background:#dfeaf4;border-radius:5px;color:#17365d;font-size:22px;padding:2px 6px}.regression-stage{position:relative}.wrapped{color:#174c3c;font-weight:700;line-height:48px}.gap-token{left:160px;position:absolute;top:96px}.cover-stage{display:inline-block;position:relative}.overlay{background:rgba(23,54,93,.94);border-radius:6px;height:100%;inset:0;position:absolute;width:100%;z-index:10}
CSS
cat > fixture/vite.config.ts <<'VITE'
import { defineConfig } from 'vite'

export default defineConfig({
  optimizeDeps: {
    include: ['@fix-webm-duration/fix'],
  },
})
VITE
cd fixture && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --no-package-lock --no-audit --no-fund && cd ..
```

Then run the bundled auditor exactly as follows:

```bash
./fixture/node_modules/.bin/tsx skills/slidev-quality-audit/scripts/audit-slidev-quality.ts --deck fixture --out outputs/audit --screenshots all --strict --channel none --timeout 120000
```

Inspect the generated report. Confirm the first slide has no `covered-content` finding and the second slide has exactly one such finding targeting `covered-target`. Do not modify the copied skill. Required exact outputs:

- `outputs/audit/quality-report.json`
- `outputs/audit/quality-report.md`
- `outputs/audit/screenshots/slide-001-click-00.png`
- `outputs/audit/screenshots/slide-002-click-00.png`
