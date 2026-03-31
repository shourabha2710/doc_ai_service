import pytesseract
from .base_ocr import OCREngine

class TesseractOCR(OCREngine):

    def extract_text(self, image):
        text = pytesseract.image_to_string(image)
        return text