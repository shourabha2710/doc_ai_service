import cv2

from app.ocr.tesseract_ocr import TesseractOCR
from app.image_processing.preprocess import preprocess
from app.extraction.aadhaar_extractor import extract_aadhaar
from app.image_processing.blur_detection import detect_blur
from app.image_processing.auto_rotate import auto_rotate_image
from app.image_processing.document_edge import detect_document_edges


ocr_engine = TesseractOCR()


def process_document(image_path):

    # 1️⃣ Load image
    image = cv2.imread(image_path)

    if image is None:
        return {
            "status": "error",
            "message": "Invalid image file"
        }

    # 2️⃣ Blur detection
    blur_result = detect_blur(image)

    if blur_result["is_blurry"]:
        return {
            "status": "failed",
            "reason": "Image too blurry",
            "blur_score": blur_result["blur_score"]
        }

    # 3️⃣ Auto rotate
    image, rotation_angle = auto_rotate_image(image)

    # 4️⃣ Document edge detection
    image, cropped = detect_document_edges(image)

    # 5️⃣ Preprocess image
    processed_image = preprocess(image)

    # 6️⃣ OCR
    text = ocr_engine.extract_text(processed_image)

    # 7️⃣ Extract fields
    fields = extract_aadhaar(text)

    return {
        "status": "success",
        "blur_score": blur_result["blur_score"],
        "rotation_angle": rotation_angle,
        "document_cropped": cropped,
        "raw_text": text,
        "fields": fields
    }