from fastapi import FastAPI
from app.api.routes.extract import router as extract_router

app = FastAPI(title="Document AI OCR Service")

app.include_router(extract_router, prefix="/api")

@app.get("/")
def root():
    return {"message":"Document AI OCR API running"}