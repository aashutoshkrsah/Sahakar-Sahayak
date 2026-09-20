import os
import io
import re
import base64
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

print("=======================================================")
print("🧠 SAHAKAAR KIOSK HEURISTIC RAG ENGINE INITIALIZING 🧠")
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

class RogueLLMParser:
    """
    Heavy-duty Python heuristic parser. 
    Mathematically rips apart the LLM's raw text to extract only the final human-readable answer.
    """
    @staticmethod
    def extract_answer(message_obj) -> str:
        if not message_obj:
            return ""
            
        content = getattr(message_obj, 'content', '') or ""
        reasoning = getattr(message_obj, 'reasoning_content', '') or ""
        text = f"{reasoning}\n{content}".strip()

        # 1. Universal Bracket Ripper (Destroys <think>, <ಆಲೋಚನೆ>, and anything else in brackets)
        text = re.sub(r'<[^>]+>.*?</[^>]+>', '', text, flags=re.DOTALL)
        # Catch any stray, unclosed tags that got left behind
        text = re.sub(r'<[^>]+>', '', text)

        # 2. Hallucination Eraser (Destroys prompt echoes and placeholders)
        hallucinations = [
            r"Let me reconsider.*?\n",
            r"The user hasn't asked.*?\n",
            r"Base your answer purely on.*?\n",
            r"\(Write your final, concise answer.*?\)",
            r"Answer:",
            r"```.*?```"
        ]
        for h in hallucinations:
            text = re.sub(h, '', text, flags=re.IGNORECASE | re.DOTALL)

        # 3. Bottom-Up Mathematical Slicer
        # If the text is still a massive wall of reasoning, we slice it into blocks.
        # We only keep the last 2 blocks (which is always the final answer).
        blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
        if len(blocks) > 2:
            text = "\n\n".join(blocks[-2:])

        return text.strip()


def normalize_query_to_english(raw_query: str) -> str:
    if not raw_query or not raw_query.strip():
        return ""

    if client is None:
        return _apply_lexicon_fallback(raw_query)

    print(f"\n[SARVAM LOG] 🔄 Normalizing Query: '{raw_query}'")
    
    try:
        normalization_prompt = (
            "Extract the main agricultural topic into 3 English search keywords.\n"
            "If the query is about sports, movies, or non-agriculture topics, output the exact word: OUT_OF_DOMAIN\n"
            f"Query: {raw_query}\n"
            "Keywords:"
        )

        response = client.chat.completions(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": normalization_prompt}],
            temperature=0.1
        )

        message_obj = response.choices[0].message if response.choices else None
        
        # Route through the Heuristic Parser
        clean_content = RogueLLMParser.extract_answer(message_obj)
        
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

    lang_map = {
        "kn": "Kannada",
        "hi": "Hindi",
        "en": "English"
    }
    target_lang = lang_map.get(language, "English")

    # Bare-bones prompt. We are not giving it formatting rules to panic over. 
    # We let it speak, and we let the Python parser rip out the trash.
    master_prompt = (
        f"You are Sahakar Sahayak, answering a farmer's question naturally in {target_lang}.\n"
        "1. Base your answer entirely on the Context provided below. If Context is empty, give general farming advice.\n"
        "2. If the user asks about cricket, movies, politics, or non-farming topics, reply ONLY with: 'I can only assist with agriculture and farming schemes.'\n\n"
        f"Context:\n{context_block if context_block else 'None'}\n\n"
        f"Farmer Query: {query}\n"
    )

    try:
        print(f"\n[SARVAM LOG] 🧠 Executing Master Synthesis for '{language}'")
        
        response = client.chat.completions(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": master_prompt}],
            temperature=0.3
        )

        message_obj = response.choices[0].message if response.choices else None
        
        # 🚀 ROUTE THROUGH THE HEURISTIC PARSER 🚀
        clean_content = RogueLLMParser.extract_answer(message_obj)
        print(f"[SARVAM LOG] 🔍 Final extracted length: {len(clean_content)}")
        
        if clean_content:
            answer_text = clean_content
        else:
            answer_text = "I apologize, but I could not synthesize an answer at this moment. Please try asking again."

        print("[SARVAM LOG] ✅ Answer Synthesis Completed.")

        is_refusal = "can only assist with agriculture" in answer_text.lower() or "out_of_domain" in answer_text.lower()
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