from fastapi import FastAPI

from backend.routes.query import router as query_router


app = FastAPI()


@app.get("/")
def home():
    return {"message": "SAHAKAAR KIOSK backend is running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "SAHAKAAR KIOSK backend"
    }


app.include_router(query_router)