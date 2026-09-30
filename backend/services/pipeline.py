"""
Feature flag: which search + answer rules the app uses.

  PIPELINE=v2   (Render -> Environment)  -> new system: gold pieces with full labels + re-ranker,
                                            stricter answer rules + number check, answer cache
  not set / v1                          -> exactly today's system

Automatic detour: if v2 fails on a question (missing file, error, crash), THAT question is answered
with v1 and the log says "[FALLBACK] v2 failed -> used v1". Nobody has to touch Render.
"""
import os

from backend.services.reqlog import log
from backend.services import retriever as v1


def wanted() -> str:
    return "v2" if os.getenv("PIPELINE", "v1").strip().lower() == "v2" else "v1"


def search(query: str, boost_terms: str = ""):
    """Returns (results, stats, pipeline_used)."""
    if wanted() == "v2":
        try:
            from backend.services import retriever_v2
            results, stats = retriever_v2.search(query, boost_terms=boost_terms)
            return results, stats, "v2"
        except Exception as e:
            log("FALLBACK", f"⚠️ v2 search failed ({type(e).__name__}: {str(e)[:160]}) -> used v1")
    results, stats = v1.search(query, boost_terms=boost_terms)
    stats["pipeline"] = "v1"
    return results, stats, "v1"


def warm_up():
    """Load v2 at startup when it is switched on, so the first question isn't slow (errors are only logged)."""
    if wanted() == "v2":
        try:
            from backend.services import retriever_v2
            retriever_v2.load()
        except Exception as e:
            log("FALLBACK", f"⚠️ v2 could not load at startup ({e}); questions will use v1")
