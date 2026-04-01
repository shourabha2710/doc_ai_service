# app/ocr/paddle_ocr.py

from paddleocr import PaddleOCR

class PaddleHandwrittenOCR:
    """
    Handwritten or low-quality OCR using PaddleOCR
    """

    def __init__(self, lang="en"):
        # Multi-language support: "en", "hi", "en|hi"
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            rec=True,
            det=True
        )

    def extract_text(self, image):
        """
        Returns text extracted from image
        """
        results = self.ocr.ocr(image, cls=True)
        lines = []

        for result in results:
            for line in result:
                text = line[1][0]  # OCR text
                lines.append(text)

        return "\n".join(lines)