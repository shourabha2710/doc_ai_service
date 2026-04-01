import re
import logging


def extract_passport(text):
    """
    Extract Passport fields from OCR text
    Supports MRZ parsing for higher accuracy
    """

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    passport_number = None
    name = None
    dob = None
    nationality = None

    try:

        # ---------- Passport Number ----------
        passport_patterns = [
            r"\b[A-Z]{1}[0-9]{7}\b",   # Indian passport format
            r"\b[A-Z]{2}[0-9]{7}\b"    # some OCR variations
        ]

        for pattern in passport_patterns:
            match = re.search(pattern, text)
            if match:
                passport_number = match.group()
                break

        # ---------- DOB ----------
        dob_patterns = [
            r"\b\d{2}/\d{2}/\d{4}\b",
            r"\b\d{2}-\d{2}-\d{4}\b"
        ]

        for pattern in dob_patterns:
            match = re.search(pattern, text)
            if match:
                dob = match.group()
                break

        # ---------- NATIONALITY ----------
        for line in lines:
            if "nationality" in line.lower():
                parts = line.split(":")
                if len(parts) > 1:
                    nationality = parts[1].strip()
                else:
                    nationality = line.replace("Nationality", "").strip()

        # ---------- NAME DETECTION ----------
        for i, line in enumerate(lines):
            if "passport" in line.lower():

                if i + 1 < len(lines):
                    candidate = lines[i + 1]

                    if not re.search(r"\d", candidate):
                        name = candidate

                break

        # ---------- MRZ DETECTION ----------
        # MRZ lines usually contain <<<<<<<<
        mrz_lines = [line for line in lines if "<<" in line]

        if len(mrz_lines) >= 2:

            line1 = mrz_lines[0]
            line2 = mrz_lines[1]

            # Passport number from MRZ
            if len(line2) >= 9:
                mrz_passport = line2[0:9].replace("<", "")
                if mrz_passport:
                    passport_number = mrz_passport

            # DOB from MRZ (YYMMDD)
            if len(line2) >= 19:
                dob_mrz = line2[13:19]

                if dob_mrz.isdigit():
                    dob = f"{dob_mrz[4:6]}/{dob_mrz[2:4]}/19{dob_mrz[0:2]}"

            # Name from MRZ
            if line1.startswith("P<"):
                name_part = line1.split("<<")
                if len(name_part) > 1:
                    name = name_part[1].replace("<", " ").strip()

    except Exception as e:
        logging.warning(f"Passport extraction failed: {str(e)}")

    return {
        "passport_number": passport_number,
        "name": name,
        "dob": dob,
        "nationality": nationality
    }