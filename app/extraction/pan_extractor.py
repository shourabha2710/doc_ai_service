import re
import logging


def clean_line(line: str):

    line = line.replace("|", "")
    line = line.replace(":", "")
    line = line.replace(";", "")

    return line.strip()


def is_valid_name(line: str):

    if re.search(r"\d", line):
        return False

    blacklist = [
        "INCOME",
        "TAX",
        "DEPARTMENT",
        "GOVT",
        "INDIA",
        "ACCOUNT",
        "NUMBER",
        "SIGNATURE"
    ]

    for b in blacklist:
        if b in line.upper():
            return False

    if len(line.split()) < 2:
        return False

    return True


def extract_pan(text: str):

    name = None
    father_name = None
    dob = None
    pan_number = None

    try:

        lines = [clean_line(l) for l in text.split("\n") if l.strip()]

        # -------------------------
        # PAN NUMBER
        # -------------------------

        pan_match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)

        if pan_match:
            pan_number = pan_match.group()

        # -------------------------
        # DOB
        # -------------------------

        dob_match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)

        if dob_match:
            dob = dob_match.group()

        # -------------------------
        # FIND DOB LINE INDEX
        # -------------------------

        dob_index = None

        for i, line in enumerate(lines):

            if dob and dob in line:
                dob_index = i
                break

        # -------------------------
        # NAME + FATHER NAME
        # -------------------------

        if dob_index is not None:

            candidates = []

            for j in range(max(0, dob_index - 3), dob_index):

                if is_valid_name(lines[j]):
                    candidates.append(lines[j])

            if len(candidates) >= 1:
                name = candidates[-2] if len(candidates) >= 2 else candidates[0]

            if len(candidates) >= 2:
                father_name = candidates[-1]

    except Exception as e:

        logging.warning(f"PAN extraction failed: {str(e)}")

    return {

        "name": name,
        "father_name": father_name,
        "dob": dob,
        "pan_number": pan_number
    }