import json
import logging
import xml.etree.ElementTree as ET
from pyzbar.pyzbar import decode


def extract_aadhaar_qr(image):
    """
    Detect and decode QR codes from the image.
    Supports Aadhaar XML QR and generic QR.
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

                # Decode bytes to string
                try:
                    qr_text = qr_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    qr_text = qr_bytes.decode("latin-1", errors="ignore")

                qr_data = None

                # -----------------------------
                # Try JSON parsing
                # -----------------------------

                try:
                    qr_data = json.loads(qr_text)

                except json.JSONDecodeError:
                    pass

                # -----------------------------
                # Try Aadhaar XML parsing
                # -----------------------------

                if not qr_data:

                    try:

                        root = ET.fromstring(qr_text)

                        qr_data = {
                            "name": root.attrib.get("name"),
                            "dob": root.attrib.get("dob"),
                            "gender": root.attrib.get("gender"),
                            "aadhaar_number": root.attrib.get("uid"),
                            "address": root.attrib.get("house", "")
                            + " "
                            + root.attrib.get("street", "")
                            + " "
                            + root.attrib.get("lm", "")
                            + " "
                            + root.attrib.get("loc", "")
                            + " "
                            + root.attrib.get("vtc", "")
                            + " "
                            + root.attrib.get("dist", "")
                            + " "
                            + root.attrib.get("state", "")
                            + " "
                            + root.attrib.get("pc", "")
                        }

                    except Exception:
                        qr_data = None

                # -----------------------------
                # Raw QR fallback
                # -----------------------------

                if not qr_data:
                    qr_data = {
                        "raw_qr_text": qr_text
                    }

                qr_data_list.append(qr_data)

            except Exception as e:
                logging.warning(f"QR decode failed: {str(e)}")
                continue

    except Exception as e:
        logging.error(f"QR extraction error: {str(e)}")
        return None

    return qr_data_list if qr_data_list else None