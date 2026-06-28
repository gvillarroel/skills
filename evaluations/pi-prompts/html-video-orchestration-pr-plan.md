Use $html-d3-anime-video-workflow to create a PR-specific production plan for a standalone HTML+D3+Anime.js video pipeline.

The requested video is a 24-second GitHub PR explainer for developers. Do not fetch the network and do not build the video. Treat this table as the entire source:

| Field | Value |
| --- | --- |
| PR title | Add streaming retry budget to ingestion workers |
| Change size | 4 files, +126/-38 |
| Main behavior | Workers now retry transient stream disconnects up to a per-job retry budget, then write a terminal failure event. |
| Files | `worker.ts` adds retry loop and budget counter; `events.ts` adds `stream_retry_exhausted`; `config.ts` adds `STREAM_RETRY_BUDGET`; `worker.test.ts` covers success after retry and terminal failure. |
| Audience | Backend engineers reviewing release notes |
| Style | Quiet technical diagram, no voiceover, no music, no captions |

Create the deliverable with a filesystem write, not by putting the plan in your final chat message. Write exactly one file named `production-plan.md` at the workspace root. Do not create `implementation-plan.md`; that filename is wrong for this task. The first section of the file must be a filled "Source Facts" table that copies the PR title, change size, behavior, exact filenames, `stream_retry_exhausted`, `STREAM_RETRY_BUDGET`, audience, and style from this prompt. Do not use placeholders like `_[exact title]_`, `TBD`, or `replace later`; the facts are already supplied. It must include:

- route decision and why this is a PR/code-change source package, not website capture
- project-local source package layout
- a 4-beat storyboard that tiles exactly 24 seconds
- static-layout-before-motion notes
- deterministic renderer contract
- validation gates from source package through final MP4 review

Before your final response, verify that `production-plan.md` exists and is non-empty. The final response can be brief, but the file is the deliverable.
