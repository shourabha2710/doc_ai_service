import pytesseract
from pytesseract import Output
from .base_ocr import OCREngine

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\shourabha.gupta\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"


class TesseractOCR(OCREngine):

    def extract_text(self, image):

        data = pytesseract.image_to_data(
            image,
            lang="eng+hin",
            config="--oem 3 --psm 4",
            output_type=Output.DICT
        )

        words = []

        for i, word in enumerate(data["text"]):

            if word.strip() == "":
                continue

            try:
                conf = float(data["conf"][i])
            except:
                conf = -1

            if conf > 25:
                words.append(word)

        text = " ".join(words)

        return text