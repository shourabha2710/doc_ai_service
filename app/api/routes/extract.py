from fastapi import APIRouter, UploadFile, File, HTTPException
from app.pipeline.document_pipeline import process_document_async
from app.schemas.extraction_schema import ExtractionResult
from app.utils.file_utils import save_temp_file, delete_file
import logging

router = APIRouter()


@router.post("/extract", response_model=ExtractionResult)
async def extract_document(file: UploadFile = File(...)):
    """
    Upload a document image and return OCR results with document type detection.
    Handles temp file saving and cleanup automatically.
    """
    path = save_temp_file(file)
    try:
        # Process document asynchronously
        result = await process_document_async(path)
        return result
    except Exception as e:
        logging.exception("Error processing document")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Ensure temp file cleanup
        delete_file(path)