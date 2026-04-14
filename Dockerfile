FROM python:3.13-alpine

COPY --from=ghcr.io/astral-sh/uv /uv /bin/

WORKDIR /app

COPY . .

RUN uv sync --no-cache

ENTRYPOINT ["uv", "run", "oai2ollama", "--host", "0.0.0.0"]
