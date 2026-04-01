import cv2
import asyncio
import logging
import re

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
from app.schemas.extraction_schema import (
    ExtractionResult,
    AadhaarFields,
    PanFields,
    PassportFields,
    DLFields,
    VoterIDFields
)

# Logging config
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

tesseract_engine = TesseractOCR()


async def async_qr_ocr(image):
    """
    Run QR extraction and OCR in parallel
    """
    loop = asyncio.get_running_loop()

    # Preprocess once
    processed_image = preprocess(image)

    qr_future = loop.run_in_executor(None, extract_aadhaar_qr, image)
    ocr_future = loop.run_in_executor(None, tesseract_engine.extract_text, processed_image)

    qr_data, text = await asyncio.gather(qr_future, ocr_future)

    return qr_data, text


def detect_document_type(text, image, qr_data=None):
    """
    Detect document type using QR, keywords, regex, or image heuristics
    """

    text_lower = text.lower()

    # QR detection
    if qr_data and isinstance(qr_data, list):
        for qr in qr_data:
            if "uid" in qr or "aadhaar" in qr:
                return "Aadhaar"

    # Keyword detection
    keywords = {
        "PAN": ["income tax department", "permanent account number"],
        "Aadhaar": ["unique identification authority of india", "aadhaar"],
        "Passport": ["passport", "republic of india"],
        "Driving License": ["driving licence", "transport department"],
        "Voter ID": ["election commission of india", "elector photo identity card"]
    }

    for doc_type, kws in keywords.items():
        if any(k in text_lower for k in kws):
            return doc_type

    # Regex detection
    patterns = {
        "PAN": r"[A-Z]{5}[0-9]{4}[A-Z]",
        "Aadhaar": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}",
        "Passport": r"[A-Z]{1}[0-9]{7}",
        "Voter ID": r"[A-Z]{3}[0-9]{7,12}",
        "Driving License": r"[A-Z]{2}\d{2}[-\s]?\d{11}"
    }

    for doc_type, pattern in patterns.items():
        if re.search(pattern, text):
            return doc_type

    # Image heuristic fallback
    height, width = image.shape[:2]
    aspect_ratio = width / height

    if aspect_ratio > 1.5:
        return "Driving License"

    if aspect_ratio < 1:
        return "Passport"

    if 1 <= aspect_ratio <= 1.5:
        return "Aadhaar or Voter ID"

    return "Unknown"


async def process_document_async(image_path: str, max_dim: int = 1200) -> ExtractionResult:
    """
    Full OCR pipeline:
    Blur detection → Rotation → Edge detection → Resize → QR + OCR → Field extraction
    """

    logging.info(f"Processing document: {image_path}")

    image = cv2.imread(image_path)

    if image is None:
        logging.error("Invalid image file")
        return ExtractionResult(status="error", reason="Invalid image file")

    # 1️⃣ Blur detection
    blur_result = detect_blur(image)

    logging.info(f"Blur score: {blur_result['blur_score']:.2f}")

    if blur_result["is_blurry"]:
        logging.warning("Image too blurry")
        return ExtractionResult(
            status="failed",
            reason="Image too blurry",
            blur_score=blur_result["blur_score"]
        )

    # 2️⃣ Auto rotation
    try:
        image, rotation_angle = auto_rotate_image(image)
        logging.info(f"Rotation applied: {rotation_angle} degrees")
    except Exception as e:
        logging.warning(f"Auto rotation failed: {str(e)}")
        rotation_angle = 0

    # 3️⃣ Edge detection
    image, cropped = detect_document_edges(image)

    if not cropped:
        logging.warning("Document edges not detected. Using original image.")

    logging.info(f"Document cropped: {cropped}")

    # 4️⃣ Resize if too large
    height, width = image.shape[:2]

    if max(height, width) > max_dim:
        scaling_factor = max_dim / max(height, width)

        image = cv2.resize(
            image,
            (0, 0),
            fx=scaling_factor,
            fy=scaling_factor,
            interpolation=cv2.INTER_AREA
        )

        logging.info(f"Image resized with scaling factor: {scaling_factor:.2f}")

    # 5️⃣ Async QR + OCR
    qr_data, text = await async_qr_ocr(image)

    logging.info(f"QR data detected: {qr_data}")

    # 6️⃣ Field extraction
    aadhaar_fields = AadhaarFields(**extract_aadhaar(text))
    pan_fields = PanFields(**extract_pan(text))
    passport_fields = PassportFields(**extract_passport(text))
    dl_fields = DLFields(**extract_dl(text))
    voterid_fields = VoterIDFields(**extract_voterid(text))

    # 7️⃣ Document type detection
    document_type = detect_document_type(text, image, qr_data)

    logging.info(f"Document type detected: {document_type}")

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