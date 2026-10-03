/* Pure mathematical transformations. No target programs, network or inference. */
globalThis.BudgetMath = (() => {
  'use strict';
  function capacity(cost, budget=200, probability=1) {
    if (!Number.isFinite(cost) || cost<=0 || !Number.isFinite(budget) || budget<0 || !Number.isFinite(probability) || probability<0 || probability>1) throw new RangeError('Invalid budget, cost or probability.');
    return budget*probability/cost;
  }
  function planning(cost, baseline, budget=200) {
    const runs=capacity(cost,budget), base=capacity(baseline,budget);
    const whole=Math.floor(runs), baselineWhole=Math.floor(base);
    return {runs, whole, baselineWhole, delta:whole-baselineWhole, relative:runs/base-1, sameUseSpend:baselineWhole*cost, sameUseBalance:budget-baselineWhole*cost, perTask:cost};
  }
  function interpolate(rows, x, key, step=false) {
    if (!rows.length) throw new RangeError('An empty curve cannot be interpolated.');
    if (x<=rows[0].x) return rows[0][key];
    if (x>=rows.at(-1).x) return rows.at(-1)[key];
    const j=rows.findIndex(r=>r.x>x), a=rows[j-1], b=rows[j];
    return step ? a[key] : a[key]+(b[key]-a[key])*(x-a.x)/(b.x-a.x);
  }
  function retry(p, cost, k, rho, budget=200) {
    if(!(p>=0&&p<=1&&cost>0&&Number.isInteger(k)&&k>=1&&rho>=0&&rho<=1)) throw new RangeError('Invalid retry inputs.');
    const q=1-p;
    const success=rho*p+(1-rho)*(1-q**k);
    const attempts=rho*(p+k*q)+(1-rho)*(p===0?k:(1-q**k)/p);
    const spend=cost*attempts;
    return {success,attempts,spend,runs:capacity(spend,budget),successful:capacity(spend,budget,success)};
  }
  function routing(p, firstCost, fallbackCost, recovery, budget=200) {
    if(!(p>=0&&p<=1&&recovery>=0&&recovery<=1&&firstCost>0&&fallbackCost>0)) throw new RangeError('Invalid recovery probability or cost.');
    const spend=firstCost+(1-p)*fallbackCost, success=p+(1-p)*recovery;
    return {spend,success,runs:capacity(spend,budget),successful:capacity(spend,budget,success)};
  }
  function reserve(amount,cost,budget=200) {
    if(!(amount>=0&&amount<budget)) throw new RangeError('The reserve must be below the budget.');
    const usable=budget-amount;
    return {usable,runs:capacity(cost,usable),costHeadroom:budget/usable-1};
  }
  return {capacity,planning,interpolate,retry,routing,reserve};
})();
