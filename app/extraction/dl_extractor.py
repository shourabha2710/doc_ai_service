import re

def extract_dl(text):
    """
    Extract Driving License fields from OCR text
    """

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    dl_number = None
    name = None
    dob = None
    expiry_date = None

    # DL number patterns (Indian DL: 2 letters + 2 digits + 11 digits optional)
    dl_match = re.search(r"[A-Z]{2}\d{2}\s?\d{11}", text)
    if dl_match:
        dl_number = dl_match.group()

    dob_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    if dob_match:
        dob = dob_match.group()

    # Expiry date heuristic
    for line in lines:
        if "valid till" in line.lower() or "expiry" in line.lower():
            date_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
            if date_match:
                expiry_date = date_match.group()
                break

    # Name detection: first non-numeric line after "Driving Licence"
    for i, line in enumerate(lines):
        if "driving licence" in line.lower():
            if i + 1 < len(lines):
                name = lines[i + 1]
            break

    return {
        "dl_number": dl_number,
        "name": name,
        "dob": dob,
        "expiry_date": expiry_date
    }