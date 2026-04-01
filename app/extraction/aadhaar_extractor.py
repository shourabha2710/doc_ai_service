import re
import logging


def extract_aadhaar(text: str):

    aadhaar_number = None
    name = None
    dob = None
    gender = None
    address = None

    try:

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Aadhaar number
        match = re.search(r"\d{4}\s?\d{4}\s?\d{4}", text)

        if match:
            aadhaar_number = match.group()

        # DOB
        match = re.search(r"\d{2}/\d{2}/\d{4}", text)

        if match:
            dob = match.group()

        # Gender
        if "male" in text.lower():
            gender = "Male"

        if "female" in text.lower():
            gender = "Female"

        # Name detection
        for i, line in enumerate(lines):

            if "government of india" in line.lower():

                if i + 1 < len(lines):

                    candidate = lines[i + 1]

                    if not re.search(r"\d", candidate):

                        name = candidate

                break

        # Address detection
        address_lines = []

        start = False

        for line in lines:

            if "address" in line.lower():
                start = True
                continue

            if start:

                address_lines.append(line)

        if address_lines:

            address = " ".join(address_lines)

    except Exception as e:

        logging.warning(f"Aadhaar extraction failed: {str(e)}")

    return {

        "aadhaar_number": aadhaar_number,
        "name": name,
        "dob": dob,
        "gender": gender,
        "address": address
    }