"""ONE-TIME (run in Codespaces, then commit the files it lists): make every meaning-number the app needs and
SAVE it in the repo, so Render never rebuilds anything and the Re-check button needs no Cloudflare call.

  1. Old v1 pieces          -> backend/data/embeddings.npy                        (Cloudflare, ~700 units)
  2. Gold v2 pieces         -> backend/data/medallion/gold_embeddings.npy         (Cloudflare, ~450 units)
  3. Gemini backup copy     -> backend/data/medallion/gold_embeddings_gemini.npy  (Gemini key; resumable)
  4. Test questions + senior-librarian scores for the Re-check button
                            -> backend/data/medallion/saved/                      (Cloudflare, ~700 units)
  5. Gemini calibration (so the backup uses the same thresholds as Cloudflare)

Cloudflare account 2 (CLOUDFLARE_ACCOUNT_ID_2 / CLOUDFLARE_API_TOKEN_2) is used automatically when account 1 is out.
Safe to run again: finished parts are loaded, not rebuilt. If Gemini's daily limit stops step 3, run it again tomorrow.
Run:  python3 -m backend.pipeline.embed"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _bank_questions():
    import json
    out = []
    for f in ("benchmark_questions_all.json", "benchmark_questions.json", "benchmark_questions_200.json",
              "benchmark_questions_100.json"):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            for q in json.load(open(p, encoding="utf-8"))["questions"]:
                if q.get("doc") and (q["language"] == "en" or q.get("group") == "reply_language"):
                    out.append(q["q"])
    return list(dict.fromkeys(out))


def main():
    from backend.services import cloudflare, gemini, meaning
    print(f"Cloudflare accounts: {len(cloudflare.accounts())} · Gemini key: {'yes' if gemini.configured() else 'NO'}\n")

    print("1) old v1 pieces (Cloudflare)")
    from backend.services import retriever as v1          # importing builds/loads v1 (saves embeddings.npy)
    if v1._word_index is None:
        v1.build_or_load_index()
    print("   v1:", "meaning numbers ready" if v1._vectors is not None else "NOT ready (Cloudflare keys / units?)")

    print("2) gold v2 pieces (Cloudflare)")
    from backend.services import retriever_v2 as v2
    v2.load()
    if v2._vectors is None:
        v2.build_embeddings()
        v2.load()
    print("   v2:", "meaning numbers ready" if v2._vectors is not None else "NOT ready")

    print("3) Gemini backup copy of the gold pieces")
    gem_done = v2._gvectors is not None or v2.build_gemini_embeddings()
    if gem_done:
        v2.load()

    print("4) test questions + senior-librarian scores for the Re-check button")
    import evaluate_rag
    for pipe in ("v1", "v2"):
        os.environ["PIPELINE"] = pipe
        evaluate_rag.run_benchmark(log=lambda m: print("  ", m))

    if gem_done and gemini.configured():
        print("5) Gemini calibration")
        qs = _bank_questions()[:150]
        todo = [q for q in qs if meaning._vecs.get("gemini", {}).get(meaning._key(q)) is None]
        for i in range(0, len(todo), 50):
            try:
                vecs = gemini.embed(todo[i:i + 50], task="RETRIEVAL_QUERY", timeout=60)
                for q, v in zip(todo[i:i + 50], vecs):
                    meaning._vecs.setdefault("gemini", {})[meaning._key(q)] = v
            except Exception as e:
                print(f"   ⚠️ Gemini question numbers stopped: {str(e)[:160]}")
                break
        v2.calibrate_gemini(qs)

    counts = meaning.save_all()
    print(f"\n✅ saved: {counts.get('cf', 0)} question numbers (Cloudflare), {counts.get('gemini', 0)} (Gemini), "
          f"{counts.get('librarian', 0)} librarian scores")
    print("   Cloudflare accounts today:", cloudflare.status())
    print("\nNow commit these files (git add each one):")
    for f in ("backend/data/embeddings.npy", "backend/data/embeddings_meta.json",
              "backend/data/chunks_cache.json",
              "backend/data/medallion/gold_embeddings.npy", "backend/data/medallion/gold_embeddings_meta.json",
              "backend/data/medallion/gold_embeddings_gemini.npy", "backend/data/medallion/gold_embeddings_gemini_meta.json",
              "backend/data/medallion/saved"):
        if os.path.exists(os.path.join(ROOT, f)):
            print("  ", f)
    if not gem_done:
        print("\n⏸ The Gemini backup copy is not finished (daily limit). Run this command again tomorrow; "
              "everything else is done.")


if __name__ == "__main__":
    main()
