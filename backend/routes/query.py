from fastapi import APIRouter, HTTPException

from backend.models.schemas import QueryRequest, QueryResponse

from backend.services.nlp_service import (
    preprocess_query,
    detect_intent,
    validate_language
)

from backend.services.rag_service import get_answer


router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):

    try:

        # 1. Validate language
        language = validate_language(request.language)

        # 2. Clean query
        cleaned_query = preprocess_query(request.query)

        # 3. Detect intent
        intent = detect_intent(
            cleaned_query,
            language
        )

        print("Original Query:", request.query)
        print("Cleaned Query :", cleaned_query)
        print("Language      :", language)
        print("Intent        :", intent)

        # 4. Retrieve relevant document
        result = get_answer(
            cleaned_query,
            language,
            intent
        )

        # 5. Add NLP information
        result["language"] = language
        result["intent"] = intent

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )