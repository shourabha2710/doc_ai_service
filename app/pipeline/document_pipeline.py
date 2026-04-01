import cv2
import asyncio
import logging
import re

from app.ocr.tesseract_ocr import TesseractOCR
from app.ocr.easyocr_engine import EasyOCREngine

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

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

tesseract_engine = TesseractOCR()
easyocr_engine = EasyOCREngine()


async def async_qr_ocr(image):

    loop = asyncio.get_running_loop()

    processed = preprocess(image)

    qr_future = loop.run_in_executor(None, extract_aadhaar_qr, image)

    easy_future = loop.run_in_executor(None, easyocr_engine.extract_text, processed)

    tess_future = loop.run_in_executor(None, tesseract_engine.extract_text, processed)

    qr_data, easy_text, tess_text = await asyncio.gather(
        qr_future,
        easy_future,
        tess_future
    )

    # combine both OCR outputs
    text = easy_text + "\n" + tess_text

    return qr_data, text


def detect_document_type(text):

    text = text.lower()

    if "income tax department" in text:
        return "PAN"

    if "aadhaar" in text or "unique identification authority":
        return "Aadhaar"

    if "passport" in text:
        return "Passport"

    if "driving licence" in text:
        return "Driving License"

    if "election commission" in text:
        return "Voter ID"

    return "Unknown"


async def process_document_async(image_path: str) -> ExtractionResult:

    logging.info(f"Processing document {image_path}")

    image = cv2.imread(image_path)

    if image is None:

        return ExtractionResult(
            status="error",
            reason="Invalid image"
        )

    blur_result = detect_blur(image)

    if blur_result["is_blurry"]:

        return ExtractionResult(
            status="failed",
            blur_score=blur_result["blur_score"],
            reason="Image too blurry"
        )

    image, rotation_angle = auto_rotate_image(image)

    image, cropped = detect_document_edges(image)

    qr_data, text = await async_qr_ocr(image)

    logging.info(text)

    document_type = detect_document_type(text)

    aadhaar_fields = AadhaarFields(**extract_aadhaar(text))
    pan_fields = PanFields(**extract_pan(text))
    passport_fields = PassportFields(**extract_passport(text))
    dl_fields = DLFields(**extract_dl(text))
    voterid_fields = VoterIDFields(**extract_voterid(text))

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