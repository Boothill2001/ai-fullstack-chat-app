from fastapi import FastAPI
from app.routes import chat, upload_image, upload_csv, memory_viewer
from fastapi.staticfiles import StaticFiles
import os
# Thư mục chứa ảnh upload
UPLOAD_DIR = os.path.join(os.getcwd(), "app/data/uploads")


app = FastAPI(title="AI Chat Backend 🚀")
# Mount static file server
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
# Gắn các route con
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(upload_image.router)
app.include_router(upload_csv.router)
app.include_router(memory_viewer.router, prefix="/memory", tags=["Memory"])

@app.get("/")
def root():
    return {"message": "AI Chat backend is running 🚀"}
