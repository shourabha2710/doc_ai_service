import cv2

def auto_rotate_image(image):

    # Simple orientation correction using width/height

    h, w = image.shape[:2]

    rotation_angle = 0

    if h > w * 1.5:

        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        rotation_angle = 90

    return image, rotation_angle