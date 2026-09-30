"""BRONZE: raw text of every PDF page, exactly as pypdf reads it (the same reader and page
numbers as the live app, so answer keys and source links keep matching).
Run:  python3 -m backend.pipeline.bronze"""
import os
from pypdf import PdfReader
from backend.pipeline.common import DOCS_DIR, BRONZE_PATH, save


def build():
    pages = []
    for pdf in sorted(f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")):
        reader = PdfReader(os.path.join(DOCS_DIR, pdf))
        for i, page in enumerate(reader.pages, start=1):
            pages.append({"document": pdf, "page": i, "text": page.extract_text() or ""})
    save(BRONZE_PATH, pages)
    print(f"bronze: {len(pages)} pages from {len(set(p['document'] for p in pages))} PDFs -> {BRONZE_PATH}")
    return pages


if __name__ == "__main__":
    build()
