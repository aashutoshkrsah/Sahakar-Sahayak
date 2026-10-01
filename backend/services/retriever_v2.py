"""
Sahakar Sahayak -- document search, version 2 (the default; see backend/services/pipeline.py).

Same three matching methods as version 1 (exact words / word parts / meaning), but on the
GOLD pieces made by the Medallion pipeline (backend/pipeline/): whole sections cut by an AI
cutter, each with a full label such as
  "Karnataka Co-operative Societies Act, 1959 › ... › Section 28 – Special general meeting › Page 64".
Then a RE-RANKER (Cloudflare bge-reranker-base, a "senior librarian") re-orders the best 20
candidates and the best 5 go to the answer writer.

The gold pieces and their meaning-numbers are ready-made files in backend/data/medallion/
(gold.json, gold_embeddings.npy), so nothing is rebuilt when Render restarts or redeploys.
If anything here fails, backend/services/pipeline.py falls back to version 1 automatically.
"""

import json
import os
import time

import numpy as np

from backend.services.reqlog import log
from backend.services import retriever as v1          # shared helpers: word search, spelling, Cloudflare

BASE_DIR = v1.BASE_DIR
MED_DIR = os.path.join(BASE_DIR, "backend", "data", "medallion")
GOLD_PATH = os.path.join(MED_DIR, "gold.json")
GOLD_EMB_PATH = os.path.join(MED_DIR, "gold_embeddings.npy")
GOLD_EMB_META = os.path.join(MED_DIR, "gold_embeddings_meta.json")
# Backup meaning-numbers made by Gemini Embedding (used only when Cloudflare can't make the question's numbers)
GOLD_GEM_PATH = os.path.join(MED_DIR, "gold_embeddings_gemini.npy")
GOLD_GEM_META = os.path.join(MED_DIR, "gold_embeddings_gemini_meta.json")
GOLD_GEM_PARTIAL = os.path.join(MED_DIR, "gold_embeddings_gemini_partial.npy")

TOP_K = 5                 # gold pieces are whole sections (about 1,100 letters), so 5 carry more than v1's 6
CANDIDATES = 20           # how many the re-ranker looks at
RERANK_MODEL = "@cf/baai/bge-reranker-base"
RERANK_TIMEOUT = 4
RERANK_WEIGHT = 0.5       # final order = half re-ranker, half the usual three-signal score

pieces = []               # gold pieces: document, page, pages, label, body, text (= "[label]\n" + body)
_word_index = None
_part_index = None
_vectors = None
_gvectors = None          # Gemini copy (backup)
_gmap = None              # [a, b]: Gemini similarity -> Cloudflare scale (measured when the copy was made)
_ready = False


def _signature():
    try:
        return os.path.getsize(GOLD_PATH)
    except OSError:
        return None


def load():
    """Load the gold pieces + their saved meaning-numbers. Raises if the gold file is missing."""
    global pieces, _word_index, _part_index, _vectors, _gvectors, _gmap, _ready
    with open(GOLD_PATH, encoding="utf-8") as f:
        pieces = json.load(f)["pieces"]
    _word_index = v1._BM25([v1.tokenize(p["text"]) for p in pieces])
    _part_index = v1._BM25([v1.part_tokens(p["text"]) for p in pieces])
    _vectors = None
    wanted = {"size": _signature(), "model": v1.CF_MODEL, "count": len(pieces)}
    try:
        with open(GOLD_EMB_META, encoding="utf-8") as f:
            meta = json.load(f)
        if meta == wanted and os.path.exists(GOLD_EMB_PATH):
            mat = np.load(GOLD_EMB_PATH).astype(np.float32)
            if mat.shape[0] == len(pieces):
                _vectors = mat
    except Exception:
        pass
    if _vectors is None:
        print("⚠️ v2: gold meaning-numbers file missing or out of date -- run: python3 -m backend.pipeline.embed "
              "(word search still works)")
    _gvectors, _gmap = None, None
    try:
        from backend.services import gemini
        with open(GOLD_GEM_META, encoding="utf-8") as f:
            gm = json.load(f)
        if gm.get("size") == _signature() and gm.get("model") == f"{gemini.EMBED_MODEL}:{gemini.EMBED_DIM}" \
                and gm.get("count") == len(pieces) and os.path.exists(GOLD_GEM_PATH):
            mat = np.load(GOLD_GEM_PATH).astype(np.float32)
            if mat.shape[0] == len(pieces):
                _gvectors, _gmap = mat, gm.get("map")
    except Exception:
        pass
    _ready = True
    print(f"✅ v2 search ready ({len(pieces)} gold pieces, meaning search {'ON' if _vectors is not None else 'OFF'}, "
          f"Gemini backup {'ON' if _gvectors is not None else 'OFF'}).")


def _gemini_transform(sims):
    """Put Gemini similarities on Cloudflare's scale, so the usual thresholds still work."""
    if _gmap:
        a, b = _gmap
        return a * sims + b
    p50, top = float(np.percentile(sims, 50)), float(sims.max())
    return v1.MEANING_LOW + (sims - p50) / max(top - p50, 1e-6) * (v1.MEANING_HIGH - v1.MEANING_LOW)


def meaning_options():
    return [("cf", _vectors, None), ("gemini", _gvectors, _gemini_transform)]


def build_embeddings():
    """One-time: ask Cloudflare for the meaning-numbers of every gold piece and SAVE them (run in Codespaces)."""
    if not pieces:
        load()
    if not v1._cf_enabled():
        raise SystemExit("CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN missing in .env")
    global _vectors
    rows = []
    for i in range(0, len(pieces), v1.EMBED_BATCH):
        batch = [p["text"] for p in pieces[i:i + v1.EMBED_BATCH]]
        for attempt in range(3):
            try:
                rows.append(v1._embed(batch, timeout=60))
                break
            except Exception as e:
                if attempt == 2:
                    raise
                print(f"   retrying batch {i // v1.EMBED_BATCH + 1}: {e}")
                time.sleep(3)
        print(f"   {min(i + v1.EMBED_BATCH, len(pieces))} / {len(pieces)} pieces")
    mat = np.vstack(rows)
    np.save(GOLD_EMB_PATH, mat.astype(np.float16))
    with open(GOLD_EMB_META, "w", encoding="utf-8") as f:
        json.dump({"size": _signature(), "model": v1.CF_MODEL, "count": len(pieces)}, f)
    _vectors = mat.astype(np.float32)
    print(f"✅ saved {GOLD_EMB_PATH} ({mat.shape[0]} x {mat.shape[1]})")


def _save_partial(rows):
    if rows:
        np.save(GOLD_GEM_PARTIAL, np.vstack(rows).astype(np.float16))


def build_gemini_embeddings(batch=50):
    """One-time: the Gemini BACKUP copy of the gold pieces' meaning-numbers. Resumable: progress is saved after
    every batch, so if Gemini's free daily limit stops it, run the same command again tomorrow.
    Returns True when complete."""
    from backend.services import gemini
    global _gvectors
    if not pieces:
        load()
    if not gemini.configured():
        print("ℹ️ GEMINI_API_KEY missing -- Gemini backup copy skipped")
        return False
    done = np.load(GOLD_GEM_PARTIAL).astype(np.float32) if os.path.exists(GOLD_GEM_PARTIAL) else np.zeros((0, gemini.EMBED_DIM), np.float32)
    if done.shape[1] != gemini.EMBED_DIM:
        done = np.zeros((0, gemini.EMBED_DIM), np.float32)
    rows = [done] if len(done) else []
    i = len(done)
    while i < len(pieces):
        texts = [p["text"] for p in pieces[i:i + batch]]
        try:
            rows.append(gemini.embed(texts, task="RETRIEVAL_DOCUMENT", timeout=90))
        except Exception as e:
            if getattr(e, "status", None) == 429:
                time.sleep(30)
                try:
                    rows.append(gemini.embed(texts, task="RETRIEVAL_DOCUMENT", timeout=90))
                except Exception as e2:
                    _save_partial(rows)
                    print(f"⏸ Gemini stopped at {i} / {len(pieces)} pieces ({str(e2)[:160]}). Saved; run the same "
                          f"command again later (tomorrow if the daily limit is used up).")
                    return False
            else:
                _save_partial(rows)
                print(f"⏸ Gemini failed at {i} / {len(pieces)} pieces ({str(e)[:160]}). Saved; run again later.")
                return False
        i += len(texts)
        np.save(GOLD_GEM_PARTIAL, np.vstack(rows).astype(np.float16))
        print(f"   Gemini backup: {i} / {len(pieces)} pieces")
    mat = np.vstack(rows)
    np.save(GOLD_GEM_PATH, mat.astype(np.float16))
    old_map = None
    try:
        old_map = json.load(open(GOLD_GEM_META, encoding="utf-8")).get("map")
    except Exception:
        pass
    with open(GOLD_GEM_META, "w", encoding="utf-8") as f:
        json.dump({"size": _signature(), "model": f"{gemini.EMBED_MODEL}:{gemini.EMBED_DIM}", "count": len(pieces),
                   "map": old_map}, f)
    if os.path.exists(GOLD_GEM_PARTIAL):
        os.remove(GOLD_GEM_PARTIAL)
    _gvectors = mat.astype(np.float32)
    print(f"✅ saved {GOLD_GEM_PATH} ({mat.shape[0]} x {mat.shape[1]})")
    return True


def calibrate_gemini(questions):
    """Measure how Gemini's similarities line up with Cloudflare's on real questions and save the mapping
    (so the backup uses the same thresholds). Uses saved/new question numbers from both engines."""
    from backend.services import meaning, gemini
    global _gmap
    if _vectors is None or _gvectors is None:
        return None
    cf_all, g_all = [], []
    for q in questions:
        vc, _ = meaning.query_vector(q, "cf")
        vg, _ = meaning.query_vector(q, "gemini")
        if vc is None or vg is None:
            continue
        cf_all.append(_vectors @ vc)
        g_all.append(_gvectors @ vg)
    if len(cf_all) < 10:
        print(f"ℹ️ Gemini calibration skipped (only {len(cf_all)} questions had both kinds of numbers)")
        return None
    c, g = np.concatenate(cf_all), np.concatenate(g_all)
    c50, c99 = np.percentile(c, 50), np.percentile(c, 99.5)
    g50, g99 = np.percentile(g, 50), np.percentile(g, 99.5)
    a = float((c99 - c50) / max(g99 - g50, 1e-6))
    b = float(c50 - a * g50)
    _gmap = [round(a, 5), round(b, 5)]
    meta = json.load(open(GOLD_GEM_META, encoding="utf-8"))
    meta["map"] = _gmap
    json.dump(meta, open(GOLD_GEM_META, "w", encoding="utf-8"))
    print(f"✅ Gemini backup calibrated on {len(cf_all)} questions: cloudflare ≈ {a:.3f} × gemini + {b:.3f}")
    return _gmap


def _rerank_live(query, texts):
    """Cloudflare re-ranker (account 1, then account 2): relevance of each text to the question (0..1)."""
    from backend.services import cloudflare
    try:
        res = cloudflare.run(RERANK_MODEL, {"query": query, "contexts": [{"text": t[:2000]} for t in texts],
                                            "top_k": len(texts)}, timeout=RERANK_TIMEOUT, what="librarian") or {}
        items = res.get("response", res) if isinstance(res, dict) else res
        scores = [None] * len(texts)
        for it in items or []:
            idx = it.get("id", it.get("index"))
            if isinstance(idx, int) and 0 <= idx < len(texts):
                sc = float(it.get("score", 0.0))
                scores[idx] = float(1 / (1 + np.exp(-sc))) if (sc < 0 or sc > 1) else sc     # logits -> 0..1
        if any(x is None for x in scores):
            raise RuntimeError("re-ranker returned an incomplete list")
        return scores
    except Exception as e:
        log("SEARCH", f"⚠️ re-ranker skipped: {str(e)[:200]}")
        return None


def _rerank(query, texts, stats=None):
    """Senior librarian scores: saved ones first (Re-check needs no call), else live (capped per day)."""
    if not texts:
        return None
    from backend.services import meaning
    scores, src = meaning.rerank(query, texts, _rerank_live)
    if stats is not None:
        stats["librarian_from"] = src
    if scores is None:
        log("SEARCH", f"🔀 HANDOVER [librarian] senior librarian skipped ({src}) → normal search order takes charge")
    return scores


def search(query: str, top_k: int = TOP_K, boost_terms: str = ""):
    """Same result format as retriever.search (so the rest of the app works unchanged),
    plus each piece's "label"; stats get "pipeline": "v2" and "reranked"."""
    if not _ready:
        load()
    started = time.perf_counter()
    stats = {"pieces_searched": len(pieces), "pdfs_searched": len({p["document"] for p in pieces}),
             "candidates_compared": 0, "meaning_available": False, "search_time_ms": 0.0,
             "pipeline": "v2", "reranked": False}
    query_words = list(dict.fromkeys(v1.tokenize(query)))
    if not query_words or not pieces:
        return [], stats
    query_parts = set(v1.part_tokens(query))
    boost_words = [w for w in dict.fromkeys(v1.tokenize(boost_terms or "")) if w not in query_words]

    word_scores = v1._normalise(_word_index.scores(query_words))
    part_scores = v1._normalise(_part_index.scores(list(query_parts)))
    boost_scores = v1._normalise(_word_index.scores(boost_words)) if boost_words else {}
    word_rank = {i: v1.WORD_WEIGHT * word_scores.get(i, 0.0) + v1.PART_WEIGHT * part_scores.get(i, 0.0)
                 + v1.BOOST_WEIGHT * boost_scores.get(i, 0.0)
                 for i in set(word_scores) | set(part_scores) | set(boost_scores)}

    from backend.services import meaning
    sims, engine, src = meaning.similarities(query, meaning_options())
    if sims is None:
        log("SEARCH", f"⚠️ meaning search failed, using word search only: {src}")
    else:
        stats["meaning_engine"], stats["meaning_from"] = engine, src
        if engine != "cf":
            log("SEARCH", f"🛟 meaning search used the {engine} backup")
    meaning_on = sims is not None
    stats["meaning_available"] = meaning_on

    shortlist = set(sorted(word_rank, key=word_rank.get, reverse=True)[:CANDIDATES * 2])
    if meaning_on:
        shortlist |= set(int(i) for i in np.argsort(-sims)[:CANDIDATES * 2])
    routed = v1._routed_documents(query)
    stats["scheme_routing"] = routed
    if routed:
        in_routed = [i for i in range(len(pieces)) if any(d.lower() in pieces[i]["document"].lower() for d in routed)]
        shortlist |= set(sorted((i for i in in_routed if i in word_rank), key=word_rank.get, reverse=True)[:8])
        if meaning_on:
            shortlist |= set(sorted(in_routed, key=lambda i: -float(sims[i]))[:8])
    stats["candidates_compared"] = len(shortlist)

    scored = []
    for i in shortlist:
        text = pieces[i]["text"]
        kw = v1._exact_keyword_score(query_words, text)
        sp = v1._spelling_score(query_parts, text)
        if meaning_on:
            raw = float(sims[i]); ms = v1._scale_meaning(raw)
            final = v1.FINAL_W_KEYWORD * kw + v1.FINAL_W_SPELLING * sp + v1.FINAL_W_MEANING * ms
            keep = kw >= v1.INCLUDE_KEYWORD or ms >= v1.INCLUDE_MEANING
        else:
            raw, ms = None, 0.0
            final = 0.7 * kw + 0.3 * sp
            keep = kw >= v1.INCLUDE_KEYWORD
        in_route = bool(routed) and any(d.lower() in pieces[i]["document"].lower() for d in routed)
        if keep or (in_route and (kw >= v1.ROUTE_MIN_MATCH or ms >= v1.ROUTE_MIN_MATCH)):
            scored.append([final + (v1.ROUTE_BONUS if in_route else 0.0), i, kw, sp, raw, ms, final, keep])
    scored.sort(key=lambda x: -x[0])
    cands = scored[:CANDIDATES]

    # Re-ranker (senior librarian): reads the question with each candidate and re-orders them
    stats["librarian_needed"] = len(cands) > 1          # with 0-1 candidates there is nothing to re-order
    rr = _rerank(query, [pieces[c[1]]["text"] for c in cands], stats) if len(cands) > 1 else None
    if rr is not None:
        stats["reranked"] = True
        for c, s in zip(cands, rr):
            c.append(s)
            c[0] = (1 - RERANK_WEIGHT) * c[0] + RERANK_WEIGHT * s
        cands.sort(key=lambda x: -x[0])
    picked = [c for c in cands if c[7]][:top_k]
    if routed and not any(any(d.lower() in pieces[c[1]]["document"].lower() for d in routed) for c in picked):
        extra = [c for c in cands if not c[7] and any(d.lower() in pieces[c[1]]["document"].lower() for d in routed)]
        if extra:
            picked = picked[:max(0, top_k - 1)] + extra[:1]
            log("SEARCH", f"📌 added a passage from the named scheme's PDF ({pieces[extra[0][1]]['document']})")

    results = []
    for c in picked:
        _key, i, kw, sp, raw, ms, final = c[:7]
        d = dict(pieces[i])
        d.update({"keyword_score": round(kw, 4), "spelling_score": round(sp, 4),
                  "meaning_score": round(raw, 4) if raw is not None else None, "meaning_scaled": round(ms, 4),
                  "final_score": round(final, 4), "similarity_score": round(final, 4),
                  "rerank_score": round(c[8], 4) if len(c) > 8 else None})
        results.append(d)
    stats["search_time_ms"] = round((time.perf_counter() - started) * 1000, 2)
    if results:
        b = results[0]
        log("SEARCH", f"🔎 v2 best {b['final_score'] * 100:.2f}% | re-ranker {'on' if stats['reranked'] else 'off'} | "
                      f"{b['label'][:120]} | {len(results)} pieces | {stats['search_time_ms']} ms")
    else:
        log("SEARCH", f"🔎 v2: no piece matched well enough -- general knowledge ({stats['search_time_ms']} ms)")
    return results, stats
