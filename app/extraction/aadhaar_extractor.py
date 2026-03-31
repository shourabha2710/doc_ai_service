import re

def extract_aadhaar(text):

    aadhaar=None
    dob=None

    aadhaar_match=re.search(r"\d{4}\s\d{4}\s\d{4}",text)

    if aadhaar_match:
        aadhaar=aadhaar_match.group()

    dob_match=re.search(r"\d{2}/\d{2}/\d{4}",text)

    if dob_match:
        dob=dob_match.group()

    return {
        "aadhaar_number":aadhaar,
        "dob":dob
    }