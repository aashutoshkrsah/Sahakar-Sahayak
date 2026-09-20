import os
import io
import re
import base64
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

print("=======================================================")
print("🧠 ENTERPRISE MULTI-STAGE RAG ENGINE INITIALIZING 🧠")
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
    r"\b(samiti|cooperative|society|pacs|dairy|sahakar|sangh)\b": "PACS Primary Agricultural Credit Societies Cooperative Governance"
}

def clean_ai_text(message_obj) -> str:
    """
    The Untranslatable Delimiter Extractor.
    Bypasses the LLM Tag Translation Bug by using pure symbols (@@@).
    """
    if not message_obj:
        return ""
        
    content_str = getattr(message_obj, 'content', '') or ""
    reasoning_str = getattr(message_obj, 'reasoning_content', '') or ""
    
    raw_text = f"{reasoning_str}\n{content_str}".strip()
    
    # 1. The Indestructible Split (Looks for @@@)
    if "@@@" in raw_text:
        parts = raw_text.split("@@@")
        if len(parts) >= 3:
            return parts[1].strip()  # Grabs everything safely inside @@@ and @@@
        if len(parts) == 2:
            return parts[1].strip()  # Grabs everything after the first @@@
            
    # 2. The Universal Tag Destroyer (Fallback)
    # If the AI hallucinates translated tags like <ಅಂತಿಮ_ಉತ್ತರ>, this regex 
    # aggressively deletes ANY text trapped inside < and >, leaving only the pure answer.
    clean_text = re.sub(r'<[^>]+>', '', raw_text).strip()
    
    return clean_text


def normalize_query_to_english(raw_query: str) -> str:
    if not raw_query or not raw_query.strip():
        return ""

    if client is None:
        return _apply_lexicon_fallback(raw_query)

    print(f"\n[SARVAM LOG] 🔄 Disambiguating Query: '{raw_query}'")
    
    try:
        normalization_prompt = (
            "Extract the core agricultural intent from the user's mixed-language text.\n"
            "Map informal scheme names to official acronyms (e.g., 'kishan' -> 'PM-KISAN').\n"
            "Output a space-separated list of clean English search keywords optimized for BM25.\n"
            "If the query is completely unrelated to agriculture, output 'OUT_OF_DOMAIN'.\n\n"
            "CRITICAL INSTRUCTION:\n"
            "You MUST place your final English keywords between three at-signs (@@@). Place nothing else inside them.\n\n"
            f"User Input: {raw_query}\n\n"
            "Output Format:\n"
            "@@@\n(keywords here)\n@@@"
        )

        response = client.chat.completions(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": normalization_prompt}],
            temperature=0.1
        )

        message_obj = response.choices[0].message if response.choices else None
        clean_content = clean_ai_text(message_obj)
        
        cleaned_search_terms = clean_content if clean_content else _apply_lexicon_fallback(raw_query)
        lexicon_boost = _apply_lexicon_fallback(raw_query)
        final_search_query = f"{cleaned_search_terms} {lexicon_boost}".strip()

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
    retrieved_docs: list = None
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
                    "link": link_url
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
            "qr_code_base64": None
        }

    lang_instructions = {
        "kn": "Respond strictly in clear, respectful Kannada (ಕನ್ನಡ).",
        "hi": "Respond strictly in clear, respectful Hindi (हिंदी).",
        "en": "Respond strictly in clear, professional English."
    }
    target_lang_instruction = lang_instructions.get(language, "Respond in clear English.")

    master_prompt = (
        "You are Sahakar Sahayak, an official digital assistant for Indian farmers.\n"
        f"{target_lang_instruction}\n\n"
        "GUIDELINES:\n"
        "1. Answer ONLY agricultural questions and cite the provided context.\n"
        "2. If Context is empty, provide general agricultural guidance politely.\n"
        "3. Refuse non-agricultural questions.\n\n"
        "CRITICAL INSTRUCTION:\n"
        "You may think step-by-step. However, your final spoken answer MUST be placed exactly between three at-signs (@@@).\n"
        "Do NOT translate the @@@ symbols. Ensure the text inside is concise for Text-to-Speech playback.\n\n"
        f"Context:\n{context_block if context_block else 'None'}\n\n"
        f"Farmer Query: {query}\n\n"
        "Response Format:\n"
        "@@@\n(Your final answer here)\n@@@"
    )

    try:
        print(f"\n[SARVAM LOG] 🧠 Executing Master Synthesis for '{language}'")
        
        response = client.chat.completions(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": master_prompt}],
            temperature=0.3
        )

        message_obj = response.choices[0].message if response.choices else None
        
        # Extract via the Untranslatable Delimiter
        clean_content = clean_ai_text(message_obj)
        print(f"[SARVAM LOG] 🔍 Final extracted length: {len(clean_content)}")
        
        if clean_content:
            answer_text = clean_content
        else:
            answer_text = "I apologize, but I could not synthesize an answer at this moment. Please try asking again."

        print("[SARVAM LOG] ✅ Answer Synthesis Completed.")

        is_refusal = "I am Sahakar Sahayak" in answer_text
        has_documents = len(sources) > 0 and context_block

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
            "qr_code_base64": qr_code_base64
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
            "qr_code_base64": None
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