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
        # Clean OCR Noise
        # -------------------------

        text = re.sub(r"[|]", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text)

        # -------------------------
        # Aadhaar Number Detection
        # -------------------------

        aadhaar_candidates = re.findall(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text)

        for candidate in aadhaar_candidates:

            candidate_clean = candidate.replace(" ", "")

            vid_check = re.search(rf"{candidate}\s*\d{{4}}", text)

            if not vid_check:
                aadhaar_number = candidate_clean
                break

        # -------------------------
        # DOB Detection
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
        # Gender Detection
        # -------------------------

        if re.search(r"\bfemale\b", text, re.IGNORECASE):
            gender = "Female"

        elif re.search(r"\bmale\b", text, re.IGNORECASE):
            gender = "Male"

        # -------------------------
        # Name Detection
        # -------------------------

        name_candidates = re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text)

        blacklist = [
            "Income Tax",
            "Government Of",
            "Unique Identification",
            "Authority Of",
            "Government India",
            "India Authority"
        ]

        for candidate in name_candidates:

            if any(b.lower() in candidate.lower() for b in blacklist):
                continue

            name = candidate
            break

        # -------------------------
        # Address Detection
        # -------------------------

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        for i, line in enumerate(lines):

            if "address" in line.lower():

                address_lines = []

                for j in range(i + 1, min(i + 8, len(lines))):

                    candidate = lines[j]

                    # stop if aadhaar number appears
                    if re.search(r"\d{4}\s?\d{4}\s?\d{4}", candidate):
                        break

                    # skip hindi lines
                    if re.search(r"[^\x00-\x7F]", candidate):
                        continue

                    address_lines.append(candidate)

                if address_lines:
                    address = " ".join(address_lines)
                    break

        # -------------------------
        # Address Cleanup
        # -------------------------

        if address:

            address = re.sub(
                r"(government of india|unique identification authority of india|aadhaar)",
                "",
                address,
                flags=re.IGNORECASE
            )

            address = re.sub(r"[^\x00-\x7F]+", " ", address)
            address = re.sub(r"[,:]+", " ", address)
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