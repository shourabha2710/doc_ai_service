import pytesseract
import cv2
import re
from pytesseract import Output
from .base_ocr import OCREngine

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\shourabha.gupta\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"


class TesseractOCR(OCREngine):

    def preprocess_for_ocr(self, image):

        # handle grayscale or color image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # noise removal
        gray = cv2.bilateralFilter(gray, 9, 75, 75)

        # contrast improvement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)

        # adaptive threshold
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        return thresh


    def extract_text(self, image):

        image = self.preprocess_for_ocr(image)

        data = pytesseract.image_to_data(
            image,
            lang="eng+hin",
            config="--oem 3 --psm 6",
            output_type=Output.DICT
        )

        words = []

        for i, word in enumerate(data["text"]):

            word = word.strip()

            if word == "":
                continue

            try:
                conf = float(data["conf"][i])
            except:
                conf = -1

            if conf > 30:
                words.append(word)

        text = " ".join(words)

        text = re.sub(r"\s+", " ", text)

        return text