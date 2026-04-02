import re
import logging

def extract_aadhaar(text: str):

    aadhaar_number = None
    name = None
    dob = None
    gender = None
    address = None

    try:

        # -------------------------
        # Aadhaar number
        # -------------------------

        match = re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text)

        if match:
            aadhaar_number = match.group()

        # -------------------------
        # DOB
        # -------------------------

        dob_patterns = [
            r"\d{2}/\d{2}/\d{4}",
            r"\d{2}-\d{2}-\d{4}",
            r"Year of Birth[: ]*\d{4}",
            r"YOB[: ]*\d{4}"
        ]

        for pattern in dob_patterns:

            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                dob = match.group()

                dob = (
                    dob.replace("Year of Birth", "")
                    .replace("YOB", "")
                    .replace(":", "")
                    .strip()
                )

                break

        # -------------------------
        # Gender
        # -------------------------

        if re.search(r"\bmale\b", text, re.IGNORECASE):
            gender = "Male"

        if re.search(r"\bfemale\b", text, re.IGNORECASE):
            gender = "Female"

        # -------------------------
        # NAME DETECTION
        # -------------------------

        clean_text = re.sub(r"\d", "", text)

        words = clean_text.split()

        english_candidates = []

        for i in range(len(words) - 1):

            candidate = words[i] + " " + words[i + 1]

            if any(k in candidate.lower() for k in [
                "male",
                "female",
                "birth",
                "aadhaar",
                "vid",
                "authority"
            ]):
                continue

            if re.match(r"^[A-Za-z ]+$", candidate):
                english_candidates.append(candidate)

        if english_candidates:
            name = english_candidates[0]

        # -------------------------
        # ADDRESS DETECTION
        # -------------------------

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        for i, line in enumerate(lines):

            if "address" in line.lower():

                address_lines = []

                for j in range(i + 1, min(i + 6, len(lines))):

                    candidate = lines[j]

                    # stop if aadhaar number appears
                    if re.search(r"\d{4}\s?\d{4}\s?\d{4}", candidate):
                        break

                    address_lines.append(candidate)

                if address_lines:
                    address = " ".join(address_lines)
                    break

        # -------------------------
        # CLEAN ADDRESS
        # -------------------------

        if address:

            # remove unwanted words
            address = re.sub(
                r"(government of india|unique identification authority of india|aadhaar)",
                "",
                address,
                flags=re.IGNORECASE
            )

            # remove extra spaces
            address = re.sub(r"\s+", " ", address).strip()

    except Exception as e:

        logging.warning(f"Aadhaar extraction failed: {str(e)}")

    return {

        "aadhaar_number": aadhaar_number,
        "name": name,
        "dob": dob,
        "gender": gender,
        "address": address
    }