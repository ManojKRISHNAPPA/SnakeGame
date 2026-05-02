#!/usr/bin/env python3
"""
LLM client with fallback chain: Ollama (local) → HuggingFace (free) → OpenAI
Set environment variables to configure:
  OLLAMA_HOST   - default: http://localhost:11434
  OLLAMA_MODEL  - default: mistral
  HF_API_TOKEN  - HuggingFace API token (free at huggingface.co)
  HF_MODEL      - default: mistralai/Mistral-7B-Instruct-v0.2
  OPENAI_API_KEY - OpenAI API key (fallback)
"""

import os
import json
import time
import urllib.request
import urllib.error

OLLAMA_HOST  = os.environ.get("OLLAMA_HOST",  "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")
HF_MODEL     = os.environ.get("HF_MODEL",     "mistralai/Mistral-7B-Instruct-v0.2")


def _http_post(url, headers, body, timeout=120):
    data = json.dumps(body).encode("utf-8")
    req  = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ensure_ollama_model():
    """Check if model is already pulled locally; pull only if missing."""
    url = f"{OLLAMA_HOST}/api/tags"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    pulled = [m["name"].split(":")[0] for m in data.get("models", [])]
    if OLLAMA_MODEL.split(":")[0] not in pulled:
        print(f"[AI] Model '{OLLAMA_MODEL}' not found locally — pulling now (one-time)...")
        pull_data = json.dumps({"name": OLLAMA_MODEL, "stream": False}).encode("utf-8")
        pull_req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/pull", data=pull_data,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(pull_req, timeout=600) as resp:
            resp.read()
        print(f"[AI] Model '{OLLAMA_MODEL}' pulled successfully.")
    else:
        print(f"[AI] Model '{OLLAMA_MODEL}' already available locally.")


def _call_ollama(prompt):
    print("[AI] Trying Ollama (local)...")
    _ensure_ollama_model()
    result = _http_post(
        f"{OLLAMA_HOST}/api/generate",
        {"Content-Type": "application/json"},
        {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    return result["response"]


def _call_huggingface(prompt):
    token = os.environ.get("HF_API_TOKEN", "")
    if not token:
        raise ValueError("HF_API_TOKEN not set")
    print(f"[AI] Trying HuggingFace free API (model: {HF_MODEL})...")

    # Mistral-Instruct prompt format
    formatted = f"<s>[INST] {prompt} [/INST]"

    for attempt in range(3):
        try:
            result = _http_post(
                f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                {
                    "Authorization": f"Bearer {token}",
                    "Content-Type":  "application/json",
                },
                {
                    "inputs": formatted,
                    "parameters": {
                        "max_new_tokens":  1024,
                        "temperature":     0.3,
                        "return_full_text": False,
                    },
                },
                timeout=120,
            )
            if isinstance(result, list):
                return result[0].get("generated_text", "").strip()
            if isinstance(result, dict) and "error" in result:
                wait = int(result.get("estimated_time", 20))
                print(f"[AI] HuggingFace model loading... waiting {wait}s (attempt {attempt+1}/3)")
                time.sleep(wait)
                continue
            return str(result)
        except urllib.error.HTTPError as e:
            if e.code == 503 and attempt < 2:
                print(f"[AI] HuggingFace 503, retrying in 20s...")
                time.sleep(20)
            else:
                raise
    raise RuntimeError("HuggingFace: model failed to load after retries")


def _call_openai(prompt):
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise ValueError("OPENAI_API_KEY not set")
    print("[AI] Trying OpenAI (fallback)...")
    result = _http_post(
        "https://api.openai.com/v1/chat/completions",
        {
            "Authorization": f"Bearer {key}",
            "Content-Type":  "application/json",
        },
        {
            "model":    "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
        },
        timeout=60,
    )
    return result["choices"][0]["message"]["content"]


def ask_llm(prompt):
    """Try each provider in order; return response text or a fallback message."""
    providers = [
        ("Ollama",       _call_ollama),
        ("HuggingFace",  _call_huggingface),
        ("OpenAI",       _call_openai),
    ]
    errors = []
    for name, fn in providers:
        try:
            response = fn(prompt)
            print(f"[AI] {name} responded successfully.")
            return response
        except Exception as e:
            errors.append(f"{name}: {e}")
            print(f"[AI] {name} failed: {e}")

    return (
        "## AI Analysis Unavailable\n\n"
        "Could not reach any LLM provider:\n"
        + "\n".join(f"- {e}" for e in errors)
        + "\n\n**To enable AI analysis:**\n"
        "- Local: run `ollama serve` and `ollama pull mistral`\n"
        "- Free cloud: set `HF_API_TOKEN` (get token at huggingface.co)\n"
        "- OpenAI: set `OPENAI_API_KEY`"
    )
