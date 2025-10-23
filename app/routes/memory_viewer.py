from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter()

MEMORY_PATH = Path("app/data/memory.json")

@router.get("/history/")
def get_memory_history():
    """
    📜 Trả về toàn bộ lịch sử hội thoại trong memory.json
    """
    if not MEMORY_PATH.exists():
        return {"history": []}
    
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        memory = json.load(f)
    
    return memory
