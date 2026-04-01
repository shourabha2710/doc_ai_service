import cv2
import pytesseract


def auto_rotate_image(image):
    """
    Detect image orientation using Tesseract OSD
    and rotate image to correct orientation
    """

    try:
        osd = pytesseract.image_to_osd(image)

        rotation_angle = 0

        for line in osd.split("\n"):
            if "Rotate" in line:
                rotation_angle = int(line.split(":")[1].strip())

        if rotation_angle == 90:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        elif rotation_angle == 180:
            image = cv2.rotate(image, cv2.ROTATE_180)

        elif rotation_angle == 270:
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return image, rotation_angle

    except Exception:
        # if orientation detection fails
        return image, 0