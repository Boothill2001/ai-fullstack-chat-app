import os
import cv2
import re
import json
import pytesseract
from datetime import datetime
from app.utils.pii_utils import PII_PATTERNS, log_audit

# Cấu hình đường dẫn Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DATA_DIR = "app/data"
os.makedirs(DATA_DIR, exist_ok=True)

# ====================================================
# 🧩 HÀM XỬ LÝ IMAGE (MASK + OCR + AUDIT)
# ====================================================
async def process_image(image_path, question: str = "Mô tả ảnh này"):
    """
    Nhận file image → OCR → mask PII → trả về câu trả lời có reference đến ảnh.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Không tìm thấy file: {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Không thể đọc ảnh. Hãy kiểm tra định dạng file!")

    detected_types = []

    # OCR detect text
    text_boxes = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    for i, word in enumerate(text_boxes["text"]):
        for key, pattern in PII_PATTERNS.items():
            if re.match(pattern, word):
                x, y, w, h = (
                    text_boxes["left"][i],
                    text_boxes["top"][i],
                    text_boxes["width"][i],
                    text_boxes["height"][i]
                )
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)
                detected_types.append(key)

    # Save masked image
    masked_path = image_path.replace(".jpg", "_masked.jpg").replace(".png", "_masked.png")
    cv2.imwrite(masked_path, img)

    # Ghi log nếu có phát hiện
    if detected_types:
        log_audit("mask_image", detected_types)

    # 🧠 Tạo câu trả lời AI reference tới ảnh
    response = (
        "🤖 I’ve analyzed the uploaded image. "
        "It seems to contain text and possibly faces. "
        f"You asked: '{question}' — "
        "this question has been linked to your uploaded image."
    )

    return {"reply": response, "masked_image_path": masked_path}
