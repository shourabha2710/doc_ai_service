import re
import logging


def clean_text(text):

    text = re.sub(r"[|]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text


def score_name(candidate):

    score = 0

    if len(candidate.split()) == 2:
        score += 3

    if len(candidate) > 6:
        score += 2

    if candidate.isalpha() or " " in candidate:
        score += 2

    blacklist = [
        "Government",
        "India",
        "Authority",
        "Identification",
        "Aadhaar"
    ]

    if any(b.lower() in candidate.lower() for b in blacklist):
        score -= 5

    return score


def extract_aadhaar(text: str):

    aadhaar_number = None
    name = None
    dob = None
    gender = None
    address = None

    try:

        text = clean_text(text)

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
        # NAME DETECTION (SCORING)
        # -------------------------

        candidates = re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text)

        best_score = -1

        for c in candidates:

            s = score_name(c)

            if s > best_score:
                best_score = s
                name = c

        # -------------------------
        # ADDRESS DETECTION
        # -------------------------

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        for i, line in enumerate(lines):

            if "address" in line.lower():

                address_lines = []

                for j in range(i + 1, min(i + 8, len(lines))):

                    candidate = lines[j]

                    if re.search(r"\d{4}\s?\d{4}\s?\d{4}", candidate):
                        break

                    if re.search(r"[^\x00-\x7F]", candidate):
                        continue

                    address_lines.append(candidate)

                if address_lines:
                    address = " ".join(address_lines)
                    break

        # Clean address
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