import asyncio
import hashlib
import json
import logging
import time
import uuid
from typing import Optional

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from open_webui.models.users import Users
from open_webui.config import (
    ENABLE_ADMIN_EXPORT,
)
from open_webui.env import (
    AIOHTTP_CLIENT_TIMEOUT,
    AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST,
    AIOHTTP_CLIENT_SESSION_SSL,
    SRC_LOG_LEVELS,
    GLOBAL_LOG_LEVEL,
)

from open_webui.utils.misc import get_last_user_message_item
from open_webui.utils.auth import get_admin_user, get_verified_user

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("GEMINI", GLOBAL_LOG_LEVEL))

router = APIRouter()

##########################################
# Gemini API Configuration
##########################################


class GeminiConfigForm(BaseModel):
    ENABLE_GEMINI_API: Optional[bool] = None
    GEMINI_API_BASE_URLS: list[str]
    GEMINI_API_KEYS: list[str]
    GEMINI_API_CONFIGS: dict


@router.get("/config")
async def get_config(request: Request, user=Depends(get_admin_user)):
    return {
        "ENABLE_GEMINI_API": request.app.state.config.ENABLE_GEMINI_API,
        "GEMINI_API_BASE_URLS": request.app.state.config.GEMINI_API_BASE_URLS,
        "GEMINI_API_KEYS": request.app.state.config.GEMINI_API_KEYS,
        "GEMINI_API_CONFIGS": request.app.state.config.GEMINI_API_CONFIGS,
    }


@router.post("/config/update")
async def update_config(
    request: Request, form_data: GeminiConfigForm, user=Depends(get_admin_user)
):
    request.app.state.config.ENABLE_GEMINI_API = form_data.ENABLE_GEMINI_API
    request.app.state.config.GEMINI_API_BASE_URLS = form_data.GEMINI_API_BASE_URLS
    request.app.state.config.GEMINI_API_KEYS = form_data.GEMINI_API_KEYS
    request.app.state.config.GEMINI_API_CONFIGS = form_data.GEMINI_API_CONFIGS

    return {
        "ENABLE_GEMINI_API": request.app.state.config.ENABLE_GEMINI_API,
        "GEMINI_API_BASE_URLS": request.app.state.config.GEMINI_API_BASE_URLS,
        "GEMINI_API_KEYS": request.app.state.config.GEMINI_API_KEYS,
        "GEMINI_API_CONFIGS": request.app.state.config.GEMINI_API_CONFIGS,
    }


##########################################
# Gemini API Models
##########################################


async def get_gemini_models(url: str, key: str) -> dict:
    """
    Fetch models from Gemini API and convert to OpenAI format.
    """
    try:
        async with aiohttp.ClientSession(
            trust_env=True,
            timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST),
        ) as session:
                # Convert Gemini models to OpenAI format
                models = []
                page_token = None
                
                while True:
                    url_with_params = f"{url}/models?key={key}"
                    if page_token:
                        url_with_params += f"&pageToken={page_token}"

                    async with session.get(
                        url_with_params,
                        headers={
                            "Content-Type": "application/json",
                        },
                        ssl=AIOHTTP_CLIENT_SESSION_SSL,
                    ) as r:
                        if r.status != 200:
                            error_detail = await r.text()
                            raise Exception(f"Gemini API Error: {error_detail}")

                        response_data = await r.json(content_type=None)
                        
                        for model in response_data.get("models", []):
                            model_name = model.get("name", "").replace("models/", "")
                            models.append({
                                "id": model_name,
                                "name": model.get("displayName", model_name),
                                "owned_by": "google",
                                "gemini": model,
                            })
                        
                        page_token = response_data.get("nextPageToken")
                        if not page_token:
                            break
                
                return {"data": models, "object": "list"}

    except Exception as e:
        log.error(f"Error fetching Gemini models: {e}")
        raise


@router.get("/models")
@router.get("/models/{url_idx}")
async def get_models(
    request: Request, url_idx: Optional[int] = None, user=Depends(get_verified_user)
):
    models = {"data": []}

    if url_idx is None:
        # Get all models from all configured Gemini endpoints
        if not request.app.state.config.ENABLE_GEMINI_API:
            return models

        for idx, url in enumerate(request.app.state.config.GEMINI_API_BASE_URLS):
            try:
                key = request.app.state.config.GEMINI_API_KEYS[idx]
                api_config = request.app.state.config.GEMINI_API_CONFIGS.get(
                    str(idx), {}
                )
                
                # Check if this connection is enabled
                if not api_config.get("enable", True):
                    continue

                # Get configured model_ids or fetch from API
                model_ids = api_config.get("model_ids", [])
                prefix_id = api_config.get("prefix_id", "")
                tags = api_config.get("tags", [])

                if model_ids:
                    # Use configured model list
                    for model_id in model_ids:
                        full_id = f"{prefix_id}.{model_id}" if prefix_id else model_id
                        models["data"].append({
                            "id": full_id,
                            "name": model_id,
                            "owned_by": "google",
                            "urlIdx": idx,
                            "tags": tags,
                        })
                else:
                    # Fetch from API
                    result = await get_gemini_models(url, key)
                    for model in result.get("data", []):
                        if prefix_id:
                            model["id"] = f"{prefix_id}.{model['id']}"
                        if tags:
                            model["tags"] = tags
                        model["urlIdx"] = idx
                        models["data"].append(model)

            except Exception as e:
                log.error(f"Error fetching models from Gemini endpoint {idx}: {e}")
                continue
    else:
        # Get models from specific endpoint
        url = request.app.state.config.GEMINI_API_BASE_URLS[url_idx]
        key = request.app.state.config.GEMINI_API_KEYS[url_idx]
        models = await get_gemini_models(url, key)

    return models


##########################################
# Gemini Connection Verification
##########################################


class ConnectionVerificationForm(BaseModel):
    url: str
    key: str
    config: Optional[dict] = None


@router.post("/verify")
async def verify_connection(
    request: Request,
    form_data: ConnectionVerificationForm,
    user=Depends(get_admin_user),
):
    url = form_data.url
    key = form_data.key

    try:
        result = await get_gemini_models(url, key)
        return result
    except Exception as e:
        log.error(f"Gemini connection verification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Connection verification failed: {str(e)}",
        )


##########################################
# OpenAI to Gemini Format Conversion
##########################################


def convert_openai_to_gemini_messages(openai_messages: list) -> tuple[list, Optional[dict]]:
    """
    Convert OpenAI messages to Gemini contents format.
    Returns (contents, system_instruction)
    
    Extracts system messages for v1beta's system_instruction parameter.
    Handles multimodal content (images).
    """
    gemini_contents = []
    system_messages = []

    for msg in openai_messages:
        role = msg.get("role")
        content = msg.get("content")

        # Extract system messages for system_instruction
        if role == "system":
            if isinstance(content, str):
                system_messages.append(content)
            continue

        # Map roles: assistant -> model, user -> user
        gemini_role = "model" if role == "assistant" else "user"

        parts = []

        # Handle string content
        if isinstance(content, str):
            parts.append({"text": content})

        # Handle multimodal content (array)
        elif isinstance(content, list):
            for item in content:
                item_type = item.get("type")

                if item_type == "text":
                    parts.append({"text": item.get("text", "")})

                elif item_type == "image_url":
                    # CRITICAL: Convert base64 images to Gemini inlineData format
                    image_url = item.get("image_url", {}).get("url", "")

                    if image_url.startswith("data:"):
                        try:
                            # Parse: data:image/png;base64,iVBORw...
                            header, base64_data = image_url.split(",", 1)
                            mime_type = header.split(":")[1].split(";")[0]

                            parts.append({
                                "inlineData": {
                                    "mimeType": mime_type,
                                    "data": base64_data  # base64 without prefix
                                }
                            })
                        except Exception as e:
                            log.error(f"Failed to parse image data URL: {e}")
                    else:
                        log.warning(f"External image URLs not supported: {image_url}")

        if parts:
            gemini_contents.append({
                "role": gemini_role,
                "parts": parts
            })

    # Prepare system_instruction if we have system messages
    system_instruction = None
    if system_messages:
        system_instruction = {
            "parts": [{"text": "\n\n".join(system_messages)}]
        }

    return gemini_contents, system_instruction


def get_safety_settings() -> list:
    """
    Safety settings to prevent overly strict content filtering.
    Using BLOCK_NONE for maximum freedom (user's choice).
    """
    return [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]


def convert_openai_to_gemini_payload(openai_payload: dict) -> dict:
    """
    Convert OpenAI chat completion payload to Gemini v1beta format.
    Uses native system_instruction (v1beta feature).
    """
    gemini_payload = {}

    messages = openai_payload.get("messages", [])

    # Convert messages and extract system_instruction
    contents, system_instruction = convert_openai_to_gemini_messages(messages)
    gemini_payload["contents"] = contents

    if system_instruction:
        gemini_payload["systemInstruction"] = system_instruction

    # Convert generation parameters
    generation_config = {}

    if "temperature" in openai_payload:
        generation_config["temperature"] = openai_payload["temperature"]

    if "max_tokens" in openai_payload:
        generation_config["maxOutputTokens"] = openai_payload["max_tokens"]

    if "top_p" in openai_payload:
        generation_config["topP"] = openai_payload["top_p"]

    if "stop" in openai_payload:
        generation_config["stopSequences"] = openai_payload["stop"]

    if generation_config:
        gemini_payload["generationConfig"] = generation_config

    # Safety settings (BLOCK_NONE for all categories)
    gemini_payload["safetySettings"] = get_safety_settings()

    return gemini_payload


def convert_gemini_to_openai_response(gemini_response: dict, model: str) -> dict:
    """
    Convert Gemini response to OpenAI format (non-streaming).
    """
    candidates = gemini_response.get("candidates", [])
    if not candidates:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [],
            "usage": {}
        }

    candidate = candidates[0
]
    content = candidate.get("content", {})
    parts = content.get("parts", [])

    # Concatenate all text parts
    text_content = ""
    for part in parts:
        text_content += part.get("text", "")
        inline_data = part.get("inlineData")
        if inline_data:
            mime_type = inline_data.get("mimeType", "image/png")
            data = inline_data.get("data", "")
            text_content += f"\n![Generated Image](data:{mime_type};base64,{data})\n"

    # Map finish reason
    finish_reason_map = {
        "STOP": "stop",
        "MAX_TOKENS": "length",
        "SAFETY": "content_filter",
        "RECITATION": "content_filter",
        "OTHER": "stop"
    }

    finish_reason = finish_reason_map.get(
        candidate.get("finishReason", "STOP"),
        "stop"
    )

    # Extract usage metadata
    usage_meta = gemini_response.get("usageMetadata", {})

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": text_content
            },
            "finish_reason": finish_reason
        }],
        "usage": {
            "prompt_tokens": usage_meta.get("promptTokenCount", 0),
            "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
            "total_tokens": usage_meta.get("totalTokenCount", 0)
        }
    }


async def stream_gemini_to_openai(stream: aiohttp.StreamReader, model: str):
    """
    Convert Gemini SSE stream to OpenAI SSE format in real-time.
    
    CRITICAL: Gemini's streaming format is completely different from OpenAI.
    Must parse each chunk, extract text from nested structure, and re-encode.
    """
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    buffer = b""

    async for data, _ in stream.iter_chunks():
        if not data:
            continue

        lines = (buffer + data).split(b"\n")
        buffer = lines[-1]  # Save incomplete line

        for line in lines[:-1]:
            line = line.strip()

            if not line or line == b"data: [DONE]":
                continue

            # Remove "data: " prefix if present
            if line.startswith(b"data: "):
                json_str = line[6:]

                try:
                    gemini_chunk = json.loads(json_str)

                    # Extract text from Gemini's nested structure
                    candidates = gemini_chunk.get("candidates", [])
                    if not candidates:
                        continue

                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])

                    # Gemini can have multiple parts per chunk
                    for part in parts:
                        text = part.get("text", "")
                        inline_data = part.get("inlineData")
                        
                        if inline_data:
                            mime_type = inline_data.get("mimeType", "image/png")
                            data = inline_data.get("data", "")
                            text += f"\n![Generated Image](data:{mime_type};base64,{data})\n"

                        if text:
                            # Convert to OpenAI format
                            openai_chunk = {
                                "id": completion_id,
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": model,
                                "choices": [{
                                    "index": 0,
                                    "delta": {"content": text},
                                    "finish_reason": None
                                }]
                            }

                            # Yield as SSE
                            yield f"data: {json.dumps(openai_chunk)}\n\n".encode()

                    # Check for finish reason
                    finish_reason = candidates[0].get("finishReason")
                    if finish_reason:
                        # Map Gemini finish reasons to OpenAI
                        finish_map = {
                            "STOP": "stop",
                            "MAX_TOKENS": "length",
                            "SAFETY": "content_filter",
                            "RECITATION": "content_filter",
                            "OTHER": "stop"
                        }

                        final_chunk = {
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": model,
                            "choices": [{
                                "index": 0,
                                "delta": {},
                                "finish_reason": finish_map.get(finish_reason, "stop")
                            }]
                        }
                        
                        # Add usage if available
                        if "usageMetadata" in gemini_chunk:
                            final_chunk["usage"] = gemini_chunk["usageMetadata"]

                        yield f"data: {json.dumps(final_chunk)}\n\n".encode()

                except json.JSONDecodeError as e:
                    log.error(f"Failed to parse Gemini SSE chunk: {e}")
                    continue

    # Send [DONE] marker
    yield b"data: [DONE]\n\n"


async def generate_chat_completion(
    request: Request,
    form_data: dict,
    user: Users,
    bypass_filter: bool = False,
):
    model_id = form_data.get("model")
    model_info = request.app.state.MODELS.get(model_id)
    
    if not model_info:
        raise HTTPException(status_code=404, detail="Model not found")

    # Get URL and Key based on urlIdx
    url_idx = model_info.get("urlIdx")
    if url_idx is None:
         raise HTTPException(status_code=400, detail="Model configuration error: urlIdx missing")

    url = request.app.state.config.GEMINI_API_BASE_URLS[url_idx]
    key = request.app.state.config.GEMINI_API_KEYS[url_idx]

    # Convert payload
    gemini_payload = convert_openai_to_gemini_payload(form_data)
    
    log.info(f"Gemini Request model_info: {model_info}")

    # Determine actual model ID
    actual_model_id = ""
    if "gemini" in model_info:
        actual_model_id = model_info["gemini"].get("name", "")
    
    if not actual_model_id:
        actual_model_id = model_info.get("name", model_id)

    # Final fallback
    if not actual_model_id:
        actual_model_id = model_id

    # Clean up model ID
    if actual_model_id.startswith("models/"):
        actual_model_id = actual_model_id[7:]
    
    if actual_model_id.startswith("/"):
        actual_model_id = actual_model_id[1:]
        
    log.info(f"Gemini Request: model_id={model_id} actual_model_id={actual_model_id}")
    
    # Construct URL
    stream = form_data.get("stream", False)
    action = "streamGenerateContent?alt=sse" if stream else "generateContent"
    
    target_url = f"{url}/models/{actual_model_id}:{action}&key={key}"
    log.info(f"Gemini Target URL: {target_url}")

    if stream:
        async def stream_wrapper():
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT)
                ) as session:
                    async with session.post(
                        target_url,
                        json=gemini_payload,
                        headers={"Content-Type": "application/json"},
                    ) as r:
                        if r.status != 200:
                            error_detail = await r.text()
                            yield f"data: {json.dumps({'error': {'message': f'Gemini API Error: {error_detail}'}})}\n\n"
                            return

                        async for chunk in stream_gemini_to_openai(r.content, model_id):
                            yield chunk
            except Exception as e:
                log.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'error': {'message': str(e)}})}\n\n"

        return StreamingResponse(
            stream_wrapper(),
            media_type="text/event-stream"
        )
    else:
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT)
            ) as session:
                async with session.post(
                    target_url,
                    json=gemini_payload,
                    headers={"Content-Type": "application/json"},
                ) as r:
                    if r.status != 200:
                        error_detail = await r.text()
                        raise Exception(f"Gemini API Error: {error_detail}")

                    data = await r.json(content_type=None)
                    return convert_gemini_to_openai_response(data, model_id)

        except Exception as e:
            log.error(f"Gemini chat completion error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/completions")
async def chat_completion(
    request: Request,
    form_data: dict,
    user=Depends(get_verified_user),
):
    return await generate_chat_completion(request, form_data, user)
