from fastapi import APIRouter, UploadFile, File
from app.pipeline.document_pipeline import process_document
from app.schemas.extraction_schema import ExtractionResult
from app.utils.file_utils import save_temp_file, delete_file

router = APIRouter()


@router.post("/extract", response_model=ExtractionResult)
async def extract_document(file: UploadFile = File(...)):
    """
    Upload a document image and return OCR results with document type detection.
    Handles temp file saving and cleanup automatically.
    """
    path = save_temp_file(file)
    try:
        result = await process_document(path)
    finally:
        delete_file(path)
    return result