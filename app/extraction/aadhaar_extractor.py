import re
import logging


def extract_aadhaar(text: str):
    """
    Extract Aadhaar fields from OCR text
    """

    aadhaar_number = None
    name = None
    dob = None
    gender = None
    address = None

    try:

        text = text.replace("\r", "\n")
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # -----------------------------
        # Aadhaar Number Extraction
        # -----------------------------

        aadhaar_patterns = [
            r"\b\d{4}\s\d{4}\s\d{4}\b",
            r"\b\d{12}\b",
            r"\b\d{4}-\d{4}-\d{4}\b",
            r"\bXXXX\sXXXX\s\d{4}\b"
        ]

        for pattern in aadhaar_patterns:
            match = re.search(pattern, text)

            if match:
                aadhaar_number = match.group()
                aadhaar_number = aadhaar_number.replace("-", " ")
                break

        # -----------------------------
        # DOB Extraction
        # -----------------------------

        dob_patterns = [
            r"\b\d{2}/\d{2}/\d{4}\b",
            r"\b\d{2}-\d{2}-\d{4}\b",
            r"DOB[:\s]*\d{2}/\d{2}/\d{4}",
            r"Year of Birth[:\s]*\d{4}"
        ]

        for pattern in dob_patterns:

            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                dob = match.group()

                dob = re.sub(
                    r"(DOB|Year of Birth|:)",
                    "",
                    dob,
                    flags=re.IGNORECASE
                ).strip()

                break

        # -----------------------------
        # Gender Extraction
        # -----------------------------

        gender_match = re.search(
            r"\b(MALE|FEMALE|Male|Female)\b",
            text
        )

        if gender_match:
            gender = gender_match.group().capitalize()

        # -----------------------------
        # Name Detection
        # -----------------------------

        for i, line in enumerate(lines):

            if "government of india" in line.lower():

                if i + 1 < len(lines):

                    candidate = lines[i + 1]

                    if (
                        not re.search(r"\d", candidate)
                        and len(candidate.split()) >= 2
                        and len(candidate) < 40
                    ):
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

        # -----------------------------
        # Address Extraction
        # -----------------------------

        address_lines = []
        start_collecting = False

        for line in lines:

            if "address" in line.lower():
                start_collecting = True
                continue

            if start_collecting:

                if re.search(aadhaar_patterns[0], line):
                    break

                address_lines.append(line)

        if address_lines:
            address = " ".join(address_lines)

    except Exception as e:
        logging.warning(f"Aadhaar extraction failed: {str(e)}")

    return {
        "aadhaar_number": aadhaar_number,
        "name": name,
        "dob": dob,
        "gender": gender,
        "address": address
    }