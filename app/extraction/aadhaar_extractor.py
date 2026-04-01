import re
import logging


def extract_aadhaar(text: str):
    """
    Extract Aadhaar number, DOB, and Name from OCR text
    """

    aadhaar = None
    dob = None
    name = None

    try:

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # ---------- Aadhaar patterns ----------
        aadhaar_patterns = [
            r"\b\d{4}\s\d{4}\s\d{4}\b",
            r"\b\d{12}\b",
            r"\b\d{4}-\d{4}-\d{4}\b",
            r"\bXXXX\sXXXX\s\d{4}\b"
        ]

        for pattern in aadhaar_patterns:
            match = re.search(pattern, text)
            if match:
                aadhaar = match.group()
                break

        # ---------- DOB patterns ----------
        dob_patterns = [
            r"\b\d{2}/\d{2}/\d{4}\b",
            r"\b\d{2}-\d{2}-\d{4}\b",
            r"DOB[:\s]*\d{2}/\d{2}/\d{4}",
            r"Year of Birth[:\s]*\d{4}",
            r"\b\d{4}\b"
        ]

        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:

                dob = match.group()

                # clean DOB label
                dob = dob.replace("DOB", "").replace("Year of Birth", "")
                dob = dob.replace(":", "").strip()

                break

        # ---------- NAME DETECTION ----------
        for i, line in enumerate(lines):

            if "government of india" in line.lower():

                if i + 1 < len(lines):
                    candidate = lines[i + 1]

                    if not re.search(r"\d", candidate):
                        name = candidate

                break

        # fallback name detection
        if not name:

            for line in lines:

                if (
                    len(line.split()) >= 2
                    and not re.search(r"\d", line)
                    and len(line) < 40
                ):
                    name = line
                    break

    except Exception as e:
        logging.warning(f"Aadhaar extraction failed: {str(e)}")

    return {
        "aadhaar_number": aadhaar,
        "dob": dob,
        "name": name
    }