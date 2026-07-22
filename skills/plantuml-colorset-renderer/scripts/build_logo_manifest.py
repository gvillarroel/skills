#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the pinned multi-source technical logo manifest from local source clones."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path


SCHEMA_VERSION = 2


@dataclass(frozen=True)
class Source:
    provider: str
    repository: str
    commit: str
    license_id: str
    license_url: str
    attribution: str
    artwork_glob: str


SOURCES = {
    "aws": Source(
        provider="AWS",
        repository="https://github.com/awslabs/aws-icons-for-plantuml",
        commit="50efda948226ff4e06937596201528b707ef3ef9",
        license_id="CC-BY-ND-2.0",
        license_url="https://creativecommons.org/licenses/by-nd/2.0/",
        attribution="Amazon Web Services (AWS); packaged by AWS Icons for PlantUML contributors",
        artwork_glob="dist/**/*.png",
    ),
    "gcp": Source(
        provider="GCP",
        repository="https://github.com/davidholsgrove/gcp-icons-for-plantuml",
        commit="f103741ffdca5793142103d7f5206814be92a405",
        license_id="CC-BY-ND-2.0",
        license_url="https://creativecommons.org/licenses/by-nd/2.0/",
        attribution="Google Cloud; packaged by GCP Icons for PlantUML contributors",
        artwork_glob="dist/**/*.png",
    ),
    "devicon": Source(
        provider="Devicon",
        repository="https://github.com/devicons/devicon",
        commit="7330accdbc47e2dc0c19789a48533c4a3c50fe58",
        license_id="MIT",
        license_url="https://spdx.org/licenses/MIT.html",
        attribution="Devicon contributors; product names and marks remain property of their owners",
        artwork_glob="icons/*/*.svg",
    ),
    "simpleicons": Source(
        provider="Simple Icons",
        repository="https://github.com/simple-icons/simple-icons",
        commit="0f9fa549da00e9aa6e3ef8d3d2171f481360e638",
        license_id="per-icon",
        license_url="https://github.com/simple-icons/simple-icons/blob/develop/DISCLAIMER.md",
        attribution="Simple Icons contributors; consult each icon's declared license and its mark owner",
        artwork_glob="icons/*.svg",
    ),
    "fontawesome": Source(
        provider="Font Awesome Brands",
        repository="https://github.com/FortAwesome/Font-Awesome",
        commit="70fb2dd154b617f62fc4ae5b0b7e2943bfd2aa96",
        license_id="CC-BY-4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        attribution="Font Awesome Free by Fonticons, Inc.; attribution required under CC-BY-4.0",
        artwork_glob="svgs/brands/*.svg",
    ),
    "ollama": Source(
        provider="Ollama",
        repository="https://github.com/ollama/ollama",
        commit="82f905cd9c06c6f0254d74c5326aa2a7f2f07e1f",
        license_id="MIT",
        license_url="https://spdx.org/licenses/MIT.html",
        attribution="Ollama contributors",
        artwork_glob="docs/ollama-logo.svg",
    ),
    "pi": Source(
        provider="Pi Coding Agent",
        repository="https://pi.dev/press-kit",
        commit="downloaded-2026-07-12",
        license_id="MIT",
        license_url="https://spdx.org/licenses/MIT.html",
        attribution="Earendil Inc. and Pi contributors",
        artwork_glob="favicon.svg",
    ),
    "opencode": Source(
        provider="OpenCode",
        repository="https://github.com/anomalyco/opencode",
        commit="cf7503687a2485621a690d18c4b0d1ff2060bc3e",
        license_id="MIT",
        license_url="https://spdx.org/licenses/MIT.html",
        attribution="OpenCode contributors",
        artwork_glob="packages/app/public/favicon-v3.svg",
    ),
    "cline": Source(
        provider="Cline",
        repository="https://github.com/cline/cline",
        commit="63099710895e24593554b1e77ec7852f6f16c05c",
        license_id="Apache-2.0",
        license_url="https://spdx.org/licenses/Apache-2.0.html",
        attribution="Cline Bot Inc. and contributors",
        artwork_glob="apps/vscode/assets/icons/icon.svg",
    ),
    "roo-code": Source(
        provider="Roo Code",
        repository="https://github.com/RooCodeInc/Roo-Code",
        commit="b867ec9145750d0ae1ff7f02d35406e9bf2a0b16",
        license_id="Apache-2.0",
        license_url="https://spdx.org/licenses/Apache-2.0.html",
        attribution="Roo Code, Inc. and contributors",
        artwork_glob="src/assets/images/roo-logo.svg",
    ),
    "continue": Source(
        provider="Continue",
        repository="https://github.com/continuedev/continue",
        commit="d0a3c0b626b5bebc3bef4742eec05a0242be0bab",
        license_id="Apache-2.0",
        license_url="https://spdx.org/licenses/Apache-2.0.html",
        attribution="Continue contributors",
        artwork_glob="docs/logo/light.svg",
    ),
    "aider": Source(
        provider="Aider",
        repository="https://github.com/Aider-AI/aider",
        commit="5dc9490bb35f9729ef2c95d00a19ccd30c26339c",
        license_id="Apache-2.0",
        license_url="https://spdx.org/licenses/Apache-2.0.html",
        attribution="Aider contributors",
        artwork_glob="aider/website/assets/logo.svg",
    ),
    "goose": Source(
        provider="Goose",
        repository="https://github.com/aaif-goose/goose",
        commit="858e8de359b6bd585813d25397744feffb50e8db",
        license_id="Apache-2.0",
        license_url="https://spdx.org/licenses/Apache-2.0.html",
        attribution="Agentic AI Foundation and Goose contributors",
        artwork_glob="documentation/static/img/logo.svg",
    ),
    "openhands": Source(
        provider="OpenHands",
        repository="https://github.com/OpenHands/OpenHands",
        commit="3949e1cc17d9443f1f4ef7d34d428baf065cd919",
        license_id="MIT",
        license_url="https://spdx.org/licenses/MIT.html",
        attribution="OpenHands contributors",
        artwork_glob="frontend/src/assets/branding/openhands-logo.svg",
    ),
    "swe-agent": Source(
        provider="SWE-agent",
        repository="https://github.com/SWE-agent/SWE-agent",
        commit="1132b3e80a45487ce8423f75d0e180874bf84caa",
        license_id="MIT",
        license_url="https://spdx.org/licenses/MIT.html",
        attribution="SWE-agent contributors",
        artwork_glob="docs/assets/mini_logo.svg",
    ),
    "qwen-code": Source(
        provider="Qwen Code",
        repository="https://github.com/QwenLM/qwen-code",
        commit="417d30584df6b2622df628194ecfc60e1bc0c920",
        license_id="Apache-2.0",
        license_url="https://spdx.org/licenses/Apache-2.0.html",
        attribution="QwenLM and Qwen Code contributors",
        artwork_glob="packages/desktop/apps/electron/resources/brands/qwen-code/icon.svg",
    ),
    "oh-my-pi": Source(
        provider="Oh My Pi",
        repository="https://github.com/can1357/oh-my-pi",
        commit="01d3fc9b6be922d2209c3211b2063e60565d7398",
        license_id="MIT",
        license_url="https://spdx.org/licenses/MIT.html",
        attribution="Oh My Pi contributors",
        artwork_glob="assets/icon.svg",
    ),
    "gemini-cli": Source(
        provider="Gemini CLI",
        repository="https://github.com/google-gemini/gemini-cli",
        commit="f354eebaf43b25bacb176007e449bb9a638fd101",
        license_id="Apache-2.0",
        license_url="https://spdx.org/licenses/Apache-2.0.html",
        attribution="Google and Gemini CLI contributors",
        artwork_glob="packages/vscode-ide-companion/assets/icon.png",
    ),
    "lobe-icons": Source(
        provider="Lobe Icons",
        repository="https://github.com/lobehub/lobe-icons",
        commit="32f4083f7a20b67ecdc7b29c0af031ada5a29c52",
        license_id="MIT",
        license_url="https://spdx.org/licenses/MIT.html",
        attribution="LobeHub Lobe Icons contributors; brand marks remain property of their owners",
        artwork_glob="packages/static-svg/icons/*.svg",
    ),
}

CODE_ASSISTANT_ASSETS = {
    "pi": ("pi.svg", "Pi Coding Agent", "svg", "https://pi.dev/favicon.svg"),
    "opencode": ("opencode.svg", "OpenCode", "svg", None),
    "cline": ("cline.svg", "Cline", "svg", None),
    "roo-code": ("roo-code.svg", "Roo Code", "svg", None),
    "continue": ("continue.svg", "Continue", "svg", None),
    "aider": ("aider.svg", "Aider", "svg", None),
    "goose": ("goose.svg", "Goose", "svg", None),
    "openhands": ("openhands.svg", "OpenHands", "svg", None),
    "swe-agent": ("swe-agent.svg", "SWE-agent", "svg", None),
    "qwen-code": ("qwen-code.svg", "Qwen Code", "svg", None),
    "oh-my-pi": ("oh-my-pi.svg", "Oh My Pi", "svg", None),
    "gemini-cli": ("gemini-cli.svg", "Gemini CLI", "png", None),
}

LOBE_CODE_ASSISTANT_ASSETS = {
    "amp": "Amp",
    "antigravity": "Google Antigravity",
    "anthropic": "Anthropic",
    "claude": "Claude",
    "claudecode": "Claude Code",
    "codex": "Codex",
    "cursor": "Cursor",
    "codegeex": "CodeGeeX",
    "copilotkit": "CopilotKit",
    "devin": "Devin",
    "greptile": "Greptile",
    "junie": "JetBrains Junie",
    "kiro": "Kiro",
    "kilocode": "Kilo Code",
    "lovable": "Lovable",
    "qoder": "Qoder",
    "replit": "Replit",
    "trae": "Trae",
    "v0": "v0",
    "windsurf": "Windsurf",
    "zencoder": "Zencoder",
}

LOBE_AI_PROVIDER_ASSETS = {
    "azureai": "Azure AI",
    "cerebras": "Cerebras",
    "deepseek": "DeepSeek",
    "fireworks": "Fireworks AI",
    "google": "Google AI",
    "groq": "Groq",
    "kimi": "Kimi",
    "lmstudio": "LM Studio",
    "minimax": "MiniMax",
    "mistral": "Mistral AI",
    "openai": "OpenAI",
    "openrouter": "OpenRouter",
    "perplexity": "Perplexity",
    "together": "Together AI",
    "vertexai": "Vertex AI",
    "xai": "xAI",
}

LOBE_AGENT_TOOL_ASSETS = {
    "agentvoice": "Agent Voice",
    "agui": "AG-UI",
    "aistudio": "Google AI Studio",
    "askverdict": "Verdict",
    "baseten": "Baseten",
    "cherrystudio": "Cherry Studio",
    "codebuddy": "CodeBuddy",
    "codeflicker": "CodeFlicker",
    "cometapi": "CometAPI",
    "comfyui": "ComfyUI",
    "coze": "Coze",
    "crewai": "CrewAI",
    "dify": "Dify",
    "docsearch": "DocSearch",
    "exa": "Exa",
    "fastgpt": "FastGPT",
    "giteeai": "Gitee AI",
    "glama": "Glama",
    "gradio": "Gradio",
    "hermesagent": "Hermes Agent",
    "higress": "Higress",
    "inference": "Inference",
    "langchain": "LangChain",
    "langfuse": "Langfuse",
    "langgraph": "LangGraph",
    "langsmith": "LangSmith",
    "livekit": "LiveKit",
    "llamaindex": "LlamaIndex",
    "llmapi": "LLM API",
    "manus": "Manus",
    "mastra": "Mastra",
    "mcp": "Model Context Protocol",
    "mcpso": "MCP.so",
    "metagpt": "MetaGPT",
    "modelscope": "ModelScope",
    "morph": "Morph",
    "n8n": "n8n",
    "openchat": "OpenChat",
    "openclaw": "OpenClaw",
    "openwebui": "Open WebUI",
    "phidata": "Phidata",
    "phind": "Phind",
    "pydanticai": "Pydantic AI",
    "relace": "Relace",
    "replicate": "Replicate",
    "searchapi": "SearchAPI",
    "smithery": "Smithery",
    "tavily": "Tavily",
    "unstructured": "Unstructured",
    "vllm": "vLLM",
    "voyage": "Voyage AI",
    "workersai": "Workers AI",
    "xinference": "Xinference",
    "zapier": "Zapier",
}

SIMPLE_ICON_ALLOWED_LICENSES = {
    "Apache-2.0": "https://spdx.org/licenses/Apache-2.0.html",
    "BSD-3-Clause": "https://spdx.org/licenses/BSD-3-Clause.html",
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "MIT": "https://spdx.org/licenses/MIT.html",
}

# Deliberately curated rather than importing the whole Brand set.  This prevents
# visual aliases (for example, ``square-*`` and historical variants) from
# duplicating the Devicon/Simple Icons catalog, and keeps only tools that the
# current catalog did not already represent.  ``openai`` and ``claude`` are not
# included: their owners' current brand policies are not permissive artwork
# licenses for a redistributable logo bundle.
FONTAWESOME_SELECTED = {
    "hugging-face",
    "obsidian",
    "octopus-deploy",
    "openstreetmap",
    "phoenix-framework",
    "signal-messenger",
    "solana",
    "ultralytics",
    "ultralytics-hub",
    "ultralytics-yolo",
    "web-awesome",
    "zoom",
    "zulip",
}


def slugify(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return value or "logo"


def semantic_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def raw_url(source: Source, relative_path: str) -> str:
    repo_path = source.repository.removeprefix("https://github.com/")
    return f"https://raw.githubusercontent.com/{repo_path}/{source.commit}/{relative_path}"


def cloud_entries(key: str, root: Path) -> list[dict[str, str]]:
    source = SOURCES[key]
    candidates = sorted(root.glob(source.artwork_glob))
    seen_hashes: set[str] = set()
    entries: list[dict[str, str]] = []
    for path in candidates:
        digest = sha256(path)
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        relative = path.relative_to(root).as_posix()
        category = path.parent.name
        name = path.stem
        logo_id = f"{key}-{slugify(category)}-{slugify(name)}"
        entries.append(
            {
                "id": logo_id,
                "assetPath": f"{key}/{slugify(category)}/{slugify(name)}.svg",
                "title": f"{source.provider} {name}",
                "provider": source.provider,
                "category": category,
                "sourceFormat": "png",
                "sourcePath": relative,
                "sourceUrl": raw_url(source, relative),
                "sourceSha256": digest,
                "licenseId": source.license_id,
                "licenseUrl": source.license_url,
                "sourceRepository": source.repository,
                "sourceCommit": source.commit,
                "attribution": source.attribution,
            }
        )
    return entries


def choose_devicon(directory: Path) -> Path | None:
    slug = directory.name
    preferences = [
        f"{slug}-original.svg",
        f"{slug}-plain.svg",
        f"{slug}-line.svg",
        f"{slug}-original-wordmark.svg",
        f"{slug}-plain-wordmark.svg",
        f"{slug}-line-wordmark.svg",
    ]
    for name in preferences:
        path = directory / name
        if path.is_file():
            return path
    return next(iter(sorted(directory.glob("*.svg"))), None)


def devicon_entries(root: Path) -> list[dict[str, str]]:
    source = SOURCES["devicon"]
    entries: list[dict[str, str]] = []
    seen_hashes: set[str] = set()
    for directory in sorted((root / "icons").iterdir()):
        if not directory.is_dir():
            continue
        path = choose_devicon(directory)
        if path is None:
            continue
        digest = sha256(path)
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        relative = path.relative_to(root).as_posix()
        entries.append(
            {
                "id": f"devicon-{slugify(directory.name)}",
                "assetPath": f"devicon/technology/{slugify(directory.name)}.svg",
                "title": directory.name,
                "provider": source.provider,
                "category": "technology",
                "sourceFormat": "svg",
                "sourcePath": relative,
                "sourceUrl": raw_url(source, relative),
                "sourceSha256": digest,
                "licenseId": source.license_id,
                "licenseUrl": source.license_url,
                "sourceRepository": source.repository,
                "sourceCommit": source.commit,
                "attribution": source.attribution,
            }
        )
    return entries


def simple_icon_slug_map(root: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for line in (root / "slugs.md").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"\| `(.+)` \| `([a-z0-9]+)` \|", line)
        if match:
            mapping[match.group(1)] = match.group(2)
    return mapping


def simple_icon_entries(root: Path) -> list[dict[str, str]]:
    source = SOURCES["simpleicons"]
    data = json.loads((root / "data" / "simple-icons.json").read_text(encoding="utf-8"))
    slugs = simple_icon_slug_map(root)
    entries: list[dict[str, str]] = []
    for item in data:
        license_data = item.get("license") or {}
        license_id = license_data.get("type")
        if license_id not in SIMPLE_ICON_ALLOWED_LICENSES:
            continue
        title = item["title"]
        slug = slugs.get(title)
        if not slug:
            raise ValueError(f"No Simple Icons slug for {title!r}")
        path = root / "icons" / f"{slug}.svg"
        if not path.is_file():
            raise ValueError(f"Missing Simple Icons SVG {path}")
        relative = path.relative_to(root).as_posix()
        entries.append(
            {
                "id": f"simpleicons-{slug}",
                "assetPath": f"simple-icons/technology-brand/{slug}.svg",
                "title": title,
                "provider": source.provider,
                "category": "technology-brand",
                "sourceFormat": "svg",
                "sourcePath": relative,
                "sourceUrl": raw_url(source, relative),
                "sourceSha256": sha256(path),
                "licenseId": license_id,
                "licenseUrl": SIMPLE_ICON_ALLOWED_LICENSES[license_id],
                "sourceRepository": source.repository,
                "sourceCommit": source.commit,
                "attribution": source.attribution,
                "originalSource": item.get("source", ""),
                "guidelines": item.get("guidelines", ""),
            }
        )
    return entries


def fontawesome_entries(root: Path) -> list[dict[str, str]]:
    source = SOURCES["fontawesome"]
    entries: list[dict[str, str]] = []
    for slug in sorted(FONTAWESOME_SELECTED):
        path = root / "svgs" / "brands" / f"{slug}.svg"
        if not path.is_file():
            raise ValueError(f"Missing Font Awesome Brands SVG {path}")
        relative = path.relative_to(root).as_posix()
        entries.append(
            {
                "id": f"fontawesome-{slug}",
                "assetPath": f"font-awesome/brands/{slug}.svg",
                "title": slug.replace("-", " ").title(),
                "provider": source.provider,
                "category": "brands",
                "sourceFormat": "svg",
                "sourcePath": relative,
                "sourceUrl": raw_url(source, relative),
                "sourceSha256": sha256(path),
                "licenseId": source.license_id,
                "licenseUrl": source.license_url,
                "sourceRepository": source.repository,
                "sourceCommit": source.commit,
                "attribution": source.attribution,
            }
        )
    return entries


def ollama_entries(root: Path) -> list[dict[str, str]]:
    source = SOURCES["ollama"]
    path = root / "docs" / "ollama-logo.svg"
    if not path.is_file():
        raise ValueError(f"Missing Ollama SVG {path}")
    relative = path.relative_to(root).as_posix()
    return [
        {
            "id": "ollama-ollama",
            "assetPath": "ollama/technology/ollama.svg",
            "title": "Ollama",
            "provider": source.provider,
            "category": "technology",
            "sourceFormat": "svg",
            "sourcePath": relative,
            "sourceUrl": raw_url(source, relative),
            "sourceSha256": sha256(path),
            "licenseId": source.license_id,
            "licenseUrl": source.license_url,
            "sourceRepository": source.repository,
            "sourceCommit": source.commit,
            "attribution": source.attribution,
        }
    ]


def code_assistant_entries(roots: dict[str, Path]) -> list[dict[str, str]]:
    missing = sorted(set(CODE_ASSISTANT_ASSETS) - set(roots))
    if missing:
        raise ValueError(f"Missing --assistant-source values for: {', '.join(missing)}")
    entries: list[dict[str, str]] = []
    for key, (filename, title, source_format, source_url) in CODE_ASSISTANT_ASSETS.items():
        source = SOURCES[key]
        matches = list(roots[key].glob(source.artwork_glob))
        if len(matches) != 1:
            raise ValueError(f"Expected one {key} artwork, found {len(matches)}")
        path = matches[0]
        relative = path.relative_to(roots[key]).as_posix()
        entries.append(
            {
                "id": f"code-assistant-{key}",
                "assetPath": f"code-assistants/harnesses/{filename}",
                "title": title,
                "provider": source.provider,
                "category": "code-assistant-harness",
                "sourceFormat": source_format,
                "sourcePath": relative,
                "sourceUrl": source_url or raw_url(source, relative),
                "sourceSha256": sha256(path),
                "licenseId": source.license_id,
                "licenseUrl": source.license_url,
                "sourceRepository": source.repository,
                "sourceCommit": source.commit,
                "attribution": source.attribution,
            }
        )
    return entries


def lobe_code_assistant_entries(root: Path) -> list[dict[str, str]]:
    source = SOURCES["lobe-icons"]
    entries: list[dict[str, str]] = []
    collections = (
        (LOBE_CODE_ASSISTANT_ASSETS, "code-assistants/products", "code-assistant-product", "code-assistant"),
        (LOBE_AI_PROVIDER_ASSETS, "code-assistants/providers", "ai-provider", "ai-provider"),
        (LOBE_AGENT_TOOL_ASSETS, "code-assistants/tools", "agent-tool", "agent-tool"),
    )
    for assets, asset_directory, category, id_prefix in collections:
        for slug, title in assets.items():
            path = root / "packages" / "static-svg" / "icons" / f"{slug}.svg"
            if not path.is_file():
                raise ValueError(f"Missing Lobe Icons SVG {path}")
            relative = path.relative_to(root).as_posix()
            filename = "claude-code.svg" if slug == "claudecode" else f"{slug}.svg"
            entries.append(
                {
                    "id": f"{id_prefix}-{slug}",
                    "assetPath": f"{asset_directory}/{filename}",
                    "title": title,
                    "provider": source.provider,
                    "category": category,
                    "sourceFormat": "svg",
                    "sourcePath": relative,
                    "sourceUrl": raw_url(source, relative),
                    "sourceSha256": sha256(path),
                    "licenseId": source.license_id,
                    "licenseUrl": source.license_url,
                    "sourceRepository": source.repository,
                    "sourceCommit": source.commit,
                    "attribution": source.attribution,
                }
            )
    return entries


def lobe_ecosystem_entries(
    root: Path, existing_entries: list[dict[str, str]]
) -> tuple[list[dict[str, str]], dict[str, int]]:
    """Import every remaining canonical Lobe icon exactly once."""
    source = SOURCES["lobe-icons"]
    icon_directory = root / "packages" / "static-svg" / "icons"
    variant_suffix = re.compile(
        r"-(?:avatar|brand|brand-color|color|combine|mono|text|text-cn)$"
    )
    candidates = sorted(
        path for path in icon_directory.glob("*.svg") if not variant_suffix.search(path.stem)
    )
    seen_semantics = {
        semantic_key(value)
        for item in existing_entries
        for value in (item["title"], Path(item["assetPath"]).stem)
    }
    # Explicitly connect common abbreviations to their already-bundled brand.
    semantic_aliases = {"aws": "amazonwebservices", "huggingface": "huggingface"}
    seen_hashes = {item["sourceSha256"] for item in existing_entries}
    entries: list[dict[str, str]] = []
    semantic_skips = 0
    hash_skips = 0
    for path in candidates:
        slug = path.stem
        key = semantic_aliases.get(semantic_key(slug), semantic_key(slug))
        if key in seen_semantics:
            semantic_skips += 1
            continue
        digest = sha256(path)
        if digest in seen_hashes:
            hash_skips += 1
            continue
        relative = path.relative_to(root).as_posix()
        title = re.sub(r"[-_]", " ", slug).title()
        entries.append(
            {
                "id": f"ai-ecosystem-{slug}",
                "assetPath": f"code-assistants/ecosystem/{slug}.svg",
                "title": title,
                "provider": source.provider,
                "category": "ai-ecosystem",
                "sourceFormat": "svg",
                "sourcePath": relative,
                "sourceUrl": raw_url(source, relative),
                "sourceSha256": digest,
                "licenseId": source.license_id,
                "licenseUrl": source.license_url,
                "sourceRepository": source.repository,
                "sourceCommit": source.commit,
                "attribution": source.attribution,
            }
        )
        seen_semantics.add(key)
        seen_hashes.add(digest)
    stats = {
        "canonicalCandidates": len(candidates),
        "importedAsEcosystem": len(entries),
        "skippedSemanticDuplicates": semantic_skips,
        "skippedHashDuplicates": hash_skips,
    }
    return entries, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aws-source", type=Path, required=True)
    parser.add_argument("--gcp-source", type=Path, required=True)
    parser.add_argument("--devicon-source", type=Path, required=True)
    parser.add_argument("--simpleicons-source", type=Path, required=True)
    parser.add_argument("--fontawesome-source", type=Path, required=True)
    parser.add_argument("--ollama-source", type=Path, required=True)
    parser.add_argument(
        "--assistant-source",
        action="append",
        default=[],
        metavar="KEY=DIR",
        help="Pinned code-assistant source directory; repeat once per curated source",
    )
    parser.add_argument("--lobe-icons-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    assistant_roots = {}
    for value in args.assistant_source:
        key, separator, directory = value.partition("=")
        if not separator or key not in CODE_ASSISTANT_ASSETS:
            raise ValueError(f"Invalid --assistant-source {value!r}")
        assistant_roots[key] = Path(directory)

    entries = (
        cloud_entries("aws", args.aws_source)
        + cloud_entries("gcp", args.gcp_source)
        + devicon_entries(args.devicon_source)
        + simple_icon_entries(args.simpleicons_source)
        + fontawesome_entries(args.fontawesome_source)
        + ollama_entries(args.ollama_source)
        + code_assistant_entries(assistant_roots)
        + lobe_code_assistant_entries(args.lobe_icons_source)
    )
    ecosystem_entries, ecosystem_stats = lobe_ecosystem_entries(
        args.lobe_icons_source, entries
    )
    entries += ecosystem_entries
    entries.sort(key=lambda item: item["id"])
    ids = [item["id"] for item in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("Generated logo IDs are not unique")
    asset_paths = [item["assetPath"] for item in entries]
    if len(asset_paths) != len(set(asset_paths)):
        raise ValueError("Generated logo asset paths are not unique")
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "normalization": {
            "width": 256,
            "height": 256,
            "viewBox": "0 0 256 256",
            "preserveAspectRatio": "xMidYMid meet",
            "padding": 16,
        },
        "sources": {
            key: {
                "provider": value.provider,
                "repository": value.repository,
                "commit": value.commit,
                "licenseId": value.license_id,
                "licenseUrl": value.license_url,
                "attribution": value.attribution,
            }
            for key, value in SOURCES.items()
        },
        "lobeCanonicalCoverage": ecosystem_stats,
        "logoCount": len(entries),
        "logos": entries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    counts = {provider: sum(e["provider"] == provider for e in entries) for provider in sorted({e["provider"] for e in entries})}
    print(f"Wrote {len(entries)} unique logos to {args.output}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
