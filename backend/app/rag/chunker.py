from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = []

    for document in documents:
        split_texts = splitter.split_text(document["text"])

        for text in split_texts:
            chunks.append(
                {
                    "text": text,
                    "source": document["source"],
                    "page": document["page"],
                }
            )

    return chunks