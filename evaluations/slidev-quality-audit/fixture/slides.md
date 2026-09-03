---
theme: default
canvasWidth: 1280
aspectRatio: 16/9
colorSchema: light
---

# Wrapped inline regression

<div class="regression-card">
  <p class="regression-stage">
    <span class="wrapped-inline" data-testid="wrapped-inline">The first inline fragment remains fully visible.<br><br>The final inline fragment also remains fully visible.</span>
    <code class="gap-token" data-testid="neighbor-token">audit-token</code>
  </p>
</div>

---

# Genuine overlay control

<div class="control-wrap">
  This second slide confirms that a real overlay is still detected:
  <span class="cover-stage">
    <span data-testid="covered-target">genuinely covered words</span>
    <span class="real-overlay" aria-label="intentional test overlay"></span>
  </span>
</div>
