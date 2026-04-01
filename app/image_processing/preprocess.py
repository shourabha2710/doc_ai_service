import cv2


def preprocess(image):
    """
    Preprocess image for better OCR accuracy

    Steps:
    1. Convert to grayscale
    2. Increase contrast
    3. Light denoise
    """

    if image is None:
        raise ValueError("Invalid image input")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Increase contrast
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)

    # Bilateral filter (keeps text edges sharp)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    return gray