# Pi Durable 1.3.0: tools, extensions, Code Mode, and execution environments

Test date: 2026-10-19. Runtime: Node.js 24.18.0 on Windows. All Pi packages are pinned to 1.3.0 in this project's package manifest. The installed package README, declaration files, and implementation were the authority for the probes. The current upstream main branch may describe features outside this release.

The probes execute a real `Harness` with `MemoryStorage`, a real registry, and the official `fauxProvider`. The provider scripts the model's next tool calls; it does not replace the tool executor, scheduler, schema validation, hooks, nested calls, file tools, shells, QuickJS VM, or image processing. No credentials or external model requests are needed. This establishes runtime behavior, not the quality of a model's autonomous tool choices.

Reproduce from this project directory:

```powershell
node_modules/.bin/tsx.cmd --test scripts/tools.test.ts
```

The final run reported **14 tests: 13 passed, 0 assertion failures, 1 skipped direct integration** in approximately 6.4 seconds. The skipped entry is an explicitly blocked Photon import, not a successful feature check. A separate bundled ESM workaround passed. Machine-readable evidence, the original import stack, local fixtures, and generated ESM bundle are under `artifacts/tools/`; these are local generated artifacts.

## Evidence matrix

| Feature | Outcome | What the probe establishes | Recommended use |
| --- | --- | --- | --- |
| `defineTool`, TypeBox parameters | Passed | Invalid number arguments are rejected before `execute`; valid calls run once. | Give every custom tool a narrow argument schema. |
| `prepareArguments` | Passed | A pure conversion repairs a string number before schema validation. | Repair a small, well-defined model formatting error; still validate the result. |
| `api.output`, `api.details` | Passed | Streamed text becomes the final output when `execute` omits output; the last details are committed. | Progress text for the model/UI, structured details for rendering. |
| Thrown tool errors | Passed | Throwing produces an error tool result containing the error message; the model run can continue. | Execution failures the agent may recover from. |
| Output limits | Passed | A small tail limit retains the last two text lines and drops earlier output. | Long command logs where the final error lines matter. |
| `control.terminate` | Passed | A round in which the tool requests termination settles after one provider request. | Tools that already deliver the final outcome and need no follow-up generation. |
| Nested `api.executeTool` | Passed | Nested tasks return to the caller and create no additional transcript tool results. Missing tools produce diagnostics. | Small deterministic orchestration written in TypeScript. |
| `structuredOutputSchema` | Passed | A nested caller receives a validated object; schema-less text tools return a string. Invalid schema output becomes an `invalid_structured_output` error. | Tools consumed programmatically or through Code Mode. |
| `callers`, `modelTools` | Passed | `callers: ['tools']` remains callable while hidden from the model; a model-only tool is unavailable to nested callers. | Constrain invocation routes and keep the model's offered tool list small. |
| Deferred tools and `tool_search` | Passed | A deferred inventory tool is absent initially, then loaded for the next request and retained in the conversation's resolved tools. | Large integrations or MCP-like catalogs. Small tool lists do not need discovery. |
| Sections, hooks, wrappers | Passed | Sections enter the positional system transcript; hooks alter arguments, block calls, and replace results; wrappers decorate the resolved winner. | Prompt composition, central policy enforcement, metrics, and transformations. |
| Both-channel redaction | Passed | An `afterTool` hook replaces both model output and schema value; the nested caller receives the redacted object. | Redaction of a tool with structured output. Redacting text alone leaves another channel exposed. |
| Registry replacement/uninstall | Passed | Installing an extension with the same name changes subsequent calls; uninstalling the policy removes its hooks/wrapper. | Development reload and controlled implementation replacement. In-flight code is documented to keep its old implementation, but that case was not forced here. |
| Parallel vs sequential | Passed | Two 80 ms calls overlap at peak 2 with parallel settings; sequential settings and a tool-level sequential override have peak 1. | Parallel for independent reads; sequential for order-sensitive actions or shared state. |
| `write`, `edit`, `read` | Passed | Exact replacement persists to disk; offset/limit selects the requested line; unmatched replacement errors. | Coding workflows in a configured execution environment. |
| `bash` on Windows | Passed on this machine | Git Bash executes the `printf` probe through the environment's default shell resolution. | Portable Bash scripts when Git Bash is installed. This does not prove every Windows installation has a shell. |
| `createPowerShellTool` | Passed | PowerShell runs directly, preserves a Unicode text fixture, and exit 7 returns an error with usable structured `exitCode: 7`. | Windows commands and PowerShell-specific scripts. Install it separately; `CodingTools` does not add it. |
| `NodeExecutionEnv.exec` argv | Passed | Direct Node argv execution preserves stdout/stderr stream identity. | Known executables with exact arguments; avoids shell parsing. |
| Node filesystem capabilities | Passed | Binary positional reads, line scans, paged directories, and `not_found` error results work. `listFiles` is absent as documented. | Host file browsing and bounded reads. Supply a walker when `listFiles` is missing. |
| Default Windows watcher | Passed | A file modification is reported using `polling`, approximately 2 seconds later. The watcher is explicitly closed. | Reloaders that tolerate snapshot latency; react to overflow/error events in a production host. |
| Code Mode / QuickJS | Passed | JavaScript calls two tools through `Promise.all`, receives schema objects, stores/loads JSON between calls, introspects tools, and reports an intentional script error. `process` is undefined inside the VM. | Ad hoc computation over many tools with compact model-visible output. The execution environment still controls the powers exposed through tools. |
| Code Mode model catalog | Passed | Catalog lookup/available lookup work; model internals are hidden from `ALL_TOOLS`; wrong-type classifier/image calls fail locally. | Discover model capabilities before requesting the appropriate model type. |
| Image passthrough without processor | Passed | A small PNG produces an image block; an oversized header produces `unsupported_image`. | Already compatible images under model limits, without decoder/resize dependencies. |
| Direct `images/node` Photon import | **Blocked integration** | Import throws before `createNodePhotonImages` can run. | Do not assume this import works in this exact unbundled Node setup. |
| Portable Photon with bundled ESM | Passed workaround | An ESM bundle loads the same Photon JS correctly; `createPhotonImages(wasm)` decodes a valid PNG and the coding read tool returns an image block. | Hosts already built through a bundler, or a deliberate bundled adapter with deployment tests. |

## Important behavior and pitfalls

Parallel tool results enter the transcript when they settle. The failed assertion in the first probe assumed that transcript index zero matched tool-call index zero. The corrected probe correlates results through `toolCallId`. A UI should use call IDs, not transcript positions, to connect outputs to calls.

The normalized faux-provider request uses `TranscriptContext.messages`. Tool declarations are in system messages. There is no `context.tools` property in that provider-facing contract. The initial discovery check incorrectly inspected that property and caused an unanswered generation; the corrected check reads system messages and the resolved conversation agent.

`NodeExecutionEnv({ cwd })` supplies a working directory, not an operating-system sandbox. These probes use only paths and commands under `artifacts/tools`; that choice does not establish a security boundary. Use an appropriately restricted custom/container environment when untrusted model-written tool arguments must be confined. Tool-route restrictions and an undefined `process` inside QuickJS do not revoke the powers of callable tools.

The installed declaration for `NodeWatchOptions` explicitly says that Windows defaults to polling because native directory handles interfere with parent renames. Its polling interval defaults to 2000 ms. The initial 1500 ms watcher assertion was too short; the corrected test allows 5000 ms and observed a change around 2000 ms. It was a probe timing error, not evidence of a broken watcher.

For nested results, `output` is absent: programs consume `structuredOutput`, diagnostics, details, usage, and status. Returning a schema object does not place it in the transcript. Text intended for a model and program values require separate thought, especially for redaction. A tool's `modelTools` visibility and nested-call availability are different decisions.

`settings.toolExecution` and a tool's `executionMode` govern a model-issued tool round. The documented nested-call contract launches calls as the caller makes them; code using `Promise.all` controls that concurrency. The overlap test covers model rounds, while the Code Mode test establishes concurrent nested invocation works. It does not benchmark throughput under load.

## Photon import failure and verified workaround

The direct import fails with:

```text
SyntaxError: The requested module '@silvia-odwyer/photon/photon_rs.js' does not provide an export named 'PhotonImage'
```

The installed Photon package is 0.3.3. Its package metadata has a `module` field pointing to `photon_rs.js`, but no `type: module`; Pi imports named exports from that JS file. In this Node/tsx environment the file is not exposed with the expected ESM exports. The portable `/images` entry has the same static import, so switching entry points alone does not solve the problem. This is the observed package/runtime compatibility problem; it does not establish failure in every bundler, Bun, or Cloudflare deployment.

The workaround test bundles the portable entry as ESM without modifying any installed source. The lab declares esbuild 0.25.12 directly; it initially used the identical version already present through tsx:

```typescript
import { build } from 'esbuild';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
await build({
  entryPoints: [require.resolve('@earendil-works/pi-durable/images')],
  outfile: 'artifacts/tools/photon-portable.mjs',
  bundle: true,
  format: 'esm',
  platform: 'node',
});
const { createPhotonImages } = await import(
  pathToFileURL(resolve('artifacts/tools/photon-portable.mjs')).href
);
const wasm = await readFile(
  require.resolve('@silvia-odwyer/photon/photon_rs_bg.wasm')
);
const images = createPhotonImages(wasm);
```

Use the executable test as the exact reproduction; a production application should declare its bundler dependency explicitly. The bundled processor runs on the calling thread and does not establish the worker-thread behavior of `createNodePhotonImages`. The initial manually supplied base64 PNG had invalid compressed image data; the final fixture is generated deterministically with valid PNG chunks and CRCs. The processor correctly refused the damaged fixture before the valid one was introduced.

## Recommended choice by moment

1. Start with a handful of direct typed tools and a local execution environment. Keep the ordinary agent loop easy to inspect.
2. Use a custom orchestration tool with `api.executeTool` when the plan is stable business logic. Give program-consumed tools explicit output schemas and inspect `isError`/diagnostics or meaningful structured status.
3. Enable Code Mode when the model needs to join, filter, aggregate, or batch many tool results. Expose a small model-facing surface, let scripts call tools, and print only the result useful for the next reasoning step.
4. Add `deferred` plus `tool_search` when the offered tool catalog becomes large. Keep metadata meaningful, because discovery ranks the names, descriptions, and schema text.
5. Run independent lookups in parallel; choose sequential execution when later work depends on earlier writes. Use a narrow policy hook for blocked actions and a wrapper for cross-cutting implementation decoration.
6. Use PowerShell for Windows-specific commands and direct argv execution for known programs. Use Bash when its shell exists and the script calls for it.
7. Use image passthrough for already compatible images. Use the verified bundled portable processor for decoding/normalization in this tested setup; test the full worker import separately before choosing that deployment path.

## Explicit coverage limits

This file does not test live commercial providers, actual classifier answers, actual image generation, arbitrary tool catalogs, production sandbox isolation, model-driven discovery quality, throughput, large-file spilling, image resize/EXIF/BMP variants, worker memory behavior, Cloudflare environments, or crashing/reopening a Code Mode script mid-flight. The source documents deterministic journaling and replay for Code Mode, but a restart test is necessary before claiming its recovery behavior was exercised. Storage and core lifecycle probes belong to other scripts in this project.

All watches, Harness instances, QuickJS sandboxes, and execution environments opened by this test file are closed in `finally` blocks. The tool that throws, malformed arguments, missing tools, blocked calls, unmatched edits, nonzero shell exits, and intentional script errors are expected test inputs; they are asserted recovery paths, not hidden failures.
