import cv2

from app.ocr.tesseract_ocr import TesseractOCR
from app.image_processing.preprocess import preprocess
from app.extraction.aadhaar_extractor import extract_aadhaar
from app.extraction.pan_extractor import extract_pan
from app.extraction.aadhaar_qr_extractor import extract_aadhaar_qr
from app.image_processing.blur_detection import detect_blur
from app.image_processing.auto_rotate import auto_rotate_image
from app.image_processing.document_edge import detect_document_edges


ocr_engine = TesseractOCR()


def process_document(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return {
            "status": "error",
            "message": "Invalid image file"
        }

    # 1️⃣ Blur detection
    blur_result = detect_blur(image)

    if blur_result["is_blurry"]:
        return {
            "status": "failed",
            "reason": "Image too blurry",
            "blur_score": blur_result["blur_score"]
        }

    # 2️⃣ Auto rotate
    image, rotation_angle = auto_rotate_image(image)

    # 3️⃣ Document edge detection
    image, cropped = detect_document_edges(image)

    # 4️⃣ QR extraction (before preprocessing)
    qr_data = extract_aadhaar_qr(image)

    # 5️⃣ Preprocess
    processed_image = preprocess(image)

    # 6️⃣ OCR
    text = ocr_engine.extract_text(processed_image)

    # 7️⃣ Field extraction
    aadhaar_fields = extract_aadhaar(text)
    pan_fields = extract_pan(text)

    return {
        "status": "success",
        "blur_score": blur_result["blur_score"],
        "rotation_angle": rotation_angle,
        "document_cropped": cropped,
        "qr_data": qr_data,
        "raw_text": text,
        "aadhaar_fields": aadhaar_fields,
        "pan_fields": pan_fields
    }