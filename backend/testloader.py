from app.rag.loader import load_pdfs
from app.rag.chunker import chunk_documents


documents = load_pdfs()

print(f"Total pages loaded: {len(documents)}")

chunks = chunk_documents(documents)

print(f"Total chunks created: {len(chunks)}")

for chunk in chunks[:3]:
    print("\nSOURCE:", chunk["source"])
    print("PAGE:", chunk["page"])
    print("TEXT:", chunk["text"][:500])