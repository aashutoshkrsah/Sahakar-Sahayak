import re

from langdetect import detect, LangDetectException


SUPPORTED_LANGUAGES = {
    "en",
    "hi",
    "kn",
    "ta",
    "te",
    "ml"
}


def preprocess_query(query: str) -> str:
    """
    Clean and normalize the user's query
    without changing its language.
    """

    query = query.strip()

    # Remove extra spaces
    query = re.sub(r"\s+", " ", query)

    # Remove unnecessary punctuation at the end
    query = query.rstrip("?!.,").strip()

    return query


def validate_language(language: str) -> str:
    """
    Validate the language supplied by the client.
    """

    language = language.lower().strip()

    if language not in SUPPORTED_LANGUAGES:
        return "en"

    return language


def detect_intent(query: str, language: str = "en") -> str:

    query_lower = query.lower()

    # English intent detection for now
    if "how" in query_lower:
        return "procedure"

    if any(word in query_lower for word in [
        "where",
        "location",
        "located"
    ]):
        return "location"

    if any(word in query_lower for word in [
        "when",
        "timing",
        "hours",
        "open",
        "close"
    ]):
        return "operating_hours"

    if any(word in query_lower for word in [
        "use",
        "usage",
        "access",
        "available",
        "availability"
    ]):
        return "usage_or_availability"

    return "general"


def detect_language(query: str) -> str:

    try:
        return detect(query)

    except LangDetectException:
        return "unknown"


if __name__ == "__main__":

    test_queries = [
        "Where is the robotics lab???",
        "When is the library open?",
        "Can I use the 3D printer?",
        "How do I use the robotics equipment?"
    ]

    for query in test_queries:

        cleaned = preprocess_query(query)

        language = detect_language(cleaned)

        # Validate detected language
        language = validate_language(language)

        intent = detect_intent(
            cleaned,
            language
        )

        print("Original Query :", query)
        print("Cleaned Query  :", cleaned)
        print("Language       :", language)
        print("Intent         :", intent)
        print()