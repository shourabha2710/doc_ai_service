from app.ocr.tesseract_ocr import TesseractOCR
from app.image_processing.preprocess import preprocess
from app.extraction.aadhaar_extractor import extract_aadhaar

ocr_engine = TesseractOCR()

def process_document(image_path):

    image = preprocess(image_path)

    text = ocr_engine.extract_text(image)

    fields = extract_aadhaar(text)

    return {
        "raw_text": text,
        "fields": fields
    }