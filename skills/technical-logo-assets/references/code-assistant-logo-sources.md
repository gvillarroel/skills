# Code-assistant logo source policy

Use this reference when maintaining or expanding `assets/logos/code-assistants/`.

## Included harnesses and products

Prefer the official project repository when it contains true vector artwork covered by its repository license. The official-source set includes Pi Coding Agent, OpenCode, Cline, Roo Code, Continue, Aider, Goose, OpenHands, SWE-agent, Qwen Code, and Oh My Pi. Resolve OpenCode's Git symlink to the actual `packages/ui/src/assets/favicon/favicon-v3.svg` bytes. Gemini CLI uses the pinned Lobe Icons `geminicli-color.svg` vector, not the former official PNG or a generic Gemini product mark.

Use the MIT-licensed Lobe Icons static SVG collection for Amp, Antigravity, Anthropic, Claude, Claude Code, CodeGeeX, Codex, CopilotKit, Cursor, Devin, Greptile, Junie, Kilo Code, Kiro, Lovable, Qoder, Replit, Trae, v0, Windsurf, and Zencoder. Use the same collection for the associated Azure AI, Cerebras, DeepSeek, Fireworks AI, Google AI, Groq, Kimi, LM Studio, MiniMax, Mistral AI, OpenAI, OpenRouter, Perplexity, Together AI, Vertex AI, and xAI provider marks. Preserve its artwork bytes and attribution. Treat the MIT grant as an artwork copyright license; brand names and trademarks remain controlled by their owners.

Also include the curated agent-tool layer from Lobe Icons. It covers agent frameworks and protocols such as AG-UI, CrewAI, LangChain, LangGraph, LlamaIndex, Mastra, MCP, MetaGPT, Phidata, and Pydantic AI; development and coding tools such as Cherry Studio, CodeBuddy, CodeFlicker, OpenClaw, Phind, and Morph; and supporting gateways, observability, search, RAG, runtime, and automation tools such as Baseten, CometAPI, Dify, Exa, Langfuse, LangSmith, n8n, Open WebUI, Replicate, Smithery, Tavily, Unstructured, vLLM, Voyage AI, Workers AI, Xinference, and Zapier. Keep this list explicit in `LOBE_AGENT_TOOL_ASSETS` so primary tools retain their more precise category before the exhaustive ecosystem pass.

After the curated layers, import every remaining canonical SVG from the pinned Lobe Icons collection into `code-assistants/ecosystem/`. Exclude `-avatar`, `-brand`, `-brand-color`, `-color`, `-combine`, `-mono`, `-text`, and `-text-cn` files as separate identities. Deduplicate by normalized title/filename and source SHA-256 against every earlier manifest entry. Record the accounting in `lobeCanonicalCoverage`; its candidate count must equal imported ecosystem entries plus semantic and hash duplicate skips. Import corresponding color or monochrome artwork only as a variant of its exact identity through `logo_variant_sources.json`, never as an extra brand. See [logo-variants.md](logo-variants.md).

## Exclusions and follow-up

Do not add an icon solely because a product is publicly visible or its source code is available. Require genuine SVG geometry with an explicit license permitting redistribution. Inspect nested SVGs and embedded resources; a PNG in an SVG wrapper, a mislabeled MIME type, or a Git symlink text file is not a vector source. Embedded outline fonts are permitted only when self-contained and verified not to contain bitmap glyph tables.

The current research pass did not find a qualifying pinned artwork source for Amazon Q Developer, Augment Code, Sourcegraph Cody, Codeium, Factory Droid, Tabnine, Tabby, Warp, Zed, or Crush. Simple Icons has Warp, Zed, and CodeRabbit artwork but does not declare an individual permissive license for those entries, so they remain excluded. Recheck official repositories and press kits during future catalog refreshes. Add them only when the artwork license is explicit; record the repository, immutable commit or source date, source path, SHA-256, license identifier, and attribution in the manifest.
