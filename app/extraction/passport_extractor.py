import re

def extract_passport(text):
    """
    Extract Passport fields from OCR text
    """

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    passport_number = None
    name = None
    dob = None
    nationality = None

    # Passport number pattern (Indian Passport: 1 letter + 7 digits)
    passport_match = re.search(r"[A-Z]{1}[0-9]{7}", text)
    if passport_match:
        passport_number = passport_match.group()

    # DOB pattern
    dob_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    if dob_match:
        dob = dob_match.group()

    # Name and Nationality detection (heuristic)
    for i, line in enumerate(lines):
        if "passport" in line.lower():
            if i + 1 < len(lines):
                name = lines[i + 1]
            if i + 2 < len(lines):
                nationality = lines[i + 2]

    return {
        "passport_number": passport_number,
        "name": name,
        "dob": dob,
        "nationality": nationality
    }