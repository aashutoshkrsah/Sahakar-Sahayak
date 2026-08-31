from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-m3"


class BGEEmbeddings:

    def __init__(self):
        print(f"Loading embedding model: {MODEL_NAME}")

        self.model = SentenceTransformer(MODEL_NAME)

    def embed_documents(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def embed_query(self, query):
        return self.model.encode(
            [query],
            normalize_embeddings=True,
        )[0]