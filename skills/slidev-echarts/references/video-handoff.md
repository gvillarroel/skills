# Video Handoff

Keep this skill responsible for the ECharts surface only. Before handing a deck to `video`, provide:

- the built deck root and exact start command;
- slide IDs and clamped `$clicks` ranges;
- the chart container selector for every video-used slide;
- deterministic data and stable series IDs or data names;
- the event or promise that proves each `setOption` update and renderer animation has settled;
- expected visible chart state at every recorded click;
- the deck build and browser-verification results;
- requested pause duration after each settled state.

For embedded HyperFrames content, also provide the local composition and resource root, cue times, the applied-seek readiness condition, and the selected static-export time or custom poster. Use [the integration contract](hyperframes-integration.md) and capture the scene only after its frame has reached the requested state.

Do not implement browser recording, WebM/MP4 conversion, narration, scene transitions, or final video review here. The downstream video contract owns those concerns.
