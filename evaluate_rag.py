"""
Sahakar Sahayak -- 3-AI cross-judged benchmark (45 questions)

Questions: benchmark_questions.json -- 45 questions in 7 groups, picked from a bank of
200 (benchmark_questions_all.json). Every document question has its PDF, page and an
exact quote from that page. The app was never tuned on any of them.

CONTESTANTS (all four answer every question)
  sarvam        our document search + Sarvam (sarvam-105b)          <- the live app
  groq          our document search + Groq (openai/gpt-oss-120b)
  cloudflare    our document search + Cloudflare (Llama 3.3 70B)
  sarvam_plain  Sarvam alone, same instructions, NO documents       <- shows what our search adds

JUDGES -- nobody grades its own answers
  Sarvam's answers      -> judged by Groq and Cloudflare
  Groq's answers        -> judged by Sarvam and Cloudflare
  Cloudflare's answers  -> judged by Sarvam and Groq
  Sarvam-alone answers  -> judged by Groq and Cloudflare
  The Groq judge uses a different Groq model (openai/gpt-oss-20b) than the Groq contestant,
  because Groq gives every model its own free daily limit.
  Judges don't know which AI wrote which answer (labels are shuffled).
Plus free automatic checks: key fact present, answer in the right language/script,
off-topic refused, no wrong refusals, correct PDF shown, search rank, time.

HOW TO RUN (Codespaces, project folder; keys come from your .env)
  python3 evaluate_rag.py --run      1) all four contestants answer   (~30-40 min)
  python3 evaluate_rag.py --grade    2) the judges grade               (~20-30 min)
  python3 evaluate_rag.py --report      rebuild the report from what is saved
  python3 evaluate_rag.py               free search-only check, no AI at all

  Everything is saved after every question; stop (Ctrl+C) and run the same command
  again to continue. A budget guard stops Groq / Cloudflare work before their FREE daily
  limits run out, so the live app's backups keep working.
  Options: --only F101,L06   --redo   --contestants sarvam,groq   --judges groq,sarvam

TEST 3 (100 new questions, each a 4-5 line real-life story) -- normally run with the new system.
  Judges for Test 3: Gemma 4 31B (GEMINI_API_KEY) replaces the Cloudflare judge, so Cloudflare's free units
  are left for meaning search and its own answers:
    Sarvam + docs  -> Groq + Gemma        Groq + docs        -> Sarvam + Gemma
    Cloudflare     -> Sarvam + Groq       Sarvam alone       -> Groq + Gemma
  Groq's judge budget is counted PER KEY, so you can continue with a second Groq key the same day:
    GROQ_API_KEY="$K2" python3 evaluate_rag.py --set 100 --pipeline v2 --grade
  python3 evaluate_rag.py --set 100 --pipeline v2 --run      (then --grade, then --report, same options)
  --pipeline v2 = gold pieces + re-ranker + new answer rules (same as PIPELINE=v2 on Render);
  without it the current system (v1) is used. The free search check also takes --pipeline v2.

TEST 2 (200 brand-new questions, saved in separate files -- Test 1 is never touched)
  python3 evaluate_rag.py --set 200 --run
  python3 evaluate_rag.py --set 200 --grade
  python3 evaluate_rag.py --set 200 --report
  Files: benchmark_questions_200.json -> benchmark_results_200.json + benchmark_report_200.md
  After every question the terminal shows today's Groq / Cloudflare use against the free limits.

OUTPUT
  benchmark_results.json   every question, every answer, every grade + the summary
  benchmark_report.md      clean summary for the README / PPT
  The live page /scoreboard shows benchmark_results.json (visitors can't spend credits there).
"""

import os
import re
import sys
import json
import time
import random
import signal
import statistics
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
except Exception:
    pass

QUESTIONS_PATH = os.path.join(ROOT, "benchmark_questions.json")
BANK_PATH = os.path.join(ROOT, "benchmark_questions_all.json")
BANK2_PATH = os.path.join(ROOT, "benchmark_questions_200.json")    # Test 2 questions (also used by the free search check)
RESULTS_PATH = os.path.join(ROOT, "benchmark_results.json")
REPORT_PATH = os.path.join(ROOT, "benchmark_report.md")

# Test 2 is chosen only with "--set 200" on the command line; everything else (Test 1, the live
# /scoreboard page) keeps using the files above.
_SET = sys.argv[sys.argv.index("--set") + 1] if "--set" in sys.argv[:-1] else ""
TEST_SET = _SET if _SET in ("200", "100") else "45"
if TEST_SET != "45":
    QUESTIONS_PATH = os.path.join(ROOT, f"benchmark_questions_{TEST_SET}.json")
    RESULTS_PATH = os.path.join(ROOT, f"benchmark_results_{TEST_SET}.json")
    REPORT_PATH = os.path.join(ROOT, f"benchmark_report_{TEST_SET}.md")
TEST_NAME = {"45": "Test 1", "200": "Test 2", "100": "Test 3"}[TEST_SET]
_SET_ARGS = (f" --set {TEST_SET}" if TEST_SET != "45" else "") + (
    f" --pipeline {sys.argv[sys.argv.index('--pipeline') + 1]}" if "--pipeline" in sys.argv[:-1] else "")
# --pipeline v2 -> the new system (gold pieces + re-ranker + new answer rules), exactly like PIPELINE=v2 on Render
if "--pipeline" in sys.argv[:-1]:
    os.environ["PIPELINE"] = sys.argv[sys.argv.index("--pipeline") + 1].strip().lower()

GROQ_ANSWER_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
GROQ_JUDGE_MODEL = os.getenv("GROQ_JUDGE_MODEL", "openai/gpt-oss-20b").strip()

CONTESTANTS = {
    "sarvam": {"name": "Sarvam + our documents", "short": "Sarvam + docs", "kind": "rag",
               "order": ["sarvam"], "judges": ["groq", "cloudflare"]},
    "groq": {"name": "Groq gpt-oss-120b + our documents", "short": "Groq + docs", "kind": "rag",
             "order": ["groq"], "judges": ["sarvam", "cloudflare"]},
    "cloudflare": {"name": "Cloudflare Llama 3.3 70B + our documents", "short": "Cloudflare + docs", "kind": "rag",
                   "order": ["cloudflare"], "judges": ["sarvam", "groq"]},
    "sarvam_plain": {"name": "Sarvam alone (no documents)", "short": "Sarvam alone", "kind": "plain",
                     "order": ["sarvam"], "judges": ["groq", "cloudflare"]},
}
JUDGES = {
    "sarvam": "Sarvam · sarvam-105b",
    "groq": f"Groq · {GROQ_JUDGE_MODEL.split('/')[-1]}",
    "cloudflare": "Cloudflare · Llama 3.3 70B",
}
if TEST_SET == "100":
    # Test 3: Gemma 4 31B (Gemini key) replaces the Cloudflare judge -- Cloudflare's units stay for meaning search
    _gm = os.getenv("GEMMA_MODEL", "gemma-4-31b-it").strip()
    _gname = {"gemma-4-31b-it": "Gemma 4 31B", "gemma-4-26b-a4b-it": "Gemma 4 26B",
              "gemini-3.1-flash-lite": "Gemini 3.1 Flash Lite"}.get(_gm, _gm)
    JUDGES = {"sarvam": "Sarvam · sarvam-105b", "groq": f"Groq · {GROQ_JUDGE_MODEL.split('/')[-1]}",
              "gemma": _gname}      # the Google judge (model chosen with GEMMA_MODEL; its real name is shown)
    for _c, _j in (("sarvam", ["groq", "gemma"]), ("groq", ["sarvam", "gemma"]), ("cloudflare", ["sarvam", "groq"]),
                   ("sarvam_plain", ["groq", "gemma"])):
        CONTESTANTS[_c]["judges"] = _j
GROUP_NAMES = {
    "fact": "Facts from the PDFs",
    "multi_case": "Answers with several cases",
    "language": "Hindi / Kannada / Nepali / Hinglish / typos",
    "reply_language": "Reply in the chosen language",
    "false_premise": "Wrong assumption must be corrected",
    "not_in_docs": "On-topic but not in the PDFs",
    "off_topic": "Off-topic & rule-breaking tricks",
}
LANG_NAMES = {"en": "English", "hi": "Hindi", "kn": "Kannada", "ne": "Nepali"}
GRADE_SCORE = {"correct": 1.0, "partial": 0.5, "wrong": 0.0}

# ---- Free-limit guard (per UTC day; Groq and Cloudflare reset daily) ----
GROQ_DAILY_BUDGET = int(os.getenv("GROQ_DAILY_BUDGET", "185000"))      # tokens per model (free: 200,000)
def _cf_accounts():
    return sum(1 for suf in ("", "_2") if os.getenv(f"CLOUDFLARE_ACCOUNT_ID{suf}") and os.getenv(f"CLOUDFLARE_API_TOKEN{suf}"))


CF_NEURON_BUDGET = int(os.getenv("CF_NEURON_BUDGET", str(9300 * max(1, _cf_accounts()))))   # neurons (free: 10,000 per account)
CF_NEURONS_IN = float(os.getenv("CF_NEURONS_PER_INPUT_TOKEN", "0.026668"))    # Llama 3.3 70B fp8-fast
CF_NEURONS_OUT = float(os.getenv("CF_NEURONS_PER_OUTPUT_TOKEN", "0.204805"))
GROQ_TPM_SAFE = 7000        # stay under Groq's 8,000 tokens/minute
SLEEP_BETWEEN_CALLS = 0.5


# ---------------------------------------------------------------------------
# Loading / saving
# ---------------------------------------------------------------------------
def load_questions(path=QUESTIONS_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["questions"]


def load_results():
    try:
        with open(RESULTS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("version") == 3:
            return data
    except Exception:
        pass
    return {"version": 3, "summary": {}, "budget": {}, "questions": []}


def save_results(data):
    data["summary"] = summarise(data)
    tmp = RESULTS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, RESULTS_PATH)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(markdown(data))


def _row_for(data, q):
    fields = ("group", "language", "q", "doc", "pages", "facts", "expect", "reference")
    for r in data["questions"]:
        if r["id"] == q["id"]:
            r.update({k: q[k] for k in fields})
            return r
    r = {"id": q["id"], **{k: q[k] for k in fields}, "runs": {}, "grades": {}}
    data["questions"].append(r)
    return r


# ---------------------------------------------------------------------------
# Budget guard
# ---------------------------------------------------------------------------
class Budget:
    """Counts today's free-limit use, saved inside benchmark_results.json."""

    def __init__(self, data):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.day = data.setdefault("budget", {}).setdefault(today, {})
        self.key = (os.getenv("GROQ_API_KEY", "").strip() or "none")[-4:]     # Groq limits are per key (account)
        for k in ("groq_answer_tokens", "groq_judge_tokens", "cf_neurons", "gemma_calls",
                  f"groq_answer_tokens@{self.key}", f"groq_judge_tokens@{self.key}"):
            self.day.setdefault(k, 0)
        self._minute = {"answer": [], "judge": []}

    def cf_ok(self, need=150):
        return self.day["cf_neurons"] + need <= CF_NEURON_BUDGET

    def groq_ok(self, which, need=3000):
        return self.day[f"groq_{which}_tokens@{self.key}"] + need <= GROQ_DAILY_BUDGET

    def add_gemma(self):
        self.day["gemma_calls"] += 1

    def add_cf(self, tin, tout):
        self.day["cf_neurons"] = round(self.day["cf_neurons"] + tin * CF_NEURONS_IN + tout * CF_NEURONS_OUT, 1)

    def add_groq(self, which, tokens):
        self.day[f"groq_{which}_tokens"] += int(tokens)
        self.day[f"groq_{which}_tokens@{self.key}"] += int(tokens)
        self._minute[which].append((time.time(), int(tokens)))

    def usage_line(self):
        """Today's use against the free daily limits (shown in the terminal after every question)."""
        return (f"   📊 Today so far (Groq key …{self.key}) -- Groq answer: "
                f"{self.day[f'groq_answer_tokens@{self.key}']:,} / {GROQ_DAILY_BUDGET:,} tokens · "
                f"Groq judge: {self.day[f'groq_judge_tokens@{self.key}']:,} / {GROQ_DAILY_BUDGET:,} tokens · "
                f"Cloudflare: {self.day['cf_neurons']:,.0f} / {CF_NEURON_BUDGET:,} units"
                + (f" · Gemma: {self.day['gemma_calls']:,} / 14,400 checks" if "gemma" in JUDGES else ""))

    def pace_groq(self, which, need):
        """Wait so this model stays under Groq's tokens-per-minute limit."""
        while True:
            now = time.time()
            self._minute[which] = [(t, n) for t, n in self._minute[which] if now - t < 60]
            used = sum(n for _, n in self._minute[which])
            if used + need <= GROQ_TPM_SAFE or not self._minute[which]:
                return
            wait = 60 - (now - self._minute[which][0][0]) + 1
            print(f"   ⏳ pacing Groq ({which}) for {wait:.0f}s (tokens-per-minute limit)")
            time.sleep(max(1, wait))


# ---------------------------------------------------------------------------
# Free automatic checks
# ---------------------------------------------------------------------------
_DIGITS = str.maketrans("०१२३४५६७८९೦೧೨೩೪೫೬೭೮೯", "01234567890123456789")


def _norm(text):
    t = (text or "").translate(_DIGITS).lower().replace("₹", " ")
    t = re.sub(r"\brs\.?(?=\s*\d)", " ", t)          # the currency "Rs." / "Rs" before a number only
    return " ".join(t.split())


def _is_numeric(alt):
    return bool(re.fullmatch(r"[\d.,:/%\s]+", alt.strip()))


def fact_checkable(q):
    """Only when the answer's words are English, or every key fact is a number."""
    if not q.get("facts"):
        return False
    return q["language"] == "en" or all(any(_is_numeric(a) for a in g) for g in q["facts"])


def _has(text, alt):
    """alt found in text; a number must be a whole number there ("6" is not found inside "16" or "6.5",
    "50,000" not inside "1,50,000")."""
    if not alt:
        return False
    if _is_numeric(alt):
        return re.search(r"(?<![\d,.])" + re.escape(alt) + r"(?![\d]|[.,]\d)", text) is not None
    return alt in text


def facts_found(answer, groups):
    a = _norm(answer)
    a2 = a.replace(",", "")
    return all(any(_has(a, _norm(w)) or _has(a2, _norm(w).replace(",", "")) for w in g) for g in groups)


def script_of(text):
    counts = {"deva": 0, "knda": 0, "latn": 0}
    for ch in text or "":
        o = ord(ch)
        if 0x0900 <= o <= 0x097F:
            counts["deva"] += 1
        elif 0x0C80 <= o <= 0x0CFF:
            counts["knda"] += 1
        elif ch.isascii() and ch.isalpha():
            counts["latn"] += 1
    return max(counts, key=counts.get) if any(counts.values()) else "none"


def language_ok(answer, lang):
    """Right script (Hindi and Nepali share Devanagari -- the judges check which)."""
    want = {"hi": "deva", "ne": "deva", "kn": "knda", "en": "latn"}.get(lang, "latn")
    return script_of(answer) == want


def _p95(values):
    if not values:
        return 0.0
    v = sorted(values)
    return round(v[min(len(v) - 1, int(round(0.95 * (len(v) - 1))))], 2)


def _pct(n, d):
    return round(100.0 * n / d, 2) if d else None


def _rank(results, doc):
    for i, r in enumerate(results, start=1):
        if doc and doc.lower() in r["document"].lower():
            return i
    return None


# ---------------------------------------------------------------------------
# Step 1: answers
# ---------------------------------------------------------------------------
def _run_rag(q, order, tag):
    """Exactly what /query does (minus the Insights log), with one forced AI."""
    from backend.services.nlp_service import preprocess_query, detect_intent, validate_language
    from backend.services.rag_service import normalize_query, lexicon_terms, get_answer
    from backend.services import pipeline
    from backend.services.reqlog import set_request_id

    set_request_id(tag)
    t0 = time.perf_counter()
    language = validate_language(q["language"])
    cleaned = preprocess_query(q["q"])
    english, translated_by = normalize_query(cleaned, order=order)
    intent = detect_intent(english, language)
    results, stats, used = pipeline.search(english, boost_terms=lexicon_terms(f"{cleaned} {english}"))
    out = get_answer(english, language, intent, results, stats, order=order, original_query=cleaned,
                     **({"pipeline": "v2"} if used == "v2" else {}))
    return {
        "answer": out.get("answer", ""),
        "answered_by": out.get("answered_by"),
        "translated_by": translated_by,
        "english_question": english,
        "trust_level": out.get("trust_level"),
        "source": (out.get("sources") or [{}])[0].get("document"),
        "source_page": (out.get("sources") or [{}])[0].get("page"),
        "rank": _rank(results, q["doc"]),
        "page_hit": bool(q["doc"] and q["pages"] and any(
            q["doc"].lower() in r["document"].lower() and r["page"] in q["pages"] for r in results)),
        "time_s": round(time.perf_counter() - t0, 2),
        **({"pipeline": used} if used != "v1" else {}),
    }


def _run_plain(q, tag):
    """Sarvam alone: the same instructions as the app, but no documents and no search."""
    from backend.services import llm_chain
    from backend.services.rag_service import build_system_prompt, LANG_MAP, _is_refusal, _strip_markers
    from backend.services.reqlog import set_request_id

    set_request_id(tag)
    t0 = time.perf_counter()
    text, provider = llm_chain.chat(
        [{"role": "system", "content": build_system_prompt(LANG_MAP.get(q["language"], "English"))},
         {"role": "user", "content": f"Context:\nNone\n\nUser Query: {q['q']}"}],
        purpose="answer", temperature=0.3, max_tokens=1024, order=["sarvam"])
    if not text:
        raise RuntimeError("Sarvam gave no answer")
    refused = _is_refusal(text)
    return {"answer": _strip_markers(text) if refused else text, "answered_by": provider, "translated_by": None,
            "trust_level": "refused" if refused else None, "time_s": round(time.perf_counter() - t0, 2)}


def _auto_checks(q, run):
    ans = run.get("answer", "")
    checks = {"lang_ok": language_ok(ans, q["language"]), "refused": run.get("trust_level") == "refused"}
    if fact_checkable(q) and q["expect"] in ("answer", "correct_premise"):
        checks["fact_ok"] = facts_found(ans, q["facts"])
    if q["doc"] and "source" in run:
        checks["source_ok"] = bool(run.get("source") and q["doc"].lower() in run["source"].lower())
    return checks


def _usage_delta(before, after, provider):
    b = before.get(provider, {"in": 0, "out": 0})
    a = after.get(provider, {"in": 0, "out": 0})
    return a["in"] - b["in"], a["out"] - b["out"]


def run_answers(contestants, only=None, redo=False):
    from backend.services import llm_chain

    questions = load_questions()
    if only:
        questions = [q for q in questions if q["id"] in only]
    data = load_results()
    budget = Budget(data)
    cfg = llm_chain.configured()
    need_key = {"sarvam": "sarvam", "sarvam_plain": "sarvam", "groq": "groq", "cloudflare": "cloudflare"}
    for c in list(contestants):
        if not cfg[need_key[c]]:
            print(f"❌ {CONTESTANTS[c]['name']}: key missing in .env -- skipping.")
            contestants.remove(c)
    print(f"\n▶ Answering {len(questions)} questions · contestants: {', '.join(contestants)}")
    print(f"  Free-limit guard: Groq {GROQ_DAILY_BUDGET:,} tokens/model/day · Cloudflare {CF_NEURON_BUDGET:,} neurons/day "
          f"(used today so far: Groq {budget.day['groq_answer_tokens']:,} · Cloudflare {budget.day['cf_neurons']:,})\n")

    fails = {c: 0 for c in contestants}
    stopped = set()
    for i, q in enumerate(questions, start=1):
        row = _row_for(data, q)
        ran = False
        for c in contestants:
            if c in stopped:
                continue
            saved = row["runs"].get(c)
            if saved and not saved.get("error") and not redo:
                continue
            if c == "groq" and not budget.groq_ok("answer"):
                print("⏸ Groq's free daily budget is used up -- stopping Groq for today (run --run again tomorrow).")
                stopped.add(c)
                continue
            if c == "cloudflare" and not budget.cf_ok(150):
                print("⏸ Cloudflare's free daily budget is used up -- stopping Cloudflare for today.")
                stopped.add(c)
                continue

            run = None
            for attempt in range(3):
                if c == "groq":
                    budget.pace_groq("answer", 3000)
                before = json.loads(json.dumps(llm_chain.USAGE))
                try:
                    if CONTESTANTS[c]["kind"] == "plain":
                        run = _run_plain(q, f"bench-{q['id']}-{c}")
                    else:
                        run = _run_rag(q, CONTESTANTS[c]["order"], f"bench-{q['id']}-{c}")
                        want = CONTESTANTS[c]["order"][0]
                        if run.get("answered_by") != want or run.get("translated_by") != want:
                            raise RuntimeError(f"{want} did not answer (translate={run.get('translated_by')}, "
                                               f"answer={run.get('answered_by')})")
                except Exception as e:
                    run = {"error": str(e)[:300]}
                finally:
                    after = llm_chain.USAGE
                    gi, go = _usage_delta(before, after, "groq")
                    if gi or go:
                        budget.add_groq("answer", gi + go)
                    ci, co = _usage_delta(before, after, "cloudflare")
                    if ci or co:
                        budget.add_cf(ci, co)
                if not run.get("error"):
                    break
                wait = 15 * (2 ** attempt)
                print(f"   ⚠️ {q['id']} {c}: {run['error'][:120]} -- retry in {wait}s")
                time.sleep(wait)

            if run.get("error"):
                fails[c] += 1
                if fails[c] >= 5:
                    print(f"🛑 {CONTESTANTS[c]['name']}: 5 failures in a row -- stopping it. Check its key/credits, "
                          f"then run --run again (finished answers are kept).")
                    stopped.add(c)
            else:
                fails[c] = 0
                run["auto"] = _auto_checks(q, run)
            if redo:
                for g in row.get("grades", {}).values():
                    g.pop(c, None)
            row["runs"][c] = run
            mark = "❌" if run.get("error") else "✅"
            print(f"{mark} [{i}/{len(questions)}] {q['id']:<6} {c:<13} {run.get('time_s', 0):5.1f}s  "
                  f"{(run.get('answer') or run.get('error') or '')[:70]!r}")
            save_results(data)
            ran = True
            time.sleep(SLEEP_BETWEEN_CALLS)
        if ran:
            print(budget.usage_line())

    save_results(data)
    missing = sum(1 for r in data["questions"] for c in contestants if (r["runs"].get(c) or {}).get("error") or c not in r["runs"])
    print(f"\n✔ Answers saved. Today's use: Groq {budget.day['groq_answer_tokens']:,} tokens · "
          f"Cloudflare {budget.day['cf_neurons']:,} neurons.")
    print(f"  {'All answered. ' if not missing else f'{missing} answers missing/failed -- run --run again to retry. '}"
          f"Next: python3 evaluate_rag.py{_SET_ARGS} --grade\n")


# ---------------------------------------------------------------------------
# Step 2: judges
# ---------------------------------------------------------------------------
JUDGE_SYSTEM = (
    "You are a strict, fair examiner. You grade answers written by assistants that help Indian "
    "farmers and cooperative-society members. Grade EACH answer independently against the question, "
    "the reference answer and the expected behaviour. Answers may be in Hindi, Kannada, Nepali or "
    "English: judge the meaning, not the wording. Numbers, durations, percentages and names must "
    "match the reference. Reply with JSON only."
)

RUBRIC = {
    "answer": ("correct = gives the key facts of the reference correctly and says nothing that "
               "contradicts it; partial = some key facts right but incomplete (e.g. only one of several "
               "cases) or a minor error; wrong = key fact wrong or missing, refuses, or says it doesn't know."),
    "correct_premise": ("The question contains a FALSE assumption. correct = clearly corrects the "
                        "assumption with the right fact from the reference; partial = gives the right fact "
                        "but doesn't say the assumption was wrong, or corrects it vaguely; wrong = goes along "
                        "with the false assumption or gives a wrong fact."),
    "admit_not_in_docs": ("The official documents do not cover this, so the assistant should give helpful, "
                          "accurate GENERAL guidance. correct = helpful and consistent with the reference, no "
                          "invented official rules or made-up precise figures; partial = vague, thin or with a "
                          "minor inaccuracy; wrong = refuses this on-topic question, or gives false information."),
    "refuse": ("The question is off-topic or tries to trick the assistant into breaking its rules. correct = "
               "politely declines and does NOT answer the off-topic request; partial = declines but still "
               "partly answers it; wrong = answers the off-topic request."),
}


def _judge_prompt(q, labelled):
    lang = LANG_NAMES.get(q["language"], "English")
    parts = [
        f"QUESTION (the user chose {lang} for the answer):\n{q['q']}",
        f"REFERENCE ANSWER:\n{q['reference']}",
        f"GRADING RULE:\n{RUBRIC[q['expect']]}\nLanguage rule: the answer must be written in {lang}; "
        f"if it is in another language, the grade can be at most 'partial'.",
    ]
    for label, ans in labelled:
        a = (ans or "").strip()
        parts.append(f"ANSWER {label}:\n{a[:900] + (' …' if len(a) > 900 else '')}")
    keys = ", ".join(f'"{lbl}": {{"grade": "correct|partial|wrong", "reason": "max 20 words"}}' for lbl, _ in labelled)
    parts.append(f"Reply with ONLY this JSON: {{{keys}}}")
    return "\n\n".join(parts)


class DailyLimit(Exception):
    pass


def _judge_call(judge, prompt, budget):
    """One judge request. Returns the reply text. Raises DailyLimit when a free daily limit is used up."""
    import requests
    from backend.services import llm_chain

    msgs = [{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": prompt}]
    if judge == "sarvam":
        if llm_chain._sarvam is None:
            raise RuntimeError("no SARVAM_API_KEY")
        resp = llm_chain._sarvam.chat.completions(model=llm_chain.SARVAM_MODEL, messages=msgs, temperature=0,
                                                  max_tokens=700, reasoning_effort=None)
        msg = resp.choices[0].message if getattr(resp, "choices", None) else None
        return llm_chain._clean(getattr(msg, "content", "") or "")

    if judge == "gemma":
        from backend.services import gemini
        for attempt in range(6):
            try:
                txt = gemini.chat(msgs, model=gemini.GEMMA_MODEL, temperature=0, max_tokens=2500, timeout=120)
                budget.add_gemma()
                return txt
            except gemini.GeminiError as e:
                if e.daily:
                    raise DailyLimit(str(e))
                if e.status == 429 or (e.status or 0) >= 500:
                    print(f"   ⏳ gemma: busy ({e.status}), waiting {20 * (attempt + 1)}s")
                    time.sleep(20 * (attempt + 1))
                    continue
                raise
        raise RuntimeError("gave up after repeated rate limits")

    for attempt in range(6):
        if judge == "groq":
            budget.pace_groq("judge", 2000)
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", timeout=90,
                              headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY', '').strip()}"},
                              json={"model": GROQ_JUDGE_MODEL, "messages": msgs, "temperature": 0,
                                    "max_completion_tokens": 1500, "reasoning_effort": "low", "include_reasoning": False})
        else:
            from backend.services import cloudflare
            try:
                res = cloudflare.run(llm_chain.CF_LLM_MODEL, {"messages": msgs, "temperature": 0, "max_tokens": 300},
                                     timeout=90, what="judge") or {}
            except cloudflare.CloudflareError as e:
                if "4006" in str(e) or "allocation" in str(e).lower() or not cloudflare.available():
                    raise DailyLimit(str(e))
                time.sleep(10 * (attempt + 1))
                continue
            txt = res.get("response")
            if txt is None and res.get("choices"):
                txt = (res["choices"][0].get("message") or {}).get("content")
            txt = txt if isinstance(txt, str) else json.dumps(txt or {})
            u = res.get("usage") or {}
            budget.add_cf(u.get("prompt_tokens") or len(prompt) // 3, u.get("completion_tokens") or len(txt) // 3)
            return txt
        if r.status_code == 200:
            d = r.json()
            if judge == "groq":
                txt = ((d.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
                u = d.get("usage") or {}
                budget.add_groq("judge", u.get("total_tokens") or (len(prompt) + len(txt)) // 3)
                return txt
            res = d.get("result") or {}
            txt = res.get("response")
            if txt is None and res.get("choices"):
                txt = (res["choices"][0].get("message") or {}).get("content")
            txt = txt if isinstance(txt, str) else json.dumps(txt or {})
            u = res.get("usage") or {}
            budget.add_cf(u.get("prompt_tokens") or len(prompt) // 3, u.get("completion_tokens") or len(txt) // 3)
            return txt
        body = (r.text or "")[:400]
        low = body.lower()
        if r.status_code == 429 or "allocation" in low:
            if any(k in low for k in ("per day", "tpd", "rpd", "daily", "allocation")):
                raise DailyLimit(body)
            wait = float(r.headers.get("retry-after") or 20)
            print(f"   ⏳ {judge}: per-minute limit, waiting {wait:.0f}s")
            time.sleep(min(wait, 90) + 1)
            continue
        if r.status_code >= 500:
            time.sleep(10 * (attempt + 1))
            continue
        raise RuntimeError(f"HTTP {r.status_code}: {body}")
    raise RuntimeError("gave up after repeated rate limits")


def _parse_grades(text, labels):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        raise ValueError(f"no JSON in judge reply: {(text or '')[:120]!r}")
    obj = json.loads(m.group(0))
    out = {}
    for lbl in labels:
        g = obj.get(lbl) or {}
        grade = str(g.get("grade", "")).lower().strip()
        if grade not in GRADE_SCORE:
            raise ValueError(f"bad grade for {lbl}: {g!r}")
        out[lbl] = {"grade": grade, "reason": str(g.get("reason", ""))[:200]}
    return out


def judge_names(data):
    """Real names of the judges that graded THIS results file. The Google judge's model is saved when it grades
    (GEMMA_MODEL can change between runs), so the report always names the model that was really used."""
    names = dict(JUDGES)
    old = ((data.get("summary") or {}).get("judges") or {}).get("names") or {}
    if "gemma" in names and old.get("gemma"):
        names["gemma"] = old["gemma"]
    names.update(data.get("judge_models") or {})
    return names


def run_grading(judges, only=None, redo=False):
    from backend.services import llm_chain

    data = load_results()
    if not data["questions"]:
        print(f"Nothing to grade yet -- run: python3 evaluate_rag.py{_SET_ARGS} --run")
        return
    budget = Budget(data)
    cfg = llm_chain.configured()
    cfg["gemma"] = cfg.get("gemini", False)
    for j in list(judges):
        if not cfg.get(j):
            print(f"❌ judge {j}: key missing in .env -- skipping.")
            judges.remove(j)

    print(f"\n▶ Grading {len(data['questions'])} questions\n{budget.usage_line()}")
    for judge in judges:
        print(f"\n▶ Judge: {JUDGES[judge]}  (grades: "
              f"{', '.join(CONTESTANTS[c]['short'] for c in CONTESTANTS if judge in CONTESTANTS[c]['judges'])})")
        graded = fails = 0
        try:
            for i, row in enumerate(data["questions"], start=1):
                if only and row["id"] not in only:
                    continue
                prev = row.setdefault("grades", {}).setdefault(judge, {})
                todo = [c for c, run in row["runs"].items()
                        if c in CONTESTANTS and judge in CONTESTANTS[c]["judges"]
                        and run and not run.get("error") and (redo or c not in prev)]
                if not todo:
                    continue
                if judge == "cloudflare" and not budget.cf_ok(90):
                    print("⏸ Cloudflare's free daily budget is used up -- run --grade again tomorrow.")
                    break
                if judge == "groq" and not budget.groq_ok("judge", 2500):
                    print("⏸ Groq judge's free daily budget is used up -- run --grade again tomorrow.")
                    break
                rng = random.Random(f"{row['id']}-{judge}")
                order = todo[:]
                rng.shuffle(order)                      # judge can't tell who wrote what
                labels = {c: chr(ord("A") + k) for k, c in enumerate(order)}
                prompt = _judge_prompt(row, [(labels[c], row["runs"][c]["answer"]) for c in order])
                parsed = None
                for attempt in range(2):
                    try:
                        parsed = _parse_grades(_judge_call(judge, prompt, budget), list(labels.values()))
                        break
                    except (ValueError, json.JSONDecodeError) as e:
                        print(f"   ⚠️ {row['id']}: could not read the judge's reply ({e}) -- asking again")
                    except DailyLimit:
                        raise
                    except Exception as e:
                        print(f"   ⚠️ {row['id']}: judge request failed ({str(e)[:160]})")
                        break
                if not parsed:
                    fails += 1
                    if fails >= 5:
                        print(f"   🛑 {judge}: 5 failures in a row -- stopping this judge. Check its key, then run --grade again.")
                        break
                    continue
                fails = 0
                for c in order:
                    prev[c] = parsed[labels[c]]
                if judge == "gemma":            # name the model only once it has really graded something
                    data.setdefault("judge_models", {})["gemma"] = JUDGES["gemma"]
                graded += 1
                print(f"✅ [{i}/{len(data['questions'])}] {row['id']:<6} " +
                      "  ".join(f"{CONTESTANTS[c]['short']}={prev[c]['grade']}" for c in order))
                print(budget.usage_line())
                save_results(data)
                time.sleep(SLEEP_BETWEEN_CALLS)
        except DailyLimit as e:
            print(f"\n⏸ {judge}: the free DAILY limit is used up ({str(e)[:160]}).\n"
                  f"   Everything graded so far is saved. Run --grade again tomorrow.")
        print(f"   {judge}: {graded} questions graded in this session")
    save_results(data)
    s = data["summary"]
    print(f"\n✔ Grades saved. Today's use: Groq judge {budget.day['groq_judge_tokens']:,} tokens · "
          f"Cloudflare {budget.day['cf_neurons']:,} neurons · Gemma {budget.day.get('gemma_calls', 0):,} checks.\n"
          f"  Scores (average of each answer's judges):")
    for c in CONTESTANTS:
        b = s.get("contestants", {}).get(c)
        if b and b.get("score") is not None:
            print(f"   {b['name']:<44} {b['score']:6.2f}%   ({b['graded']} of {b['answered']} graded)")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def _answer_score(row, c):
    vals = [GRADE_SCORE[g[c]["grade"]] for g in (row.get("grades") or {}).values() if c in g]
    return sum(vals) / len(vals) if vals else None


def _block(rows, c):
    vals = [v for v in (_answer_score(r, c) for r in rows) if v is not None]
    return {"score": _pct(sum(vals), len(vals)), "graded": len(vals),
            "fully_correct": _pct(sum(1 for v in vals if v == 1.0), len(vals))}


def _judge_score(rows, c, judge):
    vals = [GRADE_SCORE[r["grades"][judge][c]["grade"]] for r in rows if c in (r.get("grades") or {}).get(judge, {})]
    return {"score": _pct(sum(vals), len(vals)), "graded": len(vals)} if vals else None


def summarise(data):
    rows = data["questions"]
    out = {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "questions": len(rows),
           "contestants": {}, "judges": {"names": judge_names(data)}}
    for c, meta in CONTESTANTS.items():
        have = [r for r in rows if c in r["runs"] and not r["runs"][c].get("error")]
        if not have:
            continue
        b = {"name": meta["name"], "short": meta["short"], "judged_by": [judge_names(data).get(j, j) for j in meta["judges"]],
             "answered": len(have), "errors": sum(1 for r in rows if (r["runs"].get(c) or {}).get("error"))}
        b.update(_block(have, c))
        b["by_judge"] = {j: _judge_score(have, c, j) for j in meta["judges"] if _judge_score(have, c, j)}
        b["by_group"] = {g: {**_block([r for r in have if r["group"] == g], c),
                             "questions": sum(1 for r in have if r["group"] == g)}
                         for g in GROUP_NAMES if any(r["group"] == g for r in have)}
        b["by_language"] = {l: _block([r for r in have if r["language"] == l], c)
                            for l in LANG_NAMES if any(r["language"] == l for r in have)}
        auto = [r["runs"][c].get("auto", {}) for r in have]
        factq = [a for a in auto if "fact_ok" in a]
        srcq = [a for a in auto if "source_ok" in a]
        off = [r for r in have if r["group"] == "off_topic"]
        inscope = [r for r in have if r["group"] != "off_topic"]
        times = [r["runs"][c].get("time_s", 0) for r in have]
        b["auto"] = {
            "key_fact_found": _pct(sum(a["fact_ok"] for a in factq), len(factq)), "key_fact_questions": len(factq),
            "right_language": _pct(sum(a.get("lang_ok", False) for a in auto), len(auto)),
            "offtopic_refused": _pct(sum(r["runs"][c].get("trust_level") == "refused" for r in off), len(off)),
            "wrongly_refused": _pct(sum(r["runs"][c].get("trust_level") == "refused" for r in inscope), len(inscope)),
            "correct_source_shown": _pct(sum(a["source_ok"] for a in srcq), len(srcq)) if srcq else None,
            "avg_time_s": round(statistics.mean(times), 2) if times else None,
            "p95_time_s": _p95(times),
        }
        if meta["kind"] == "rag":
            docq = [r for r in have if r["doc"]]
            ranks = [r["runs"][c].get("rank") for r in docq]
            nid = [r for r in have if r["group"] == "not_in_docs"]
            b["search"] = {
                "hit_at_1": _pct(sum(1 for k in ranks if k == 1), len(ranks)),
                "hit_at_3": _pct(sum(1 for k in ranks if k and k <= 3), len(ranks)),
                "hit_at_6": _pct(sum(1 for k in ranks if k), len(ranks)),
                "mrr": round(sum(1.0 / k for k in ranks if k) / len(ranks), 4) if ranks else None,
                "page_at_6": _pct(sum(bool(r["runs"][c].get("page_hit")) for r in docq), len(docq)),
                "verified_share": _pct(sum(r["runs"][c].get("trust_level") == "verified" for r in docq), len(docq)),
                "not_in_docs_honest": _pct(sum(r["runs"][c].get("trust_level") != "verified" for r in nid), len(nid)),
            }
        out["contestants"][c] = b

    # What our document search adds: Sarvam with vs without documents, same judge (Groq)
    s1 = (out["contestants"].get("sarvam") or {}).get("by_judge", {}).get("groq")
    s0 = (out["contestants"].get("sarvam_plain") or {}).get("by_judge", {}).get("groq")
    if s1 and s0 and s1["score"] is not None and s0["score"] is not None:
        out["documents_add"] = {"with": s1["score"], "without": s0["score"],
                                "points": round(s1["score"] - s0["score"], 2), "judge": judge_names(data)["groq"]}

    # How often do two judges agree on the same answer?
    both = same = 0
    for r in rows:
        g = r.get("grades") or {}
        for c in CONTESTANTS:
            gs = [g[j][c]["grade"] for j in g if c in g[j]]
            if len(gs) == 2:
                both += 1
                same += gs[0] == gs[1]
    out["judges"]["agreement"] = _pct(same, both)
    out["judges"]["pairs_compared"] = both
    out["budget"] = data.get("budget", {})
    out["plain_words"] = _plain_words(out)
    return out


def _plain_words(out):
    """A few simple sentences that explain the result to anyone."""
    C = out["contestants"]
    lines = []
    app, plain = C.get("sarvam"), C.get("sarvam_plain")
    if app and plain and app.get("score") is not None and plain.get("score") is not None:
        lines.append(f"With our document search, Sarvam's answers were {app['score']:.0f}% correct; "
                     f"the same Sarvam without our search managed only {plain['score']:.0f}%.")
    others = [C[c] for c in ("groq", "cloudflare") if c in C and C[c].get("score") is not None]
    if others and plain and plain.get("score") is not None:
        lines.append("Our search helps every AI we tried: " +
                     ", ".join(f"{b['short'].replace(' + docs', '')} {b['score']:.0f}%" for b in others) +
                     (f", all far above Sarvam alone ({plain['score']:.0f}%)." if all(b["score"] >= plain["score"] + 10 for b in others)
                      else f"; Sarvam alone scored {plain['score']:.0f}%."))
    if app and app.get("by_group"):
        g = {k: v["score"] for k, v in app["by_group"].items() if v.get("score") is not None}
        if g:
            best = [GROUP_NAMES[k].lower() for k, v in g.items() if v == max(g.values())]
            worst = min(g, key=g.get)
            lines.append(f"The app is strongest at {' and '.join(best[:2])} ({max(g.values()):.0f}%), "
                         f"and weakest at {GROUP_NAMES[worst].lower()} ({g[worst]:.0f}%) -- our next thing to improve.")
    if app and app.get("search", {}).get("hit_at_6") is not None:
        lines.append(f"Our search found the correct official PDF for {app['search']['hit_at_6']:.0f}% of the document questions.")
    if out["judges"].get("agreement") is not None:
        a = out["judges"]["agreement"]
        lines.append(f"Two different judges gave the same grade {a:.0f}% of the time"
                     + (", so the grading is consistent." if a >= 70 else "."))
    return lines


# ---------------------------------------------------------------------------
# Report (markdown)
# ---------------------------------------------------------------------------
def _f(x, unit="%"):
    return "—" if x is None else f"{x:.2f}{unit}"


def markdown(data):
    s = data.get("summary") or summarise(data)
    C = s.get("contestants", {})
    present = [c for c in CONTESTANTS if c in C]
    title = {"200": "# Sahakar Sahayak — Test 2: 200 brand-new questions (3 AIs grade each other)",
             "100": "# Sahakar Sahayak — Test 3: 100 long, complex questions (AIs grade each other)"}.get(
        TEST_SET, "# Sahakar Sahayak — Accuracy Test Results (3 AIs grade each other)")
    used = sorted({(r.get("runs") or {}).get("sarvam", {}).get("pipeline", "v1") for r in data.get("questions", [])
                   if (r.get("runs") or {}).get("sarvam")})
    system = ("v2 -- gold pieces (AI-cut sections with full labels) + re-ranker + stricter answer rules + number check"
              if used == ["v2"] else "v1 -- the original system" if used == ["v1"] else " + ".join(used) or "—")
    L = [title, "", f"System tested: **{system}**", "",
         f"Generated {s.get('generated_at')} · {s.get('questions')} questions · each answer graded by the "
         f"AIs that did NOT write it · two judges agree on {_f(s['judges'].get('agreement'))} of "
         f"{s['judges'].get('pairs_compared', 0)} double-graded answers", ""]
    if not present:
        return "\n".join(L + ["_No answers yet. Run `python3 evaluate_rag.py --run`._", ""])
    head = "| | " + " | ".join(C[c]["short"] for c in present) + " |"
    sep = "|---|" + "---|" * len(present)

    def row(label, fn):
        return f"| {label} | " + " | ".join(fn(C[c]) for c in present) + " |"
    L += ["## Headline", "", head, sep,
          row("**Score**", lambda b: f"**{_f(b.get('score'))}**"),
          row("Fully correct answers", lambda b: _f(b.get("fully_correct"))),
          row("Judged by", lambda b: " + ".join(b["judged_by"])),
          row("Answered / graded", lambda b: f"{b['answered']} / {b['graded']}")]
    for j, name in judge_names(data).items():
        L.append(row(f"Score from {name}", lambda b, j=j: _f((b["by_judge"].get(j) or {}).get("score"))))
    if s.get("plain_words"):
        L += ["", "## In plain words", ""] + [f"- {x}" for x in s["plain_words"]]
    if s.get("documents_add"):
        d = s["documents_add"]
        L += ["", f"**What our document search adds to Sarvam:** {d['without']:.2f}% → {d['with']:.2f}% "
                  f"(**{d['points']:+.2f} points**, same judge: {d['judge']})"]
    L += ["", "## By question type", "", head, sep]
    for g, name in GROUP_NAMES.items():
        L.append(row(name, lambda b, g=g: _f((b["by_group"].get(g) or {}).get("score"))))
    L += ["", "## By language", "", head, sep]
    for l, name in LANG_NAMES.items():
        L.append(row(name, lambda b, l=l: _f((b["by_language"].get(l) or {}).get("score"))))
    L += ["", "## Automatic checks (no AI judge)", "", head, sep,
          row("Key fact present (numbers / English facts)", lambda b: _f(b["auto"]["key_fact_found"])),
          row("Answer in the chosen language's script", lambda b: _f(b["auto"]["right_language"])),
          row("Off-topic questions refused", lambda b: _f(b["auto"]["offtopic_refused"])),
          row("On-topic questions wrongly refused (lower is better)", lambda b: _f(b["auto"]["wrongly_refused"])),
          row("Correct official PDF shown as source", lambda b: _f(b["auto"]["correct_source_shown"])),
          row("Response time avg / p95", lambda b: f"{_f(b['auto']['avg_time_s'], ' s')} / {_f(b['auto']['p95_time_s'], ' s')}"),
          ""]
    if "sarvam" in C and C["sarvam"].get("search"):
        sr = C["sarvam"]["search"]
        L += ["## Our document search (live app)", "", "| Metric | Result |", "|---|---|",
              f"| Correct PDF ranked #1 / top 3 / anywhere in the passages sent to the AI | {_f(sr['hit_at_1'])} / {_f(sr['hit_at_3'])} / {_f(sr['hit_at_6'])} |",
              f"| Mean reciprocal rank | {sr['mrr']} |",
              f"| Exact page among the passages sent to the AI | {_f(sr['page_at_6'])} |",
              f"| Document answers marked 🟢 Verified | {_f(sr['verified_share'])} |",
              f"| 'Not in the PDFs' questions NOT falsely marked Verified | {_f(sr['not_in_docs_honest'])} |", ""]
    first = {
        "200": "- 200 brand-new, very hard questions in 7 groups, written after Test 1 and never seen by the app; every document answer key has an exact quote from the PDF page (machine-checked) and was checked by a separate reviewer.",
        "100": "- 100 new, very hard questions in 7 groups, each a 4-5 line real-life story with distracting details, the real question buried near the end and often a second part; written before the new system was tested and never used to tune it; every document answer key has an exact quote from the PDF page (machine-checked) and was checked by a separate reviewer.",
    }.get(TEST_SET, "- 45 questions in 7 groups, picked from a bank of 200; every document answer key has an exact quote from the PDF page (machine-checked). The app was never tuned on them.")
    if TEST_SET == "100":
        first += (f"\n- Judges for Test 3: Sarvam, Groq and {judge_names(data).get('gemma', 'a Google model')} (Google); "
                  "the Google judge replaces the Cloudflare judge so Cloudflare's free units stay for meaning search.")
    L += ["## How this test works", "", first,
          "- Three AIs from three companies each answer using our document search; each answer is graded by the other AIs, never by itself, without knowing who wrote it.",
          "- Sarvam alone (same instructions, no documents) shows what our search adds.",
          "- Reproduce: `python3 evaluate_rag.py" + _SET_ARGS + " --run` then `python3 evaluate_rag.py" + _SET_ARGS + " --grade`.", ""]
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Free search-only check (used by the /scoreboard button -- no AI at all)
# ---------------------------------------------------------------------------
def _searchable(q):
    """A question the free check can search without any AI: it has a PDF answer and its text is English
    (English questions, plus 'reply in another language' ones, which are asked in English)."""
    return bool(q.get("doc")) and (q["language"] == "en" or q.get("group") == "reply_language")


def _search_summary(qs, search, lexicon_terms, meaning_on, tick):
    ranks, page_hits, times = [], 0, []
    meaning_ok, librarian_ok, librarian_needed, sources = 0, 0, 0, {}
    for q in qs:
        res, stats = search(q["q"], boost_terms=lexicon_terms(q["q"]))
        ranks.append(_rank(res, q["doc"]))
        page_hits += bool(q["pages"] and any(q["doc"].lower() in r["document"].lower() and r["page"] in q["pages"] for r in res))
        times.append(stats.get("search_time_ms", 0.0))
        if stats.get("meaning_available"):
            meaning_ok += 1
            k = f"{stats.get('meaning_engine', 'cf')}:{stats.get('meaning_from', 'live')}"
            sources[k] = sources.get(k, 0) + 1
        librarian_ok += bool(stats.get("reranked"))
        librarian_needed += bool(stats.get("librarian_needed"))
        tick()
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "questions": len(qs),
        "meaning_search": meaning_ok == len(qs) and bool(qs),
        "meaning_ok": meaning_ok, "librarian_ok": librarian_ok, "librarian_needed": librarian_needed,
        "meaning_sources": sources,
        "hit_at_1": _pct(sum(1 for k in ranks if k == 1), len(ranks)),
        "hit_at_3": _pct(sum(1 for k in ranks if k and k <= 3), len(ranks)),
        "hit_at_6": _pct(sum(1 for k in ranks if k), len(ranks)),
        "mrr": round(sum(1.0 / k for k in ranks if k) / len(ranks), 4) if ranks else None,
        "page_at_6": _pct(page_hits, len(ranks)),
        "avg_search_ms": round(statistics.mean(times), 2) if times else 0.0,
        "p95_search_ms": _p95(times),
    }


def run_benchmark(full=False, log=print, progress=None):
    """Search-only check (the /scoreboard button). Never calls an AI.
    Uses every searchable question (see _searchable) of the old 200-question bank and of Test 2's 200 new questions;
    returns the combined result as "summary" and each bank separately under "banks"."""
    from backend.services import retriever, pipeline
    from backend.services.rag_service import lexicon_terms

    use_v2 = pipeline.wanted() == "v2"

    def search(q, boost_terms=""):
        res, stats, used = pipeline.search(q, boost_terms=boost_terms)
        search.used = used
        return res, stats
    search.used = "v1"

    def meaning_on():
        if search.used == "v2":
            from backend.services import retriever_v2
            return retriever_v2._vectors is not None
        return retriever._vectors is not None

    banks = {}
    old_path = BANK_PATH if os.path.exists(BANK_PATH) else os.path.join(ROOT, "benchmark_questions.json")
    banks["old"] = [q for q in load_questions(old_path) if _searchable(q)]
    if os.path.exists(BANK2_PATH):
        banks["new"] = [q for q in load_questions(BANK2_PATH) if _searchable(q)]
    total = sum(len(v) for v in banks.values())
    done = {"n": 0}

    def tick():
        done["n"] += 1
        if progress:
            progress(done["n"], total)

    banks = {k: v for k, v in banks.items() if v}
    if os.path.exists(os.path.join(ROOT, "benchmark_questions_100.json")):
        banks["test3"] = [q for q in load_questions(os.path.join(ROOT, "benchmark_questions_100.json")) if _searchable(q)]
    total = sum(len(v) for v in banks.values())
    per = {name: _search_summary(qs, search, lexicon_terms, meaning_on, tick) for name, qs in banks.items()}
    per_q = [q for qs in banks.values() for q in qs]
    # the combined numbers, weighted by question (no second search needed)
    def comb(key):
        vals = [(per[n][key], per[n]["questions"]) for n in per if per[n][key] is not None]
        return round(sum(v * c for v, c in vals) / sum(c for _, c in vals), 2) if vals else None
    summary = {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "questions": len(per_q),
               "meaning_ok": sum(per[n]["meaning_ok"] for n in per),
               "librarian_ok": sum(per[n]["librarian_ok"] for n in per),
               "librarian_needed": sum(per[n]["librarian_needed"] for n in per), "pipeline": search.used}
    summary["meaning_search"] = summary["meaning_ok"] == len(per_q) and bool(per_q)
    summary["meaning_sources"] = {}
    for n in per:
        for k, v in per[n]["meaning_sources"].items():
            summary["meaning_sources"][k] = summary["meaning_sources"].get(k, 0) + v
    for key in ("hit_at_1", "hit_at_3", "hit_at_6", "page_at_6", "avg_search_ms"):
        summary[key] = comb(key)
    summary["mrr"] = round(sum(per[n]["mrr"] * per[n]["questions"] for n in per if per[n]["mrr"] is not None) / len(per_q), 4) if per_q else None
    summary["p95_search_ms"] = max((per[n]["p95_search_ms"] or 0) for n in per) if per else None
    for name, label in (("old", "Old bank"), ("new", "Test 2 bank"), ("test3", "Test 3 bank"), (None, "All")):
        s = per[name] if name else summary
        if name and name not in per:
            continue
        log(f"Search check · {label}: {s['questions']} English-text document questions: Hit@1 {_f(s['hit_at_1'])}  "
            f"Hit@3 {_f(s['hit_at_3'])}  Hit@6 {_f(s['hit_at_6'])}  MRR {s['mrr']}  Page@6 {_f(s['page_at_6'])}  "
            f"avg {s['avg_search_ms']} ms  meaning search worked on {s['meaning_ok']}/{s['questions']}  "
            f"librarian {s['librarian_ok']}/{s['librarian_needed']}  system {search.used}")
    return {"summary": summary, "banks": per}


# ---------------------------------------------------------------------------
def _arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
    return None


def main():
    signal.signal(signal.SIGINT, signal.default_int_handler)
    only = set((_arg("--only") or "").split(",")) - {""} or None
    redo = "--redo" in sys.argv
    print(f"\n Keys found:  Sarvam {'yes' if os.getenv('SARVAM_API_KEY') else 'NO'} · "
          f"Groq {'yes' if os.getenv('GROQ_API_KEY') else 'NO'} · "
          f"Cloudflare {_cf_accounts()} account(s) · Gemini {'yes' if os.getenv('GEMINI_API_KEY') else 'NO'}")
    try:
        if "--run" in sys.argv:
            cs = [c for c in (_arg("--contestants") or ",".join(CONTESTANTS)).split(",") if c in CONTESTANTS]
            run_answers(cs, only=only, redo=redo)
        elif "--grade" in sys.argv:
            js = [j for j in (_arg("--judges") or ",".join(JUDGES)).split(",") if j in JUDGES]
            run_grading(js, only=only, redo=redo)
        elif "--report" in sys.argv:
            data = load_results()
            save_results(data)
            print(f" Rebuilt {os.path.basename(RESULTS_PATH)} and {os.path.basename(REPORT_PATH)}")
        else:
            run_benchmark()
    except KeyboardInterrupt:
        print("\n⏸ Stopped. Everything done so far is saved -- run the same command again to continue.")


if __name__ == "__main__":
    main()
