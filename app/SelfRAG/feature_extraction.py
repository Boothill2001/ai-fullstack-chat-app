# feature_extraction.py
# -------------------------------------------------------------
# Bước 2: Trích xuất đặc trưng (embeddings) từ hình ảnh và caption bằng CLIP
# -------------------------------------------------------------

from PIL import Image
from sentence_transformers import SentenceTransformer
import torch
import os
import pickle
from tqdm import tqdm
import numpy as np

# -------------------------------------------------------------
# ⚙️ Khởi tạo model CLIP
# -------------------------------------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer('clip-ViT-B-32', device=device)
print(f"🔥 Model đang chạy trên: {device.upper()}")

# -------------------------------------------------------------
# 🧠 Hàm chính
# -------------------------------------------------------------
def extract_features(dataset_path='app/SelfRAG/dataset', 
                     output_path='app/SelfRAG/clip_features.pkl'):
    """
    1️⃣ Duyệt tất cả ảnh trong dataset/
    2️⃣ Đọc caption tương ứng
    3️⃣ Dùng CLIP encode cả ảnh và caption
    4️⃣ Lưu vector embeddings vào file .pkl
    """
    data = []

    for folder in tqdm(os.listdir(dataset_path), desc="Extracting features"):
        folder_path = os.path.join(dataset_path, folder)
        if not os.path.isdir(folder_path):
            continue

        image_path = os.path.join(folder_path, 'image.jpg')
        caption_path = os.path.join(folder_path, 'caption.txt')

        if not os.path.exists(image_path) or not os.path.exists(caption_path):
            print(f"[⚠️] Thiếu file trong {folder_path}, bỏ qua.")
            continue

        # Đọc caption
        with open(caption_path, 'r', encoding='utf-8') as f:
            caption = f.read().strip()

        # Mở ảnh (chuyển về RGB để tránh lỗi)
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            print(f"[❌] Không đọc được ảnh {image_path}: {e}")
            continue

        # Encode bằng CLIP
        image_emb = model.encode(image, convert_to_tensor=True)
        text_emb = model.encode(caption, convert_to_tensor=True)

        # Lưu vector
        data.append({
            "id": folder,
            "caption": caption,
            "image_embedding": image_emb.cpu().numpy(),
            "text_embedding": text_emb.cpu().numpy()
        })

    # Ghi file
    with open(output_path, 'wb') as f:
        pickle.dump(data, f)

    print(f"\n✅ Đã lưu toàn bộ đặc trưng vào {output_path}")

# -------------------------------------------------------------
# 🚀 Entry point
# -------------------------------------------------------------
if __name__ == "__main__":
    extract_features()
