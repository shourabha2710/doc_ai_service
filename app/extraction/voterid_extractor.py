import re
import logging


def extract_voterid(text):
    """
    Extract Voter ID (EPIC) fields from OCR text
    """

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    voter_id = None
    name = None
    father_name = None
    dob = None

    try:

        # ---------- VOTER ID / EPIC ----------
        voter_patterns = [
            r"\b[A-Z]{3}[0-9]{7}\b",     # ABC1234567
            r"\b[A-Z]{2,3}[0-9]{6,8}\b"  # OCR variations
        ]

        for pattern in voter_patterns:
            match = re.search(pattern, text)
            if match:
                voter_id = match.group()
                break

        # ---------- DOB ----------
        dob_patterns = [
            r"\b\d{2}/\d{2}/\d{4}\b",
            r"\b\d{2}-\d{2}-\d{4}\b"
        ]

        for pattern in dob_patterns:
            match = re.search(pattern, text)
            if match:
                dob = match.group()
                break

        # ---------- NAME / FATHER NAME ----------
        for i, line in enumerate(lines):

            lower_line = line.lower()

            # Detect name
            if "name" in lower_line and not name:
                parts = line.split(":")
                if len(parts) > 1:
                    name = parts[1].strip()

            # Detect father name
            if any(k in lower_line for k in ["father", "s/o", "d/o", "w/o"]):
                parts = line.split(":")
                if len(parts) > 1:
                    father_name = parts[1].strip()

        # ---------- FALLBACK NAME DETECTION ----------
        if not name:

            for line in lines:

                if (
                    len(line.split()) >= 2
                    and not re.search(r"\d", line)
                    and len(line) < 40
                ):
                    name = line
                    break

    except Exception as e:
        logging.warning(f"Voter ID extraction failed: {str(e)}")

    return {
        "voter_id": voter_id,
        "name": name,
        "father_name": father_name,
        "dob": dob
    }