import pytesseract
from pytesseract import Output
from .base_ocr import OCREngine


class TesseractOCR(OCREngine):

    def extract_text(self, image):
        """
        Extract text using Tesseract with confidence filtering
        """

        data = pytesseract.image_to_data(
            image,
            lang="eng+hin",
            config="--oem 3 --psm 4",
            output_type=Output.DICT
        )

        words = []
        confidences = data["conf"]

        for i, word in enumerate(data["text"]):

            if word.strip() == "":
                continue

            try:
                conf = float(confidences[i])
            except:
                conf = -1

            # filter low confidence OCR
            if conf > 50:
                words.append(word)

        text = " ".join(words)

        return text