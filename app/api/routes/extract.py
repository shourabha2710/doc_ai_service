from fastapi import APIRouter, UploadFile, File
import shutil
from app.pipeline.document_pipeline import process_document

router = APIRouter()

@router.post("/extract")

async def extract_document(file: UploadFile = File(...)):

    path=f"temp/{file.filename}"

    with open(path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)

    result=process_document(path)

    return result