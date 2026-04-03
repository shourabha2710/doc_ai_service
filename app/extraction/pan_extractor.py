import re
import logging


def clean_line(line: str):
    return re.sub(r"[|:;]", "", line).strip()


def is_valid_name(line: str):
    if re.search(r"\d", line):
        return False

    blacklist = [
        "INCOME", "TAX", "DEPARTMENT", "GOVT", "INDIA",
        "ACCOUNT", "NUMBER", "SIGNATURE", "PERMANENT"
    ]

    return (
        len(line.split()) >= 2
        and not any(b in line.upper() for b in blacklist)
    )


def extract_pan(text: str):

    name = None
    father_name = None
    dob = None
    pan_number = None

    try:
        lines = [clean_line(l) for l in text.split("\n") if l.strip()]

        # -------- PAN --------
        pan_match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)
        if pan_match:
            pan_number = pan_match.group()

        # -------- DOB --------
        dob_match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)
        if dob_match:
            dob = dob_match.group()

        # -------- FILTER VALID NAME LINES --------
        name_candidates = []

        for line in lines:

            # ❌ Skip signature related lines
            if any(k in line.lower() for k in ["signature"]):
                continue

            # ❌ Skip noisy OCR like ! or random chars
            if re.search(r"[!@#$%^&*]", line):
                continue

            if is_valid_name(line):
                name_candidates.append(line)

        # 🔥 IMPORTANT CHANGE: reverse order (bottom-up)
        name_candidates = name_candidates[::-1]

        # PAN structure:
        # bottom → name
        # above → father

        if len(name_candidates) >= 2:
            name = name_candidates[0]          # AKANSHA JAISWAL
            father_name = name_candidates[1]   # SHIV PRASAD JAISWAL

        elif len(name_candidates) == 1:
            name = name_candidates[0]

    except Exception as e:
        logging.warning(f"PAN extraction failed: {str(e)}")

    return {
        "name": name,
        "father_name": father_name,
        "dob": dob,
        "pan_number": pan_number
    }