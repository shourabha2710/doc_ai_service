import pytesseract
from .base_ocr import OCREngine


class TesseractOCR(OCREngine):

    def extract_text(self, image):
        """
        Extract text using Tesseract OCR
        """

        text = pytesseract.image_to_string(
            image,
            lang="eng+hin",
            config="--oem 3 --psm 6"
        )

        return text

    def extract_full_text(self, image):

        return pytesseract.image_to_string(
            image,
            lang="eng+hin",
            config="--oem 3 --psm 6"
        )