from pathlib import Path
import pickle
import re

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from app.rag.embeddings import BGEEmbeddings


# -----------------------------
# Paths
# -----------------------------

INDEX_PATH = Path("data/indexes/faiss.index")
METADATA_PATH = Path("data/indexes/metadata.pkl")
BM25_PATH = Path("data/indexes/bm25.pkl")


# -----------------------------
# Tokenizer
# -----------------------------

def tokenize(text):
    """
    Normalize text into tokens.

    Keeps hyphenated terms such as:
        PM-KISAN
        PMFBY
        crop-insurance

    Example:
        "What is PM-KISAN?"
        -> ["what", "is", "pm-kisan"]
    """

    return re.findall(
        r"\b\w+(?:-\w+)*\b",
        text.lower()
    )


# -----------------------------
# Load FAISS
# -----------------------------

print("Loading FAISS index...")

faiss_index = faiss.read_index(
    str(INDEX_PATH)
)

print(
    "FAISS vectors:",
    faiss_index.ntotal
)


# -----------------------------
# Load metadata
# -----------------------------

print("Loading metadata...")

with open(
    METADATA_PATH,
    "rb"
) as f:

    chunks = pickle.load(f)


print(
    "Metadata chunks:",
    len(chunks)
)


# -----------------------------
# Load BM25
# -----------------------------

print("Loading BM25 index...")

with open(
    BM25_PATH,
    "rb"
) as f:

    bm25 = pickle.load(f)


print("BM25 loaded!")


# -----------------------------
# Load BGE-M3
# -----------------------------

print("Loading BGE-M3...")

embedding_model = BGEEmbeddings()


# -----------------------------
# FAISS Search
# -----------------------------

def faiss_search(query, top_k=5):

    # Generate query embedding
    query_vector = embedding_model.embed_query(
        query
    )

    # Convert to float32 numpy array
    query_vector = np.asarray(
        query_vector,
        dtype="float32"
    ).reshape(1, -1)

    # Normalize for cosine similarity
    faiss.normalize_L2(
        query_vector
    )

    # Search FAISS
    scores, indices = faiss_index.search(
        query_vector,
        top_k
    )

    results = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx == -1:
            continue

        results.append({

            "index": int(idx),

            "faiss_score": float(score),

            "text": chunks[idx]["text"],

            "source": chunks[idx].get(
                "source"
            ),

            "page": chunks[idx].get(
                "page"
            )
        })

    return results


# -----------------------------
# BM25 Search
# -----------------------------

def bm25_search(query, top_k=5):

    # IMPORTANT:
    # Use the same tokenizer that was
    # used when creating bm25.pkl.

    tokenized_query = tokenize(query)

    # Get BM25 scores
    scores = bm25.get_scores(
        tokenized_query
    )

    # Get highest scoring documents
    top_indices = np.argsort(
        scores
    )[::-1][:top_k]

    results = []

    for idx in top_indices:

        results.append({

            "index": int(idx),

            "bm25_score": float(
                scores[idx]
            ),

            "text": chunks[idx]["text"],

            "source": chunks[idx].get(
                "source"
            ),

            "page": chunks[idx].get(
                "page"
            )
        })

    return results


# -----------------------------
# Hybrid Search
# -----------------------------

def hybrid_search(
    query,
    top_k=5
):

    # -------------------------
    # FAISS results
    # -------------------------

    faiss_results = faiss_search(
        query,
        top_k=top_k
    )


    # -------------------------
    # BM25 results
    # -------------------------

    bm25_results = bm25_search(
        query,
        top_k=top_k
    )


    # -------------------------
    # Combine results
    # -------------------------

    combined = {}


    # -------------------------
    # Add FAISS results
    # -------------------------

    for rank, result in enumerate(
        faiss_results
    ):

        idx = result["index"]

        combined.setdefault(
            idx,
            {
                "index": idx,

                "text": result["text"],

                "source": result["source"],

                "page": result["page"],

                "faiss_score": 0.0,

                "bm25_score": 0.0,

                "hybrid_score": 0.0
            }
        )


        combined[idx][
            "faiss_score"
        ] = result["faiss_score"]


        # Reciprocal Rank Fusion
        combined[idx][
            "hybrid_score"
        ] += (
            1 / (60 + rank + 1)
        )


    # -------------------------
    # Add BM25 results
    # -------------------------

    for rank, result in enumerate(
        bm25_results
    ):

        idx = result["index"]

        combined.setdefault(
            idx,
            {
                "index": idx,

                "text": result["text"],

                "source": result["source"],

                "page": result["page"],

                "faiss_score": 0.0,

                "bm25_score": 0.0,

                "hybrid_score": 0.0
            }
        )


        combined[idx][
            "bm25_score"
        ] = result["bm25_score"]


        # Reciprocal Rank Fusion
        combined[idx][
            "hybrid_score"
        ] += (
            1 / (60 + rank + 1)
        )


    # -------------------------
    # Sort by hybrid score
    # -------------------------

    results = sorted(
        combined.values(),
        key=lambda x: x[
            "hybrid_score"
        ],
        reverse=True
    )


    return results[:top_k]


# -----------------------------
# Test
# -----------------------------

if __name__ == "__main__":

    query = "What is PM-KISAN?"


    print(
        "\n=============================="
    )

    print(
        "QUERY:",
        query
    )

    print(
        "=============================="
    )


    # Show query tokens
    print(
        "\nQuery tokens:"
    )

    print(
        tokenize(query)
    )


    # Run hybrid search
    results = hybrid_search(
        query,
        top_k=5
    )


    # Display results
    for i, result in enumerate(
        results,
        1
    ):

        print(
            f"\n--- Result {i} ---"
        )


        print(
            "Hybrid score:",
            result["hybrid_score"]
        )


        print(
            "FAISS score:",
            result["faiss_score"]
        )


        print(
            "BM25 score:",
            result["bm25_score"]
        )


        print(
            "Source:",
            result["source"]
        )


        print(
            "Page:",
            result["page"]
        )


        print("Text:")

        print(
            result["text"][:1000]
        )