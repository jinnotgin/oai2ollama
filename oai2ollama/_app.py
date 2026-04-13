from fastapi import Depends, FastAPI, Request
from fastapi.responses import StreamingResponse

from .config import env

app = FastAPI()


def _add_ephemeral_cache_control_to_block(block: object):
    if isinstance(block, dict) and "type" in block:
        block.setdefault("cache_control", {"type": "ephemeral"})


def _add_ephemeral_cache_control_to_content(content: object):
    if isinstance(content, list):
        for block in content:
            _add_ephemeral_cache_control_to_block(block)


def _prepare_chat_completions_payload(data: dict):
    system = data.get("system")
    _add_ephemeral_cache_control_to_content(system)

    messages = data.get("messages")
    if isinstance(messages, list):
        for message in messages:
            if isinstance(message, dict):
                _add_ephemeral_cache_control_to_content(message.get("content"))

    tools = data.get("tools")
    if isinstance(tools, list):
        for tool in tools:
            _add_ephemeral_cache_control_to_block(tool)

    return data


def _prepare_responses_payload(data: dict):
    if "instructions" in data:
        data.setdefault("instructions_cache_control", {"type": "ephemeral"})

    input_data = data.get("input")
    if isinstance(input_data, list):
        for item in input_data:
            _add_ephemeral_cache_control_to_block(item)
            if isinstance(item, dict):
                _add_ephemeral_cache_control_to_content(item.get("content"))

    tools = data.get("tools")
    if isinstance(tools, list):
        for tool in tools:
            _add_ephemeral_cache_control_to_block(tool)

    return data


@Depends
async def _new_client():
    from httpx import AsyncClient

    async with AsyncClient(base_url=str(env.base_url), headers={"Authorization": f"Bearer {env.api_key}"}, timeout=60, http2=True, follow_redirects=True) as client:
        yield client


@app.get("/api/tags")
async def models(client=_new_client):
    res = await client.get("/models")
    res.raise_for_status()
    try:
        data = res.json()["data"]
    except (KeyError, TypeError):
        data = []
    models_map = {i["id"]: {"name": i["id"], "model": i["id"]} for i in data} | {i: {"name": i, "model": i} for i in env.extra_models}
    return {"models": list(models_map.values())}


@app.post("/api/show")
async def show_model():
    return {
        "model_info": {"general.architecture": "CausalLM"},
        "capabilities": ["completion", *env.capabilities],
    }


@app.get("/v1/models")
async def list_models(client=_new_client):
    res = await client.get("/models")
    res.raise_for_status()
    return res.json()


@app.post("/v1/chat/completions")
async def chat_completions(request: Request, client=_new_client):
    data = _prepare_chat_completions_payload(await request.json())

    if data.get("stream", False):

        async def stream():
            async with client.stream("POST", "/chat/completions", json=data) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

        return StreamingResponse(stream(), media_type="text/event-stream")

    else:
        res = await client.post("/chat/completions", json=data)
        res.raise_for_status()
        return res.json()


@app.post("/v1/responses")
async def responses(request: Request, client=_new_client):
    data = _prepare_responses_payload(await request.json())

    if data.get("stream", False):

        async def stream():
            async with client.stream("POST", "/responses", json=data) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

        return StreamingResponse(stream(), media_type="text/event-stream")

    else:
        res = await client.post("/responses", json=data)
        res.raise_for_status()
        return res.json()


@app.get("/api/version")
async def ollama_version():
    return {"version": "0.12.10"}
