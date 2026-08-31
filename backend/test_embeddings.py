from app.rag.embeddings import BGEEmbeddings


embedding_model = BGEEmbeddings()

texts = [
    "Kisan Credit Card provides credit support to farmers.",
    "PM-KISAN provides income support to eligible farmers.",
]

vectors = embedding_model.embed_documents(texts)

print("Number of vectors:", len(vectors))
print("Vector shape:", vectors.shape)
print("First vector:", vectors[0][:10])