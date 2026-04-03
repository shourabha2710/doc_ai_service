from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import logging

from app.pipeline.document_pipeline import process_document_async
from app.schemas.extraction_schema import ExtractionResult
from app.utils.file_utils import save_temp_file, delete_file

router = APIRouter()


@router.post("/extract", response_model=ExtractionResult)
async def extract_document(
    document_type: str = Form(...),
    front_image: UploadFile = File(...),
    back_image: Optional[UploadFile] = File(None)
):

    logging.info(f"🔥 Incoming request: {document_type}")

    front_path = save_temp_file(front_image)
    back_path = None

    if back_image:
        back_path = save_temp_file(back_image)

    try:

        result = await process_document_async(
            document_type=document_type,
            front_path=front_path,
            back_path=back_path
        )

        logging.info("✅ Extraction completed")

        return result

    except Exception as e:

        logging.exception("❌ Error processing document")

        raise HTTPException(status_code=500, detail=str(e))

    finally:

        delete_file(front_path)

        if back_path:
            delete_file(back_path)