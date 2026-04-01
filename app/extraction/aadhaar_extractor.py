import re
import logging


def extract_aadhaar(text: str):
    """
    Extract Aadhaar number and DOB from OCR text.
    Supports multiple Aadhaar formats including masked numbers.
    """

    aadhaar = None
    dob = None

    try:

        # Aadhaar patterns
        aadhaar_patterns = [
            r"\b\d{4}\s\d{4}\s\d{4}\b",      # 1234 5678 9012
            r"\b\d{12}\b",                   # 123456789012
            r"\b\d{4}-\d{4}-\d{4}\b",        # 1234-5678-9012
            r"\bXXXX\sXXXX\s\d{4}\b",        # masked aadhaar
        ]

        for pattern in aadhaar_patterns:
            match = re.search(pattern, text)
            if match:
                aadhaar = match.group()
                break

        # DOB patterns
        dob_patterns = [
            r"\b\d{2}/\d{2}/\d{4}\b",   # 12/05/1990
            r"\b\d{2}-\d{2}-\d{4}\b",   # 12-05-1990
        ]

        for pattern in dob_patterns:
            match = re.search(pattern, text)
            if match:
                dob = match.group()
                break

    except Exception as e:
        logging.warning(f"Aadhaar extraction failed: {str(e)}")

    return {
        "aadhaar_number": aadhaar,
        "dob": dob
    }