from pathlib import Path
import pickle

import faiss
import numpy as np

from app.rag.embeddings import BGEEmbeddings


# Paths
INDEX_PATH = Path("data/indexes/faiss.index")
METADATA_PATH = Path("data/indexes/metadata.pkl")


print("Loading FAISS index...")
index = faiss.read_index(str(INDEX_PATH))

print("FAISS vectors:", index.ntotal)


print("Loading metadata...")

with open(METADATA_PATH, "rb") as f:
    chunks = pickle.load(f)

print("Metadata chunks:", len(chunks))


print("Loading BGE-M3...")
embedding_model = BGEEmbeddings()


def search(query: str, top_k: int = 5):

    # Convert query into embedding
    query_vector = embedding_model.embed_query(query)

    query_vector = np.asarray(
        query_vector,
        dtype="float32"
    ).reshape(1, -1)

    # Normalize for cosine similarity
    faiss.normalize_L2(query_vector)

    # Search FAISS
    scores, indices = index.search(query_vector, top_k)

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        chunk = chunks[idx]

        results.append({
            "score": float(score),
            "text": chunk["text"],
            "source": chunk.get("source"),
            "page": chunk.get("page")
        })

    return results


if __name__ == "__main__":

    query = "What is PM-KISAN?"

    print("\nQuery:", query)

    results = search(query, top_k=5)

    print("\n===== SEARCH RESULTS =====")

    for i, result in enumerate(results, 1):

        print(f"\n--- Result {i} ---")
        print("Score:", result["score"])
        print("Source:", result["source"])
        print("Page:", result["page"])
        print("Text:")
        print(result["text"][:1000])