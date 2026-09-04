import string
import numpy as np
import faiss
from pathlib import Path
from pypdf import PdfReader
from deep_translator import GoogleTranslator
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

DOCUMENTS_PATH = Path(__file__).parent.parent / "data" / "documents"

INDEX_CACHE = {
    "chunks": [],
    "bm25": None,
    "faiss_index": None,
    "embed_model": None
}


def load_and_chunk_documents(chunk_size=300, overlap=50):
    """Loads PDFs/TXTs and splits them into granular semantic chunks."""
    chunks = []
    if not DOCUMENTS_PATH.exists():
        return chunks

    for file in DOCUMENTS_PATH.iterdir():
        raw_text_blocks = []

        if file.suffix.lower() == ".txt":
            try:
                text = file.read_text(encoding="utf-8")
                raw_text_blocks.append((1, text))
            except Exception as e:
                print(f"Error reading {file.name}: {e}")

        elif file.suffix.lower() == ".pdf":
            try:
                reader = PdfReader(file)
                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        raw_text_blocks.append((idx + 1, page_text.strip()))
            except Exception as e:
                print(f"Error reading {file.name}: {e}")

        # Chunk text into overlapping passages
        for page_num, text in raw_text_blocks:
            words = text.split()
            for i in range(0, len(words), chunk_size - overlap):
                chunk_text = " ".join(words[i : i + chunk_size])
                if len(chunk_text.strip()) > 40:
                    chunks.append({
                        "document": file.name,
                        "page": page_num,
                        "content": chunk_text
                    })

    return chunks


def initialize_hybrid_index():
    """Builds and caches BM25 keyword and FAISS vector indices."""
    if INDEX_CACHE["bm25"] is not None and INDEX_CACHE["faiss_index"] is not None:
        return

    print("[HYBRID RAG] Initializing BM25 & FAISS Indices...")
    chunks = load_and_chunk_documents()
    INDEX_CACHE["chunks"] = chunks

    if not chunks:
        print("[HYBRID RAG WARNING] No document chunks found.")
        return

    # 1. BM25 Tokenization
    tokenized_corpus = [
        chunk["content"].lower().translate(str.maketrans("", "", string.punctuation)).split()
        for chunk in chunks
    ]
    INDEX_CACHE["bm25"] = BM25Okapi(tokenized_corpus)

    # 2. FAISS Vector Embedding Index
    model = SentenceTransformer("all-MiniLM-L6-v2")
    INDEX_CACHE["embed_model"] = model

    contents = [c["content"] for c in chunks]
    embeddings = model.encode(contents, convert_to_numpy=True, show_progress_bar=False)

    faiss.normalize_L2(embeddings)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    INDEX_CACHE["faiss_index"] = index

    print(f"[HYBRID RAG SUCCESS] Indexed {len(chunks)} chunks across uploaded documents.")


def is_non_ascii(text: str) -> bool:
    """Detects presence of regional script characters (e.g., Kannada or Hindi)."""
    return any(ord(char) > 127 for char in text)


def get_answer(query: str, language: str = "en", intent: str = "general"):
    target_lang = str(language).strip().lower() if language else "en"

    # Auto-detect target language script if query contains non-ASCII characters
    if target_lang == "en" and is_non_ascii(query):
        # Kannada unicode block range check
        if any('\u0C80' <= c <= '\u0CFF' for c in query):
            target_lang = "kn"
        # Devanagari (Hindi) unicode block range check
        elif any('\u0900' <= c <= '\u097F' for c in query):
            target_lang = "hi"

    # Step 1: Translate non-English incoming queries into English for document lookup
    search_query = query
    if target_lang != "en" or is_non_ascii(query):
        try:
            translated = GoogleTranslator(source="auto", target="en").translate(query)
            if translated:
                search_query = translated
                print(f"[RAG_SERVICE] Translated query to English: '{search_query}'")
        except Exception as err:
            print(f"[RAG_SERVICE ERROR] Input translation failed: {err}")

    initialize_hybrid_index()
    chunks = INDEX_CACHE["chunks"]

    if not chunks:
        return {
            "answer": "I could not find relevant information.",
            "language": target_lang,
            "sources": [],
            "confidence": 0.0
        }

    # Step 2: BM25 Keyword Search
    tokenized_query = search_query.lower().translate(str.maketrans("", "", string.punctuation)).split()
    bm25_scores = INDEX_CACHE["bm25"].get_scores(tokenized_query)
    top_bm25_indices = np.argsort(bm25_scores)[::-1][:10]

    # Step 3: FAISS Vector Search
    query_vector = INDEX_CACHE["embed_model"].encode([search_query], convert_to_numpy=True)
    faiss.normalize_L2(query_vector)
    _, top_faiss_indices = INDEX_CACHE["faiss_index"].search(query_vector, 10)
    top_faiss_indices = top_faiss_indices[0]

    # Step 4: Reciprocal Rank Fusion (RRF) Scoring
    rrf_scores = {}
    k = 60

    for rank, idx in enumerate(top_bm25_indices):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + (1.0 / (k + rank + 1))

    for rank, idx in enumerate(top_faiss_indices):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + (1.0 / (k + rank + 1))

    best_chunk_idx = max(rrf_scores, key=rrf_scores.get)
    raw_rrf = rrf_scores[best_chunk_idx]

    confidence = min(raw_rrf * 25.0, 0.95)

    # Step 5: Strict Threshold Check (Filters Out-of-Domain Queries)
    if confidence < 0.60 or bm25_scores[best_chunk_idx] == 0:
        return {
            "answer": "I could not find relevant information.",
            "language": target_lang,
            "sources": [],
            "confidence": 0.0
        }

    answer_text = chunks[best_chunk_idx]["content"].strip()

    # Step 6: Translate Answer Back to Target Language
    if target_lang != "en":
        try:
            translated_answer = GoogleTranslator(source="auto", target=target_lang).translate(answer_text)
            if translated_answer:
                answer_text = translated_answer
        except Exception as err:
            print(f"[RAG_SERVICE ERROR] Output translation failed: {err}")

    return {
        "answer": answer_text,
        "language": target_lang,
        "sources": [
            {
                "document": chunks[best_chunk_idx]["document"],
                "page": chunks[best_chunk_idx]["page"]
            }
        ],
        "confidence": round(confidence, 2)
    }