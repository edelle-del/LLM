import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx


JAVA_SERVICE_URL = os.getenv("JAVA_SERVICE_URL", "http://localhost:8080")

app = FastAPI(title="Python LLM Gateway", version="1.0.0")


class PromptRequest(BaseModel):
    prompt: str


class GenerationResponse(BaseModel):
    result: str


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/generate", response_model=GenerationResponse)
async def generate(req: PromptRequest) -> GenerationResponse:
    """
    Accepts a prompt string and forwards it to the Java LLM service.
    """
    target_url = f"{JAVA_SERVICE_URL.rstrip('/')}/llm/generate"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(target_url, json=req.dict())
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error calling LLM service: {e}") from e

    data = resp.json()
    result = data.get("result")
    if result is None:
        raise HTTPException(status_code=502, detail="LLM service did not return a 'result' field")

    return GenerationResponse(result=result)

