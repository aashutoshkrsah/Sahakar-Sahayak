"""
Feature flag: which search + answer rules the app uses -- with AUTOMATIC fallback, so nobody ever has to
touch Render when something breaks.

  not set / PIPELINE=v2 (default)  -> new system: gold pieces with full labels + re-ranker,
                                       stricter answer rules + number check, answer cache
  PIPELINE=v1 (Render -> Environment) -> the old system, only if you ever want to force it

Automatic fallback, two levels:
  1. ONE question: if v2 fails on it (search OR answer step), THAT question is answered with v1.
     Render log:  🔀 HANDOVER [pipeline] v2 failed (...) → v1 takes charge
  2. BAD PERIOD: if v2 fails on 3 questions in a row, the whole app uses v1 for 10 minutes, then tries
     v2 again by itself.
     Render log:  🚨 PIPELINE SWITCH v2 → v1 for 10 min   ...   ✅ PIPELINE BACK v1 → v2
  (PIPELINE_FAIL_LIMIT and PIPELINE_REST_MINUTES change these numbers.)
"""
import os
import threading
import time

from backend.services.reqlog import log
from backend.services import retriever as v1

FAIL_LIMIT = int(os.getenv("PIPELINE_FAIL_LIMIT", "3"))
REST_SECONDS = float(os.getenv("PIPELINE_REST_MINUTES", "10")) * 60

_lock = threading.Lock()
_state = {"fails_in_row": 0, "rest_until": 0.0, "switches": 0, "v2_ok": 0, "v2_failed": 0, "last_error": None}


def wanted() -> str:
    """What Render asks for: v2 unless PIPELINE=v1 is set."""
    return "v1" if os.getenv("PIPELINE", "v2").strip().lower() == "v1" else "v2"


def active() -> str:
    """What the app really uses right now: v2 when asked for and not resting after repeated failures."""
    if wanted() != "v2":
        return "v1"
    with _lock:
        resting = time.time() < _state["rest_until"]
        was_resting = _state["rest_until"] > 0 and not resting
        if was_resting:
            _state["rest_until"] = 0.0
            _state["fails_in_row"] = 0
    if was_resting:
        log("PIPELINE", "🔁 v2 rest period over -- checking v2 again")
        if not self_check():
            return "v1"
        log("PIPELINE", "✅ PIPELINE BACK v1 → v2 (v2 passed its check again)")
    return "v1" if resting else "v2"


def why() -> str:
    """One line for the logs / status page: which system is serving and why."""
    if wanted() != "v2":
        return "v1 because PIPELINE=v1 is set on Render"
    st = status()
    if st["active"] == "v1":
        return f"v1 for about {max(1, round(st['resting_seconds_left'] / 60))} more min because: {st['last_v2_error']}"
    return "v2 (default) -- passed its checks; any failing question is answered with v1"


def report_failure(where: str, err: Exception) -> None:
    """Count one v2 failure; after FAIL_LIMIT in a row, rest v2 for REST_SECONDS."""
    msg = f"{type(err).__name__}: {str(err)[:160]}"
    with _lock:
        _state["fails_in_row"] += 1
        _state["v2_failed"] += 1
        _state["last_error"] = f"{where}: {msg}"
        switch = _state["fails_in_row"] >= FAIL_LIMIT and time.time() >= _state["rest_until"]
        if switch:
            _state["rest_until"] = time.time() + REST_SECONDS
            _state["switches"] += 1
    log("PIPELINE", f"🔀 HANDOVER [pipeline] v2 {where} failed ({msg}) → v1 takes charge for this question")
    if switch:
        log("PIPELINE", f"🚨 PIPELINE SWITCH v2 → v1 for {REST_SECONDS / 60:.0f} min "
                        f"({FAIL_LIMIT} failures in a row). v2 will be tried again automatically.")


def report_success() -> None:
    with _lock:
        _state["fails_in_row"] = 0
        _state["v2_ok"] += 1


def status() -> dict:
    with _lock:
        s = dict(_state)
    rest = max(0.0, s["rest_until"] - time.time())
    return {"requested": wanted(), "active": active(), "resting_seconds_left": round(rest),
            "v2_questions_ok": s["v2_ok"], "v2_failures": s["v2_failed"], "failures_in_a_row": s["fails_in_row"],
            "automatic_switches": s["switches"], "last_v2_error": s["last_error"],
            "how_it_decides": "v2 by default; a failing question is redone with v1; 3 failures in a row or a failed "
                              "startup self-check rest v2 for 10 minutes, then it is tried again automatically"}


def search(query: str, boost_terms: str = ""):
    """Returns (results, stats, pipeline_used)."""
    if active() == "v2":
        try:
            from backend.services import retriever_v2
            results, stats = retriever_v2.search(query, boost_terms=boost_terms)
            return results, stats, "v2"
        except Exception as e:
            report_failure("search", e)
    elif wanted() == "v2":
        log("PIPELINE", f"⏸ this question uses v1 -- {why()}")
    results, stats = v1.search(query, boost_terms=boost_terms)
    stats["pipeline"] = "v1"
    return results, stats, "v1"


def _rest(reason: str) -> None:
    """Put v2 to rest right away (used when the startup self-check finds a problem)."""
    with _lock:
        _state["rest_until"] = time.time() + REST_SECONDS
        _state["switches"] += 1
        _state["last_error"] = reason
    log("PIPELINE", f"🚨 PIPELINE SWITCH v2 → v1 for {REST_SECONDS / 60:.0f} min: {reason}. "
                    f"v2 will be tried again automatically.")


def self_check() -> bool:
    """Startup self-check: decide by itself whether v2 is fit to serve, and say WHY in the log.
      - v2's gold file can't load                         -> use v1
      - v2 has no meaning-numbers but v1 does             -> use v1 (v1 would search better)
      - otherwise                                         -> use v2"""
    if wanted() != "v2":
        log("PIPELINE", "ℹ️ PIPELINE=v1 is set on Render -- using the old system on purpose")
        return False
    try:
        from backend.services import retriever_v2
        if not retriever_v2._ready:
            retriever_v2.load()
    except Exception as e:
        _rest(f"v2 could not load ({type(e).__name__}: {str(e)[:120]})")
        return False
    if retriever_v2._vectors is None and v1._vectors is not None:
        _rest("v2 has no saved meaning-numbers but v1 has them, so v1 will search better")
        return False
    with _lock:
        _state["fails_in_row"] = 0
    log("PIPELINE", f"✅ self-check passed: v2 ready ({len(retriever_v2.pieces)} gold pieces, "
                    f"meaning search {'ON' if retriever_v2._vectors is not None else 'OFF in both systems'})")
    return True


def warm_up():
    """At startup: load both systems, run the self-check, print the STARTUP CHECK block. Never raises."""
    try:
        if v1._word_index is None:
            v1.build_or_load_index()
    except Exception as e:
        log("PIPELINE", f"⚠️ v1 index could not load at startup: {e}")
    try:
        self_check()
    except Exception as e:
        log("PIPELINE", f"⚠️ self-check could not run: {e}")
    try:
        from backend.services import bench_stats
        bench_stats.warm_up_in_background()          # Explorer statistics ready before anyone opens the page
    except Exception as e:
        log("PIPELINE", f"⚠️ Explorer statistics warm-up skipped: {e}")
    try:
        from backend.services import status
        status.startup_report()
    except Exception as e:
        log("PIPELINE", f"⚠️ startup report could not run: {e}")
