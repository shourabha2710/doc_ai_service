import re
import logging


def clean_text(text):

    text = re.sub(r"[|]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text


def extract_name(lines):

    for line in lines:

        # Remove relations
        line = re.sub(r"(S/O|D/O|W/O)[: ]*", "", line, flags=re.IGNORECASE)

        # Candidate name
        if (
            len(line.split()) >= 2
            and not re.search(r"\d", line)
            and len(line) < 40
        ):

            blacklist = [
                "government",
                "india",
                "authority",
                "identification",
                "address"
            ]

            if not any(b in line.lower() for b in blacklist):

                return line.strip()

    return None


def extract_address(lines):

    address_lines = []
    capture = False

    for line in lines:

        if "address" in line.lower():
            capture = True
            continue

        if capture:

            if re.search(r"\d{4}\s?\d{4}\s?\d{4}", line):
                break

            if len(line) > 3:
                address_lines.append(line)

    if address_lines:
        address = " ".join(address_lines)

        address = re.sub(r"\s+", " ", address)

        return address

    return None


def extract_aadhaar(text: str):

    aadhaar_number = None
    name = None
    dob = None
    gender = None
    address = None

    try:

        text = clean_text(text)

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # -------------------------
        # Aadhaar Number
        # -------------------------

        aadhaar_candidates = re.findall(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text)

        for candidate in aadhaar_candidates:

            vid_check = re.search(rf"{candidate}\s*\d{{4}}", text)

            if not vid_check:

                aadhaar_number = candidate.replace(" ", "")
                break

        # -------------------------
        # DOB
        # -------------------------

        dob_match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)

        if dob_match:
            dob = dob_match.group()

        # -------------------------
        # Gender
        # -------------------------

        if re.search(r"\bfemale\b", text, re.IGNORECASE):
            gender = "Female"

        elif re.search(r"\bmale\b", text, re.IGNORECASE):
            gender = "Male"

        # -------------------------
        # Name
        # -------------------------

        name = extract_name(lines)

        # -------------------------
        # Address
        # -------------------------

        address = extract_address(lines)

    except Exception as e:

        logging.warning(f"Aadhaar extraction failed: {str(e)}")

    return {
        "aadhaar_number": aadhaar_number,
        "name": name,
        "dob": dob,
        "gender": gender,
        "address": address
    }