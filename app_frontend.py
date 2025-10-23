import streamlit as st
import requests
import pandas as pd
import os
import time

# --- CONFIG ---
API_BASE = "http://localhost:8000"  # FastAPI backend
st.set_page_config(page_title="🤖 AI Full-stack Chat App", layout="wide", initial_sidebar_state="expanded")

# --- UTILS FUNCTIONS ---
def api_call(endpoint, method="post", files=None, data=None):
    """Hàm gọi API chung, xử lý lỗi và trả về JSON."""
    url = f"{API_BASE}/{endpoint}"
    try:
        if method.lower() == "post":
            response = requests.post(url, files=files, data=data)
        else:
            response = requests.get(url)
            
        response.raise_for_status()  # Ném Exception nếu status code là lỗi
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API Connection Error: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def append_to_history(role, message):
    """Thêm tin nhắn vào lịch sử chat và đảm bảo không có tin nhắn trùng lặp liên tiếp."""
    if not st.session_state.chat_history or st.session_state.chat_history[-1]['message'] != message:
        st.session_state.chat_history.append({"role": role, "message": message})

# --- SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_image_path" not in st.session_state:
    st.session_state.uploaded_image_path = None
if "csv_preview" not in st.session_state:
    st.session_state.csv_preview = None

# --- SIDEBAR: Upload & Config ---
with st.sidebar:
    st.title("📂 Tính năng Mở rộng")
    
    st.markdown("---")
    
    # --- CSV Upload Section (Dùng st.expander để gọn gàng hơn) ---
    with st.expander("🧾 CSV Chat & Analysis", expanded=True):
        csv_file = st.file_uploader("Upload CSV file", type=["csv"])
        csv_url = st.text_input("Hoặc dán CSV URL", placeholder="e.g., raw GitHub link")
        csv_question = st.text_input("Đặt câu hỏi về CSV", value="Summarize the dataset", key="csv_q")
        
        if st.button("Submit CSV Question", use_container_width=True) and (csv_file or csv_url):
            with st.spinner("Đang xử lý CSV & Trả lời..."):
                files = {"file": csv_file} if csv_file else None
                data = {"url": csv_url, "question": csv_question}
                
                # Gọi API
                result = api_call(f"csv/upload_csv/", files=files, data=data)
                
                # Ghi lịch sử người dùng và xử lý kết quả
                append_to_history("user", f"Phân tích CSV: {csv_question} (Đã gửi file/URL)")
                
                if "error" in result:
                    append_to_history("assistant", f"Lỗi CSV: {result['error']}")
                else:
                    reply = result.get("reply", "🤖 Phân tích CSV hoàn thành.")
                    append_to_history("assistant", reply)
                    
                    # Cập nhật CSV Preview
                    if isinstance(reply, (dict, list)):
                        try:
                            st.session_state.csv_preview = pd.DataFrame(reply)
                        except:
                            st.session_state.csv_preview = None
            st.rerun() # Rerun để cập nhật UI chat

    st.markdown("---")

    # --- Image Upload Section ---
    with st.expander("🖼️ Image Chat & PII Masking", expanded=True):
        image_file = st.file_uploader("Upload Ảnh (PII Masking)", type=["png", "jpg", "jpeg"])
        image_question = st.text_input("Hỏi về nội dung ảnh", value="What is in this photo?", key="image_q")

        if st.button("Upload & Ask Image", use_container_width=True):
            if image_file:
                with st.spinner("Đang phân tích & Che giấu PII..."):
                    files = {"file": image_file}
                    data = {"question": image_question}
                    
                    # Gọi API
                    result = api_call(f"image/upload_image/", files=files, data=data)
                    
                    if "error" in result:
                        append_to_history("assistant", f"Lỗi Ảnh: {result['error']}")
                    else:
                        st.session_state.uploaded_image_path = result.get("masked_image_path")
                        reply = result.get("reply", "🤖 Ảnh đã được xử lý thành công.")
                        
                        append_to_history("user", f"Hỏi về ảnh: {image_question}")
                        append_to_history("assistant", reply)
                st.rerun()
            else:
                st.warning("Vui lòng tải lên một ảnh trước!")

# --- MAIN SECTION: Chat Interface ---

# 1. Tiêu đề và Layout
st.title("💬 AI Full-stack Chat App")

# 2. Hiển thị Lịch sử Chat (Dùng st.chat_message)
# Dùng st.container() để cuộn được lịch sử chat
chat_container = st.container(height=500, border=True)

with chat_container:
    for chat in st.session_state.chat_history:
        # Sử dụng API chat_message mới của Streamlit (Đẹp hơn st.markdown)
        with st.chat_message(chat["role"]):
            st.markdown(chat["message"])

# 3. Thanh nhập liệu Chính
prompt = st.chat_input("💬 Nhập tin nhắn và nhấn Enter")

if prompt:
    # 3a. Thêm tin nhắn người dùng vào lịch sử
    append_to_history("user", prompt)
    
    # 3b. Gọi API cho Chat
    with chat_container: # Thêm tin nhắn ngay lập tức trong container
        with st.chat_message("user"):
            st.markdown(prompt)

    with st.spinner("Assistant đang suy nghĩ..."):
        result = api_call(f"chat", data={"message": prompt})
        
        if "error" in result:
             append_to_history("assistant", f"Lỗi Chat: {result['error']}")
        else:
            reply = result.get("reply", "🤖 No reply received.")
            append_to_history("assistant", str(reply))
            
    st.rerun() # Rerunning để cập nhật thanh chat input và UI

st.markdown("---")

# --- FOOTER: Preview Sections ---
col_img, col_csv = st.columns(2)

# 4. Hiển thị Ảnh đã Masking (Bên trái)
with col_img:
    if st.session_state.uploaded_image_path:
        st.subheader("🖼️ Ảnh đã Tải lên & Che giấu PII")
        try:
            # Lưu ý: Cần đảm bảo FastAPI có route /uploads/ để phục vụ file tĩnh
            masked_path = st.session_state.uploaded_image_path
            filename = os.path.basename(masked_path)
            image_url = f"{API_BASE}/uploads/{filename}"
            
            st.caption(f"Đường dẫn file Masked: {filename}")
            st.image(image_url, use_container_width=True)
            
        except Exception as e:
            st.warning(f"Không thể hiển thị ảnh: {e}")

# 5. Hiển thị CSV Preview (Bên phải)
with col_csv:
    if st.session_state.csv_preview is not None:
        st.subheader("📊 CSV Data Preview (5 hàng đầu)")
        try:
            st.dataframe(st.session_state.csv_preview.head(), use_container_width=True)
        except Exception as e:
             st.warning(f"Không thể hiển thị DataFrame: {e}")