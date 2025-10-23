# app/routes/upload_csv.py
from fastapi import APIRouter, UploadFile, Form
from app.utils.csv_utils import process_csv, save_memory
from app.utils.pii_utils import mask_pii, mask_csv_pii
import pandas as pd

router = APIRouter(prefix="/csv", tags=["CSV"])

@router.post("/upload_csv/")
async def upload_csv(
    file: UploadFile = None,
    url: str = Form(None),
    question: str = Form("Tóm tắt dataset")
):
    """
    API nhận file CSV hoặc URL + câu hỏi (form-data)
    Tích hợp PII masking
    """
    try:
        # Mask PII trong câu hỏi user
        masked_question = mask_pii(question)

        # Xử lý CSV + trả về answer (có thể DataFrame hoặc text)
        answer = await process_csv(file=file, url=url, question=masked_question)

        # Nếu trả về DataFrame → mask PII trong CSV
        if isinstance(answer, pd.DataFrame):
            answer = mask_csv_pii(answer)

        # Lưu lịch sử (user question → answer đã mask)
        try:
            save_memory(masked_question, answer)
        except Exception:
            pass  # don't fail endpoint if logging fails

        return {"reply": answer}
    except Exception as e:
        return {"error": str(e)}
