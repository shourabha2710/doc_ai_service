import cv2
import asyncio
import logging
import re

from app.ocr.paddle_ocr import PaddleOCREngine

from app.image_processing.preprocess import preprocess
from app.extraction.aadhaar_extractor import extract_aadhaar
from app.extraction.pan_extractor import extract_pan
from app.extraction.aadhaar_qr_extractor import extract_aadhaar_qr
from app.extraction.passport_extractor import extract_passport
from app.extraction.dl_extractor import extract_dl
from app.extraction.voterid_extractor import extract_voterid

from app.image_processing.blur_detection import detect_blur
from app.image_processing.auto_rotate import auto_rotate_image

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

ocr_engine = PaddleOCREngine()


async def async_ocr(image):
    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(
        None,
        ocr_engine.extract_text,
        image
    )


def normalize_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


async def process_document_async(
    document_type: str,
    front_path: str,
    back_path: str | None = None
) -> ExtractionResult:

    logging.info(f"Processing document type: {document_type}")

    front_image = cv2.imread(front_path)

    if front_image is None:
        return ExtractionResult(
            status="error",
            reason="Invalid front image"
        )

    cv2.imwrite("debug_original.jpg", front_image)

    # ---------------- BLUR ----------------
    blur_result = detect_blur(front_image)

    if blur_result["is_blurry"]:
        return ExtractionResult(
            status="failed",
            blur_score=blur_result["blur_score"],
            reason="Front image too blurry"
        )

    # ---------------- QR ----------------
    qr_data = extract_aadhaar_qr(front_image)

    logging.info(f"QR detected: {qr_data}")

    # ---------------- ROTATE ----------------
    front_image, rotation_angle = auto_rotate_image(front_image)

    # ---------------- RESIZE ----------------
    h, w = front_image.shape[:2]
    max_dim = 1500
    scale = max_dim / max(h, w)

    if scale < 1:
        front_image = cv2.resize(
            front_image,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA
        )

    if len(front_image.shape) == 2:
        front_image = cv2.cvtColor(front_image, cv2.COLOR_GRAY2BGR)

    cv2.imwrite("debug_processed.jpg", front_image)

    # ---------------- OCR FRONT ----------------
    front_text = await async_ocr(front_image)

    # ❌ REMOVE retry (heavy + slow)
    if not front_text:
        front_text = ""

    front_text = normalize_text(front_text)

    logging.info(f"OCR LINES:\n{front_text}")

    back_text = ""

    # ---------------- OCR BACK ----------------
    if back_path:
        back_image = cv2.imread(back_path)

        if back_image is not None:
            back_image, _ = auto_rotate_image(back_image)

            if len(back_image.shape) == 2:
                back_image = cv2.cvtColor(back_image, cv2.COLOR_GRAY2BGR)

            back_text = await async_ocr(back_image)

    back_text = normalize_text(back_text)

    text = (front_text + "\n" + back_text).strip()

    logging.info(f"OCR TEXT: {text}")

    # ---------------- FIELD EXTRACTION ----------------
    aadhaar_fields = None
    pan_fields = None
    passport_fields = None
    dl_fields = None
    voterid_fields = None

    document_type = document_type.lower()

    if document_type == "aadhaar":

        if qr_data:
            qr = qr_data[0]

            aadhaar_fields = AadhaarFields(
                aadhaar_number=qr.get("aadhaar_number"),
                name=qr.get("name"),
                dob=qr.get("dob"),
                gender=qr.get("gender"),
                address=qr.get("address")
            )
        else:
            aadhaar_fields = AadhaarFields(**extract_aadhaar(text))

    elif document_type == "pan":
        pan_fields = PanFields(**extract_pan(text))

    elif document_type == "passport":
        passport_fields = PassportFields(**extract_passport(text))

    elif document_type == "dl":
        dl_fields = DLFields(**extract_dl(text))

    elif document_type == "voter":
        voterid_fields = VoterIDFields(**extract_voterid(text))

    return ExtractionResult(
        status="success",
        blur_score=blur_result["blur_score"],
        rotation_angle=rotation_angle,
        document_cropped=False,
        qr_data=qr_data,
        raw_text=text,
        aadhaar_fields=aadhaar_fields,
        pan_fields=pan_fields,
        passport_fields=passport_fields,
        dl_fields=dl_fields,
        voterid_fields=voterid_fields,
        document_type=document_type
    )