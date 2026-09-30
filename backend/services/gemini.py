"""
Google Gemini API (one key: GEMINI_API_KEY, free from aistudio.google.com) -- three jobs:

  Gemma 4 31B          judge 2 of every live answer, and a Test 3 judge   (GEMMA_MODEL, default gemma-4-31b-it)
  Gemini Flash Lite    spare judge + the LAST backup answer writer         (GEMINI_LITE_MODEL, default gemini-3.1-flash-lite)
  Gemini Embedding     backup meaning-numbers when Cloudflare is down      (GEMINI_EMBED_MODEL, default gemini-embedding-001)

Free limits (AI Studio, per key): Gemma 30/min & 14,400/day · Flash Lite 15/min & 500/day ·
Embedding 100/min & 1,000/day. Note: Google may use free-tier requests to improve its products.
"""
import os
import threading
import time

import numpy as np
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma-4-31b-it").strip()
LITE_MODEL = os.getenv("GEMINI_LITE_MODEL", "gemini-3.1-flash-lite").strip()
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001").strip()
EMBED_DIM = int(os.getenv("GEMINI_EMBED_DIM", "768"))
BASE = "https://generativelanguage.googleapis.com/v1beta"

_http = requests.Session()
_lock = threading.Lock()
_last_call = {}                              # model -> time of the last call (gentle per-minute pacing)
MIN_GAP = {GEMMA_MODEL: 2.1, LITE_MODEL: 4.1, EMBED_MODEL: 0.7}


def key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


def configured() -> bool:
    return bool(key())


class GeminiError(RuntimeError):
    def __init__(self, msg, status=None, daily=False):
        super().__init__(msg)
        self.status = status
        self.daily = daily


def _pace(model):
    gap = MIN_GAP.get(model, 0)
    with _lock:
        wait = _last_call.get(model, 0) + gap - time.time()
        _last_call[model] = max(time.time(), _last_call.get(model, 0) + gap)
    if wait > 0:
        time.sleep(min(wait, 10))


def _post(path, payload, timeout):
    if not key():
        raise GeminiError("no GEMINI_API_KEY")
    r = _http.post(f"{BASE}/{path}", json=payload, timeout=timeout,
                   headers={"x-goog-api-key": key(), "Content-Type": "application/json"})
    if r.status_code != 200:
        body = (r.text or "")[:300].replace("\n", " ")
        low = body.lower()
        daily = r.status_code == 429 and ("per day" in low or "perday" in low or "daily" in low)
        raise GeminiError(f"HTTP {r.status_code}: {body}", status=r.status_code, daily=daily)
    return r.json()


def chat(messages, model=None, temperature=0.0, max_tokens=800, timeout=40):
    """messages = [{"role": "system"|"user"|"assistant", "content": "..."}] -> reply text (thinking removed)."""
    model = model or LITE_MODEL
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
                for m in messages if m["role"] != "system"]
    payload = {"contents": contents,
               "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    _pace(model)
    data = _post(f"models/{model}:generateContent", payload, timeout)
    cands = data.get("candidates") or []
    if not cands:
        raise GeminiError(f"no answer ({str(data.get('promptFeedback') or data)[:200]})")
    parts = (cands[0].get("content") or {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    if not text.strip():
        raise GeminiError(f"empty answer (finish reason {cands[0].get('finishReason')})")
    return text.strip()


def embed(texts, task="RETRIEVAL_QUERY", timeout=30):
    """Meaning-numbers for a list of texts (unit length, EMBED_DIM numbers each). Raises on failure."""
    reqs = [{"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": t[:8000]}]},
             "taskType": task, "outputDimensionality": EMBED_DIM} for t in texts]
    _pace(EMBED_MODEL)
    data = _post(f"models/{EMBED_MODEL}:batchEmbedContents", {"requests": reqs}, timeout)
    embs = data.get("embeddings") or []
    if len(embs) != len(texts):
        raise GeminiError(f"expected {len(texts)} embeddings, got {len(embs)}")
    vecs = np.asarray([e.get("values") or [] for e in embs], dtype=np.float32)
    return vecs / np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-8)
