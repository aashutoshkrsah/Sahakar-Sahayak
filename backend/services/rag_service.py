import string
from pathlib import Path


DOCUMENTS_PATH = Path(__file__).parent.parent / "data" / "documents"


def load_documents():
    documents = []

    for file in DOCUMENTS_PATH.glob("*.txt"):
        text = file.read_text(encoding="utf-8")

        documents.append({
            "document": file.name,
            "content": text
        })

    print("DOCUMENTS LOADED:")
    for doc in documents:
        print(doc["document"])

    return documents


def get_answer(query: str, language: str, intent: str):

    documents = load_documents()

    stop_words = {
        "where", "what", "when", "who", "why", "how",
        "is", "the", "a", "an", "are", "was", "were",
        "do", "does", "can", "i", "me", "my", "to", "for",
        "of", "in", "on", "and", "or", "should"
    }

    query_words = [
        word.strip(string.punctuation).lower()
        for word in query.split()
        if word.strip(string.punctuation).lower() not in stop_words
    ]

    best_document = None
    best_score = 0

    for doc in documents:

        content = doc["content"].lower()

        score = 0

        for word in query_words:
            if word in content:
                score += 1

        if score > best_score:
            best_score = score
            best_document = doc

    # No relevant document found
    if best_document is None or best_score == 0:
        return {
            "answer": "I could not find relevant information.",
            "language": language,
            "sources": [],
            "confidence": 0.0
        }

    # Avoid division by zero
    if len(query_words) == 0:
        confidence = 0.0
    else:
        confidence = min(
            best_score / len(query_words),
            1.0
        )

    return {
        "answer": best_document["content"],
        "language": language,
        "sources": [
            {
                "document": best_document["document"],
                "page": None
            }
        ],
        "confidence": round(confidence, 2)
    }