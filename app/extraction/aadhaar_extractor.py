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
        
        # remove numbers
        clean_text = re.sub(r"\d", "", text)
        
        # split words
        words = clean_text.split()
        
        english_candidates = []
        hindi_candidates = []
        
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
        
            # detect english name
            if re.match(r"^[A-Za-z ]+$", candidate):
                english_candidates.append(candidate)
        
            else:
                hindi_candidates.append(candidate)
        
        # priority: english name
        if english_candidates:
            name = english_candidates[0]
        
        elif hindi_candidates:
            name = hindi_candidates[0]
        # -------------------------
        # ADDRESS DETECTION
        # -------------------------

        addr_match = re.search(r"address[: ]*(.*)", text, re.IGNORECASE)

        if addr_match:
            address = addr_match.group(1)

    except Exception as e:

        logging.warning(f"Aadhaar extraction failed: {str(e)}")

    return {

        "aadhaar_number": aadhaar_number,
        "name": name,
        "dob": dob,
        "gender": gender,
        "address": address
    }