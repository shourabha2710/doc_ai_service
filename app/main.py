from fastapi import FastAPI
from app.api.routes.extract import router as extract_router

app = FastAPI(
    title="Document AI OCR Service",
    description="Upload documents (Aadhaar, PAN, Passport, DL, Voter ID) and get OCR fields + document type",
    version="1.0.0"
)

# Include API routes
app.include_router(extract_router, prefix="/api", tags=["Document Extraction"])

@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint
    """
    return {"message": "Document AI OCR API running"}