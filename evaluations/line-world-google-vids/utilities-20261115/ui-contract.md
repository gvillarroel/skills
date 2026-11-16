Use only the loaded line-world-google-vids skill. Keep it read-only. This is an
offline pure-parser test: do not browse or operate an account. Use the bundled
compact AX parser with Node.js on this synthetic accessibility text, saved at
input/state.txt:

```text
0 document Fixture - Google Vids Value: https://docs.google.com/videos/d/fixture/edit
1 button Document status: Saved to Drive.
2 button Insert voiceover
3 button (disabled) Update voiceover
4 text Scene 2 of 3, duration 1 second 200 milliseconds
5 text 00:02.0
6 text 00:03.0
7 group Description: compare.mp4
8 button Scene 2 of 3
9 tab item (selectable) All scenes
10 list item option Unrelated confidential file
```

Write its complete structured result to output/summary.json. Verify that it
keeps the fresh scene-card index, All scenes tab index, enabled insertion
control and native duration text, while omitting the unrelated file and the
disabled update control. Also parse `0 document Downloads Value: chrome://downloads/`
and write output/guard.json. That result must be recognized=false. Do not claim
that this parser operates the interface or bypasses a host URL verification stop.
