import re
import logging


def clean_ocr_text(text: str) -> str:
    """
    Fix common OCR mistakes in PAN numbers
    """
    replacements = {
        "O": "0",
        "I": "1",
        "S": "5",
        "B": "8"
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    return text


def extract_pan(text: str):
    """
    Extract PAN card fields from OCR text
    """

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    pan_number = None
    name = None
    father_name = None
    dob = None

    try:

        # PAN regex (ABCDE1234F)
        pan_pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

        # DOB patterns
        dob_patterns = [
            r"\b\d{2}/\d{2}/\d{4}\b",
            r"\b\d{2}-\d{2}-\d{4}\b"
        ]

        for i, line in enumerate(lines):

            clean_line = clean_ocr_text(line.upper())

            # PAN detection
            pan_match = re.search(pan_pattern, clean_line)
            if pan_match and not pan_number:
                pan_number = pan_match.group()

            # DOB detection
            for pattern in dob_patterns:
                dob_match = re.search(pattern, line)
                if dob_match:
                    dob = dob_match.group()
                    break

            # Name detection heuristic
            if "INCOME TAX DEPARTMENT" in line.upper():

                if i + 1 < len(lines):
                    name = lines[i + 1]

                if i + 2 < len(lines):
                    father_name = lines[i + 2]

        # Fallback name detection
        if not name:
            for line in lines:
                if line.isalpha() and len(line.split()) >= 2:
                    name = line
                    break

    except Exception as e:
        logging.warning(f"PAN extraction failed: {str(e)}")

    return {
        "name": name,
        "father_name": father_name,
        "dob": dob,
        "pan_number": pan_number
    }