import json
from pyzbar.pyzbar import decode


def extract_aadhaar_qr(image):
    """
    Detect and decode Aadhaar QR code
    """

    qr_data = None

    decoded_objects = decode(image)

    for obj in decoded_objects:
        try:
            qr_text = obj.data.decode("utf-8")

            # Aadhaar secure QR usually JSON/XML
            try:
                qr_data = json.loads(qr_text)
            except:
                qr_data = {"raw_qr_text": qr_text}

        except Exception:
            qr_data = None

    return qr_data