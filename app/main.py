# app/main.py
import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
).rstrip("/")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
APP_NAME = os.getenv("APP_NAME", "Brand Studio")
APP_URL = os.getenv("APP_URL", "http://localhost:8000")

app = FastAPI(title=APP_NAME, version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class DesignRequest(BaseModel):
    brand_name: str = Field(min_length=1, max_length=120)
    industry: str = Field(min_length=1, max_length=160)
    audience: str = Field(default="", max_length=500)
    product: str = Field(default="", max_length=500)
    style: str = Field(default="", max_length=300)
    deliverables: list[str] = Field(default_factory=list, max_length=12)
    model: str | None = Field(default=None, max_length=200)


def openrouter_headers() -> dict[str, str]:
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="OPENROUTER_API_KEY is not configured on the server.",
        )

    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": APP_URL,
        "X-Title": APP_NAME,
    }


@app.get("/")
async def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME}


@app.get("/api/models")
async def list_models() -> dict[str, Any]:
    headers = openrouter_headers()
    url = f"{OPENROUTER_BASE_URL}/models"

    try:
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="OpenRouter could not return the model list.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to OpenRouter.",
        ) from exc

    payload = response.json()
    models = payload.get("data", [])

    # Return a compact list suitable for a model selector.
    simplified = [
        {
            "id": item.get("id", ""),
            "name": item.get("name") or item.get("id", ""),
            "context_length": item.get("context_length"),
        }
        for item in models
        if item.get("id")
    ]

    return {"data": simplified}


@app.post("/api/design")
async def create_design(request: DesignRequest) -> dict[str, Any]:
    headers = openrouter_headers()
    model = request.model or DEFAULT_MODEL

    system_prompt = """
You are a professional brand identity and packaging design assistant.
Create useful, production-aware creative direction.
Return your answer in Arabic.
Do not claim that generated concepts are production-ready print files.
Use these sections:
1. ملخص العلامة
2. الفكرة الإبداعية
3. لوحة الألوان (HEX values)
4. الخطوط المقترحة
5. اتجاه الشعار
6. فكرة التغليف والملصق
7. النصوص الإعلانية
8. مواصفات الإنتاج التي يجب تأكيدها
Be concise, specific, and avoid unsupported claims.
""".strip()

    user_prompt = f"""
Create a complete first-pass creative direction for this brand.

Brand name: {request.brand_name}
Industry: {request.industry}
Product: {request.product or "Not specified"}
Target audience: {request.audience or "Not specified"}
Preferred visual style: {request.style or "Open to proposals"}
Requested deliverables: {", ".join(request.deliverables) or "Brand identity and packaging"}
""".strip()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        message = "OpenRouter rejected the request."
        try:
            error_payload = exc.response.json()
            message = error_payload.get("error", {}).get("message", message)
        except (ValueError, AttributeError):
            pass
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=message,
        ) from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="The model request timed out. Try again.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to OpenRouter.",
        ) from exc

    result = response.json()
    choices = result.get("choices", [])
    if not choices:
        raise HTTPException(status_code=502, detail="The model returned no result.")

    message = choices[0].get("message", {}).get("content", "")
    if isinstance(message, list):
        message = "\n".join(
            part.get("text", "")
            for part in message
            if isinstance(part, dict)
        )

    return {
        "model": result.get("model", model),
        "design": message,
        "usage": result.get("usage"),
    }
