import pickle
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


METADATA_PATH = Path("data/indexes/metadata.pkl")
BM25_PATH = Path("data/indexes/bm25.pkl")


def tokenize(text):
    """
    Convert text into normalized tokens.

    Example:
        "What is PM-KISAN?"
        -> ["what", "is", "pm-kisan"]
    """
    return re.findall(r"\b\w+(?:-\w+)*\b", text.lower())


print("Loading chunks...")

with open(METADATA_PATH, "rb") as f:
    chunks = pickle.load(f)

print("Chunks loaded:", len(chunks))


# Extract text
texts = [chunk["text"] for chunk in chunks]


# Tokenize documents
tokenized_documents = [
    tokenize(text)
    for text in texts
]


print("Building BM25 index...")

bm25 = BM25Okapi(tokenized_documents)

print("BM25 index created!")


# Save BM25 index
with open(BM25_PATH, "wb") as f:
    pickle.dump(bm25, f)

print(f"BM25 index saved to: {BM25_PATH}")