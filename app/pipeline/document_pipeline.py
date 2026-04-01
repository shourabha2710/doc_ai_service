import cv2

from app.ocr.tesseract_ocr import TesseractOCR
from app.image_processing.preprocess import preprocess
from app.extraction.aadhaar_extractor import extract_aadhaar
from app.image_processing.blur_detection import detect_blur


ocr_engine = TesseractOCR()


def process_document(image_path):

    # 1️⃣ Load Image
    image = cv2.imread(image_path)

    if image is None:
        return {
            "status": "error",
            "message": "Invalid image file"
        }

    # 2️⃣ Blur Detection
    blur_result = detect_blur(image)

    if blur_result["is_blurry"]:
        return {
            "status": "failed",
            "reason": "Image is too blurry",
            "blur_score": blur_result["blur_score"]
        }

    # 3️⃣ Preprocess Image
    processed_image = preprocess(image_path)

    # 4️⃣ OCR
    text = ocr_engine.extract_text(processed_image)

    # 5️⃣ Extract Aadhaar Fields
    fields = extract_aadhaar(text)

    # 6️⃣ Final Response
    return {
        "status": "success",
        "blur_score": blur_result["blur_score"],
        "raw_text": text,
        "fields": fields
    }