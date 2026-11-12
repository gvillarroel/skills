// Copy into the generated extension project and import it by its local path.
// Dependency-free TypeScript; Node 24 can load it directly. No Pi API calls.

export type Revision = string | number | bigint;
export type GuardedIntentResult = "applied" | "cancelled" | "stale";

export interface GuardedIntentOptions<Intent> {
  getRevision: () => Revision;
  collect: () => Promise<Intent | undefined>;
  // Validate domain rules before writing. Return undefined; never await here.
  apply: (intent: Intent) => undefined;
}

/** Collect intent asynchronously; apply only to the version it was opened on. */
export async function runGuardedIntent<Intent>(
  options: GuardedIntentOptions<Intent>,
): Promise<GuardedIntentResult> {
  // This catches the usual accidental async callback before it can run.
  // Normal functions returning a promise also violate the apply contract.
  if (options.apply.constructor.name === "AsyncFunction") {
    throw new TypeError("Guarded apply must be synchronous; collect asynchronous work before applying.");
  }
  const expectedRevision = options.getRevision();
  const intent = await options.collect();
  if (intent === undefined) return "cancelled";
  if (!Object.is(options.getRevision(), expectedRevision)) return "stale";

  // No await belongs between this revision check and domain validation/write.
  // The caller owns validation order and must not schedule a later mutation.
  const result = options.apply(intent);
  if (result !== undefined) {
    throw new TypeError("Guarded apply must return undefined and must not return a promise.");
  }
  return "applied";
}
