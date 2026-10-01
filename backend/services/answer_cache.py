"""
Answer cache: the same question asked again gets the saved answer instantly, with no AI calls
(saves Sarvam / Groq / Cloudflare credits). On whenever the v2 system is in use (the default), or with ANSWER_CACHE=on.

Safety rules:
  - EXACT repeats only: same words after lower-casing and removing punctuation/extra spaces,
    AND the same answer language. "PM Kisan kitna paisa milta hai?" == "pm kisan kitna paisa milta hai",
    but "PM Kisan kab milta hai" is a different question -> no reuse.
  - Never price questions (prices change daily), refusals, errors or search-only answers.
  - Only answers whose live AI check scored 50 or more are reused (unverified or low-scored ones never are).
  - Saved answers expire after 3 days; at most 2,000 are kept (a few MB of memory).
"""
import copy
import os
import re
import time
from collections import OrderedDict
from threading import Lock

from backend.services import live_judge, pipeline

TTL_SECONDS = 3 * 24 * 3600
MAX_ENTRIES = 2000
MIN_SCORE = 50

_cache = OrderedDict()
_lock = Lock()


def enabled() -> bool:
    return pipeline.wanted() == "v2" or os.getenv("ANSWER_CACHE", "").strip().lower() == "on"


def key(question: str, language: str) -> str:
    words = re.sub(r"[^\w]+", " ", (question or "").lower(), flags=re.UNICODE).split()
    return f"{language}|{pipeline.wanted()}|{' '.join(words)}"


def put(k: str, request_id: str, result: dict) -> None:
    if not enabled():
        return
    if result.get("prices") or result.get("trust_level") in ("refused", "error") \
            or result.get("answered_by") in (None, "search_only"):
        return
    with _lock:
        _cache[k] = {"rid": request_id, "result": copy.deepcopy(result), "t": time.time()}
        _cache.move_to_end(k)
        while len(_cache) > MAX_ENTRIES:
            _cache.popitem(last=False)


def get(k: str):
    """(saved_result, saved_ai_check, original_request_id) for an exact repeat whose AI check scored >= 50, else None."""
    if not enabled():
        return None
    with _lock:
        e = _cache.get(k)
        if not e:
            return None
        if time.time() - e["t"] > TTL_SECONDS:
            _cache.pop(k, None)
            return None
    check = live_judge._results.get(e["rid"])
    if live_judge.ENABLED:
        if not check or check.get("status") != "ok" or (check.get("score") or 0) < MIN_SCORE:
            if check and check.get("status") == "ok":          # checked and scored low: never reuse
                with _lock:
                    _cache.pop(k, None)
            return None
    return copy.deepcopy(e["result"]), (copy.deepcopy(check) if check else None), e["rid"]
