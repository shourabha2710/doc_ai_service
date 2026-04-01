import re


def extract_pan(text):
    """
    Extract PAN card fields from OCR text
    """

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    pan_number = None
    name = None
    father_name = None
    dob = None

    # PAN regex
    pan_pattern = r"[A-Z]{5}[0-9]{4}[A-Z]"

    # DOB patterns
    dob_pattern = r"\d{2}/\d{2}/\d{4}"

    for i, line in enumerate(lines):

        # PAN number
        pan_match = re.search(pan_pattern, line)
        if pan_match:
            pan_number = pan_match.group()

        # DOB
        dob_match = re.search(dob_pattern, line)
        if dob_match:
            dob = dob_match.group()

        # Name detection
        if "INCOME TAX DEPARTMENT" in line.upper():

            if i + 1 < len(lines):
                name = lines[i + 1]

            if i + 2 < len(lines):
                father_name = lines[i + 2]

    return {
        "name": name,
        "father_name": father_name,
        "dob": dob,
        "pan_number": pan_number
    }