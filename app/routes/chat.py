from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from app.utils.llm_client import query_LLM
from app.utils.csv_utils import save_memory, process_csv
from app.utils.pii_utils import mask_pii, mask_csv_pii
import pandas as pd

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = ""
    csv_url: str | None = None
    csv_file: UploadFile | None = None

@router.post("/")
async def chat_endpoint(req: ChatRequest):
    """
    Xử lý chat text bình thường, hoặc chat về CSV nếu có file/url
    Tích hợp PII masking.
    """
    user_msg = req.message

    # Mask PII trong text
    masked_user_msg = mask_pii(user_msg)

    # Nếu người dùng có upload hoặc URL → xử lý CSV
    if req.csv_url or req.csv_file:
        try:
            csv_reply = await process_csv(req.csv_file, req.csv_url, masked_user_msg)

            # Mask PII trong dữ liệu CSV trả về nếu là DataFrame
            if isinstance(csv_reply, pd.DataFrame):
                csv_reply = mask_csv_pii(csv_reply)

            save_memory(masked_user_msg, csv_reply)
            return {"reply": csv_reply, "type": "csv"}
        except Exception as e:
            return {"error": str(e)}

    # Chat bình thường
    bot_reply = query_LLM(masked_user_msg)
    save_memory(masked_user_msg, bot_reply)
    return {"reply": bot_reply, "type": "text"}
