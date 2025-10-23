
# 🚀 AI Full-stack Chat App

A **lightweight and secure** full-stack AI chat system designed for data interaction, built with **FastAPI** (backend) and **Streamlit** (frontend).

This application goes beyond basic chat by supporting advanced features like **PII detection and masking** across both images and CSV datasets.

---

## ✨ Key Features

* 🗨️ **Core Chat:** Multi-turn conversation with persistent history.
* 🖼️ **Image Chat:** Chat about uploaded images, including automatic **PII masking**.
* 📊 **CSV Data Chat:** Interact with uploaded or URL-based CSV datasets to get summaries, missing value analysis, and plots.
* 🔒 **Security-First:** Automatic **PII detection, masking, and detailed audit logging** for all sensitive operations.

---

## 🛠️ Detailed Capabilities

### 1. Core Chat

* Multi-turn conversation between User and Assistant.
* Chat history is persistently saved to `app/data/memory.json`.
* Includes timestamps for each turn and supports **Markdown rendering**.

### 2. Image Chat

* **Upload** PNG/JPG images.
* Automatic **PII masking** (emails, phone numbers, and names) is applied.
* PII audit logs are saved to `data/pii_audit.json`.
* The masked result is stored in `SelfRAG/dataset/uploads/`.

### 3. CSV Data Chat

The app processes CSV data from **file uploads** or a **Raw GitHub CSV URL**.

It supports natural language questions for data analysis, such as:
* "Summarize the dataset"
* "Show missing values"
* "Which column has the most missing values?"
* "Plot histogram of price"

Results are displayed **inline** as text, tables, or simple plots. The system also automatically **detects and masks PII** in the CSV data, logging all actions to `data/pii_audit.json`.

---

## 🛡️ PII Handling System

This system uses regex patterns for reliable detection and supports automatic masking for auditability.

### PII Types Detected

| Type | Regex Pattern |
| :--- | :--- |
| Phone | `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b` |
| Email | `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}` |
| Name | `([A-Z][a-z]+ [A-Z][a-z]+)` |

### Audit Log Example (`data/pii_audit.json`)

```json
{
  "time": "13:03 22/10/25",
  "action": "mask_csv",
  "details": ["phone", "email", "name"]
}
## ⚙️ Tech Stack

### Backend
- Python + FastAPI – High-performance API server

### Frontend
- Streamlit – Interactive web UI

### AI / ML Utilities
- PyTorch, CLIP – For future Self-RAG image/caption embeddings

### OCR
- Tesseract (`pytesseract`) – Extracts text from images for PII detection

### Data Handling
- Pandas, Matplotlib – CSV parsing, numeric stats, plotting

### Persistence
- JSON (memory.json, pii_audit.json) – Chat history & audit logs

```

### 2\. Install dependencies

You can choose between a minimal or a full set of dependencies:

  * **Minimal (for running the demo):**
    ```bash
    pip install -r requirements.txt
    ```
  * **Full (all dependencies used in development):**
    ```bash
    pip install -r requirements_full.txt
    ```

### 3\. Run the backend (FastAPI)

```bash
uvicorn app.main:app --reload --port 8000
```

### 4\. Run the frontend (Streamlit)

```bash
streamlit run app_frontend.py
```

The application will be accessible at:

  * **Frontend App:** [http://localhost:8501](https://www.google.com/search?q=http://localhost:8501)
  * **Backend API:** [http://localhost:8000](https://www.google.com/search?q=http://localhost:8000)

-----

## 📁 Project Structure

This structure separates the core application logic, utility functions, and persistent data storage.

```
app/
├── main.py             # FastAPI entry point
├── routes/             # API endpoints for chat, CSV, image upload
├── utils/              # Helper functions (CSV, image, LLM client, PII)
├── data/               # Persistent storage (memory.json, pii_audit.json)
├── SelfRAG/            # Directory for SelfRAG components (future use)
├── app_frontend.py     # Streamlit entry point
└── requirements.txt
```

-----

## 💡 Future Enhancements

  * **Advanced Retrieval:** Integrate **CLIP + Self-RAG** for smarter image/caption retrieval.
  * **Contextual Summarization:** Add **LLM summarization** for complex CSV or image context.
  * **Deployment:** Set up live deployment to platforms like **Render** or **Hugging Face Spaces**.

-----

## 🖼️ Screenshots & Demo

Watch a full demonstration of the app's capabilities:

🎥 [**Watch Full Demo Video**](https://drive.google.com/file/d/1L9SSGkkwUqwXr8TanTxr-5YBmCmxSThD/view?usp=sharing)

*(Include your screenshots here: CSV Upload + Masking, Image PII Masking, PII Audit Log)*

-----

## ✍️ Author

**A A**
AI Developer & Research Intern Candidate
*Submission Date: October 23, 2025*
Built with ❤️ for the AI Full-stack Internship Assignment

```

This version is more polished, uses a professional tone, and effectively highlights the app's unique selling points, especially the **PII handling** and the **full-stack architecture**.

What part of the app's functionality would you like to explore next? For example, the PII masking implementation or the CSV data querying?
```
