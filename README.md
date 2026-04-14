# Oai2Ollama

This is a CLI tool that starts a lightweight proxy in front of an OpenAI-compatible API, with first-class
support for model aliasing and automatic Claude prompt caching injection. It still exposes Ollama-compatible
endpoints, but the primary value is request shaping for upstream model routing and Anthropic-friendly caching.

When `--auto-claude-prompt-caching` is enabled, OpenAI-format requests whose resolved upstream model
ID contains `claude` automatically add prompt caching directives where supported. Existing
caller-provided cache settings are preserved.

## Usage

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

> [!TIP]
> To mark the model as supporting certain capabilities, you can use the `--capabilities` (or `-c`) option with a list of strings. For example, the following two syntaxes are supported:
>
> `oai2ollama -c tools` or `oai2ollama --capabilities tools`
>
> `oai2ollama -c tools -c vision` or `oai2ollama --capabilities -c tools,vision`
>
> To support models that are not returned by the `/models` endpoint, use the `--models` (or `-m`) option to add them to the `/api/tags` response:
>
> `oai2ollama -m model1 -m model2` or `oai2ollama -m model1,model2`
>
> To expose friendly model names that forward to a different upstream model, use `--model-alias` (or `-a`):
>
> `oai2ollama -a sonnet=anthropic/claude-3-5-sonnet`
>
> `oai2ollama -a sonnet=anthropic/claude-3-5-sonnet -a opus=anthropic/claude-opus-4-1`
>
> To enable automatic prompt caching for Claude models after alias resolution:
>
> `oai2ollama --auto-claude-prompt-caching true`
>
> Capabilities currently [used by Ollama](https://github.com/ollama/ollama/blob/main/types/model/capability.go#L6-L11) are:
> `tools`, `insert`, `vision`, `embedding`, `thinking` and `completion`. We always include `completion`.
>
> Set `OPENAI_BASE_URL` / `--base-url` to the API root without `/v1`, for example `https://api.openai.com`.
>
> If `OPENAI_API_KEY` / `--api-key` is omitted, the proxy forwards incoming `Authorization`, `api-key`, or `x-api-key` headers to the upstream API instead.

## What It Does

- Exposes stable local model aliases and rewrites them to upstream model IDs.
- Optionally injects Claude prompt caching directives on supported OpenAI-format request shapes.
- Forwards authentication from config or from the incoming request.
- Still provides Ollama-compatible `/api/tags` and `/api/show` endpoints for clients that need them.

Or you can use a `.env` file to set these options:

```properties
OPENAI_BASE_URL=https://api.openai.com
HOST=0.0.0.0
CAPABILITIES=["vision","thinking"]
AUTO_CLAUDE_PROMPT_CACHING=true
MODELS=["custom-model1","custom-model2"]
MODEL_ALIAS=["sonnet=anthropic/claude-3-5-sonnet","opus=anthropic/claude-opus-4-1"]
```

> [!WARNING]
> The option name `capacities` is deprecated. Use `capabilities` instead. The old name still works for now but will emit a deprecation warning.

### with Docker

First, build the image:

```sh
docker build -t oai2ollama .
```

Then, run the container with your credentials:

```sh
docker run -p 11434:11434 \
  -e OPENAI_API_KEY="your_api_key" \
  -e OPENAI_BASE_URL="https://api.openai.com" \
  oai2ollama
```

Or omit `OPENAI_API_KEY` and let the proxy forward auth headers from each incoming request:

```sh
docker run -p 11434:11434 \
  -e OPENAI_BASE_URL="https://api.openai.com" \
  oai2ollama
```

Or you can pass these as command line arguments:

```sh
docker run -p 11434:11434 oai2ollama --api-key your_api_key --base-url https://api.openai.com
```

To have the server listen on a different host, like all IPv6 interfaces, use the `--host` argument:

```sh
docker run -p 11434:11434 oai2ollama --host "::"
```
