import cv2

from app.ocr.tesseract_ocr import TesseractOCR
from app.image_processing.preprocess import preprocess
from app.extraction.aadhaar_extractor import extract_aadhaar
from app.extraction.pan_extractor import extract_pan
from app.extraction.aadhaar_qr_extractor import extract_aadhaar_qr
from app.extraction.passport_extractor import extract_passport
from app.extraction.dl_extractor import extract_dl
from app.extraction.voterid_extractor import extract_voterid
from app.image_processing.blur_detection import detect_blur
from app.image_processing.auto_rotate import auto_rotate_image
from app.image_processing.document_edge import detect_document_edges
from app.schemas.extraction_schema import ExtractionResult, AadhaarFields, PanFields, PassportFields, DLFields, VoterIDFields

ocr_engine = TesseractOCR()


# -----------------------------
# Smart Hybrid Document Type Detection
# -----------------------------
def detect_document_type(text, image, qr_data=None):
    """
    Detect the document type using:
    1️⃣ QR data (if present)
    2️⃣ OCR keyword detection
    3️⃣ Regex patterns
    4️⃣ Image layout heuristics
    """

    text_lower = text.lower()

    # 1️⃣ Check QR data for Aadhaar
    if qr_data:
        if isinstance(qr_data, list):
            for qr in qr_data:
                if "uid" in qr or "aadhaar" in qr:
                    return "Aadhaar"
        elif isinstance(qr_data, dict):
            if "uid" in qr_data or "aadhaar" in qr_data:
                return "Aadhaar"

    # 2️⃣ Keyword detection
    keywords = {
        "PAN": ["income tax department", "permanent account number"],
        "Aadhaar": ["unique identification authority of india", "aadhaar"],
        "Passport": ["passport", "republic of india"],
        "Driving License": ["driving licence", "transport department"],
        "Voter ID": ["election commission of india", "elector photo identity card"]
    }

    for doc_type, kws in keywords.items():
        if any(kw.lower() in text_lower for kw in kws):
            return doc_type

    # 3️⃣ Regex detection
    import re
    patterns = {
        "PAN": r"[A-Z]{5}[0-9]{4}[A-Z]",
        "Aadhaar": r"\d{4}\s\d{4}\s\d{4}",
        "Passport": r"[A-Z]{1}[0-9]{7}",
        "Voter ID": r"[A-Z]{3}[0-9]{7,12}",  # optional extended length
        "Driving License": r"[A-Z]{2}\d{2}\s?\d{11}"
    }

    for doc_type, pattern in patterns.items():
        if re.search(pattern, text):
            return doc_type

    # 4️⃣ Fallback image heuristics
    height, width = image.shape[:2]
    aspect_ratio = width / height

    if aspect_ratio > 1.5:
        return "Driving License"
    if aspect_ratio < 1:
        return "Passport"
    if 1 <= aspect_ratio <= 1.5:
        return "Aadhaar or Voter ID"

    return "Unknown"


# -----------------------------
# Main Document Processing
# -----------------------------
def process_document(image_path, max_dim=1200) -> ExtractionResult:
    """
    Process document image:
    1. Blur detection
    2. Auto rotation
    3. Edge detection & cropping
    4. QR extraction
    5. Preprocess
    6. OCR
    7. Field extraction
    8. Document type detection
    """

    image = cv2.imread(image_path)
    if image is None:
        return ExtractionResult(
            status="error",
            reason="Invalid image file"
        )

    # 1️⃣ Blur detection
    blur_result = detect_blur(image)
    if blur_result["is_blurry"]:
        return ExtractionResult(
            status="failed",
            reason="Image too blurry",
            blur_score=blur_result["blur_score"]
        )

    # 2️⃣ Auto rotate
    image, rotation_angle = auto_rotate_image(image)

    # 3️⃣ Document edge detection
    image, cropped = detect_document_edges(image)

    # 4️⃣ Resize large images to max_dim for faster OCR
    height, width = image.shape[:2]
    if max(height, width) > max_dim:
        scaling_factor = max_dim / max(height, width)
        image = cv2.resize(image, (0, 0), fx=scaling_factor, fy=scaling_factor)

    # 5️⃣ QR extraction
    qr_data = extract_aadhaar_qr(image)

    # 6️⃣ Preprocess for OCR
    processed_image = preprocess(image)

    # 7️⃣ OCR
    text = ocr_engine.extract_text(processed_image)

    # 8️⃣ Field extraction
    aadhaar_fields_dict = extract_aadhaar(text)
    pan_fields_dict = extract_pan(text)
    passport_fields_dict = extract_passport(text)
    dl_fields_dict = extract_dl(text)
    voterid_fields_dict = extract_voterid(text)

    aadhaar_fields = AadhaarFields(**aadhaar_fields_dict)
    pan_fields = PanFields(**pan_fields_dict)
    passport_fields = PassportFields(**passport_fields_dict)
    dl_fields = DLFields(**dl_fields_dict)
    voterid_fields = VoterIDFields(**voterid_fields_dict)

    # 9️⃣ Document Type Detection (pass QR data)
    document_type = detect_document_type(text, image, qr_data)

    return ExtractionResult(
        status="success",
        blur_score=blur_result["blur_score"],
        rotation_angle=rotation_angle,
        document_cropped=cropped,
        qr_data=qr_data,
        raw_text=text,
        aadhaar_fields=aadhaar_fields,
        pan_fields=pan_fields,
        passport_fields=passport_fields,
        dl_fields=dl_fields,
        voterid_fields=voterid_fields,
        document_type=document_type
    )