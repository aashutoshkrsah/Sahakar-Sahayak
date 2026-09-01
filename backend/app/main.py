from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.rag.llm import ask_sarvam

app = FastAPI(
    title="Sahakar Sahayak API",
    description="Grounded Multilingual Scheme RAG Engine",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str
    language: str = "English"
    top_k: int = 5

class QueryResponse(BaseModel):
    question: str
    language: str
    answer: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Sahakar Sahayak RAG Engine"}

@app.post("/api/v1/ask", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    try:
        answer = ask_sarvam(
            question=request.question,
            language=request.language,
            top_k=request.top_k
        )
        return QueryResponse(
            question=request.question,
            language=request.language,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))