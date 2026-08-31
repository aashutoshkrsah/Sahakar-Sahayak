from app.rag.hybrid_search import hybrid_search


def build_context(query, top_k=8):
    """
    Retrieve relevant chunks using hybrid search
    and combine them into a single context string
    for the LLM.
    """

    results = hybrid_search(
        query,
        top_k=top_k
    )

    if not results:
        return "No relevant information found in the government documents."

    context_parts = []

    for i, result in enumerate(results, 1):

        source = result.get("source", "Unknown")
        page = result.get("page", "Unknown")
        text = result.get("text", "").strip()

        context = f"""
SOURCE {i}
Document: {source}
Page: {page}

{text}
"""

        context_parts.append(context.strip())

    return "\n\n".join(context_parts)


# ---------------------------------
# Test
# ---------------------------------

if __name__ == "__main__":

    questions = [
        "What is PM-KISAN?",
        "How much money does a farmer receive under PM-KISAN?",
        "Who is eligible for PM-KISAN?",
        "Who is excluded from PM-KISAN?",
        "How are PM-KISAN benefits transferred?"
    ]

    for query in questions:

        print("\n" + "=" * 60)
        print("QUERY")
        print("=" * 60)

        print(query)

        context = build_context(
            query,
            top_k=8
        )

        print("\n" + "=" * 60)
        print("RETRIEVED CONTEXT")
        print("=" * 60)

        print(context)