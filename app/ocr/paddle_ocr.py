from paddleocr import PaddleOCR
import cv2
from .base_ocr import OCREngine

ocr_instance = None  # 🔥 global singleton


def get_ocr():
    global ocr_instance

    if ocr_instance is None:
        print("🔥 Initializing PaddleOCR (one-time)...")

        ocr_instance = PaddleOCR(
            use_angle_cls=True,
            lang="en",
            use_gpu=False,
            show_log=False
        )

    return ocr_instance


class PaddleOCREngine(OCREngine):

    def preprocess(self, image):
        if image is None:
            return None

        h, w = image.shape[:2]
        scale = 1.5

        return cv2.resize(
            image,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_CUBIC
        )

    def extract_text(self, image):

        image = self.preprocess(image)

        if image is None:
            return ""

        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        try:
            ocr = get_ocr()  # 🔥 use singleton
            result = ocr.ocr(image, cls=True)

        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

        if not result:
            return ""

        lines = []

        for res in result:
            if res:
                for line in res:
                    if line and len(line) >= 2:
                        text = line[1][0]
                        conf = line[1][1]

                        if text and conf > 0.5:
                            lines.append(text.strip())

        return "\n".join(lines)