from pydantic import BaseModel


class QueryRequest(BaseModel):

    query: str
    language: str


class Source(BaseModel):

    document: str
    page: int | None = None


class QueryResponse(BaseModel):

    answer: str
    language: str
    intent: str
    sources: list[Source] = []
    confidence: float = 0.0