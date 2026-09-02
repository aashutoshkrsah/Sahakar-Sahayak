import string
from pathlib import Path
from pypdf import PdfReader
from deep_translator import GoogleTranslator

DOCUMENTS_PATH = Path(__file__).parent.parent / "data" / "documents"


def load_documents():
    chunks = []

    if not DOCUMENTS_PATH.exists():
        return chunks

    for file in DOCUMENTS_PATH.iterdir():
        if file.suffix.lower() == ".txt":
            try:
                text = file.read_text(encoding="utf-8")
                chunks.append({
                    "document": file.name,
                    "page": 1,
                    "content": text
                })
            except Exception as e:
                print(f"Error reading {file.name}: {e}")

        elif file.suffix.lower() == ".pdf":
            try:
                reader = PdfReader(file)
                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        chunks.append({
                            "document": file.name,
                            "page": idx + 1,
                            "content": page_text
                        })
            except Exception as e:
                print(f"Error reading {file.name}: {e}")

    return chunks


def get_answer(query: str, language: str = "en", intent: str = "general"):
    chunks = load_documents()

    stop_words = {
        "where", "what", "when", "who", "why", "how",
        "is", "the", "a", "an", "are", "was", "were",
        "do", "does", "can", "i", "me", "my", "to", "for",
        "of", "in", "on", "and", "or", "should"
    }

    scheme_acronyms = {"pmksy", "pmkisan", "pm-kisan", "rwbcis", "pmfby", "kcc"}
    generic_terms = {
        "operational", "guidelines", "guideline", "scheme", 
        "schemes", "revised", "official"
    }

    clean_query = query.lower().translate(str.maketrans("", "", string.punctuation))
    query_words = [w for w in clean_query.split() if w not in stop_words]

    best_chunk = None
    best_score = 0

    for chunk in chunks:
        content_lower = chunk["content"].lower()
        doc_name_lower = chunk["document"].lower()
        score = 0

        for word in query_words:
            count = content_lower.count(word)

            if word in scheme_acronyms:
                if word in content_lower:
                    score += 50 + (count * 10)
                if word in doc_name_lower:
                    score += 100
            elif word in generic_terms:
                score += min(count, 2)
            else:
                score += count * 3

        if score > best_score:
            best_score = score
            best_chunk = chunk

    if best_chunk is None or best_score == 0:
        return {
            "answer": "I could not find relevant information.",
            "language": language,
            "sources": [],
            "confidence": 0.0
        }

    confidence = min(best_score / 50.0, 1.0)
    answer_text = best_chunk["content"].strip()

    if len(answer_text) > 1000:
        answer_text = answer_text[:1000] + "..."

    # Force and log translation
    target_lang = str(language).strip().lower() if language else "en"
    print(f"[RAG_SERVICE] Target language passed: '{target_lang}'")

    if target_lang != "en":
        try:
            print(f"[RAG_SERVICE] Translating {len(answer_text)} characters to '{target_lang}'...")
            translated_text = GoogleTranslator(source="auto", target=target_lang).translate(answer_text)
            if translated_text:
                answer_text = translated_text
                print("[RAG_SERVICE] Translation successful!")
            else:
                print("[RAG_SERVICE] Translator returned empty response.")
        except Exception as err:
            print(f"[RAG_SERVICE ERROR] Translation failed: {err}")

    return {
        "answer": answer_text,
        "language": language,
        "sources": [
            {
                "document": best_chunk["document"],
                "page": best_chunk["page"]
            }
        ],
        "confidence": round(confidence, 2)
    }