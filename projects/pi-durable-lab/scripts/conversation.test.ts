import assert from "node:assert/strict";
import test from "node:test";
import { setTimeout as delay } from "node:timers/promises";
import { BACKGROUND_CONTEXT, withAbortSignal, awaitWithContext } from "@earendil-works/chord/context";
import { createModels } from "@earendil-works/pi-ai/models";
import { Type } from "@earendil-works/pi-ai";
import { fauxProvider, fauxAssistantMessage, fauxToolCall } from "@earendil-works/pi-ai/providers/faux";
import {
  Harness, MemoryStorage, createRegistry, defineExtension, defineTool, section,
  ConversationBusy, ProviderDoc, UsageDoc, LiveDoc, CompactionTask, hook, watchEvents, configure, defineTask,
} from "@earendil-works/pi-durable";

// These probes use the real Harness and official deterministic faux provider.
// Every wait is bounded; cleanup always uses the uncancelled background context.
const bg = BACKGROUND_CONTEXT;
const bounded = (ms = 5000) => withAbortSignal(AbortSignal.timeout(ms), bg);
const options = { timeout: 10000 };
const done = async (submission: any) => {
  const result = await submission.wait(bounded());
  assert.equal(result.status, "done", JSON.stringify(result));
  return result;
};
const text = (value: unknown) => JSON.stringify(value);
function gate() {
  let resolve!: () => void;
  const promise = new Promise<void>((r) => { resolve = r; });
  return { promise, resolve };
}
async function eventually(check: () => boolean | Promise<boolean>, message: string) {
  const deadline = Date.now() + 4000;
  while (!(await check())) {
    if (Date.now() >= deadline) assert.fail(message);
    await delay(5);
  }
}
async function lab(extra: any = {}) {
  const faux = fauxProvider({ models: [{ id: "faux-1", contextWindow: 32000 }, { id: "faux-2" }], ...extra.faux });
  const models = createModels();
  models.setProvider(faux.provider);
  const registry = createRegistry();
  for (const extension of extra.extensions ?? []) registry.install(extension);
  const reports: unknown[] = [];
  const harness = await Harness.open(extra.storage ?? new MemoryStorage(), {
    models, registry, onReport: (error: unknown) => reports.push(error),
    settings: { retry: { enabled: false }, compaction: { enabled: false, keepRecentTokens: 1 }, ...extra.settings },
  }, bounded());
  const root = await harness.root(bounded(), { agent: { model: { provider: faux.models[0].provider, modelId: "faux-1" } } });
  return { faux, models, registry, reports, harness, root };
}
async function withLab(run: (value: Awaited<ReturnType<typeof lab>>) => Promise<void>, extra: any = {}) {
  const value = await lab(extra);
  try { await run(value); assert.deepEqual(value.reports, [], "Harness reported an unexpected nonfatal failure"); }
  finally { await value.harness.close(bg); }
}
function holdingExtension() {
  const entered = gate();
  const release = gate();
  const tool = defineTool({
    name: "hold", description: "Wait for the local test latch", parameters: Type.Object({}), replay: "safe",
    execute: async (_args, _api, context) => {
      entered.resolve();
      await awaitWithContext(release.promise, context);
      return { output: [{ type: "text", text: "released" }] };
    },
  });
  return { entered, release, extension: defineExtension({ name: "holding", tools: [tool] }) };
}

test("C01 basic input, requestId idempotency, reacquisition and custom entry", options, async () => {
  await withLab(async ({ root, faux, harness }) => {
    faux.setResponses([fauxAssistantMessage("Paris")]);
    const one = await root.submit({ type: "input", content: "Capital of France?", requestId: "capital", entry: { kind: "chat.mention", data: { author: "tester" } } }, bounded());
    const settled = await done(one);
    const again = await root.submit({ type: "input", content: "ignored duplicate", requestId: "capital" }, bounded());
    assert.equal(again.id, one.id);
    assert.equal((await harness.submission(one.id, bounded()))?.id, one.id);
    assert.equal(faux.state.callCount, 1);
    const answer = await root.commit((tx) => tx.entry(settled.answer), bounded());
    assert.match(text(answer), /Paris/);
    const entries = await root.entries({ order: "ascending" }, 100, undefined, bounded());
    assert.equal(entries.items.filter((entry) => entry.kind === "chat.mention").length, 1);
    assert.match(text((await root.context(bounded())).messages), /Capital of France/);
    assert.doesNotMatch(text((await root.context(bounded())).messages), /ignored duplicate/);
  });
});

test("C02 passive writes append immediately without model calls", options, async () => {
  await withLab(async ({ root, faux }) => {
    const written = await done(await root.submit({ type: "write", entry: { kind: "app.note", data: "display only" } }, bounded()));
    assert.equal(written.type, "write");
    assert.equal(faux.state.callCount, 0);
    assert.match(text((await root.entries({}, 100, undefined, bounded())).items), /display only/);
    assert.doesNotMatch(text((await root.context(bounded())).messages), /display only/);
  });
});

test("C03 follow-up starts a new run; passive writes bypass queue; queued abort withdraws", options, async () => {
  const hold = holdingExtension();
  await withLab(async ({ root, faux }) => {
    try {
      faux.setResponses([fauxAssistantMessage(fauxToolCall("hold", {}), { stopReason: "toolUse" }), fauxAssistantMessage("first answer"), fauxAssistantMessage("follow-up answer")]);
      const first = await root.submit({ type: "input", content: "first" }, bounded());
      await awaitWithContext(hold.entered.promise, bounded());
      const follow = await root.submit({ type: "input", content: "follow" }, bounded());
      const withdrawn = await root.submit({ type: "input", content: "withdraw me" }, bounded());
      assert.equal((await follow.status(bounded())).status, "queued");
      assert.equal(await withdrawn.abort(bounded()), "aborted");
      assert.equal((await withdrawn.wait(bounded())).status, "unanswered");
      await done(await root.submit({ type: "write", entry: { kind: "app.note", data: "visible mid-tool" } }, bounded()));
      assert.equal((await follow.status(bounded())).status, "queued");
      hold.release.resolve();
      const [a, b] = await Promise.all([done(first), done(follow)]);
      assert.notEqual(a.answer, b.answer);
      assert.equal(faux.state.callCount, 3);
      assert.doesNotMatch(text((await root.context(bounded())).messages), /withdraw me|visible mid-tool/);
    } finally { hold.release.resolve(); }
  }, { extensions: [hold.extension] });
});

test("C04 steer joins the current run after a tool round; reject writes nothing", options, async () => {
  const hold = holdingExtension();
  await withLab(async ({ root, faux }) => {
    try {
      const observed: string[] = [];
      faux.setResponses([fauxAssistantMessage(fauxToolCall("hold", {}), { stopReason: "toolUse" }), (context) => { observed.push(text(context)); return fauxAssistantMessage("steered answer"); }]);
      const first = await root.submit({ type: "input", content: "first" }, bounded());
      await awaitWithContext(hold.entered.promise, bounded());
      await assert.rejects(root.submit({ type: "input", content: "reject marker", whenBusy: "reject" }, bounded()), ConversationBusy);
      const steer = await root.submit({ type: "input", content: "steer marker", whenBusy: "steer" }, bounded());
      assert.equal((await steer.status(bounded())).status, "queued");
      hold.release.resolve();
      const [a, b] = await Promise.all([done(first), done(steer)]);
      assert.equal(a.answer, b.answer);
      assert.match(observed[0], /steer marker/);
      assert.doesNotMatch(text((await root.context(bounded())).messages), /reject marker/);
      assert.equal(faux.state.callCount, 2);
    } finally { hold.release.resolve(); }
  }, { extensions: [hold.extension] });
});

test("C05 cancelling only a waiter leaves generation running; conversation abort stops it", options, async () => {
  const hold = holdingExtension();
  await withLab(async ({ root, faux }) => {
    try {
      faux.setResponses([fauxAssistantMessage(fauxToolCall("hold", {}), { stopReason: "toolUse" })]);
      const first = await root.submit({ type: "input", content: "wait test" }, bounded());
      await awaitWithContext(hold.entered.promise, bounded());
      await assert.rejects(first.wait(bounded(30)));
      assert.equal((await first.status(bounded())).status, "placed");
      const queued = await root.submit({ type: "input", content: "queued" }, bounded());
      await root.abort(bounded());
      assert.equal((await first.wait(bounded())).status, "unanswered");
      assert.equal((await queued.wait(bounded())).status, "unanswered");
      await root.waitForIdle(bounded());
    } finally { hold.release.resolve(); }
  }, { extensions: [hold.extension] });
});

test("C06 provider UUID is stable across reset and model change; fork gets fresh UUID", options, async () => {
  await withLab(async ({ root, faux, harness }) => {
    const sessions: string[] = [];
    faux.setResponses([(_context, request) => { sessions.push(request!.sessionId!); return fauxAssistantMessage("one"); }, (_context, request) => { sessions.push(request!.sessionId!); return fauxAssistantMessage("two"); }]);
    const first = await done(await root.submit({ type: "input", content: "original" }, bounded()));
    const before = await harness.snapshot(ProviderDoc, root.id, bounded());
    assert.match(before!.sessionId, /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
    const fork = await root.fork(first.answer, { ownership: { kind: "ownerless" } }, bounded());
    assert.notEqual((await harness.snapshot(ProviderDoc, fork.id, bounded()))!.sessionId, before!.sessionId);
    await root.reset("handoff context", bounded());
    await root.configure({ model: { provider: "faux", modelId: "faux-2" } }, bounded());
    await done(await root.submit({ type: "input", content: "next" }, bounded()));
    assert.deepEqual(sessions, [before!.sessionId, before!.sessionId]);
    assert.equal((await harness.snapshot(ProviderDoc, root.id, bounded()))!.sessionId, before!.sessionId);
  });
});

test("C07 fork copies history and agent as of cut; branches remain independent", options, async () => {
  await withLab(async ({ root, faux }) => {
    faux.setResponses([fauxAssistantMessage("shared answer"), fauxAssistantMessage("parent answer"), fauxAssistantMessage("fork answer")]);
    await root.configure({ instructions: "instruction at cut" }, bounded());
    const cut = await done(await root.submit({ type: "input", content: "shared context" }, bounded()));
    await root.configure({ instructions: "new parent instruction" }, bounded());
    const fork = await root.fork(cut.answer, { ownership: { kind: "ownerless" } }, bounded());
    assert.equal((await fork.agent(bounded())).instructions, "instruction at cut");
    await done(await root.submit({ type: "input", content: "parent only marker" }, bounded()));
    await done(await fork.submit({ type: "input", content: "fork only marker" }, bounded()));
    const parentContext = text((await root.context(bounded())).messages);
    const forkContext = text((await fork.context(bounded())).messages);
    assert.match(forkContext, /shared context/);
    assert.doesNotMatch(forkContext, /parent only marker/);
    assert.doesNotMatch(parentContext, /fork only marker/);
    assert.doesNotMatch(text((await root.context(bounded(), { at: cut.answer })).messages), /parent only marker/);
  });
});

test("C08 configure extensions, modelTools, instructions, cwd; null restores host tools", options, async () => {
  const alpha = defineTool({ name: "alpha", description: "alpha", parameters: Type.Object({}), execute: async () => ({}) });
  const beta = defineTool({ name: "beta", description: "beta", parameters: Type.Object({}), execute: async () => ({}) });
  const first = defineExtension({ name: "first", tools: [alpha], sections: [section("preamble", () => "stable preamble", { tag: false })] });
  const second = defineExtension({ name: "second", tools: [beta] });
  await withLab(async ({ root, faux, registry }) => {
    await root.configure({ tools: [alpha, beta], modelTools: [alpha], instructions: "local instructions", cwd: "/sandbox", thinkingLevel: "high" }, bounded());
    const agent = await root.agent(bounded());
    assert.deepEqual(agent.tools.map((tool) => tool.name), ["alpha"]);
    assert.deepEqual(agent.callable.map((tool) => tool.name), ["alpha", "beta"]);
    assert.equal(agent.cwd, "/sandbox");
    let request = "";
    faux.setResponses([(context) => { request = text(context); return fauxAssistantMessage("configured"); }]);
    await done(await root.submit({ type: "input", content: "configured request" }, bounded()));
    assert.match(request, /stable preamble/);
    assert.match(request, /local instructions/);
    await root.configure({ extensions: { remove: [second] }, tools: null, modelTools: null }, bounded());
    assert.deepEqual((await root.agent(bounded())).tools.map((tool) => tool.name), ["alpha"]);
    registry.uninstall(first);
    assert.deepEqual((await root.agent(bounded())).tools, []);
    registry.install(first);
    assert.deepEqual((await root.agent(bounded())).tools.map((tool) => tool.name), ["alpha"]);
  }, { extensions: [first, second] });
});

test("C09 reset hides previous context while full history stays; handoff becomes user context", options, async () => {
  await withLab(async ({ root, faux }) => {
    faux.setResponses([fauxAssistantMessage("old answer")]);
    await done(await root.submit({ type: "input", content: "old secret marker" }, bounded()));
    await root.reset(undefined, bounded());
    assert.deepEqual((await root.context(bounded())).messages, []);
    assert.match(text((await root.entries({}, 100, undefined, bounded())).items), /old secret marker/);
    await root.reset("handoff marker", bounded());
    assert.match(text((await root.context(bounded())).messages), /handoff marker/);
    assert.doesNotMatch(text((await root.context(bounded())).messages), /old secret marker/);
  });
});

test("C10 reset during tools ends current run and applies handoff", options, async () => {
  const hold = holdingExtension();
  await withLab(async ({ root, faux }) => {
    try {
      faux.setResponses([fauxAssistantMessage(fauxToolCall("hold", {}), { stopReason: "toolUse" })]);
      const first = await root.submit({ type: "input", content: "before reset" }, bounded());
      await awaitWithContext(hold.entered.promise, bounded());
      await root.reset("continue from reset", bounded());
      hold.release.resolve();
      const settled = await first.wait(bounded());
      assert.equal(settled.status, "unanswered");
      assert.equal(settled.reason, "reset");
      const context = text((await root.context(bounded())).messages);
      assert.match(context, /continue from reset/);
      assert.doesNotMatch(context, /before reset/);
      assert.equal(faux.state.callCount, 1);
    } finally { hold.release.resolve(); }
  }, { extensions: [hold.extension] });
});

test("C11 viewState and serialized watch observe committed changes", options, async () => {
  await withLab(async ({ root, faux }) => {
    const view = await root.viewState(bg);
    const watch = await root.watch(bg);
    let observed = 0;
    let opsCount = 0;
    let viewCount = 0;
    const unsubscribe = view.subscribe(() => { viewCount++; });
    watch.start(async (_value, ops) => { observed++; opsCount += ops.length; });
    try {
      faux.setResponses([fauxAssistantMessage("observed answer")]);
      await done(await root.submit({ type: "input", content: "observe me" }, bounded()));
      await eventually(() => observed > 0 && text(watch.value).includes("observed answer"), "watch did not advance");
      assert.ok(viewCount > 0);
      assert.ok(opsCount > 0);
      assert.match(text(view.value), /observed answer/);
    } finally {
      if (typeof unsubscribe === "function") unsubscribe();
      view.dispose();
      assert.equal((await watch.stop()).reason, "stopped");
    }
  });
});

test("C12 watchEvents produces snapshot, lifecycle and usage events", options, async () => {
  await withLab(async ({ root, faux, harness }) => {
    const stream = await watchEvents(harness, root.id, bg);
    const types: string[] = [];
    assert.equal(stream.snapshot.type, "snapshot");
    stream.start(async (events) => { types.push(...events.map((event) => event.type)); });
    try {
      faux.setResponses([fauxAssistantMessage("event answer")]);
      await done(await root.submit({ type: "input", content: "events" }, bounded()));
      await eventually(() => types.includes("run_end"), "missing run_end event");
      for (const type of ["run_start", "turn_start", "message_start", "message_end", "submission", "usage_changed"]) assert.ok(types.includes(type), `missing ${type}`);
    } finally { assert.equal((await stream.stop()).reason, "stopped"); }
  });
});

test("C13 manual compaction hook summary shrinks active context, preserves history and UUID", options, async () => {
  let requestedInstructions: string | undefined;
  const compact = defineExtension({ name: "summary", hooks: [hook(CompactionTask, { beforeCompact: (request) => { requestedInstructions = request.instructions; return { summary: "condensed summary marker" }; } })] });
  await withLab(async ({ root, faux, harness }) => {
    faux.setResponses([fauxAssistantMessage("first long answer " + "a".repeat(300)), fauxAssistantMessage("second long answer " + "b".repeat(300)), fauxAssistantMessage("recent answer")]);
    for (const content of ["older detail marker " + "x".repeat(300), "middle detail " + "y".repeat(300), "recent input"]) await done(await root.submit({ type: "input", content }, bounded()));
    const session = (await harness.snapshot(ProviderDoc, root.id, bounded()))!.sessionId;
    const before = (await root.context(bounded())).entries.length;
    const taskId = await root.compact("preserve test names", bounded());
    const task = await harness.waitForTask(taskId, bounded());
    assert.equal(task.state.outcome.status, "completed", text(task.state.outcome));
    const submissionId = (task.state.outcome as any).result.submissionId;
    assert.ok(submissionId);
    await done((await harness.submission(submissionId, bounded()))!);
    const after = await root.context(bounded());
    assert.equal(requestedInstructions, "preserve test names");
    assert.match(text(after.messages), /condensed summary marker/);
    assert.doesNotMatch(text(after.messages), /older detail marker/);
    assert.ok(after.entries.length < before);
    assert.match(text((await root.entries({}, 100, undefined, bounded())).items), /older detail marker/);
    assert.equal((await harness.snapshot(ProviderDoc, root.id, bounded()))!.sessionId, session);
    assert.equal(faux.state.callCount, 3, "hook supplied summary should avoid a provider request");
  }, { extensions: [compact] });
});

test("C14 compaction may decline; default summarizer calls provider and adds usage", options, async () => {
  await withLab(async ({ root, faux, harness, registry }) => {
    faux.setResponses([fauxAssistantMessage("old answer"), fauxAssistantMessage("recent answer"), fauxAssistantMessage("provider summary marker")]);
    for (const content of ["old message " + "a".repeat(200), "recent message"]) await done(await root.submit({ type: "input", content }, bounded()));
    const decline = defineExtension({ name: "decline", hooks: [hook(CompactionTask, { beforeCompact: () => ({ decline: true }) })] });
    registry.install(decline);
    const declined = await harness.waitForTask(await root.compact(undefined, bounded()), bounded());
    assert.equal(declined.state.outcome.status, "completed");
    assert.deepEqual((declined.state.outcome as any).result, {});
    registry.uninstall(decline);
    const usageBefore = (await harness.usage(bounded())).models["faux/faux-1"].totalTokens;
    const compacted = await harness.waitForTask(await root.compact(undefined, bounded()), bounded());
    assert.equal(compacted.state.outcome.status, "completed", text(compacted.state.outcome));
    const submissionId = (compacted.state.outcome as any).result.submissionId;
    await done((await harness.submission(submissionId, bounded()))!);
    assert.match(text((await root.context(bounded())).messages), /provider summary marker/);
    assert.ok((await harness.usage(bounded())).models["faux/faux-1"].totalTokens > usageBefore);
    assert.equal(faux.state.callCount, 3);
  });
});

test("C15 usage aggregates independent conversation spend and counts failed attempts", options, async () => {
  await withLab(async ({ root, faux, harness }) => {
    faux.setResponses([fauxAssistantMessage("response one"), fauxAssistantMessage("response two"), fauxAssistantMessage("", { stopReason: "error", errorMessage: "invalid API key" })]);
    await done(await root.submit({ type: "input", content: "root input" }, bounded()));
    const other = await harness.createConversation({ ownership: { kind: "ownerless" }, agent: { model: { provider: "faux", modelId: "faux-1" } } }, bounded());
    await done(await other.submit({ type: "input", content: "other input" }, bounded()));
    const rootSpend = (await harness.snapshot(UsageDoc, root.id, bounded()))!.models["faux/faux-1"].totalTokens;
    const otherSpend = (await harness.snapshot(UsageDoc, other.id, bounded()))!.models["faux/faux-1"].totalTokens;
    assert.equal((await harness.usage(bounded())).models["faux/faux-1"].totalTokens, rootSpend + otherSpend);
    const failure = await (await root.submit({ type: "input", content: "failure input" }, bounded())).wait(bounded());
    assert.equal(failure.status, "unanswered");
    assert.equal(failure.reason, "model_error");
    assert.ok((await harness.snapshot(UsageDoc, root.id, bounded()))!.models["faux/faux-1"].totalTokens > rootSpend);
  });
});

test("C16 retryable model failure retries, nonretryable failure settles unanswered", options, async () => {
  await withLab(async ({ root, faux }) => {
    faux.setResponses([fauxAssistantMessage("", { stopReason: "error", errorMessage: "429 rate limit exceeded" }), fauxAssistantMessage("recovered")]);
    await done(await root.submit({ type: "input", content: "retry" }, bounded()));
    assert.equal(faux.state.callCount, 2);
    faux.setResponses([fauxAssistantMessage("", { stopReason: "error", errorMessage: "400 invalid request" })]);
    const failed = await (await root.submit({ type: "input", content: "do not retry invalid input" }, bounded())).wait(bounded());
    assert.equal(failed.status, "unanswered");
    assert.equal(failed.reason, "model_error");
    assert.equal(faux.state.callCount, 3);
    faux.setResponses([fauxAssistantMessage("", { stopReason: "error", errorMessage: "429 insufficient_quota: billing limit" })]);
    const quota = await (await root.submit({ type: "input", content: "account quota is not a transient throttle" }, bounded())).wait(bounded());
    assert.equal(quota.status, "unanswered");
    assert.equal(quota.reason, "model_error");
    assert.equal(faux.state.callCount, 4, "quota/billing 429 must not be retried");
  }, { settings: { retry: { enabled: true, maxRetries: 1, baseDelayMs: 1 } } });
});

test("C17 deferred provider submission polls to a final answer", options, async () => {
  await withLab(async ({ root, faux }) => {
    faux.setResponses([fauxAssistantMessage("deferred final marker")]);
    await done(await root.submit({ type: "input", content: "run deferred" }, bounded()));
    assert.equal(faux.state.callCount, 1);
    assert.ok(faux.state.deferredFetchCount >= 2);
    assert.match(text((await root.context(bounded())).messages), /deferred final marker/);
  }, { faux: { deferred: { pendingFetches: 1, pollAfterMs: 1 } }, settings: { stream: { deferred: true } } });
});

test("C18 followUpMode all groups queued inputs; model-visible write waits for boundary", options, async () => {
  const hold = holdingExtension();
  await withLab(async ({ root, faux }) => {
    try {
      const requests: string[] = [];
      faux.setResponses([
        fauxAssistantMessage(fauxToolCall("hold", {}), { stopReason: "toolUse" }),
        (context) => { requests.push(text(context)); return fauxAssistantMessage("first result"); },
        (context) => { requests.push(text(context)); return fauxAssistantMessage("grouped follow-ups result"); },
      ]);
      const first = await root.submit({ type: "input", content: "initial" }, bounded());
      await awaitWithContext(hold.entered.promise, bounded());
      const followOne = await root.submit({ type: "input", content: "follow one marker" }, bounded());
      const followTwo = await root.submit({ type: "input", content: "follow two marker" }, bounded());
      const write = await root.submit({ type: "write", entry: { kind: "app.context", data: "context write", model: [{ role: "user", content: "model visible marker", timestamp: Date.now() }] } }, bounded());
      assert.equal((await write.status(bounded())).status, "queued");
      hold.release.resolve();
      const [initial, a, b] = await Promise.all([done(first), done(followOne), done(followTwo)]);
      await done(write);
      assert.notEqual(initial.answer, a.answer);
      assert.equal(a.answer, b.answer);
      assert.match(requests[0], /model visible marker/);
      assert.doesNotMatch(requests[0], /follow one marker|follow two marker/);
      assert.match(requests[1], /follow one marker/);
      assert.match(requests[1], /follow two marker/);
      assert.equal(faux.state.callCount, 3);
    } finally { hold.release.resolve(); }
  }, { extensions: [hold.extension], settings: { followUpMode: "all" } });
});

test("C19 a tool handoff resets context and settles done with the tool-call assistant", options, async () => {
  const handoff = defineTool({ name: "handoff", description: "Transfer context", parameters: Type.Object({}), execute: async () => ({ output: [{ type: "text", text: "saved" }], control: { handoff: "tool handoff marker" } }) });
  await withLab(async ({ root, faux }) => {
    faux.setResponses([fauxAssistantMessage(fauxToolCall("handoff", {}), { stopReason: "toolUse" })]);
    const settled = await (await root.submit({ type: "input", content: "old handoff context" }, bounded())).wait(bounded());
    // Tool-driven handoff intentionally settles done, unlike a queued host reset.
    // Its answer is the assistant that asked for the tool, not a fresh text answer.
    assert.equal(settled.status, "done");
    const answer = await root.commit((tx) => tx.entry((settled as any).answer), bounded());
    assert.match(text(answer), /toolCall/);
    const context = text((await root.context(bounded())).messages);
    assert.match(context, /tool handoff marker/);
    assert.doesNotMatch(context, /old handoff context/);
    assert.equal(faux.state.callCount, 1);
  }, { extensions: [defineExtension({ name: "handoff", tools: [handoff] })] });
});

test("C20 automatic blocking compaction executes before the next provider request", options, async () => {
  const reasons: string[] = [];
  const summary = defineExtension({ name: "auto-summary", hooks: [hook(CompactionTask, { beforeCompact: (request) => { reasons.push(request.reason); return { summary: "automatic compact marker" }; } })] });
  await withLab(async ({ root, faux }) => {
    let secondRequest = "";
    faux.setResponses([fauxAssistantMessage("first answer " + "a".repeat(800)), (context) => { secondRequest = text(context); return fauxAssistantMessage("second answer"); }]);
    await done(await root.submit({ type: "input", content: "old automatic context " + "a".repeat(800) }, bounded()));
    await done(await root.submit({ type: "input", content: "new input" }, bounded()));
    assert.deepEqual(reasons, ["threshold"]);
    assert.match(secondRequest, /automatic compact marker/);
    assert.doesNotMatch(secondRequest, /old automatic context/);
    assert.equal(faux.state.callCount, 2);
  }, { extensions: [summary], faux: { models: [{ id: "faux-1", contextWindow: 300 }] }, settings: { compaction: { enabled: true, reserveTokens: 100, keepRecentTokens: 1, backgroundTokens: 0 } } });
});

test("C21 a blocking compaction failure prevents generation; failure remains visible", options, async () => {
  await withLab(async ({ root, faux, harness }) => {
    faux.setResponses([fauxAssistantMessage("first answer " + "a".repeat(800)), fauxAssistantMessage("", { stopReason: "error", errorMessage: "400 summary rejected" })]);
    await done(await root.submit({ type: "input", content: "old context " + "a".repeat(800) }, bounded()));
    const failed = await (await root.submit({ type: "input", content: "new input" }, bounded())).wait(bounded());
    assert.equal(failed.status, "unanswered");
    assert.equal(failed.reason, "model_error");
    assert.match(text(failed.detail), /Compaction failed:.*summary rejected/);
    const live = await harness.snapshot(LiveDoc, root.id, bounded());
    assert.match(text(live!.compactionFailure), /summary rejected/);
    assert.equal(faux.state.callCount, 2, "second provider request is summarization; generation must not run");
  }, { faux: { models: [{ id: "faux-1", contextWindow: 300 }] }, settings: { compaction: { enabled: true, reserveTokens: 100, keepRecentTokens: 1, backgroundTokens: 0 } } });
});

test("C22 context overflow compacts and retries once", options, async () => {
  const reasons: string[] = [];
  const summary = defineExtension({ name: "overflow-summary", hooks: [hook(CompactionTask, { beforeCompact: (request) => { reasons.push(request.reason); return { summary: "overflow summary" }; } })] });
  await withLab(async ({ root, faux }) => {
    faux.setResponses([fauxAssistantMessage("old answer"), fauxAssistantMessage("", { stopReason: "error", errorMessage: "Your input exceeds the context window of this model" }), fauxAssistantMessage("recovered overflow")]);
    await done(await root.submit({ type: "input", content: "old input" }, bounded()));
    await done(await root.submit({ type: "input", content: "overflow input" }, bounded()));
    assert.deepEqual(reasons, ["overflow"]);
    assert.equal(faux.state.callCount, 3);
    assert.match(text((await root.context(bounded())).messages), /recovered overflow/);
  }, { extensions: [summary], settings: { compaction: { enabled: true, reserveTokens: 100, keepRecentTokens: 1, backgroundTokens: 0 } } });
});

test("C23 abort cancels an outstanding deferred provider handle", options, async () => {
  await withLab(async ({ root, faux, harness }) => {
    faux.setResponses([fauxAssistantMessage("must never finish")]);
    const submission = await root.submit({ type: "input", content: "deferred cancellation" }, bounded());
    await eventually(async () => (await harness.snapshot(LiveDoc, root.id, bounded()))?.generation?.deferred !== undefined, "deferred handle never became visible");
    await root.abort(bounded());
    assert.equal((await submission.wait(bounded())).status, "unanswered");
    assert.equal(faux.state.cancelledDeferred.length, 1);
    assert.equal(faux.state.deferredFetchCount, 0);
  }, { faux: { deferred: { pendingFetches: 100, pollAfterMs: 1000 } }, settings: { stream: { deferred: true } } });
});

function delegatingExtension(onChild: (id: any, submission: any) => void = () => {}) {
  let extension: any;
  const delegate = defineTool({
    name: "delegate", description: "Run a foreground subagent", parameters: Type.Object({ task: Type.String() }), replay: "safe",
    execute: async (args, api, context) => {
      const acquireChild = () => api.commit(async (tx) => {
        const existing = (await tx.scanConversations({ ownerTaskId: api.taskId }, 1)).items[0];
        if (existing) return existing.id;
        const child = await tx.createConversation({ ownership: { kind: "task", taskId: api.taskId } });
        await configure(tx, child.id, { model: { provider: "faux", modelId: "faux-2" }, extensions: { remove: [extension] } });
        return child.id;
      }, context);
      const child = await acquireChild();
      assert.equal(await acquireChild(), child, "owner-index reuse must prevent duplicate child creation");
      await api.details({ conversationId: child }, context);
      const conversation = (await api.conversation(child, context))!;
      const request = { type: "input", content: args.task, requestId: `subagent:${api.taskId}` } as const;
      const submission = await conversation.submit(request, context);
      assert.equal((await conversation.submit(request, context)).id, submission.id);
      onChild(child, submission.id);
      const settled = await submission.wait(context);
      return { output: [{ type: "text", text: `Child settled ${settled.status}` }] };
    },
  });
  extension = defineExtension({ name: "delegation", tools: [delegate] });
  return extension;
}

test("C24 foreground subagent inherits choices, changes model, and deduplicates creation/input", options, async () => {
  let childId: any;
  const delegate = delegatingExtension((child) => { childId = child; });
  await withLab(async ({ root, faux, harness }) => {
    faux.setResponses([fauxAssistantMessage(fauxToolCall("delegate", { task: "child task marker" }), { stopReason: "toolUse" }), fauxAssistantMessage("child final"), fauxAssistantMessage("parent final")]);
    await root.configure({ instructions: "shared policy", cwd: "/parent-cwd" }, bounded());
    await done(await root.submit({ type: "input", content: "delegate task" }, bounded()));
    const child = (await harness.conversation(childId, bounded()))!;
    const agent = await child.agent(bounded());
    assert.equal(agent.instructions, "shared policy");
    assert.equal(agent.cwd, "/parent-cwd");
    assert.equal(agent.model!.modelId, "faux-2");
    assert.doesNotMatch(text(agent.extensions), /delegation/);
    assert.notEqual((await harness.snapshot(ProviderDoc, child.id, bounded()))!.sessionId, (await harness.snapshot(ProviderDoc, root.id, bounded()))!.sessionId);
    assert.match(text((await child.context(bounded())).messages), /child task marker/);
    assert.doesNotMatch(text((await child.context(bounded())).messages), /delegate task/);
    assert.equal(faux.state.callCount, 3);
    await root.waitForIdle(bounded());
  }, { extensions: [delegate] });
});

test("C25 foreground abort cascades through the tool to the child conversation", options, async () => {
  const hold = holdingExtension();
  let childId: any;
  let childSubmission: any;
  const delegate = delegatingExtension((child, submission) => { childId = child; childSubmission = submission; });
  await withLab(async ({ root, faux, harness }) => {
    try {
      faux.setResponses([fauxAssistantMessage(fauxToolCall("delegate", { task: "child waits" }), { stopReason: "toolUse" }), fauxAssistantMessage(fauxToolCall("hold", {}), { stopReason: "toolUse" })]);
      const parent = await root.submit({ type: "input", content: "start foreground" }, bounded());
      await awaitWithContext(hold.entered.promise, bounded());
      const child = (await harness.conversation(childId, bounded()))!;
      const queued = await child.submit({ type: "input", content: "child queued" }, bounded());
      await root.abort(bounded());
      assert.equal((await parent.wait(bounded())).status, "unanswered");
      assert.equal((await (await harness.submission(childSubmission, bounded()))!.wait(bounded())).status, "unanswered");
      assert.equal((await queued.wait(bounded())).status, "unanswered");
      await child.waitForIdle(bounded());
      assert.equal((await harness.inspect(bounded())).tasks.length, 0);
    } finally { hold.release.resolve(); }
  }, { extensions: [hold.extension, delegate] });
});

test("C26 background anchor owns a subagent that survives ordinary parent abort and idle", options, async () => {
  const hold = holdingExtension();
  let childId: any;
  let childSubmission: any;
  const anchor = defineTask({
    name: "lab.background-subagent", version: 1, initial: () => ({ phase: "run" as const }),
    phases: {
      run: async (_task, runtime, context) => {
        let child: any;
        await runtime.commit(async (tx) => {
          const existing = (await tx.scanConversations({ ownerTaskId: runtime.taskId }, 1)).items[0];
          if (existing) child = existing.id;
          else child = (await tx.createConversation({ ownership: { kind: "task", taskId: runtime.taskId } })).id;
        }, context);
        childId = child;
        const conversation = (await runtime.conversation(child, context))!;
        const submission = await conversation.submit({ type: "input", content: "background child work", requestId: `background:${runtime.taskId}` }, context);
        childSubmission = submission.id;
        const result = await submission.wait(context);
        await runtime.commit(() => ({ status: "terminal", outcome: { status: "completed", result: result.status } }), context);
      },
    },
    abort: async (_task, runtime, context) => { await runtime.commit(() => ({ status: "terminal", outcome: { status: "aborted" } }), context); },
  });
  await withLab(async ({ root, faux, harness }) => {
    try {
      faux.setResponses([fauxAssistantMessage(fauxToolCall("hold", {}), { stopReason: "toolUse" }), fauxAssistantMessage("parent can answer")]);
      const anchorId = await root.commit((tx) => tx.createTask(anchor, {}, { ownership: { kind: "conversation" }, background: true }), bounded());
      harness.resume();
      await awaitWithContext(hold.entered.promise, bounded());
      const parent = await root.submit({ type: "input", content: "ordinary parent request" }, bounded());
      await done(parent);
      await root.waitForIdle(bounded());
      await root.abort(bounded());
      assert.notEqual((await harness.getTask(anchorId, bounded()))!.state.status, "terminal");
      assert.equal((await (await harness.submission(childSubmission, bounded()))!.status(bounded())).status, "placed");
      const child = (await harness.conversation(childId, bounded()))!;
      await assert.rejects(child.waitForIdle(bounded(25)));
      await root.abort(bounded(), { background: true });
      const result = await harness.waitForTask(anchorId, bounded());
      assert.equal(result.state.outcome.status, "aborted");
      assert.equal((await (await harness.submission(childSubmission, bounded()))!.wait(bounded())).status, "unanswered");
      await child.waitForIdle(bounded());
    } finally { hold.release.resolve(); }
  }, { extensions: [hold.extension, defineExtension({ name: "background-subagent", tasks: [anchor] })] });
});

test("C27 throwing foreground owner aborts its live child before parent completes", options, async () => {
  const hold = holdingExtension();
  let childSubmission: any;
  const failingOwner = defineTool({
    name: "fail-owner", description: "Fail with an owned child", parameters: Type.Object({}), replay: "safe",
    execute: async (_args, api, context) => {
      const child = await api.commit(async (tx) => (await tx.createConversation({ ownership: { kind: "task", taskId: api.taskId } })).id, context);
      const conversation = (await api.conversation(child, context))!;
      childSubmission = (await conversation.submit({ type: "input", content: "owned child waits", requestId: `owned:${api.taskId}` }, context)).id;
      await awaitWithContext(hold.entered.promise, context);
      throw new Error("deliberate owner failure");
    },
  });
  await withLab(async ({ root, faux, harness }) => {
    try {
      faux.setResponses([fauxAssistantMessage(fauxToolCall("fail-owner", {}), { stopReason: "toolUse" }), fauxAssistantMessage(fauxToolCall("hold", {}), { stopReason: "toolUse" }), fauxAssistantMessage("parent handles owner failure")]);
      await done(await root.submit({ type: "input", content: "test failed ownership" }, bounded()));
      const settledChild = await (await harness.submission(childSubmission, bounded()))!.wait(bounded());
      assert.equal(settledChild.status, "unanswered");
      assert.match(text((await root.context(bounded())).messages), /deliberate owner failure/);
      assert.equal((await harness.inspect(bounded())).tasks.length, 0);
    } finally { hold.release.resolve(); }
  }, { extensions: [hold.extension, defineExtension({ name: "failing-owner", tools: [failingOwner] })] });
});

test("C28 background compaction leaves current generation and ordinary idle unblocked", options, async () => {
  const entered = gate();
  const release = gate();
  const summary = defineExtension({ name: "background-summary", hooks: [hook(CompactionTask, {
    beforeCompact: async (_request, _api, context) => {
      entered.resolve();
      await awaitWithContext(release.promise, context);
      return { summary: "background compact marker" };
    },
  })] });
  await withLab(async ({ root, faux, harness }) => {
    try {
      faux.setResponses([fauxAssistantMessage("old answer"), fauxAssistantMessage("generation finished before summary")]);
      await done(await root.submit({ type: "input", content: "old background context " + "a".repeat(800) }, bounded()));
      await done(await root.submit({ type: "input", content: "new input" }, bounded()));
      await awaitWithContext(entered.promise, bounded());
      await root.waitForIdle(bounded());
      const live = await harness.snapshot(LiveDoc, root.id, bounded());
      assert.equal(live!.compactions!.length, 1);
      assert.equal(live!.compactions![0].blocking, false);
      const taskId = live!.compactions![0].taskId;
      await root.abort(bounded());
      assert.notEqual((await harness.getTask(taskId, bounded()))!.state.status, "terminal");
      release.resolve();
      const compacted = await harness.waitForTask(taskId, bounded());
      assert.equal(compacted.state.outcome.status, "completed");
      await done((await harness.submission((compacted.state.outcome as any).result.submissionId, bounded()))!);
      assert.match(text((await root.context(bounded())).messages), /background compact marker/);
      assert.match(text((await root.context(bounded())).messages), /generation finished before summary/);
    } finally { release.resolve(); }
  }, { extensions: [summary], faux: { models: [{ id: "faux-1", contextWindow: 1000 }] }, settings: { compaction: { enabled: true, reserveTokens: 100, keepRecentTokens: 1, backgroundTokens: 800 } } });
});

test("C29 older concurrent compaction summary is stale after a farther cut wins", options, async () => {
  const firstEntered = gate();
  const firstRelease = gate();
  let summaryCount = 0;
  const summary = defineExtension({ name: "concurrent-summary", hooks: [hook(CompactionTask, {
    beforeCompact: async (_request, _api, context) => {
      summaryCount++;
      if (summaryCount === 1) {
        firstEntered.resolve();
        await awaitWithContext(firstRelease.promise, context);
        return { summary: "older summary must be stale" };
      }
      return { summary: "newer farther summary marker" };
    },
  })] });
  await withLab(async ({ root, faux, harness }) => {
    try {
      faux.setResponses([fauxAssistantMessage("answer one"), fauxAssistantMessage("answer two"), fauxAssistantMessage("answer three")]);
      for (const content of ["input one", "input two"]) await done(await root.submit({ type: "input", content }, bounded()));
      const oldId = await root.compact(undefined, bounded());
      await awaitWithContext(firstEntered.promise, bounded());
      await done(await root.submit({ type: "input", content: "input three" }, bounded()));
      const newer = await harness.waitForTask(await root.compact(undefined, bounded()), bounded());
      assert.equal(newer.state.outcome.status, "completed");
      await done((await harness.submission((newer.state.outcome as any).result.submissionId, bounded()))!);
      firstRelease.resolve();
      const older = await harness.waitForTask(oldId, bounded());
      assert.equal(older.state.outcome.status, "completed");
      const oldSubmission = (await harness.submission((older.state.outcome as any).result.submissionId, bounded()))!;
      const stale = await oldSubmission.wait(bounded());
      assert.equal(stale.status, "unanswered");
      assert.equal(stale.reason, "stale");
      const context = text((await root.context(bounded())).messages);
      assert.match(context, /newer farther summary marker/);
      assert.doesNotMatch(context, /older summary must be stale/);
    } finally { firstRelease.resolve(); }
  }, { extensions: [summary] });
});

test("C30 slow serialized watch coalesces backlog and event watch emits a fresh snapshot", options, async () => {
  await withLab(async ({ root, harness }) => {
    const watch = await root.watch(bg);
    const stream = await watchEvents(harness, root.id, bg);
    const enteredWatch = gate();
    const enteredEvents = gate();
    const release = gate();
    let watchCalls = 0;
    let activeCallbacks = 0;
    let maxCallbacks = 0;
    const snapshots: any[] = [];
    watch.start(async () => {
      activeCallbacks++;
      maxCallbacks = Math.max(maxCallbacks, activeCallbacks);
      watchCalls++;
      if (watchCalls === 1) {
        enteredWatch.resolve();
        await release.promise;
      }
      activeCallbacks--;
    });
    let eventCalls = 0;
    let finalEventReceived = false;
    stream.start(async (events) => {
      eventCalls++;
      snapshots.push(...events.filter((event) => event.type === "snapshot"));
      if (text(events).includes("backlog-120")) finalEventReceived = true;
      if (eventCalls === 1) {
        enteredEvents.resolve();
        await release.promise;
      }
    });
    try {
      await done(await root.submit({ type: "write", entry: { kind: "app.note", data: "first slow callback" } }, bounded()));
      await awaitWithContext(Promise.all([enteredWatch.promise, enteredEvents.promise]), bounded());
      for (let i = 0; i < 121; i++) await done(await root.submit({ type: "write", entry: { kind: "app.note", data: `backlog-${i}` } }, bounded()));
      release.resolve();
      // The replacement snapshot is created when the buffer crosses 100; later
      // commits are delivered as ordinary delta batches on top of that snapshot.
      await eventually(() => text(watch.value).includes("backlog-120") && snapshots.length > 0 && finalEventReceived, "coalesced observers never caught up");
      assert.equal(maxCallbacks, 1, "watch callbacks must remain serialized");
      assert.ok(watchCalls < 122, `expected frame coalescing, got ${watchCalls} callbacks`);
      assert.ok(eventCalls < 122, `expected event batch coalescing, got ${eventCalls} callbacks`);
      assert.equal(watch.value.entries.length, 122);
    } finally {
      release.resolve();
      await watch.stop();
      await stream.stop();
    }
  });
});
