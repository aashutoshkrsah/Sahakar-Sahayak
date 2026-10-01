"""
Statistics for the Explorer page (/scoreboard/explore). Everything is computed from the SAVED benchmark
result files -- no AI is called, no credits are used.

Methods (all explained on the page with an (i) button):
  - score           mean of each answer's grade (correct 1, partial 0.5, wrong 0), averaged over its judges
  - 95% range       bootstrap: re-draw the questions with replacement 2,000 times; middle 95% of the scores
  - paired gain     same questions, with minus without our PDFs, question by question (+ bootstrap range)
  - sign test       better vs worse per question; exact two-sided binomial p-value (ties left out)
  - Cohen's h       effect size for two proportions: 2·asin(√p1) − 2·asin(√p2)  (0.2 small, 0.5 medium, 0.8 large)
  - Cohen's kappa   judge agreement with chance agreement removed (0.61–0.80 = substantial)
  - calibration     of answers the app marked 🟢 Verified, how many the judges graded correct
"""
import hashlib
import json
import math
import os
import random
import statistics
import threading

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GRADE = {"correct": 1.0, "partial": 0.5, "wrong": 0.0}
TESTS = {
    "1": {"file": "benchmark_results.json", "name": "Test 1", "about": "45 hard questions"},
    "2": {"file": "benchmark_results_200.json", "name": "Test 2", "about": "200 brand-new hard questions"},
    "3": {"file": "benchmark_results_100.json", "name": "Test 3", "about": "100 long, story-style questions"},
}
ORDER = ["sarvam", "groq", "cloudflare", "sarvam_plain"]
RAG = ["sarvam", "groq", "cloudflare"]
GROUPS = {
    "fact": "Facts from the PDFs", "multi_case": "Answers with several cases",
    "language": "Hindi / Kannada / Nepali / typos", "reply_language": "Reply in the chosen language",
    "false_premise": "Wrong assumption corrected", "not_in_docs": "On-topic, not in the PDFs",
    "off_topic": "Off-topic & tricks",
}
LANGS = {"en": "English", "hi": "Hindi", "kn": "Kannada", "ne": "Nepali"}
DOC_ALIAS = {"UPIS": "FINAL_UPISOGs"}
DOC_SHORT = {"11of1959": "Karnataka Co-op Act", "247816": "Multi-State Act 2023", "405MDD58": "RBI KCC 2026",
             "UPIS": "UPIS insurance", "FINAL_UPISOGs": "UPIS insurance", "Initiatives": "Ministry initiatives",
             "Model Byelaws": "PACS bye-laws", "New Schemes": "Schemes booklet", "PMKSY": "PMKSY irrigation",
             "RWBCIS": "Weather insurance (RWBCIS)", "PM-KISAN": "PM-KISAN", "doc1": "PMFBY crop insurance",
             "none": "No PDF"}
B = 2000

_cache = {}
_lock = threading.Lock()


def _doc_name(doc):
    if not doc:
        return "No PDF (general / off-topic)"
    try:
        from backend.pipeline.common import OFFICIAL_NAMES
        return OFFICIAL_NAMES.get(DOC_ALIAS.get(doc, doc), doc)
    except Exception:
        return doc


def _mean(v):
    return sum(v) / len(v) if v else None


def _boot(values, seed):
    """95% bootstrap range of the mean (in %). NumPy does all 2,000 re-draws at once (fast C code)."""
    if len(values) < 2:
        return None
    arr = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(int(hashlib.md5(str(seed).encode()).hexdigest()[:8], 16))
    means = arr[rng.integers(0, len(arr), size=(B, len(arr)))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return [round(100 * float(lo), 1), round(100 * float(hi), 1)]


def _sign_p(better, worse):
    """Exact two-sided sign test p-value."""
    n = better + worse
    if n == 0:
        return 1.0
    k = min(better, worse)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def _cohen_h(p1, p2):
    return 2 * math.asin(math.sqrt(max(0, min(1, p1)))) - 2 * math.asin(math.sqrt(max(0, min(1, p2))))


def _h_words(h):
    a = abs(h)
    return "very large" if a >= 1.2 else "large" if a >= 0.8 else "medium" if a >= 0.5 else "small" if a >= 0.2 else "tiny"


def _kappa_words(k):
    return ("almost perfect" if k > 0.8 else "substantial" if k > 0.6 else "moderate" if k > 0.4
            else "fair" if k > 0.2 else "slight")


def _answer_score(row, c):
    v = [GRADE[g[c]["grade"]] for g in (row.get("grades") or {}).values() if c in g and g[c].get("grade") in GRADE]
    return _mean(v)


def _pct(x):
    return None if x is None else round(100 * x, 1)


def _p95(v):
    if not v:
        return None
    v = sorted(v)
    return round(v[min(len(v) - 1, int(round(0.95 * (len(v) - 1))))], 2)


def compute(test):
    meta = TESTS[test]
    path = os.path.join(ROOT, meta["file"])
    if not os.path.exists(path):
        return None
    mtime = os.path.getmtime(path)
    with _lock:
        hit = _cache.get(test)
        if hit and hit[0] == mtime:
            return hit[1]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out = _compute(test, data)
    with _lock:
        _cache[test] = (mtime, out)
    return out


def _compute(test, data):
    rows = data.get("questions") or []
    summ = data.get("summary") or {}
    names = (summ.get("judges") or {}).get("names") or {}
    C = summ.get("contestants") or {}
    present = [c for c in ORDER if c in C]
    pipes = sorted({(r.get("runs") or {}).get("sarvam", {}).get("pipeline", "v1") for r in rows if (r.get("runs") or {}).get("sarvam")})
    sc = {c: {r["id"]: _answer_score(r, c) for r in rows} for c in present}

    contestants = {}
    for i, c in enumerate(present):
        vals = [v for v in sc[c].values() if v is not None]
        grades = {"correct": 0, "partial": 0, "wrong": 0}
        for v in vals:
            grades["correct" if v >= 0.999 else "wrong" if v <= 0.001 else "partial"] += 1
        by_group, by_lang, by_doc = {}, {}, {}
        for r in rows:
            v = sc[c].get(r["id"])
            if v is None:
                continue
            by_group.setdefault(r["group"], []).append(v)
            by_lang.setdefault(r["language"], []).append(v)
            by_doc.setdefault(r.get("doc") or "none", []).append(v)
        times = [((r.get("runs") or {}).get(c) or {}).get("time_s") for r in rows]
        times = [t for t in times if isinstance(t, (int, float))]
        info = C.get(c) or {}
        judges = {}
        for j in names:
            jv = [GRADE[(r.get("grades") or {}).get(j, {}).get(c, {}).get("grade")] for r in rows
                  if (r.get("grades") or {}).get(j, {}).get(c, {}).get("grade") in GRADE]
            if jv:
                judges[j] = _pct(_mean(jv))
        group_scores = {g: _pct(_mean(v)) for g, v in by_group.items()}
        best = max(group_scores, key=group_scores.get) if group_scores else None
        worst = min(group_scores, key=group_scores.get) if group_scores else None
        contestants[c] = {
            "name": info.get("name", c), "short": info.get("short", c), "judged_by": info.get("judged_by", []),
            "n": len(vals), "score": _pct(_mean(vals)), "range": _boot(vals, f"{test}-{c}"),
            "grades": grades,
            "by_group": {g: {"score": _pct(_mean(v)), "n": len(v), "range": _boot(v, f"{test}-{c}-{g}")} for g, v in by_group.items()},
            "by_language": {l: {"score": _pct(_mean(v)), "n": len(v)} for l, v in by_lang.items()},
            "by_doc": {d: {"score": _pct(_mean(v)), "n": len(v)} for d, v in by_doc.items()},
            "category_spread": round(statistics.pstdev([x for x in group_scores.values()]), 1) if len(group_scores) > 1 else None,
            "best_area": best, "worst_area": worst,
            "by_judge": judges,
            "time_median": round(statistics.median(times), 2) if times else None, "time_p95": _p95(times),
            "auto": info.get("auto") or {},
        }

    def paired(a, b):
        ids = [i for i in sc.get(a, {}) if sc[a].get(i) is not None and sc.get(b, {}).get(i) is not None]
        if not ids:
            return None
        diff = [sc[a][i] - sc[b][i] for i in ids]
        better = sum(1 for d in diff if d > 0)
        worse = sum(1 for d in diff if d < 0)
        pa, pb = _mean([sc[a][i] for i in ids]), _mean([sc[b][i] for i in ids])
        h = _cohen_h(pa, pb)
        return {"a": a, "b": b, "n": len(ids), "gain": _pct(_mean(diff)), "range": _boot(diff, f"{test}-{a}-{b}"),
                "better": better, "same": len(ids) - better - worse, "worse": worse,
                "p_value": _sign_p(better, worse), "cohen_h": round(h, 2), "effect": _h_words(h)}

    comparisons = [p for p in (paired("sarvam", "sarvam_plain"), paired("sarvam", "groq"), paired("sarvam", "cloudflare"),
                               paired("groq", "cloudflare")) if p]

    # judge agreement + Cohen's kappa (3 grade levels)
    pairs = []
    for r in rows:
        g = r.get("grades") or {}
        js = list(g)
        for x in range(len(js)):
            for y in range(x + 1, len(js)):
                for c in g[js[x]]:
                    if c in g[js[y]] and g[js[x]][c].get("grade") in GRADE and g[js[y]][c].get("grade") in GRADE:
                        pairs.append((g[js[x]][c]["grade"], g[js[y]][c]["grade"]))
    kappa = agree = None
    if pairs:
        n = len(pairs)
        po = sum(a == b for a, b in pairs) / n
        pe = sum((sum(a == k for a, _ in pairs) / n) * (sum(b == k for _, b in pairs) / n) for k in GRADE)
        kappa = round((po - pe) / (1 - pe), 2) if pe < 1 else 1.0
        agree = _pct(po)

    # calibration of the live app's green "Verified" badge
    ver = [sc["sarvam"][r["id"]] for r in rows if "sarvam" in sc and sc["sarvam"].get(r["id"]) is not None
           and ((r.get("runs") or {}).get("sarvam") or {}).get("trust_level") == "verified"]
    calibration = {"verified_answers": len(ver), "fully_correct": _pct(_mean([1.0 if v >= 0.999 else 0.0 for v in ver])),
                   "score": _pct(_mean(ver))} if ver else None

    # hardest questions: every document-search AI got 0
    rag = [c for c in RAG if c in sc]
    hardest = [r["id"] for r in rows if rag and all(sc[c].get(r["id"]) == 0.0 for c in rag)]

    search = (C.get("sarvam") or {}).get("search") or {}
    questions = []
    for r in rows:
        runs = {}
        for c in present:
            run = (r.get("runs") or {}).get(c)
            if not run:
                continue
            runs[c] = {
                "answer": run.get("answer") or ("(no answer: " + str(run.get("error"))[:80] + ")" if run.get("error") else ""),
                "score": sc[c].get(r["id"]),
                "grades": {j: {"grade": g[c].get("grade"), "reason": g[c].get("reason", "")}
                           for j, g in (r.get("grades") or {}).items() if c in g},
                "time": run.get("time_s"), "trust": run.get("trust_level"),
                "fact_ok": (run.get("auto") or {}).get("fact_ok"), "lang_ok": (run.get("auto") or {}).get("lang_ok"),
                "source": run.get("source"), "page": run.get("source_page"),
            }
        questions.append({"id": r["id"], "group": r["group"], "language": r["language"], "q": r["q"],
                          "doc": r.get("doc") or "none", "pages": r.get("pages") or [], "reference": r.get("reference", ""),
                          "runs": runs, "all_wrong": r["id"] in hardest})
    return {
        "test": test, "name": TESTS[test]["name"], "about": TESTS[test]["about"],
        "generated_at": summ.get("generated_at"), "questions_total": len(rows),
        "pipeline": " + ".join(pipes) or "v1",
        "judge_names": names, "contestants": contestants, "order": present, "comparisons": comparisons,
        "judges": {"agreement": agree, "kappa": kappa, "kappa_words": _kappa_words(kappa) if kappa is not None else None,
                   "pairs": len(pairs)},
        "calibration": calibration, "hardest": hardest, "search": search,
        "groups": GROUPS, "languages": LANGS,
        "docs": {(d or "none"): _doc_name(d) for d in {r.get("doc") or "" for r in rows}},
        "docs_short": {(d or "none"): DOC_SHORT.get(d or "none", d) for d in {r.get("doc") or "" for r in rows}},
        "questions": questions,
    }


def progress():
    """Sarvam with / without our PDFs across Test 1 -> 2 -> 3 (for the progress chart)."""
    out = []
    for t in ("1", "2", "3"):
        s = compute(t)
        if not s:
            continue
        c = s["contestants"]
        out.append({"test": t, "name": s["name"], "pipeline": s["pipeline"], "n": s["questions_total"],
                    "with": {"score": (c.get("sarvam") or {}).get("score"), "range": (c.get("sarvam") or {}).get("range")},
                    "without": {"score": (c.get("sarvam_plain") or {}).get("score"),
                                "range": (c.get("sarvam_plain") or {}).get("range")}})
    return out


def warm_up_in_background():
    """Compute every test's statistics right after startup, so the Explorer opens instantly."""
    def _run():
        for t in TESTS:
            try:
                compute(t)
            except Exception as e:
                print(f"⚠️ Explorer statistics for Test {t} could not be prepared: {e}", flush=True)
    threading.Thread(target=_run, daemon=True, name="explorer-stats").start()
