import cv2


def preprocess(image):
    """
    Preprocess image for better OCR accuracy
    Steps:
    1. Convert to grayscale
    2. Apply Gaussian blur
    3. Adaptive threshold
    """

    if image is None:
        raise ValueError("Invalid image input")

    # 1️⃣ Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2️⃣ Remove noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3️⃣ Improve contrast using adaptive threshold
    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    return thresh