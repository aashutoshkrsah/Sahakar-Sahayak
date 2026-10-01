import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel

from backend.models.schemas import QueryRequest, QueryResponse

from backend.services.nlp_service import (
    preprocess_query,
    detect_intent,
    validate_language
)
from backend.services.rag_service import get_answer, normalize_query, lexicon_terms
from backend.services.reqlog import new_request_id, log
from backend.services import pipeline          # PIPELINE=v1 (today) or v2 (gold pieces + new rules), with auto fallback
from backend.services import answer_cache
from backend.services.help_contacts import helplines_for
from backend.services.small_talk import small_talk
from backend.services import analytics
from backend.services import live_judge
from backend.services import mandi_prices

# Friendly names for the Insights page (keys = file-name parts used by scheme routing)
TOPIC_NAMES = {
    "PM-KISAN": "PM-KISAN", "doc1": "PMFBY crop insurance", "RWBCIS": "Weather crop insurance",
    "UPIS": "Package insurance (UPIS)", "405MDD58": "Kisan Credit Card", "PMKSY": "PMKSY irrigation",
    "11of1959": "Karnataka Co-op Act", "247816": "Multi-State Co-op Act", "Model Byelaws": "PACS bye-laws",
    "Initiatives": "PACS initiatives",
}


router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    started = time.perf_counter()
    rid = new_request_id()
    try:
        # 1. Validate target UI output language
        language = validate_language(request.language)

        # 2. Clean query
        cleaned_query = preprocess_query(request.query)
        log("QUERY", f"📩 new question | language={language} | {cleaned_query[:200]!r}")

        # 2b. Exact repeat of a question already answered well? Reuse it: no AI calls at all (v2 only)
        cache_key = answer_cache.key(cleaned_query, language)
        hit = answer_cache.get(cache_key)
        if hit:
            result, check, from_rid = hit
            total_ms = round((time.perf_counter() - started) * 1000, 2)
            if isinstance(result.get("search_report"), dict):
                result["search_report"].update({"total_time_ms": total_ms, "request_id": rid, "cached_from": from_rid})
            if check:
                live_judge._results[rid] = check          # the website's AI check shows the saved grade, no new AI call
            analytics.log_query(
                question=cleaned_query, english_question=(result.get("search_report") or {}).get("search_query"),
                language=language, intent=result.get("intent"), trust_level=result.get("trust_level"),
                answer_source=result.get("answer_source"), top_document=(result.get("sources") or [{}])[0].get("document"),
                confidence=result.get("confidence"), response_ms=total_ms, topics=[], answered_by=result.get("answered_by"),
                report=result.get("search_report"), top_page=(result.get("sources") or [{}])[0].get("page"))
            log("CACHE", f"♻️ exact repeat of REQ {from_rid} -- saved answer reused, no AI calls ({total_ms / 1000:.2f}s)")
            log("SUMMARY", f"═══ SUMMARY ═══ cache=HIT (reused REQ {from_rid}) | answered={result.get('answered_by')} | "
                           f"no AI calls | {total_ms / 1000:.2f}s")
            return JSONResponse(content=jsonable_encoder(result), media_type="application/json; charset=utf-8")

        # 2c. Small talk ("hi", "what is your name?", "thank you"): a friendly built-in reply, no search, no AI
        small = small_talk(cleaned_query, language)
        if small:
            total_ms = round((time.perf_counter() - started) * 1000, 2)
            small["search_report"].update({"total_time_ms": total_ms, "request_id": rid, "search_query": cleaned_query})
            analytics.log_query(question=cleaned_query, english_question=cleaned_query, language=language,
                                intent="small_talk", trust_level="general", answer_source="general", top_document=None,
                                confidence=0.0, response_ms=total_ms, topics=[], answered_by="built_in",
                                report=small["search_report"], top_page=None)
            log("SUMMARY", f"═══ SUMMARY ═══ small talk → built-in friendly reply | no search, no AI | {total_ms / 1000:.2f}s")
            return JSONResponse(content=jsonable_encoder(small), media_type="application/json; charset=utf-8")

        # 3. Translate code-mixed input into clean English (Sarvam -> Groq -> Cloudflare -> Gemini)
        english_query, translated_by = normalize_query(cleaned_query)

        # 4. Detect intent
        intent = detect_intent(english_query, language)

        # 5. Hybrid search of the PDFs: keyword (BM25) + spelling + meaning (Cloudflare).
        #    Official scheme names only help find candidates; they don't change the scores.
        boost = lexicon_terms(f"{cleaned_query} {english_query}")
        retrieved_docs, search_stats, pipeline_used = pipeline.search(english_query, boost_terms=boost)
        routed = search_stats.get("scheme_routing") or []
        log("QUERY", f"📚 intent={intent} | {len(retrieved_docs)} pieces found | routed to {routed or 'none'}")

        # 5b. Mandi prices -- ONLY for price questions; every other question gets None and runs as before
        try:
            prices = mandi_prices.lookup(cleaned_query, english_query)
        except Exception as e:
            log("PRICES", f"⚠️ price lookup skipped: {e}")
            prices = None
        price_context = mandi_prices.as_context(prices)

        # 6. Generate answer in user's UI language (Sarvam -> Groq -> Cloudflare -> Gemini -> search-only).
        #    If the v2 answer step crashes, THIS question is redone with v1 (search + answer) automatically.
        answer_args = dict(query=english_query, language=language, intent=intent, original_query=cleaned_query,
                           extra_context=price_context)
        if pipeline_used == "v2":
            try:
                result = get_answer(retrieved_docs=retrieved_docs, search_stats=search_stats, pipeline="v2", **answer_args)
                pipeline.report_success()
            except Exception as e:
                pipeline.report_failure("answer step", e)
                retrieved_docs, search_stats = pipeline.v1.search(english_query, boost_terms=boost)
                search_stats["pipeline"], pipeline_used = "v1", "v1"
                routed = search_stats.get("scheme_routing") or []
                result = get_answer(retrieved_docs=retrieved_docs, search_stats=search_stats, **answer_args)
        else:
            result = get_answer(retrieved_docs=retrieved_docs, search_stats=search_stats, **answer_args)
        result["prices"] = prices

        result["language"] = language
        result["intent"] = intent

        # 7. "Talk to a person": official helplines under answers that aren't fully verified
        result["helplines"] = helplines_for(
            f"{cleaned_query} {english_query}", result.get("trust_level"), intent, routed)

        total_ms = round((time.perf_counter() - started) * 1000, 2)
        if isinstance(result.get("search_report"), dict):
            result["search_report"].update({
                "total_time_ms": total_ms,
                "search_query": english_query,
                "request_id": rid,
                "translated_by": translated_by,
                "answered_by": result.get("answered_by"),
                "pipeline": pipeline_used,
            })

        # 8. Log for the admin Insights page (never breaks the answer)
        analytics.log_query(
            question=cleaned_query, english_question=english_query, language=language, intent=intent,
            trust_level=result.get("trust_level"), answer_source=result.get("answer_source"),
            top_document=(result.get("sources") or [{}])[0].get("document"),
            confidence=result.get("confidence"), response_ms=total_ms,
            topics=[TOPIC_NAMES.get(d, d) for d in routed] + (["Mandi prices"] if prices else []),
            answered_by=result.get("answered_by"),
            report=result.get("search_report"),
            top_page=(result.get("sources") or [{}])[0].get("page"),
        )
        # 9. Keep what the AI judges need; the website asks for the check right after showing the answer
        live_judge.remember(rid, cleaned_query, english_query, result.get("answer"), language,
                            result.get("trust_level"), result.get("answered_by"),
                            ([price_context] if price_context else [])
                            + ([d.get("text", "") for d in retrieved_docs] if result.get("answer_source") == "documents" else []))
        answer_cache.put(cache_key, rid, result)
        log("QUERY", f"🏁 finished in {total_ms / 1000:.2f}s | translated by {translated_by or 'none'} | "
                     f"answered by {result.get('answered_by')} | trust={result.get('trust_level')} | "
                     f"helplines={len(result['helplines'])}")
        log("SUMMARY", _summary(pipeline_used, search_stats, translated_by, result, total_ms, cache="miss"))

        return JSONResponse(
            content=jsonable_encoder(result),
            media_type="application/json; charset=utf-8"
        )

    except Exception as e:
        log("QUERY", f"💥 crashed after {time.perf_counter() - started:.2f}s: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query (request {rid}): {str(e)}"
        )


def _summary(pipeline_used, stats, translated_by, result, total_ms, cache):
    """One line at the end of every question: who did what (search the Render logs for 'SUMMARY')."""
    stats = stats or {}
    if stats.get("meaning_available"):
        eng = {"cf": "cloudflare", "gemini": "GEMINI BACKUP"}.get(stats.get("meaning_engine", "cf"), stats.get("meaning_engine"))
        meaning = f"{eng} ({stats.get('meaning_from', 'live')})"
    else:
        meaning = "OFF (word search only)"
    if pipeline_used == "v2":
        lib = ("on" + f" ({stats.get('librarian_from')})" if stats.get("reranked") else
               "not needed (0-1 candidates)" if not stats.get("librarian_needed") else
               f"SKIPPED ({stats.get('librarian_from') or 'failed'})")
    else:
        lib = "— (v1 has no librarian)"
    return (f"═══ SUMMARY ═══ pipeline={pipeline_used} | meaning={meaning} | librarian={lib} | "
            f"translated={translated_by or 'none'} | answered={result.get('answered_by')} | "
            f"trust={result.get('trust_level')} | cache={cache} | {total_ms / 1000:.2f}s")


@router.get("/health/details", include_in_schema=False)
def health_details():
    """Live status of every moving part (which pipeline, which accounts are used up, which AIs have keys)."""
    from backend.services import status
    return JSONResponse(content=jsonable_encoder(status.details()))


class JudgeRequest(BaseModel):
    request_id: str


@router.post("/judge")
def judge_answer(request: JudgeRequest):
    """Live AI check of one answer: graded by the AIs that did NOT write it (see live_judge.py).
    Called by the website right after an answer is shown; never delays the answer."""
    return JSONResponse(content=jsonable_encoder(live_judge.judge(request.request_id.strip()[:32])))
