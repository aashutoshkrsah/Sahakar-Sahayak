# Sahakar Sahayak — Test 2: 200 brand-new questions (3 AIs grade each other)

Generated 2026-09-30 00:09 · 200 questions · each answer graded by the AIs that did NOT write it · two judges agree on 76.86% of 458 double-graded answers

## Headline

| | Sarvam + docs | Groq + docs | Cloudflare + docs | Sarvam alone |
|---|---|---|---|---|
| **Score** | **62.00%** | **58.25%** | **62.75%** | **26.50%** |
| Fully correct answers | 52.00% | 47.50% | 43.50% | 20.50% |
| Judged by | Groq · gpt-oss-20b + Cloudflare · Llama 3.3 70B | Sarvam · sarvam-105b + Cloudflare · Llama 3.3 70B | Sarvam · sarvam-105b + Groq · gpt-oss-20b | Groq · gpt-oss-20b + Cloudflare · Llama 3.3 70B |
| Answered / graded | 200 / 200 | 200 / 200 | 200 / 200 | 200 / 200 |
| Score from Sarvam · sarvam-105b | — | 56.00% | 59.50% | — |
| Score from Groq · gpt-oss-20b | 64.07% | — | 66.33% | 26.88% |
| Score from Cloudflare · Llama 3.3 70B | 49.43% | 54.60% | — | 10.92% |

## In plain words

- With our document search, Sarvam's answers were 62% correct; the same Sarvam without our search managed only 26%.
- Our search helps every AI we tried: Groq 58%, Cloudflare 63%, all far above Sarvam alone (26%).
- The app is strongest at off-topic & rule-breaking tricks (100%), and weakest at on-topic but not in the pdfs (40%) -- our next thing to improve.
- Our search found the correct official PDF for 87% of the document questions.
- Two different judges gave the same grade 77% of the time, so the grading is consistent.

**What our document search adds to Sarvam:** 26.88% → 64.07% (**+37.19 points**, same judge: Groq · gpt-oss-20b)

## By question type

| | Sarvam + docs | Groq + docs | Cloudflare + docs | Sarvam alone |
|---|---|---|---|---|
| Facts from the PDFs | 48.64% | 48.18% | 57.27% | 11.82% |
| Answers with several cases | 65.00% | 52.86% | 54.29% | 11.43% |
| Hindi / Kannada / Nepali / Hinglish / typos | 68.75% | 62.50% | 66.25% | 13.75% |
| Reply in the chosen language | 60.00% | 60.00% | 55.00% | 5.00% |
| Wrong assumption must be corrected | 72.00% | 66.00% | 66.00% | 42.00% |
| On-topic but not in the PDFs | 40.00% | 45.00% | 57.50% | 57.50% |
| Off-topic & rule-breaking tricks | 100.00% | 100.00% | 100.00% | 96.67% |

## By language

| | Sarvam + docs | Groq + docs | Cloudflare + docs | Sarvam alone |
|---|---|---|---|---|
| English | 60.84% | 57.69% | 62.76% | 26.57% |
| Hindi | 73.81% | 66.67% | 73.81% | 26.19% |
| Kannada | 52.38% | 52.38% | 47.62% | 23.81% |
| Nepali | 70.00% | 60.00% | 68.33% | 30.00% |

## Automatic checks (no AI judge)

| | Sarvam + docs | Groq + docs | Cloudflare + docs | Sarvam alone |
|---|---|---|---|---|
| Key fact present (numbers / English facts) | 57.58% | 52.73% | 60.00% | 12.73% |
| Answer in the chosen language's script | 100.00% | 100.00% | 100.00% | 96.00% |
| Off-topic questions refused | 80.00% | 100.00% | 80.00% | 86.67% |
| On-topic questions wrongly refused (lower is better) | 0.54% | 0.00% | 0.00% | 8.65% |
| Correct official PDF shown as source | 78.18% | 81.21% | 78.18% | — |
| Response time avg / p95 | 1.21 s / 1.83 s | 1.58 s / 2.66 s | 6.03 s / 13.65 s | 0.67 s / 1.15 s |

## Our document search (live app)

| Metric | Result |
|---|---|
| Correct PDF ranked #1 / top 3 / top 6 | 78.18% / 84.24% / 86.67% |
| Mean reciprocal rank | 0.8151 |
| Exact page among the 6 passages | 70.30% |
| Document answers marked 🟢 Verified | 16.36% |
| 'Not in the PDFs' questions NOT falsely marked Verified | 100.00% |

## How this test works

- 200 brand-new, very hard questions in 7 groups, written after Test 1 and never seen by the app; every document answer key has an exact quote from the PDF page (machine-checked) and was checked by a separate reviewer.
- Three AIs from three companies each answer using our document search; each answer is graded by the other AIs, never by itself, without knowing who wrote it.
- Sarvam alone (same instructions, no documents) shows what our search adds.
- Reproduce: `python3 evaluate_rag.py --set 200 --run` then `python3 evaluate_rag.py --set 200 --grade`.
