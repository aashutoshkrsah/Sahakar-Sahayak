"""
Health of every moving part, for people (the startup block in the Render log) and for the browser
(GET /health/details). Nothing here calls an AI: it only looks at keys, loaded files and today's counters.
"""
import os
from datetime import datetime, timezone

LINE = "═" * 66


def _ok(v):
    return "✅" if v else "❌"


def details() -> dict:
    from backend.services import pipeline, cloudflare, gemini, llm_chain, live_judge, meaning
    from backend.services import retriever as v1
    v2 = None
    try:
        from backend.services import retriever_v2 as v2
    except Exception:
        pass
    meaning._load("cf")
    meaning._load("gemini")
    meaning._load_scores()
    cfg = llm_chain.configured()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    judges = {j: {"has_key": live_judge._has_key(j), "used_today": live_judge._used.get(f"{today}:{j}", 0),
                  "daily_limit": live_judge.DAILY_LIMIT.get(j)} for j in live_judge.JUDGE_ORDER}
    return {
        "time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "pipeline": {**pipeline.status(), "why": pipeline.why()},
        "search_data": {
            "v1_pieces": len(v1.chunks), "v1_meaning_numbers": v1._vectors is not None,
            "v2_loaded": bool(v2 and v2._ready), "v2_gold_pieces": len(v2.pieces) if v2 else 0,
            "v2_meaning_numbers": bool(v2 and v2._vectors is not None),
            "v2_gemini_backup_numbers": bool(v2 and v2._gvectors is not None),
            "saved_question_numbers": len(meaning._vecs.get("cf") or {}),
            "saved_librarian_scores": len(meaning._scores or {}),
        },
        "cloudflare_accounts": cloudflare.status(),
        "answer_chain": [{"ai": p, "has_key": bool(cfg.get(p))} for p in llm_chain.DEFAULT_ORDER] + [{"ai": "search_only", "has_key": True}],
        "gemini_key": gemini.configured(),
        "judges": judges,
        "live_judge_on": live_judge.ENABLED,
    }


def startup_report() -> None:
    """The block printed once when Render starts (search the log for STARTUP CHECK)."""
    try:
        d = details()
    except Exception as e:
        print(f"{LINE}\nSAHAKAR SAHAYAK · STARTUP CHECK could not run: {e}\n{LINE}", flush=True)
        return
    p, s = d["pipeline"], d["search_data"]
    from backend.services import pipeline as _pl
    pipe = f"PIPELINE      : serving {p['active'].upper()} ({_pl.why()})"
    cf = " · ".join(f"{a['account']} {'🪫 used up today' if a['used_up_today'] else '✅'}"
                    for a in d["cloudflare_accounts"]) or "no keys ❌"
    chain = " → ".join(f"{a['ai']} {_ok(a['has_key'])}" for a in d["answer_chain"])
    judges = " → ".join(f"{j} {_ok(v['has_key'])}" for j, v in d["judges"].items())
    lines = [
        LINE, "SAHAKAR SAHAYAK · STARTUP CHECK", LINE, pipe,
        f"MEANING DATA  : v1 {_ok(s['v1_meaning_numbers'])} · v2 {_ok(s['v2_meaning_numbers'])} · "
        f"Gemini backup {_ok(s['v2_gemini_backup_numbers'])} · {s['saved_question_numbers']} saved questions · "
        f"{s['saved_librarian_scores']} librarian scores",
        f"CLOUDFLARE    : {cf}",
        f"ANSWER CHAIN  : {chain}",
        f"JUDGES        : {judges}  (first 2 that work check each answer)" + ("" if d["live_judge_on"] else "  [LIVE_JUDGE=off]"),
        "LOG GUIDE     : search 'HANDOVER' (who took charge), 'SUMMARY' (one line per question), "
        "'PIPELINE SWITCH' (v2 resting)",
        "STATUS PAGE   : /health/details", LINE,
    ]
    print("\n".join(lines), flush=True)
