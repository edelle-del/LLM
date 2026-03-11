import os
import json

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def health(request):
    return JsonResponse({"status": "ok"})


@csrf_exempt
def generate(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        payload = request.body.decode("utf-8")
        body = {} if not payload else json.loads(payload)
    except ValueError:
        return JsonResponse({"detail": "Invalid JSON body"}, status=400)

    prompt = body.get("prompt")
    if prompt is None:
        prompt = ""

    api_key = os.getenv("LLM_API_KEY", "")
    mock_when_missing_key = os.getenv("LLM_API_MOCK_WHEN_MISSING_KEY", "true").lower() == "true"

    if not api_key:
        if mock_when_missing_key:
            return JsonResponse({"result": f"Mock LLM response for prompt: {prompt}"})
        return JsonResponse({"detail": "LLM_API_KEY is not configured"}, status=502)

    base_url = os.getenv("LLM_API_BASE_URL", "https://api.openai.com").rstrip("/")
    chat_path = os.getenv("LLM_API_CHAT_PATH", "/v1/chat/completions")
    model = os.getenv("LLM_API_MODEL", "gpt-4o-mini")

    url = f"{base_url}{chat_path if chat_path.startswith('/') else '/' + chat_path}"
    request_body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=request_body,
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        return JsonResponse({"detail": f"LLM API request failed: {exc}"}, status=502)

    try:
        data = resp.json()
    except ValueError:
        return JsonResponse({"detail": "LLM API returned invalid JSON"}, status=502)

    result = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content")
    )
    if result is None:
        return JsonResponse({"detail": "LLM API returned no message content"}, status=502)

    return JsonResponse({"result": result})
