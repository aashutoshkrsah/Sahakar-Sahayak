# Sahakar Sahayak — Test 3: 100 long, complex questions (AIs grade each other)

System tested: **v2 -- gold pieces (AI-cut sections with full labels) + re-ranker + stricter answer rules + number check**

Generated 2026-09-30 23:24 · 100 questions · each answer graded by the AIs that did NOT write it · two judges agree on 81.25% of 400 double-graded answers

## Headline

| | Sarvam + docs | Groq + docs | Cloudflare + docs | Sarvam alone |
|---|---|---|---|---|
| **Score** | **81.00%** | **80.00%** | **74.00%** | **26.50%** |
| Fully correct answers | 68.00% | 69.00% | 61.00% | 14.00% |
| Judged by | Groq · gpt-oss-20b + Gemini 3.1 Flash Lite | Sarvam · sarvam-105b + Gemini 3.1 Flash Lite | Sarvam · sarvam-105b + Groq · gpt-oss-20b | Groq · gpt-oss-20b + Gemini 3.1 Flash Lite |
| Answered / graded | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 |
| Score from Sarvam · sarvam-105b | — | 79.50% | 70.50% | — |
| Score from Groq · gpt-oss-20b | 81.50% | — | 77.50% | 30.00% |
| Score from Gemini 3.1 Flash Lite | 80.50% | 80.50% | — | 23.00% |

## In plain words

- With our document search, Sarvam's answers were 81% correct; the same Sarvam without our search managed only 26%.
- Our search helps every AI we tried: Groq 80%, Cloudflare 74%, all far above Sarvam alone (26%).
- The app is strongest at answers with several cases (97%), and weakest at wrong assumption must be corrected (56%) -- our next thing to improve.
- Our search found the correct official PDF for 98% of the document questions.
- Two different judges gave the same grade 81% of the time, so the grading is consistent.

**What our document search adds to Sarvam:** 30.00% → 81.50% (**+51.50 points**, same judge: Groq · gpt-oss-20b)

## By question type

| | Sarvam + docs | Groq + docs | Cloudflare + docs | Sarvam alone |
|---|---|---|---|---|
| Facts from the PDFs | 83.93% | 79.46% | 83.93% | 15.18% |
| Answers with several cases | 97.06% | 92.65% | 89.71% | 11.76% |
| Hindi / Kannada / Nepali / Hinglish / typos | 72.50% | 86.25% | 71.25% | 21.25% |
| Reply in the chosen language | 70.00% | 75.00% | 80.00% | 0.00% |
| Wrong assumption must be corrected | 56.25% | 45.83% | 62.50% | 18.75% |
| On-topic but not in the PDFs | 92.50% | 75.00% | 75.00% | 70.00% |
| Off-topic & rule-breaking tricks | 87.50% | 100.00% | 25.00% | 84.38% |

## By language

| | Sarvam + docs | Groq + docs | Cloudflare + docs | Sarvam alone |
|---|---|---|---|---|
| English | 82.39% | 78.17% | 77.46% | 25.70% |
| Hindi | 77.08% | 93.75% | 75.00% | 41.67% |
| Kannada | 75.00% | 70.00% | 57.50% | 10.00% |
| Nepali | 82.14% | 89.29% | 60.71% | 32.14% |

## Automatic checks (no AI judge)

| | Sarvam + docs | Groq + docs | Cloudflare + docs | Sarvam alone |
|---|---|---|---|---|
| Key fact present (numbers / English facts) | 70.37% | 59.26% | 76.54% | 8.64% |
| Answer in the chosen language's script | 99.00% | 100.00% | 100.00% | 94.00% |
| Off-topic questions refused | 87.50% | 100.00% | 12.50% | 62.50% |
| On-topic questions wrongly refused (lower is better) | 1.09% | 0.00% | 0.00% | 8.70% |
| Correct official PDF shown as source | 95.12% | 96.34% | 93.90% | — |
| Response time avg / p95 | 2.94 s / 4.90 s | 2.25 s / 3.14 s | 10.98 s / 20.27 s | 1.10 s / 1.97 s |

## Our document search (live app)

| Metric | Result |
|---|---|
| Correct PDF ranked #1 / top 3 / anywhere in the passages sent to the AI | 95.12% / 97.56% / 97.56% |
| Mean reciprocal rank | 0.9614 |
| Exact page among the passages sent to the AI | 81.71% |
| Document answers marked 🟢 Verified | 32.93% |
| 'Not in the PDFs' questions NOT falsely marked Verified | 100.00% |

## How this test works

- 100 new, very hard questions in 7 groups, each a 4-5 line real-life story with distracting details, the real question buried near the end and often a second part; written before the new system was tested and never used to tune it; every document answer key has an exact quote from the PDF page (machine-checked) and was checked by a separate reviewer.
- Judges for Test 3: Sarvam, Groq and Gemma 4 31B (Google); Gemma replaces the Cloudflare judge so Cloudflare's free units stay for meaning search.
- Three AIs from three companies each answer using our document search; each answer is graded by the other AIs, never by itself, without knowing who wrote it.
- Sarvam alone (same instructions, no documents) shows what our search adds.
- Reproduce: `python3 evaluate_rag.py --set 100 --pipeline v2 --run` then `python3 evaluate_rag.py --set 100 --pipeline v2 --grade`.
