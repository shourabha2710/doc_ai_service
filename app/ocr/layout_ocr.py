import cv2
import pytesseract
from pytesseract import Output


def detect_text_blocks(image):
    """
    Detect text blocks using Tesseract bounding boxes
    """

    data = pytesseract.image_to_data(
        image,
        lang="eng+hin",
        config="--oem 3 --psm 4",
        output_type=Output.DICT
    )

    blocks = []

    n = len(data["text"])

    for i in range(n):

        word = data["text"][i].strip()

        if word == "":
            continue

        try:
            conf = float(data["conf"][i])
        except:
            conf = -1

        if conf < 25:
            continue

        x = data["left"][i]
        y = data["top"][i]
        w = data["width"][i]
        h = data["height"][i]

        blocks.append({
            "text": word,
            "x": x,
            "y": y,
            "w": w,
            "h": h
        })

    return blocks


def group_words_into_lines(blocks, y_threshold=20):
    """
    Group words into lines based on Y coordinate
    """

    if not blocks:
        return []

    blocks = sorted(blocks, key=lambda b: b["y"])

    lines = []
    current_line = []
    current_y = blocks[0]["y"]

    for block in blocks:

        if abs(block["y"] - current_y) < y_threshold:

            current_line.append(block)

        else:

            lines.append(current_line)
            current_line = [block]
            current_y = block["y"]

    if current_line:
        lines.append(current_line)

    return lines


def build_text_from_lines(lines):
    """
    Reconstruct text from sorted lines
    """

    ordered_text = []

    for line in lines:

        line = sorted(line, key=lambda b: b["x"])

        words = [b["text"] for b in line]

        ordered_text.append(" ".join(words))

    return "\n".join(ordered_text)


def layout_aware_ocr(image):
    """
    Perform layout aware OCR
    """

    blocks = detect_text_blocks(image)

    lines = group_words_into_lines(blocks)

    text = build_text_from_lines(lines)

    return text