import re
import pandas as pd
import json
import os
import cv2
import pytesseract
from datetime import datetime

# 🧠 Đường dẫn đến tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -----------------------------
# 1️⃣ Cấu hình PII patterns
# -----------------------------
PII_PATTERNS = {
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "name": r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b"
}

# -----------------------------
# 2️⃣ File log
# -----------------------------
AUDIT_DIR = "data"
AUDIT_LOG = os.path.join(AUDIT_DIR, "pii_audit.json")
os.makedirs(AUDIT_DIR, exist_ok=True)

# -----------------------------
# 3️⃣ Hàm ghi log
# -----------------------------
def log_audit(action, details):
    entry = {
        "time": datetime.now().strftime("%H:%M %d/%m/%y"),
        "action": action,
        "details": details
    }

    # Nếu file chưa có, tạo mới
    if not os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, "w", encoding="utf-8") as f:
            json.dump([entry], f, indent=2, ensure_ascii=False)
        return

    # Ghi thêm vào log cũ
    try:
        with open(AUDIT_LOG, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        with open(AUDIT_LOG, "w", encoding="utf-8") as f:
            json.dump([entry], f, indent=2, ensure_ascii=False)

# -----------------------------
# 4️⃣ Hàm mask text
# -----------------------------
def mask_pii(text):
    masked = text
    detected = []
    for key, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, masked)
        if matches:
            detected.append(key)
            masked = re.sub(pattern, f"<{key.upper()}>", masked)
    if detected:
        log_audit("mask_text", detected)
    return masked

# -----------------------------
# 5️⃣ Hàm mask CSV (đã tối ưu)
# -----------------------------
def mask_csv_pii(csv_path):
    """
    Mask toàn bộ CSV — chỉ log 1 dòng duy nhất cho mỗi lần xử lý.
    """
    df = pd.read_csv(csv_path)
    detected_types = set()

    for col in df.columns:
        if df[col].dtype == object:
            # Quét và mask PII (không log từng ô)
            df[col] = df[col].astype(str)
            for key, pattern in PII_PATTERNS.items():
                has_match = df[col].str.contains(pattern, regex=True, na=False, flags=re.IGNORECASE)
                if has_match.any():
                    detected_types.add(key)
                    df[col] = df[col].str.replace(pattern, f"<{key.upper()}>", regex=True)

    # 🔥 Log chỉ 1 dòng duy nhất
    if detected_types:
        log_audit("mask_csv", list(detected_types))

    return df

# -----------------------------
# 6️⃣ Hàm mask Image
# -----------------------------
def mask_image_pii(image_path, output_path=None):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    detected_types = []

    text_boxes = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    for i, word in enumerate(text_boxes['text']):
        for key, pattern in PII_PATTERNS.items():
            if re.match(pattern, word):
                x, y, w, h = (
                    text_boxes['left'][i],
                    text_boxes['top'][i],
                    text_boxes['width'][i],
                    text_boxes['height'][i]
                )
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)
                detected_types.append(key)

    # Save masked image
    if not output_path:
        output_path = image_path.replace(".jpg", "_masked.jpg").replace(".png", "_masked.png")
    cv2.imwrite(output_path, img)

    if detected_types:
        log_audit("mask_image", detected_types)

    return output_path
