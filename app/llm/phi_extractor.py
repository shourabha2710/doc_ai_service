import requests
import json
import logging

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"


def extract_with_phi(text: str, doc_type: str):

    if not text:
        return None

    # limit prompt size (important)
    text = text[:2000]

    prompt = f"""
You are an AI information extraction system.

Extract structured JSON fields from OCR text.

Return ONLY valid JSON.

Document type: {doc_type}

OCR TEXT:
{text}

JSON FORMAT:

aadhaar:
{{
 "aadhaar_number": "",
 "name": "",
 "dob": "",
 "gender": "",
 "address": ""
}}

pan:
{{
 "name": "",
 "father_name": "",
 "dob": "",
 "pan_number": ""
}}

passport:
{{
 "passport_number": "",
 "name": "",
 "dob": "",
 "nationality": ""
}}

dl:
{{
 "dl_number": "",
 "name": "",
 "dob": "",
 "expiry_date": ""
}}

voter:
{{
 "voter_id": "",
 "name": "",
 "father_name": "",
 "dob": ""
}}
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )

        result = response.json().get("response", "")

        # try to parse JSON
        return json.loads(result)

    except Exception as e:

        logging.warning(f"Phi extraction failed: {str(e)}")

        return None