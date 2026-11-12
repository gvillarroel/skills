# Guard stateful Pi dialogs against stale input

Use this recipe when a Pi command edits, reviews or commits shared state while
native dialogs are open. `await ctx.ui.input(...)`, row selection and commit
confirmation all allow time for another command to change that state. Guard
edits as well as commits; protecting only the final confirmation is insufficient.

## Contents

- [Choose the authority version](#choose-the-authority-version)
- [Collect intent and apply synchronously](#collect-intent-and-apply-synchronously)
- [Use the small helper](#use-the-small-helper)
- [Verify the interleaving](#verify-the-interleaving)

## Choose the authority version

Use a monotonic draft revision for a small shared draft, or a row version for
independent edits. Increment it on every relevant mutation, including explicit
argument commands. Capture it **before the first dialog await**, including a
row selector if it uses that draft. Comparing only a value captured after the
input resolves cannot detect an intervening edit.

For review/commit, keep the reviewed snapshot and its authority revision
separate from live draft data. Invalidate the review after a changed edit.
Confirm the reviewed intent, then recheck its authority immediately before
applying it. Do not reconstruct a confirmation's approved rows from a newer
live draft or report success before the write finishes.

## Collect intent and apply synchronously

1. Capture the current authority version before opening controls.
2. Collect row selection, text or confirmation into a local intent. Do not
   mutate domain state while collecting it. Native dismissal maps to
   `undefined`; preserve valid falsy values instead of treating them as cancel.
3. After all dialog awaits, compare the authority version again. On mismatch,
   leave newer state intact, explain that the draft changed, and offer a fresh
   Edit/Review action. Keep the returned text as a draft only if that does not
   overwrite the authoritative value.
4. In one synchronous continuation, validate domain rules, prepare the next
   state, apply it and advance its version. Put no await between the final
   version check and write. Validate before mutation so a rejected input does
   not partially change state. Publish success after this transition.

A row-level guard can allow independent rows to change concurrently. A whole
draft guard is simpler but may ask for a retry after a nonconflicting change.
Choose deliberately and describe the tradeoff. This recipe is a local state
guard, not a transaction system for a remote service.

## Use the small helper

Copy [guarded-intent.ts](../assets/templates/pi-stateful/guarded-intent.ts)
beside the generated extension and import it locally. It has no runtime
dependency and does not call Pi, start inference or persist data.
For a one-file output contract, inline the same small primitive in that file
instead of creating an undeclared supporting module.

```typescript
import { runGuardedIntent } from "./guarded-intent.ts";

const result = await runGuardedIntent({
  getRevision: () => draftVersion,
  collect: async () => {
    const selected = await ctx.ui.select("Choose record", labels);
    if (selected === undefined) return undefined;
    const text = await ctx.ui.input("New name", "Enter a name");
    return text === undefined ? undefined : { selected, text };
  },
  apply: intent => {
    const next = validateAndPrepareEdit(currentDraft, intent);
    currentDraft = next;
    draftVersion++;
    reviewedSnapshot = undefined;
    return undefined;
  },
});
if (result === "stale") {
  // Use the command's ordinary visible output path, including no-UI fallback.
  showResult("The draft changed. Reopen Edit; your newer values were kept.");
}
```

This is a focused integration sketch: implement the task's data, labels,
validator and output path. Keep `apply` synchronous and returning `undefined`;
never pass an async callback or schedule a later mutation from it. The helper
rejects a directly declared async callback before collection and detects a
returned value/promise, but cannot roll back arbitrary writes a misbehaving
callback has already performed. A thrown validator error should be reported
as recoverable input feedback without discarding the current draft.

For confirmation, collect `confirmed ? reviewedIntent : undefined`, then
validate the snapshot/revision and commit synchronously in `apply`. A cancel
does not clear a valid review unless the task's explicit Cancel action requires
that transition. All other [Pi mode and message rules](pi-extensions.md) apply.

## Verify the interleaving

Use controllable dialog promises, not only sequential happy-path invocations:

- Open Edit for one record, submit a newer value through another command,
  then resolve the old input. Require the newer same-record value to remain.
- Open confirmation, mutate/invalidate its reviewed draft, then accept the
  old confirmation. Require no stale commit and usable review/retry guidance.
- Dismiss each dialog; require no unintended mutation. Check unchanged-version
  success and valid `false`, `0` or empty-string intents where the domain allows.
- Confirm validation failures happen before writes and later retry uses a
  fresh version. Verify direct argument commands advance the same authority.

Helper tests establish this primitive's behavior. Also exercise the generated
handler and actual RPC dialog transport; neither source nor helper tests prove
native terminal paint, focus, accessibility or representative-user usability.
