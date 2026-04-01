import re
import logging


def extract_dl(text):
    """
    Extract Driving License fields from OCR text
    Supports multiple Indian DL formats
    """

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    dl_number = None
    name = None
    dob = None
    expiry_date = None

    try:

        # DL patterns (India multiple formats)
        dl_patterns = [
            r"\b[A-Z]{2}\d{2}\s?\d{11}\b",     # MH1220110012345
            r"\b[A-Z]{2}-\d{2}-\d{11}\b",      # MH-12-20110012345
            r"\b[A-Z]{2}\d{13}\b"              # DL0420110149646
        ]

        # Date patterns
        date_patterns = [
            r"\b\d{2}/\d{2}/\d{4}\b",
            r"\b\d{2}-\d{2}-\d{4}\b"
        ]

        # ---------- DL NUMBER ----------
        for pattern in dl_patterns:
            match = re.search(pattern, text)
            if match:
                dl_number = match.group()
                break

        # ---------- DOB ----------
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                dob = match.group()
                break

        # ---------- EXPIRY DATE ----------
        for line in lines:

            if any(k in line.lower() for k in ["valid till", "expiry", "valid upto", "valid up to"]):

                for pattern in date_patterns:
                    match = re.search(pattern, line)
                    if match:
                        expiry_date = match.group()
                        break

        # ---------- NAME DETECTION ----------
        for i, line in enumerate(lines):

            if "driving licence" in line.lower() or "driving license" in line.lower():

                if i + 1 < len(lines):

                    candidate = lines[i + 1]

                    # avoid numeric or garbage lines
                    if not re.search(r"\d", candidate):
                        name = candidate

                break

        # ---------- FALLBACK NAME ----------
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
        logging.warning(f"DL extraction failed: {str(e)}")

    return {
        "dl_number": dl_number,
        "name": name,
        "dob": dob,
        "expiry_date": expiry_date
    }