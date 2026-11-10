import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const [packagePath, promptPath] = process.argv.slice(2);
const { ModelRuntime, getAgentDir, VERSION } = await import(
  pathToFileURL(resolve(packagePath, "dist/index.js"))
);
const { AuthStorage } = await import(pathToFileURL(resolve(packagePath, "dist/core/auth-storage.js")));
const provider = "github-copilot";
const modelId = "gpt-6-luna";
const auth = JSON.parse(readFileSync(join(getAgentDir(), "auth.json"), "utf8"));
const runtime = await ModelRuntime.create({
  credentials: AuthStorage.inMemory(auth),
  modelsPath: null,
  allowModelNetwork: false,
  refreshOnCreate: false,
});
const model = runtime.getPhysicalModel(provider, modelId);
if (!model || model.provider !== provider || model.id !== modelId || !auth[provider]) {
  throw new Error("The configured GitHub Copilot Luna model is unavailable.");
}
const receipt = { version: VERSION, provider, model: modelId, thinking: "low" };
if (promptPath === "--check") {
  console.log(JSON.stringify(receipt));
} else {
  const prompt = readFileSync(promptPath, "utf8");
  const promptHash = createHash("sha256").update(prompt, "utf8").digest("hex");
  const started = Date.now();
  const reply = await runtime.completeSimple(model, {
    messages: [{ role: "user", content: prompt, timestamp: started }],
  }, {
    reasoning: "low",
    maxTokens: 12000,
    maxRetries: 0,
    cacheRetention: "none",
    timeoutMs: 150000,
    signal: AbortSignal.timeout(160000),
  });
  const output = reply.content.filter((part) => part.type === "text").map((part) => part.text).join("");
  console.log(JSON.stringify({
    ...receipt,
    prompt_sha256: promptHash,
    duration_ms: Date.now() - started,
    observed_model: reply.model,
    observed_provider: reply.provider,
    response_model: reply.responseModel ?? null,
    stop_reason: reply.stopReason,
    usage: reply.usage,
    output,
  }));
  if (reply.stopReason !== "stop" || reply.model !== modelId || reply.provider !== provider || !output) {
    process.exitCode = 2;
  }
}
