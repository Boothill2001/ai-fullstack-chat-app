import pandas as pd
import io
import json
from pathlib import Path
import matplotlib.pyplot as plt
import uuid
import os
from datetime import datetime
from app.utils.pii_utils import mask_csv_pii  # 🧩 import mask CSV
import re

# ⚙️ Đường dẫn lưu data
MEMORY_PATH = Path("app/data/memory.json")
DATA_DIR = "app/data"
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

# ====================================================
# 🧩 HÀM PHÂN TÍCH CSV
# ====================================================
async def process_csv(file=None, url=None, question=None):
    """
    Đọc CSV, mask PII, và trả kết quả theo câu hỏi người dùng.
    """
    # Đọc file CSV
    if file:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        temp_path = os.path.join(DATA_DIR, f"temp_{uuid.uuid4().hex}.csv")
        df.to_csv(temp_path, index=False)
        df = mask_csv_pii(temp_path)

    elif url:
        df = pd.read_csv(url)
        temp_path = os.path.join(DATA_DIR, f"temp_{uuid.uuid4().hex}.csv")
        df.to_csv(temp_path, index=False)
        df = mask_csv_pii(temp_path)
    else:
        raise ValueError("Cần file hoặc URL CSV!")

    # Chuẩn hóa câu hỏi
    q = question.lower() if question else ""

    # Các loại câu hỏi
    if "tóm tắt" in q or "summary" in q:
        return str(df.describe(include='all'))

    elif ("missing" in q or "na" in q) and ("column" in q or "nhiều" in q or "most" in q):
        col = df.isnull().sum().idxmax()
        return f"🧩 The column with the most missing values is: '{col}'."

    elif "missing" in q or "na" in q:
        missing = df.isnull().sum().sort_values(ascending=False)
        return f"🔍 Missing value summary:\n{missing.head()}"

    # 2️⃣ Thống kê cơ bản cho cột số
    elif "basic stats" in q or "numeric" in q or "thống kê" in q:
        numeric_df = df.select_dtypes(include=['number'])
        if numeric_df.empty:
            return "Không tìm thấy cột số nào trong dataset."
        stats = numeric_df.describe().to_string()
        return f"📊 Basic statistics for numeric columns:\n{stats}"
    elif "histogram" in q or "hist" in q or "biểu đồ" in q:
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return "Không có cột số để vẽ biểu đồ!"
        col = numeric_cols[0]
        chart_path = os.path.join(DATA_DIR, f"{uuid.uuid4()}.png")
        plt.figure()
        df[col].hist()
        plt.title(f"Histogram của {col}")
        plt.savefig(chart_path)
        plt.close()
        return f"Đã tạo biểu đồ histogram cho '{col}' tại {chart_path}"

    else:
        return f"Dataset có {df.shape[0]} hàng và {df.shape[1]} cột."

# ====================================================
# 💾 HÀM LƯU LỊCH SỬ CHAT
# ====================================================
def save_memory(user_msg: str, bot_reply: str):
    """
    Lưu lịch sử chat vào memory.json (format: {"history": [ ... ]})
    """
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    if MEMORY_PATH.exists():
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            try:
                memory = json.load(f)
            except json.JSONDecodeError:
                memory = {"history": []}
    else:
        memory = {"history": []}

    if not isinstance(memory, dict):
        memory = {"history": []}
    if "history" not in memory or not isinstance(memory["history"], list):
        memory["history"] = []

    memory["history"].append({
        "user": user_msg,
        "bot": bot_reply,
        "time": datetime.now().strftime("%H:%M %d/%m/%y")
    })

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
