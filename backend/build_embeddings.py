from pathlib import Path
import pickle
import numpy as np
import faiss

from app.rag.loader import load_pdfs
from app.rag.chunker import chunk_documents
from app.rag.embeddings import BGEEmbeddings


print("Loading documents...")
documents = load_pdfs()

print(f"Pages loaded: {len(documents)}")

print("Creating chunks...")
chunks = chunk_documents(documents)

print(f"Chunks created: {len(chunks)}")

print("Loading BGE-M3...")
embedding_model = BGEEmbeddings()

texts = [chunk["text"] for chunk in chunks]

print("Creating embeddings...")
vectors = embedding_model.embed_documents(texts)

print("Embedding completed!")
print("Number of vectors:", len(vectors))
print("Vector shape:", vectors.shape)


# Convert embeddings to NumPy float32
vectors = np.asarray(vectors, dtype="float32")


# Create index directory
index_dir = Path("data/indexes")
index_dir.mkdir(parents=True, exist_ok=True)


# Build FAISS index
dimension = vectors.shape[1]

print(f"Building FAISS index with dimension: {dimension}")

index = faiss.IndexFlatIP(dimension)

# Normalize vectors for cosine similarity
faiss.normalize_L2(vectors)

index.add(vectors)

print("FAISS index created!")
print("Number of vectors in FAISS:", index.ntotal)


# Save FAISS index
faiss_path = index_dir / "faiss.index"
faiss.write_index(index, str(faiss_path))

print(f"FAISS index saved to: {faiss_path}")


# Save chunk metadata
metadata_path = index_dir / "metadata.pkl"

with open(metadata_path, "wb") as f:
    pickle.dump(chunks, f)

print(f"Metadata saved to: {metadata_path}")

print("\n✅ Embedding + FAISS building completed successfully!")