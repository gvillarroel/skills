# Gauge Charts In Slidev

- **Data shape:** Use one ratio or score value plus a short KPI label.
- **Animation pattern:** Update `data[0].value` from `$clicks` and enable `detail.valueAnimation`. Keep min/max fixed.
- **Display guidance:** Use gauges for one headline metric with obvious thresholds. Add explanatory text outside the chart rather than extra series.
- **Modules:** Register `GaugeChart`.
- **Pitfalls:** Gauges waste space for comparisons; use bar or bullet-style custom marks for multiple KPIs.
