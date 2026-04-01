import cv2
import numpy as np


def detect_blur(image, threshold=100):
    """
    Detect if image is blurry using variance of Laplacian
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    is_blurry = laplacian_var < threshold

    return {
        "blur_score": float(laplacian_var),
        "is_blurry": is_blurry
    }