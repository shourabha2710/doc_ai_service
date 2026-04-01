import os
import uuid
import shutil
from fastapi import UploadFile

TEMP_FOLDER = "temp"

def save_temp_file(upload_file: UploadFile, folder: str = TEMP_FOLDER) -> str:
    """
    Save an uploaded file to a temp folder with a unique name.
    Returns the saved file path.
    """
    os.makedirs(folder, exist_ok=True)
    filename = f"{uuid.uuid4()}_{upload_file.filename}"
    path = os.path.join(folder, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)

    return path

def delete_file(file_path: str):
    """
    Safely delete a file if it exists.
    """
    if os.path.exists(file_path):
        os.remove(file_path)