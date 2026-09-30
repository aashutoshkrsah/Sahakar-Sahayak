"""
Meaning search that (almost) never switches off.

The question's meaning-numbers are found in this order:
  1. SAVED  -- numbers already made for this exact text (the test questions are saved in the repo, so the
               Re-check button needs NO Cloudflare call for them; live questions are remembered in memory)
  2. Cloudflare account 1  (bge-m3)
  3. Cloudflare account 2  (bge-m3, same numbers -- see cloudflare.py)
  4. Gemini Embedding      (different numbers, so it is compared with the Gemini copy of the gold pieces)
  5. nothing works -> word search only (the caller handles it; the app still answers)

The senior librarian (re-ranker) scores are saved the same way: the Re-check button reads them from the repo,
and live questions are capped per day (LIBRARIAN_DAILY) so the librarian can never eat the meaning-search budget.

Saved files (made once in Codespaces by  python3 -m backend.pipeline.embed , then committed):
  backend/data/medallion/saved/query_numbers_cf.npy / .json
  backend/data/medallion/saved/query_numbers_gemini.npy / .json
  backend/data/medallion/saved/librarian_scores.json
"""
import hashlib
import json
import os
import threading
from datetime import datetime, timezone

import numpy as np

from backend.services.reqlog import log

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SAVED_DIR = os.path.join(BASE_DIR, "backend", "data", "medallion", "saved")
CF_MODEL = "@cf/baai/bge-m3"
LIBRARIAN_DAILY = int(os.getenv("LIBRARIAN_DAILY", "2000"))   # live re-ranker calls per day (~2 units each)
MAX_MEMORY = 20000

_lock = threading.Lock()
_vecs = {}            # engine -> {key: vector}
_loaded = set()
_scores = None        # key -> librarian score
_dirty = False
_librarian_used = {}  # "YYYY-MM-DD" -> live librarian calls today


def _key(text):
    return hashlib.sha1((text or "").strip().encode("utf-8")).hexdigest()[:20]


def _files(engine):
    return (os.path.join(SAVED_DIR, f"query_numbers_{engine}.npy"),
            os.path.join(SAVED_DIR, f"query_numbers_{engine}.json"))


def _model(engine):
    if engine == "cf":
        return CF_MODEL
    from backend.services import gemini
    return f"{gemini.EMBED_MODEL}:{gemini.EMBED_DIM}"


def _load(engine):
    if engine in _loaded:
        return
    with _lock:
        if engine in _loaded:
            return
        store = _vecs.setdefault(engine, {})
        npy, meta = _files(engine)
        try:
            with open(meta, encoding="utf-8") as f:
                m = json.load(f)
            if m.get("model") == _model(engine):
                mat = np.load(npy).astype(np.float32)
                for k, row in zip(m["keys"], mat):
                    store.setdefault(k, row)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ saved {engine} question numbers could not be read: {e}")
        _loaded.add(engine)


def _live(engine, text):
    if engine == "cf":
        from backend.services import cloudflare
        from backend.services import retriever
        return retriever._embed([text], timeout=retriever.QUERY_TIMEOUT)[0]
    from backend.services import gemini
    return gemini.embed([text], task="RETRIEVAL_QUERY", timeout=8)[0]


def engine_ready(engine) -> bool:
    if engine == "cf":
        from backend.services import cloudflare
        return cloudflare.available()
    from backend.services import gemini
    return gemini.configured()


def query_vector(text, engine):
    """(vector, "saved"|"live") or (None, reason). Never raises."""
    global _dirty
    _load(engine)
    k = _key(text)
    v = _vecs.get(engine, {}).get(k)
    if v is not None:
        return v, "saved"
    if not engine_ready(engine):
        return None, "not available"
    try:
        v = np.asarray(_live(engine, text), dtype=np.float32)
    except Exception as e:
        return None, str(e)[:200]
    with _lock:
        store = _vecs.setdefault(engine, {})
        if len(store) < MAX_MEMORY:
            store[k] = v
            _dirty = True
    return v, "live"


def similarities(text, options):
    """options = [(engine, piece_matrix, transform)] in order of preference (transform maps the engine's
    similarities onto Cloudflare's scale, or None). Returns (sims, engine, source) or (None, None, reasons)."""
    reasons = []
    for engine, matrix, transform in options:
        if matrix is None:
            reasons.append(f"{engine}: no saved piece numbers")
            continue
        v, src = query_vector(text, engine)
        if v is None:
            reasons.append(f"{engine}: {src}")
            continue
        if v.shape[0] != matrix.shape[1]:
            reasons.append(f"{engine}: size mismatch")
            continue
        sims = matrix @ v
        if transform is not None:
            sims = transform(sims)
        return sims, engine, src
    return None, None, "; ".join(reasons)


# ---------------------------------------------------------------------------
# Senior librarian (re-ranker) scores
# ---------------------------------------------------------------------------
def _scores_file():
    return os.path.join(SAVED_DIR, "librarian_scores.json")


def _load_scores():
    global _scores
    if _scores is not None:
        return
    with _lock:
        if _scores is not None:
            return
        try:
            with open(_scores_file(), encoding="utf-8") as f:
                _scores = json.load(f)
        except FileNotFoundError:
            _scores = {}
        except Exception as e:
            print(f"⚠️ saved librarian scores could not be read: {e}")
            _scores = {}


def rerank(query, texts, live_fn):
    """(scores, "saved"|"live") or (None, reason). live_fn(query, texts) -> list of scores or None."""
    global _dirty
    _load_scores()
    keys = [_key(query + "\x00" + t) for t in texts]
    if keys and all(k in _scores for k in keys):
        return [_scores[k] for k in keys], "saved"
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with _lock:
        if _librarian_used.get(day, 0) >= LIBRARIAN_DAILY:
            return None, f"daily librarian limit ({LIBRARIAN_DAILY}) reached"
        _librarian_used[day] = _librarian_used.get(day, 0) + 1
    out = live_fn(query, texts)
    if out is None:
        return None, "librarian call failed"
    with _lock:
        if len(_scores) < MAX_MEMORY * 20:
            for k, s in zip(keys, out):
                _scores[k] = round(float(s), 5)
            _dirty = True
    return out, "live"


def save_all():
    """Write everything remembered so far to the saved files (run by backend.pipeline.embed in Codespaces)."""
    os.makedirs(SAVED_DIR, exist_ok=True)
    counts = {}
    for engine in ("cf", "gemini"):
        _load(engine)
        store = _vecs.get(engine) or {}
        if not store:
            continue
        keys = sorted(store)
        npy, meta = _files(engine)
        np.save(npy, np.vstack([store[k] for k in keys]).astype(np.float16))
        with open(meta, "w", encoding="utf-8") as f:
            json.dump({"model": _model(engine), "keys": keys}, f)
        counts[engine] = len(keys)
    _load_scores()
    with open(_scores_file(), "w", encoding="utf-8") as f:
        json.dump(_scores, f, sort_keys=True)
    counts["librarian"] = len(_scores)
    return counts
