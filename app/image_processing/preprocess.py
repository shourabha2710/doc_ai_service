import cv2
import numpy as np


def preprocess(image):

    # convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # increase contrast
    gray = cv2.equalizeHist(gray)

    # denoise
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        15,
        10
    )

    return thresh