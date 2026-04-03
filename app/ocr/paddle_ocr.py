from paddleocr import PaddleOCR
import cv2
import numpy as np
from .base_ocr import OCREngine


class PaddleOCREngine(OCREngine):

    def __init__(self):
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en",
            rec=True,
            use_gpu=False,
            det_db_thresh=0.3,
            det_db_box_thresh=0.5,
            det_limit_side_len=1280
        )

    def preprocess(self, image):
        if image is None:
            return None

        # Resize only (keep color)
        h, w = image.shape[:2]
        scale = 1.5

        image = cv2.resize(
            image,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_CUBIC
        )

        return image

    def extract_text(self, image):

        image = self.preprocess(image)

        if image is None:
            return ""

        # Ensure 3-channel
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        try:
            result = self.ocr.ocr(image, cls=True)
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

        if not result:
            return ""

        words = []

        for res in result:
            if res is None:
                continue

            for line in res:
                if line is None or len(line) < 2:
                    continue

                text = line[1][0]
                conf = line[1][1]

                if text and conf and conf > 0.5:
                    words.append(text)

        lines = []

        for res in result:
            if res is None:
                continue
            
            for line in res:
                if line is None or len(line) < 2:
                    continue
                
                text = line[1][0]
                conf = line[1][1]

                if text and conf and conf > 0.5:
                    lines.append(text.strip())

        # 🔥 return multi-line text
        return "\n".join(lines)