import os
import io
import re
import base64
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

print("=======================================================")
print("🧠 SAHAKAAR KIOSK RAG ENGINE INITIALIZING 🧠")
print("=======================================================")

try:
    from sarvamai import SarvamAI
    api_key = os.getenv("SARVAM_API_KEY", "").strip()
    client = SarvamAI(api_subscription_key=api_key) if api_key else None

    MODEL_NAME = "sarvam-105b"
    if client:
        print(f"[SARVAM LOG] ✅ Engine Online: Model '{MODEL_NAME}' connected.")
except Exception as e:
    print(f"[SARVAM LOG] ❌ FATAL INIT ERROR: {e}")
    client = None
    MODEL_NAME = None

OFFICIAL_SCHEME_LEXICON = {
    r"\b(kishan|kisan|samman|nidhi|2000|6000|hafta|kist|modi paisa)\b": "PM-KISAN Pradhan Mantri Kisan Samman Nidhi",
    r"\b(bima|fasal bima|crop insurance|sukha|baadh|nuksan|claim)\b": "PMFBY Pradhan Mantri Fasal Bima Yojana crop insurance",
    r"\b(credit card|kcc|loan|karj|kisaan card|pashupalan loan)\b": "KCC Kisan Credit Card agricultural credit loan",
    r"\b(soil card|mitti|urvarak|fertilizer|khad|dap|urea)\b": "Soil Health Card Scheme nutrient management",
    r"\b(sinchai|irrigation|paani|drip|sprinkler|borewell)\b": "PMKSY Pradhan Mantri Krishi Sinchayee Yojana irrigation",
    r"\b(mandi|enam|e-nam|bhav|bechna|msp|rate)\b": "e-NAM National Agriculture Market MSP procurement",
    r"\b(samiti|cooperative|society|pacs|dairy|sahakar|sangh)\b": "PACS Primary Agricultural Credit Societies Cooperative Governance",
}

# Extend this as your frontend's language dropdown grows. Keys must match
# whatever `language` code the frontend sends. Sarvam supports all of these.
LANG_MAP = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "or": "Odia",
}


def _clean_model_text(message_obj) -> str:
    """
    Return ONLY the final answer from a Sarvam chat message.

    Sarvam puts chain-of-thought in a SEPARATE `reasoning_content` field on
    the message object -- it never mixes it into `content`. We simply never
    read `reasoning_content`, so there is nothing to "un-mix" after the
    fact. That merge-then-guess step is what was leaking reasoning text
    into your answers before. We also call the API with
    reasoning_effort=None (below), so reasoning_content won't even be
    populated.

    The regex here is only a defensive net in case a model/SDK version
    ever inlines a <think> block directly into `content`.
    """
    if not message_obj:
        return ""
    content = (getattr(message_obj, "content", "") or "").strip()
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
    return content


def normalize_query_to_english(raw_query: str) -> str:
    if not raw_query or not raw_query.strip():
        return ""

    if client is None:
        return _apply_lexicon_fallback(raw_query)

    print(f"\n[SARVAM LOG] 🔄 Normalizing Query: '{raw_query}'")

    try:
        response = client.chat.completions(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract the main agricultural topic from the user's message "
                        "into 3 concise English search keywords. If the message is "
                        "about sports, movies, politics, or anything unrelated to "
                        "agriculture or farming, reply with exactly: OUT_OF_DOMAIN. "
                        "Reply with ONLY the keywords (or OUT_OF_DOMAIN) -- no "
                        "preamble, no explanation, no punctuation."
                    ),
                },
                {"role": "user", "content": raw_query},
            ],
            temperature=0.1,
            max_tokens=60,
            reasoning_effort=None,  # keyword extraction needs zero "thinking"
        )

        message_obj = response.choices[0].message if response.choices else None
        cleaned_search_terms = _clean_model_text(message_obj)

        lexicon_boost = _apply_lexicon_fallback(raw_query)
        final_search_query = f"{cleaned_search_terms} {lexicon_boost}".strip()
        final_search_query = final_search_query or raw_query

        print(f"[SARVAM LOG] ✅ Search Keywords: '{final_search_query}'")
        return final_search_query

    except Exception as e:
        print(f"[SARVAM LOG] ❌ Normalization failed: {e}")
        return _apply_lexicon_fallback(raw_query)


def _apply_lexicon_fallback(text: str) -> str:
    boosters = []
    for pattern, official_term in OFFICIAL_SCHEME_LEXICON.items():
        if re.search(pattern, text.lower(), re.IGNORECASE):
            boosters.append(official_term)
    return " ".join(boosters) if boosters else text


def get_answer(
    query: str,
    language: str = "en",
    intent: str = "general",
    retrieved_docs: list = None,
) -> dict:
    sources = []
    context_chunks = []
    seen_texts = set()

    if retrieved_docs:
        for doc in retrieved_docs:
            doc_name = doc.get("document", doc.get("source_doc", "Official_Document.pdf"))
            raw_page = doc.get("page", doc.get("source_page", None))
            text_chunk = doc.get("text", "").strip()

            if not text_chunk or text_chunk in seen_texts:
                continue
            seen_texts.add(text_chunk)

            try:
                page_val = int(raw_page)
            except (ValueError, TypeError):
                page_val = None

            context_chunks.append(
                f"[Document: {doc_name} | Page: {page_val if page_val is not None else 'General'}]\n{text_chunk}"
            )

            if doc_name not in [s["document"] for s in sources]:
                link_url = f"/documents/{urllib.parse.quote(doc_name)}"
                if page_val is not None:
                    link_url += f"#page={page_val}"

                sources.append({
                    "document": doc_name,
                    "page": page_val,
                    "link": link_url,
                })

    context_block = "\n\n---\n\n".join(context_chunks[:5])

    if client is None:
        return {
            "answer": "AI Error: SARVAM_API_KEY is missing.",
            "language": language,
            "intent": intent,
            "sources": sources,
            "confidence": 0.0,
            "action_url": None,
            "qr_code_base64": None,
        }

    target_lang = LANG_MAP.get(language, "English")

    system_prompt = (
        f"You are Sahakar Sahayak, a farmer-assistance chatbot. Always reply "
        f"naturally in {target_lang}, in plain prose -- no headers, no markdown, "
        f"no meta-commentary about what you are doing.\n"
        "Rules:\n"
        "1. Base your answer entirely on the Context below when it is relevant. "
        "If the Context is empty or not relevant to the question, answer from "
        "general farming knowledge instead.\n"
        "2. If the farmer's question is about cricket, movies, politics, or any "
        "non-farming topic, reply with ONLY this sentence, translated into "
        f"{target_lang}: 'I can only assist with agriculture and farming schemes.'\n"
        "3. Never show your reasoning, thinking, or notes -- output only the "
        "final answer meant for the farmer to read."
    )

    user_prompt = f"Context:\n{context_block if context_block else 'None'}\n\nFarmer Query: {query}"

    try:
        print(f"\n[SARVAM LOG] 🧠 Executing Master Synthesis for '{language}'")

        response = client.chat.completions(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
            reasoning_effort=None,  # closed-book extraction + translation --
                                    # keep the whole token budget for the
                                    # actual answer, not chain-of-thought
        )

        message_obj = response.choices[0].message if response.choices else None
        answer_text = _clean_model_text(message_obj)
        print(f"[SARVAM LOG] 🔍 Final extracted length: {len(answer_text)}")

        if not answer_text:
            answer_text = "I apologize, but I could not synthesize an answer at this moment. Please try asking again."

        print("[SARVAM LOG] ✅ Answer Synthesis Completed.")

        is_refusal = "can only assist with agriculture" in answer_text.lower() or "out_of_domain" in answer_text.lower()
        has_documents = len(sources) > 0 and bool(context_block)

        if is_refusal:
            sources = []
            confidence = 0.0
        elif has_documents:
            confidence = 0.98
        else:
            sources = []
            confidence = 0.85

        action_url, qr_code_base64 = _generate_share_qr(query, answer_text, sources, confidence)

        return {
            "answer": answer_text,
            "language": language,
            "intent": intent,
            "sources": sources,
            "confidence": confidence,
            "action_url": action_url,
            "qr_code_base64": qr_code_base64,
        }

    except Exception as e:
        print(f"[SARVAM LOG] ❌ Master Synthesis Exception: {str(e)}")
        return {
            "answer": f"System Notice: We experienced an issue communicating with the reasoning engine ({str(e)}). Please try again.",
            "language": language,
            "intent": intent,
            "sources": sources,
            "confidence": 0.0,
            "action_url": None,
            "qr_code_base64": None,
        }


def _generate_share_qr(query: str, answer: str, sources: list, confidence: float):
    if confidence <= 0.0:
        return None, None

    try:
        primary_doc = sources[0]["document"] if sources else "General Guidelines"
        clean_excerpt = answer[:600].replace("\n", " ").strip()
        if len(answer) > 600:
            clean_excerpt += "..."

        share_text = f"🌾 *Sahakar Sahayak Receipt*\n\n*Query:* {query}\n\n*Guidance:* {clean_excerpt}\n\n*Source:* {primary_doc}"
        encoded_message = urllib.parse.quote(share_text)
        action_url = f"https://wa.me/?text={encoded_message}"

        import qrcode
        qr = qrcode.QRCode(version=None, box_size=4, border=2)
        qr.add_data(action_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return action_url, qr_code_base64
    except Exception as e:
        print(f"[RAG QR LOG] ⚠️ QR generation bypassed: {e}")
        return None, None