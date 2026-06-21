# Candlestick Charts In Slidev

- **Data shape:** Use OHLC arrays in ECharts order `[open, close, low, high]` and stable x-axis labels.
- **Animation pattern:** Update later candles while keeping the time index fixed. Preserve conventional up/down colors.
- **Display guidance:** Use candlesticks for interval movement, not ordinary min-max ranges. Add volume only when the slide has enough room.
- **Modules:** Register `CandlestickChart`, `GridComponent`, and `TooltipComponent`.
- **Pitfalls:** Incorrect OHLC order makes candles visually wrong; verify the array contract before tuning styles.
