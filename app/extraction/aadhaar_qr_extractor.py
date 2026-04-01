import json
from pyzbar.pyzbar import decode

def extract_aadhaar_qr(image):
    """
    Detect and decode Aadhaar QR codes.
    Returns a list of QR data dictionaries.
    """
    decoded_objects = decode(image)
    qr_data_list = []

    for obj in decoded_objects:
        try:
            qr_text = obj.data.decode("utf-8")

            # Try to parse JSON, fallback to raw text
            try:
                qr_data = json.loads(qr_text)
            except:
                qr_data = {"raw_qr_text": qr_text}

            qr_data_list.append(qr_data)

        except Exception:
            continue

    # Return None if no QR codes detected
    return qr_data_list if qr_data_list else None