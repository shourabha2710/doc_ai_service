import cv2
import asyncio
import logging
import re
import numpy as np

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
from app.ocr.layout_ocr import layout_aware_ocr

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


# -----------------------------
# PARALLEL OCR
# -----------------------------
async def async_ocr(image):

    loop = asyncio.get_running_loop()

    tess_future = loop.run_in_executor(
        None,
        tesseract_engine.extract_text,
        image
    )

    layout_future = loop.run_in_executor(
        None,
        layout_aware_ocr,
        image
    )

    tess_text, layout_text = await asyncio.gather(
        tess_future,
        layout_future
    )

    text = tess_text + "\n" + layout_text

    return text


# -----------------------------
# MAIN DOCUMENT PIPELINE
# -----------------------------
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

    # -----------------------------
    # BLUR CHECK
    # -----------------------------
    blur_result = detect_blur(front_image)

    if blur_result["is_blurry"]:

        return ExtractionResult(
            status="failed",
            blur_score=blur_result["blur_score"],
            reason="Front image too blurry"
        )

    # -----------------------------
    # QR DETECTION (ORIGINAL IMAGE)
    # -----------------------------
    qr_data = extract_aadhaar_qr(front_image)

    logging.info(f"QR detected: {qr_data}")

    # -----------------------------
    # AUTO ROTATE
    # -----------------------------
    front_image, rotation_angle = auto_rotate_image(front_image)

    # -----------------------------
    # DOCUMENT EDGE DETECTION
    # -----------------------------
    front_image, cropped = detect_document_edges(front_image)

    # -----------------------------
    # IMAGE RESIZE
    # -----------------------------
    h, w = front_image.shape[:2]

    max_dim = 1500
    scale = max_dim / max(h, w)

    if scale < 1:

        front_image = cv2.resize(
            front_image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA
        )

    # -----------------------------
    # OCR FRONT
    # -----------------------------
    front_text = await async_ocr(front_image)

    # -----------------------------
    # CLEAN TEXT
    # (IMPORTANT: Hindi remove nahi karna)
    # -----------------------------
    front_text = re.sub(r"[ \t]+", " ", front_text)

    back_text = ""

    # -----------------------------
    # BACK IMAGE OCR
    # -----------------------------
    if back_path:

        back_image = cv2.imread(back_path)

        if back_image is not None:

            back_image, _ = auto_rotate_image(back_image)

            back_image = cv2.resize(
                back_image,
                None,
                fx=2,
                fy=2,
                interpolation=cv2.INTER_CUBIC
            )

            back_text = await async_ocr(back_image)

    text = front_text + "\n" + back_text

    logging.info(text)

    aadhaar_fields = None
    pan_fields = None
    passport_fields = None
    dl_fields = None
    voterid_fields = None

    document_type = document_type.lower()

    # -----------------------------
    # AADHAAR (QR PRIORITY)
    # -----------------------------
    if document_type == "aadhaar":

        if qr_data:

            logging.info("Using Aadhaar QR data")

            qr = qr_data[0]

            aadhaar_fields = AadhaarFields(
                aadhaar_number=qr.get("aadhaar_number"),
                name=qr.get("name"),
                dob=qr.get("dob"),
                gender=qr.get("gender"),
                address=qr.get("address")
            )

        else:

            logging.info("Using OCR Aadhaar extraction")

            aadhaar_fields = AadhaarFields(
                **extract_aadhaar(text)
            )

    # -----------------------------
    # PAN
    # -----------------------------
    elif document_type == "pan":

        pan_fields = PanFields(
            **extract_pan(text)
        )

    # -----------------------------
    # PASSPORT
    # -----------------------------
    elif document_type == "passport":

        passport_fields = PassportFields(
            **extract_passport(text)
        )

    # -----------------------------
    # DRIVING LICENSE
    # -----------------------------
    elif document_type == "dl":

        dl_fields = DLFields(
            **extract_dl(text)
        )

    # -----------------------------
    # VOTER ID
    # -----------------------------
    elif document_type == "voter":

        voterid_fields = VoterIDFields(
            **extract_voterid(text)
        )

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