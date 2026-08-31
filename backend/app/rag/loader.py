from pathlib import Path
from pypdf import PdfReader


DOCUMENTS_DIR = Path(__file__).resolve().parents[2] / "data" / "documents"


def load_pdfs():
    documents = []

    for pdf_path in DOCUMENTS_DIR.glob("*.pdf"):
        reader = PdfReader(pdf_path)

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()

            if text and text.strip():
                documents.append(
                    {
                        "text": text.strip(),
                        "source": pdf_path.name,
                        "page": page_number,
                    }
                )

    return documents