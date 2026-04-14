---
title: Introduction
icon: lucide/anchor
---

# :fontawesome-brands-openai:{ title="OpenAI-compatible API" } :lucide-chevrons-right:{ style="opacity: 0.3" title="👉" } :simple-ollama:{ title="Ollama-compatible API" }

[`oai2ollama`](https://pypi.org/project/oai2ollama/) is a lightweight FastAPI server that translates an OpenAI ChatCompletions API endpoint into an Ollama-compatible endpoint. It allows you to use custom LLM providers for coding agents that don't support custom OpenAI APIs but do support Ollama (like GitHub Copilot for VS Code).

## Quick Start

### with Python

You can run directly via `uvx` (if you have `uv` installed) or `pipx`:

```sh
uvx oai2ollama --help
```

```text
usage: oai2ollama [--api-key str] [--base-url HttpUrl] [--capabilities list[str]] [--models list[str]] [--model-alias list[str]] [--host str] [--auto-claude-prompt-caching bool]
options:
  --help, -h                    Show this help message and exit
  --api-key str                 Optional upstream API key for authentication
  --base-url HttpUrl            Base URL for the OpenAI-compatible API root, without /v1 (required)
  --capabilities, -c list[str]  Extra capabilities to mark the model as supporting
  --models, -m list[str]        Extra models to include in the /api/tags response
  --model-alias, -a list[str]   Model alias in alias=target form
  --host str                    IP / hostname for the API server (default: localhost)
  --auto-claude-prompt-caching bool
                                Enable automatic prompt caching for Claude models (default: False)
```

Or you can use a `.env` file:

```properties
OPENAI_BASE_URL=https://api.openai.com
HOST=0.0.0.0
CAPABILITIES=["vision","thinking"]
AUTO_CLAUDE_PROMPT_CACHING=true
MODELS=["custom-model1","custom-model2"]
MODEL_ALIAS=["sonnet=anthropic/claude-3-5-sonnet"]
```

!!! tip ""

    To mark the model as supporting certain capabilities, use the `--capabilities` (or `-c`) option:

    `oai2ollama -c tools` or `oai2ollama --capabilities tools`

    `oai2ollama -c tools -c vision` or `oai2ollama --capabilities -c tools,vision`

    To support models that are not returned by the `/models` endpoint:

    `oai2ollama -m model1 -m model2` or `oai2ollama -m model1,model2`

    To expose a shorter local model name that forwards to a different upstream model:

    `oai2ollama -a sonnet=anthropic/claude-3-5-sonnet`

    To enable automatic prompt caching for Claude models after alias resolution:

    `oai2ollama --auto-claude-prompt-caching true`

    Set `OPENAI_BASE_URL` to the API root without `/v1`, for example `https://api.openai.com`.

    If `OPENAI_API_KEY` is omitted, incoming `Authorization`, `api-key`, and `x-api-key` headers are forwarded upstream.

    Capabilities currently used by Ollama are: `tools`, `insert`, `vision`, `embedding`, `thinking` and `completion`. We always include `completion`.

### with Docker

```sh
docker build -t oai2ollama .
docker run -p 11434:11434 \
  -e OPENAI_API_KEY="your_api_key" \
  -e OPENAI_BASE_URL="https://api.openai.com" \
  oai2ollama
```

To listen on all interfaces:

```sh
docker run -p 11434:11434 oai2ollama --host "::"
```

## Features

- OpenAI-compatible `/v1/chat/completions` endpoint
- Ollama-compatible `/api/tags` and `/api/show` endpoints
- Streaming response support
- Configurable model list with extra models
- Model aliasing for request rewriting and discovery
- Customizable capabilities (tools, insert, vision, embedding, thinking)
