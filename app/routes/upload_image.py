from fastapi import APIRouter, UploadFile, File, Form
import os, shutil
from uuid import uuid4
from app.utils.image_utils import process_image
from app.utils.csv_utils import save_memory

router = APIRouter(prefix="/image", tags=["Image"])

UPLOAD_DIR = "app/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_image/")
async def upload_image(file: UploadFile = File(...), question: str = Form("What’s in this photo?")):
    """
    Upload ảnh → OCR + mask PII → trả về câu trả lời liên kết ảnh.
    """
    try:
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = await process_image(file_path, question)
        save_memory(question, result["reply"])

        return {
            "message": "Image uploaded and analyzed successfully",
            "reply": result["reply"],
            "masked_image_path": result["masked_image_path"]
        }

    except Exception as e:
        return {"error": str(e)}
