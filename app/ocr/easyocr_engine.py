import easyocr
from .base_ocr import OCREngine


class EasyOCREngine(OCREngine):

    def __init__(self):

        # load once
        self.reader = easyocr.Reader(
            ['en','hi'],
            gpu=False
        )

    def extract_text(self, image):

        results = self.reader.readtext(image)

        words = []

        for bbox, text, conf in results:

            if conf > 0.4:
                words.append(text)

        return " ".join(words)