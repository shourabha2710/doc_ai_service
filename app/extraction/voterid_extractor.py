import re

def extract_voterid(text):
    """
    Extract Voter ID fields from OCR text
    """

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    voter_id = None
    name = None
    dob = None
    father_name = None

    # Voter ID pattern (e.g., 3 letters + 7 digits)
    voter_match = re.search(r"[A-Z]{3}[0-9]{7}", text)
    if voter_match:
        voter_id = voter_match.group()

    # DOB pattern
    dob_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    if dob_match:
        dob = dob_match.group()

    # Name / Father Name heuristics
    for i, line in enumerate(lines):
        if "elector" in line.lower() or "voter" in line.lower():
            if i + 1 < len(lines):
                name = lines[i + 1]
            if i + 2 < len(lines):
                father_name = lines[i + 2]
            break

    return {
        "voter_id": voter_id,
        "name": name,
        "father_name": father_name,
        "dob": dob
    }