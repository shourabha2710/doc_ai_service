import json
import logging
from pyzbar.pyzbar import decode


def extract_aadhaar_qr(image):
    """
    Detect and decode QR codes from the image.
    Returns a list of decoded QR data dictionaries.
    """

    qr_data_list = []

    try:
        decoded_objects = decode(image)

        if not decoded_objects:
            return None

        for obj in decoded_objects:
            try:
                qr_bytes = obj.data

                if not qr_bytes:
                    continue

                try:
                    qr_text = qr_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    qr_text = qr_bytes.decode("latin-1", errors="ignore")

                # Try parsing JSON
                try:
                    qr_data = json.loads(qr_text)
                except json.JSONDecodeError:
                    qr_data = {"raw_qr_text": qr_text}

                qr_data_list.append(qr_data)

            except Exception as e:
                logging.warning(f"QR decode failed: {str(e)}")
                continue

    except Exception as e:
        logging.error(f"QR extraction error: {str(e)}")
        return None

    return qr_data_list if qr_data_list else None