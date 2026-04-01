import pytesseract
from .base_ocr import OCREngine

class TesseractOCR(OCREngine):

    def extract_text(self, image):
        text = pytesseract.image_to_string(
            image,
            lang="eng+hin",
            config="--oem 3 --psm 6"
        )
        return text