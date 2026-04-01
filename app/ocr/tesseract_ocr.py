import pytesseract
from pytesseract import Output
from .base_ocr import OCREngine


class TesseractOCR(OCREngine):

    def extract_text(self, image):
        """
        Extract text using Tesseract OCR
        Filters low confidence words
        """

        data = pytesseract.image_to_data(
            image,
            lang="eng+hin",
            config="--oem 3 --psm 6",
            output_type=Output.DICT
        )

        words = []
        confidences = data["conf"]
        texts = data["text"]

        for i in range(len(texts)):

            word = texts[i].strip()

            if word == "":
                continue

            try:
                conf = float(confidences[i])
            except:
                conf = -1

            # Ignore low confidence words
            if conf > 50:
                words.append(word)

        # Final OCR text
        final_text = " ".join(words)

        return final_text


    def extract_full_text(self, image):
        """
        Return full raw OCR text without confidence filtering
        Useful for debugging
        """

        text = pytesseract.image_to_string(
            image,
            lang="eng+hin",
            config="--oem 3 --psm 6"
        )

        return text