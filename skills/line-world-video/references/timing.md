# Editable timing

`story.json` contains the only beat-duration source:

```json
{
  "timing": {
    "cloud": 7,
    "relations": 8,
    "travel": 4,
    "compare": 14,
    "history": 9,
    "categories": 8,
    "overview": 6
  }
}
```

These seven values total 56 seconds. Change any value and run `build` again;
later beats shift automatically. The output `timing.json` records each beat's
start, end, duration, focus windows and total duration. No manual edit of GSAP
times or root HTML duration is necessary.

Reveals inside cloud, relationship, category and overview beats use normalized
beat progress. Shortening those beats also accelerates their construction;
camera moves shorten within the same beat so labels can settle before it ends.
The comparison's minimum reading budget and history minimum still apply.

For a slower table, increase `compare`, for example from 14 to 20. For a longer
view of the histories, increase `history`. `travel` affects only the move into
the data region. The preview's playback-speed control changes viewing speed;
it does not change exported timing. Render fps controls temporal sampling,
not story length.

Every beat must be at least 2 seconds. Require `compare >= 2 + 2 * rowCount`
and `history >= 5`; shorter reading windows should fail before rendering.
The starter allocates the comparison's first 2 seconds to arrival and reveal,
then divides the rest equally among rows. Camera transitions occupy a bounded
initial part of their beat; reading holds use the remaining time.

When narration is introduced, place measured speech duration and pauses in the
story before retiming. Do not speed up or trim speech merely to fit a fixed
template. Rebuild, inspect transition midpoints and verify exact duration with
FFprobe after every timing change.

The preview exposes `renderAt(seconds)` for deterministic inspection. Seeking
forward, backward or repeatedly to the same time must produce the same SVG and
focus state. Never make a visual depend on wall time, incremental simulation
ticks, `Math.random()` or an autonomous CSS animation.

Guide radii and point transfers are controlled separately by `attention`.
`emissionSeconds` spreads births within a focus hold; `flightSeconds` controls
the trip to the receiving view. The runtime bounds both to the reading window
when a scene is shortened. These settings do not change exported duration.
Read [attention choreography](attention-choreography.md) for sizes, point units
and category mapping. Rebuild after editing `story.json`.
