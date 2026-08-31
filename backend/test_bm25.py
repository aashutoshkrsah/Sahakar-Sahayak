import pickle
import re

from pathlib import Path


METADATA_PATH = Path("data/indexes/metadata.pkl")
BM25_PATH = Path("data/indexes/bm25.pkl")


def tokenize(text):
    return re.findall(r"\b\w+(?:-\w+)*\b", text.lower())


# Load chunks
with open(METADATA_PATH, "rb") as f:
    chunks = pickle.load(f)


# Load BM25
with open(BM25_PATH, "rb") as f:
    bm25 = pickle.load(f)


query = "What is PM-KISAN?"

query_tokens = tokenize(query)

print("Query:")
print(query)

print("\nQuery tokens:")
print(query_tokens)


print("\nSearching for PM-KISAN in chunks...")

for i, chunk in enumerate(chunks):

    text = chunk["text"]

    if "PM" in text.upper() and "KISAN" in text.upper():

        tokens = tokenize(text)

        print("\nChunk:", i)
        print("Source:", chunk.get("source"))
        print("Page:", chunk.get("page"))

        matching_tokens = [
            token for token in tokens
            if "kisan" in token
        ]

        print("KISAN-related tokens:", matching_tokens[:20])


scores = bm25.get_scores(query_tokens)

top_indices = scores.argsort()[::-1][:10]

print("\n==============================")
print("TOP BM25 RESULTS")
print("==============================")


for rank, idx in enumerate(top_indices, 1):

    print(f"\n--- Result {rank} ---")
    print("Index:", idx)
    print("Score:", scores[idx])
    print("Source:", chunks[idx].get("source"))
    print("Page:", chunks[idx].get("page"))