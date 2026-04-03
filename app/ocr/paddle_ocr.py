from paddleocr import PaddleOCR
import cv2
from .base_ocr import OCREngine


class PaddleOCREngine(OCREngine):

    def __init__(self):

        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en",
            use_gpu=False
        )

    def preprocess(self, image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gray = cv2.bilateralFilter(gray, 9, 75, 75)

        gray = cv2.resize(gray, None, fx=2, fy=2)

        return gray

    def extract_text(self, image):

        image = self.preprocess(image)

        result = self.ocr.ocr(image)

        words = []

        if result:

            for line in result:

                for word in line:

                    text = word[1][0]
                    conf = word[1][1]

                    if conf > 0.6:
                        words.append(text)

        return " ".join(words)